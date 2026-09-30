# skills/github_followme/skill.py
import sys
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

class GithubFollowMe:
    # ✅ 增加 eval_limit 参数
    def __init__(self, project_root: Path, count=2, sub_thresh=14.0, star_thresh=16.0, window=24, eval_limit=2):
        self.project_root = project_root
        self.main_script = project_root / "skills" / "github_followme" / "main.py"
        
        self.count = count
        self.sub_thresh = sub_thresh
        self.star_thresh = star_thresh
        self.window = window
        self.eval_limit = eval_limit

    def run(self, dry_run: bool = False) -> bool:
        if not self.main_script.exists():
            logger.error(f" 找不到主脚本: {self.main_script}")
            return False

        cmd = [
            sys.executable, str(self.main_script),
            "-n", str(self.count),
            "--subscribe-threshold", str(self.sub_thresh),
            "--star-threshold", str(self.star_thresh),
            "-w", str(self.window),
            "--evaluate-limit", str(self.eval_limit) # ✅ 传递给 main.py
        ]
        
        if dry_run:
            cmd.append("--dry-run")
            logger.info("🔍 [Dry Run] 模式：仅评估，不执行关注/Star")

        logger.info(f"🚀 启动流程 (Fetch {self.count}, Eval Limit {self.eval_limit})...")
        logger.info(" 提示：Ollama 评分可能需要 1~2 分钟/个，请耐心等待...")
        
        skill_dir = self.main_script.parent
        
        try:
            process = subprocess.Popen(
                cmd, cwd=str(skill_dir), stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, text=True, encoding="utf-8", bufsize=1
            )
            
            for line in process.stdout:
                print(f"  [FollowMe] {line.strip()}")
            
            process.wait(timeout=600) # 10分钟超时
            
            if process.returncode == 0:
                logger.info("✅ 流程执行成功")
                return True
            else:
                logger.error(f"❌ 流程失败 (exit code {process.returncode})")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("⏱️ 评估超时！Ollama 响应过慢。")
            process.kill()
            return False
        except Exception as e:
            logger.error(f"💥 执行异常: {e}")
            return False