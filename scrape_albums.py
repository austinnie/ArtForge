import asyncio
import json
import urllib.parse
from pathlib import Path
from patchright.async_api import async_playwright

# 你的公众号 Biz ID (从你给的链接里提取的)
BIZ = "Mzg2Njc1OTk4NQ=="
STATE_FILE = Path("wechat_admin_state.json")

async def main():
    async with async_playwright() as p:
        # 启动浏览器 (首次运行不要用 headless，需要扫码)
        browser = await p.chromium.launch(headless=False)
        
        # 加载登录态，如果没有则新建
        if STATE_FILE.exists():
            context = await browser.new_context(storage_state=STATE_FILE)
        else:
            context = await browser.new_context()

        page = await context.new_page()

        # 用于存储拦截到的合集数据
        albums_data = []
        
        # 核心：监听网络响应，自动捕获包含 album 数据的 API
        async def handle_response(response):
            # 微信获取合集列表的接口通常包含 appmsg 且 action 是 list_ex 或类似
            if "cgi-bin/appmsg" in response.url and response.status == 200:
                try:
                    data = await response.json()
                    # 检查返回的 JSON 里是否有合集列表
                    if data and "album_list" in data:
                        for item in data["album_list"]:
                            base_info = item.get("base_info", {})
                            album_id = base_info.get("album_id")
                            title = base_info.get("title")
                            if album_id and title:
                                # 去重
                                if not any(a["id"] == album_id for a in albums_data):
                                    albums_data.append({
                                        "id": album_id,
                                        "title": title.strip()
                                    })
                                    print(f"✅ 成功捕获: {title} (ID: {album_id})")
                except Exception:
                    pass # 忽略非 JSON 响应或解析错误

        page.on("response", handle_response)

        print("🌐 正在打开微信公众平台...")
        await page.goto("https://mp.weixin.qq.com/")

        # 判断是否需要扫码
        if "cgi-bin/home" not in page.url:
            print("⚠️ 请在浏览器中扫码登录您的公众号！")
            print("⏳ 等待登录跳转...")
            await page.wait_for_url("**/cgi-bin/home**", timeout=0)
            # 登录成功后保存状态，下次就不用扫码了
            await context.storage_state(path=STATE_FILE)
            print("💾 登录状态已保存，下次运行无需扫码。")

        print("📂 正在打开合集管理页面...")
        
        # 直接通过点击左侧菜单进入合集页面最稳妥
        # 先等待后台左侧菜单加载
        await page.wait_for_selector("iframe", timeout=10000)
        
        # 微信后台的内容通常在 iframe 里，我们直接走特定的前端路由
        # 使用 token 跳到合集页面的捷径
        token = await page.evaluate("() => window.wx.commonData.t")
        if not token:
            # 兜底：从 URL 获取
            parsed = urllib.parse.urlparse(page.url)
            token = urllib.parse.parse_qs(parsed.query).get("token", [""])[0]
            
        album_url = f"https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_list&action=list_ex&type=10&begin=0&count=10&token={token}&lang=zh_CN"
        await page.goto(album_url)
        
        # 等待第一页数据加载完毕
        await page.wait_for_timeout(3000)
        
        # 自动翻页 (假设最多 10 页，每页10条)
        print("🔄 开始自动翻页抓取...")
        for page_num in range(1, 10):
            # 尝试点击“下一页”按钮，或者直接修改 URL 的 begin 参数
            # 这里采用直接修改 URL 参数的方法，更稳定
            next_url = f"https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_list&action=list_ex&type=10&begin={page_num*10}&count=10&token={token}&lang=zh_CN"
            await page.goto(next_url)
            await page.wait_for_timeout(2000) # 给接口响应留出时间
            
            # 如果连续两页没有抓到新数据，说明到底了
            if len(albums_data) % 10 != 0 or len(albums_data) == 0:
                break

        await browser.close()

        if not albums_data:
            print("❌ 未抓到任何合集，可能是后台改版或接口变了。")
            return

        # 1. 保存为 JSON (方便以后使用)
        json_path = Path("albums_data.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(albums_data, f, ensure_ascii=False, indent=2)
        print(f"\n💾 纯数据已保存至: {json_path}")

        # 2. 生成 Markdown 导航文档
        md_lines = ["# 📚 公众号全站历史合集导航\n", "> 内部索引页，持续更新。\n"]
        
        for album in albums_data:
            # 拼装微信合集的真实跳转链接
            url = f"https://mp.weixin.qq.com/mp/appmsgalbum?__biz={BIZ}&action=getalbum&album_id={album['id']}#wechat_redirect"
            md_lines.append(f"- [{album['title']}]({url})")
            
        md_path = Path("albums_navigation.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))
            
        print(f"📝 导航文章 Markdown 已生成: {md_path}")
        print("👉 接下来你可以直接用 wechat_formatter 把它排版并发布到公众号后台。")

if __name__ == "__main__":
    asyncio.run(main())