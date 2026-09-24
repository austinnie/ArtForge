# services/aging_processor.py
"""
做旧处理器 — 宣纸 / 绢本 / 老纸 / 褐纸 + 泛黄 / 霉斑 / 磨损 / 暗角 / 噪点

用法:
    from services.aging_processor import AgingProcessor

    ap = AgingProcessor()

    # 1. 一键做旧（默认宣纸 + 全套老化）
    aged = ap.apply(image, texture="xuan_paper", strength=0.6)

    # 2. 只用某几种效果
    aged = ap.apply(image, texture="silk",
                    effects=["yellowing", "vignette", "grain"])

    # 3. 只要纹理，不要老化
    aged = ap.apply(image, texture="aged", effects=[])

    # 4. 关掉纹理，只做泛黄+暗角
    aged = ap.apply(image, texture=None, effects=["yellowing", "vignette"])

可用的 texture:  None | "xuan_paper" | "silk" | "aged" | "brown"
可用的 effects:  ["yellowing", "foxing", "wear", "vignette", "grain"]
"""

from __future__ import annotations

import random
import os
import sys
from pathlib import Path
from typing import List, Optional, Sequence, Tuple, Union

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


# ============================================================
# 路径 & 常量
# ============================================================

# ============================================================
# 路径修正（让 services/ 下的脚本能 import 项目根模块）
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:      # ← 新增
    sys.path.insert(0, str(PROJECT_ROOT))  # ← 新增
    
TEXTURE_DIR = PROJECT_ROOT / "assets" / "textures"

# 素材目录映射（如果用户放了真实纹理图，优先用素材）
TEXTURE_DIRS = {
    "xuan_paper": TEXTURE_DIR / "xuan_paper",
    "silk":       TEXTURE_DIR / "silk",
    "aged":       TEXTURE_DIR / "aged",
    "brown":      TEXTURE_DIR / "brown",
}

ALL_EFFECTS = ["yellowing", "foxing", "wear", "vignette", "grain"]


# ============================================================
# AgingProcessor
# ============================================================

class AgingProcessor:
    """做旧处理器"""

    def __init__(self, seed: Optional[int] = None):
        """
        Args:
            seed: 随机种子。指定后同一 seed 的做旧结果可复现。
        """
        self.seed = seed
        self._rng = random.Random(seed)
        if seed is not None:
            np.random.seed(seed)

    # ------------------------------------------------------------
    # 对外主接口
    # ------------------------------------------------------------

    def apply(
        self,
        image: Image.Image,
        texture: Optional[str] = "xuan_paper",
        effects: Optional[Sequence[str]] = None,
        strength: float = 0.6,
    ) -> Image.Image:
        """
        做旧主流程。

        Args:
            image:    输入图像（PIL Image）
            texture:  纸张纹理名，None 表示不加纹理
            effects:  老化效果列表，None 表示全部
            strength: 整体强度 0.0-1.0（1.0 最旧）

        Returns:
            做旧后的 RGB 图像
        """
        if effects is None:
            effects = list(ALL_EFFECTS)

        # 校验
        bad = [e for e in effects if e not in ALL_EFFECTS]
        if bad:
            print(f"   ⚠️ 未知效果 {bad}，已忽略")
            effects = [e for e in effects if e in ALL_EFFECTS]

        strength = max(0.0, min(1.0, strength))

        # 统一为 RGB
        if image.mode != "RGB":
            image = image.convert("RGB")

        arr = np.asarray(image, dtype=np.float32)

        # 1. 纸张纹理（multiply 混合）
        if texture:
            arr = self._apply_texture(arr, texture, strength)

        # 2. 老化效果
        if "yellowing" in effects:
            arr = self._yellowing(arr, strength)
        if "foxing" in effects:
            arr = self._foxing(arr, strength)
        if "wear" in effects:
            arr = self._wear(arr, strength)
        if "vignette" in effects:
            arr = self._vignette(arr, strength)
        if "grain" in effects:
            arr = self._grain(arr, strength)

        arr = np.clip(arr, 0, 255).astype(np.uint8)
        return Image.fromarray(arr)

    # ------------------------------------------------------------
    # 纹理层
    # ------------------------------------------------------------

    def _apply_texture(
        self,
        arr: np.ndarray,
        texture: str,
        strength: float,
    ) -> np.ndarray:
        """叠加纸张纹理（multiply 混合）。"""
        h, w = arr.shape[:2]

        # 1) 优先用素材图
        tex = self._load_texture_file(texture, (w, h))

        # 2) 没有素材 → 程序生成
        if tex is None:
            tex = self._generate_texture(texture, (w, h))

        if tex is None:
            return arr

        # multiply 混合 + strength 控制浓度
        tex_arr = np.asarray(tex.convert("RGB"), dtype=np.float32) / 255.0
        alpha = 0.35 + 0.45 * strength        # 0.35~0.80
        blended = arr * (1.0 - alpha) + (arr * tex_arr) * alpha

        return blended

    def _load_texture_file(
        self,
        texture: str,
        size: Tuple[int, int],
    ) -> Optional[Image.Image]:
        """如果 assets/textures/<name>/ 下有图，随机取一张。"""
        d = TEXTURE_DIRS.get(texture)
        if not d or not d.exists():
            return None

        files = list(d.glob("*.jpg")) + list(d.glob("*.png")) + \
                list(d.glob("*.jpeg"))
        if not files:
            return None

        f = self._rng.choice(files)
        try:
            img = Image.open(f).convert("RGB").resize(size, Image.Resampling.LANCZOS)
            return img
        except Exception as e:
            print(f"   ⚠️ 读取纹理失败 {f.name}: {e}")
            return None

    def _generate_texture(
        self,
        texture: str,
        size: Tuple[int, int],
    ) -> Optional[Image.Image]:
        """程序生成纹理。"""
        w, h = size
        if texture == "xuan_paper":
            return self._tex_xuan_paper(w, h)
        if texture == "silk":
            return self._tex_silk(w, h)
        if texture == "aged":
            return self._tex_aged(w, h)
        if texture == "brown":
            return self._tex_brown(w, h)
        print(f"   ⚠️ 未知纹理 '{texture}'")
        return None

    # ---------- 四种程序纹理 ----------

    def _tex_xuan_paper(self, w: int, h: int) -> Image.Image:
        """
        宣纸：暖白底 + 细密纤维 + 淡云斑。
        """
        # 底：暖白
        base = np.full((h, w, 3), [248, 244, 232], dtype=np.float32)

        # 长纤维：细横纹
        rng = np.random.default_rng(self.seed)
        fiber = rng.normal(0, 1.0, (h, w))
        fiber = np.abs(fiber)
        # 横向拉伸纤维
        from PIL import ImageFilter
        fib_img = Image.fromarray(
            np.clip(fiber * 8, 0, 255).astype(np.uint8)
        ).filter(ImageFilter.GaussianBlur(0.6))
        fiber = np.asarray(fib_img, dtype=np.float32) / 255.0
        base -= fiber[..., None] * np.array([6, 8, 10], dtype=np.float32)

        # 云斑：低频噪声
        cloud = self._value_noise(w, h, cell=64)
        base -= cloud[..., None] * np.array([3, 4, 6], dtype=np.float32)

        return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))

    def _tex_silk(self, w: int, h: int) -> Image.Image:
        """
        绢本：偏黄 + 经纬网格 + 轻微光泽。
        """
        base = np.full((h, w, 3), [242, 232, 208], dtype=np.float32)

        # 经线（竖直）
        xx = np.arange(w)
        warp = (np.sin(xx * np.pi / 3.0) * 0.5 + 0.5)[None, :]
        # 纬线（水平）
        yy = np.arange(h)
        weft = (np.sin(yy * np.pi / 3.0) * 0.5 + 0.5)[:, None]

        grid = (warp * 0.5 + weft * 0.5) * 6.0
        base -= grid[..., None] * np.array([1.0, 1.2, 1.5], dtype=np.float32)

        # 光泽不均
        glow = self._value_noise(w, h, cell=96)
        base += (glow[..., None] - 0.5) * 6.0

        return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))

    def _tex_aged(self, w: int, h: int) -> Image.Image:
        """
        老纸：明显泛黄 + 深浅斑块。
        """
        base = np.full((h, w, 3), [228, 210, 172], dtype=np.float32)

        # 大块深浅
        blotch = self._value_noise(w, h, cell=48)
        base -= (blotch[..., None] - 0.5) * 30.0

        # 小霉点
        rng = np.random.default_rng(self.seed)
        spots = rng.random((h, w))
        mask = spots > 0.997
        base[mask] *= np.array([0.72, 0.66, 0.55], dtype=np.float32)

        return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))

    def _tex_brown(self, w: int, h: int) -> Image.Image:
        """
        褐纸：深褐 + 强烈暗角。
        """
        base = np.full((h, w, 3), [200, 176, 132], dtype=np.float32)

        # 中心亮、四周暗
        yy, xx = np.mgrid[0:h, 0:w]
        cx, cy = w / 2, h / 2
        r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        r /= (np.sqrt(cx ** 2 + cy ** 2) + 1e-6)
        base -= (r ** 1.6)[..., None] * 60.0

        # 纤维
        rng = np.random.default_rng(self.seed)
        fiber = np.abs(rng.normal(0, 1.0, (h, w)))
        fiber = np.asarray(
            Image.fromarray(np.clip(fiber * 6, 0, 255).astype(np.uint8))
            .filter(ImageFilter.GaussianBlur(0.8)),
            dtype=np.float32,
        ) / 255.0
        base -= fiber[..., None] * 8.0

        return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))

    # ------------------------------------------------------------
    # 老化效果层
    # ------------------------------------------------------------

    def _yellowing(self, arr: np.ndarray, strength: float) -> np.ndarray:
        """
        泛黄：整体偏暖 + 轻微降对比。
        """
        # 暖色调因子
        warmth = np.array([1.06, 1.00, 0.86], dtype=np.float32)
        amount = 0.4 + 0.6 * strength
        warmed = arr * (1 - amount) + arr * warmth * amount

        # 降对比（向中灰靠拢一点点）
        gray = warmed.mean(axis=2, keepdims=True)
        contrast = 0.92 - 0.10 * strength
        out = gray + (warmed - gray) * contrast

        return out

    def _foxing(self, arr: np.ndarray, strength: float) -> np.ndarray:
        """
        霉斑 / 水渍：随机黄褐色小斑 + 少量大斑。
        """
        h, w = arr.shape[:2]
        rng = np.random.default_rng(
            (self.seed or 0) + 17
        )

        # 密度随 strength 上升
        n_small = int((w * h) * (0.00002 + 0.00008 * strength))
        n_large = int(20 + 80 * strength)

        out = arr.copy()

        # 小斑：直接改像素
        if n_small > 0:
            ys = rng.integers(0, h, n_small)
            xs = rng.integers(0, w, n_small)
            tint = np.array([0.86, 0.74, 0.55], dtype=np.float32)
            for y, x in zip(ys, xs):
                out[y, x] = out[y, x] * tint

        # 大斑：用 PIL 画半透明圆
        if n_large > 0:
            overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            d = ImageDraw.Draw(overlay)
            for _ in range(n_large):
                cx = rng.integers(0, w)
                cy = rng.integers(0, h)
                r = int(rng.integers(8, 40))
                a = int(18 + 45 * strength)
                color = (150 + rng.integers(0, 40),
                         120 + rng.integers(0, 30),
                         70 + rng.integers(0, 30),
                         a)
                d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
            overlay = overlay.filter(ImageFilter.GaussianBlur(6))
            base = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert("RGBA")
            base = Image.alpha_composite(base, overlay)
            out = np.asarray(base.convert("RGB"), dtype=np.float32)

        return out

    def _wear(self, arr: np.ndarray, strength: float) -> np.ndarray:
        """
        边缘磨损：四边不规则变暗 + 少量缺口。
        """
        h, w = arr.shape[:2]
        rng = np.random.default_rng((self.seed or 0) + 31)

        # 生成边缘遮罩：0=完好，1=磨损
        mask = np.zeros((h, w), dtype=np.float32)

        # 四边渐变
        edge = max(4, int(min(w, h) * 0.04))
        for i in range(edge):
            v = 1.0 - i / edge
            mask[i, :] = np.maximum(mask[i, :], v * 0.9)
            mask[h - 1 - i, :] = np.maximum(mask[h - 1 - i, :], v * 0.9)
            mask[:, i] = np.maximum(mask[:, i], v * 0.9)
            mask[:, w - 1 - i] = np.maximum(mask[:, w - 1 - i], v * 0.9)

        # 加噪声让边缘不规则
        noise = rng.random((h, w)).astype(np.float32)
        mask = mask * (0.6 + 0.4 * noise)

        # 挖几个缺口
        n_gaps = int(6 + 20 * strength)
        for _ in range(n_gaps):
            side = rng.integers(0, 4)
            length = int(rng.integers(8, max(10, min(w, h) // 6)))
            depth = int(rng.integers(2, max(3, edge)))
            if side == 0:      # 上
                x = int(rng.integers(0, w))
                x2 = min(w, x + length)
                mask[0:depth, x:x2] = 1.0
            elif side == 1:    # 下
                x = int(rng.integers(0, w))
                x2 = min(w, x + length)
                mask[h - depth:h, x:x2] = 1.0
            elif side == 2:    # 左
                y = int(rng.integers(0, h))
                y2 = min(h, y + length)
                mask[y:y2, 0:depth] = 1.0
            else:              # 右
                y = int(rng.integers(0, h))
                y2 = min(h, y + length)
                mask[y:y2, w - depth:w] = 1.0

        mask = np.clip(mask * (0.6 + 0.6 * strength), 0, 1)

        # 磨损区 → 变暗 + 偏黄
        wear_color = np.array([170, 148, 110], dtype=np.float32)
        out = arr * (1 - mask[..., None]) + wear_color * mask[..., None]

        return out

    def _vignette(self, arr: np.ndarray, strength: float) -> np.ndarray:
        """暗角：四周压暗。"""
        h, w = arr.shape[:2]
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        cx, cy = w / 2, h / 2
        r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        r /= (np.sqrt(cx ** 2 + cy ** 2) + 1e-6)

        # 平滑曲线
        v = np.clip((r - 0.4) / 0.6, 0, 1) ** 1.6
        v *= 0.55 * strength

        return arr * (1 - v[..., None])

    def _grain(self, arr: np.ndarray, strength: float) -> np.ndarray:
        """噪点：模拟老照片颗粒。"""
        h, w = arr.shape[:2]
        rng = np.random.default_rng((self.seed or 0) + 53)
        noise = rng.normal(0, 1.0, (h, w)).astype(np.float32)
        noise *= (6.0 + 12.0 * strength)

        return arr + noise[..., None]

    # ------------------------------------------------------------
    # 工具
    # ------------------------------------------------------------

    def _value_noise(
        self,
        w: int,
        h: int,
        cell: int = 64,
    ) -> np.ndarray:
        """
        简易 value noise：生成 cell×cell 随机值，
        放大到 (h, w)，再高斯模糊。返回 0-1。
        """
        rng = np.random.default_rng((self.seed or 0) + 7)
        gw = max(2, w // cell)
        gh = max(2, h // cell)
        grid = rng.random((gh, gw)).astype(np.float32)

        img = Image.fromarray((grid * 255).astype(np.uint8))
        img = img.resize((w, h), Image.Resampling.BICUBIC)
        img = img.filter(ImageFilter.GaussianBlur(cell / 3))
        return np.asarray(img, dtype=np.float32) / 255.0


# ============================================================
# 自检
# ============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  AgingProcessor 自检")
    print("=" * 70)

    out_dir = PROJECT_ROOT / "output" / "tmp" / "aging"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 造一张测试图：米白底 + 一个红方块 + 一条黑线
    test = Image.new("RGB", (800, 1200), (245, 240, 225))
    d = ImageDraw.Draw(test)
    d.rectangle([300, 400, 500, 600], fill=(180, 40, 40))
    d.line([100, 800, 700, 900], fill=(30, 30, 30), width=6)
    test.save(out_dir / "_source.png")
    print(f"\n  ✅ 原图: _source.png")

    ap = AgingProcessor(seed=42)

    # 1. 四种纹理（全套效果）
    for tex in ["xuan_paper", "silk", "aged", "brown"]:
        out = ap.apply(test, texture=tex, strength=0.6)
        out.save(out_dir / f"tex_{tex}.png")
        print(f"  ✅ 纹理 {tex:12s} → tex_{tex}.png")

    # 2. 单效果对比
    for eff in ALL_EFFECTS:
        out = ap.apply(test, texture=None, effects=[eff], strength=0.8)
        out.save(out_dir / f"eff_{eff}.png")
        print(f"  ✅ 效果 {eff:10s} → eff_{eff}.png")

    # 3. 最强做旧
    out = ap.apply(test, texture="aged", strength=1.0)
    out.save(out_dir / "max_aged.png")
    print(f"  ✅ 最强做旧 → max_aged.png")

    # 4. 可复现性
    ap1 = AgingProcessor(seed=1)
    ap2 = AgingProcessor(seed=1)
    o1 = np.asarray(ap1.apply(test, texture="aged", strength=0.7))
    o2 = np.asarray(ap2.apply(test, texture="aged", strength=0.7))
    same = np.array_equal(o1, o2)
    print(f"\n  🔁 seed 复现: {'✅ 一致' if same else '❌ 不一致'}")

    print("\n" + "=" * 70)
    print("  ✅ 自检完成")
    print("=" * 70)