---
name: cnki-scholar-copilot
description: 知网文献研究助手。理解用户研究需求，自动生成检索策略，通过浏览器自动化在CNKI高级检索中搜索论文，多维度评分筛选Top-N，分析核心作者与机构，下载PDF并生成完整研究包（Excel+报告）。适用于文献调研、开题报告、综述写作等学术研究场景。
---

# CNKI Scholar Copilot（知网文献研究助手）

不是简单的"论文下载器"，而是一位能够理解研究需求、制定检索策略、评估文献质量、分析作者与机构，并在用户拥有合法访问权限的情况下自动整理和下载论文的智能研究助手。

## 六Agent流水线

`
用户输入（自然语言）
    │
    ▼
① 需求理解Agent ─── 解析为结构化参数（主题/时间/来源/数量）
    │
    ▼
② 检索策略Agent ─── 同义词扩展、构建专业检索式、降级方案
    │
    ▼
③ 知网搜索Agent ─── 浏览器自动化高级检索 + 批量详情提取
    │
    ▼
④ 论文评分Agent ─── 7维度打分（引用/核心/基金/期刊/时效/摘要/匹配）
    │
    ▼
⑤ 作者分析Agent ─── 核心作者画像、机构分布、合作网络、关键词共现
    │
    ▼
⑥ PDF整理Agent ─── 下载Top-N PDF + 生成研究包
    │
    ▼
输出：PDF/ + 论文信息.xlsx + 作者分析.xlsx + 参考文献.xlsx + 研究报告.md
`

## 前置条件

1. Chrome 以远程调试模式运行：
   `ash
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
   `
2. 已在该Chrome中登录知网（如需下载PDF）
3. 安装依赖：pip install playwright openpyxl
4. CNKI shared modules 已安装（来自 cnki-codex-skills）

## 使用方法

### 自然语言输入（推荐）

`ash
python -m copilot "数字人文在高校图书馆中的应用，近五年，CSSCI，20篇"
`

### 参数化输入

`ash
python -m copilot --query "AI图书馆" --count 15 --source CSSCI --output ./research/
`

### 不下载PDF（仅整理元数据）

`ash
python -m copilot "区块链+供应链金融" --no-pdf
`

## 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| query | 研究主题（自然语言） | 必填 |
| --output, -o | 输出目录 | ./output |
| --cdp-url | Chrome CDP地址 | http://127.0.0.1:9222 |
| --count, -n | 目标论文数量 | 20 |
| --source, -s | 来源: CSSCI/CSCD/SCI/EI/hx | 不限 |
| --no-pdf | 不下载PDF | false |

## 输出结构

`
数字人文_高校图书馆/
├── PDF/                    # Top-N 论文PDF
│   ├── 01_xxx.pdf
│   └── ...
├── 论文信息.xlsx           # 评分排序后的推荐论文（含摘要）
├── 作者分析.xlsx           # 核心作者/机构分布/高频关键词
├── 参考文献.xlsx           # 全部检索结果
└── 研究报告.md             # 完整文献调研报告
`

## 评分维度

| 维度 | 分值 | 说明 |
|------|------|------|
| 引用量 | 0-25 | 被引次数 |
| 核心来源 | 0-15 | CSSCI/北大核心/SCI/EI |
| 基金 | 0-10 | 国家级/省部级/其他 |
| 期刊等级 | 0-15 | 顶刊/权威/一般 |
| 时效性 | 0-10 | 发表年份新度 |
| 摘要质量 | 0-10 | 摘要完整度 |
| 主题匹配 | 0-15 | 与检索主题的相关度 |

满分100，默认阈值30分。

## 注意事项

- 知网弹滑块验证码时需手动在Chrome中完成
- PDF下载需要用户已登录且有机构授权
- 不绕过任何访问限制或版权机制
- 建议单次检索不超过50篇目标量
