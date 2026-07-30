# CNKI Scholar Copilot

> 知网文献研究助手 — 理解需求、智能检索、评分筛选、作者分析、自动整理

## 它是什么

不是简单的"论文下载器"，而是一位完整的学术研究助手：

1. **理解你的需求** — 用自然语言描述研究主题，自动解析为结构化参数
2. **帮你搜** — 自动扩展同义词、构建专业检索式、多轮降级搜索
3. **帮你筛** — 7维度评分（引用/核心/基金/期刊/时效/摘要/匹配），只留Top-N
4. **帮你分析** — 核心作者画像、机构分布、合作网络、高频关键词、时间趋势
5. **帮你整理** — 下载PDF + 生成Excel + 输出文献调研报告

## 快速开始

`ash
# 1. 启动Chrome（远程调试模式）
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222

# 2. 安装依赖
pip install playwright openpyxl

# 3. 设置CNKI模块路径
set CNKI_SKILL_DIR=C:\Users\<用户名>\.codex\skills\_shared\cnki

# 4. 运行
python -m copilot "数字人文在高校图书馆中的应用，近五年，CSSCI，20篇"
`

## 使用示例

`ash
# 自然语言（推荐）
python -m copilot "AI图书馆"
python -m copilot "区块链+供应链金融，近3年，北大核心，15篇"
python -m copilot "深度学习在医学影像诊断中的应用" --no-pdf

# 参数化
python -m copilot --query "知识图谱" --count 30 --source CSSCI --output ./research/
`

## 输出

`
数字人文_高校图书馆/
├── PDF/                 # Top-N 论文PDF（需登录权限）
├── 论文信息.xlsx        # 评分排序的推荐论文（含摘要、关键词）
├── 作者分析.xlsx        # 核心作者 / 机构分布 / 高频关键词
├── 参考文献.xlsx        # 全部检索结果
└── 研究报告.md          # 完整文献调研报告
`

## 架构

`
用户 → ①NLU → ②检索策略 → ③知网搜索 → ④评分 → ⑤作者分析 → ⑥PDF整理 → 输出
`

| Agent | 职责 |
|-------|------|
| ① 需求理解 | 解析自然语言 → 结构化参数 |
| ② 检索策略 | 同义词扩展、构建检索式、降级方案 |
| ③ 知网搜索 | 浏览器自动化高级检索 + 批量详情提取 |
| ④ 论文评分 | 7维度打分，筛选Top-N |
| ⑤ 作者分析 | 作者画像、机构、合作、关键词共现 |
| ⑥ PDF整理 | 下载PDF + 生成研究包 |

## 评分体系

| 维度 | 分值 | 说明 |
|------|------|------|
| 引用量 | 0-25 | 被引次数 |
| 核心来源 | 0-15 | CSSCI / 北大核心 / SCI / EI |
| 基金 | 0-10 | 国家级 > 省部级 > 其他 |
| 期刊等级 | 0-15 | 顶刊 / 权威 / 一般 |
| 时效性 | 0-10 | 越新越高 |
| 摘要质量 | 0-10 | 摘要完整度 |
| 主题匹配 | 0-15 | 与检索主题相关度 |

## 依赖

- Python 3.10+
- playwright
- openpyxl
- CNKI shared modules（[cnki-codex-skills](https://github.com/cfh-7598/cnki-codex-skills)）

## 合规说明

本工具仅在用户已拥有合法访问权限（机构授权/个人登录）的前提下，自动化完成用户原本可以手动完成的检索、筛选、整理操作。不绕过任何访问限制或版权机制。

## License

MIT
