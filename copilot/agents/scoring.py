"""
Agent 4: 论文评分
对检索结果进行多维度打分，筛选Top-N
"""
import re
from dataclasses import dataclass


@dataclass
class ScoredPaper:
    """评分后的论文"""
    title: str
    score: float
    score_breakdown: dict
    data: dict  # 原始数据


# 期刊等级映射
JOURNAL_TIERS = {
    "中国社会科学": 10, "学术月刊": 9, "中国图书馆学报": 9,
    "图书情报工作": 8, "大学图书馆学报": 8, "情报学报": 8,
    "图书情报知识": 8, "情报资料工作": 7, "图书馆建设": 7,
    "图书馆杂志": 7, "现代图书情报技术": 7, "数据分析与知识发现": 7,
}


def score_paper(paper: dict, request=None) -> ScoredPaper:
    """
    多维度评分:
    - 引用量 (0-25)
    - 是否核心/CSSCI (0-15)
    - 是否有基金 (0-10)
    - 期刊等级 (0-15)
    - 发布时间新度 (0-10)
    - 摘要质量 (0-10)
    - 关键词匹配度 (0-15)
    """
    breakdown = {}
    total = 0.0

    # 1. 引用量 (0-25)
    citations = _parse_int(paper.get("citations", "0"))
    if citations >= 100:
        breakdown["引用量"] = 25
    elif citations >= 50:
        breakdown["引用量"] = 20
    elif citations >= 20:
        breakdown["引用量"] = 15
    elif citations >= 10:
        breakdown["引用量"] = 10
    elif citations >= 5:
        breakdown["引用量"] = 6
    elif citations >= 1:
        breakdown["引用量"] = 3
    else:
        breakdown["引用量"] = 0
    total += breakdown["引用量"]

    # 2. 是否核心 (0-15)
    database = paper.get("database", "")
    journal = paper.get("journal", "") or paper.get("journalDetail", "")
    is_core = any(k in database for k in ["CSSCI", "北大核心", "CSCD", "SCI", "EI"])
    is_core = is_core or any(k in journal for k in ["核心", "CSSCI"])
    breakdown["核心来源"] = 15 if is_core else 0
    total += breakdown["核心来源"]

    # 3. 基金 (0-10)
    fund = paper.get("fund", "")
    if fund:
        if "国家" in fund or "自然科学" in fund or "社会科学" in fund:
            breakdown["基金"] = 10
        elif "省" in fund or "教育部" in fund:
            breakdown["基金"] = 7
        else:
            breakdown["基金"] = 4
    else:
        breakdown["基金"] = 0
    total += breakdown["基金"]

    # 4. 期刊等级 (0-15)
    journal_score = 0
    for name, tier in JOURNAL_TIERS.items():
        if name in journal:
            journal_score = tier
            break
    if journal_score == 0 and journal:
        journal_score = 5  # 有期刊名但不在列表中
    breakdown["期刊等级"] = min(15, journal_score)
    total += breakdown["期刊等级"]

    # 5. 时间新度 (0-10)
    date_str = paper.get("date", "") or paper.get("pubInfo", "")
    year = _extract_year(date_str)
    if year:
        from datetime import datetime
        age = datetime.now().year - year
        if age <= 1:
            breakdown["时效性"] = 10
        elif age <= 2:
            breakdown["时效性"] = 8
        elif age <= 3:
            breakdown["时效性"] = 6
        elif age <= 5:
            breakdown["时效性"] = 4
        else:
            breakdown["时效性"] = 2
    else:
        breakdown["时效性"] = 3
    total += breakdown["时效性"]

    # 6. 摘要质量 (0-10)
    abstract = paper.get("abstract", "")
    if len(abstract) >= 200:
        breakdown["摘要质量"] = 10
    elif len(abstract) >= 100:
        breakdown["摘要质量"] = 7
    elif len(abstract) >= 50:
        breakdown["摘要质量"] = 4
    else:
        breakdown["摘要质量"] = 0
    total += breakdown["摘要质量"]

    # 7. 关键词匹配 (0-15) - 如果有request.topics
    if request and hasattr(request, "topics") and request.topics:
        keywords = paper.get("keywords", [])
        title = paper.get("title", "")
        match_count = 0
        for topic in request.topics:
            if topic in title or any(topic in kw for kw in keywords):
                match_count += 1
        ratio = match_count / max(1, len(request.topics))
        breakdown["主题匹配"] = int(ratio * 15)
    else:
        breakdown["主题匹配"] = 8  # 无主题信息时给中间分
    total += breakdown["主题匹配"]

    return ScoredPaper(
        title=paper.get("title", ""),
        score=total,
        score_breakdown=breakdown,
        data=paper,
    )


def rank_papers(papers: list[dict], request=None, top_n: int = 20,
                min_score: float = 30) -> list[ScoredPaper]:
    """对所有论文评分并排序，返回Top-N"""
    scored = [score_paper(p, request) for p in papers]
    scored.sort(key=lambda x: -x.score)

    # 过滤低分
    filtered = [s for s in scored if s.score >= min_score]

    print(f"\n  [Agent4] 评分完成: {len(scored)} 篇, 及格(>={min_score}分): {len(filtered)} 篇")
    if filtered:
        print(f"  [Agent4] 最高分: {filtered[0].score:.0f} - {filtered[0].title[:40]}")
        print(f"  [Agent4] 最低入选: {filtered[min(top_n, len(filtered))-1].score:.0f} 分")

    return filtered[:top_n]


def format_scoring_results(scored: list[ScoredPaper]) -> str:
    """格式化评分结果"""
    lines = ["\n论文评分排名:", "-" * 60]
    for i, s in enumerate(scored[:20], 1):
        stars = "★" * min(5, int(s.score / 20)) + "☆" * (5 - min(5, int(s.score / 20)))
        lines.append(f"  {i:2d}. [{s.score:5.1f}分] {stars} {s.title[:45]}")
    return "\n".join(lines)


def _parse_int(s) -> int:
    if isinstance(s, int):
        return s
    s = str(s).replace(",", "").strip()
    m = re.search(r"\d+", s)
    return int(m.group()) if m else 0


def _extract_year(s: str) -> int:
    m = re.search(r"(20\d{2}|19\d{2})", str(s))
    return int(m.group()) if m else 0
