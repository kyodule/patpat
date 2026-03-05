

Let me first read the PRD document and understand the project context.

好的，以下是基于 PRD 拆解的完整 User Story 列表和实施方案。

---

# PatPat User Story 拆解

## US-01: 项目初始化与工程脚手架

**标题：** 项目基础工程搭建

**用户故事：** As a 开发者, I want 一个结构清晰、依赖完整的项目骨架, So that 后续功能开发有统一的基础。

**验收标准：**
- Given 项目仓库为空, When 执行 `pip install -r requirements.txt`, Then 所有依赖安装成功
- Given `.env.example` 存在, When 开发者复制为 `.env` 并填入 API Key, Then 程序可读取配置
- Given `.gitignore` 存在, When 执行 `git status`, Then `.env` 文件不会被追踪

**优先级：** P0
**Story Points：** 1
**依赖关系：** 无
**技术实现要点：**
- 创建项目目录结构：`patpat/` 包、`main.py` 入口
- `requirements.txt`：`openai`, `rich`, `python-dotenv`
- `.env.example`：`OPENAI_API_KEY=your-key-here`, `OPENAI_MODEL=gpt-3.5-turbo`
- `.gitignore`：`.env`, `__pycache__/`, `*.pyc`, `.patpat/`
- `patpat/__init__.py`：空文件

**涉及文件：** `.env.example`, `.gitignore`, `requirements.txt`, `patpat/__init__.py`

---

## US-02: 心理疏导 System Prompt 设计

**标题：** 共情式心理疏导 Prompt 模板

**用户故事：** As a 用户, I want Bot 以温暖、共情的方式回应我的倾诉, So that 我感到被理解和支持。

**验收标准：**
- Given System Prompt 已配置, When 用户输入"我今天很难过", Then Bot 回复包含共情表达（如"我能感受到..."），而非冷冰冰的建议
- Given System Prompt 已配置, When 用户输入任何内容, Then Bot 不会以医生/咨询师身份自居，不做诊断
- Given Prompt 模板文件存在, When 需要调整 Bot 风格, Then 只需修改 `prompts.py` 而无需改动其他代码

**优先级：** P0
**Story Points：** 2
**依赖关系：** US-01
**技术实现要点：**
- `patpat/prompts.py` 中定义 `SYSTEM_PROMPT` 常量
- Prompt 要点：角色设定（温暖的倾听者）、回应风格（先共情再引导）、边界约束（不做诊断、不开药）、语言风格（口语化、温柔）
- 预留 prompt 模板变量支持（如用户昵称）
- 加入免责声明提示语常量 `DISCLAIMER`

**涉及文件：** `patpat/prompts.py`

---

## US-03: LLM 对话核心引擎

**标题：** 多轮对话与流式输出

**用户故事：** As a 用户, I want 与 Bot 进行连续多轮对话并实时看到回复, So that 对话体验流畅自然。

**验收标准：**
- Given Bot 已初始化, When 用户连续发送 3 条消息, Then 每次回复都能理解之前的对话上下文
- Given 用户发送消息, When LLM 开始响应, Then 回复以流式方式逐字显示，而非等待全部生成后一次性输出
- Given 对话进行中, When 消息历史超过 token 限制, Then 自动裁剪早期消息，保留最近 N 轮

**优先级：** P0
**Story Points：** 3
**依赖关系：** US-01, US-02
**技术实现要点：**
- `patpat/bot.py` 封装 `PatPatBot` 类
- 内部维护 `messages: list[dict]`，首条为 system prompt
- 调用 `openai.ChatCompletion.create(stream=True)` 实现流式输出
- 实现滑动窗口：保留 system prompt + 最近 20 轮对话（可配置）
- 模型名称从环境变量读取，支持切换
- 异常处理：API 超时、网络错误、Key 无效等场景

**涉及文件：** `patpat/bot.py`

---

## US-04: CLI 交互界面

**标题：** 终端聊天交互界面

**用户故事：** As a 用户, I want 在终端中通过简单命令启动 Bot 并开始对话, So that 我能快速方便地使用。

**验收标准：**
- Given 环境配置完成, When 执行 `python main.py`, Then 显示欢迎语和免责声明，进入对话模式
- Given 对话进行中, When 用户输入文字并回车, Then Bot 回复以美化格式显示（区分用户/Bot 消息）
- Given 对话进行中, When 用户按 Ctrl+C, Then 显示告别语并优雅退出，不抛出异常
- Given 对话进行中, When 用户输入 `/quit` 或 `/exit`, Then 正常结束对话

**优先级：** P0
**Story Points：** 2
**依赖关系：** US-03
**技术实现要点：**
- `main.py` 作为入口，`while True` 循环读取输入
- 使用 `rich` 库：`Console` 输出美化、`Markdown` 渲染 Bot 回复、`Panel` 显示欢迎/免责信息
- 用户输入前缀 `> `，Bot 回复带颜色区分
- 捕获 `KeyboardInterrupt` 和 `EOFError`
- 支持命令：`/quit`, `/exit`, `/new`（开始新对话）

**涉及文件：** `main.py`

---

## US-05: 危机识别与安全转介

**标题：** 心理危机关键词检测与求助引导

**用户故事：** As a 用户, I want 在我表达出严重心理危机时 Bot 能识别并引导我寻求专业帮助, So that 我的安全得到保障。

**验收标准：**
- Given 用户输入包含"想死"、"自杀"、"不想活了"等关键词, When 消息发送后, Then Bot 回复前先显示醒目的求助热线信息（全国24小时心理援助热线：400-161-9995）
- Given 危机检测触发, When Bot 继续回复, Then 回复内容包含温暖的关怀，而非机械的警告
- Given 用户输入不包含危机关键词, When 消息发送后, Then 不显示求助信息，正常对话

**优先级：** P0（PRD 中标为 P1，但安全底线应提升至 P0）
**Story Points：** 2
**依赖关系：** US-01
**技术实现要点：**
- `patpat/crisis.py` 实现 `CrisisDetector` 类
- 维护关键词列表（中英文）：自杀、自伤、不想活、想死、割腕、跳楼等
- `detect(text: str) -> bool` 方法，基于关键词匹配
- 求助信息常量：包含多条热线（全国心理援助热线、北京心理危机研究与干预中心、生命热线等）
- 在 `bot.py` 中调用：用户消息发送前先检测，触发时在 Bot 回复前插入求助信息

**涉及文件：** `patpat/crisis.py`, `patpat/bot.py`（集成调用）

---

## US-06: 对话历史持久化

**标题：** 对话记录本地存储与恢复

**用户故事：** As a 用户, I want 我的对话记录被保存到本地, So that 下次打开时可以继续之前的对话。

**验收标准：**
- Given 对话结束（退出程序）, When 检查 `~/.patpat/history/` 目录, Then 存在以时间戳命名的 JSON 文件，包含完整对话记录
- Given 存在历史对话文件, When 启动程序并输入 `/history`, Then 显示历史会话列表
- Given 用户选择某个历史会话, When 输入 `/load <session_id>`, Then 恢复该会话上下文并可继续对话

**优先级：** P1
**Story Points：** 3
**依赖关系：** US-03, US-04
**技术实现要点：**
- `patpat/storage.py` 实现 `StorageManager` 类
- 存储路径：`~/.patpat/history/{timestamp}_{session_id}.json`
- JSON 结构：`{ "session_id", "created_at", "updated_at", "messages": [...], "emotion_tags": [...] }`
- `save(messages, session_id)` / `load(session_id)` / `list_sessions()` 方法
- 自动保存：每轮对话后增量写入，而非仅退出时保存
- `main.py` 中集成 `/history`, `/load` 命令

**涉及文件：** `patpat/storage.py`, `main.py`（集成命令）

---

## US-07: 情绪标签自动标记

**标题：** 对话情绪自动识别与标记

**用户故事：** As a 用户, I want Bot 能自动识别我每轮对话的情绪, So that 我可以回顾自己的情绪变化。

**验收标准：**
- Given 用户发送一条消息, When Bot 处理后, Then 该轮对话被标记一个情绪标签（如：焦虑、悲伤、愤怒、平静、开心）
- Given 对话历史已保存, When 查看 JSON 文件, Then 每条用户消息附带 `emotion` 字段
- Given 用户输入 `/mood`, When 命令执行, Then 显示当前会话的情绪变化轨迹

**优先级：** P1
**Story Points：** 3
**依赖关系：** US-03, US-06
**技术实现要点：**
- 在 `patpat/bot.py` 中扩展：每轮对话后，额外调用 LLM（轻量 prompt）对用户消息做情绪分类
- 情绪标签枚举：`焦虑`, `悲伤`, `愤怒`, `恐惧`, `孤独`, `疲惫`, `平静`, `开心`, `感恩`, `其他`
- 或者：在 system prompt 中要求 Bot 回复时附带结构化情绪标签（JSON 格式），解析后分离
- 标签存入 `storage.py` 的对话记录中
- `/mood` 命令：用 `rich` 表格展示情绪时间线

**涉及文件：** `patpat/bot.py`, `patpat/storage.py`, `main.py`

---

## US-08: Web 聊天界面

**标题：** 浏览器端聊天 UI

**用户故事：** As a 用户, I want 通过浏览器访问 PatPat, So that 我不需要使用终端也能对话。

**验收标准：**
- Given 服务已启动, When 浏览器访问 `http://localhost:8000`, Then 显示聊天界面
- Given 聊天界面已加载, When 用户输入消息并发送, Then Bot 回复以流式方式逐字显示在界面上
- Given 对话进行中, When 刷新页面, Then 当前会话对话历史仍然保留

**优先级：** P2
**Story Points：** 5
**依赖关系：** US-03, US-05, US-06
**技术实现要点：**
- 后端：FastAPI + WebSocket 实现流式通信
- 前端：单页 HTML + 原生 JS（或轻量框架），聊天气泡 UI
- 复用 `patpat/bot.py` 核心逻辑
- Session 管理：基于 WebSocket 连接维护会话
- 新增文件：`web/app.py`（FastAPI 入口）、`web/static/index.html`、`web/static/chat.js`、`web/static/style.css`

**涉及文件：** `web/app.py`, `web/static/index.html`, `web/static/chat.js`, `web/static/style.css`

---

## US-09: 情绪趋势可视化

**标题：** 情绪变化趋势图表

**用户故事：** As a 用户, I want 看到我过去一段时间的情绪变化趋势图, So that 我能更好地了解自己的情绪模式。

**验收标准：**
- Given 存在多次会话的情绪标签数据, When 用户在 Web 界面点击"情绪趋势", Then 显示折线图/柱状图展示情绪随时间的变化
- Given 情绪数据不足（少于 3 次会话）, When 查看趋势, Then 提示"数据不足，继续对话后可查看趋势"

**优先级：** P2
**Story Points：** 3
**依赖关系：** US-07, US-08
**技术实现要点：**
- 后端：新增 API `/api/emotions/trend`，聚合历史情绪数据
- 前端：使用 Chart.js 渲染图表
- 数据聚合：按天/按会话统计各情绪出现频次
- 新增文件：`web/static/trend.js`

**涉及文件：** `web/app.py`（新增 API）, `web/static/trend.js`, `web/static/index.html`（新增页面入口）

---

## US-10: 多种疏导策略切换

**标题：** 支持 CBT/正念等多种疏导风格

**用户故事：** As a 用户, I want 根据自己的需要选择不同的疏导风格, So that 我能获得最适合当前状态的帮助。

**验收标准：**
- Given 对话进行中, When 用户输入 `/style cbt`, Then Bot 切换为认知行为疗法风格回应
- Given 对话进行中, When 用户输入 `/style mindful`, Then Bot 切换为正念引导风格
- Given 用户未指定风格, When 开始对话, Then 默认使用通用共情风格

**优先级：** P2
**Story Points：** 2
**依赖关系：** US-02, US-03
**技术实现要点：**
- `patpat/prompts.py` 中新增多套 prompt 模板：`PROMPT_DEFAULT`, `PROMPT_CBT`, `PROMPT_MINDFUL`, `PROMPT_POSITIVE`
- `bot.py` 新增 `switch_style(style: str)` 方法，替换 system prompt 并保留对话历史
- `main.py` 中集成 `/style` 命令
- 可扩展：后续可通过配置文件加载自定义 prompt

**涉及文件：** `patpat/prompts.py`, `patpat/bot.py`, `main.py`

---

# 依赖关系图

```
US-01 (项目初始化)
  ├── US-02 (Prompt 设计)
  │     └── US-10 (多种疏导策略) [P2]
  ├── US-05 (危机识别)
  └── US-03 (对话引擎)
        ├── US-04 (CLI 界面)
        │     └── US-06 (历史持久化) [P1]
        │           └── US-07 (情绪标签) [P1]
        └── US-08 (Web UI) [P2]
              └── US-09 (情绪可视化) [P2]
```

# 工作量汇总

| Story | Points | 优先级 | 里程碑 |
|-------|--------|--------|--------|
| US-01 项目初始化 | 1 | P0 | M1 |
| US-02 Prompt 设计 | 2 | P0 | M1 |
| US-03 对话引擎 | 3 | P0 | M1 |
| US-04 CLI 界面 | 2 | P0 | M1 |
| US-05 危机识别 | 2 | P0 | M1 |
| US-06 历史持久化 | 3 | P1 | M2 |
| US-07 情绪标签 | 3 | P1 | M2 |
| US-08 Web UI | 5 | P2 | M3 |
| US-09 情绪可视化 | 3 | P2 | M3 |
| US-10 疏导策略 | 2 | P2 | M3 |
| **合计** | **26** | | |

# 风险评估

| 风险 | 影响 Story | 等级 | 应对 |
|------|-----------|------|------|
| LLM 输出有害内容 | US-02, US-03 | 高 | Prompt 严格约束 + US-05 危机检测兜底 |
| 用户误认为专业咨询 | US-04 | 中 | 启动免责声明 + Prompt 中明确角色边界 |
| API Key 泄露 | US-01 | 中 | `.env` + `.gitignore`，代码审查 |
| 上下文 token 超限 | US-03 | 低 | 滑动窗口裁剪，可配置保留轮数 |
| 情绪分类准确度不足 | US-07 | 中 | 使用结构化输出 + 有限枚举，降低分类难度 |
| Web UI 安全性 | US-08 | 中 | 仅本地访问，不暴露公网；后续可加认证 |

# 建议实施顺序

M1（MVP，10 Story Points）：US-01 → US-02 → US-05 → US-03 → US-04，按此顺序串行开发，预估 1-2 天。

M2（增强，6 Story Points）：US-06 → US-07，预估 2-3 天。

M3（Web 化，10 Story Points）：US-08 → US-09 + US-10 并行，预估 3-5 天。