# AI 工具导航广告站

一个面向 Google 搜索流量和 AdSense 变现的静态 AI 工具导航网站。

## 线上访问

GitHub Pages: http://mo.novaeworld.top/

## 已实现

- 10 个 AI 工具分类，每类 25 个工具，共 250 篇文章。
- 每篇文章标题包含分类关键词，例如 `AI写作工具`、`AI绘图工具`、`AI编程工具`。
- 每篇正文约 1400-1700 字，生成 Markdown 和 HTML 两份。
- 文章页包含快速判断表、适合人群、上手流程、选择风险、替代工具和 FAQ。
- 首页、分类页、文章页、关于、联系、隐私与广告说明页。
- 站内搜索、内部链接、Article JSON-LD、canonical、sitemap.xml、robots.txt。
- AdSense 友好广告位，占位标签统一使用 `Advertisements`。
- `ads.txt.template` 用于替换真实 Google Publisher ID。

## 构建

```powershell
python .\build_site.py
python .\tests\verify_site.py
```

构建产物在 `public/`，可部署到 Cloudflare Pages、Netlify、Vercel、GitHub Pages 或任意静态空间。

## 部署到 GitHub Pages

1. 在 GitHub 新建一个仓库，例如 `ai-tools-directory`。
2. 本地执行：

```powershell
git init
git add .
git commit -m "Initial AI tools directory site"
git branch -M main
git remote add origin https://github.com/你的用户名/ai-tools-directory.git
git push -u origin main
```

3. 打开 GitHub 仓库：`Settings` -> `Pages`。
4. `Build and deployment` 的 `Source` 选择 `GitHub Actions`。
5. 等待 `Deploy GitHub Pages` 工作流完成。

默认发布地址通常是：

```text
https://你的用户名.github.io/ai-tools-directory/
```

如果要写入真实 AdSense ID，在仓库 `Settings` -> `Secrets and variables` -> `Actions` -> `Variables` 里新增：

```text
SITE_BASE_URL=https://你的域名
ADSENSE_CLIENT=ca-pub-你的发布商ID
ADSENSE_PUBLISHER_ID=pub-你的发布商ID
```

## 配置 AdSense

构建前设置：

```powershell
$env:ADSENSE_CLIENT="ca-pub-你的发布商ID"
python .\build_site.py
```

然后把 `ads.txt.template` 中的 `pub-REPLACE_WITH_YOUR_ADSENSE_PUBLISHER_ID` 替换成你的真实 ID，并上传为站点根目录的 `ads.txt`。

如果设置了 `ADSENSE_PUBLISHER_ID`，构建器会自动生成 `public/ads.txt`。

## 重要合规原则

不要要求用户点击广告，不要用箭头、动画、奖励、误导按钮或“支持我们”文案诱导点击。本站模板只做清晰标注的广告位，主要靠 SEO 内容、内部链接和页面体验提高自然流量。
