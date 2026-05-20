from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
ARTICLES = ROOT / "content" / "articles"


def main() -> None:
    article_files = sorted(ARTICLES.glob("*.md"))
    html_files = sorted((PUBLIC / "articles").glob("*.html"))
    assert len(article_files) == 250, len(article_files)
    assert len(html_files) == 250, len(html_files)

    stats = json.loads((ROOT / "content" / "article_stats.json").read_text(encoding="utf-8"))
    assert stats["total_articles"] == 250, stats
    assert stats["min_chars"] >= 1250, stats
    assert 1300 <= stats["average_chars"] <= 1700, stats
    assert stats["max_chars"] <= 1900, stats

    titles = []
    for article in article_files:
        text = article.read_text(encoding="utf-8")
        title = re.search(r'^title: "(.+)"$', text, re.MULTILINE)
        keyword = re.search(r'^keyword: "(.+)"$', text, re.MULTILINE)
        assert title and keyword, article
        titles.append(title.group(1))
        assert keyword.group(1) in title.group(1), article

    assert len(set(titles)) == 250
    sitemap = (PUBLIC / "sitemap.xml").read_text(encoding="utf-8")
    assert sitemap.count("<url>") == 264, sitemap.count("<url>")

    index = (PUBLIC / "index.html").read_text(encoding="utf-8")
    assert "Advertisements" in index
    forbidden = ["请点击广告", "点击广告支持", "帮忙点广告", "多点广告", "click the ads", "support us by clicking"]
    all_html = "\n".join(path.read_text(encoding="utf-8").lower() for path in PUBLIC.rglob("*.html"))
    assert not any(term.lower() in all_html for term in forbidden)

    print("OK: 250 articles, SEO titles, sitemap, ad labels and policy text verified.")


if __name__ == "__main__":
    main()
