"""
CNKI 搜索与提取操作
复用 CNKI skill 的 search.py / paper.py 底层逻辑
"""
import asyncio
from typing import Any

from search import parse_results_from_page, _collect_result_items
from paper import ensure_detail_page, extract_detail_from_page
from cnki_selectors import ADVANCED_SEARCH_URL


async def advanced_search(browser_mgr, query: str, author: str = "",
                          source: str = "", start_year: str = "", end_year: str = "",
                          max_pages: int = 5, max_items: int = 50) -> list[dict]:
    """
    CNKI 高级搜索，返回结构化结果列表。
    source: SCI / EI / hx / CSSCI / CSCD
    """
    page = await browser_mgr.new_page()
    try:
        await browser_mgr.session.goto(page, ADVANCED_SEARCH_URL)
        await browser_mgr.session.ensure_selector(page, "#txt_1_value1")
        await browser_mgr.session.require_no_captcha(page)
        await asyncio.sleep(1)

        source_types = [source] if source else []
        payload = {
            "query": query,
            "fieldType": "SU",
            "author": author,
            "sourceTypes": source_types,
            "startYear": start_year,
            "endYear": end_year,
        }

        await page.evaluate(
            """(config) => {
              const selects = Array.from(document.querySelectorAll('select')).filter(s => s.offsetParent !== null);
              if (selects[0]) { selects[0].value = config.fieldType; selects[0].dispatchEvent(new Event('change', {bubbles:true})); }
              const input1 = document.querySelector('#txt_1_value1');
              if (input1) { input1.value = config.query; input1.dispatchEvent(new Event('input', {bubbles:true})); }
              const author = document.querySelector('#au_1_value1');
              if (author && config.author) { author.value = config.author; author.dispatchEvent(new Event('input', {bubbles:true})); }
              if (config.startYear) { const sy = document.querySelector('#startYear'); if(sy){sy.value=config.startYear; sy.dispatchEvent(new Event('change',{bubbles:true}));} }
              if (config.endYear) { const ey = document.querySelector('#endYear'); if(ey){ey.value=config.endYear; ey.dispatchEvent(new Event('change',{bubbles:true}));} }
              if (config.sourceTypes.length > 0) {
                const all = document.querySelector('#gjAll');
                if (all && all.checked) all.click();
                for (const key of config.sourceTypes) {
                  const box = document.querySelector('#' + key);
                  if (box && !box.checked) box.click();
                }
              }
              document.querySelector('div.search')?.click();
            }""",
            payload,
        )

        await asyncio.sleep(5)
        body = await page.text_content("body")
        if "条结果" not in body:
            return []

        parsed = await parse_results_from_page(page)
        total = parsed.get("total", "0")
        print(f"    [搜索] 共 {total} 条结果")

        seen = set()
        collected = []
        _collect_result_items(parsed, seen, collected)

        current_page = 1
        while len(collected) < max_items and current_page < max_pages:
            try:
                next_btn = page.get_by_text("下一页")
                if await next_btn.count() == 0:
                    break
                cls = await next_btn.first.get_attribute("class") or ""
                if "disabled" in cls or "noMore" in cls:
                    break
                await next_btn.first.click()
                await asyncio.sleep(3)
                await browser_mgr.session.require_no_captcha(page)
                parsed = await parse_results_from_page(page)
                _collect_result_items(parsed, seen, collected)
                current_page += 1
            except Exception:
                break

        return collected[:max_items]
    finally:
        await page.close()


async def extract_detail(browser_mgr, url: str) -> dict[str, Any]:
    """提取单篇论文详情"""
    detail_page = await browser_mgr.new_page()
    try:
        await ensure_detail_page(browser_mgr.session, detail_page, url)
        await browser_mgr.session.dismiss_known_overlays(detail_page)
        return await extract_detail_from_page(detail_page)
    finally:
        await detail_page.close()


async def batch_extract_details(browser_mgr, items: list[dict],
                                 delay: float = 1.5,
                                 on_progress=None) -> list[dict]:
    """批量提取论文详情，返回enriched列表"""
    enriched = []
    for i, item in enumerate(items):
        url = item.get("url", "")
        title = item.get("title", "")
        if not url:
            enriched.append({**item, "detailError": "no_url"})
            continue

        if on_progress:
            on_progress(i, len(items), title)

        try:
            await asyncio.sleep(delay)
            detail = await extract_detail(browser_mgr, url)
            merged = {**item, **detail, "detail": detail}
            enriched.append(merged)
        except Exception as e:
            enriched.append({**item, "detailError": str(e)[:100]})

    return enriched
