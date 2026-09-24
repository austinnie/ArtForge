# api_engines/siliconflow.py
"""硅基流动 (SiliconFlow) 图像生成引擎"""

import requests
import base64
import io
import time
import json
import random
from PIL import Image


class SiliconFlowEngine:
    """硅基流动引擎 - 支持 SDXL、SD3、Qwen-Image 等"""

    # 免费/低价模型（2026年可用）
    AVAILABLE_MODELS = [
        "sd-turbo",                          # 免费，512x512
        "sdxl-turbo",                        # 免费，1024x1024
        "stable-diffusion-xl-base-1.0",
        "stable-diffusion-3-medium",
        "Qwen/Qwen-Image-Edit-2509",
    ]

    def __init__(self, api_key: str, model: str = "sd-turbo"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.siliconflow.cn/v1"

        if not self.api_key:
            print("⚠️ 未设置 SILICONFLOW_API_KEY，请从 https://siliconflow.cn 获取")

        print(f"🔍 硅基流动引擎初始化")
        print(f"🔍 模型: {self.model}")

    def _get_image_size(self, width: int, height: int) -> str:
        """硅基流动对尺寸有严格限制"""
        # sd-turbo 仅支持 512x512；SDXL 支持 1024x1024 或 768x768
        if "turbo" in self.model and "sdxl" not in self.model:
            return "512x512"
        if width >= height:
            return "1024x1024" if width == height else "1024x768"
        return "768x1024"

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

        size = self._get_image_size(width, height)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.model,
            "prompt": prompt,
            "image_size": size,
        }
        if negative:
            data["negative_prompt"] = negative
        if seed:
            data["seed"] = seed

        print(f"🔍 硅基流动请求")
        print(f"🔍 模型: {self.model}, 尺寸: {size}")

        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                resp = requests.post(
                    f"{self.base_url}/images/generations",
                    headers=headers,
                    json=data,
                    timeout=120,
                )

                if resp.status_code == 200:
                    result = resp.json()
                    # 硅基流动返回 data[0].url（临时直链，10分钟有效）
                    img_url = result["data"][0].get("url")
                    if img_url:
                        img_resp = requests.get(img_url, timeout=30)
                        return Image.open(io.BytesIO(img_resp.content))
                    raise Exception(f"无法解析图片URL: {json.dumps(result)[:200]}")

                # 排队/资源不足时 data 为空，等待重试
                if resp.status_code in (429, 500, 503):
                    print(f"⚠️ 状态码 {resp.status_code}，等待重试 ({attempt}/{max_retries})")
                    time.sleep(3 * attempt)
                    continue

                raise Exception(f"硅基流动失败 (状态码 {resp.status_code}): {resp.text[:200]}")

            except requests.exceptions.RequestException as e:
                if attempt == max_retries:
                    raise Exception(f"硅基流动请求失败: {e}")
                time.sleep(2)

        raise Exception("硅基流动生成失败：所有重试已用尽")

    def get_usage(self):
        return {"info": "请登录 https://siliconflow.cn 查看使用量"}

    def get_model(self) -> str:
        return self.model

    def get_name(self) -> str:
        return f"硅基流动 ({self.model})"