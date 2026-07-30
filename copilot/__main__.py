#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CNKI Scholar Copilot - 知网文献研究助手
主入口：将6个Agent串成流水线

用法:
  python -m copilot "数字人文在高校图书馆中的应用，近五年，CSSCI，20篇"
  python -m copilot --query "AI图书馆" --count 15 --source CSSCI --no-pdf
"""
import sys
import os
import asyncio
import argparse
from datetime import datetime

# 确保 CNKI shared modules 可用
CNKI_SKILL_DIR = os.environ.get("CNKI_SKILL_DIR", "")
if not CNKI_SKILL_DIR:
    candidates = [
        os.path.join(os.path.expanduser("~"), ".codex", "skills", "_shared", "cnki"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_shared", "cnki"),
    ]
    for c in candidates:
        if os.path.exists(os.path.join(c, "browser.py")):
            CNKI_SKILL_DIR = c
            break
if CNKI_SKILL_DIR and CNKI_SKILL_DIR not in sys.path:
    sys.path.insert(0, CNKI_SKILL_DIR)

from copilot.agents.nlu import parse_request, format_request
from copilot.agents.strategy import build_strategy, format_strategy
from copilot.agents.search import execute_search
from copilot.agents.scoring import rank_papers, format_scoring_results
from copilot.agents.author_analysis import analyze_authors, format_author_analysis
from copilot.agents.pdf_report import download_pdfs, generate_research_package
from copilot.core.browser_manager import BrowserManager


async def run_pipeline(args):
    """执行完整的6-Agent流水线"""
    print("=" * 60)
    print("  CNKI Scholar Copilot - 知网文献研究助手")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # ===== Agent 1: 需求理解 =====
    print("\n[Agent 1/6] 需求理解...")
    request = parse_request(args.query)
    if args.count:
        request.max_count = args.count
    if args.source:
        request.source = args.source
    if args.no_pdf:
        request.need_pdf = False
    print(format_request(request))

    # ===== Agent 2: 检索策略 =====
    print("\n[Agent 2/6] 生成检索策略...")
    strategy = build_strategy(request.topics)
    print(format_strategy(strategy))

    # ===== Agent 3: 知网搜索 =====
    print("\n[Agent 3/6] 知网检索...")
    async with BrowserManager(args.cdp_url) as browser:
        all_papers = await execute_search(browser, strategy, request)

        if not all_papers:
            print("\n[!] 未检索到任何论文，请调整检索策略后重试。")
            return

        # ===== Agent 4: 论文评分 =====
        print("\n[Agent 4/6] 论文评分与筛选...")
        scored = rank_papers(all_papers, request, top_n=request.max_count, min_score=25)
        print(format_scoring_results(scored))

        if not scored:
            print("\n[!] 无论文达到评分阈值，降低阈值重试...")
            scored = rank_papers(all_papers, request, top_n=request.max_count, min_score=10)

        # ===== Agent 5: 作者分析 =====
        print("\n[Agent 5/6] 作者与机构分析...")
        author_data = [sp.data for sp in scored]
        analysis = analyze_authors(author_data)
        print(format_author_analysis(analysis))

        # ===== Agent 6: PDF下载 + 研究包 =====
        print("\n[Agent 6/6] 生成研究包...")
        topic = " + ".join(request.topics)
        safe_topic = topic.replace(" ", "_").replace("/", "_")[:30]
        output_dir = os.path.join(os.path.abspath(args.output), safe_topic)

        downloads = []
        if request.need_pdf:
            top_data = [sp.data for sp in scored]
            downloads = await download_pdfs(browser, top_data, output_dir, max_count=request.max_count)
        else:
            print("  [跳过] 不需要PDF下载")

    # 生成研究包（Excel + 报告）
    generate_research_package(
        output_dir, topic, request, strategy,
        all_papers, scored, analysis, downloads
    )

    # 最终汇总
    print("\n" + "=" * 60)
    print("  完成！研究包已生成")
    print(f"  主题: {topic}")
    print(f"  检索: {len(all_papers)} 篇 -> 筛选: {len(scored)} 篇 -> 下载: {sum(1 for d in downloads if d['status'] in ('ok','exists'))} 篇")
    print(f"  核心作者: {len([a for a in analysis.authors if a.recommendation >= 4])} 位")
    if analysis.institutions:
        print(f"  主要机构: {', '.join(inst for inst, _ in analysis.institutions[:3])}")
    if analysis.top_keywords:
        print(f"  高频关键词: {', '.join(kw for kw, _ in analysis.top_keywords[:5])}")
    print(f"  输出目录: {output_dir}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="CNKI Scholar Copilot - 知网文献研究助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python -m copilot "数字人文在高校图书馆中的应用，近五年，CSSCI，20篇"
  python -m copilot --query "AI图书馆" --count 15 --source CSSCI
  python -m copilot "区块链+供应链金融" --no-pdf --output ./research/
        """
    )
    parser.add_argument("query_positional", nargs="?", help="研究主题（自然语言）")
    parser.add_argument("--query", "-q", help="研究主题（与位置参数二选一）")
    parser.add_argument("--output", "-o", default="./output", help="输出目录")
    parser.add_argument("--cdp-url", default="http://127.0.0.1:9222", help="Chrome CDP地址")
    parser.add_argument("--count", "-n", type=int, help="目标论文数量")
    parser.add_argument("--source", "-s", choices=["CSSCI", "CSCD", "SCI", "EI", "hx"], help="来源限定")
    parser.add_argument("--no-pdf", action="store_true", help="不下载PDF")
    args = parser.parse_args()

    # 合并位置参数和--query
    if not args.query and args.query_positional:
        args.query = args.query_positional
    if not args.query:
        parser.error("请提供研究主题，例如: python -m copilot \"数字人文在高校图书馆中的应用\"")

    asyncio.run(run_pipeline(args))


if __name__ == "__main__":
    main()
