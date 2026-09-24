# services/scroll_composer.py
"""
ArtForge 画幅合成器
职责：
- 立轴：加绫边（天地/左右）+ 上下木轴 + 惊燕带
- 横卷：加引首纸 + 拖尾纸 + 天头地头
- 屏风：多扇拼接（2/4/6 扇）
- 团扇：圆形裁切 + 扇柄
- 册页：多页组合（蝴蝶装）

设计原则：
- 所有装裱元素程序生成（不依赖素材图）
- 颜色参考传统装裱色谱（米黄绫、深褐轴、青绿引首）
- 支持 seed 复现
"""
from __future__ import annotations
import random
from pathlib import Path
from typing import Optional, Tuple, List
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance


# ============================================================
# 传统装裱色谱（参考故宫装裱配色）
# ============================================================
class MountColors:
    """传统装裱配色"""
    # 绫边（米黄/浅驼色）
    LING_BEIGE     = (228, 213, 180)  # 米黄绫
    LING_LIGHT     = (238, 225, 195)  # 浅驼绫
    LING_DARK      = (195, 170, 125)  # 深驼绫
    # 轴头（木色）
    ZHOU_WOOD      = (95, 60, 35)     # 深褐木轴
    ZHOU_WOOD_L    = (135, 95, 60)    # 浅褐木轴
    ZHOU_JADE      = (120, 155, 120)  # 青玉轴
    ZHOU_RED       = (140, 45, 40)    # 朱红漆轴
    # 引首/拖尾纸
    YINSHOU_PAPER  = (245, 238, 220)  # 仿古宣纸
    TUOWEI_PAPER   = (240, 230, 210)  # 拖尾纸（略深）
    # 惊燕带（立轴上方两条细带）
    JINGYAN        = (180, 155, 110)  # 惊燕带色
    # 屏风框
    BYOBU_FRAME    = (60, 45, 30)     # 深木框
    BYOBU_GOLD     = (210, 175, 95)   # 金箔边
    # 团扇
    FAN_HANDLE     = (110, 75, 45)    # 扇柄木色
    FAN_RIB        = (200, 175, 130)  # 扇骨


# ============================================================
# 纹理生成工具
# ============================================================
def _make_ling_texture(
    width: int, height: int,
    base_color: Tuple[int, int, int],
    seed: Optional[int] = None,
) -> Image.Image:
    """
    生成绫缎纹理（斜纹 + 微噪点）
    """
    rng = random.Random(seed)
    img = Image.new("RGB", (width, height), base_color)
    draw = ImageDraw.Draw(img)

    # 斜纹（绫缎特征）
    step = 4
    for i in range(-height, width, step):
        shade = rng.randint(-12, 12)
        c = tuple(max(0, min(255, base_color[k] + shade)) for k in range(3))
        draw.line([(i, 0), (i + height, height)], fill=c, width=1)

    # 微噪点（用 PIL 直接画小点）
    n_dots = width * height // 200
    for _ in range(n_dots):
        x = rng.randint(0, width - 1)
        y = rng.randint(0, height - 1)
        shade = rng.randint(-8, 8)
        c = tuple(max(0, min(255, base_color[k] + shade)) for k in range(3))
        draw.point((x, y), fill=c)

    return img

def _make_wood_texture(
    width: int, height: int,
    base_color: Tuple[int, int, int],
    seed: Optional[int] = None,
    vertical: bool = True,
) -> Image.Image:
    """生成木纹纹理（轴头用）"""
    rng = random.Random(seed)
    img = Image.new("RGB", (width, height), base_color)
    draw = ImageDraw.Draw(img)

    # 木纹线条
    n_lines = 8 + rng.randint(0, 4)
    for _ in range(n_lines):
        shade = rng.randint(-25, -5)
        c = tuple(max(0, base_color[k] + shade) for k in range(3))
        if vertical:
            x = rng.randint(0, width - 1)
            w = rng.randint(1, 2)
            draw.line([(x, 0), (x, height)], fill=c, width=w)
        else:
            y = rng.randint(0, height - 1)
            w = rng.randint(1, 2)
            draw.line([(0, y), (width, y)], fill=c, width=w)
    return img


def _make_paper_texture(
    width: int, height: int,
    base_color: Tuple[int, int, int],
    seed: Optional[int] = None,
) -> Image.Image:
    """生成仿古宣纸纹理（纤维感）"""
    rng = random.Random(seed)
    img = Image.new("RGB", (width, height), base_color)
    draw = ImageDraw.Draw(img)

    # 纤维丝
    for _ in range(width * height // 800):
        x = rng.randint(0, width - 1)
        y = rng.randint(0, height - 1)
        length = rng.randint(3, 10)
        shade = rng.randint(-15, -5)
        c = tuple(max(0, base_color[k] + shade) for k in range(3))
        draw.line([(x, y), (x + length, y + rng.randint(-1, 1))], fill=c, width=1)

    # 轻微泛黄斑点
    for _ in range(width * height // 4000):
        x = rng.randint(0, width - 1)
        y = rng.randint(0, height - 1)
        r = rng.randint(1, 3)
        shade = rng.randint(-20, -8)
        c = tuple(max(0, base_color[k] + shade) for k in range(3))
        draw.ellipse([(x - r, y - r), (x + r, y + r)], fill=c)

    return img


# ============================================================
# ScrollComposer 主类
# ============================================================
class ScrollComposer:
    """画幅合成器"""

    def __init__(self, seed: Optional[int] = None):
        self.seed = seed
        self.rng = random.Random(seed)

    # ---------- 立轴（挂轴） ----------
    def compose_vertical_scroll(
        self,
        artwork: Image.Image,
        ling_color: Tuple[int, int, int] = MountColors.LING_BEIGE,
        zhou_color: Tuple[int, int, int] = MountColors.ZHOU_WOOD,
        top_ratio: float = 0.15,       # 天头占比
        bottom_ratio: float = 0.25,    # 地头占比
        side_ratio: float = 0.08,      # 左右边占比
        jingyan: bool = True,          # 加惊燕带
    ) -> Image.Image:
        """
        立轴装裱：天头 + 地头 + 左右绫边 + 上下木轴 + 惊燕带
        """
        aw, ah = artwork.size
        # 计算绫边尺寸
        side_w = max(20, int(aw * side_ratio))
        top_h = max(40, int(ah * top_ratio))
        bottom_h = max(60, int(ah * bottom_ratio))

        # 总尺寸
        total_w = aw + side_w * 2
        total_h = ah + top_h + bottom_h

        canvas = Image.new("RGB", (total_w, total_h), ling_color)

        # 绫边纹理
        ling_tex = _make_ling_texture(total_w, total_h, ling_color, self.seed)
        canvas.paste(ling_tex)

        # 贴画心
        canvas.paste(artwork, (side_w, top_h))

        # 画心细边（深色镶线，1-2px）
        draw = ImageDraw.Draw(canvas)
        border_color = tuple(max(0, c - 30) for c in ling_color)
        draw.rectangle(
            [side_w, top_h, side_w + aw - 1, top_h + ah - 1],
            outline=border_color, width=1,
        )

        # 惊燕带（天头两条竖带）
        if jingyan:
            jy_w = max(6, side_w // 3)
            jy_h = int(top_h * 0.7)
            jy_y = int(top_h * 0.1)
            jy_x1 = side_w + int(aw * 0.25)
            jy_x2 = side_w + int(aw * 0.75) - jy_w
            for x in (jy_x1, jy_x2):
                draw.rectangle(
                    [x, jy_y, x + jy_w, jy_y + jy_h],
                    fill=MountColors.JINGYAN,
                )

        # 上轴（细轴，天杆）
        rod_h = max(8, int(total_h * 0.012))
        rod_tex = _make_wood_texture(total_w, rod_h, zhou_color, self.seed, vertical=False)
        canvas.paste(rod_tex, (0, 0))

        # 下轴（粗轴，地杆）
        bottom_rod_h = max(18, int(total_h * 0.025))
        rod_tex2 = _make_wood_texture(total_w, bottom_rod_h, zhou_color, self.seed, vertical=False)
        canvas.paste(rod_tex2, (0, total_h - bottom_rod_h))

        # 轴头（下轴两端圆形装饰）
        cap_r = bottom_rod_h // 2 + 3
        rod_y = total_h - bottom_rod_h // 2
        for x in (cap_r, total_w - cap_r):
            draw.ellipse(
                [x - cap_r, y - cap_r, x + cap_r, y + cap_r],
                fill=MountColors.ZHOU_JADE,
                outline=MountColors.ZHOU_WOOD, width=2,
            )

        return canvas

    # ---------- 横卷（手卷） ----------
    def compose_horizontal_scroll(
        self,
        artwork: Image.Image,
        yinshou: bool = True,      # 加引首纸
        tuowei: bool = True,       # 加拖尾纸
        paper_color: Tuple[int, int, int] = MountColors.YINSHOU_PAPER,
    ) -> Image.Image:
        """
        横卷装裱：天头 + 引首 + 画心 + 拖尾 + 地头
        横向拼接，整体高度一致
        """
        aw, ah = artwork.size
        # 各段宽度（按画心比例）
        tiantou_w = int(aw * 0.25)
        yinshou_w = int(aw * 0.35) if yinshou else 0
        tuowei_w = int(aw * 0.6) if tuowei else 0
        ditou_w = int(aw * 0.2)

        total_w = tiantou_w + yinshou_w + aw + tuowei_w + ditou_w
        total_h = ah

        canvas = Image.new("RGB", (total_w, total_h), paper_color)
        draw = ImageDraw.Draw(canvas)

        x = 0
        # 天头
        tiantou_tex = _make_paper_texture(tiantou_w, total_h, MountColors.YINSHOU_PAPER, self.seed)
        canvas.paste(tiantou_tex, (x, 0))
        x += tiantou_w

        # 引首（略深色的纸，可题写卷名）
        if yinshou:
            ys_tex = _make_paper_texture(yinshou_w, total_h, MountColors.LING_DARK, self.seed)
            canvas.paste(ys_tex, (x, 0))
            # 引首与画心间细线
            draw.line([(x + yinshou_w, 0), (x + yinshou_w, total_h)],
                      fill=MountColors.ZHOU_WOOD, width=2)
            x += yinshou_w

        # 画心
        canvas.paste(artwork, (x, 0))
        draw.rectangle([x, 0, x + aw, total_h], outline=MountColors.ZHOU_WOOD, width=2)
        x += aw

        # 拖尾（用于后人题跋）
        if tuowei:
            tw_tex = _make_paper_texture(tuowei_w, total_h, MountColors.TUOWEI_PAPER, self.seed)
            canvas.paste(tw_tex, (x, 0))
            draw.line([(x, 0), (x, total_h)], fill=MountColors.ZHOU_WOOD, width=2)
            x += tuowei_w

        # 地头
        ditou_tex = _make_paper_texture(ditou_w, total_h, MountColors.YINSHOU_PAPER, self.seed)
        canvas.paste(ditou_tex, (x, 0))

        return canvas

    # ---------- 屏风（多扇） ----------
    def compose_byobu(
        self,
        artworks: List[Image.Image],
        n_panels: int = 6,
        frame_color: Tuple[int, int, int] = MountColors.BYOBU_FRAME,
        gold_edge: bool = True,
    ) -> Image.Image:
        """
        屏风装裱：多扇画面 + 木框 + 金箔边
        artworks: 每扇的画面（数量应等于 n_panels，不足则循环复用）
        """
        if not artworks:
            raise ValueError("至少需要一张画面")

        # 统一到相同尺寸
        panel_w, panel_h = artworks[0].size
        for a in artworks:
            if a.size != (panel_w, panel_h):
                a = a.resize((panel_w, panel_h), Image.Resampling.LANCZOS)

        # 框宽
        frame_w = max(8, panel_w // 40)
        gap_w = max(4, frame_w // 2)

        total_w = n_panels * panel_w + (n_panels + 1) * frame_w + (n_panels - 1) * gap_w
        total_h = panel_h + 2 * frame_w

        canvas = Image.new("RGB", (total_w, total_h), frame_color)
        draw = ImageDraw.Draw(canvas)

        # 木纹底
        frame_tex = _make_wood_texture(total_w, total_h, frame_color, self.seed, vertical=False)
        canvas.paste(frame_tex)

        x = frame_w
        for i in range(n_panels):
            art = artworks[i % len(artworks)]
            # 金箔边（内圈）
            if gold_edge:
                gold_w = max(2, frame_w // 3)
                draw.rectangle(
                    [x - gold_w, frame_w - gold_w,
                     x + panel_w + gold_w, frame_w + panel_h + gold_w],
                    fill=MountColors.BYOBU_GOLD,
                )
            canvas.paste(art, (x, frame_w))
            x += panel_w + frame_w + gap_w

        return canvas

    # ---------- 团扇（圆形） ----------
    def compose_fan(
        self,
        artwork: Image.Image,
        handle_color: Tuple[int, int, int] = MountColors.FAN_HANDLE,
        show_handle: bool = True,
    ) -> Image.Image:
        """
        团扇装裱：圆形画面 + 扇柄
        """
        aw, ah = artwork.size
        # 圆形直径取短边
        diameter = min(aw, ah)
        # 扇柄长度
        handle_len = int(diameter * 0.8) if show_handle else 0
        handle_w = max(10, diameter // 25)

        # 画布尺寸
        canvas_w = diameter + 40
        canvas_h = diameter + handle_len + 20

        canvas = Image.new("RGBA", (canvas_w, canvas_h), (255, 255, 255, 0))
        draw = ImageDraw.Draw(canvas)

        # 扇柄（先画，被扇面覆盖一部分）
        if show_handle:
            hx = canvas_w // 2
            hy_start = diameter + 10
            hy_end = hy_start + handle_len
            # 木纹柄
            handle_img = _make_wood_texture(handle_w, handle_len, handle_color, self.seed)
            handle_img = handle_img.convert("RGBA")
            canvas.paste(handle_img, (hx - handle_w // 2, hy_start), handle_img)

        # 圆形裁切画心
        cx, cy = canvas_w // 2, diameter // 2 + 10
        mask = Image.new("L", (diameter, diameter), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse([0, 0, diameter, diameter], fill=255)

        # 裁切
        art_sq = artwork.copy()
        # 居中裁切为正方形
        if aw > ah:
            left = (aw - ah) // 2
            art_sq = art_sq.crop((left, 0, left + ah, ah))
        elif ah > aw:
            top = (ah - aw) // 2
            art_sq = art_sq.crop((0, top, aw, top + aw))
        art_sq = art_sq.resize((diameter, diameter), Image.Resampling.LANCZOS)

        art_rgba = art_sq.convert("RGBA")
        canvas.paste(art_rgba, (cx - diameter // 2, cy - diameter // 2), mask)

        # 扇边（竹圈）
        draw = ImageDraw.Draw(canvas)
        draw.ellipse(
            [cx - diameter // 2, cy - diameter // 2,
             cx + diameter // 2, cy + diameter // 2],
            outline=MountColors.FAN_RIB, width=max(3, diameter // 80),
        )

        return canvas.convert("RGB")

    # ---------- 册页（多页组合） ----------
    def compose_album(
        self,
        artworks: List[Image.Image],
        cols: int = 2,
        paper_color: Tuple[int, int, int] = MountColors.YINSHOU_PAPER,
        gap: int = 20,
        border: int = 15,
    ) -> Image.Image:
        """
        册页装裱：多幅画按网格排列，仿古宣纸底 + 细边
        """
        if not artworks:
            raise ValueError("至少需要一张画面")

        # 统一尺寸
        cell_w, cell_h = artworks[0].size
        for a in artworks:
            if a.size != (cell_w, cell_h):
                a = a.resize((cell_w, cell_h), Image.Resampling.LANCZOS)

        n = len(artworks)
        rows = (n + cols - 1) // cols

        total_w = cols * cell_w + (cols - 1) * gap + 2 * border
        total_h = rows * cell_h + (rows - 1) * gap + 2 * border

        canvas = Image.new("RGB", (total_w, total_h), paper_color)
        paper_tex = _make_paper_texture(total_w, total_h, paper_color, self.seed)
        canvas.paste(paper_tex)

        draw = ImageDraw.Draw(canvas)
        for i, art in enumerate(artworks):
            r, c = divmod(i, cols)
            x = border + c * (cell_w + gap)
            y = border + r * (cell_h + gap)
            canvas.paste(art, (x, y))
            # 细边
            draw.rectangle(
                [x - 2, y - 2, x + cell_w + 2, y + cell_h + 2],
                outline=MountColors.ZHOU_WOOD, width=1,
            )

        return canvas

    # ---------- 自动分发 ----------
    def compose(
        self,
        artwork: Image.Image,
        composition: str = "vertical",
        extra_artworks: Optional[List[Image.Image]] = None,
        **kwargs,
    ) -> Image.Image:
        """
        根据 composition 关键字自动选择装裱方式
        composition: vertical / horizontal / byobu / fan / album
        """
        comp = (composition or "").lower()

        if any(w in comp for w in ["vertical", "scroll", "hanging", "立轴", "挂轴", "lidu"]):
            return self.compose_vertical_scroll(artwork, **kwargs)
        if any(w in comp for w in ["horizontal", "handscroll", "横卷", "长卷", "emaki"]):
            return self.compose_horizontal_scroll(artwork, **kwargs)
        if any(w in comp for w in ["fan", "团扇", "round"]):
            return self.compose_fan(artwork, **kwargs)
        if any(w in comp for w in ["album", "册页"]):
            arts = extra_artworks or [artwork]
            return self.compose_album(arts, **kwargs)
        if any(w in comp for w in ["screen", "byobu", "屏风"]):
            arts = extra_artworks or [artwork]
            return self.compose_byobu(arts, **kwargs)

        # 默认立轴
        return self.compose_vertical_scroll(artwork, **kwargs)


# ============================================================
# 自检
# ============================================================
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    print("=" * 70)
    print("  ScrollComposer 自检")
    print("=" * 70)

    # 创建一张测试画心（模拟水墨山水）
    test_art = Image.new("RGB", (600, 900), (245, 240, 225))
    draw = ImageDraw.Draw(test_art)
    # 简单山水
    draw.polygon([(0, 600), (200, 300), (400, 500), (600, 200), (600, 900), (0, 900)],
                 fill=(80, 85, 90))
    draw.polygon([(0, 700), (300, 450), (600, 650), (600, 900), (0, 900)],
                 fill=(50, 55, 60))
    draw.ellipse([(450, 100), (550, 200)], fill=(220, 200, 170))  # 月亮

    out_dir = Path(__file__).resolve().parents[1] / "output" / "tmp"
    out_dir.mkdir(parents=True, exist_ok=True)

    composer = ScrollComposer(seed=42)

    # 1. 立轴
    r1 = composer.compose_vertical_scroll(test_art)
    r1.save(out_dir / "test_vertical.png")
    print(f"✅ 立轴: {r1.size}")

    # 2. 横卷
    r2 = composer.compose_horizontal_scroll(test_art)
    r2.save(out_dir / "test_horizontal.png")
    print(f"✅ 横卷: {r2.size}")

    # 3. 屏风（6 扇）
    r3 = composer.compose_byobu([test_art] * 6, n_panels=6)
    r3.save(out_dir / "test_byobu.png")
    print(f"✅ 屏风: {r3.size}")

    # 4. 团扇
    r4 = composer.compose_fan(test_art)
    r4.save(out_dir / "test_fan.png")
    print(f"✅ 团扇: {r4.size}")

    # 5. 册页（4 页）
    r5 = composer.compose_album([test_art] * 4, cols=2)
    r5.save(out_dir / "test_album.png")
    print(f"✅ 册页: {r5.size}")

    print("\n" + "=" * 70)
    print(f"  自检完成 → {out_dir}")
    print("=" * 70)