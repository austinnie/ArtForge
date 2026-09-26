# run_gui_tk.py
"""
ArtForge Tkinter GUI（桌面版）

用法:
    python run_gui_tk.py
"""
from __future__ import annotations

import os
import sys
import threading
import subprocess
from pathlib import Path
from datetime import datetime
from tkinter import (
    Tk, ttk, StringVar, IntVar, BooleanVar,
    Frame, Label, Button, Text, Canvas, Scrollbar,
    END, BOTH, LEFT, RIGHT, TOP, BOTTOM, X, Y,
    DISABLED, NORMAL, filedialog, messagebox,
)
from tkinter.constants import NW

# -------- 项目路径 --------
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# -------- .env --------
try:
    from dotenv import load_dotenv
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    else:
        load_dotenv()
except ImportError:
    pass

# -------- PIL（图片预览） --------
try:
    from PIL import Image, ImageTk
    PIL_OK = True
except ImportError:
    PIL_OK = False


# ============================================================
# 元数据
# ============================================================
COMPOSITIONS = {
    "vertical":   "立轴 9:16",
    "horizontal": "横卷 16:9",
    "byobu":      "屏风 4:3",
    "fan":        "团扇 1:1",
    "album":      "册页 3:4",
}

SEAL_SCHEMES = {
    "classic":  "传统经典（朱文方 + 朱文长方）",
    "contrast": "对比鲜明（白文方 + 朱文长方）",
    "luxury":   "华丽大气（双边框 + 长方 + 圆印）",
    "minimal":  "简洁（只有右下朱文方印）",
}

LANGUAGES = {
    "auto":     "自动",
    "chinese":  "中文",
    "japanese": "日文",
}

ENGINES = ["pollinations", "agnes", "siliconflow"]


# ============================================================
# 主窗口
# ============================================================
class ArtForgeApp:
    def __init__(self, root: Tk):
        self.root = root
        self.root.title("ArtForge · 东方艺术生成工坊")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)

        # 缓存
        self._presets_by_cat: dict = {}
        self._preview_img = None       # 防止 GC
        self._current_image_path = None

        # 加载预设
        self._load_presets()

        # 构建 UI
        self._build_menu()
        self._build_body()

        # 状态
        self._set_status("就绪")

    # ---------- 加载预设 ----------
    def _load_presets(self):
        try:
            from core.prompt_builder import PromptBuilder
            builder = PromptBuilder()
            self._presets_by_cat = builder.list_presets() or {}
        except Exception as e:
            self._presets_by_cat = {}
            print(f"⚠️ 加载预设失败: {e}")

    # ---------- 菜单栏 ----------
    def _build_menu(self):
        menubar = ttk.Frame(self.root)
        menubar.pack(side=TOP, fill=X)

        # 顶部标题
        title = Label(
            menubar,
            text="🎎 ArtForge · 东方艺术生成工坊",
            font=("Microsoft YaHei", 14, "bold"),
            fg="#333",
            pady=8,
        )
        title.pack(side=TOP)

        # 刷新按钮
        btn_refresh = Button(
            menubar, text="🔄 刷新预设",
            command=self._on_refresh_presets,
            relief="flat", bg="#f0f0f0",
        )
        btn_refresh.pack(side=RIGHT, padx=8, pady=4)

    # ---------- 主体 ----------
    def _build_body(self):
        body = ttk.Frame(self.root)
        body.pack(side=TOP, fill=BOTH, expand=True)

        # 左侧：参数面板（固定宽度）
        left = ttk.Frame(body, width=320)
        left.pack(side=LEFT, fill=Y)
        left.pack_propagate(False)

        # 右侧：图片预览 + 日志
        right = ttk.Frame(body)
        right.pack(side=RIGHT, fill=BOTH, expand=True)

        self._build_left_panel(left)
        self._build_right_panel(right)

    # ---------- 左侧参数 ----------
    def _build_left_panel(self, parent):
        # 主题分类
        Label(parent, text="主题分类", anchor="w").pack(
            fill=X, padx=12, pady=(12, 2))

        self.var_category = StringVar()
        cats = list(self._presets_by_cat.keys()) or ["yokai"]
        self.combo_category = ttk.Combobox(
            parent, textvariable=self.var_category,
            values=cats, state="readonly",
        )
        self.combo_category.pack(fill=X, padx=12)
        self.combo_category.bind("<<ComboboxSelected>>",
                                 self._on_category_change)
        self.var_category.set(cats[0])

        # 预设
        Label(parent, text="预设", anchor="w").pack(
            fill=X, padx=12, pady=(10, 2))

        self.var_preset = StringVar()
        presets = self._presets_by_cat.get(cats[0], [])
        self.combo_preset = ttk.Combobox(
            parent, textvariable=self.var_preset,
            values=presets, state="readonly",
        )
        self.combo_preset.pack(fill=X, padx=12)
        if presets:
            self.var_preset.set(presets[0])

        # 引擎
        Label(parent, text="引擎", anchor="w").pack(
            fill=X, padx=12, pady=(10, 2))
        self.var_engine = StringVar(value="pollinations")
        ttk.Combobox(
            parent, textvariable=self.var_engine,
            values=ENGINES, state="readonly",
        ).pack(fill=X, padx=12)

        # 画幅
        Label(parent, text="画幅", anchor="w").pack(
            fill=X, padx=12, pady=(10, 2))
        self.var_composition = StringVar(value="vertical")
        comp_frame = ttk.Frame(parent)
        comp_frame.pack(fill=X, padx=12)
        for i, (k, v) in enumerate(COMPOSITIONS.items()):
            ttk.Radiobutton(
                comp_frame, text=v, value=k,
                variable=self.var_composition,
            ).grid(row=i // 2, column=i % 2, sticky="w", padx=4)

        # 印章方案
        Label(parent, text="印章方案", anchor="w").pack(
            fill=X, padx=12, pady=(10, 2))
        self.var_seal_scheme = StringVar(value="contrast")
        ttk.Combobox(
            parent, textvariable=self.var_seal_scheme,
            values=list(SEAL_SCHEMES.keys()), state="readonly",
        ).pack(fill=X, padx=12)

        # 语言
        Label(parent, text="题词语言", anchor="w").pack(
            fill=X, padx=12, pady=(10, 2))
        self.var_language = StringVar(value="auto")
        ttk.Combobox(
            parent, textvariable=self.var_language,
            values=list(LANGUAGES.keys()), state="readonly",
        ).pack(fill=X, padx=12)

        # 功能开关
        Label(parent, text="处理步骤", anchor="w").pack(
            fill=X, padx=12, pady=(10, 2))

        self.var_aging = BooleanVar(value=True)
        self.var_inscription = BooleanVar(value=True)
        self.var_seal = BooleanVar(value=True)
        self.var_watermark = BooleanVar(value=True)
        self.var_scroll = BooleanVar(value=True)

        switch_frame = ttk.Frame(parent)
        switch_frame.pack(fill=X, padx=12)
        ttk.Checkbutton(switch_frame, text="做旧",
                        variable=self.var_aging).pack(anchor="w")
        ttk.Checkbutton(switch_frame, text="题词",
                        variable=self.var_inscription).pack(anchor="w")
        ttk.Checkbutton(switch_frame, text="印章",
                        variable=self.var_seal).pack(anchor="w")
        ttk.Checkbutton(switch_frame, text="水印",
                        variable=self.var_watermark).pack(anchor="w")
        ttk.Checkbutton(switch_frame, text="装裱",
                        variable=self.var_scroll).pack(anchor="w")

        # 种子
        Label(parent, text="随机种子（-1=随机）", anchor="w").pack(
            fill=X, padx=12, pady=(10, 2))
        self.var_seed = StringVar(value="-1")
        ttk.Entry(parent, textvariable=self.var_seed).pack(
            fill=X, padx=12)

        # 按钮
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=X, padx=12, pady=16)

        self.btn_generate = Button(
            btn_frame, text="🚀 一键生成",
            command=self._on_generate,
            bg="#4CAF50", fg="white",
            font=("Microsoft YaHei", 11, "bold"),
            relief="raised", bd=2,
        )
        self.btn_generate.pack(fill=X, pady=4)

        Button(
            btn_frame, text="📂 打开输出目录",
            command=self._on_open_output,
        ).pack(fill=X, pady=4)

        Button(
            btn_frame, text="📁 选择图片查看",
            command=self._on_pick_image,
        ).pack(fill=X, pady=4)

    # ---------- 右侧 ----------
    def _build_right_panel(self, parent):
        # 图片预览
        preview_frame = ttk.LabelFrame(parent, text="图片预览")
        preview_frame.pack(fill=BOTH, expand=True, padx=8, pady=(8, 4))

        self.canvas = Canvas(
            preview_frame, bg="#f0f0f0",
            width=600, height=600,
        )
        self.canvas.pack(fill=BOTH, expand=True, padx=4, pady=4)
        self.canvas.create_text(
            300, 300,
            text="（还没生成图片）\n\n点击左侧「🚀 一键生成」",
            fill="#999", font=("Microsoft YaHei", 12),
            tags="placeholder",
        )
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        # 日志
        log_frame = ttk.LabelFrame(parent, text="执行日志")
        log_frame.pack(fill=BOTH, expand=False, padx=8, pady=(4, 8))

        self.text_log = Text(
            log_frame, height=10, wrap="word",
            font=("Consolas", 10),
        )
        self.text_log.pack(fill=BOTH, expand=True, padx=4, pady=4)

        # 状态栏
        self.status_var = StringVar(value="就绪")
        status = Label(
            self.root, textvariable=self.status_var,
            anchor="w", relief="sunken", bd=1,
            font=("Microsoft YaHei", 9),
        )
        status.pack(side=BOTTOM, fill=X)

    # ============================================================
    # 事件
    # ============================================================

    def _on_category_change(self, event=None):
        cat = self.var_category.get()
        presets = self._presets_by_cat.get(cat, [])
        self.combo_preset["values"] = presets
        if presets:
            self.var_preset.set(presets[0])
        else:
            self.var_preset.set("")

    def _on_refresh_presets(self):
        self._load_presets()
        cats = list(self._presets_by_cat.keys()) or ["yokai"]
        self.combo_category["values"] = cats
        self._on_category_change()
        self._set_status(f"✅ 已刷新预设（{len(cats)} 个分类）")

    def _on_canvas_resize(self, event=None):
        # 窗口大小变化时重绘占位
        if self._preview_img is None:
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
            self.canvas.delete("placeholder")
            self.canvas.create_text(
                w // 2, h // 2,
                text="（还没生成图片）\n\n点击左侧「🚀 一键生成」",
                fill="#999", font=("Microsoft YaHei", 12),
                tags="placeholder",
            )

    def _on_open_output(self):
        cat = self.var_category.get() or "misc"
        out_dir = PROJECT_ROOT / "output" / cat
        out_dir.mkdir(parents=True, exist_ok=True)
        try:
            if sys.platform == "win32":
                os.startfile(str(out_dir))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(out_dir)])
            else:
                subprocess.Popen(["xdg-open", str(out_dir)])
            self._set_status(f"📂 已打开: {out_dir}")
        except Exception as e:
            messagebox.showerror("打开失败", str(e))

    def _on_pick_image(self):
        path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[
                ("图片", "*.png *.jpg *.jpeg *.webp"),
                ("所有文件", "*.*"),
            ],
            initialdir=str(PROJECT_ROOT / "output"),
        )
        if not path:
            return
        self._show_image(path)
        self._current_image_path = path
        self._set_status(f"📁 {path}")

    # ============================================================
    # 生成（后台线程）
    # ============================================================

    def _on_generate(self):
        # 收集参数
        params = {
            "category": self.var_category.get(),
            "preset": self.var_preset.get(),
            "engine": self.var_engine.get(),
            "composition": self.var_composition.get(),
            "seal_scheme": self.var_seal_scheme.get(),
            "language": self.var_language.get(),
            "use_aging": self.var_aging.get(),
            "use_inscription": self.var_inscription.get(),
            "use_seal": self.var_seal.get(),
            "use_watermark": self.var_watermark.get(),
            "use_scroll": self.var_scroll.get(),
        }

        seed_str = self.var_seed.get().strip()
        try:
            seed_val = int(seed_str)
            params["seed"] = seed_val if seed_val >= 0 else None
        except ValueError:
            params["seed"] = None

        # 清空日志
        self.text_log.delete("1.0", END)
        self._log("=" * 60)
        self._log(f"开始生成")
        self._log(f"  分类: {params['category']}")
        self._log(f"  预设: {params['preset']}")
        self._log(f"  引擎: {params['engine']}")
        self._log(f"  画幅: {params['composition']}")
        self._log(f"  印章: {params['seal_scheme']}")
        self._log("=" * 60)

        # 禁用按钮
        self.btn_generate.config(state=DISABLED, text="⏳ 生成中...")
        self._set_status("⏳ 生成中，请稍候...")

        # 后台线程跑
        threading.Thread(
            target=self._generate_worker,
            args=(params,),
            daemon=True,
        ).start()

    def _generate_worker(self, params):
        """后台执行生成（不要碰 Tk 组件！）"""
        try:
            from core.prompt_builder import PromptBuilder
            from api_engines import create_engine
            from compose_artwork import (
                InscriptionRenderer, pick_size, theme_from_preset,
                load_config, ARTIST_NAME,
            )

            seed = params["seed"]
            category = params["category"]
            preset = params["preset"]

            # 1. prompt
            builder = PromptBuilder()
            prompt, detail = builder.compose_preset(
                preset, category=category, return_detail=True,
            )
            theme = theme_from_preset(preset, category)

            comp_map = {
                "vertical":   "vertical hanging scroll, kakemono",
                "horizontal": "horizontal handscroll, emaki",
                "byobu":      "folding screen, byobu, multi-panel",
                "fan":        "round fan, circular composition",
                "album":      "square album leaf",
            }
            detail["composition"] = comp_map.get(
                params["composition"], comp_map["vertical"])
            detail.pop("inscription", None)
            parts = [detail[k] for k in builder.LAYER_ORDER
                     if detail.get(k)]
            prompt = ", ".join(parts)

            negative = builder.get_negative()
            negative += (
                ", calligraphy, text, chinese characters, "
                "japanese text, kanji, kana, seal, stamp, "
                "signature, watermark, logo, letters, words"
            )
            self._log(f"✅ Prompt 就绪（主题: {theme}）")

            # 2. 出图
            width, height = pick_size(detail)
            engine = create_engine(params["engine"], load_config())
            self._log(f"🎨 出图中 ({width}x{height})...")
            image = engine.generate_single(
                prompt=prompt, negative=negative,
                width=width, height=height, seed=seed,
            )
            if image.mode != "RGBA":
                image = image.convert("RGBA")
            self._log(f"✅ 出图 {image.size[0]}x{image.size[1]}")

            # 3. 做旧
            if params["use_aging"]:
                try:
                    from services.aging_processor import AgingProcessor
                    image = AgingProcessor(seed=seed).apply(
                        image.convert("RGB"),
                        texture="xuan_paper", strength=0.55,
                    ).convert("RGBA")
                    self._log("✅ 做旧")
                except Exception as e:
                    self._log(f"⚠️ 做旧跳过: {e}")

            # 4. 题词
            inscription_text = ""
            if params["use_inscription"]:
                try:
                    from services.inscription_generator import (
                        InscriptionGenerator,
                    )
                    ig = InscriptionGenerator(seed=seed)
                    lang = params["language"]
                    lang = None if lang == "auto" else lang
                    inscription_text, meta = ig.generate(
                        theme=theme, format="auto",
                        return_meta=True,
                        backend=params["engine"] if params["engine"]
                        in ("agnes", "pollinations") else "auto",
                        category=category, language=lang,
                    )
                    renderer = InscriptionRenderer()
                    fs = max(24, int(min(width, height) * 0.045))
                    image = renderer.render(
                        image, inscription_text,
                        font_size=fs,
                        color=(45, 40, 35),
                        position="top_right",
                        margin=int(min(width, height) * 0.055),
                        max_chars_per_col=8,
                    )
                    self._log(f"✅ 题词: {inscription_text[:30]}...")
                except Exception as e:
                    self._log(f"⚠️ 题词跳过: {e}")

            # 5. 印章
            if params["use_seal"]:
                try:
                    from services.seal_generator import SealGenerator
                    sg = SealGenerator()
                    image = sg.apply_scheme(
                        image, ARTIST_NAME,
                        scheme=params["seal_scheme"],
                        margin_ratio=0.05,
                    )
                    self._log(f"✅ 印章「{ARTIST_NAME}」")
                except Exception as e:
                    self._log(f"⚠️ 印章跳过: {e}")

            # 6. 装裱
            if params["use_scroll"]:
                try:
                    from services.scroll_composer import ScrollComposer
                    sc = ScrollComposer(seed=seed)
                    image = sc.compose(
                        image.convert("RGB"),
                        composition=params["composition"],
                    ).convert("RGBA")
                    self._log(f"✅ 装裱 {params['composition']}")
                except Exception as e:
                    self._log(f"⚠️ 装裱跳过: {e}")

            # 7. 水印
            if params["use_watermark"]:
                try:
                    from services.watermark import WatermarkProcessor
                    wp = WatermarkProcessor(seed=seed)
                    image = wp.add_subtle_watermark(
                        image, text=ARTIST_NAME,
                        opacity=30, font_size=40,
                        angle=-30,
                        spacing_x=180, spacing_y=180,
                    )
                    if image.mode != "RGBA":
                        image = image.convert("RGBA")
                    self._log(f"✅ 水印")
                except Exception as e:
                    self._log(f"⚠️ 水印跳过: {e}")

            # 8. 保存
            out_dir = PROJECT_ROOT / "output" / category
            out_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            out_path = out_dir / f"{preset}_{ts}.png"
            image.convert("RGB").save(out_path, quality=95)
            self._log(f"✅ 保存: {out_path}")

            # 回主线程更新 UI
            self.root.after(0, self._on_generate_done, str(out_path))

        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            self.root.after(0, self._on_generate_error, str(e), tb)

    def _on_generate_done(self, path: str):
        """生成成功，回主线程刷新 UI"""
        self._log("=" * 60)
        self._log("✅ 全部完成")
        self._log("=" * 60)
        self._show_image(path)
        self._current_image_path = path
        self._set_status(f"✅ 完成: {Path(path).name}")
        self.btn_generate.config(state=NORMAL, text="🚀 一键生成")

    def _on_generate_error(self, err: str, tb: str):
        """生成失败"""
        self._log(f"\n❌ 失败: {err}")
        self._log(tb)
        self._set_status(f"❌ 失败: {err[:60]}")
        self.btn_generate.config(state=NORMAL, text="🚀 一键生成")
        messagebox.showerror("生成失败", err)

    # ============================================================
    # 工具
    # ============================================================

    def _set_status(self, text: str):
        self.status_var.set(text)

    def _log(self, text: str):
        """线程安全写日志"""
        def _do():
            self.text_log.insert(END, text + "\n")
            self.text_log.see(END)
        self.root.after(0, _do)

    def _show_image(self, path: str):
        """在画布上显示图片（自适应大小）"""
        if not PIL_OK:
            self._set_status("⚠️ 未安装 Pillow，无法预览")
            return
        try:
            img = Image.open(path)
            # 画布尺寸
            self.canvas.update_idletasks()
            cw = self.canvas.winfo_width() or 600
            ch = self.canvas.winfo_height() or 600
            iw, ih = img.size
            scale = min(cw / iw, ch / ih, 1.0)
            new_size = (int(iw * scale), int(ih * scale))
            img_resized = img.resize(new_size, Image.Resampling.LANCZOS)
            self._preview_img = ImageTk.PhotoImage(img_resized)

            self.canvas.delete("all")
            self.canvas.create_image(
                cw // 2, ch // 2,
                image=self._preview_img,
                anchor="center",
            )
        except Exception as e:
            self._set_status(f"⚠️ 预览失败: {e}")


# ============================================================
# 入口
# ============================================================
def main():
    root = Tk()
    try:
        # 尝试用 Windows 高 DPI 缩放
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = ArtForgeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()