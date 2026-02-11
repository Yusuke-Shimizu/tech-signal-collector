---
name: neta-trend-daily
description: "トレンドネタ収集"
---

# トレンドネタ収集

はてなブックマークIT人気エントリー、Hacker News、AWS What's New、AWSブログ、生成AIブログ、Redditの人気記事を収集し、`ideas/daily/YYYYMMDD-trend.md` に保存する。

## 実行手順

### 0. ユーザープロファイル読み込み

`.claude/rules/user-profile.md` を読み込み、ユーザーの興味領域を理解する。

### 1. トレンド情報の収集

#### 1a. Pythonスクリプトでデータ取得（Reddit, Hacker News, AWS, はてブ）

以下のBashコマンドでデータを一括取得する：

```bash
python3 scripts/fetch_trends.py
```

- JSON形式で標準出力に結果が出る。進捗は標準エラーに表示される
- ソースを絞る場合: `python3 scripts/fetch_trends.py reddit hatena` のように指定可能
- 利用可能ソース: `reddit`, `hn`, `aws`, `hatena`

**スクリプトが取得するデータ:**
- **Reddit**: r/OpenAI, r/LocalLLaMA, r/ClaudeCode, r/cscareerquestions, r/productivity の各 hot 10件（タイトル、投票数、コメント数、URL）
- **Hacker News**: トップ30件（タイトル、スコア、コメント数、HN URL、元記事URL）
- **AWS**: What's New 20件 + Blog JP 10件（タイトル、URL、日付）
- **はてブ**: IT/プログラミング/AI・機械学習/はてなブログ(テクノロジー)/エンジニア の5カテゴリRSS（タイトル、URL、ブクマ数、カテゴリ。重複排除済み、ブクマ数降順）

#### 1b. WebFetchで取得（生成AIブログ）

以下はスクリプト非対応のため、WebFetchツールで直接取得する：

**生成AIブログ**
- https://simonwillison.net/ - Simon Willison's Weblog（LLM実践・AIツール活用の第一人者）
- https://www.anthropic.com/blog - Anthropic公式ブログ（Claude/エージェント設計の一次情報）
- 最新3-5記事をチェックし、注目トピックに含める
- **タイトルは日本語に翻訳して出力**

#### データ利用時の注意

- **Hacker News**: スクリプト出力の `hn_url` をリンクに使用（`item?id=`形式）。元記事URLではなくHNコメントページURL
- **Reddit**: スクリプト出力の `url` をリンクに使用（`https://www.reddit.com/r/...`形式の完全URL）
- **はてブ**: スクリプト出力の `url` が元記事URL（はてブページURLではない）
- **英語タイトルは日本語に翻訳して出力**（HN, Reddit, AWS What's New, 生成AIブログ）

### 2. 分析

収集した情報を以下の観点で分析：

**興味領域マッチング（最優先）**
- 各記事を興味領域と照合し、関連度を評価
- 高関連度の記事を「注目トピック」の最上位に配置
- 特に注目すべきトピック：
  - 生成AI/LLM関連（新モデル、エージェント、開発ツール、プロンプトエンジニアリング）
  - AWS関連（新サービス、AI/ML、サーバーレス、アーキテクチャ）
  - OSS/個人開発関連（成功事例、マーケティング、収益化）
  - キャリア関連（外資転職、リモートワーク、副業）
  - JavaScript/TypeScript関連（新技術、ツール、フレームワーク）

**はてブIT**
- 日本のエンジニアに刺さりやすい話題
- 議論を呼びそうなトピック
- 技術トレンド（AI、開発手法、ツール等）
- キャリア・働き方関連

**Hacker News**
- グローバルで話題の技術トレンド
- スタートアップ・プロダクト関連
- AI/LLM関連の議論
- 議論を呼んでいるトピック（ポイント数が高い）

**AWS What's New / AWS Blog**
- AI/ML関連（Bedrock、SageMaker、Generative AI）
- サーバーレス・コンテナ関連
- コスト最適化・新リージョン
- 開発者ツール関連

**生成AIブログ**
- LLMの新機能・活用事例
- エージェント設計・アーキテクチャ
- プロンプトエンジニアリング
- AIツールのレビュー・比較

**Reddit（5サブレッド）**
- AI系：OpenAI、ローカルLLM、Claude Code関連
- キャリア/実践系：キャリア、生産性
- 投票数（ups）とコメント数でコミュニティの反応を評価
- 議論が活発なトピック（コメント数が多い）を優先

### 3. 出力

**まず「ネタ収集完了。」というメッセージを返してから、結果を `ideas/daily/YYYYMMDD-trend.md` に保存。**

以下のフォーマットで出力：

```markdown
# トレンドネタ: YYYY-MM-DD

## ★★★ 記事インデックス

全ソースから興味度★★★の記事を抽出し、**通し番号**で一覧化。`/neta-interest-daily` での番号指定に使用。

| # | タイトル | ソース | 指標 | メモ |
|---|---------|--------|------|------|
| 1 | [タイトル](URL) | はてブ | XXX users | 一言メモ |
| 2 | [タイトル](URL) | HN | XXXpt | 一言メモ |
| 3 | [タイトル](URL) | AWS What's New | YYYY-MM-DD | 一言メモ |
| 4 | [タイトル](URL) | AWS Blog | YYYY-MM-DD | 一言メモ |
| 5 | [タイトル](URL) | Simon Willison | - | 一言メモ |
| 6 | [タイトル](URL) | Anthropic | - | 一言メモ |
| 7 | [タイトル](URL) | r/subreddit | XXX ups | 一言メモ |
| ... | ... | ... | ... | ... |

---

## はてブIT（日本市場）

### 注目トピック

| タイトル | ブクマ数 | 興味度 | カテゴリ | メモ |
|---------|---------|--------|---------|------|
| [タイトル](元記事URL) | XXX users | ★★★/★★/★ | AI/開発/キャリア等 | 発信に活用できるポイント |

**興味度の定義**:
- ★★★: 興味領域に直接関連（AI/LLM、AWS、個人開発、キャリアなど）
- ★★: 間接的に関連（技術トレンド全般、エンジニアリング文化）
- ★: 一般的なIT/技術ニュース

### 全エントリー

1. [タイトル](元記事URL) (XXX users) - 概要
2. ...

## Hacker News（グローバル）

### 注目トピック

| タイトル | ポイント | 興味度 | カテゴリ | メモ |
|---------|---------|--------|---------|------|
| [タイトル](HNコメントページURL) | XXXpt | ★★★/★★/★ | AI/Dev/Career等 | 発信に活用できるポイント |

### 全エントリー

1. [タイトル](HNコメントページURL) (XXXpt) - 概要
2. ...

## AWS What's New / AWS Blog

### 注目トピック

| タイトル | ソース | 日付 | 興味度 | カテゴリ | メモ |
|---------|--------|------|--------|---------|------|
| [タイトル](URL) | What's New / Blog | YYYY-MM-DD | ★★★/★★/★ | AI・ML/Serverless/Container等 | 発信に活用できるポイント |

### 全エントリー

1. [タイトル](URL) (YYYY-MM-DD) - 概要
2. ...

## 生成AIブログ

### Simon Willison's Weblog

| タイトル | 興味度 | メモ |
|---------|--------|------|
| [タイトル](URL) | ★★★/★★/★ | 要点 |

### Anthropic Blog

| タイトル | 興味度 | メモ |
|---------|--------|------|
| [タイトル](URL) | ★★★/★★/★ | 要点 |

## Reddit（5サブレッド）

### 注目トピック

| タイトル | 投票数 | コメント数 | 興味度 | カテゴリ | サブレッド | メモ |
|---------|--------|-----------|--------|---------|-----------|------|
| [タイトル](Redditコメントページ完全URL) | XXX ups | XXX | ★★★/★★/★ | AI/Career等 | r/subreddit | 発信に活用できるポイント |

### カテゴリ別エントリー

#### AI系
1. [タイトル](RedditコメントページURL) (XXX ups, XXX comments) - r/OpenAI - 概要
2. ...

#### キャリア/実践系
1. [タイトル](RedditコメントページURL) (XXX ups, XXX comments) - r/cscareerquestions - 概要
2. ...
```

## 注意事項

- **データ取得は `python3 scripts/fetch_trends.py` を最初に実行**し、そのJSON出力をもとに分析・出力する
- 生成AIブログ（Simon Willison, Anthropic）のみWebFetchツールで取得
- **すべての記事にURLリンクを必ず含める（リンクなしは不可）**
- **英語タイトルは日本語に翻訳**（HN, Reddit, AWS What's New, 生成AIブログ）
- 投票数（ups）/コメント数が高い記事を優先
- ポイント数/ブックマーク数が高い記事は特に注目
- 出力ファイルのYYYYMMDDは実行日の日付を使用
