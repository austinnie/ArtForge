# skills/social_auto_upload/uploader/facebook_uploader/main.py
# -*- coding: utf-8 -*-
"""
Facebook 动态发布器
支持发布文字+图片到个人主页或公共主页。
"""
from __future__ import annotations
import asyncio
import os
from pathlib import Path
from patchright.async_api import Page, Playwright, async_playwright
from conf import BASE_DIR, LOCAL_CHROME_HEADLESS
from uploader.base_video import BaseVideoUploader
from utils.base_social_media import set_init_script

FACEBOOK_HOME_URL = "https://www.facebook.com/"

def _resolve_account_file(account_file: str | Path) -> str:
    path = Path(account_file).expanduser()
    if path.is_absolute(): return str(path)
    if len(path.parts) == 1:
        return str((Path(BASE_DIR) / "cookies" / "facebook_uploader" / path).resolve())
    return str(path.resolve())

async def cookie_auth(account_file) -> bool:
    account_file = _resolve_account_file(account_file)
    if not os.path.exists(account_file): return False
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True, channel="chromium")
        try:
            context = await browser.new_context(storage_state=account_file)
            context = await set_init_script(context)
            page = await context.new_page()
            await page.goto(FACEBOOK_HOME_URL, wait_until="domcontentloaded")
            await page.wait_for_timeout(5000)
            if "login" in page.url: return False
            # 检查是否有菜单按钮（登录态）
            menu_btn = page.locator('div[aria-label="Menu"]').first
            return await menu_btn.count() > 0
        except Exception:
            return False
        finally:
            await browser.close()

class FBPost(BaseVideoUploader):
    def __init__(self, image_paths, text, account_file, headless: bool = LOCAL_CHROME_HEADLESS):
        self.image_paths = [str(p) for p in image_paths]
        self.text = text
        self.account_file = _resolve_account_file(account_file)
        self.headless = headless

    async def upload(self, playwright: Playwright) -> None:
        browser = await playwright.chromium.launch(headless=self.headless, channel="chromium")
        context = await browser.new_context(storage_state=self.account_file)
        context = await set_init_script(context)
        page = await context.new_page()
        
        try:
            await page.goto(FACEBOOK_HOME_URL, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            
            # 1. 点击“创建帖子”输入框
            post_box = page.locator('div[contenteditable="true"][role="textbox"][aria-label="What\'s on your mind?"]').first
            if not await post_box.count():
                # 备选选择器
                post_box = page.locator('div[contenteditable="true"][role="textbox"]').first
            
            await post_box.click()
            await page.wait_for_timeout(1000)
            
            # 2. 输入文字
            if self.text:
                await post_box.fill(self.text)
                logger.info("✅ 已填写文字")
            
            # 3. 上传图片 (通过点击照片/视频按钮)
            if self.image_paths:
                photo_btn = page.locator('div[aria-label="Photo/video"]').first
                if await photo_btn.count():
                    async with page.expect_file_chooser() as fc_info:
                        await photo_btn.click()
                    file_chooser = await fc_info.value
                    await file_chooser.set_files(self.image_paths)
                    logger.info(f"✅ 已上传 {len(self.image_paths)} 张图片")
                    await page.wait_for_timeout(5000) # 等待上传
            
            # 4. 点击“发布” (Post)
            # FB 的发布按钮文案可能是 "Post" 或 "发布"
            post_btn = page.locator('div[aria-label="Post"], div[aria-label="发布"]').first
            if await post_btn.count():
                await post_btn.click()
                logger.info("🚀 已点击发布")
                await page.wait_for_timeout(5000)
                
            await context.storage_state(path=self.account_file)
            logger.success("✅ Facebook 发布完成")
            
        except Exception as e:
            logger.error(f"❌ Facebook 发布失败: {e}")
            raise
        finally:
            await context.close()
            await browser.close()