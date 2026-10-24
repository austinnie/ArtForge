# skills/wechat_liker/skill.py
"""
微信公众号文章自动点赞技能 (极简稳定版：激活窗口 + End键触底)
"""
import time
import random
import logging
import pyperclip
import uiautomation as auto

logger = logging.getLogger(__name__)

class WechatLiker:
    def __init__(self, delay_range=(10, 20)):
        self.delay_range = delay_range
        self.wechat_window = None

    def _get_wechat_window(self):
        """获取微信主窗口"""
        if self.wechat_window and self.wechat_window.Exists(0, 0):
            return self.wechat_window
        self.wechat_window = auto.WindowControl(ClassName="WeChatMainWndForPC")
        if self.wechat_window.Exists(3, 1):
            return self.wechat_window
        self.wechat_window = auto.WindowControl(searchDepth=1, Name="微信")
        if self.wechat_window.Exists(3, 1):
            return self.wechat_window
        raise RuntimeError("❌ 未找到 PC 版微信窗口，请确保微信已登录并运行。")

    def _click_visit_card_by_position(self, search_win) -> bool:
        """根据搜索窗口相对位置点击“访问网页”卡片"""
        try:
            rect = search_win.BoundingRectangle
            card_x = rect.left + int((rect.right - rect.left) * 0.35)
            card_y = rect.top + 220
            logger.info(f"🎯 点击“访问网页”卡片坐标: ({card_x}, {card_y})")
            auto.Click(card_x, card_y)
            return True
        except Exception as e:
            logger.error(f"❌ 坐标点击异常: {e}")
            return False

    def like_article(self, url: str, action: str = "like") -> bool:
        if not url.startswith("http"):
            logger.error(f"❌ 无效的链接: {url}")
            return False

        try:
            # ================= 第一部分：打开网页（保留原有逻辑） =================
            wx = self._get_wechat_window()
            wx.SwitchToThisWindow()
            time.sleep(0.5)

            logger.info(f" 呼出微信搜索框...")
            wx.SendKeys("{Ctrl}f")
            time.sleep(0.8)
            
            pyperclip.copy(url)
            wx.SendKeys("{Ctrl}v")
            time.sleep(1)
            wx.SendKeys("{Enter}")
            time.sleep(2.5)

            search_win = auto.GetForegroundControl()
            logger.info("🖱️ 正在点击【访问网页】卡片...")
            self._click_visit_card_by_position(search_win)
            time.sleep(4)

            # ================= 第二部分：滚动到底部并点赞（极简重写） =================
            
            # 1. 获取文章窗口
            article_window = auto.WindowControl(ClassName="Chrome_WidgetWin_1")
            if not article_window.Exists(2, 1):
                wx.SendKeys("{Enter}") 
                time.sleep(3)
                article_window = auto.WindowControl(ClassName="Chrome_WidgetWin_1")

            if not article_window.Exists(2, 1):
                logger.error("❌ 无法打开文章窗口。")
                return False

            # 2.  核心：激活窗口并点击“空白区域”锁定焦点
            article_window.SwitchToThisWindow()
            time.sleep(0.5)
            rect = article_window.BoundingRectangle
            width = rect.right - rect.left
            height = rect.bottom - rect.top
            
            # 计算窗口中上部的坐标（避开底部按钮，也尽量避开文章开头的图片）
            # 点击这里是为了让焦点落在网页正文的空白处，而不是图片上
            focus_x = rect.left + int(width * 0.5)
            focus_y = rect.top + int(height * 0.3) 

            logger.info("🔒 正在点击网页空白区域锁定焦点...")
            auto.Click(focus_x, focus_y)
            time.sleep(0.5)

            # 3. 🔥 核心：使用 {End} 键直接滚动到最底部
            # 只要焦点在网页正文，{End} 键 100% 触底，且绝对不会触发图片缩放
            logger.info("📜 正在发送 {End} 键滚动到最底部...")
            auto.SendKeys("{End}")
            time.sleep(2.0)  # 等待滚动动画和底部按钮渲染

            # 4. 🔥 相对坐标精准点击“赞”
            # 微信底部栏布局："赞" 永远在窗口宽度的 62% 处，距底部边缘 25px
            logger.info("🎯 正在通过相对坐标点击【赞】...")
            
            if action == "like":
                target_x = rect.left + int(width * 0.62)
                target_y = rect.bottom - 25
            else:
                # 点击“推荐” (在赞的右侧，大约 72% 处)
                target_x = rect.left + int(width * 0.72)
                target_y = rect.bottom - 25

            auto.Click(target_x, target_y)
            logger.info(f"✅ 已执行点击坐标: ({target_x}, {target_y})")
            time.sleep(1.5)

            # 5. 随机休眠
            sleep_time = random.uniform(*self.delay_range)
            logger.info(f"💤 休眠 {sleep_time:.1f} 秒...")
            time.sleep(sleep_time)

            return True

        except Exception as e:
            logger.error(f"💥 执行异常: {e}")
            return False

    def batch_like(self, urls: list, action: str = "like"):
        logger.info(f"🚀 开始批量 {action} 任务，共 {len(urls)} 篇文章")
        success_count = 0
        for i, url in enumerate(urls):
            logger.info(f"\n------------------ [{i+1}/{len(urls)}] ------------------")
            if self.like_article(url, action):
                success_count += 1
        logger.info(f"\n🎉 批量处理完成: 成功 {success_count}/{len(urls)}")