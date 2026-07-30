"""
Agent 1: 需求理解 (NLU)
将用户自然语言输入解析为结构化检索参数
"""
import re
from dataclasses import dataclass, field


@dataclass
class SearchRequest:
    """结构化检索需求"""
    topics: list[str] = field(default_factory=list)
    start_year: str = ""
    end_year: str = ""
    source: str = ""           # CSSCI / CSCD / SCI / EI / 北大核心
    max_count: int = 20
    language: str = "中文"
    doc_type: str = "期刊"     # 期刊 / 博士 / 硕士
    need_pdf: bool = True
    need_review: bool = False
    author: str = ""
    journal: str = ""
    raw_input: str = ""


# 中文数字映射
CN_NUM_MAP = {"一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5,
              "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
              "十一": 11, "十二": 12, "十五": 15, "二十": 20}


def _cn_to_int(s: str) -> int:
    """将中文数字或阿拉伯数字字符串转为int"""
    s = s.strip()
    if s.isdigit():
        return int(s)
    if s in CN_NUM_MAP:
        return CN_NUM_MAP[s]
    # 处理 "十X" 形式
    if s.startswith("十") and len(s) == 2:
        return 10 + CN_NUM_MAP.get(s[1], 0)
    return 5  # 默认


# 时间表达映射（支持中文数字和阿拉伯数字）
TIME_PATTERNS = [
    (r"近([\d一二两三四五六七八九十]+)年", lambda m: _cn_to_int(m.group(1))),
    (r"最近([\d一二两三四五六七八九十]+)年", lambda m: _cn_to_int(m.group(1))),
    (r"(\d{4})\s*[-–~至到]\s*(\d{4})", lambda m: (m.group(1), m.group(2))),
    (r"(\d{4})年以[来后]", lambda m: (m.group(1), "")),
]

# 来源识别
SOURCE_KEYWORDS = {
    "cssci": "CSSCI",
    "c刊": "CSSCI",
    "cssci": "CSSCI",
    "南大核心": "CSSCI",
    "cscd": "CSCD",
    "sci": "SCI",
    "ei": "EI",
    "北大核心": "hx",
    "核心": "hx",
}

# 文献类型
DOC_TYPE_KEYWORDS = {
    "期刊": "期刊", "论文": "期刊", "文章": "期刊",
    "博士": "博士", "博士论文": "博士",
    "硕士": "硕士", "硕士论文": "硕士",
    "学位论文": "学位论文",
}


def parse_request(user_input: str) -> SearchRequest:
    """解析用户自然语言为结构化检索需求"""
    req = SearchRequest(raw_input=user_input)
    text = user_input.lower()

    # 1. 提取时间
    from datetime import datetime
    current_year = datetime.now().year

    for pat, handler in TIME_PATTERNS:
        m = re.search(pat, user_input)
        if m:
            result = handler(m)
            if isinstance(result, tuple):
                req.start_year = result[0]
                req.end_year = result[1] or str(current_year)
            else:
                years = result if isinstance(result, int) else int(result)
                req.start_year = str(current_year - years)
                req.end_year = str(current_year)
            break

    # 2. 识别来源
    for kw, src in SOURCE_KEYWORDS.items():
        if kw in text:
            req.source = src
            break

    # 3. 识别文献类型
    for kw, dt in DOC_TYPE_KEYWORDS.items():
        if kw in text:
            req.doc_type = dt
            break

    # 4. 提取数量
    count_match = re.search(r"(\d+)\s*篇", user_input)
    if count_match:
        req.max_count = int(count_match.group(1))

    # 5. 是否需要PDF
    if "不要pdf" in text or "不需要pdf" in text or "不用下载" in text:
        req.need_pdf = False
    elif "pdf" in text or "下载" in text or "全文" in text:
        req.need_pdf = True

    # 6. 是否需要综述
    if "综述" in text or "调研报告" in text or "文献报告" in text:
        req.need_review = True

    # 7. 提取主题（去掉修饰词后的核心内容）
    # 简单策略：去掉时间、来源、数量等修饰，剩余为主题
    topic_text = user_input
    topic_text = re.sub(r"近[\d一二两三四五六七八九十]+年|最近[\d一二两三四五六七八九十]+年|\d{4}\s*[-–~至到]\s*\d{4}", "", topic_text)
    topic_text = re.sub(r"(cssci|cscd|sci|ei|北大核心|核心|c刊)", "", topic_text, flags=re.I)
    topic_text = re.sub(r"\d+\s*篇", "", topic_text)
    topic_text = re.sub(r"(期刊|论文|文章|博士|硕士|学位论文)", "", topic_text)
    topic_text = re.sub(r"(最好|需要|我要|研究|关于|帮我|找|搜|检索|下载|pdf|全文|综述|报告)", "", topic_text)
    topic_text = re.sub(r"[，。,.、\s]+", " ", topic_text).strip()

    if topic_text:
        # 按"在...中"、"与"、"和"分割子主题
        parts = re.split(r"[在中的与和及]", topic_text)
        req.topics = [p.strip() for p in parts if len(p.strip()) >= 2]

    if not req.topics:
        req.topics = [user_input.strip()]

    return req


def format_request(req: SearchRequest) -> str:
    """格式化输出结构化需求"""
    lines = [
        "=" * 50,
        "需求解析结果",
        "=" * 50,
        f"  研究主题: {' + '.join(req.topics)}",
        f"  时间范围: {req.start_year or '不限'} - {req.end_year or '不限'}",
        f"  来源要求: {req.source or '不限'}",
        f"  文献类型: {req.doc_type}",
        f"  目标数量: {req.max_count} 篇",
        f"  语言: {req.language}",
        f"  需要PDF: {'是' if req.need_pdf else '否'}",
        f"  需要综述: {'是' if req.need_review else '否'}",
    ]
    if req.author:
        lines.append(f"  指定作者: {req.author}")
    if req.journal:
        lines.append(f"  指定期刊: {req.journal}")
    lines.append("=" * 50)
    return "\n".join(lines)
