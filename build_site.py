from __future__ import annotations

import html
import json
import os
import re
import shutil
import textwrap
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from data.tools_seed import CATEGORIES, SITE_NAME, SITE_TAGLINE, TOOLS_BY_CATEGORY

ROOT = Path(__file__).parent
PUBLIC = ROOT / "public"
ARTICLES = ROOT / "content" / "articles"
BASE_URL = os.environ.get("SITE_BASE_URL", "https://example.com").rstrip("/")
ADSENSE_CLIENT = os.environ.get("ADSENSE_CLIENT", "")
ADSENSE_PUBLISHER_ID = os.environ.get("ADSENSE_PUBLISHER_ID", "")
TODAY = date.today().isoformat()


@dataclass(frozen=True)
class Tool:
    name: str
    slug: str
    category_id: str
    category_name: str
    category_keyword: str
    category_intent: str
    color: str
    title: str
    description: str
    body: str
    chars: int


def main() -> None:
    reset_output()
    tools = build_tools()
    write_assets(tools)
    write_home(tools)
    write_categories(tools)
    write_articles(tools)
    write_static_pages(tools)
    write_indexes(tools)
    write_article_markdown(tools)
    write_stats(tools)
    print(f"Built {len(tools)} tools and articles into {PUBLIC}")
    print(f"Article length range: {min(t.chars for t in tools)}-{max(t.chars for t in tools)} chars")


def reset_output() -> None:
    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    PUBLIC.mkdir(parents=True)
    (PUBLIC / ".nojekyll").write_text("", encoding="utf-8")
    ARTICLES.mkdir(parents=True, exist_ok=True)
    for old in ARTICLES.glob("*.md"):
        old.unlink()


def build_tools() -> list[Tool]:
    tools: list[Tool] = []
    for category_id, names in TOOLS_BY_CATEGORY.items():
        category = CATEGORIES[category_id]
        for position, name in enumerate(names, start=1):
            slug = f"{category_id}-{slugify(name)}"
            title = f"{name} {category['keyword']}推荐：{category['name']}场景、优势与选择指南"
            description = (
                f"了解 {name} 在{category['name']}中的适用场景、核心价值、使用建议和替代选择，"
                f"适合正在寻找{category['keyword']}的个人、团队和中小企业。"
            )
            body = build_article_body(name, category_id, category, position)
            tools.append(
                Tool(
                    name=name,
                    slug=slug,
                    category_id=category_id,
                    category_name=category["name"],
                    category_keyword=category["keyword"],
                    category_intent=category["intent"],
                    color=category["color"],
                    title=title,
                    description=description,
                    body=body,
                    chars=count_text_chars(body),
                )
            )
    return tools


def build_article_body(name: str, category_id: str, category: dict, position: int) -> str:
    keyword = category["keyword"]
    category_name = category["name"]
    intent = category["intent"]
    scenarios = {
        "writing": ("选题规划、长文草稿、标题改写、产品描述、邮件和社媒脚本", "内容团队可以把它放在关键词研究之后、人工校对之前"),
        "research": ("资料检索、论文阅读、竞品梳理、事实核对和问题拆解", "研究人员可以把它作为第一轮信息地图，而不是最终结论"),
        "image": ("封面图、广告图、商品图、品牌视觉、灵感探索和批量改图", "设计人员可以先用它验证方向，再进入精修环节"),
        "video": ("短视频脚本、数字人讲解、字幕生成、片段剪辑和素材复用", "运营团队可以用它缩短从想法到可发布视频的周期"),
        "coding": ("代码补全、需求拆解、错误排查、测试用例和原型开发", "开发者可以让它处理重复劳动，把架构判断留给人工"),
        "office": ("会议纪要、任务分解、文档总结、幻灯片和日程安排", "团队可以把它嵌入日常办公流程，减少低价值切换"),
        "marketing": ("SEO内容、广告素材、销售邮件、社媒排期和线索运营", "增长团队可以用它做多版本测试，再用数据筛选胜出方案"),
        "audio": ("配音、播客清理、音乐草稿、降噪、字幕和多语言声音内容", "创作者可以用它提升声音素材的生产和交付效率"),
        "data": ("表格分析、图表解释、指标归因、预测建模和报表自动化", "业务人员可以用自然语言询问数据，再交叉验证关键结论"),
        "automation": ("客服机器人、网页采集、工作流编排、智能体任务和线索处理", "运营团队可以先从单一流程自动化开始，再逐步扩大范围"),
    }[category_id]
    differentiator = [
        "它的价值不在于替代专业判断，而在于把重复、低门槛、耗时的步骤压缩到几分钟内。",
        "选择这类工具时，不要只看演示效果，更要看输出是否稳定、是否容易复用到真实工作流。",
        "如果你的目标是做内容站或商业项目，它适合承担前期素材整理和方案草拟，但最终发布前仍要人工复核。",
        "对于想提升效率的团队，最好的使用方式是固定输入模板、保存优秀案例，并建立可复查的质量标准。",
    ][position % 4]
    compare = [
        "如果你更重视免费额度，可以先对比同类产品的限制；如果你更重视团队协作，则应关注权限、版本和导出能力。",
        "如果你已经有成熟流程，建议先把它接入一个小任务，确认结果稳定后再扩大到更多成员。",
        "如果你面向中文用户，还要额外检查中文理解、术语一致性和本地化输出质量。",
        "如果页面要依靠搜索流量变现，文章中应给出真实场景、优缺点和替代方案，而不是堆砌关键词。",
    ][position % 4]
    ad_note = (
        "从网站变现角度看，围绕它写工具介绍、对比清单和常见问题页，比单纯放链接更容易承接长尾搜索。"
        "广告位应清楚标注，避免任何诱导点击。"
    )
    qa = [
        f"{name} 适合新手吗？如果需求集中在{scenarios[0]}，新手可以从模板化任务开始，先验证输出质量，再增加复杂要求。",
        f"{name} 能直接替代人工吗？更合理的定位是辅助工具。它能提高初稿、检索和整理速度，但事实准确性、版权风险和品牌语气仍要人工确认。",
    ]
    body = f"""
    {name} 是一个值得收录到 AI 工具导航中的 {keyword}。它适合希望在{category_name}环节节省时间的人，尤其是需要{intent}的个人创作者、运营团队和中小企业。相比只收藏官网链接，更有价值的做法是理解它能解决什么问题、适合什么任务，以及什么时候应该换用其他工具。

    在实际使用中，{name} 更适合处理{scenarios[0]}。{scenarios[1]}。如果流程以前依赖大量手动复制、整理和改写，可以先把任务拆成输入、生成、检查、发布四步，再逐步沉淀成固定模板。

    {differentiator} 对 SEO 内容站来说，介绍 {name} 时最好围绕明确关键词展开，例如“{keyword}推荐”“{name} 使用场景”“{category_name} AI 工具对比”。标题要直接说明用途，正文要回答适用人群、上手成本、限制和替代选择。

    选择 {name} 时，建议重点看三点：第一，核心输出是否满足真实任务；第二，是否支持团队协作、导出、历史记录或 API；第三，价格、隐私和版权条款是否适合商业项目。{compare}

    {ad_note} 如果你正在建设 AI 工具导航网站，可以把 {name} 页面做成“结论 + 场景 + 替代工具 + FAQ”的结构，再通过分类页和相关文章互相链接。

    常见问题：{qa[0]} {qa[1]}
    """
    body = clean_paragraphs(body)
    fillers = [
        f"补充建议：发布前可以加入真实截图、测试案例或更新日期，让页面比普通采集站更可信。",
        f"运营建议：同一分类下应保留横向对比入口，用户看完 {name} 后能继续浏览其他 {keyword}。",
        f"风险提醒：不要承诺工具永远免费或效果绝对准确，具体功能和价格应以官方页面为准。",
    ]
    index = 0
    while count_text_chars(body) < 760:
        body += "\n\n" + fillers[index % len(fillers)]
        index += 1
    return body


def write_assets(tools: list[Tool]) -> None:
    assets = PUBLIC / "assets"
    assets.mkdir()
    (assets / "styles.css").write_text(STYLES, encoding="utf-8")
    search_index = [
        {
            "name": t.name,
            "title": t.title,
            "category": t.category_name,
            "keyword": t.category_keyword,
            "url": f"articles/{t.slug}.html",
            "description": t.description,
        }
        for t in tools
    ]
    (assets / "search-index.json").write_text(
        json.dumps(search_index, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (assets / "app.js").write_text(APP_JS, encoding="utf-8")


def write_home(tools: list[Tool]) -> None:
    category_cards = []
    for category_id, category in CATEGORIES.items():
        category_tools = [tool for tool in tools if tool.category_id == category_id]
        category_cards.append(
            f"""
            <a class="category-card" href="categories/{category_id}.html" style="--accent:{category['color']}">
              <span>{category['name']}</span>
              <strong>{category['keyword']}</strong>
              <em>{len(category_tools)} 个工具</em>
            </a>
            """
        )
    featured = "".join(tool_card(tool, "") for tool in tools[:36])
    content = f"""
    <section class="directory-head">
      <div>
        <p class="eyebrow">AI Tools Directory</p>
        <h1>{SITE_NAME}：按分类查找高价值 AI 工具</h1>
        <p>{SITE_TAGLINE}。本站为内容型导航结构，适合用 SEO 长尾页面获取搜索流量，并预留合规广告位。</p>
      </div>
      {ad_slot("home_top")}
    </section>
    <section class="search-panel">
      <label for="toolSearch">搜索工具、分类或关键词</label>
      <input id="toolSearch" type="search" placeholder="例如：AI写作工具、Midjourney、代码助手" autocomplete="off">
      <div id="searchResults" class="search-results" aria-live="polite"></div>
    </section>
    <section>
      <h2>AI 工具分类</h2>
      <div class="category-grid">{"".join(category_cards)}</div>
    </section>
    {ad_slot("home_mid")}
    <section>
      <h2>推荐 AI 工具文章</h2>
      <div class="tool-grid">{featured}</div>
    </section>
    """
    write_page(PUBLIC / "index.html", "AI工具导航库：AI工具分类、推荐与SEO文章", SITE_TAGLINE, content, "")


def write_categories(tools: list[Tool]) -> None:
    folder = PUBLIC / "categories"
    folder.mkdir()
    for category_id, category in CATEGORIES.items():
        category_tools = [tool for tool in tools if tool.category_id == category_id]
        cards = "".join(tool_card(tool, "../") for tool in category_tools)
        content = f"""
        <section class="directory-head compact">
          <div>
            <p class="eyebrow">{html.escape(category['keyword'])}</p>
            <h1>{html.escape(category['name'])} AI 工具推荐</h1>
            <p>{html.escape(category['intent'])}。本分类共收录 {len(category_tools)} 篇工具介绍，适合按用途、场景和关键词继续扩展内容。</p>
          </div>
          {ad_slot(f"category_{category_id}")}
        </section>
        <div class="tool-grid">{cards}</div>
        """
        write_page(
            folder / f"{category_id}.html",
            f"{category['keyword']}推荐：{category['name']}分类导航",
            f"收录 {len(category_tools)} 个{category['keyword']}，覆盖使用场景、选择建议和替代方案。",
            content,
            "../",
        )


def write_articles(tools: list[Tool]) -> None:
    folder = PUBLIC / "articles"
    folder.mkdir()
    by_category = {category_id: [t for t in tools if t.category_id == category_id] for category_id in CATEGORIES}
    for tool in tools:
        related = [t for t in by_category[tool.category_id] if t.slug != tool.slug][:6]
        article_html = markdownish_to_html(tool.body)
        related_links = "".join(
            f'<li><a href="{item.slug}.html">{html.escape(item.name)} {html.escape(item.category_keyword)}</a></li>'
            for item in related
        )
        content = f"""
        <article class="article">
          <nav class="breadcrumb"><a href="../index.html">首页</a> / <a href="../categories/{tool.category_id}.html">{html.escape(tool.category_name)}</a> / {html.escape(tool.name)}</nav>
          <p class="eyebrow">{html.escape(tool.category_keyword)}</p>
          <h1>{html.escape(tool.title)}</h1>
          <p class="summary">{html.escape(tool.description)}</p>
          {ad_slot(f"article_top_{tool.slug}")}
          {article_html}
          {ad_slot(f"article_mid_{tool.slug}")}
          <section class="related">
            <h2>同类 AI 工具继续看</h2>
            <ul>{related_links}</ul>
          </section>
        </article>
        """
        schema = article_schema(tool)
        write_page(
            folder / f"{tool.slug}.html",
            tool.title,
            tool.description,
            content,
            "../",
            schema=schema,
            canonical=f"{BASE_URL}/articles/{tool.slug}.html",
        )


def write_static_pages(tools: list[Tool]) -> None:
    privacy = """
    <section class="article">
      <h1>隐私政策与广告说明</h1>
      <p>本站是 AI 工具导航与内容站。站点可能使用 Google AdSense 或其他广告网络展示广告。广告服务商可能使用 Cookie 或类似技术，根据用户访问内容展示相关广告。</p>
      <p>本站不会要求用户点击广告，也不会用奖励、误导性按钮或夸张提示诱导广告点击。广告位会以 Advertisements 或 Sponsored Links 标注。</p>
      <p>如果你需要上线，请把本页替换为与你公司主体、联系方式、数据收集方式和所在地法律一致的正式隐私政策。</p>
    </section>
    """
    about = f"""
    <section class="article">
      <h1>关于 {SITE_NAME}</h1>
      <p>{SITE_NAME} 是一个面向搜索流量的 AI 工具导航模板，核心结构包括分类页、工具文章页、内部链接、搜索索引、sitemap 和合规广告位。</p>
      <p>当前已生成 {len(tools)} 篇工具文章。建议上线后继续补充真实试用截图、价格更新时间、优缺点对比和原创案例，让页面更接近用户真正需要的决策资料。</p>
    </section>
    """
    contact = """
    <section class="article">
      <h1>联系我们</h1>
      <p>如果你想提交 AI 工具、更新文章信息或投放品牌广告，请在此处填写你的邮箱、表单或商务联系方式。</p>
    </section>
    """
    write_page(PUBLIC / "privacy.html", "隐私政策与广告说明", "AI工具导航库的隐私政策、广告 Cookie 与合规说明。", privacy, "")
    write_page(PUBLIC / "about.html", f"关于{SITE_NAME}", "了解 AI 工具导航库的内容结构、广告位和 SEO 运营方式。", about, "")
    write_page(PUBLIC / "contact.html", "联系与工具提交", "提交 AI 工具、内容更新和商务合作。", contact, "")
    (PUBLIC / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n", encoding="utf-8")
    if ADSENSE_PUBLISHER_ID:
        (PUBLIC / "ads.txt").write_text(
            f"google.com, {ADSENSE_PUBLISHER_ID}, DIRECT, f08c47fec0942fa0\n",
            encoding="utf-8",
        )
    (ROOT / "ads.txt.template").write_text(
        "google.com, pub-REPLACE_WITH_YOUR_ADSENSE_PUBLISHER_ID, DIRECT, f08c47fec0942fa0\n",
        encoding="utf-8",
    )


def write_indexes(tools: list[Tool]) -> None:
    urls = ["index.html", "privacy.html", "about.html", "contact.html"]
    urls += [f"categories/{category_id}.html" for category_id in CATEGORIES]
    urls += [f"articles/{tool.slug}.html" for tool in tools]
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in urls:
        sitemap.append(f"<url><loc>{BASE_URL}/{url}</loc><lastmod>{TODAY}</lastmod></url>")
    sitemap.append("</urlset>")
    (PUBLIC / "sitemap.xml").write_text("\n".join(sitemap), encoding="utf-8")


def write_article_markdown(tools: list[Tool]) -> None:
    for tool in tools:
        markdown = f"""---
title: "{tool.title}"
description: "{tool.description}"
category: "{tool.category_name}"
keyword: "{tool.category_keyword}"
slug: "{tool.slug}"
chars: {tool.chars}
---

# {tool.title}

{tool.body}
"""
        (ARTICLES / f"{tool.slug}.md").write_text(markdown, encoding="utf-8")


def write_stats(tools: list[Tool]) -> None:
    stats = {
        "total_articles": len(tools),
        "min_chars": min(tool.chars for tool in tools),
        "max_chars": max(tool.chars for tool in tools),
        "average_chars": round(sum(tool.chars for tool in tools) / len(tools), 1),
        "by_category": {
            category_id: len([tool for tool in tools if tool.category_id == category_id])
            for category_id in CATEGORIES
        },
    }
    (ROOT / "content" / "article_stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")


def write_page(
    path: Path,
    title: str,
    description: str,
    content: str,
    prefix: str,
    schema: dict | None = None,
    canonical: str | None = None,
) -> None:
    adsense = ""
    if ADSENSE_CLIENT:
        adsense = f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={html.escape(ADSENSE_CLIENT)}" crossorigin="anonymous"></script>'
    schema_tag = f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>' if schema else ""
    canonical_tag = f'<link rel="canonical" href="{html.escape(canonical)}">' if canonical else ""
    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description)}">
  {canonical_tag}
  <link rel="stylesheet" href="{prefix}assets/styles.css">
  {adsense}
  {schema_tag}
</head>
<body>
  <header class="site-header">
    <a class="brand" href="{prefix}index.html"><span>AI</span>{SITE_NAME}</a>
    <nav>
      <a href="{prefix}index.html">导航</a>
      <a href="{prefix}about.html">关于</a>
      <a href="{prefix}privacy.html">隐私与广告</a>
      <a href="{prefix}contact.html">提交工具</a>
    </nav>
  </header>
  <main>{content}</main>
  <footer>
    <p>{SITE_NAME} · 工具信息以官网为准 · 广告位只使用清晰标签，不诱导点击。</p>
  </footer>
  <script src="{prefix}assets/app.js" defer></script>
</body>
</html>
"""
    path.write_text(page, encoding="utf-8")


def tool_card(tool: Tool, prefix: str) -> str:
    initials = html.escape(tool.name[:2].upper())
    return f"""
    <a class="tool-card" href="{prefix}articles/{tool.slug}.html" style="--accent:{tool.color}">
      <span class="logo">{initials}</span>
      <span class="pill">{html.escape(tool.category_keyword)}</span>
      <strong>{html.escape(tool.name)}</strong>
      <p>{html.escape(tool.description)}</p>
    </a>
    """


def ad_slot(slot_id: str) -> str:
    if ADSENSE_CLIENT:
        return f"""
        <aside class="ad-slot" aria-label="Advertisements">
          <span>Advertisements</span>
          <ins class="adsbygoogle" style="display:block" data-ad-client="{html.escape(ADSENSE_CLIENT)}" data-ad-slot="{html.escape(slot_id)}" data-ad-format="auto" data-full-width-responsive="true"></ins>
          <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
        </aside>
        """
    return f"""
    <aside class="ad-slot placeholder" aria-label="Advertisements">
      <span>Advertisements</span>
      <strong>广告位 {html.escape(slot_id)}</strong>
      <p>上线 AdSense 后替换为真实广告单元。这里保留尺寸，避免布局跳动。</p>
    </aside>
    """


def article_schema(tool: Tool) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": tool.title,
        "description": tool.description,
        "datePublished": TODAY,
        "dateModified": TODAY,
        "author": {"@type": "Organization", "name": SITE_NAME},
        "mainEntityOfPage": f"{BASE_URL}/articles/{tool.slug}.html",
    }


def markdownish_to_html(text: str) -> str:
    paragraphs = [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]
    html_parts = []
    for index, paragraph in enumerate(paragraphs):
        if index == 1:
            html_parts.append("<h2>适用场景与核心价值</h2>")
        if index == 3:
            html_parts.append("<h2>选择建议与 SEO 运营方式</h2>")
        if index == len(paragraphs) - 1:
            html_parts.append("<h2>常见问题</h2>")
        html_parts.append(f"<p>{html.escape(paragraph)}</p>")
    return "\n".join(html_parts)


def clean_paragraphs(text: str) -> str:
    return "\n\n".join(
        " ".join(line.strip() for line in paragraph.splitlines() if line.strip())
        for paragraph in textwrap.dedent(text).strip().split("\n\n")
    )


def count_text_chars(text: str) -> int:
    compact = re.sub(r"\s+", "", text)
    return len(compact)


def slugify(value: str) -> str:
    value = value.lower().replace("&", "and")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "tool"


STYLES = """
:root{--paper:#f7f2e8;--ink:#17201b;--muted:#5d665f;--line:#d9d3c5;--panel:#fffdf7;--blue:#244c89;--red:#c8442e;--green:#1f6a55}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:"Microsoft YaHei","PingFang SC","Segoe UI",sans-serif;line-height:1.65}a{color:inherit;text-decoration:none}
.site-header{position:sticky;top:0;z-index:10;display:flex;align-items:center;justify-content:space-between;gap:20px;padding:14px 28px;border-bottom:1px solid var(--line);background:rgba(247,242,232,.92);backdrop-filter:blur(14px)}
.brand{display:flex;align-items:center;gap:10px;font-weight:800}.brand span{display:inline-grid;place-items:center;width:34px;height:34px;background:var(--ink);color:white;border-radius:6px}
nav{display:flex;gap:18px;flex-wrap:wrap;color:var(--muted);font-size:14px}main{width:min(1180px,calc(100% - 32px));margin:0 auto;padding:22px 0 48px}
.directory-head{display:grid;grid-template-columns:minmax(0,1fr) 336px;gap:22px;align-items:stretch;margin:10px 0 22px}.directory-head.compact{margin-top:18px}
.eyebrow{margin:0 0 8px;color:var(--red);font-weight:800;letter-spacing:0;text-transform:uppercase;font-size:13px}h1{font-family:"Noto Serif CJK SC","Source Han Serif SC","SimSun",Georgia,serif;font-size:52px;line-height:1.08;margin:0 0 14px;letter-spacing:0}h2{font-size:24px;margin:28px 0 12px;letter-spacing:0}p{margin:0 0 14px;color:var(--muted)}
.search-panel{padding:16px;border:1px solid var(--line);background:var(--panel);border-radius:8px;margin:16px 0 22px}.search-panel label{display:block;font-weight:800;margin-bottom:8px}.search-panel input{width:100%;padding:14px 16px;border:1px solid var(--line);border-radius:6px;background:white;font-size:16px}
.search-results{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px;margin-top:12px}.search-hit{padding:12px;border:1px solid var(--line);border-radius:8px;background:#fff}.search-hit strong{display:block}
.category-grid,.tool-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(236px,1fr));gap:12px}.category-card,.tool-card{display:block;min-height:142px;padding:14px;border:1px solid var(--line);border-radius:8px;background:var(--panel);transition:transform .16s ease,border-color .16s ease,box-shadow .16s ease}.category-card:hover,.tool-card:hover{transform:translateY(-2px);border-color:var(--accent);box-shadow:0 8px 24px rgba(23,32,27,.08)}
.category-card span,.pill{display:inline-block;color:var(--accent);font-weight:800;font-size:13px}.category-card strong,.tool-card strong{display:block;font-size:20px;margin:8px 0 6px}.category-card em{font-style:normal;color:var(--muted)}
.logo{display:inline-grid;place-items:center;width:42px;height:42px;margin-right:8px;background:var(--accent);color:white;border-radius:8px;font-size:12px;font-weight:900}.tool-card p{font-size:14px;margin-top:10px}.pill{float:right;padding:3px 8px;border:1px solid color-mix(in srgb,var(--accent),white 72%);border-radius:999px;background:#fff}
.ad-slot{display:flex;flex-direction:column;justify-content:center;min-height:160px;padding:14px;border:1px dashed #a99f8d;background:#fffaf0;border-radius:8px;color:var(--muted)}.ad-slot span{font-size:12px;text-transform:uppercase;color:#8b7f6d}.ad-slot strong{color:var(--ink)}
.article{max-width:820px;margin:18px auto;padding:22px;border:1px solid var(--line);background:var(--panel);border-radius:8px}.article h1{font-size:44px}.summary{font-size:18px;color:#445047}.breadcrumb{font-size:13px;color:var(--muted);margin-bottom:12px}.related ul{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:8px;padding-left:18px}
footer{border-top:1px solid var(--line);padding:24px;text-align:center;color:var(--muted);font-size:14px}
@media(max-width:820px){.site-header{align-items:flex-start;flex-direction:column;padding:12px 16px}.directory-head{grid-template-columns:1fr}h1{font-size:34px}.article h1{font-size:32px}.article{padding:16px}.category-grid,.tool-grid{grid-template-columns:1fr}}
"""


APP_JS = """
const input = document.querySelector('#toolSearch');
const results = document.querySelector('#searchResults');
if (input && results) {
  fetch('assets/search-index.json')
    .then(response => response.json())
    .then(items => {
      input.addEventListener('input', () => {
        const query = input.value.trim().toLowerCase();
        if (!query) { results.innerHTML = ''; return; }
        const hits = items.filter(item =>
          [item.name, item.title, item.category, item.keyword, item.description].join(' ').toLowerCase().includes(query)
        ).slice(0, 12);
        results.innerHTML = hits.map(item => `
          <a class="search-hit" href="${item.url}">
            <strong>${escapeHtml(item.name)}</strong>
            <span>${escapeHtml(item.category)} · ${escapeHtml(item.keyword)}</span>
          </a>
        `).join('');
      });
    });
}
function escapeHtml(value) {
  return value.replace(/[&<>"']/g, character => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[character]));
}
"""


if __name__ == "__main__":
    main()
