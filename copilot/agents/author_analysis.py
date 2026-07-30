"""
Agent 5: 作者分析
分析核心作者、机构分布、合作关系
"""
from collections import Counter, defaultdict
from dataclasses import dataclass, field


@dataclass
class AuthorProfile:
    """作者画像"""
    name: str
    affiliations: list[str] = field(default_factory=list)
    paper_count: int = 0
    total_citations: int = 0
    journals: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    papers: list[str] = field(default_factory=list)
    recommendation: int = 0  # 1-5星


@dataclass
class AuthorAnalysis:
    """作者分析结果"""
    authors: list[AuthorProfile] = field(default_factory=list)
    institutions: list[tuple[str, int]] = field(default_factory=list)
    collaborations: list[tuple[str, str, int]] = field(default_factory=list)
    top_keywords: list[tuple[str, int]] = field(default_factory=list)
    journal_distribution: list[tuple[str, int]] = field(default_factory=list)
    year_distribution: list[tuple[str, int]] = field(default_factory=list)


def analyze_authors(papers: list[dict]) -> AuthorAnalysis:
    """从论文列表中提取作者分析"""
    analysis = AuthorAnalysis()

    author_map = defaultdict(lambda: {
        "affiliations": set(), "count": 0, "citations": 0,
        "journals": set(), "keywords": set(), "papers": [], "coauthors": set()
    })
    institution_counter = Counter()
    keyword_counter = Counter()
    journal_counter = Counter()
    year_counter = Counter()
    collab_counter = Counter()

    for paper in papers:
        title = paper.get("title", "")
        citations = _safe_int(paper.get("citations", 0))
        journal = paper.get("journal", "") or paper.get("journalDetail", "")
        date = paper.get("date", "") or paper.get("pubInfo", "")
        keywords = paper.get("keywords", [])
        affiliations = paper.get("affiliations", [])
        authors = paper.get("authors", []) or paper.get("detailAuthors", [])

        # 作者列表
        author_names = []
        if isinstance(authors, list):
            for a in authors:
                if isinstance(a, dict):
                    author_names.append(a.get("name", ""))
                elif isinstance(a, str):
                    author_names.append(a)

        # 统计每个作者
        for name in author_names:
            if not name or len(name) < 2:
                continue
            info = author_map[name]
            info["count"] += 1
            info["citations"] += citations
            info["papers"].append(title)
            if journal:
                info["journals"].add(journal)
            for kw in keywords:
                info["keywords"].add(kw)
            for aff in affiliations:
                info["affiliations"].add(aff)
            # 合作关系
            for other in author_names:
                if other != name and other:
                    info["coauthors"].add(other)
                    pair = tuple(sorted([name, other]))
                    collab_counter[pair] += 1

        # 机构统计
        for aff in affiliations:
            institution_counter[aff] += 1

        # 关键词统计
        for kw in keywords:
            keyword_counter[kw] += 1

        # 期刊统计
        if journal:
            journal_counter[journal] += 1

        # 年份统计
        import re
        year_match = re.search(r"(20\d{2}|19\d{2})", str(date))
        if year_match:
            year_counter[year_match.group()] += 1

    # 构建作者画像并排序
    for name, info in author_map.items():
        if info["count"] < 1:
            continue
        profile = AuthorProfile(
            name=name,
            affiliations=list(info["affiliations"])[:3],
            paper_count=info["count"],
            total_citations=info["citations"],
            journals=list(info["journals"])[:5],
            keywords=list(info["keywords"])[:8],
            papers=info["papers"][:10],
        )
        # 推荐度：基于论文数和引用量
        score = info["count"] * 2 + min(info["citations"] / 10, 20)
        if score >= 20:
            profile.recommendation = 5
        elif score >= 12:
            profile.recommendation = 4
        elif score >= 6:
            profile.recommendation = 3
        elif score >= 3:
            profile.recommendation = 2
        else:
            profile.recommendation = 1
        analysis.authors.append(profile)

    # 按论文数排序
    analysis.authors.sort(key=lambda x: (-x.paper_count, -x.total_citations))
    analysis.authors = analysis.authors[:20]

    # 其他统计
    analysis.institutions = institution_counter.most_common(15)
    analysis.collaborations = [(a, b, c) for (a, b), c in collab_counter.most_common(10)]
    analysis.top_keywords = keyword_counter.most_common(20)
    analysis.journal_distribution = journal_counter.most_common(10)
    analysis.year_distribution = sorted(year_counter.items())

    return analysis


def format_author_analysis(analysis: AuthorAnalysis) -> str:
    """格式化作者分析结果"""
    lines = [
        "\n" + "=" * 60,
        "作者与机构分析",
        "=" * 60,
    ]

    # 核心作者
    lines.append("\n核心作者:")
    for a in analysis.authors[:10]:
        stars = "★" * a.recommendation + "☆" * (5 - a.recommendation)
        aff = a.affiliations[0] if a.affiliations else "未知"
        lines.append(f"  {a.name} | {aff} | {a.paper_count}篇 | 引用{a.total_citations} | {stars}")

    # 机构分布
    lines.append("\n主要机构:")
    for inst, count in analysis.institutions[:8]:
        lines.append(f"  {inst}: {count}篇")

    # 高频关键词
    lines.append("\n高频关键词:")
    kw_str = ", ".join(f"{kw}({c})" for kw, c in analysis.top_keywords[:12])
    lines.append(f"  {kw_str}")

    # 期刊分布
    lines.append("\n期刊分布:")
    for j, c in analysis.journal_distribution[:6]:
        lines.append(f"  {j}: {c}篇")

    # 合作关系
    if analysis.collaborations:
        lines.append("\n合作关系:")
        for a, b, c in analysis.collaborations[:5]:
            lines.append(f"  {a} <-> {b}: {c}次合作")

    # 年份分布
    if analysis.year_distribution:
        lines.append("\n年份分布:")
        for year, count in analysis.year_distribution:
            bar = "█" * count
            lines.append(f"  {year}: {bar} ({count})")

    lines.append("=" * 60)
    return "\n".join(lines)


def _safe_int(v) -> int:
    import re
    if isinstance(v, int):
        return v
    m = re.search(r"\d+", str(v).replace(",", ""))
    return int(m.group()) if m else 0
