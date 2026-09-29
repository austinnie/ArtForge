# skills/amway_daily/skill.py
"""
安利产品每日自动推送技能
逻辑：扫描目录 -> 查找未发送的 docx -> pandoc 转 md -> wechat_formatter 推送
"""
import json
import subprocess
import logging
import re
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class AmwayDaily:
    # ✅ 接收 work_dir 参数
    def __init__(self, docx_dir: str, work_dir: str, queue_file: str = "data/amway_queue.json", theme: str = "newspaper"):
        self.docx_dir = Path(docx_dir)
        self.work_dir = Path(work_dir)  # 用于存放生成的 md 和图片
        self.queue_file = Path(queue_file)
        self.theme = theme
        
        # 确保工作目录存在
        self.work_dir.mkdir(parents=True, exist_ok=True)


    def _load_queue(self) -> dict:
        if self.queue_file.exists():
            return json.loads(self.queue_file.read_text(encoding="utf-8"))
        return {"sent_files": [], "last_run": None}

    def _save_queue(self, data: dict):
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)
        self.queue_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _get_title_from_filename(self, filename: str) -> str:
        """从文件名提取标题，去掉前面的编号 (如 0065_)"""
        name = Path(filename).stem
        # 去掉开头的数字和下划线
        clean_name = re.sub(r'^\d+_', '', name)
        return clean_name

    def run(self) -> bool:
        if not self.docx_dir.exists():
            logger.error(f"❌ 源目录不存在: {self.docx_dir}")
            return False

        # 只抓取 docx 文件
        all_docs = sorted(self.docx_dir.glob("*.docx"))
        if not all_docs:
            logger.warning("⚠️ 目录下没有 docx 文件")
            return False

        queue = self._load_queue()
        sent_files = set(queue.get("sent_files", []))
        
        # 找到下一个没发过的文件
        next_doc = None
        for doc in all_docs:
            if doc.name not in sent_files:
                next_doc = doc
                break

        if not next_doc:
            logger.info("🎉 所有产品文档已发送完毕！")
            return True

        logger.info(f"🎯 今日推送目标: {next_doc.name}")
        title = self._get_title_from_filename(next_doc.name)

        try:
            # 3. 使用 Pandoc 转换为 Markdown (必须提取图片)
            md_path = self.work_dir / f"{next_doc.stem}.md"
            
            # ✅ 关键：指定图片提取目录为 images
            # 这样 wechat_formatter 能自动识别这里的图片作为正文和封面
            images_dir = self.work_dir / "images"
            images_dir.mkdir(exist_ok=True)

            logger.info("🔄 正在转换文档 (Pandoc)...")
            cmd = [
                "pandoc", str(next_doc), 
                "-t", "markdown", 
                "-o", str(md_path),
                f"--extract-media={str(images_dir)}"  # ← 必须加这个，把 Word 里的图提出来
            ]
            subprocess.run(cmd, check=True, capture_output=True)

            # 检查是否提取到了图片
            extracted_imgs = list(images_dir.glob("*"))
            if extracted_imgs:
                logger.info(f"🖼️ 成功从 Word 提取 {len(extracted_imgs)} 张图片 (将用作正文和封面)")
            else:
                logger.warning("⚠️ 未提取到图片，请检查 Word 文档是否包含图片")

            # 4. 注入标题 (防止 docx 里没有 H1 标题)
            content = md_path.read_text(encoding="utf-8")
            if not content.startswith("# "):
                content = f"# {title}\n\n{content}"
                md_path.write_text(content, encoding="utf-8")

            # 5. 调用 wechat_formatter 推送
            logger.info("🚀 正在排版并推送...")
            from skills.wechat_formatter import WechatFormatter
            fmt = WechatFormatter()

            # 排版
            r = fmt.format(str(md_path), theme=self.theme, open=False)
            
            if r.get("status") == "success":
                article_dir = r["result"]["article_dir"]
                
                # ✅ 推送 (此时 article_dir 里应该有 images 文件夹，或者 markdown 里引用了图片)
                # 如果 wechat_formatter 还是报没封面，我们可以强制把提取的图复制一份叫 cover.jpg
                # 但通常只要 markdown 里有图，它就能处理。
                
                pub_result = fmt.publish(str(article_dir), dry_run=False)
                
                if pub_result.get("status") == "success":
                    logger.info(f"✅ 推送成功: {title}")
                    queue["sent_files"].append(next_doc.name)
                    queue["last_run"] = datetime.now().isoformat()
                    self._save_queue(queue)
                    return True
                else:
                    logger.error(f"⚠️ 发布失败: {pub_result.get('error')}")
            else:
                logger.error(f"❌ 排版失败: {r.get('error')}")
                
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Pandoc 转换失败: {e.stderr.decode()}")
        except Exception as e:
            logger.error(f"❌ 发生异常: {e}")
            
        return False        