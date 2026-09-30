# skills/wechat_liker/skill.py
"""
微信公众号文章自动点赞/在看技能 (终极稳定版)
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
        """获取微信主窗口 (增强鲁棒性)"""
        if self.wechat_window and self.wechat_window.Exists(0, 0):
            return self.wechat_window
        
        # 优先通过 ClassName 查找，不依赖可能带有未读消息数的 Name
        self.wechat_window = auto.WindowControl(ClassName="WeChatMainWndForPC")
        if self.wechat_window.Exists(3, 1):
            return self.wechat_window
            
        self.wechat_window = auto.WindowControl(searchDepth=1, Name="微信")
        if self.wechat_window.Exists(3, 1):
            return self.wechat_window
            
        raise RuntimeError("❌ 未找到 PC 版微信窗口，请确保微信已登录并运行。")

    def like_article(self, url: str, action: str = "like") -> bool:
        if not url.startswith("http"):
            logger.error(f"❌ 无效的链接: {url}")
            return False

        try:
            wx = self._get_wechat_window()
            wx.SwitchToThisWindow()
            time.sleep(1)

            logger.info(f"🔍 正在搜索: {url[:30]}...")
            # 1. 呼出搜索框
            auto.SendKeys("{Ctrl}f")
            time.sleep(1)
            
            # 2. 粘贴链接
            pyperclip.copy(url)
            auto.SendKeys("{Ctrl}v")
            time.sleep(2)  # 🔥 关键：等待搜索结果列表渲染出来
            
            # 3. 🔥 核心改进：确保选中第一个结果并打开
            # 先按 Down 键，将焦点从搜索框移动到第一个搜索结果（通常是"访问网页"）
            auto.SendKeys("{Down}")
            time.sleep(0.5)
            auto.SendKeys("{Enter}")
            
            # 4. 🔥 核心改进：严格等待文章窗口弹出并加载完成
            logger.info("⏳ 等待文章窗口加载...")
            article_window = auto.WindowControl(ClassName="Chrome_WidgetWin_1")
            max_wait = 10
            loaded = False
            for _ in range(max_wait):
                if article_window.Exists(1, 1):
                    # 窗口出现了，再多等 2 秒确保内部 DOM 和按钮渲染完毕
                    time.sleep(2.5)
                    loaded = True
                    break
                time.sleep(1)
                
            if not loaded:
                logger.error("❌ 文章窗口超时未弹出，可能链接失效或网络卡顿。")
                return False
            
            # 激活文章窗口
            article_window.SwitchToThisWindow()
            time.sleep(1)

            # 5. 🔥 核心改进：滚动到底部 (按两次 End 确保绝对到底)
            logger.info("📜 滚动到文章底部...")
            article_window.SendKeys("{End}")
            time.sleep(1)
            article_window.SendKeys("{End}") 
            time.sleep(1.5) # 等待滚动动画和底部按钮渲染

            # 6. 🔥 核心改进：多维度查找点赞按钮
            btn_names = ["推荐", "赞"] if action == "like" else ["在看"]
            clicked = False
            
            for name in btn_names:
                # 尝试找 Button 控件
                btn = article_window.ButtonControl(Name=name, searchDepth=20)
                if btn.Exists(0, 0):
                    btn.Click()
                    logger.info(f"✅ 成功点击 Button: {name}")
                    clicked = True
                    break
                
                # 尝试找 Text 控件
                txt = article_window.TextControl(Name=name, searchDepth=20)
                if txt.Exists(0, 0):
                    txt.Click()
                    logger.info(f"✅ 成功点击 Text: {name}")
                    clicked = True
                    break
                
                # 尝试找 Pane 控件 (有时按钮被包裹在 Pane 中)
                pane = article_window.PaneControl(Name=name, searchDepth=20)
                if pane.Exists(0, 0):
                    pane.Click()
                    logger.info(f"✅ 成功点击 Pane: {name}")
                    clicked = True
                    break

            # 7. 🔥 终极兜底：如果名字都找不到，直接点击窗口右下角区域 (微信点赞按钮的固定位置)
            if not clicked:
                logger.warning(f"⚠️ 未通过名称找到 '{btn_names}'，尝试坐标兜底点击...")
                rect = article_window.BoundingRectangle
                if rect.width() > 0 and rect.height() > 0:
                    # 估算右下角点赞按钮位置 (距离右边 120px, 距离底部 60px)
                    click_x = rect.right - 120
                    click_y = rect.bottom - 60
                    logger.info(f"🎯 执行坐标点击: ({click_x}, {click_y})")
                    auto.Click(click_x, click_y)
                    clicked = True
                else:
                    logger.error("❌ 无法获取窗口坐标进行兜底点击")

            # 8. 关闭文章窗口
            time.sleep(1)
            article_window.SendKeys("{Alt}F4")
            time.sleep(1)

            # 9. 随机休眠
            sleep_time = random.uniform(*self.delay_range)
            logger.info(f"💤 休眠 {sleep_time:.1f} 秒...")
            time.sleep(sleep_time)
            
            return clicked

        except Exception as e:
            logger.error(f"💥 点赞过程异常: {e}")
            try:
                auto.WindowControl(ClassName="Chrome_WidgetWin_1").SendKeys("{Alt}F4")
            except: pass
            return False

    def batch_like(self, urls: list, action: str = "like"):
        logger.info(f"🚀 开始批量 {action}，共 {len(urls)} 篇文章")
        success_count = 0
        for i, url in enumerate(urls):
            logger.info(f"[{i+1}/{len(urls)}] 处理中...")
            if self.like_article(url, action):
                success_count += 1
        logger.info(f"🎉 批量完成: 成功 {success_count}/{len(urls)}")