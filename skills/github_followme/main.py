#!/usr/bin/env python3
"""Run the full pipeline sequentially: fetch, evaluate, subscribe, star.

Default cycle:
  1. fetch 5 new repos
  2. evaluate everything not yet scored
  3. follow profiles updated in last 24h with idea+skill > SUBSCRIBE_THRESHOLD
  4. star repos    updated in last 24h with idea+skill > STAR_THRESHOLD
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

from libs import db
from libs.settings import load_settings


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the full followme pipeline.")
    parser.add_argument("-n", "--count", type=int, default=None,
                        help="Repos to fetch this cycle (default: FETCH_COUNT, normally 5)")
    parser.add_argument("--subscribe-threshold", type=float, default=None,
                        help="idea+skill > X to follow (default: SUBSCRIBE_THRESHOLD)")
    parser.add_argument("--star-threshold", type=float, default=None,
                        help="idea+skill > Y to star (default: STAR_THRESHOLD)")
    parser.add_argument("-w", "--window-hours", type=int, default=None,
                        help="Recency window in hours (default: WINDOW_HOURS)")
    parser.add_argument("--evaluate-limit", type=int, default=None,
                        help="Cap repos evaluated this cycle (default: no cap)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Skip follow/star side effects; still fetches and evaluates")
    parser.add_argument("-i", "--infinite", action="store_true",
                        help="Loop forever; sleep --sleep seconds between cycles")
    parser.add_argument("--sleep", type=float, default=600.0,
                        help="Seconds to sleep between cycles in --infinite mode (default 600)")
    return parser.parse_args()


def step(label: str) -> None:
    logger.info(f"=== {label} ===")


def run_cycle(args: argparse.Namespace, settings: dict) -> None:
    from scripts.fetch import main as fetch_main
    from scripts.evaluate import main as evaluate_main
    from scripts.subscribe import main as subscribe_main
    from scripts.star import main as star_main

    count = args.count if args.count is not None else settings["fetch_count"]
    subscribe_threshold = args.subscribe_threshold if args.subscribe_threshold is not None else settings["subscribe_threshold"]
    star_threshold = args.star_threshold if args.star_threshold is not None else settings["star_threshold"]
    window = args.window_hours if args.window_hours is not None else settings["window_hours"]

    step(f"fetch -n {count}")
    sys.argv = ["scripts/fetch.py", "-n", str(count)]
    fetch_main()

    step(f"evaluate{'' if args.evaluate_limit is None else f' -l {args.evaluate_limit}'}")
    sys.argv = ["scripts/evaluate.py"] + (["-l", str(args.evaluate_limit)] if args.evaluate_limit is not None else [])
    evaluate_main()

    step(f"subscribe -s {subscribe_threshold} -w {window}")
    sub_argv = ["scripts/subscribe.py", "-s", str(subscribe_threshold), "-w", str(window)]
    if args.dry_run:
        sub_argv.append("--dry-run")
    sys.argv = sub_argv
    subscribe_main()

    step(f"star -s {star_threshold} -w {window}")
    star_argv = ["scripts/star.py", "-s", str(star_threshold), "-w", str(window)]
    if args.dry_run:
        star_argv.append("--dry-run")
    sys.argv = star_argv
    star_main()

    conn = db.connect(settings["db_path"])
    s = db.stats(conn)
    logger.info(
        f"DB stats: total={s['total']} evaluated={s['evaluated']} "
        f"followed_profiles={s['followed']} starred={s['starred']} flagged={s['flagged']}"
    )


def main() -> int:
    args = parse_args()
    settings = load_settings(Path(__file__).resolve().parent)

    if not args.infinite:
        run_cycle(args, settings)
        return 0

    cycle = 0
    while True:
        cycle += 1
        logger.info(f"# cycle {cycle}")
        try:
            run_cycle(args, settings)
        except KeyboardInterrupt:
            logger.info("Interrupted")
            return 130
        except Exception as exc:
            logger.warning(f"Cycle {cycle} failed: {exc}")
        logger.info(f"sleeping {args.sleep}s before next cycle")
        time.sleep(max(0.0, args.sleep))


if __name__ == "__main__":
    sys.exit(main())
