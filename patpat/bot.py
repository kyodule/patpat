import os
from openai import OpenAI, APIConnectionError, AuthenticationError, APITimeoutError
from patpat.prompts import SYSTEM_PROMPT, STYLE_MAP, EMOTION_CLASSIFY_PROMPT
from patpat.crisis import CrisisDetector, CRISIS_RESOURCES


class PatPatBot:
    def __init__(self, max_rounds: int = 20, nickname: str = "你"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.max_rounds = max_rounds
        self.nickname = nickname
        self.crisis_detector = CrisisDetector()
        self.style = "default"
        self._init_messages(SYSTEM_PROMPT)

    def _init_messages(self, system_prompt: str):
        prompt = system_prompt.replace("{nickname}", self.nickname)
        self.messages = [{"role": "system", "content": prompt}]

    def reset(self):
        self._init_messages(STYLE_MAP.get(self.style, SYSTEM_PROMPT))

    def switch_style(self, style: str) -> bool:
        if style not in STYLE_MAP:
            return False
        self.style = style
        prompt = STYLE_MAP[style].replace("{nickname}", self.nickname)
        self.messages[0] = {"role": "system", "content": prompt}
        return True

    def load_messages(self, messages: list[dict]):
        self.messages = messages

    def _trim_messages(self):
        if len(self.messages) <= 1:
            return
        max_items = self.max_rounds * 2
        if len(self.messages) - 1 > max_items:
            self.messages = [self.messages[0]] + self.messages[-(max_items):]

    def check_crisis(self, text: str) -> bool:
        return self.crisis_detector.detect(text)

    def chat(self, user_input: str):
        self.messages.append({"role": "user", "content": user_input})
        self._trim_messages()
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                stream=True,
            )
            full_response = ""
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    full_response += delta.content
                    yield delta.content
            self.messages.append({"role": "assistant", "content": full_response})
        except AuthenticationError:
            yield "\n[错误] API Key 无效，请检查 .env 文件中的 OPENAI_API_KEY 配置。"
        except APIConnectionError:
            yield "\n[错误] 网络连接失败，请检查网络设置。"
        except APITimeoutError:
            yield "\n[错误] 请求超时，请稍后重试。"
        except Exception as e:
            yield f"\n[错误] 发生未知错误：{e}"

    def classify_emotion(self, user_message: str) -> str:
        prompt = EMOTION_CLASSIFY_PROMPT.format(message=user_message)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0,
            )
            tag = response.choices[0].message.content.strip()
            valid = ["焦虑", "悲伤", "愤怒", "恐惧", "孤独", "疲惫", "平静", "开心", "感恩", "其他"]
            return tag if tag in valid else "其他"
        except Exception:
            return "其他"
