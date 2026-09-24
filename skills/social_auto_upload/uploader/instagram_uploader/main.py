# skills/social_auto_upload/uploader/instagram_uploader/main.py
# -*- coding: utf-8 -*-
"""
Instagram 图文发布器
注意：Instagram 风控极严，请务必使用“小号”测试，并确保账号已登录过网页版。
"""
from __future__ import annotations
import asyncio
import os
import time
from pathlib import Path
from patchright.async_api import Page, Playwright, async_playwright
from conf import BASE_DIR, LOCAL_CHROME_HEADLESS, LOCAL_CHROME_PATH
from uploader.base_video import BaseVideoUploader
from utils.base_social_media import set_init_script
from utils.log import logger # 复用通用日志或新建 instagram_logger

INSTAGRAM_HOME_URL = "https://www.instagram.com/"
INSTAGRAM_CREATE_URL = "https://www.instagram.com/creator/" # 创作者中心发布页更稳定

def _resolve_account_file(account_file: str | Path) -> str:
    path = Path(account_file).expanduser()
    if path.is_absolute():
        return str(path)
    if len(path.parts) == 1:
        return str((Path(BASE_DIR) / "cookies" / "instagram_uploader" / path).resolve())
    return str(path.resolve())

async def cookie_auth(account_file) -> bool:
    """验证 Instagram cookie"""
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
            # 如果跳转到登录页，说明 cookie 失效
            if "login" in page.url:
                return False
            # 检查是否有头像（登录态标志）
            profile_btn = page.locator('svg[aria-label="Profile"]').first
            return await profile_btn.count() > 0
        except Exception:
            return False
        finally:
            await browser.close()

async def instagram_setup(account_file, handle=False, return_detail=False, headless: bool = LOCAL_CHROME_HEADLESS):
    account_file = _resolve_account_file(account_file)
    if not os.path.exists(account_file) or not await cookie_auth(account_file):
        if not handle:
            return {"success": False, "message": "Cookie 无效"}
        # 这里简化处理，实际应打开浏览器让用户手动扫码/登录
        print("️ Instagram 需要手动登录，请在弹出的浏览器中操作...")
        # 触发登录逻辑（略，参考 douyin_cookie_gen）
        return {"success": False, "message": "请手动登录"}
    return {"success": True, "message": "Cookie 有效"}

class InstaPost(BaseVideoUploader):
    """Instagram 图文发布"""
    def __init__(self, image_paths, caption, account_file, headless: bool = LOCAL_CHROME_HEADLESS):
        self.image_paths = [str(p) for p in image_paths]
        self.caption = caption
        self.account_file = _resolve_account_file(account_file)
        self.headless = headless

    async def upload(self, playwright: Playwright) -> None:
        browser = await playwright.chromium.launch(headless=self.headless, channel="chromium")
        context = await browser.new_context(storage_state=self.account_file)
        context = await set_init_script(context)
        page = await context.new_page()
        
        try:
            # 1. 进入发布页
            await page.goto(INSTAGRAM_CREATE_URL, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            
            # 2. 点击“创建新帖子” (如果是创作者中心)
            # 注意：DOM 选择器可能随版本变化，需灵活调整
            create_btn = page.locator('button:has-text("Create")').first
            if await create_btn.count():
                await create_btn.click()
            
            # 3. 上传图片
            # Instagram 的 file input 通常隐藏，需要触发点击
            file_input = page.locator('input[type="file"][accept="image/*,image/heic,image/heif"]').first
            if not await file_input.count():
                file_input = page.locator('input[type="file"]').first
            
            await file_input.set_input_files(self.image_paths)
            logger.info(f"✅ 已选择 {len(self.image_paths)} 张图片")
            await page.wait_for_timeout(5000) # 等待上传处理
            
            # 4. 点击“下一步” (Next) - 可能需要点多次（裁剪、滤镜）
            for _ in range(3):
                next_btn = page.locator('button:has-text("Next")').first
                if await next_btn.count() and await next_btn.is_visible():
                    await next_btn.click()
                    await page.wait_for_timeout(1000)
                else:
                    break
            
            # 5. 填写 Caption
            caption_box = page.locator('textarea[placeholder="Write a caption..."]').first
            if await caption_box.count():
                await caption_box.click()
                await caption_box.fill(self.caption[:2200]) # IG 限制 2200 字
                logger.info("✅ 已填写文案")
            
            # 6. 点击“分享” (Share)
            share_btn = page.locator('button:has-text("Share")').first
            if await share_btn.count():
                await share_btn.click()
                logger.info("🚀 已点击分享")
                await page.wait_for_timeout(5000)
                
            # 7. 保存 Cookie
            await context.storage_state(path=self.account_file)
            logger.success("✅ Instagram 发布完成")
            
        except Exception as e:
            logger.error(f"❌ Instagram 发布失败: {e}")
            raise
        finally:
            await context.close()
            await browser.close()