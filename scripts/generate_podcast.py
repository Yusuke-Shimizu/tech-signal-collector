#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
NotebookLMを使って複数のURLからpodcastを生成するスクリプト
1週間以上古いNotebookは自動削除（ローリング方式）
"""
import subprocess
import sys
import re
import json
from datetime import datetime, timedelta
from pathlib import Path


def run_command(cmd, capture=True, check=True):
    """コマンドを実行して結果を返す"""
    print(f"実行: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=capture, text=True)
    if check and result.returncode != 0:
        print(f"エラー: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip() if capture else None


def list_notebooks():
    """全Notebookのリストを取得"""
    output = run_command(['nlm', 'notebook', 'list', '--json'])
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return []


def delete_notebook(notebook_id):
    """Notebookを削除"""
    print(f"  削除中: {notebook_id}")
    run_command(['nlm', 'notebook', 'delete', notebook_id, '--confirm'], capture=False, check=False)


def cleanup_old_notebooks(days=7):
    """指定日数より古いNotebookを削除"""
    print(f"\n🗑️  {days}日以上古いNotebookを削除中...")
    notebooks = list_notebooks()
    
    if not notebooks:
        print("  削除対象のNotebookはありません")
        return
    
    cutoff_date = datetime.now() - timedelta(days=days)
    deleted_count = 0
    
    for notebook in notebooks:
        # Notebook名から日付を抽出（"Daily Trends YYYYMMDD" 形式を想定）
        match = re.search(r'Daily Trends (\d{8})', notebook.get('title', ''))
        if match:
            date_str = match.group(1)
            try:
                notebook_date = datetime.strptime(date_str, '%Y%m%d')
                if notebook_date < cutoff_date:
                    delete_notebook(notebook['id'])
                    deleted_count += 1
            except ValueError:
                continue
    
    if deleted_count > 0:
        print(f"✓ {deleted_count}個のNotebookを削除しました")
    else:
        print("  削除対象のNotebookはありませんでした")


def create_notebook(name):
    """Notebookを作成してIDを返す"""
    output = run_command(['nlm', 'notebook', 'create', name])
    # 出力から notebook ID (UUID形式) を抽出
    match = re.search(r'ID: ([a-f0-9-]{36})', output)
    if match:
        return match.group(1)
    # 見つからない場合はエラー
    print(f"エラー: Notebook IDを抽出できませんでした: {output}")
    sys.exit(1)


def add_source(notebook_id, url):
    """NotebookにURLソースを追加"""
    print(f"  追加中: {url}")
    run_command(['nlm', 'source', 'add', notebook_id, '--url', url], capture=False)


def create_audio(notebook_id):
    """Podcast音声を生成（日本語）"""
    print("Podcast生成を開始（日本語）...")
    run_command(['nlm', 'audio', 'create', notebook_id, '--language', 'ja', '--confirm'], capture=False)


def main():
    # 引数チェック
    if len(sys.argv) < 2:
        print(f"使い方: {sys.argv[0]} <url1> [url2] [url3] ...")
        print(f"例: {sys.argv[0]} https://example.com/article1 https://example.com/article2")
        sys.exit(1)
    
    urls = sys.argv[1:]
    
    # URLの検証
    for url in urls:
        if not url.startswith('http://') and not url.startswith('https://'):
            print(f"エラー: 無効なURL: {url}")
            sys.exit(1)
    
    print(f"\n📖 {len(urls)}個のURLを処理します")
    for i, url in enumerate(urls, 1):
        print(f"  {i}. {url}")
    
    # 古いNotebookを削除（1週間以上前）
    cleanup_old_notebooks(days=7)
    
    # Notebook名を生成
    date_str = datetime.now().strftime("%Y%m%d")
    notebook_name = f"Daily Trends {date_str}"
    
    # Notebook作成
    print(f"\n📝 Notebook作成中: {notebook_name}")
    notebook_id = create_notebook(notebook_name)
    print(f"✓ Notebook ID: {notebook_id}")
    
    # URLを追加
    print(f"\n📎 {len(urls)}個のソースを追加中...")
    for url in urls:
        add_source(notebook_id, url)
    
    print(f"\n✓ 全てのソースを追加完了")
    
    # Podcast生成
    print(f"\n🎙️  Podcast生成中...")
    create_audio(notebook_id)
    
    print(f"\n✅ 完了！")
    print(f"   Notebook ID: {notebook_id}")
    print(f"   NotebookLMで確認: https://notebooklm.google.com")


if __name__ == '__main__':
    main()
