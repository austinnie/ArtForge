"""
关注引导卡合成器 v5 (双版本生成)
改进：
1. 移除视频号二维码，单图居中更显克制
2. 生成两个版本：技术实战版 (footer_tech.png) 和 东方美学版 (footer_art.png)
3. 针对不同版本使用不同配色和文案
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# ==================== 通用配置 ====================
QR_WECHAT = "公众号.png"
QR_SIZE        = 240
CARD_PAD       = 14
CARD_RADIUS    = 12
W              = 800
PADDING_TOP    = 80
PADDING_BOTTOM = 70
LINE_PADDING   = 120

# 颜色通用配置
BG_CARD     = "#ffffff"
C_NAME      = "#1e1e3c"
C_LINE      = "#c8c8dd"

# 字体
FONT_NAME  = "C:/Windows/Fonts/simsun.ttc"
FONT_BOLD  = "C:/Windows/Fonts/msyhbd.ttc"
FONT_REG   = "C:/Windows/Fonts/msyh.ttc"
FONT_EMOJI = "C:/Windows/Fonts/seguiemj.ttf"

# ==================== 双版本配置 ====================
CARDS_CONFIG = [
    {
        "output": "footer_tech.png",
        "name": "爱行天下行者无疆",
        "tagline": "左手 AI 代码，右手东方美学",
        "motto": "以技术拓路  以文心耀灯",
        "tips": [
            "📌 关注我 → 每天一个 GitHub 实战",
            "💡 点个在看 → 分享给身边的开发者",
            "📱 长按识别下方二维码",
        ],
        "bg": "#f4f7fa",       # 偏科技感的极浅灰蓝
        "tag_color": "#4a5568",
        "motto_color": "#718096",
        "tip_color": "#2d3748",
        "label_color": "#a0aec0",
    },
    {
        "output": "footer_art.png",
        "name": "爱行天下行者无疆",
        "tagline": "在代码之外，探寻东方美学",
        "motto": "观云听雨  修心造境",
        "tips": [
            "📌 关注我 → 每日分享国风艺术",
            "💡 点个在看 → 把美分享给朋友",
            "📱 长按识别下方二维码",
        ],
        "bg": "#f4f1fa",       # 原版的淡紫底
        "tag_color": "#5c5c80",
        "motto_color": "#666688",
        "tip_color": "#2a2a4a",
        "label_color": "#8888a0",
    }
]
# ====================================================

def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        print(f"⚠️ 字体加载失败 {path}，回退默认")
        return ImageFont.load_default()

def is_emoji(ch):
    cp = ord(ch)
    return (0x1F300 <= cp <= 0x1FAFF or 0x1F000 <= cp <= 0x1F2FF or 0x2600 <= cp <= 0x26FF or 0x2700 <= cp <= 0x27BF)

def measure_text(draw, text, cjk_font, emoji_font):
    items = []
    total_w = 0
    max_h = 0
    for ch in text:
        use_emoji = is_emoji(ch) and emoji_font is not None
        font = emoji_font if use_emoji else cjk_font
        try:
            bbox = draw.textbbox((0, 0), ch, font=font)
        except Exception:
            bbox = (0, 0, 0, 0)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        if w == 0 and use_emoji:
            font = cjk_font
            use_emoji = False
            bbox = draw.textbbox((0, 0), ch, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
        if w == 0: w = 6
        items.append((ch, font, use_emoji, w))
        total_w += w
        max_h = max(max_h, h)
    return items, total_w, max_h

def draw_mixed_line(draw, canvas, text, y, cjk_font, emoji_font, fill):
    items, total_w, line_h = measure_text(draw, text, cjk_font, emoji_font)
    x = (canvas.width - total_w) // 2
    for ch, font, use_emoji, w in items:
        if use_emoji:
            try:
                draw.text((x, y), ch, font=font, embedded_color=True)
            except TypeError:
                draw.text((x, y), ch, font=font, fill=fill)
        else:
            draw.text((x, y), ch, font=font, fill=fill)
        x += w
    return line_h

def build_card(cfg):
    print(f"🎨 正在生成: {cfg['output']} ...")
    
    # 载入单个二维码
    qr_w = Image.open(QR_WECHAT).convert("RGB").resize((QR_SIZE, QR_SIZE), Image.LANCZOS)

    f_name  = load_font(FONT_NAME, 52)
    f_ovo   = load_font(FONT_BOLD, 14)
    f_tag   = load_font(FONT_REG, 22)
    f_motto = load_font(FONT_NAME, 22)
    f_tip   = load_font(FONT_REG, 22)
    f_emoji = load_font(FONT_EMOJI, 24)

    tmp = Image.new("RGB", (1, 1))
    td = ImageDraw.Draw(tmp)

    _, _, h_name  = measure_text(td, cfg['name'], f_name, f_emoji)
    _, _, h_tag   = measure_text(td, cfg['tagline'], f_tag, f_emoji)
    _, _, h_motto = measure_text(td, cfg['motto'], f_motto, f_emoji)
    h_ovo = 18
    tip_hs = [measure_text(td, t, f_tip, f_emoji)[2] for t in cfg['tips']]

    card_h = QR_SIZE + CARD_PAD * 2

    H = PADDING_TOP + 30 + h_name + 10 + h_ovo + 18 + h_tag + 28 + 1 + 28 + h_motto + 32
    for th in tip_hs:
        H += th + 14
    H += 40 + card_h + PADDING_BOTTOM

    # 正式画布
    canvas = Image.new("RGB", (W, H), cfg['bg'])
    draw = ImageDraw.Draw(canvas)

    y = PADDING_TOP

    # 顶部装饰线
    draw.line([(LINE_PADDING, y - 30), (W - LINE_PADDING, y - 30)], fill=C_LINE, width=1)

    # 名字
    draw_mixed_line(draw, canvas, cfg['name'], y, f_name, f_emoji, C_NAME)
    y += h_name + 10

    # OVO 装饰
    ovo_text = "— OVO —"
    bbox = td.textbbox((0, 0), ovo_text, font=f_ovo)
    ow = bbox[2] - bbox[0]
    draw.text(((W - ow) // 2, y), ovo_text, font=f_ovo, fill=cfg['label_color'])
    y += h_ovo + 18

    # 副标题
    draw_mixed_line(draw, canvas, cfg['tagline'], y, f_tag, f_emoji, cfg['tag_color'])
    y += h_tag + 28

    # 分隔线
    draw.line([(LINE_PADDING, y), (W - LINE_PADDING, y)], fill=C_LINE, width=1)
    y += 1 + 28

    # 箴言
    draw_mixed_line(draw, canvas, cfg['motto'], y, f_motto, f_emoji, cfg['motto_color'])
    y += h_motto + 32

    # 引导文案
    for i, tip in enumerate(cfg['tips']):
        draw_mixed_line(draw, canvas, tip, y, f_tip, f_emoji, cfg['tip_color'])
        y += tip_hs[i] + 14

    # 居中二维码 + 白色圆角卡片
    y += 40
    x_start = (W - QR_SIZE) // 2

    draw.rounded_rectangle(
        [x_start - CARD_PAD, y - CARD_PAD, x_start + QR_SIZE + CARD_PAD, y + QR_SIZE + CARD_PAD],
        radius=CARD_RADIUS, fill=BG_CARD, outline=C_LINE, width=1,
    )
    canvas.paste(qr_w, (x_start, y))

    # 保存
    canvas.save(cfg['output'], quality=95)
    print(f"  ✅ 已保存: {Path(cfg['output']).resolve()} (尺寸: {canvas.size})")

def main():
    for cfg in CARDS_CONFIG:
        build_card(cfg)

if __name__ == "__main__":
    main()