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
from urllib.parse import urlparse

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
    custom_domain = custom_domain_from_base_url(BASE_URL)
    if custom_domain:
        (PUBLIC / "CNAME").write_text(f"{custom_domain}\n", encoding="utf-8")
    ARTICLES.mkdir(parents=True, exist_ok=True)
    for old in ARTICLES.glob("*.md"):
        old.unlink()


CATEGORY_PROFILES = {
    "writing": {
        "personas": ["内容运营", "独立站站长", "SEO编辑", "社媒创作者"],
        "jobs": ["长文初稿生成", "标题和摘要改写", "产品描述扩写", "邮件和社媒脚本整理"],
        "metrics": ["结构完整度、可读性、事实准确性和品牌语气"],
        "pitfalls": ["必须核对事实、引用、数字和品牌承诺，避免把未验证内容直接发布"],
        "strengths": ["适合快速搭建内容框架，并把零散想法整理成可编辑草稿"],
        "limitations": ["输出容易显得模板化，需要加入真实案例、产品细节和人工观点"],
        "workflow": "brief -> draft -> edit -> publish",
        "evaluation": "看首稿可用率、改稿次数、标题 CTR 和自然搜索表现",
    },
    "research": {
        "personas": ["研究助理", "产品经理", "投资分析师", "学生和知识工作者"],
        "jobs": ["资料检索", "论文和报告速读", "竞品信息整理", "问题拆解和事实核查"],
        "metrics": ["来源透明度、引用质量、覆盖范围和结论可验证性"],
        "pitfalls": ["不能把摘要当作最终事实，关键结论要回到原始来源复核"],
        "strengths": ["适合把陌生主题快速拆成问题清单、关键词和可继续阅读的资料路径"],
        "limitations": ["不同工具对来源展示和引用准确性的处理差异很大"],
        "workflow": "question -> sources -> synthesis -> verification",
        "evaluation": "看引用是否可追溯、是否覆盖反例、是否减少二次搜索时间",
    },
    "image": {
        "personas": ["设计师", "电商运营", "品牌主理人", "广告素材制作人员"],
        "jobs": ["封面图生成", "商品图优化", "广告视觉探索", "品牌风格草案制作"],
        "metrics": ["画面一致性、可控性、版权风险、商用输出质量"],
        "pitfalls": ["商用前要确认素材授权、人物肖像、商标和训练数据相关风险"],
        "strengths": ["适合快速探索多种视觉方向，并把创意从文字变成可讨论的画面"],
        "limitations": ["复杂文字、精确构图和系列一致性仍需要人工精修"],
        "workflow": "prompt -> variations -> refine -> export",
        "evaluation": "看生成稳定性、局部修改能力、分辨率和品牌一致性",
    },
    "video": {
        "personas": ["短视频运营", "课程创作者", "品牌营销团队", "自媒体剪辑师"],
        "jobs": ["脚本转视频", "数字人讲解", "字幕和片段剪辑", "短视频素材再加工"],
        "metrics": ["画面连贯性、音画同步、字幕准确率和导出效率"],
        "pitfalls": ["发布前要检查人物授权、素材版权、事实表述和平台审核风险"],
        "strengths": ["适合缩短从脚本到视频草稿的周期，让团队更快测试创意方向"],
        "limitations": ["长视频叙事、复杂镜头调度和品牌级成片仍需要专业剪辑介入"],
        "workflow": "script -> assets -> generation -> edit -> publish",
        "evaluation": "看成片可用率、重剪成本、导出格式和批量生产能力",
    },
    "coding": {
        "personas": ["全栈开发者", "独立开发者", "技术负责人", "低代码产品团队"],
        "jobs": ["代码补全", "错误排查", "测试用例生成", "原型页面和脚本开发"],
        "metrics": ["代码正确性、安全性、可维护性和测试覆盖"],
        "pitfalls": ["生成代码必须经过审查和测试，尤其是认证、支付、数据库和权限逻辑"],
        "strengths": ["适合减少重复编码和搜索文档时间，帮助开发者更快形成可运行原型"],
        "limitations": ["复杂架构判断、业务边界和安全责任仍必须由工程师把关"],
        "workflow": "issue -> context -> patch -> tests -> review",
        "evaluation": "看能否减少上下文切换、是否通过测试、是否符合项目风格",
    },
    "office": {
        "personas": ["团队负责人", "项目经理", "行政和运营人员", "销售团队"],
        "jobs": ["会议纪要", "任务拆解", "文档总结", "幻灯片和日程整理"],
        "metrics": ["信息完整度、责任人清晰度、协作效率和后续执行率"],
        "pitfalls": ["涉及客户、合同或内部机密时，要检查隐私设置和数据留存方式"],
        "strengths": ["适合把分散信息变成结构化任务和文档，减少沟通损耗"],
        "limitations": ["如果团队流程本身混乱，AI 只能整理信息，不能替代管理决策"],
        "workflow": "capture -> summarize -> assign -> follow-up",
        "evaluation": "看纪要准确率、任务遗漏率、团队采用率和节省时间",
    },
    "marketing": {
        "personas": ["增长负责人", "广告投放人员", "SEO运营", "B2B销售团队"],
        "jobs": ["广告素材生成", "SEO页面规划", "销售邮件撰写", "社媒内容排期"],
        "metrics": ["转化率、点击率、线索质量、内容一致性和测试效率"],
        "pitfalls": ["不要用夸张承诺或虚假稀缺制造点击，广告和落地页必须一致"],
        "strengths": ["适合快速生成多版本创意，帮助团队用数据筛选有效方向"],
        "limitations": ["它不能替代定位、报价、用户洞察和渠道策略"],
        "workflow": "audience -> message -> variations -> test -> optimize",
        "evaluation": "看素材迭代速度、A/B 测试表现和最终线索质量",
    },
    "audio": {
        "personas": ["播客创作者", "课程团队", "短视频剪辑师", "品牌内容团队"],
        "jobs": ["配音生成", "播客清理", "音乐草稿", "降噪和声音素材处理"],
        "metrics": ["声音自然度、情绪控制、授权范围和后期处理成本"],
        "pitfalls": ["克隆声音、音乐商用和人物授权要特别谨慎，避免侵权"],
        "strengths": ["适合让声音内容生产更轻量，尤其适合批量脚本和多语言版本"],
        "limitations": ["高端品牌广告、影视配乐和强表演性声音仍需要专业制作"],
        "workflow": "script -> voice/style -> generation -> mastering -> publish",
        "evaluation": "看听感自然度、噪声控制、导出格式和版权条款",
    },
    "data": {
        "personas": ["业务分析师", "运营负责人", "财务人员", "产品经理"],
        "jobs": ["表格分析", "指标归因", "图表解释", "报表自动化和预测"],
        "metrics": ["计算准确性、可解释性、数据权限和结论复现性"],
        "pitfalls": ["关键指标要用原始数据复算，不能只相信自然语言解释"],
        "strengths": ["适合让非技术人员用自然语言理解数据，降低分析门槛"],
        "limitations": ["脏数据、口径不一致和权限问题仍需要数据治理来解决"],
        "workflow": "data -> question -> analysis -> chart -> decision",
        "evaluation": "看能否复现结论、是否解释口径、是否支持导出和协作",
    },
    "automation": {
        "personas": ["运营自动化负责人", "客服团队", "独立创业者", "内部工具开发者"],
        "jobs": ["工作流编排", "客服机器人", "网页采集", "智能体任务和线索处理"],
        "metrics": ["成功率、失败重试、日志可追踪性和人工接管能力"],
        "pitfalls": ["自动化必须设置权限、审计和回滚，不能让机器人无限制执行敏感动作"],
        "strengths": ["适合把重复流程串起来，让任务从提醒、复制和录入变成自动执行"],
        "limitations": ["跨系统流程越复杂，越需要异常处理、权限边界和人工审批"],
        "workflow": "trigger -> action -> review -> fallback",
        "evaluation": "看执行成功率、维护成本、异常告警和节省人力时间",
    },
}


def build_tools() -> list[Tool]:
    tools: list[Tool] = []
    for category_id, names in TOOLS_BY_CATEGORY.items():
        category = CATEGORIES[category_id]
        for position, name in enumerate(names, start=1):
            slug = f"{category_id}-{slugify(name)}"
            title = f"{name}是什么？{category['keyword']}使用场景、优缺点和替代工具"
            description = (
                f"{name} 适合谁使用？本文从{category['keyword']}搜索意图出发，整理核心场景、"
                f"上手流程、选择风险、同类替代工具和 FAQ。"
            )
            related_names = names[position:position + 4] + names[:max(0, 4 - len(names[position:position + 4]))]
            body = build_article_body(name, category_id, category, position, related_names)
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


def custom_domain_from_base_url(base_url: str) -> str:
    host = urlparse(base_url).netloc
    if not host or host.endswith(".github.io") or host == "example.com":
        return ""
    return host


def build_article_body(name: str, category_id: str, category: dict, position: int, related_names: list[str]) -> str:
    keyword = category["keyword"]
    category_name = category["name"]
    intent = category["intent"]
    profile = CATEGORY_PROFILES[category_id]
    primary_job = profile["jobs"][(position - 1) % len(profile["jobs"])]
    secondary_job = profile["jobs"][position % len(profile["jobs"])]
    persona = profile["personas"][(position + 1) % len(profile["personas"])]
    metric = profile["metrics"][position % len(profile["metrics"])]
    pitfall = profile["pitfalls"][(position + 2) % len(profile["pitfalls"])]
    evaluation = profile["evaluation"]
    alternatives = "、".join(related_names[:4])
    strength = profile["strengths"][position % len(profile["strengths"])]
    limitation = profile["limitations"][position % len(profile["limitations"])]
    body = f"""
    快速结论：{name} 更适合把它当作一个面向“{primary_job}”的{keyword}候选，而不是简单收藏在导航页里等以后再看。正在做{category_name}工作的用户，通常关心三件事：能不能更快完成任务，输出是否足够稳定，以及结果能不能放进真实业务流程。围绕这三个问题评估 {name}，比只看官网宣传语更接近搜索用户的真实需求。

    适合人群：如果你是{persona}，并且正在寻找能够{intent}的工具，{name} 值得进入第一轮筛选。它尤其适合处理{primary_job}，也可以辅助完成{secondary_job}。如果你的团队已经有固定 SOP，建议先把 {name} 放到一个低风险环节里试用，例如草稿、素材整理、初步分析或批量预处理，再决定是否扩大到核心流程。

    核心优势：{strength}。这类{keyword}的价值不只是“生成得快”，更重要的是降低重复劳动，让人把时间放在判断、编辑、审核和策略上。使用 {name} 时，可以把任务拆成“输入目标、提供上下文、生成结果、人工检查、沉淀模板”五步。这样做的好处是每次输出都有可复用的标准，而不是临时对话一次就结束。

    上手流程：第一步，准备一个非常具体的任务，不要只输入“帮我做一下”。第二步，补充目标受众、格式、语气、限制条件和示例。第三步，用 {metric} 作为检查标准。第四步，把表现好的输入保存为模板。第五步，定期复盘哪些任务适合交给 {name}，哪些任务仍然应该由人完成，复盘时可以重点看{evaluation}。这个流程能显著提高稳定性，也更容易在团队里复制。

    可能限制：{limitation}。很多工具在演示页面看起来很强，但真正用于商业项目时，还要检查价格、导出格式、数据隐私、版权条款、中文支持、协作权限和历史记录。对于需要发布到公开渠道的内容，{pitfall}。因此，{name} 更适合被视为提效工具，而不是完全替代专业人员的自动机器。

    选择建议：评估 {name} 时，可以从四个角度判断。第一，核心任务是否覆盖你的主场景；第二，生成结果是否稳定，是否需要大量返工；第三，是否能和现有工具协同，例如文档、表格、设计软件、代码仓库或自动化平台；第四，长期成本是否可控。如果这些答案都比较清楚，{name} 就更适合进入正式试用。

    替代工具：同类页面可以继续比较 {alternatives}。如果你更在意免费额度，可以优先看入门限制；如果你更在意团队落地，要看权限、版本管理和导出能力；如果你面向中文市场，还要重点检查中文理解、术语一致性和本地化效果。不要只看单个工具，横向比较通常能更快找到合适方案。

    搜索意图与决策建议：多数用户搜索“{keyword}推荐”“{name}是什么”“{name}替代工具”时，并不是只想看到一句简介，而是想快速判断它是否适合自己的场景。阅读这一类工具页时，建议把注意力放在适用任务、限制条件、替代方案和成本上。只要这些问题回答清楚，就能减少反复搜索，也能更快做出试用或放弃的决定。

    常见问题：{name} 适合新手吗？适合，但建议从单一任务开始，不要一上来就替代完整流程。{name} 可以直接商用吗？要看具体输出、授权和隐私条款，发布前仍需要人工审核。{name} 值得付费吗？如果它能持续节省时间、减少返工，并且输出能进入正式业务流程，付费才更有意义。
    """
    body = clean_paragraphs(body)
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
          {tool_fact_table(tool)}
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


def tool_fact_table(tool: Tool) -> str:
    names = TOOLS_BY_CATEGORY[tool.category_id]
    position = names.index(tool.name) + 1
    profile = CATEGORY_PROFILES[tool.category_id]
    primary_job = profile["jobs"][(position - 1) % len(profile["jobs"])]
    metric = profile["metrics"][position % len(profile["metrics"])]
    alternatives = "、".join((names[position:position + 3] + names[:max(0, 3 - len(names[position:position + 3]))])[:3])
    rows = [
        ("推荐场景", primary_job),
        ("适合人群", profile["personas"][(position + 1) % len(profile["personas"])]),
        ("评估重点", metric),
        ("可比较工具", alternatives),
    ]
    return f"""
    <table class="fact-table">
      <tbody>
        {"".join(f"<tr><th>{html.escape(label)}</th><td>{html.escape(value)}</td></tr>" for label, value in rows)}
      </tbody>
    </table>
    <p class="editor-note">编辑提示：AI 工具功能、价格和授权条款变化很快，正式采购或商用前建议以官网信息和实际试用结果为准。</p>
    """


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
            html_parts.append("<h2>适合人群与使用场景</h2>")
        if index == 3:
            html_parts.append("<h2>上手流程与评估标准</h2>")
        if index == 5:
            html_parts.append("<h2>选择建议与替代工具</h2>")
        if index == 7:
            html_parts.append("<h2>SEO 价值与常见问题</h2>")
        if index == len(paragraphs) - 1:
            html_parts.append("<h2>FAQ</h2>")
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
.fact-table{width:100%;border-collapse:collapse;margin:18px 0;border:1px solid var(--line);background:#fff}.fact-table th,.fact-table td{padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}.fact-table th{width:116px;text-align:left;color:var(--ink);background:#f2eadc}.fact-table td{color:#445047}.editor-note{padding:10px 12px;border-left:4px solid var(--green);background:#eef7f1;color:#3e5548;border-radius:4px}
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
