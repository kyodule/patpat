import re


CRISIS_KEYWORDS = [
    "自杀", "自伤", "自残", "不想活", "想死", "去死",
    "割腕", "跳楼", "跳河", "跳桥", "上吊", "吞药",
    "活不下去", "活着没意思", "生无可恋", "了结自己",
    "不想活了", "死了算了", "想去死", "寻死",
    "suicide", "self-harm", "self harm", "kill myself",
    "end my life", "want to die", "wanna die",
]

# Patterns that contain crisis keywords but are NOT actual crisis signals
FALSE_POSITIVE_PATTERNS = [
    re.compile(r"想死心塌地"),
    re.compile(r"想死心"),
    re.compile(r"笑死"),
    re.compile(r"气死"),
    re.compile(r"累死"),
    re.compile(r"饿死"),
    re.compile(r"渴死"),
    re.compile(r"热死"),
    re.compile(r"冷死"),
    re.compile(r"无聊死"),
    re.compile(r"丑死"),
    re.compile(r"烦死"),
]

CRISIS_RESOURCES = (
    "\n╔══════════════════════════════════════════════════════╗\n"
    "║  💛 你并不孤单，有人愿意倾听你                      ║\n"
    "║                                                      ║\n"
    "║  全国24小时心理援助热线：400-161-9995                ║\n"
    "║  北京心理危机研究与干预中心：010-82951332            ║\n"
    "║  生命热线：400-821-1215                              ║\n"
    "║  希望24热线：400-161-9995                            ║\n"
    "║                                                      ║\n"
    "║  如果你正处于危险中，请立即拨打 120 或 110           ║\n"
    "╚══════════════════════════════════════════════════════╝\n"
)


class CrisisDetector:
    def __init__(self):
        self.keywords = CRISIS_KEYWORDS

    def detect(self, text: str) -> bool:
        text_lower = text.lower().strip()
        for pattern in FALSE_POSITIVE_PATTERNS:
            if pattern.search(text_lower):
                text_lower = pattern.sub("", text_lower)
        for keyword in self.keywords:
            if keyword in text_lower:
                return True
        return False
