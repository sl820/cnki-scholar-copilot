"""
Agent 2: 检索策略优化
将用户模糊主题扩展为专业检索式
"""
import re
from dataclasses import dataclass, field


@dataclass
class SearchStrategy:
    """检索策略"""
    core_terms: list[str] = field(default_factory=list)
    object_terms: list[str] = field(default_factory=list)
    direction_terms: list[str] = field(default_factory=list)
    search_expression: str = ""
    cnki_query: str = ""       # 实际用于CNKI搜索框的查询
    fallback_queries: list[str] = field(default_factory=list)


# 同义词/扩展词知识库（按领域）
SYNONYM_MAP = {
    "人工智能": ["AI", "AIGC", "生成式人工智能", "大语言模型", "LLM", "深度学习", "机器学习"],
    "数字人文": ["数字人文", "DH", "数字学术", "数字文化", "人文计算"],
    "图书馆": ["高校图书馆", "公共图书馆", "数字图书馆", "智慧图书馆", "大学图书馆"],
    "知识服务": ["知识服务", "知识组织", "知识管理", "学科服务", "情报服务"],
    "大数据": ["大数据", "数据挖掘", "数据分析", "数据驱动", "数据治理"],
    "区块链": ["区块链", "分布式账本", "智能合约", "去中心化"],
    "元宇宙": ["元宇宙", "虚拟现实", "VR", "AR", "数字孪生", "沉浸式"],
    "教育": ["高等教育", "教学改革", "课程建设", "人才培养", "教育数字化"],
    "医疗": ["临床", "诊断", "治疗", "医学", "健康"],
    "经济": ["经济增长", "产业发展", "数字经济", "高质量发展"],
    "环境": ["生态环境", "碳中和", "绿色发展", "可持续发展", "双碳"],
    "安全": ["网络安全", "信息安全", "数据安全", "隐私保护"],
}

# 对象扩展
OBJECT_EXPANSIONS = {
    "图书馆": ["高校图书馆", "公共图书馆", "数字图书馆", "智慧图书馆"],
    "教育": ["高校", "大学", "职业教育", "基础教育"],
    "医疗": ["医院", "社区卫生", "公共卫生"],
    "企业": ["中小企业", "制造业", "互联网企业"],
    "政府": ["政府治理", "公共服务", "数字政府"],
}


def build_strategy(topics: list[str]) -> SearchStrategy:
    """根据主题列表生成检索策略"""
    strategy = SearchStrategy()

    all_terms = []
    for topic in topics:
        expanded = expand_topic(topic)
        all_terms.extend(expanded)

    # 分类：核心词 vs 对象词 vs 方向词
    for term in all_terms:
        if any(obj in term for obj in ["图书馆", "医院", "学校", "企业", "政府", "平台"]):
            if term not in strategy.object_terms:
                strategy.object_terms.append(term)
        elif len(term) <= 4:
            if term not in strategy.core_terms:
                strategy.core_terms.append(term)
        else:
            if term not in strategy.direction_terms:
                strategy.direction_terms.append(term)

    # 如果没有明确分类，全部作为核心词
    if not strategy.core_terms and not strategy.object_terms:
        strategy.core_terms = topics[:]

    # 构建CNKI搜索表达式
    strategy.cnki_query = build_cnki_query(strategy)
    strategy.search_expression = build_formal_expression(strategy)

    # 生成降级查询（如果主查询结果太少）
    strategy.fallback_queries = build_fallbacks(strategy)

    return strategy


def expand_topic(topic: str) -> list[str]:
    """扩展单个主题词"""
    terms = [topic]
    topic_lower = topic.lower()

    for key, synonyms in SYNONYM_MAP.items():
        if key in topic or topic in key:
            terms.extend(synonyms)

    for key, expansions in OBJECT_EXPANSIONS.items():
        if key in topic:
            terms.extend(expansions)

    # 去重保序
    seen = set()
    result = []
    for t in terms:
        if t not in seen:
            seen.add(t)
            result.append(t)
    return result


def build_cnki_query(strategy: SearchStrategy) -> str:
    """构建CNKI搜索框查询（主题检索）"""
    parts = []

    if strategy.core_terms:
        core = " OR ".join(strategy.core_terms[:5])
        parts.append(f"({core})" if len(strategy.core_terms) > 1 else core)

    if strategy.object_terms:
        obj = " OR ".join(strategy.object_terms[:4])
        parts.append(f"({obj})" if len(strategy.object_terms) > 1 else obj)

    if parts:
        return " AND ".join(parts)

    if strategy.direction_terms:
        return " OR ".join(strategy.direction_terms[:5])

    return ""


def build_formal_expression(strategy: SearchStrategy) -> str:
    """构建正式检索式（展示用）"""
    lines = []
    if strategy.core_terms:
        lines.append(f"核心概念: ({' OR '.join(strategy.core_terms[:6])})")
    if strategy.object_terms:
        lines.append(f"研究对象: ({' OR '.join(strategy.object_terms[:5])})")
    if strategy.direction_terms:
        lines.append(f"研究方向: ({' OR '.join(strategy.direction_terms[:5])})")
    return "\n  AND\n".join(lines)


def build_fallbacks(strategy: SearchStrategy) -> list[str]:
    """生成降级查询"""
    fallbacks = []
    # 只用核心词
    if strategy.core_terms:
        fallbacks.append(" OR ".join(strategy.core_terms[:3]))
    # 只用对象词+第一个核心词
    if strategy.object_terms and strategy.core_terms:
        fallbacks.append(f"{strategy.core_terms[0]} AND {strategy.object_terms[0]}")
    # 最简：只用第一个主题
    if strategy.core_terms:
        fallbacks.append(strategy.core_terms[0])
    return fallbacks


def format_strategy(strategy: SearchStrategy) -> str:
    """格式化输出检索策略"""
    lines = [
        "=" * 50,
        "检索策略",
        "=" * 50,
        f"  核心词: {', '.join(strategy.core_terms[:8])}",
        f"  对象词: {', '.join(strategy.object_terms[:6])}",
        f"  方向词: {', '.join(strategy.direction_terms[:6])}",
        "",
        "  正式检索式:",
        f"  {strategy.search_expression}",
        "",
        f"  CNKI查询: {strategy.cnki_query}",
        "",
        f"  降级方案: {len(strategy.fallback_queries)} 个",
        "=" * 50,
    ]
    return "\n".join(lines)
