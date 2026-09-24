# api_engines/free_multimodal_proxy.py
"""Free Multimodal Proxy 图像生成引擎 - InferencePort AI 免费代理"""

import os
import requests
import base64
import io
import time
import json
import random
from PIL import Image


class FreeMultimodalProxyEngine:
    """Free Multimodal Proxy 引擎（无需注册，无需 API Key）"""

    # 常用模型（来自 /v1/models 缓存列表）
    DEFAULT_MODEL = "zimage"
    AVAILABLE_MODELS = [
        "zimage", "flux", "gpt-image", "seedream", "qwen-image",
        "ideogram", "imagen", "wan",
    ]

    def __init__(self, base_url: str = None, model: str = None, proxy_token: str = None):
        self.base_url = (base_url or "http://localhost:8080/v1").rstrip("/")
        self.model = model or self.DEFAULT_MODEL
        self.proxy_token = proxy_token  # 可选，公开部署时的 Bearer Token
        self.last_request_time = 0
        self.min_interval = 1.0

        print(f"🔍 Free Multimodal Proxy 引擎初始化")
        print(f"🔍 API 地址: {self.base_url}")
        print(f"🔍 当前模型: {self.model}")

    def _headers(self) -> dict:
        h = {"Content-Type": "application/json"}
        if self.proxy_token:
            h["Authorization"] = f"Bearer {self.proxy_token}"
        return h

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

        # 限速
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)

        data = {
            "model": self.model,
            "prompt": prompt,
            "n": 1,
            "size": f"{width}x{height}",
            "response_format": "b64_json",
        }
        if seed:
            data["seed"] = seed

        url = f"{self.base_url}/images/generations"
        print(f"🔍 Free Multimodal Proxy 请求")
        print(f"🔍 模型: {self.model}, 尺寸: {width}x{height}")

        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                response = requests.post(
                    url, headers=self._headers(), json=data, timeout=120
                )
                self.last_request_time = time.time()

                if response.status_code == 200:
                    result = response.json()
                    item = result["data"][0]

                    # 优先 b64_json
                    b64 = item.get("b64_json")
                    if b64:
                        if b64.startswith("data:image"):
                            b64 = b64.split(",", 1)[1]
                        return Image.open(io.BytesIO(base64.b64decode(b64)))

                    # 兜底 url
                    img_url = item.get("url")
                    if img_url:
                        img_resp = requests.get(img_url, timeout=30)
                        return Image.open(io.BytesIO(img_resp.content))

                    raise Exception(f"无法解析图片数据: {json.dumps(result)[:200]}")

                # 429/5xx 重试
                if response.status_code in (429, 500, 502, 503, 504):
                    print(f"⚠️ 状态码 {response.status_code}，重试 ({attempt}/{max_retries})")
                    time.sleep(2 * attempt)
                    continue

                raise Exception(
                    f"Free Multimodal Proxy 失败 (状态码 {response.status_code}): "
                    f"{response.text[:200]}"
                )

            except requests.exceptions.RequestException as e:
                if attempt == max_retries:
                    raise Exception(f"Free Multimodal Proxy 请求失败: {e}")
                print(f"⚠️ 请求异常 ({attempt}/{max_retries}): {e}")
                time.sleep(2)

        raise Exception("Free Multimodal Proxy 生成失败：所有重试已用尽")

    def get_usage(self):
        return {
            "info": "Free Multimodal Proxy 无需注册和 API Key，基于 InferencePort AI",
            "model": self.model,
            "available_models": self.AVAILABLE_MODELS,
        }

    def get_model(self) -> str:
        return self.model

    def get_name(self) -> str:
        return f"Free Multimodal Proxy ({self.model})"