# skills/artforge_daily/skill.py
"""
ArtForge 日更号 —— 智能调度版
流程：
1. 智能选择分类与预设（支持周计划、防重复、权重控制）
2. 用 ArtForge 6 层预设出图
3. 做旧 → 题词 → 印章 → 装裱 → 水印
4. image_curator 鉴赏写文章
5. wechat_formatter 排版
6. 推公众号草稿（图文）
7. 推公众号贴图（图片消息）
8. 图片合成视频，推视频号
"""
from __future__ import annotations

import argparse
import json
import logging
import random
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from dotenv import load_dotenv
    env_file = PROJECT_ROOT / ".env"
    load_dotenv(env_file if env_file.exists() else None)
except ImportError:
    pass

logger = logging.getLogger(__name__)

# ============================================================
# 🎯 智能调度配置（可根据你的公众号定位自行修改）
# ============================================================
PRESETS_DIR = PROJECT_ROOT / "presets"
HISTORY_FILE = PROJECT_ROOT / "output" / "daily_history.json"
AVOID_RECENT_DAYS = 7  # 默认防重复天数

# 1. 绝对黑名单（发了封号，或不符合东方艺术定位的）
DAILY_BLACKLIST = {
    "art_nude", "art_nude_explicit", "art_nude_modern", "art_nude_oriental",
    "war", "beast", "mythical", "astrology", "medicine"
}

# 2. 优质分类白名单 & 权重（数字越大，被抽中的概率越高）
DAILY_CATEGORY_POOL = {
    # 核心主打（权重高）
    "tang": 4, "japanese": 4, "gufeng": 4, "genji": 3, "yokai": 3,
    "yokai_legend": 3, "yokai_animals": 2, "yokai_ghost": 2, "yokai_tsukumogami": 2,
    # 垂直细分（权重中）
    "landscape": 3, "mountain": 2, "water": 2, "tree": 2, "flower": 2, 
    "bird": 2, "season": 2, "festival": 2, "tea_ceremony": 2, "calligraphy": 2,
    "costume": 2, "opera": 2, "pattern": 2, "furniture": 2, "architecture": 2,
    # 趣味点缀（权重低）
    "cat": 1, "dog": 1, "fish": 1, "insect": 1, "fruit": 1, "vegetable": 1,
    "music": 1, "musician": 1, "dance": 1, "figure": 1, "object": 1, "vehicle": 1,
    "weapon": 1, "weather": 1, "region": 1, "dynasty": 1, "buddhism": 1, 
    "incense": 1, "flower_arrangement": 1, "literati_gathering": 1, "folklore": 1,
    "modern": 1
}

# 3. 主题周计划映射（0=周一, 6=周日）
WEEKLY_THEME_SCHEDULE = {
    0: ["tang", "genji", "dynasty"],                  # 周一：大唐气象 / 源氏 / 朝代
    1: ["japanese", "yokai", "yokai_legend"],         # 周二：浮世绘 / 妖怪
    2: ["gufeng", "landscape", "mountain"],           # 周三：古风 / 山水
    3: ["flower", "bird", "cat", "insect"],           # 周四：花鸟 / 萌宠 (轻松一点)
    4: ["yokai_animals", "yokai_ghost", "yokai_tsukumogami", "folklore"], # 周五：妖怪民俗
    5: ["season", "festival", "weather"],             # 周六：四季 / 节日
    6: ["calligraphy", "tea_ceremony", "incense", "literati_gathering"]   # 周日：静心雅集
}


# ============================================================
# 自动发现预设
# ============================================================
def list_categories() -> List[str]:
    """扫描 presets/ 下所有含 .py 的分类"""
    if not PRESETS_DIR.exists():
        return []
    cats = []
    for d in sorted(PRESETS_DIR.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        py_files = [f for f in d.glob("*.py")
                    if f.stem not in ("__init__", "__pycache__")]
        if py_files:
            cats.append(d.name)
    return cats

def list_presets(category: str) -> List[str]:
    """列出某分类下的所有预设名"""
    d = PRESETS_DIR / category
    if not d.exists():
        return []
    return sorted(
        f.stem for f in d.glob("*.py")
        if f.stem not in ("__init__",)
    )

def pick_default_presets(category: str, count: int = 3) -> List[str]:
    """用户没指定 presets 时，从分类下随机挑 count 个"""
    all_presets = list_presets(category)
    if not all_presets:
        return []
    if len(all_presets) <= count:
        return all_presets
    return random.sample(all_presets, count)


# ============================================================
# 🧠 智能调度核心逻辑
# ============================================================
def _load_history() -> list:
    """加载历史记录"""
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

def _save_history(history: list):
    """保存历史记录（只保留最近 30 条）"""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(
        json.dumps(history[-30:], ensure_ascii=False, indent=2), 
        encoding="utf-8"
    )

def smart_pick_category(week_plan: bool = False, avoid_days: int = AVOID_RECENT_DAYS) -> str:
    """
    智能选择分类：
    1. 如果开启周计划，根据星期几限定主题池
    2. 过滤黑名单
    3. 过滤最近 N 天用过的分类（防重复）
    4. 按权重随机抽取
    """
    all_cats = list_categories()
    history = _load_history()
    recent_cats = set([h["category"] for h in history[-avoid_days:]])
    
    # 确定候选池
    if week_plan:
        weekday = datetime.now().weekday()
        base_pool = WEEKLY_THEME_SCHEDULE.get(weekday, list(DAILY_CATEGORY_POOL.keys()))
    else:
        base_pool = list(DAILY_CATEGORY_POOL.keys())
        
    # 构建有效池（过滤黑名单、不存在、近期重复）
    valid_pool = {}
    for cat in base_pool:
        if cat in DAILY_BLACKLIST:
            continue
        if cat not in all_cats:
            continue
        if cat in recent_cats:
            continue
        weight = DAILY_CATEGORY_POOL.get(cat, 1)
        valid_pool[cat] = weight
        
    # 如果过滤太狠导致没得选，放宽“防重复”限制
    if not valid_pool:
        logger.warning("⚠️ 防重复过滤过严，放宽限制...")
        for cat in base_pool:
            if cat in DAILY_BLACKLIST or cat not in all_cats:
                continue
            valid_pool[cat] = DAILY_CATEGORY_POOL.get(cat, 1)
            
    # 兜底：如果白名单里全被删了，从所有非黑名单里随机
    if not valid_pool:
        logger.warning("⚠️ 白名单无可用分类，回退到全量非黑名单...")
        valid_pool = {c: 1 for c in all_cats if c not in DAILY_BLACKLIST}

    categories = list(valid_pool.keys())
    weights = list(valid_pool.values())
    
    chosen = random.choices(categories, weights=weights, k=1)[0]
    logger.info(f"🎯 智能选中分类: {chosen} (权重: {valid_pool[chosen]})")
    return chosen

def smart_pick_presets(category: str, count: int = 3) -> list:
    """从指定分类中随机挑选预设，如果该分类预设不足，则全部返回"""
    presets = list_presets(category)
    if not presets:
        return []
    if len(presets) <= count:
        return presets
    return random.sample(presets, count)


# ============================================================
# 主类
# ============================================================
class ArtForgeDaily:
    name = "artforge_daily"
    version = "2.0.0"  # 升级版本号

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._setup_logging()

    def _setup_logging(self):
        level = self.config.get("log_level", "INFO")
        logging.basicConfig(
            level=getattr(logging, level.upper()),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    # ---------- 步骤 1：生成图片 ----------
    def generate_images(
        self, category: str, presets: List[str], count: int, engine: str,
        composition: str, seed: Optional[int], seal_scheme: str, language: str,
        use_aging: bool = True, use_inscription: bool = True, use_seal: bool = True,
        use_scroll: bool = True, use_watermark: bool = True,
    ) -> Path:
        from core.prompt_builder import PromptBuilder
        from core.safety import check_safety
        from api_engines import create_engine
        from compose_artwork import (
            InscriptionRenderer, pick_size, theme_from_preset,
            load_config, ARTIST_NAME,
        )

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = PROJECT_ROOT / "output" / "daily" / f"{ts}_images"
        out_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"输出目录: {out_dir}")

        builder = PromptBuilder()
        engine_obj = create_engine(engine, load_config())
        comp_map = {
            "vertical":   "vertical hanging scroll, kakemono",
            "horizontal": "horizontal handscroll, emaki",
            "byobu":      "folding screen, byobu, multi-panel",
            "fan":        "round fan, circular composition",
            "album":      "square album leaf",
        }

        total = len(presets) * count
        idx = 0
        produced: List[Path] = []
        failed: List[str] = []

        for preset in presets:
            for i in range(count):
                idx += 1
                tag = f"{preset}_{i+1:02d}"
                logger.info(f"[{idx}/{total}] 生成 {tag}")
                try:
                    prompt, detail = builder.compose_preset(
                        preset, category=category, return_detail=True)
                    theme = theme_from_preset(preset, category)
                    detail["composition"] = comp_map.get(composition, comp_map["vertical"])
                    detail.pop("inscription", None)
                    full_prompt = ", ".join(
                        detail[k] for k in builder.LAYER_ORDER if detail.get(k))
                    negative = builder.get_negative() + (
                        ", calligraphy, text, chinese characters, japanese text, "
                        "kanji, kana, seal, stamp, signature, inscription, "
                        "poem text, red seal, watermark, logo, letters, words")

                    is_safe, reason = check_safety(
                        full_prompt, detail.get("style", ""), detail.get("subject", ""))
                    if not is_safe:
                        logger.warning(f"{tag} 安全检查未过: {reason}")
                        failed.append(tag)
                        continue

                    width, height = pick_size(detail)
                    image = engine_obj.generate_single(
                        prompt=full_prompt, negative=negative,
                        width=width, height=height, seed=seed)
                    if image.mode != "RGBA":
                        image = image.convert("RGBA")

                    # 做旧
                    if use_aging:
                        try:
                            from services.aging_processor import AgingProcessor
                            image = AgingProcessor(seed=seed).apply(
                                image.convert("RGB"), texture="xuan_paper", strength=0.55
                            ).convert("RGBA")
                        except Exception as e:
                            logger.warning(f"做旧失败: {e}")

                    # 题词
                    if use_inscription:
                        try:
                            from services.inscription_generator import InscriptionGenerator
                            ig = InscriptionGenerator(seed=seed)
                            lang = None if language == "auto" else language
                            inscription_text, _ = ig.generate(
                                theme=theme, format="auto", return_meta=True,
                                backend=engine if engine in ("agnes", "pollinations") else "auto",
                                category=category, language=lang)
                            renderer = InscriptionRenderer()
                            fs = max(24, int(min(width, height) * 0.045))
                            image = renderer.render(
                                image, inscription_text, font_size=fs,
                                color=(45, 40, 35), position="top_right",
                                margin=int(min(width, height) * 0.055), max_chars_per_col=8)
                        except Exception as e:
                            logger.warning(f"题词失败: {e}")

                    # 印章
                    if use_seal:
                        try:
                            from services.seal_generator import SealGenerator
                            image = SealGenerator().apply_scheme(
                                image, ARTIST_NAME, scheme=seal_scheme, margin_ratio=0.05)
                        except Exception as e:
                            logger.warning(f"印章失败: {e}")

                    # 装裱
                    if use_scroll:
                        try:
                            from services.scroll_composer import ScrollComposer
                            image = ScrollComposer(seed=seed).compose(
                                image.convert("RGB"), composition=composition).convert("RGBA")
                        except Exception as e:
                            logger.warning(f"装裱失败: {e}")

                    # 水印
                    if use_watermark:
                        try:
                            from services.watermark import WatermarkProcessor
                            image = WatermarkProcessor(seed=seed).add_subtle_watermark(
                                image, text=ARTIST_NAME, opacity=30, font_size=40,
                                angle=-30, spacing_x=180, spacing_y=180)
                            if image.mode != "RGBA":
                                image = image.convert("RGBA")
                        except Exception as e:
                            logger.warning(f"水印失败: {e}")

                    out_path = out_dir / f"{preset}_{i+1:02d}.png"
                    image.convert("RGB").save(out_path, quality=95)
                    produced.append(out_path)
                    logger.info(f"  → {out_path.name}")

                    if idx < total:
                        time.sleep(1.5)

                except Exception as e:
                    logger.error(f"{tag} 失败: {e}")
                    traceback.print_exc()
                    failed.append(tag)

        logger.info(f"生成完成: {len(produced)} 成功 / {len(failed)} 失败")
        return out_dir

    # ---------- 步骤 2：鉴赏 ----------
    def curate(self, image_dir: Path, title: Optional[str] = None) -> Optional[Path]:
        from skills.image_curator import ImageCurator
        if not title:
            title = f"东方艺术 · {datetime.now().strftime('%Y-%m-%d')}"
        curator = ImageCurator({
            "generate_html": True, "generate_docx": True,
            "generate_pdf": True, "generate_clipboard": True,
        })
        r = curator.curate(str(image_dir), title=title)
        if r.get("status") != "success":
            logger.error(f"鉴赏失败: {r.get('error')}")
            return None
        return Path(r["result"]["article_path"])

    # ---------- 步骤 3：排版 ----------
    def format(self, md_path: Path, theme: str, footer_image: Optional[str] = None) -> Optional[Path]:
        from skills.wechat_formatter import WechatFormatter
        fmt = WechatFormatter()
        kwargs = {"theme": theme, "open": False}
        if footer_image:
            fp = Path(footer_image)
            if not fp.is_absolute():
                fp = PROJECT_ROOT / fp
            if fp.exists():
                kwargs["footer_image"] = str(fp)
                kwargs["footer_alt"] = "关注"
        r = fmt.format(str(md_path), **kwargs)
        if r.get("status") != "success":
            logger.error(f"排版失败: {r.get('error')}")
            return None
        return Path(r["result"]["article_dir"])

    # ---------- 步骤 4：推文章草稿 ----------
    def push_article(self, article_dir: Path, dry_run: bool = False) -> Dict:
        from skills.wechat_formatter import WechatFormatter
        fmt = WechatFormatter()
        r = fmt.publish(str(article_dir), dry_run=dry_run)
        return {"ok": r.get("status") == "success", "error": r.get("error")}

    # ---------- 步骤 5：推贴图 ----------
    def push_newspic(self, image_dir: Path, title: str, content: str = "") -> Dict:
        try:
            from skills.wechat_formatter.publisher import wechat_publish as wp
            imgs = sorted([
                p for p in image_dir.iterdir()
                if p.suffix.lower() in (".png", ".jpg", ".jpeg")
            ])[:20]
            if not imgs:
                return {"ok": False, "error": "目录里没有图片"}
            token = wp.get_access_token()
            media_ids = wp.upload_images_as_material(token, [str(p) for p in imgs])
            if not media_ids:
                return {"ok": False, "error": "所有图片上传失败"}
            media_id = wp.push_draft(
                token, title=title[:20], content=content[:1000] or title[:20],
                article_type="newspic", image_media_ids=media_ids)
            return {"ok": bool(media_id), "media_id": media_id}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _generate_bgm(self, category: str, duration: int = 24) -> Optional[Path]:
        """根据分类自动生成匹配的背景音乐"""
        try:
            # 分类 → 情绪映射
            EMOTION_MAP = {
                "tang": "epic", "genji": "epic", "dynasty": "epic",
                "japanese": "mysterious", "yokai": "mysterious", 
                "yokai_legend": "mysterious", "yokai_animals": "mysterious",
                "gufeng": "peaceful", "landscape": "peaceful", "mountain": "peaceful",
                "water": "peaceful", "tree": "peaceful", "flower": "joyful",
                "bird": "joyful", "cat": "joyful", "dog": "joyful",
                "fish": "joyful", "insect": "joyful",
                "tea_ceremony": "melancholic", "calligraphy": "melancholic",
                "incense": "melancholic", "literati_gathering": "melancholic",
                "season": "peaceful", "festival": "joyful", "weather": "peaceful",
                "buddhism": "peaceful", "folklore": "mysterious",
            }
            
            # 分类 → 编曲风格映射
            ARRANGEMENT_MAP = {
                "tang": "chinese", "genji": "chamber", "dynasty": "chinese",
                "japanese": "baroque", "yokai": "epic",
                "gufeng": "chinese", "landscape": "new_age", "mountain": "new_age",
                "flower": "folk", "bird": "folk", "cat": "folk",
                "tea_ceremony": "chamber", "calligraphy": "chamber",
                "season": "new_age", "festival": "folk",
            }
            
            emotion = EMOTION_MAP.get(category, "peaceful")
            arrangement = ARRANGEMENT_MAP.get(category, "new_age")
            
            logger.info(f"🎵 自动生成 BGM: 情绪={emotion}, 编曲={arrangement}, 时长={duration}s")
            
            # 调用 music_generator
            from skills.music_generator.music_generator_cli import MusicGenerator
            gen = MusicGenerator()
            result = gen.create_music(
                topic=f"东方艺术 {category}",
                emotion=emotion,
                duration=duration,
            )
            
            if result["status"] == "success":
                bgm_path = Path(result["audio_file"])
                logger.info(f"✅ BGM 已生成: {bgm_path.name}")
                return bgm_path
            else:
                logger.warning(f"⚠️ BGM 生成失败: {result.get('message')}")
                return None
                
        except Exception as e:
            logger.warning(f"⚠️ 自动生成 BGM 异常: {e}")
            return None
            
    # ---------- 步骤 6：合成视频 + 推视频号 ----------
    def build_video(self, image_dir: Path, title: str, per_image: float = 4.0,
                    size: str = "1080x1920", bgm: Optional[Path] = None) -> Optional[Path]:
        import shutil
        import subprocess
        import random

        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            logger.error("未找到 ffmpeg")
            return None
            
        imgs = sorted([
            p for p in image_dir.iterdir()
            if p.suffix.lower() in (".png", ".jpg", ".jpeg")
        ])
        if not imgs:
            return None

        #  智能音乐选择逻辑（解决冲突 + 无声问题）
        final_bgm = None
        
        # 1. 优先使用手动指定的 bgm
        if bgm and Path(bgm).exists():
            final_bgm = Path(bgm)
            logger.info(f"🎵 使用指定背景音乐: {final_bgm.name}")
        else:
            # 2. 兜底：从 assets/music 随机选一个 MP3
            music_dir = PROJECT_ROOT / "assets" / "music"
            if music_dir.exists():
                mp3_files = list(music_dir.glob("*.mp3"))
                if mp3_files:
                    final_bgm = random.choice(mp3_files)
                    logger.info(f" 随机选择背景音乐: {final_bgm.name}")

        W, H = map(int, size.split("x"))
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe = "".join(c for c in title[:20] if c.isalnum() or c in " _-").strip() or "video"
        out = PROJECT_ROOT / "output" / "videos" / f"{ts}_{safe}.mp4"
        out.parent.mkdir(parents=True, exist_ok=True)
        
        import tempfile
        work = Path(tempfile.mkdtemp(prefix="af_video_"))
        
        try:
            segs = []
            for i, img in enumerate(imgs):
                seg = work / f"seg_{i:03d}.mp4"
                vf = (
                    f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
                    f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,"
                    f"setsar=1,format=yuv420p")
                subprocess.run([
                    ffmpeg, "-y", "-loop", "1", "-t", str(per_image), "-i", str(img),
                    "-vf", vf, "-r", "30", "-c:v", "libx264", "-preset", "medium",
                    "-crf", "20", "-pix_fmt", "yuv420p", str(seg),
                ], capture_output=True, check=True)
                segs.append(seg)
                
            concat = work / "concat.txt"
            concat.write_text("\n".join(f"file '{s.as_posix()}'" for s in segs), encoding="utf-8")
            merged = work / "merged.mp4"
            subprocess.run([
                ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
                "-c", "copy", str(merged),
            ], capture_output=True, check=True)
            
            # 🎵 混入音乐
            if final_bgm and final_bgm.exists():
                subprocess.run([
                    ffmpeg, "-y", "-i", str(merged), "-stream_loop", "-1", "-i", str(final_bgm),
                    "-shortest",  # 关键：以最短的流（视频）为准，自动截断长音乐
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", str(out),
                ], capture_output=True, check=True)
                logger.info(f"✅ 视频已添加音乐: {final_bgm.name}")
            else:
                shutil.copy2(merged, out)
                logger.warning("⚠️ 未找到背景音乐，视频无声")
                
            return out
        finally:
            shutil.rmtree(work, ignore_errors=True)
            
    def push_video(self, video_path: Path, title: str, desc: str = "",
                   cover: Optional[Path] = None, account: str = "test") -> Dict:
        try:
            from skills.social_auto_upload import SocialAutoUpload
            pub = SocialAutoUpload()
            r = pub.publish_video(
                platform="tencent", file=str(video_path), title=title, desc=desc, tags=[],
                account=account, thumbnail=str(cover) if cover and cover.exists() else None)
            return {"ok": r.get("status") == "success", "error": r.get("error")}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ---------- 主流程 ----------
    def execute(self, **kwargs) -> Dict[str, Any]:
        start = time.time()
        logger.info(f"执行 {self.name} v{self.version}")

        category = kwargs.get("category")
        presets = kwargs.get("presets")
        count = int(kwargs.get("count", 2))
        
        # 智能调度参数
        use_smart = kwargs.get("smart", False)
        week_plan = kwargs.get("week_plan", False)
        avoid_days = int(kwargs.get("avoid_days", AVOID_RECENT_DAYS))

        # 1) 智能选择分类
        if use_smart and not category:
            category = smart_pick_category(week_plan=week_plan, avoid_days=avoid_days)
        elif not category:
            all_cats = list_categories()
            safe_cats = [c for c in all_cats if c not in DAILY_BLACKLIST]
            if not safe_cats:
                return {"status": "error", "error": "没有可用的安全分类"}
            category = random.choice(safe_cats)
            logger.info(f"未指定分类，随机选中: {category}")

        # 2) 智能选择预设
        if use_smart and not presets:
            all_presets = list_presets(category)
            if not all_presets:
                return {"status": "error", "error": f"分类 {category} 下没有预设"}
            
            # 随机挑选 count 个预设（如果分类下预设不足，则全选）
            num_to_pick = min(count, len(all_presets))
            presets = random.sample(all_presets, num_to_pick)
            
            # 既然每个预设只生成 1 张，就把 count 设为 1
            count = 1
            logger.info(f"🎲 智能选中 {len(presets)} 个预设，每个生成 1 张: {presets}")
        elif not presets:
            presets = pick_default_presets(category, count=count)
            if not presets:
                return {"status": "error", "error": f"分类 {category} 下没有预设"}
            logger.info(f"未指定预设，随机选中: {presets}")

        engine = kwargs.get("engine", "pollinations")
        composition = kwargs.get("composition", "vertical")
        theme = kwargs.get("theme", "newspaper")
        seed = kwargs.get("seed")
        seal_scheme = kwargs.get("seal_scheme", "contrast")
        language = kwargs.get("language", "auto")
        push_article = kwargs.get("push_article", True)
        push_newspic_flag = kwargs.get("push_newspic", True)
        push_video_flag = kwargs.get("push_video", True)
        dry_run = kwargs.get("dry_run", False)
        footer_image = kwargs.get("footer_image")
        bgm = kwargs.get("bgm")
        video_account = kwargs.get("video_account", "test")
        title = kwargs.get("title")

        result: Dict[str, Any] = {
            "image_dir": None, "md_path": None, "article_dir": None,
            "video_path": None, "push_article": None, "push_newspic": None, "push_video": None,
        }

        try:
            # 1. 生成
            image_dir = self.generate_images(
                category=category, presets=presets, count=count, engine=engine,
                composition=composition, seed=seed, seal_scheme=seal_scheme, language=language)
            result["image_dir"] = str(image_dir)
            if not list(image_dir.glob("*.png")):
                return {"status": "error", "error": "没有生成任何图片"}

            # 2. 鉴赏（先不传 title，让它自动生成 intro）
            md = self.curate(image_dir, title=None)  # ← 改成 None
            if not md:
                return {"status": "error", "error": "鉴赏失败", "result": result}
            result["md_path"] = str(md)
            
            # 2.5 🌟 智能生成标题
            smart_title = self._generate_smart_title(md, category, presets)
            if smart_title:
                # ✅ 关键：更新路径！
                md = self._update_article_title(md, smart_title)
                result["md_path"] = str(md)  # 同步更新 result 里的路径
                logger.info(f"🎯 智能标题: {smart_title}")
                effective_title = smart_title
            else:
                effective_title = f"{category.replace('_', ' ').title()} · {datetime.now().strftime('%Y-%m-%d')}"
            

            # 3. 排版
            art_dir = self.format(md, theme, footer_image=footer_image)
            if not art_dir:
                return {"status": "error", "error": "排版失败", "result": result}
            result["article_dir"] = str(art_dir)

            # 4. 推文章
            if push_article:
                result["push_article"] = self.push_article(art_dir, dry_run)

            # 5. 推贴图
            if push_newspic_flag:
                np_title = (title or f"{category} · {datetime.now().strftime('%m-%d')}")[:20]

                # 🌟 新增：读取鉴赏文章的 intro 作为贴图内容
                np_content = ""
                if md and md.parent.exists():
                    meta_file = md.parent / "metadata.json"
                    if meta_file.exists():
                        try:
                            import json
                            meta = json.loads(meta_file.read_text(encoding="utf-8"))
                            np_content = meta.get("intro", "")[:200] # 取前200字
                        except:
                            pass
                
                # 如果没读到 intro，就用分类名兜底
                if not np_content:              
                    np_content = f"东方艺术 · {category} 主题鉴赏"

                # 传入 content 参数
                result["push_newspic"] = self.push_newspic(image_dir, np_title, content=np_content)


            # 6. 视频
            if push_video_flag:
                v_title = (title or f"东方艺术 · {category}")[:20]
                bgm_path = Path(bgm) if bgm else None
                if bgm_path and not bgm_path.is_absolute():
                    bgm_path = PROJECT_ROOT / bgm_path
                
                # 🎵 传入 category 让 build_video 能自动生成 BGM
                video = self.build_video(
                    image_dir, v_title, 
                    per_image=4.0,  # 每张 4 秒
                    bgm=bgm_path,                    
                )
                
                if video:
                    result["video_path"] = str(video)
                    cover = next(image_dir.glob("*.png"), None)
                    result["push_video"] = self.push_video(
                        video, v_title, desc=v_title, 
                        cover=cover, account=video_account)

            # 7. 记录历史（用于防重复）
            if use_smart:
                try:
                    history = _load_history()
                    history.append({
                        "category": category,
                        "presets": presets,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                    _save_history(history)
                except Exception as e:
                    logger.warning(f"保存历史记录失败: {e}")

            return {
                "status": "success",
                "result": result,
                "metadata": {
                    "skill": self.name, "version": self.version,
                    "elapsed": f"{time.time() - start:.1f}s",
                },
            }
        except Exception as e:
            logger.error(f"执行失败: {e}")
            traceback.print_exc()
            return {"status": "error", "error": str(e), "result": result}


    def _generate_smart_title(self, md_path: Path, category: str, presets: list) -> Optional[str]:
        """根据鉴赏内容智能生成标题"""
        try:
            # 读取 metadata
            article_dir = md_path.parent
            metadata_file = article_dir / "metadata.json"
            if not metadata_file.exists():
                return None
            
            metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
            intro = metadata.get("intro", "")
            title = metadata.get("title", "")
            
            if not intro:
                return None
            
            # 用 LLM 生成标题
            from api_engines import create_engine
            from config.settings import settings
            
            engine = create_engine("agnes", {
                "AGNES_API_KEY": settings.agnes_api_key,
                "AGNES_BASE_URL": settings.agnes_base_url,
                "AGNES_TEXT_MODEL": settings.agnes_text_model or "agnes-2.5-flash",
            })
            
            prompt = f"""你是一位资深的艺术编辑，请根据以下鉴赏文章的引言，生成一个诗意且贴切的标题。

要求：
1. 标题长度：8-15 个字
2. 风格：优雅、含蓄、有东方韵味
3. 可以包含意象（如：月、风、花、云、山、水等）
4. 不要直接重复引言内容，要提炼升华
5. 只输出标题，不要任何解释

分类：{category}
预设：{', '.join(presets)}
引言：{intro}

请生成标题："""
            
            result = engine.chat_simple(prompt)
            smart_title = result.strip()
            
            # 清理：去掉可能的引号、换行
            smart_title = smart_title.strip('"').strip("'").strip("「」").strip()
            
            # 验证长度
            if 4 <= len(smart_title) <= 20:
                return smart_title
            else:
                logger.warning(f"⚠️ 生成的标题长度不合适: {smart_title}")
                return None
                
        except Exception as e:
            logger.warning(f"⚠️ 智能标题生成失败: {e}")
            return None
    
    def _update_article_title(self, md_path: Path, new_title: str):
        """更新文章标题（metadata + markdown + html）"""
        try:
            article_dir = md_path.parent
            metadata_file = article_dir / "metadata.json"
            
            # 1. 更新 metadata
            if metadata_file.exists():
                metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
                metadata["title"] = new_title
                metadata_file.write_text(
                    json.dumps(metadata, ensure_ascii=False, indent=2),
                    encoding="utf-8"
                )
            
            # 2. 更新 markdown
            if md_path.exists():
                content = md_path.read_text(encoding="utf-8")
                # 替换第一行标题（# 开头的）
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if line.startswith("# "):
                        lines[i] = f"# {new_title}"
                        break
                md_path.write_text("\n".join(lines), encoding="utf-8")
            
            # 3. 更新 html（如果存在）
            html_path = article_dir / "article.html"
            if html_path.exists():
                content = html_path.read_text(encoding="utf-8")
                # 替换 <title> 和 <h1>
                import re
                content = re.sub(r'<title>.*?</title>', f'<title>{new_title}</title>', content)
                content = re.sub(r'<h1>.*?</h1>', f'<h1>{new_title}</h1>', content)
                html_path.write_text(content, encoding="utf-8")
            
            # 4. 重命名目录（可选）
            # 当前目录名格式：20260927_154830_东方艺术  2026-09-27
            # 改成：20260927_154830_新标题
            old_name = article_dir.name
            parts = old_name.split("_", 2)
            if len(parts) >= 3:
                new_name = f"{parts[0]}_{parts[1]}_{new_title}"
                new_path = article_dir.parent / new_name
                if not new_path.exists():
                    article_dir.rename(new_path)
                    # 更新 result 里的路径
                    logger.info(f"📁 目录已重命名: {old_name} → {new_name}")
                    return new_path / "article.md"  # ✅ 返回新路径
                    
        except Exception as e:
            logger.warning(f"⚠️ 更新标题失败: {e}")
        return md_path  # ✅ 兜底返回原路径            
            
# ============================================================
# CLI
# ============================================================
def _cli():
    ap = argparse.ArgumentParser(
        description="ArtForge 日更号（智能调度版）")
    
    # 基础参数
    ap.add_argument("--category", default=None, help="分类，不指定则智能随机")
    ap.add_argument("--presets", nargs="*", default=None, help="预设名，不指定则智能随机")
    ap.add_argument("--count", type=int, default=2)
    ap.add_argument("--engine", default="agnes", choices=["pollinations", "agnes", "siliconflow"])
    ap.add_argument("--composition", default="vertical", choices=["vertical", "horizontal", "byobu", "fan", "album"])
    ap.add_argument("--theme", default="newspaper")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--seal-scheme", default="contrast")
    ap.add_argument("--language", default="auto")
    
    # 🧠 智能调度高级参数
    ap.add_argument("--smart", action="store_true", 
                    help="启用智能调度（白名单+权重+防重复）")
    ap.add_argument("--week-plan", action="store_true", 
                    help="启用主题周计划（需配合 --smart，按星期几决定主题）")
    ap.add_argument("--avoid-days", type=int, default=AVOID_RECENT_DAYS,
                    help=f"防重复天数，最近 N 天不重复同一分类（默认 {AVOID_RECENT_DAYS}）")
    
    # 推送控制
    ap.add_argument("--no-article", action="store_true")
    ap.add_argument("--no-newspic", action="store_true")
    ap.add_argument("--no-video", action="store_true")
    ap.add_argument("--footer-image", default=None)
    ap.add_argument("--bgm", default=None)
    ap.add_argument("--video-account", default="test")
    ap.add_argument("--title", default=None)
    ap.add_argument("--dry-run", action="store_true")
    
    # 辅助命令
    ap.add_argument("--list-categories", action="store_true", help="列出所有分类后退出")
    ap.add_argument("--list-presets", metavar="CATEGORY", default=None, help="列出某分类下的所有预设后退出")
    ap.add_argument("--show-history", action="store_true", help="查看最近 7 天的日更历史")

    args = ap.parse_args()

    # ---- 辅助命令：列出分类 ----
    if args.list_categories:
        cats = list_categories()
        if not cats:
            print("presets/ 下没有任何分类")
            return
        print(f"\n共 {len(cats)} 个分类:")
        for c in cats:
            n = len(list_presets(c))
            mark = "🚫" if c in DAILY_BLACKLIST else f"⚖️{x}" if c in DAILY_CATEGORY_POOL else ""
            weight = DAILY_CATEGORY_POOL.get(c, "")
            print(f"  {c:22s} ({n:2d} 个预设) {mark}{weight}")
        return

    # ---- 辅助命令：列出某分类下的预设 ----
    if args.list_presets:
        presets = list_presets(args.list_presets)
        if not presets:
            print(f"分类 {args.list_presets} 不存在或为空")
            return
        print(f"\n{args.list_presets} 下的 {len(presets)} 个预设:")
        for p in presets:
            print(f"  {p}")
        return
        
    # ---- 辅助命令：查看历史 ----
    if args.show_history:
        history = _load_history()
        if not history:
            print("暂无日更历史记录")
            return
        print(f"\n最近 {len(history)} 条日更记录:")
        for h in history[-7:]:
            print(f"  [{h['date']}] 分类: {h['category']} | 预设: {h['presets']}")
        return

    # ---- 正常流程 ----
    pipe = ArtForgeDaily()
    r = pipe.execute(
        category=args.category, presets=args.presets, count=args.count,
        engine=args.engine, composition=args.composition, theme=args.theme,
        seed=args.seed, seal_scheme=args.seal_scheme, language=args.language,
        push_article=not args.no_article,
        push_newspic=not args.no_newspic,
        push_video=not args.no_video,
        footer_image=args.footer_image, bgm=args.bgm,
        video_account=args.video_account, title=args.title,
        dry_run=args.dry_run,
        smart=args.smart, week_plan=args.week_plan, avoid_days=args.avoid_days,
    )

    if r["status"] == "success":
        print("\n" + "=" * 72)
        print("  ✅ ArtForge 日更完成")
        print("=" * 72)
        for k, v in r["result"].items():
            print(f"  {k}: {v}")
    else:
        print(f"\n❌ {r.get('error')}")
        sys.exit(1)

if __name__ == "__main__":
    _cli()