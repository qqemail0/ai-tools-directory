SITE_NAME = "AI工具导航库"
SITE_TAGLINE = "面向效率、创作、开发与商业增长的 AI 工具导航"

CATEGORIES = {
    "writing": {
        "name": "写作与内容",
        "keyword": "AI写作工具",
        "intent": "提升选题、草稿、改写、SEO内容生产效率",
        "color": "#1f6a55",
    },
    "research": {
        "name": "搜索与研究",
        "keyword": "AI搜索工具",
        "intent": "帮助用户更快找到资料、论文、引用和答案",
        "color": "#244c89",
    },
    "image": {
        "name": "图像与设计",
        "keyword": "AI绘图工具",
        "intent": "生成图片、海报、商品图和品牌视觉素材",
        "color": "#c8442e",
    },
    "video": {
        "name": "视频与动画",
        "keyword": "AI视频工具",
        "intent": "生成短视频、数字人、字幕、剪辑和动画内容",
        "color": "#6b4f9a",
    },
    "coding": {
        "name": "代码与开发",
        "keyword": "AI编程工具",
        "intent": "辅助写代码、查问题、生成界面和自动化开发流程",
        "color": "#202124",
    },
    "office": {
        "name": "办公与效率",
        "keyword": "AI办公工具",
        "intent": "处理会议、文档、任务、幻灯片和团队协作",
        "color": "#8a5a2b",
    },
    "marketing": {
        "name": "营销与增长",
        "keyword": "AI营销工具",
        "intent": "优化广告素材、SEO、社媒、邮件和销售线索",
        "color": "#0f766e",
    },
    "audio": {
        "name": "音频与语音",
        "keyword": "AI语音工具",
        "intent": "生成配音、音乐、播客、降噪和语音处理内容",
        "color": "#9f1239",
    },
    "data": {
        "name": "数据与分析",
        "keyword": "AI数据分析工具",
        "intent": "分析表格、生成图表、理解指标和预测趋势",
        "color": "#155e75",
    },
    "automation": {
        "name": "智能体与自动化",
        "keyword": "AI自动化工具",
        "intent": "搭建工作流、客服机器人、智能体和自动化任务",
        "color": "#365314",
    },
}

TOOLS_BY_CATEGORY = {
    "writing": [
        "ChatGPT", "Claude", "Gemini", "Poe", "Jasper", "Copy.ai", "Writesonic", "Rytr",
        "Notion AI", "GrammarlyGO", "QuillBot", "Wordtune", "Anyword", "Sudowrite",
        "Writer", "HyperWrite", "DeepL Write", "Cohesive AI", "Frase", "Surfer AI",
        "Scalenut", "ContentShake AI", "Hypotenuse AI", "Neuroflash", "INK",
    ],
    "research": [
        "Perplexity", "Consensus", "Elicit", "Scite", "Semantic Scholar", "Research Rabbit",
        "Connected Papers", "Scholarcy", "Iris.ai", "SciSpace", "Explainpaper", "Jenni AI",
        "Paperpal", "Humata", "ChatPDF", "AskYourPDF", "NotebookLM", "You.com", "Komo",
        "Andi", "Phind", "Genspark", "Exa", "Brave Leo", "Arc Search",
    ],
    "image": [
        "Midjourney", "DALL-E", "Stable Diffusion", "Adobe Firefly", "Leonardo AI",
        "Ideogram", "Canva AI", "Krea AI", "Playground AI", "Recraft", "Freepik AI",
        "Clipdrop", "Magnific AI", "DreamStudio", "BlueWillow", "NightCafe", "Lexica",
        "Artbreeder", "Let's Enhance", "Remove.bg", "Cleanup.pictures", "Mokker AI",
        "Photoroom", "Pebblely", "Flair AI",
    ],
    "video": [
        "Runway", "Pika", "Kling AI", "Luma Dream Machine", "HeyGen", "Synthesia",
        "Descript", "CapCut AI", "VEED AI", "InVideo AI", "Fliki", "OpusClip", "Vidyo.ai",
        "Kaiber", "Colossyan", "D-ID", "Hour One", "Elai", "Steve AI", "Animaker AI",
        "Vyond", "Kapwing AI", "Wisecut", "Captions", "Submagic",
    ],
    "coding": [
        "GitHub Copilot", "Cursor", "Replit AI", "Codeium", "Tabnine", "Sourcegraph Cody",
        "Amazon Q Developer", "JetBrains AI Assistant", "Continue", "CodeRabbit", "Devin",
        "Qodo", "Mutable AI", "Phind", "v0 by Vercel", "Bolt", "Lovable", "Windsurf",
        "Aider", "Supermaven", "Blackbox AI", "AskCodi", "Pieces", "CodeWhisperer",
        "Codiga",
    ],
    "office": [
        "Microsoft Copilot", "Google Gemini Workspace", "ClickUp AI", "Asana Intelligence",
        "Trello AI", "Slack AI", "Zoom AI Companion", "Otter.ai", "Fireflies.ai", "Fathom",
        "tl;dv", "Mem", "Motion", "Reclaim.ai", "Magical", "Zapier AI", "Make AI",
        "Airtable AI", "Coda AI", "Gamma", "Tome", "Beautiful.ai", "SlidesAI", "Taskade",
        "SaneBox AI",
    ],
    "marketing": [
        "HubSpot AI", "Semrush AI", "Ahrefs AI", "Clearscope", "MarketMuse", "AdCreative.ai",
        "Pencil", "Predis.ai", "Ocoya", "Hootsuite OwlyWriter", "Buffer AI Assistant",
        "Lately.ai", "Flick", "Taplio", "Typefully", "Clay", "Apollo AI", "Instantly AI",
        "Lavender", "Smartlead", "Mailchimp AI", "Klaviyo AI", "Manychat AI", "Brand24 AI",
        "Canva Magic Write",
    ],
    "audio": [
        "ElevenLabs", "PlayHT", "Murf AI", "Speechify", "Resemble AI", "LOVO", "WellSaid Labs",
        "Descript Overdub", "Adobe Podcast", "Krisp", "Auphonic", "Cleanvoice", "Podcastle",
        "Riverside AI", "Suno", "Udio", "Soundraw", "AIVA", "Boomy", "Mubert", "Lalal.ai",
        "Moises", "Riffusion", "Kits AI", "Voicemod",
    ],
    "data": [
        "ChatGPT Advanced Data Analysis", "Julius AI", "Tableau AI", "Power BI Copilot",
        "ThoughtSpot Sage", "Akkio", "Obviously AI", "MonkeyLearn", "Polymer", "DataRobot",
        "Dataiku", "KNIME AI", "Hex Magic", "Mode AI", "Rows AI", "Equals AI", "Formula Bot",
        "SheetAI", "Numerous.ai", "Looker Gemini", "Qlik Answers", "Vanna AI", "PandasAI",
        "Deepnote AI", "Seek AI",
    ],
    "automation": [
        "Zapier Agents", "Lindy", "AgentGPT", "AutoGPT", "CrewAI", "LangChain", "Flowise",
        "Dify", "n8n AI", "Gumloop", "Bardeen AI", "Browse AI", "Relevance AI", "Stack AI",
        "Voiceflow", "Botpress", "Intercom Fin", "Zendesk AI", "Ada", "Tidio AI",
        "CustomGPT.ai", "Chatbase", "Botsonic", "Forethought", "Dust",
    ],
}
