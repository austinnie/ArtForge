#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ArtForge 智能日更调度脚本
功能：
  1. 自动选择今日主题（按周计划 + 防重复 + 权重）
  2. 调用 artforge_daily 完成完整流水线
  3. 可选：追加 GitHub 日报 / 新闻聚合
  4. 记录执行日志

用法：
  python scripts/smart_daily.py                    # 默认：只跑艺术日更
  python scripts/smart_daily.py --all              # 全部任务
  python scripts/smart_daily.py --skip-video       # 跳过视频推送
  python scripts/smart_daily.py --dry-run          # 只打印计划，不执行
"""
import argparse
import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / "output" / "daily" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 日志配置
# ============================================================
def setup_logger():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"smart_daily_{ts}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return logging.getLogger("smart_daily"), log_file

# ============================================================
# 任务执行器
# ============================================================
def run_command(cmd: list, description: str, logger) -> bool:
    """执行命令并返回是否成功"""
    logger.info(f"▶ 开始: {description}")
    logger.info(f"  命令: {' '.join(cmd)}")
    
    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=3600,  # 1 小时超时
        )
        elapsed = time.time() - start
        
        # 打印输出
        if result.stdout:
            for line in result.stdout.splitlines()[-20:]:  # 只打最后 20 行
                logger.info(f"  [stdout] {line}")
        if result.stderr:
            for line in result.stderr.splitlines()[-10:]:
                logger.warning(f"  [stderr] {line}")
        
        if result.returncode == 0:
            logger.info(f"✅ 完成: {description} ({elapsed:.1f}s)")
            return True
        else:
            logger.error(f"❌ 失败: {description} (exit={result.returncode}, {elapsed:.1f}s)")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"⏰ 超时: {description} (>3600s)")
        return False
    except Exception as e:
        logger.error(f"💥 异常: {description} - {e}")
        return False

# ============================================================
# 任务定义
# ============================================================
def task_artforge_daily(args, logger) -> bool:
    """艺术日更（核心任务）"""
    cmd = [
        sys.executable, "-m", "skills.artforge_daily.skill",
        "--smart",
        "--week-plan",
        "--avoid-days", "7",
        "--count", "6",
        "--engine", "agnes",
        "--theme", "terracotta",
        "--footer-image", "assets/qr/公众号结束处.png",
    ]
    
    if args.skip_video:
        cmd.append("--no-video")
    if args.skip_newspic:
        cmd.append("--no-newspic")
    
    return run_command(cmd, "🎨 ArtForge 艺术日更", logger)


def task_github_daily(args, logger) -> bool:
    """GitHub 仓库日报（可选）"""
    cmd = [
        sys.executable, "skills/github_repo_daily/github_repo_daily_cli.py",
        "--theme", "newspaper",
    ]
    if args.no_publish:
        cmd.append("--no-publish")
    return run_command(cmd, "📦 GitHub 仓库日报", logger)


def task_news_daily(args, logger) -> bool:
    """新闻聚合（可选）"""
    cmd = [
        sys.executable, "-m", "skills.news_aggregator.skill",
        "--category", "tech",
        "--top-n", "15",
    ]
    return run_command(cmd, "📰 科技新闻聚合", logger)

# ============================================================
# 执行报告
# ============================================================
def save_report(log_file: Path, results: dict, logger):
    """保存执行报告"""
    report = {
        "executed_at": datetime.now().isoformat(),
        "log_file": str(log_file),
        "results": results,
        "summary": {
            "total": len(results),
            "success": sum(1 for v in results.values() if v),
            "failed": sum(1 for v in results.values() if not v),
        },
    }
    
    report_file = LOG_DIR / f"report_{datetime.now().strftime('%Y%m%d')}.json"
    
    # 追加到当日报告（同一天多次执行会覆盖）
    report_file.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info(f"📋 报告已保存: {report_file}")
    
    # 打印摘要
    logger.info("")
    logger.info("=" * 60)
    logger.info("  📊 执行摘要")
    logger.info("=" * 60)
    for task_name, ok in results.items():
        status = "✅ 成功" if ok else "❌ 失败"
        logger.info(f"  {task_name}: {status}")
    logger.info(f"  总计: {report['summary']['success']}/{report['summary']['total']} 成功")
    logger.info("=" * 60)

# ============================================================
# 主入口
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="ArtForge 智能日更调度")
    parser.add_argument("--all", action="store_true", help="执行全部任务")
    parser.add_argument("--skip-video", action="store_true", help="跳过视频推送")
    parser.add_argument("--skip-newspic", action="store_true", help="跳过贴图推送")
    parser.add_argument("--no-publish", action="store_true", help="不推送到公众号")
    parser.add_argument("--dry-run", action="store_true", help="只打印计划，不执行")
    args = parser.parse_args()
    
    logger, log_file = setup_logger()
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("  🎎 ArtForge 智能日更调度")
    logger.info(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    logger.info(f"📁 项目根: {PROJECT_ROOT}")
    logger.info(f"📝 日志  : {log_file}")
    
    # 构建任务列表
    tasks = []
    
    # 核心任务：艺术日更（总是执行）
    tasks.append(("🎨 艺术日更", lambda: task_artforge_daily(args, logger)))
    
    # 可选任务
    if args.all:
        tasks.append(("📦 GitHub 日报", lambda: task_github_daily(args, logger)))
        tasks.append(("📰 新闻聚合", lambda: task_news_daily(args, logger)))
    
    # Dry run 模式
    if args.dry_run:
        logger.info("")
        logger.info("🔍 Dry-run 模式，计划执行的任务：")
        for name, _ in tasks:
            logger.info(f"  - {name}")
        return 0
    
    # 执行任务
    results = {}
    for name, task_fn in tasks:
        try:
            results[name] = task_fn()
        except Exception as e:
            logger.error(f"💥 {name} 执行异常: {e}")
            results[name] = False
    
    # 保存报告
    save_report(log_file, results, logger)
    
    # 返回码：全部成功返回 0，否则返回 1
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())