# 任务清单：patpat-chatbot-full-stack

## 里程碑 M1：MVP（P0，预估 1-2 天）

### 前置准备：项目初始化（US-01）
- [ ] 创建项目目录结构：`patpat/` 包目录、`patpat/__init__.py`（空文件）、`main.py` 入口文件
- [ ] 编写 `requirements.txt`，包含依赖：`openai`、`rich`、`python-dotenv`
- [ ] 创建 `.env.example`，包含 `OPENAI_API_KEY=your-key-here` 和 `OPENAI_MODEL=gpt-3.5-turbo`
- [ ] 创建 `.gitignore`，排除 `.env`、`__pycache__/`、`*.pyc`、`.patpat/`
- [ ] 验证：执行 `pip install -r requirements.txt` 确认所有依赖安装成功
- [ ] 验证：确认 `.env` 不被 git 追踪

### 核心实施

#### Prompt 模板设计（US-02）
- [ ] 创建 `patpat/prompts.py`，定义 `SYSTEM_PROMPT` 常量，包含角色设定（温暖的倾听者）、回应风格（先共情再引导）、边界约束（不做诊断、不开药）、语言风格（口语化、温柔）
- [ ] 在 `prompts.py` 中定义 `DISCLAIMER` 免责声明常量，说明本工具不替代专业心理咨询
- [ ] 预留 prompt 模板变量支持（如 `{nickname}` 用户昵称占位符）
- [ ] 验证：审查 prompt 内容，确保不会以医生/咨询师身份自居

#### 危机识别模块（US-05）
- [ ] 创建 `patpat/crisis.py`，实现 `CrisisDetector` 类
- [ ] 维护中英文危机关键词列表：自杀、自伤、不想活、想死、割腕、跳楼、suicide、self-harm 等
- [ ] 实现 `detect(text: str) -> bool` 方法，基于关键词匹配检测危机信号
- [ ] 定义求助信息常量 `CRISIS_RESOURCES`，包含多条热线：全国24小时心理援助热线 400-161-9995、北京心理危机研究与干预中心 010-82951332、生命热线 400-821-1215
- [ ] 验证：测试关键词匹配准确性，确保"想死"触发、"想死心塌地学习"等误报场景的处理

#### 对话核心引擎（US-03）
- [ ] 创建 `patpat/bot.py`，实现 `PatPatBot` 类，构造函数初始化 `messages: list[dict]`，首条为 system prompt
- [ ] 实现模型名称从环境变量 `OPENAI_MODEL` 读取，支持运行时切换
- [ ] 实现 `chat(user_input: str)` 方法，调用 OpenAI ChatCompletion API（`stream=True`）实现流式输出
- [ ] 实现滑动窗口机制：保留 system prompt + 最近 20 轮对话（可通过参数配置 `max_rounds`）
- [ ] 集成 `CrisisDetector`：在处理用户消息前调用 `detect()`，触发时在回复前插入求助信息
- [ ] 实现异常处理：捕获 API 超时（`Timeout`）、网络错误（`ConnectionError`）、Key 无效（`AuthenticationError`）等，返回友好提示
- [ ] 验证：模拟多轮对话，确认上下文保持和滑动窗口裁剪正确

#### CLI 交互界面（US-04）
- [ ] 在 `main.py` 中实现主循环：加载 `.env` 配置、初始化 `PatPatBot`、`while True` 循环读取用户输入
- [ ] 使用 `rich` 库实现启动欢迎语：`Panel` 显示欢迎信息和 `DISCLAIMER` 免责声明
- [ ] 实现用户输入提示符 `> `，Bot 回复使用 `rich.Markdown` 渲染并带颜色区分
- [ ] 实现流式输出显示：逐字打印 Bot 回复，使用 `rich.Live` 或逐块刷新
- [ ] 实现命令解析：`/quit` 和 `/exit` 正常退出、`/new` 开始新对话（重置消息历史）
- [ ] 捕获 `KeyboardInterrupt` 和 `EOFError`，显示告别语并优雅退出
- [ ] 验证：手动测试完整对话流程，包括正常对话、命令执行、Ctrl+C 退出

### M1 集成测试
- [ ] 端到端测试：启动程序 → 显示欢迎语 → 多轮对话 → 流式输出 → `/quit` 退出
- [ ] 危机检测测试：输入含危机关键词的消息，确认求助热线信息显示
- [ ] 异常测试：使用无效 API Key 启动，确认错误提示友好

---

## 里程碑 M2：增强功能（P1，预估 2-3 天）

### 对话历史持久化（US-06）
- [ ] 创建 `patpat/storage.py`，实现 `StorageManager` 类
- [ ] 实现存储目录初始化：自动创建 `~/.patpat/history/` 目录
- [ ] 定义 JSON 存储结构：`{ "session_id", "created_at", "updated_at", "messages": [...], "emotion_tags": [...] }`
- [ ] 实现 `save(messages, session_id)` 方法：以 `{timestamp}_{session_id}.json` 命名，支持增量写入（每轮对话后自动保存）
- [ ] 实现 `load(session_id) -> dict` 方法：根据 session_id 加载历史会话
- [ ] 实现 `list_sessions() -> list` 方法：列出所有历史会话摘要（时间、消息数、首条用户消息预览）
- [ ] 在 `main.py` 中集成自动保存：每轮对话后调用 `save()`
- [ ] 在 `main.py` 中集成 `/history` 命令：使用 `rich.Table` 展示历史会话列表
- [ ] 在 `main.py` 中集成 `/load <session_id>` 命令：恢复会话上下文并继续对话
- [ ] 验证：退出后检查 `~/.patpat/history/` 目录下 JSON 文件内容正确；重启后 `/load` 恢复对话

### 情绪标签自动标记（US-07）
- [ ] 定义情绪标签枚举：`焦虑`、`悲伤`、`愤怒`、`恐惧`、`孤独`、`疲惫`、`平静`、`开心`、`感恩`、`其他`
- [ ] 在 `patpat/bot.py` 中扩展：每轮对话后额外调用 LLM（轻量 prompt）对用户消息做情绪分类，返回单个情绪标签
- [ ] 设计情绪分类 prompt：要求 LLM 仅返回枚举中的一个标签，使用结构化输出降低分类难度
- [ ] 将情绪标签写入 `storage.py` 的对话记录中，每条用户消息附带 `emotion` 字段
- [ ] 在 `main.py` 中集成 `/mood` 命令：使用 `rich.Table` 展示当前会话的情绪变化时间线
- [ ] 验证：检查 JSON 文件中每条用户消息是否包含 `emotion` 字段；`/mood` 命令输出正确

### M2 集成测试
- [ ] 端到端测试：多轮对话 → 退出 → 重启 → `/history` 查看列表 → `/load` 恢复会话 → 继续对话
- [ ] 情绪标签测试：对话后检查 JSON 中情绪标签存在且合理；`/mood` 展示正确
- [ ] 边界测试：无历史记录时 `/history` 和 `/mood` 的提示信息友好

---

## 里程碑 M3：Web 化（P2，预估 3-5 天）

### Web 聊天界面（US-08）
- [ ] 在 `requirements.txt` 中新增依赖：`fastapi`、`uvicorn`、`websockets`
- [ ] 创建 `web/app.py`：FastAPI 应用入口，挂载静态文件目录，配置 WebSocket 端点
- [ ] 实现 WebSocket `/ws/chat` 端点：接收用户消息，复用 `PatPatBot` 核心逻辑，流式返回 Bot 回复
- [ ] 实现 Session 管理：基于 WebSocket 连接维护独立的 `PatPatBot` 实例和会话状态
- [ ] 创建 `web/static/index.html`：单页聊天界面，包含消息输入框、发送按钮、聊天气泡区域
- [ ] 创建 `web/static/style.css`：聊天气泡样式，区分用户/Bot 消息，响应式布局
- [ ] 创建 `web/static/chat.js`：WebSocket 连接管理、消息发送/接收、流式渲染 Bot 回复（逐字显示）
- [ ] 实现页面刷新后会话恢复：通过 `StorageManager` 持久化，重连时加载最近会话
- [ ] 集成危机检测：WebSocket 消息处理中调用 `CrisisDetector`，触发时优先推送求助信息
- [ ] 验证：浏览器访问 `http://localhost:8000`，完成多轮对话，刷新页面后历史保留

### 情绪趋势可视化（US-09）
- [ ] 在 `web/app.py` 中新增 REST API `GET /api/emotions/trend`：聚合历史情绪数据，按会话/按天统计各情绪出现频次
- [ ] 处理数据不足场景：少于 3 次会话时返回提示信息
- [ ] 创建 `web/static/trend.js`：使用 Chart.js 渲染情绪趋势折线图/柱状图
- [ ] 在 `index.html` 中新增"情绪趋势"入口按钮/页面，点击后展示图表
- [ ] 验证：多次会话后查看趋势图，数据与 JSON 文件一致

### 多种疏导策略切换（US-10）
- [ ] 在 `patpat/prompts.py` 中新增多套 prompt 模板：`PROMPT_DEFAULT`（通用共情）、`PROMPT_CBT`（认知行为疗法）、`PROMPT_MINDFUL`（正念引导）、`PROMPT_POSITIVE`（积极心理学）
- [ ] 在 `patpat/bot.py` 中新增 `switch_style(style: str)` 方法：替换 system prompt，保留现有对话历史
- [ ] 在 `main.py` 中集成 `/style <name>` 命令：支持 `default`、`cbt`、`mindful`、`positive`，输入无效风格时提示可用选项
- [ ] 在 Web 界面中集成风格切换：下拉菜单或按钮组选择疏导风格
- [ ] 验证：CLI 和 Web 中切换风格后，Bot 回复风格明显变化且对话上下文保留

### M3 集成测试
- [ ] Web 端到端测试：启动服务 → 浏览器对话 → 流式输出 → 刷新恢复 → 危机检测触发
- [ ] 情绪趋势测试：多次会话后图表数据正确，不足 3 次时提示友好
- [ ] 风格切换测试：CLI `/style cbt` 和 Web 界面切换均生效
- [ ] 跨端一致性测试：CLI 和 Web 共享同一存储，历史记录互通
