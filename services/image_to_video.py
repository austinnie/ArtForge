# services/image_to_video.py
"""
图片 → 视频 合成器（供 AI MV 脚本调用）
用 ffmpeg 把多张图合成带淡入淡出转场的视频
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional


class ImageToVideo:
    def __init__(self, ffmpeg: Optional[str] = None):
        self.ffmpeg = ffmpeg or shutil.which("ffmpeg")
        if not self.ffmpeg:
            raise RuntimeError("未找到 ffmpeg，请先安装")

    def build(
        self,
        images: List[Path],
        output: Path,
        per_image: float = 4.0,
        size: str = "1920x1080",
        bgm: Optional[Path] = None,
        fade: float = 0.5,
    ) -> Path:
        """
        合成视频。
        - per_image: 每张停留秒数
        - fade: 每张的淡入淡出（不跨图，只做单张淡入淡出）
        """
        if not images:
            raise ValueError("images 为空")

        W, H = map(int, size.split("x"))
        output.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(prefix="af_i2v_") as tmp:
            tmp_dir = Path(tmp)
            segs = []

            for i, img in enumerate(images):
                seg = tmp_dir / f"seg_{i:03d}.mp4"
                vf = (
                    f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
                    f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,"
                    f"setsar=1,"
                    f"fade=t=in:st=0:d={fade},"
                    f"fade=t=out:st={per_image-fade}:d={fade},"
                    f"format=yuv420p"
                )
                subprocess.run([
                    self.ffmpeg, "-y",
                    "-loop", "1", "-t", str(per_image),
                    "-i", str(img),
                    "-vf", vf,
                    "-r", "30",
                    "-c:v", "libx264", "-preset", "medium",
                    "-crf", "20", "-pix_fmt", "yuv420p",
                    str(seg),
                ], capture_output=True, check=True)
                segs.append(seg)

            # 合并
            concat = tmp_dir / "concat.txt"
            concat.write_text(
                "\n".join(f"file '{s.as_posix()}'" for s in segs),
                encoding="utf-8")
            merged = tmp_dir / "merged.mp4"
            subprocess.run([
                self.ffmpeg, "-y",
                "-f", "concat", "-safe", "0",
                "-i", str(concat),
                "-c", "copy", str(merged),
            ], capture_output=True, check=True)

            # 加 BGM
            if bgm and Path(bgm).exists():
                subprocess.run([
                    self.ffmpeg, "-y",
                    "-i", str(merged),
                    "-stream_loop", "-1", "-i", str(bgm),
                    "-shortest",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    str(output),
                ], capture_output=True, check=True)
            else:
                shutil.copy2(merged, output)

        return output