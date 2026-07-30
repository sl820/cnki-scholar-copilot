<div align="center">

# 🎓 CNKI Scholar Copilot

### 知网文献研究助手

**理解需求 → 智能检索 → 评分筛选 → 作者分析 → 自动整理**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-Automated-green.svg)](https://playwright.dev/)
[![CNKI](https://img.shields.io/badge/CNKI-kns.cnki.net-red.svg)](https://www.cnki.net/)

</div>

---

## 📖 简介

**CNKI Scholar Copilot** 不是简单的"论文下载器"，而是一位完整的学术研究助手。

它能理解你的研究需求，自动构建专业检索式，通过浏览器自动化在知网高级检索中搜索论文，对结果进行多维度评分筛选，分析核心作者与机构分布，最终生成一份包含 PDF、Excel、调研报告的完整研究包。

> 💡 很多人不会搜论文。这个 Skill 帮你搜、帮你筛、帮你整理。

---

## ✨ 核心特性

| 特性 | 说明 |
|:---:|------|
| 🧠 **自然语言输入** | 直接说"数字人文在高校图书馆中的应用，近五年，CSSCI，20篇" |
| 🔍 **智能检索扩展** | 自动扩展同义词（AI→AIGC/大语言模型/LLM），构建 OR+AND 专业检索式 |
| 📊 **7维度评分** | 引用量、核心来源、基金、期刊等级、时效性、摘要质量、主题匹配 |
| 👤 **作者画像** | 核心作者识别、机构分布、合作网络、H-index 估算 |
| 📦 **一键研究包** | PDF + 论文信息.xlsx + 作者分析.xlsx + 参考文献.xlsx + 研究报告.md |
| 🔄 **断点续跑** | 中断后自动跳过已完成项 |
| 🛡️ **合规设计** | 仅在用户已有合法权限时自动下载，不绕过任何访问限制 |

---

## 🏗️ 架构

`mermaid
graph TD
    A["👤 用户输入<br/>(自然语言)"] --> B["① 需求理解 Agent<br/>NLU 解析"]
    B --> C["② 检索策略 Agent<br/>同义词扩展 + 检索式"]
    C --> D["③ 知网搜索 Agent<br/>浏览器自动化"]
    D --> E["④ 论文评分 Agent<br/>7维度打分"]
    E --> F["⑤ 作者分析 Agent<br/>画像 + 机构 + 合作"]
    F --> G["⑥ PDF整理 Agent<br/>下载 + 研究包"]
    G --> H["📦 输出<br/>PDF/ + Excel + 报告"]

    style A fill:#e1f5fe
    style H fill:#e8f5e9
    style D fill:#fff3e0
    style E fill:#fce4ec
`

### 六 Agent 流水线

`
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  用户: "数字人文在高校图书馆中的应用，近五年，CSSCI，20篇"            │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ① NLU Agent          ② Strategy Agent       ③ Search Agent        │
│  ┌──────────────┐     ┌──────────────┐       ┌──────────────┐      │
│  │ 主题: 数字人文│     │ 核心词:       │       │ Chrome CDP   │      │
│  │ 对象: 高校图书馆│   │  数字人文     │       │ 高级检索     │      │
│  │ 时间: 2021-2026│    │  OR DH       │       │ 翻页采集     │      │
│  │ 来源: CSSCI   │     │  OR 人文计算  │       │ 详情提取     │      │
│  │ 数量: 20      │     │ AND          │       │ 降级搜索     │      │
│  └──────────────┘     │  高校图书馆   │       └──────────────┘      │
│                        │  OR 智慧图书馆│                              │
│                        └──────────────┘                              │
│                                                                     │
│  ④ Scoring Agent      ⑤ Author Agent         ⑥ PDF Agent           │
│  ┌──────────────┐     ┌──────────────┐       ┌──────────────┐      │
│  │ 引用量  0-25 │     │ 核心作者 TOP │       │ 下载 Top-N   │      │
│  │ 核心    0-15 │     │ 机构分布     │       │ 生成 Excel   │      │
│  │ 基金    0-10 │     │ 合作网络     │       │ 生成报告     │      │
│  │ 期刊    0-15 │     │ 关键词共现   │       │ 整理目录     │      │
│  │ 时效    0-10 │     │ 年份趋势     │       │              │      │
│  │ 摘要    0-10 │     └──────────────┘       └──────────────┘      │
│  │ 匹配    0-15 │                                                   │
│  └──────────────┘                                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
`

---

## 🚀 快速开始

### 环境准备

`ash
# 1. 启动 Chrome（远程调试模式）
# Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222

# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

# Linux
google-chrome --remote-debugging-port=9222
`

`ash
# 2. 安装依赖
pip install playwright openpyxl
python -m playwright install chromium

# 3. 设置 CNKI 共享模块路径
# Windows
set CNKI_SKILL_DIR=C:\Users\<用户名>\.codex\skills\_shared\cnki

# Linux/macOS
export CNKI_SKILL_DIR=~/.codex/skills/_shared/cnki
`

### 运行

`ash
# 自然语言输入（推荐）
python -m copilot "数字人文在高校图书馆中的应用，近五年，CSSCI，20篇"

# 更多示例
python -m copilot "AI图书馆"
python -m copilot "区块链+供应链金融，近3年，北大核心，15篇"
python -m copilot "深度学习在医学影像诊断中的应用" --no-pdf

# 参数化
python -m copilot --query "知识图谱" --count 30 --source CSSCI --output ./research/
`

---

## 📁 输出结构

`
数字人文_高校图书馆/
│
├── 📂 PDF/                         # Top-N 论文 PDF（需登录权限）
│   ├── 01_数字人文视域下高校图书馆...pdf
│   ├── 02_智慧图书馆知识服务...pdf
│   └── ...
│
├── 📄 论文信息.xlsx                 # 评分排序的推荐论文
│   └── 排名 | 评分 | 标题 | 作者 | 单位 | 期刊 | 年份 | 引用 | 关键词 | 摘要
│
├── 📄 作者分析.xlsx                 # 三个 Sheet
│   ├── 核心作者（姓名/单位/论文数/引用/推荐度）
│   ├── 机构分布（机构/论文数）
│   └── 高频关键词（关键词/频次）
│
├── 📄 参考文献.xlsx                 # 全部检索结果
│   └── 序号 | 标题 | 作者 | 期刊 | 年份 | 引用 | 数据库
│
└── 📄 研究报告.md                   # 完整文献调研报告
    ├── 检索概况
    ├── 检索策略
    ├── 推荐论文 Top-20（含评分星级）
    ├── 核心作者表
    ├── 主要机构
    ├── 高频关键词
    ├── 时间分布
    └── 下载目录
`

---

## 📊 评分体系

每篇论文满分 **100 分**，默认阈值 30 分：

`mermaid
pie title 评分维度权重
    "引用量 (25)" : 25
    "核心来源 (15)" : 15
    "期刊等级 (15)" : 15
    "主题匹配 (15)" : 15
    "基金 (10)" : 10
    "时效性 (10)" : 10
    "摘要质量 (10)" : 10
`

| 维度 | 分值 | 评分规则 |
|------|:----:|----------|
| 📈 引用量 | 0-25 | ≥100次=25, ≥50=20, ≥20=15, ≥10=10, ≥5=6 |
| 🏅 核心来源 | 0-15 | CSSCI/北大核心/SCI/EI = 15, 否则 0 |
| 💰 基金 | 0-10 | 国家级=10, 省部级=7, 其他=4 |
| 📰 期刊等级 | 0-15 | 顶刊=10, 权威=8, 一般=5 |
| ⏰ 时效性 | 0-10 | ≤1年=10, ≤2年=8, ≤3年=6, ≤5年=4 |
| 📝 摘要质量 | 0-10 | ≥200字=10, ≥100字=7, ≥50字=4 |
| 🎯 主题匹配 | 0-15 | 按主题词命中率×15 |

---

## 🔍 检索策略示例

用户输入 "AI图书馆" 时，Agent 自动扩展为：

`
核心概念: (人工智能 OR AIGC OR 生成式人工智能 OR 大语言模型 OR LLM OR 深度学习)
    AND
研究对象: (高校图书馆 OR 公共图书馆 OR 数字图书馆 OR 智慧图书馆)
    AND
研究方向: (知识服务 OR 数字资源 OR 智能问答 OR 知识组织 OR 信息行为 OR 数字人文)
`

如果主查询结果不足，自动触发 **降级搜索**：
1. 只用核心词
2. 核心词 + 第一个对象词
3. 仅第一个主题词

---

## ⚙️ 命令行参数

| 参数 | 缩写 | 说明 | 默认值 |
|------|:----:|------|:------:|
| query | | 研究主题（自然语言） | 必填 |
| --output | -o | 输出目录 | ./output |
| --cdp-url | | Chrome CDP 地址 | http://127.0.0.1:9222 |
| --count | -n | 目标论文数量 | 20 |
| --source | -s | 来源: CSSCI / CSCD / SCI / EI / hx | 不限 |
| --no-pdf | | 不下载 PDF | false |

---

## 🧩 作为 Codex Skill 使用

将本仓库放入 ~/.codex/skills/ 目录，Codex 会自动识别 SKILL.md 并在相关任务中调用。

`ash
cd ~/.codex/skills/
git clone https://github.com/sl820/cnki-scholar-copilot.git
`

Skill 触发描述：
> 知网文献研究助手。理解用户研究需求，自动生成检索策略，通过浏览器自动化在CNKI高级检索中搜索论文，多维度评分筛选Top-N，分析核心作者与机构，下载PDF并生成完整研究包。

---

## 📋 依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | ≥ 3.10 | 运行环境 |
| playwright | ≥ 1.40 | 浏览器自动化 |
| openpyxl | ≥ 3.1 | Excel 读写 |
| CNKI shared modules | — | 知网页面操作（[cnki-codex-skills](https://github.com/cfh-7598/cnki-codex-skills)） |

---

## ❓ FAQ

**Q: 搜索时弹出滑块验证码怎么办？**
A: 脚本会暂停并提示你，去 Chrome 中手动拖动滑块完成验证，然后回终端按回车继续。

**Q: PDF 下载失败？**
A: 需要确保：① 已在 Chrome 中登录知网 ② 账号有机构下载权限 ③ 未达到每日阅读上限。

**Q: 搜索结果太少？**
A: 脚本会自动触发降级查询。如果仍然不够，可以尝试：去掉 --source 限制、增大 --count、用更宽泛的主题词。

**Q: 和 cnki-batch-extract-skill 有什么区别？**
A: cnki-batch-extract-skill 是按**人名+单位**批量提取已知作者的论文；cnki-scholar-copilot 是按**研究主题**智能检索未知文献。两者互补。

**Q: 是否合规？**
A: 本工具仅在用户已拥有合法访问权限的前提下，自动化完成用户原本可以手动完成的检索、筛选、整理操作。不绕过任何访问限制或版权机制。

---

## 🗺️ Roadmap

- [ ] 生成文献综述（基于摘要的 AI 总结）
- [ ] 导出 BibTeX / EndNote 格式
- [ ] 知识图谱可视化（作者合作网络）
- [ ] 支持 Web of Science / Scopus 等多数据库
- [ ] 自动阅读 PDF 并提取方法论
- [ ] 定时监控：新论文提醒

---

## 📜 License

[MIT](LICENSE)

---

<div align="center">

**Made with ❤️ for researchers**

如果这个项目对你有帮助，请给一个 ⭐ Star！

</div>
