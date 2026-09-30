# skills/github_followme/cli.py
import argparse
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from skills.github_followme.skill import GithubFollowMe

def main():
    parser = argparse.ArgumentParser(description="GitHub FollowMe 自动发现与互动工具")
    parser.add_argument("-n", "--count", type=int, default=2, help="Fetch 仓库数量 (默认 2)")
    parser.add_argument("--sub-thresh", type=float, default=14.0, help="关注作者阈值")
    parser.add_argument("--star-thresh", type=float, default=16.0, help="Star 仓库阈值")
    parser.add_argument("-w", "--window", type=int, default=24, help="时间窗口小时数")
    parser.add_argument("--dry-run", action="store_true", help="模拟运行")
    # ✅ 新增：限制每次评估的仓库数量，防止 Ollama 崩溃
    parser.add_argument("--eval-limit", type=int, default=2, help="限制本次只评估几个仓库 (默认 2)")
    
    args = parser.parse_args()

    print("=" * 60)
    print("   GitHub FollowMe 技能测试")
    print("=" * 60)

    follower = GithubFollowMe(
        project_root=PROJECT_ROOT,
        count=args.count,
        sub_thresh=args.sub_thresh,
        star_thresh=args.star_thresh,
        window=args.window,
        eval_limit=args.eval_limit # ✅ 传入限制
    )

    success = follower.run(dry_run=args.dry_run)
    
    if success:
        print("\n✅ 测试完成")
    else:
        print("\n❌ 测试失败")
        sys.exit(1)

if __name__ == "__main__":
    main()