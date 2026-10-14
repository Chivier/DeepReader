"""Small OpenAI-compatible adapter for the review pipeline."""
import os
from openai import OpenAI
from reader.paths import PROJECT_ROOT  # Loads .env before settings.

class SimpleChatModel:
    def __init__(self, model=None):
        self.model = model or os.getenv("DEEPREADER_MODEL_NAME", "gpt-4.1")

    def chat(self, prompt):
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL") or None,
            timeout=120,
            max_retries=2,
        )
        response = client.chat.completions.create(
            model=self.model, messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("模型未返回内容，请检查模型配置后重试")
        return content
