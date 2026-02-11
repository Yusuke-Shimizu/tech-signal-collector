#!/usr/bin/env python3
"""トレンドデータ取得スクリプト

各ソースからトレンドデータを取得し、JSON形式で標準出力に出力する。
Claude Codeの /neta-trend-daily スキルから呼び出される。

使い方:
    python scripts/fetch_trends.py                # 全ソース取得
    python scripts/fetch_trends.py reddit          # Reddit のみ
    python scripts/fetch_trends.py hatena           # はてブ のみ
    python scripts/fetch_trends.py hn               # Hacker News のみ
    python scripts/fetch_trends.py aws              # AWS What's New のみ
    python scripts/fetch_trends.py reddit hatena    # 複数指定
"""

import json
import sys
import time
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

USER_AGENT = "neta-trend-collector/1.0 (trend analysis tool)"

# ── Reddit ──────────────────────────────────────────────────

SUBREDDITS = {
    "ai": ["OpenAI", "LocalLLaMA", "ClaudeCode"],
    "career": ["cscareerquestions", "productivity"],
}


def fetch_reddit():
    results = {}
    all_subs = [s for subs in SUBREDDITS.values() for s in subs]
    for sub in all_subs:
        url = f"https://old.reddit.com/r/{sub}/hot.json?t=day&limit=10"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
            posts = []
            for child in data.get("data", {}).get("children", []):
                d = child.get("data", {})
                posts.append({
                    "title": d.get("title", ""),
                    "ups": d.get("ups", 0),
                    "num_comments": d.get("num_comments", 0),
                    "url": f"https://www.reddit.com{d.get('permalink', '')}",
                    "subreddit": sub,
                })
            results[sub] = posts
        except Exception as e:
            results[sub] = {"error": str(e)}
        time.sleep(1)
    return results


# ── Hacker News ─────────────────────────────────────────────


def fetch_hn():
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=15) as resp:
        ids = json.loads(resp.read().decode())

    posts = []
    for item_id in ids[:30]:
        item_url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
        req = urllib.request.Request(item_url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                item = json.loads(resp.read().decode())
            posts.append({
                "title": item.get("title", ""),
                "score": item.get("score", 0),
                "comments": item.get("descendants", 0),
                "hn_url": f"https://news.ycombinator.com/item?id={item_id}",
                "article_url": item.get("url", ""),
            })
        except Exception:
            continue
    return posts


# ── AWS What's New (RSS) ────────────────────────────────────


def fetch_aws_whatsnew():
    url = "https://aws.amazon.com/about-aws/whats-new/recent/feed/"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=15) as resp:
        xml_data = resp.read()

    root = ET.fromstring(xml_data)
    items = root.findall(".//item")
    posts = []
    for item in items[:20]:
        title_el = item.find("title")
        link_el = item.find("link")
        pub_el = item.find("pubDate")
        posts.append({
            "title": title_el.text if title_el is not None else "",
            "url": link_el.text if link_el is not None else "",
            "date": pub_el.text if pub_el is not None else "",
        })
    return posts


# ── AWS Blog (Japanese, RSS) ────────────────────────────────


def fetch_aws_blog_jp():
    url = "https://aws.amazon.com/jp/blogs/news/feed/"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            xml_data = resp.read()
        root = ET.fromstring(xml_data)
        items = root.findall(".//{http://www.w3.org/2005/Atom}entry") or root.findall(".//item")
        posts = []
        for item in items[:10]:
            # Try RSS format
            title_el = item.find("title")
            link_el = item.find("link")
            pub_el = item.find("pubDate")
            if link_el is None:
                link_el = item.find("{http://www.w3.org/2005/Atom}link")
            if pub_el is None:
                pub_el = item.find("{http://www.w3.org/2005/Atom}updated")
            posts.append({
                "title": title_el.text if title_el is not None else "",
                "url": (link_el.text if link_el is not None and link_el.text
                        else link_el.get("href", "") if link_el is not None else ""),
                "date": pub_el.text if pub_el is not None else "",
            })
        return posts
    except Exception as e:
        return {"error": str(e)}


# ── はてなブックマーク (RSS) ─────────────────────────────────

HATENA_FEEDS = {
    "it": "https://b.hatena.ne.jp/hotentry/it.rss",
    "programming": "https://b.hatena.ne.jp/hotentry/it/%E3%83%97%E3%83%AD%E3%82%B0%E3%83%A9%E3%83%9F%E3%83%B3%E3%82%B0.rss",
    "ai_ml": "https://b.hatena.ne.jp/hotentry/it/AI%E3%83%BB%E6%A9%9F%E6%A2%B0%E5%AD%A6%E7%BF%92.rss",
    "hatena_blog_tech": "https://b.hatena.ne.jp/hotentry/it/%E3%81%AF%E3%81%A6%E3%81%AA%E3%83%96%E3%83%AD%E3%82%B0%EF%BC%88%E3%83%86%E3%82%AF%E3%83%8E%E3%83%AD%E3%82%B8%E3%83%BC%EF%BC%89.rss",
    "engineer": "https://b.hatena.ne.jp/hotentry/it/%E3%82%A8%E3%83%B3%E3%82%B8%E3%83%8B%E3%82%A2.rss",
}

NS_DC = "http://purl.org/dc/elements/1.1/"
NS_HATENA = "http://www.hatena.ne.jp/info/xmlns#"
NS_CONTENT = "http://purl.org/rss/1.0/modules/content/"
NS_RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
NS_RSS10 = "http://purl.org/rss/1.0/"


def _parse_hatena_bookmarkcount(item):
    """はてブ数を取得"""
    bc = item.find(f"{{{NS_HATENA}}}bookmarkcount")
    if bc is not None and bc.text:
        return int(bc.text)
    return 0


def fetch_hatena():
    seen_urls = set()
    all_entries = []

    for category, feed_url in HATENA_FEEDS.items():
        req = urllib.request.Request(feed_url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                xml_data = resp.read()
            root = ET.fromstring(xml_data)
            # RSS 1.0 (RDF) format
            items = root.findall(f"{{{NS_RSS10}}}item")
            if not items:
                # Try RSS 2.0 format
                items = root.findall(".//item")

            for item in items:
                link_el = item.find(f"{{{NS_RSS10}}}link")
                if link_el is None:
                    link_el = item.find("link")
                title_el = item.find(f"{{{NS_RSS10}}}title")
                if title_el is None:
                    title_el = item.find("title")

                url = link_el.text if link_el is not None else ""
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)

                bookmarks = _parse_hatena_bookmarkcount(item)

                # RDF about attribute as fallback URL
                if not url:
                    url = item.get(f"{{{NS_RDF}}}about", "")

                all_entries.append({
                    "title": title_el.text if title_el is not None else "",
                    "url": url,
                    "bookmarks": bookmarks,
                    "category": category,
                })
        except Exception as e:
            all_entries.append({"error": str(e), "category": category})
        time.sleep(0.5)

    # ブクマ数降順でソート
    all_entries.sort(key=lambda x: x.get("bookmarks", 0), reverse=True)
    return all_entries


# ── メイン ───────────────────────────────────────────────────

FETCHERS = {
    "reddit": ("Reddit (5 subreddits)", fetch_reddit),
    "hn": ("Hacker News (top 30)", fetch_hn),
    "aws": ("AWS What's New + Blog JP", lambda: {
        "whatsnew": fetch_aws_whatsnew(),
        "blog_jp": fetch_aws_blog_jp(),
    }),
    "hatena": ("Hatena Bookmark IT", fetch_hatena),
}


def main():
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(FETCHERS.keys())
    invalid = [t for t in targets if t not in FETCHERS]
    if invalid:
        print(f"Unknown sources: {', '.join(invalid)}", file=sys.stderr)
        print(f"Available: {', '.join(FETCHERS.keys())}", file=sys.stderr)
        sys.exit(1)

    results = {}
    for target in targets:
        label, fetcher = FETCHERS[target]
        print(f"Fetching {label}...", file=sys.stderr)
        try:
            results[target] = fetcher()
        except Exception as e:
            results[target] = {"error": str(e)}

    json.dump(results, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
