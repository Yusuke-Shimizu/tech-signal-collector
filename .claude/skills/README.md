# Claude Code Skills

このプロジェクトで利用可能なClaude Codeスキル一覧。

## スキル一覧

| スキル | 説明 | 引数 | 使用例 |
|-------|------|------|--------|
| `/neta-trend-daily` | トレンドネタ収集 | なし | `/neta-trend-daily` |
| `/neta-interest-daily` | 興味関心メモ作成 | 記事番号 / `all` / URL | `/neta-interest-daily 1,3,7` |
| `/git-push` | 変更をコミットしてpush | コミットメッセージ(省略可) | `/git-push interestスキルを修正` |

## 日次ワークフロー

```
1. /neta-trend-daily          → トレンド収集 → ideas/daily/YYYYMMDD-trend.md
2. /neta-interest-daily       → ★★★記事一覧から選択 → 深掘り → ideas/daily/YYYYMMDD-interest.md
3. /git-push                  → コミット & プッシュ
```

## 各スキルの詳細

### /neta-trend-daily

はてブIT、Hacker News、AWS What's New、生成AIブログ（Simon Willison / Anthropic）、Reddit（5サブレッド）から最新トレンドを収集。ユーザープロファイル（`.claude/rules/user-profile.md`）の興味領域に基づいて★★★〜★の興味度を付与する。

**出力**: `ideas/daily/YYYYMMDD-trend.md`

### /neta-interest-daily

トレンドメモから興味度★★★の記事を抽出し、ユーザーが選択した記事をWebFetchで深掘り。複数ソースを横断的に分析し、興味関心メモを作成する。必要に応じてユーザープロファイルも更新。

**出力**: `ideas/daily/YYYYMMDD-interest.md`

**引数パターン**:
- 引数なし → ★★★記事の番号付き一覧を提示 → 選択を待つ
- `1,3,7` → 該当番号の記事を即座に深掘り
- `all` → ★★★記事をすべて深掘り
- URL → 指定URLの記事を深掘り
- 混在 → `1,3 https://example.com/article` のように番号とURL両方OK

### /git-push

変更ファイルをまとめてコミットし、リモートにプッシュ。コミットメッセージは引数で指定するか、変更内容から自動生成。

**引数パターン**:
- 引数なし → 変更内容を分析してコミットメッセージを自動生成
- テキスト → そのままコミットメッセージとして使用

## ディレクトリ構成

```
.claude/skills/
├── README.md                          # このファイル
├── neta-trend-daily/
│   └── SKILL.md
├── neta-interest-daily/
│   └── SKILL.md
└── git-push/
    └── SKILL.md
```
