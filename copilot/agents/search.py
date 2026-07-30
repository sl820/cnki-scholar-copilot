"""
Agent 3: 知网搜索
执行浏览器自动化检索，收集论文元数据
"""
import asyncio
from ..core.cnki_ops import advanced_search, batch_extract_details


async def execute_search(browser_mgr, strategy, request, on_progress=None) -> list[dict]:
    """
    执行CNKI搜索流程：
    1. 用主查询搜索
    2. 结果不足时用降级查询
    3. 批量提取详情
    """
    query = strategy.cnki_query
    if not query:
        query = " OR ".join(request.topics)

    print(f"\n  [Agent3] 开始搜索: {query[:80]}")
    print(f"  [Agent3] 来源={request.source or '不限'}, 年份={request.start_year or '不限'}-{request.end_year or '不限'}")

    # 主搜索
    items = await advanced_search(
        browser_mgr,
        query=query,
        source=request.source,
        start_year=request.start_year,
        end_year=request.end_year,
        max_pages=max(3, request.max_count // 10 + 1),
        max_items=request.max_count * 3,  # 多取一些用于后续筛选
    )

    # 结果不足时尝试降级查询
    if len(items) < request.max_count and strategy.fallback_queries:
        for fb_query in strategy.fallback_queries:
            if len(items) >= request.max_count:
                break
            print(f"  [Agent3] 结果不足，尝试降级查询: {fb_query[:60]}")
            await asyncio.sleep(2)
            more = await advanced_search(
                browser_mgr,
                query=fb_query,
                source=request.source,
                start_year=request.start_year,
                end_year=request.end_year,
                max_pages=2,
                max_items=request.max_count,
            )
            # 去重合并
            existing_urls = {it.get("url") for it in items}
            for m in more:
                if m.get("url") not in existing_urls:
                    items.append(m)
                    existing_urls.add(m.get("url"))

    print(f"  [Agent3] 搜索完成，共 {len(items)} 条元数据")

    # 批量提取详情（摘要、关键词、基金、单位等）
    print(f"  [Agent3] 开始提取论文详情...")

    def progress_cb(i, total, title):
        if on_progress:
            on_progress(i, total, title)
        else:
            print(f"    [{i+1}/{total}] {title[:50]}")

    enriched = await batch_extract_details(
        browser_mgr, items,
        delay=1.5,
        on_progress=progress_cb,
    )

    success = sum(1 for e in enriched if not e.get("detailError"))
    print(f"  [Agent3] 详情提取完成: {success}/{len(enriched)} 成功")

    return enriched
