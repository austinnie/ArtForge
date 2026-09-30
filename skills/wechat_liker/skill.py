# skills/wechat_liker/skill.py
"""
微信公众号文章自动点赞技能 (焦点激活 + DOM 深度 Debug + 坐标兜底点赞版)
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

    def _dump_window_controls(self, control, max_depth=3, current_depth=0):
        """Debug 节点挖掘函数：打印文章窗口内的 UI 控件树"""
        if current_depth > max_depth:
            return
        
        children = control.GetChildren()
        for child in children:
            try:
                name = child.Name.strip() if child.Name else ""
                ctrl_type = child.ControlTypeName
                if name or current_depth <= 2:
                    logger.debug(f"{'  ' * current_depth}├── [{ctrl_type}] Name: '{name}' (ClassName: {child.ClassName})")
                self._dump_window_controls(child, max_depth, current_depth + 1)
            except Exception:
                continue

    def _click_bottom_like_by_position(self, article_win) -> bool:
        """兜底方案：在文章窗口底部直接按照相对比例点击“赞”按钮"""
        try:
            rect = article_win.BoundingRectangle
            # 计算底部“赞”按钮的位置（通常位于窗口底端向上约 25px，水平靠右约 30% 区域，或左下用户头像右侧）
            # 根据截图：底栏在最下方，"👍 赞" 在底栏中间偏右位置
            click_x = rect.left + int((rect.right - rect.left) * 0.70)
            click_y = rect.bottom - 22  # 距底部边缘 22 像素
            
            logger.info(f"🎯 执行【坐标兜底点赞】：点击位置 ({click_x}, {click_y})")
            auto.Click(click_x, click_y)
            return True
        except Exception as e:
            logger.error(f"❌ 兜底坐标点击失败: {e}")
            return False

    def like_article(self, url: str, action: str = "like") -> bool:
        if not url.startswith("http"):
            logger.error(f"❌ 无效的链接: {url}")
            return False

        try:
            wx = self._get_wechat_window()
            wx.SwitchToThisWindow()
            time.sleep(0.5)

            logger.info(f"🔍 呼出微信搜索框...")
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

            # 获取文章窗口
            article_window = auto.WindowControl(ClassName="Chrome_WidgetWin_1")
            
            if not article_window.Exists(2, 1):
                logger.info("⚠️ 未检测到文章窗口，重试 Enter...")
                wx.SendKeys("{Enter}")
                time.sleep(3)
                article_window = auto.WindowControl(ClassName="Chrome_WidgetWin_1")

            if not article_window.Exists(2, 1):
                logger.error("❌ 无法打开文章窗口，请检查网络或微信状态。")
                return False

            # 1. 激活并点击窗口中央，获取输入焦点
            article_window.SwitchToThisWindow()
            time.sleep(0.5)
            rect = article_window.BoundingRectangle
            center_x = rect.left + int((rect.right - rect.left) / 2)
            center_y = rect.top + int((rect.bottom - rect.top) / 2)
            auto.Click(center_x, center_y)  # 激活 CEF 页面内部焦点
            time.sleep(0.5)

            # 2. 强力向下滚动到底部
            logger.info("📜 正在强力滚动文章到底部...")
            auto.SendKeys("{End}")
            time.sleep(0.8)
            auto.SendKeys("{PageDown}")
            time.sleep(0.8)
            
            # 使用鼠标滚轮继续向下滚，确保彻底触底
            for _ in range(5):
                auto.WheelDown(wheelTimes=5)
                time.sleep(0.1)

            time.sleep(1.5)  # 等待底层点赞控件渲染

            # 3. Debug: Dig/挖掘当前窗口 DOM 树控件
            logger.info("🔍 [DEBUG] 正在挖掘文章窗口 UI 控件树...")
            self._dump_window_controls(article_window, max_depth=3)

            # 4. 尝试寻找 UIA 控件点赞
            btn_names = ["推荐", "赞"] if action == "like" else ["在看"]
            clicked = False
            
            for name in btn_names:
                # 不限制控件类型，查找所有包含对应 Name 的 Control
                ctrl = article_window.Control(Name=name, searchDepth=25)
                if ctrl.Exists(1, 0):
                    ctrl.Click()
                    logger.info(f"🎉 成功找到并点击【{name}】控件！")
                    clicked = True
                    break

            # 5. 如果 UIA 未查找到，使用坐标兜底点击底栏“赞”
            if not clicked:
                logger.warning("⚠️ UIA 未探测到控件，正在启动【相对坐标点击】方案...")
                clicked = self._click_bottom_like_by_position(article_window)

            # 6. 休眠
            sleep_time = random.uniform(*self.delay_range)
            logger.info(f"💤 休眠 {sleep_time:.1f} 秒...")
            time.sleep(sleep_time)

            return clicked

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