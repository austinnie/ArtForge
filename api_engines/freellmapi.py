# api_engines/freellmapi.py
"""FreeLLMAPI 引擎 - 聚合 16 家免费 LLM 提供商，~17 亿 token/月"""

import requests
import base64
import io
import time
import json
import random
from PIL import Image


class FreeLLMAPIEngine:
    """
    FreeLLMAPI 引擎

    主要用途：文本/LLM 能力（提示词增强、对话等）
    图像生成：如果路由器后端配置了图像模型，也可调用
    """

    DEFAULT_TEXT_MODEL = "auto"  # 路由器自动选择

    def __init__(self, base_url: str = None, model: str = None, api_key: str = None):
        self.base_url = (base_url or "http://localhost:3000/v1").rstrip("/")
        self.model = model or self.DEFAULT_TEXT_MODEL
        self.api_key = api_key or "freellmapi"  # 本地部署通常不需要真实 Key
        self.last_request_time = 0
        self.min_interval = 0.5

        print(f"🔍 FreeLLMAPI 引擎初始化")
        print(f"🔍 API 地址: {self.base_url}")
        print(f"🔍 模型: {self.model}")

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    # ---------- 文本能力（PromptForge 的 LLM 增强可复用） ----------

    def chat(self, prompt: str, system: str = None, max_tokens: int = 512) -> str:
        """调用 FreeLLMAPI 的 chat/completions"""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }

        resp = requests.post(
            f"{self.base_url}/chat/completions",
            headers=self._headers(),
            json=data,
            timeout=60,
        )
        if resp.status_code != 200:
            raise Exception(f"FreeLLMAPI chat 失败: {resp.text[:200]}")

        result = resp.json()
        return result["choices"][0]["message"]["content"]

    # ---------- 图像能力（如果有后端图像模型） ----------

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
        """尝试通过 FreeLLMAPI 的图像端点生成图片"""

        if seed is None:
            seed = random.randint(1, 2**32 - 1)

        data = {
            "model": self.model,
            "prompt": prompt,
            "n": 1,
            "size": f"{width}x{height}",
            "response_format": "b64_json",
        }
        if seed:
            data["seed"] = seed

        resp = requests.post(
            f"{self.base_url}/images/generations",
            headers=self._headers(),
            json=data,
            timeout=120,
        )

        if resp.status_code != 200:
            raise Exception(f"FreeLLMAPI 图像生成失败: {resp.text[:200]}")

        result = resp.json()
        item = result["data"][0]
        b64 = item.get("b64_json")
        if b64:
            if b64.startswith("data:image"):
                b64 = b64.split(",", 1)[1]
            return Image.open(io.BytesIO(base64.b64decode(b64)))

        img_url = item.get("url")
        if img_url:
            img_resp = requests.get(img_url, timeout=30)
            return Image.open(io.BytesIO(img_resp.content))

        raise Exception("FreeLLMAPI 无法解析图片数据")

    def get_usage(self):
        return {
            "info": "FreeLLMAPI 聚合 16 家免费 LLM，~17 亿 token/月",
            "model": self.model,
        }

    def get_model(self) -> str:
        return self.model

    def get_name(self) -> str:
        return f"FreeLLMAPI ({self.model})"