
# skills/wechat_rss_liker/skill.py
"""
微信公众号 RSS 自动访问与点赞技能
原理：通过 feedparser 解析 RSS 获取最新链接，通过 Playwright 模拟真人访问并尝试点赞。
"""
import time
import random
import logging
import feedparser
from datetime import datetime, timedelta
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

logger = logging.getLogger(__name__)

class WechatRssLiker:
    def __init__(self, rss_urls: list, mode: str = "visit", max_age_hours: int = 24):
        """
        :param rss_urls: RSS 订阅链接列表 (例如来自 RSSHub 的微信订阅)
        :param mode: "visit" (仅访问滚动，刷活跃度) 或 "like" (尝试点击赞/在看)
        :param max_age_hours: 只处理最近 N 小时内发布的文章
        """
        self.rss_urls = rss_urls
        self.mode = mode
        self.max_age_hours = max_age_hours
        self.processed_links = set()  # 内存去重，防止重复处理

    def _fetch_new_articles(self) -> list:
        """从 RSS 获取最新文章"""
        articles = []
        cutoff_time = datetime.now() - timedelta(hours=self.max_age_hours)
        
        for url in self.rss_urls:
            try:
                logger.info(f"📡 正在解析 RSS: {url}")
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    # 尝试解析发布时间
                    pub_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    
                    # 如果没有时间或时间在限制范围内，则加入候选
                    if pub_date is None or pub_date > cutoff_time:
                        link = entry.get('link', '')
                        if link and link not in self.processed_links and "mp.weixin.qq.com" in link:
                            articles.append({
                                "title": entry.get('title', '无标题'),
                                "link": link,
                                "pub_date": pub_date
                            })
                            self.processed_links.add(link)
            except Exception as e:
                logger.warning(f"⚠️ 解析 RSS 失败 {url}: {e}")
                
        # 按时间倒序排列，最新的在前
        articles.sort(key=lambda x: x["pub_date"] or datetime.min, reverse=True)
        return articles

    def _simulate_human_reading(self, page):
        """模拟真人阅读行为：随机滚动、停留"""
        logger.info("  👀 模拟真人阅读中...")
        # 随机滚动 3 到 6 次
        scroll_times = random.randint(3, 6)
        for _ in range(scroll_times):
            # 随机向下滚动 300 到 800 像素
            scroll_px = random.randint(300, 800)
            page.mouse.wheel(0, scroll_px)
            # 随机停留 1 到 3 秒
            time.sleep(random.uniform(1.0, 3.0))
        # 滚回顶部
        page.mouse.wheel(0, -10000)
        time.sleep(1.0)

    def process_articles(self):
        """主处理流程"""
        articles = self._fetch_new_articles()
        if not articles:
            logger.info("🎉 没有发现新的符合条件的文章。")
            return

        logger.info(f"🚀 发现 {len(articles)} 篇新文章，开始处理...")
        
        with sync_playwright() as p:
            # 启动浏览器 (headless=False 方便你看到过程，如果需要后台运行可改为 True)
            browser = p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            for i, article in enumerate(articles):
                logger.info(f"[{i+1}/{len(articles)}] 处理: {article['title'][:30]}...")
                try:
                    # 1. 打开文章
                    page.goto(article['link'], wait_until="domcontentloaded", timeout=30000)
                    time.sleep(2.0) # 等待页面初始渲染

                    # 2. 模拟阅读
                    self._simulate_human_reading(page)

                    # 3. 尝试点赞 (如果模式为 like)
                    if self.mode == "like":
                        try:
                            # 微信文章底部的点赞按钮通常包含文本 "赞" 或 "推荐" (新版)
                            # 使用 locator 查找并点击
                            like_btn = page.locator("text=推荐").first
                            if not like_btn.count():
                                like_btn = page.locator("text=赞").first
                            
                            if like_btn.count() and like_btn.is_visible():
                                like_btn.click()
                                logger.info("  ✅ 已尝试点击 '赞/推荐'")
                                
                                # 点击后可能会弹出“扫码登录”提示，等待一下并关闭弹窗（如果有）
                                time.sleep(2.0)
                                # 尝试点击弹窗的关闭按钮 (如果有)
                                close_btn = page.locator(".weui-desktop-dialog__close").first
                                if close_btn.count():
                                    close_btn.click()
                            else:
                                logger.info("  ℹ️ 未找到点赞按钮，或已点过。")
                        except PlaywrightTimeout:
                            logger.warning("  ⚠️ 查找点赞按钮超时，可能页面结构变化或未登录。")

                    # 4. 随机休眠，防止被风控
                    sleep_time = random.uniform(10.0, 20.0)
                    logger.info(f"  💤 休眠 {sleep_time:.1f} 秒...")
                    time.sleep(sleep_time)

                except Exception as e:
                    logger.error(f"  ❌ 处理文章失败: {e}")
                    continue

            browser.close()
            
        logger.info("🎉 所有文章处理完毕！")