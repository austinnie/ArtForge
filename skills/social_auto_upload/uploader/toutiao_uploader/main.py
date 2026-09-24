# skills/social_auto_upload/uploader/toutiao_uploader/main.py
# -*- coding: utf-8 -*-
"""
今日头条 (头条号) 图文发布器
后台地址：https://mp.toutiao.com/
"""
from __future__ import annotations
import asyncio
import os
from pathlib import Path
from patchright.async_api import Page, Playwright, async_playwright
from conf import BASE_DIR, LOCAL_CHROME_HEADLESS
from uploader.base_video import BaseVideoUploader
from utils.base_social_media import set_init_script

TOUTIAO_HOME_URL = "https://mp.toutiao.com/"
TOUTIAO_PUBLISH_URL = "https://mp.toutiao.com/profile_v4/graphic/publish"

def _resolve_account_file(account_file: str | Path) -> str:
    path = Path(account_file).expanduser()
    if path.is_absolute(): return str(path)
    if len(path.parts) == 1:
        return str((Path(BASE_DIR) / "cookies" / "toutiao_uploader" / path).resolve())
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
            await page.goto(TOUTIAO_HOME_URL, wait_until="domcontentloaded")
            await page.wait_for_timeout(5000)
            if "login" in page.url: return False
            # 检查是否有“发布”按钮
            publish_btn = page.locator('button:has-text("发布")').first
            return await publish_btn.count() > 0
        except Exception:
            return False
        finally:
            await browser.close()

class ToutiaoPost(BaseVideoUploader):
    def __init__(self, title, content, image_paths, account_file, headless: bool = LOCAL_CHROME_HEADLESS):
        self.title = title
        self.content = content # 头条正文通常是富文本，这里简化处理，实际需操作编辑器
        self.image_paths = [str(p) for p in image_paths]
        self.account_file = _resolve_account_file(account_file)
        self.headless = headless

    async def upload(self, playwright: Playwright) -> None:
        browser = await playwright.chromium.launch(headless=self.headless, channel="chromium")
        context = await browser.new_context(storage_state=self.account_file)
        context = await set_init_script(context)
        page = await context.new_page()
        
        try:
            await page.goto(TOUTIAO_PUBLISH_URL, wait_until="domcontentloaded")
            await page.wait_for_timeout(5000)
            
            # 1. 填写标题
            title_input = page.locator('input[placeholder="请输入标题（5～30字）"]').first
            if await title_input.count():
                await title_input.fill(self.title[:30])
                logger.info("✅ 已填写标题")
            
            # 2. 上传图片 (头条图文通常先传图)
            if self.image_paths:
                upload_btn = page.locator('div.upload-image-card, button:has-text("上传图片")').first
                if await upload_btn.count():
                    async with page.expect_file_chooser() as fc_info:
                        await upload_btn.click()
                    file_chooser = await fc_info.value
                    await file_chooser.set_files(self.image_paths)
                    logger.info(f"✅ 已上传 {len(self.image_paths)} 张图片")
                    await page.wait_for_timeout(5000)
            
            # 3. 填写正文 (简化版：操作 contenteditable 区域)
            # 头条编辑器是复杂的富文本，这里仅做示例
            editor = page.locator('div.ql-editor, div[contenteditable="true"]').first
            if await editor.count():
                await editor.click()
                await page.keyboard.type(self.content)
                logger.info("✅ 已填写正文")
            
            # 4. 点击“发布”
            submit_btn = page.locator('button.publish-btn, button:has-text("发布")').first
            if await submit_btn.count():
                await submit_btn.click()
                logger.info("🚀 已点击发布")
                await page.wait_for_timeout(5000)
                
            await context.storage_state(path=self.account_file)
            logger.success("✅ 今日头条发布完成")
            
        except Exception as e:
            logger.error(f"❌ 今日头条发布失败: {e}")
            raise
        finally:
            await context.close()
            await browser.close()