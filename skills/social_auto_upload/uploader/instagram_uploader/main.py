# skills/social_auto_upload/uploader/instagram_uploader/main.py
# -*- coding: utf-8 -*-
"""Instagram 图文发布器 (完整修复版)"""
from __future__ import annotations
import asyncio
import os
import time
from pathlib import Path
from patchright.async_api import Page, Playwright, async_playwright
from conf import BASE_DIR, LOCAL_CHROME_HEADLESS, LOCAL_CHROME_PATH
from uploader.base_video import BaseVideoUploader
from utils.base_social_media import set_init_script
from utils.log import logger

INSTAGRAM_HOME_URL = "https://www.instagram.com/"
# 改用主站的创建按钮，比 creator 页面更稳
INSTAGRAM_CREATE_URL = "https://www.instagram.com/" 

def _resolve_account_file(account_file: str | Path) -> str:
    path = Path(account_file).expanduser()
    if path.is_absolute():
        return str(path)
    if len(path.parts) == 1:
        return str((Path(BASE_DIR) / "cookies" / "instagram_uploader" / path).resolve())
    return str(path.resolve())


async def cookie_auth(account_file) -> bool:
    account_file = _resolve_account_file(account_file)
    if not os.path.exists(account_file):
        return False
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True, channel="chromium")
        try:
            context = await browser.new_context(storage_state=account_file)
            context = await set_init_script(context)
            page = await context.new_page()
            await page.goto(INSTAGRAM_HOME_URL, wait_until="domcontentloaded")
            await page.wait_for_timeout(5000)
            
            # 1. 如果 URL 明确包含 login，直接失败
            if "login" in page.url or "accounts" in page.url:
                return False
            
            # 2. 检查是否存在登录表单（如果有，说明肯定没登录）
            login_form = page.locator('input[name="username"]')
            if await login_form.count() > 0:
                return False
                
            # 3. 检查是否有发帖或主页图标
            profile_btn = page.locator('svg[aria-label="New post"], svg[aria-label="Profile"]').first
            return await profile_btn.count() > 0
        except Exception:
            return False
        finally:
            await browser.close()

async def instagram_setup(account_file, handle=False, return_detail=False, headless: bool = LOCAL_CHROME_HEADLESS):
    account_file = _resolve_account_file(account_file)
    
    # 先检测现有 Cookie 是否有效
    if os.path.exists(account_file) and await cookie_auth(account_file):
        return {"success": True, "message": "Cookie 有效"}

    if not handle:
        return {"success": False, "message": "Cookie 无效，请先登录"}
    
    print("🔐 正在打开浏览器，请在弹出的窗口中手动登录 Instagram...")
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False, channel="chromium")
        context = await browser.new_context()
        context = await set_init_script(context)
        page = await context.new_page()
        await page.goto(INSTAGRAM_HOME_URL)
        
        # 强制等待 3 秒，让页面完全跳转到登录页（或主页）
        await asyncio.sleep(3)
        
        success = False
        print("⏳ 请在浏览器中完成登录，脚本会自动检测（最长等待 5 分钟）...")
        
        # 循环检测 300 次，每次 1 秒
        for _ in range(300):
            await asyncio.sleep(1)
            
            # 实时检测页面元素
            try:
                # 如果出现了用户名输入框，说明还在登录页，继续等
                login_form = page.locator('input[name="username"]')
                if await login_form.count() > 0:
                    continue
                
                # 如果出现了发帖图标，说明登录成功，且进入了主页
                profile_btn = page.locator('svg[aria-label="New post"], svg[aria-label="新帖子"]').first
                if await profile_btn.count() > 0:
                    success = True
                    break
                    
            except Exception:
                pass
        
        if success:
            # 稍微多等 2 秒，确保 Cookie 完全写入
            await asyncio.sleep(2)
            await context.storage_state(path=account_file)
            print("✅ 登录成功，Cookie 已保存！")
        else:
            print("❌ 登录超时（5 分钟未完成）")
        
        await context.close()
        await browser.close()
        
        if success:
            return {"success": True, "message": "登录成功"}
        return {"success": False, "message": "登录超时"}
        
class InstaPost(BaseVideoUploader):
    """Instagram 图文发布"""
    def __init__(self, image_paths, title="", note="", account_file="", headless: bool = LOCAL_CHROME_HEADLESS, **kwargs):
        self.image_paths = [str(p) for p in image_paths]
        # 合并标题和正文作为 Caption
        self.caption = f"{title}\n\n{note}".strip()
        self.account_file = _resolve_account_file(account_file)
        self.headless = headless

    async def upload(self, playwright: Playwright) -> None:
        browser = await playwright.chromium.launch(headless=self.headless, channel="chromium")
        # 直接注入 Cookie
        context = await browser.new_context(storage_state=self.account_file, viewport={"width": 1280, "height": 800})
        context = await set_init_script(context)
        page = await context.new_page()
        
        try:
            logger.info("🚀 正在打开 Instagram...")
            await page.goto(INSTAGRAM_CREATE_URL, wait_until="domcontentloaded")
            await page.wait_for_timeout(5000)
            
            # 处理可能出现的 "Save Info" 或 "Notifications" 弹窗
            try:
                not_now_btn = page.locator('button:has-text("Not Now"), button:has-text("稍后")').first
                if await not_now_btn.is_visible(timeout=3000):
                    await not_now_btn.click()
            except:
                pass

            # 1. 点击左侧导航栏的 "Create" (发帖图标)
            logger.info("点击发帖按钮...")
            create_btn = page.locator('svg[aria-label="New post"], svg[aria-label="新帖子"]').first
            await create_btn.click()
            await page.wait_for_timeout(2000)
            
            # 2. 上传图片
            logger.info(f"选择图片 ({len(self.image_paths)} 张)...")
            file_input = page.locator('input[type="file"]').first
            await file_input.set_input_files(self.image_paths)
            await page.wait_for_timeout(5000) # 等待图片加载
            
            # 3. 点击 "Next" (裁剪页面)
            next_btn = page.locator('div[role="button"]:has-text("Next"), div[role="button"]:has-text("下一步")').last
            await next_btn.click()
            await page.wait_for_timeout(2000)
            
            # 4. 点击 "Next" (滤镜/编辑页面)
            next_btn = page.locator('div[role="button"]:has-text("Next"), div[role="button"]:has-text("下一步")').last
            await next_btn.click()
            await page.wait_for_timeout(2000)
            
            # 5. 填写 Caption
            logger.info("填写文案...")
            caption_box = page.locator('div[aria-label="Write a caption..."], div[aria-label="编写配文..."]').first
            await caption_box.click()
            await page.wait_for_timeout(500)
            # 模拟人类打字
            await page.keyboard.type(self.caption[:2200], delay=10)
            await page.wait_for_timeout(1000)
            
            # 6. 点击 "Share"
            logger.info("点击分享...")
            share_btn = page.locator('div[role="button"]:has-text("Share"), div[role="button"]:has-text("分享")').last
            await share_btn.click()
            
            # 等待上传完成 (出现 "Your post has been shared" 等字样)
            await page.wait_for_timeout(8000)
            
            # 保存最新 Cookie
            await context.storage_state(path=self.account_file)
            logger.success("✅ Instagram 发布完成！")
            
        except Exception as e:
            logger.error(f"❌ Instagram 发布失败: {e}")
            raise
        finally:
            await context.close()
            await browser.close()

    async def main(self):
        async with async_playwright() as playwright:
            await self.upload(playwright)