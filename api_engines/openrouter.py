# api_engines/openrouter.py
"""OpenRouter 图像生成引擎 - 聚合 30+ 图像模型"""

import requests
import base64
import io
import time
import json
import random
from PIL import Image


class OpenRouterEngine:
    """OpenRouter 引擎 - 支持 Seedream、GPT-Image 等 30+ 模型"""

    # 常用图像模型
    AVAILABLE_MODELS = [
        "bytedance-seed/seedream-4.5",
        "openai/gpt-image-2",
        "google/gemini-3.1-flash-image",
        "black-forest-labs/flux-1.1-pro",
    ]

    def __init__(self, api_key: str, model: str = "bytedance-seed/seedream-4.5"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"

        if not self.api_key:
            print("⚠️ 未设置 OPENROUTER_API_KEY，请从 https://openrouter.ai 获取")

        print(f"🔍 OpenRouter 引擎初始化")
        print(f"🔍 模型: {self.model}")

    def generate_single(
        self,
        prompt: str,
        negative: str = "",
        width: int = 1024,
        height: int = 1024,
        steps: int = 20,
        cfg: float = 7.5,
        seed: int = None,
    ) -> Image.Image:

        if seed is None:
            seed = random.randint(1, 2**32 - 1)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://promptforge.local",  # OpenRouter 要求
            "X-Title": "PromptForge",
        }

        data = {
            "model": self.model,
            "prompt": prompt,
            "n": 1,
            "size": f"{width}x{height}",
            "response_format": "b64_json",
        }
        if seed:
            data["seed"] = seed

        print(f"🔍 OpenRouter 请求")
        print(f"🔍 模型: {self.model}, 尺寸: {width}x{height}")

        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                resp = requests.post(
                    f"{self.base_url}/images/generations",
                    headers=headers,
                    json=data,
                    timeout=180,  # OpenRouter 图像生成可能较慢（~94s）
                )

                if resp.status_code == 200:
                    result = resp.json()
                    item = result["data"][0]

                    b64 = item.get("b64_json")
                    if b64:
                        if b64.startswith("data:image"):
                            b64 = b64.split(",", 1)[1]
                        return Image.open(io.BytesIO(base64.b64decode(b64)))

                    img_url = item.get("url")
                    if img_url:
                        img_resp = requests.get(img_url, timeout=60)
                        return Image.open(io.BytesIO(img_resp.content))

                    raise Exception(f"无法解析图片: {json.dumps(result)[:200]}")

                if resp.status_code in (429, 500, 502, 503):
                    print(f"⚠️ 状态码 {resp.status_code}，重试 ({attempt}/{max_retries})")
                    time.sleep(3 * attempt)
                    continue

                raise Exception(f"OpenRouter 失败 (状态码 {resp.status_code}): {resp.text[:200]}")

            except requests.exceptions.RequestException as e:
                if attempt == max_retries:
                    raise Exception(f"OpenRouter 请求失败: {e}")
                time.sleep(2)

        raise Exception("OpenRouter 生成失败：所有重试已用尽")

    def get_usage(self):
        return {"info": "请登录 https://openrouter.ai 查看使用量"}

    def get_model(self) -> str:
        return self.model

    def get_name(self) -> str:
        return f"OpenRouter ({self.model})"