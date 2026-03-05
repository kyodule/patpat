from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.live import Live

from patpat.bot import PatPatBot
from patpat.crisis import CRISIS_RESOURCES
from patpat.prompts import DISCLAIMER, STYLE_MAP
from patpat.storage import StorageManager


console = Console()
storage = StorageManager()


def show_welcome():
    console.print(Panel(
        "[bold green]欢迎来到拍拍 (PatPat) 🤗[/bold green]\n\n"
        "我是你的倾听伙伴，随时准备陪你聊聊。\n"
        "输入你想说的话，按回车发送。\n\n"
        "可用命令：\n"
        "  /quit 或 /exit - 退出\n"
        "  /new - 开始新对话\n"
        "  /history - 查看历史会话\n"
        "  /load <id> - 加载历史会话\n"
        "  /mood - 查看当前情绪轨迹\n"
        "  /style <name> - 切换风格 (default/cbt/mindful/positive)",
        title="拍拍 PatPat",
        border_style="cyan",
    ))
    console.print(Panel(DISCLAIMER, border_style="yellow"))


def show_history():
    sessions = storage.list_sessions()
    if not sessions:
        console.print("[yellow]暂无历史会话记录。[/yellow]")
        return
    table = Table(title="历史会话", border_style="cyan")
    table.add_column("Session ID", style="green")
    table.add_column("创建时间", style="white")
    table.add_column("消息数", justify="right")
    table.add_column("预览", style="dim")
    for s in sessions:
        table.add_row(s["session_id"], s["created_at"][:19], str(s["message_count"]), s["preview"])
    console.print(table)


def show_mood(emotion_tags: list[dict]):
    if not emotion_tags:
        console.print("[yellow]当前会话暂无情绪记录。[/yellow]")
        return
    table = Table(title="情绪轨迹", border_style="cyan")
    table.add_column("#", justify="right", style="dim")
    table.add_column("消息", style="white")
    table.add_column("情绪", style="green")
    for i, tag in enumerate(emotion_tags, 1):
        table.add_row(str(i), tag.get("message", "")[:40], tag.get("emotion", "其他"))
    console.print(table)


def main():
    load_dotenv()
    bot = PatPatBot()
    session_id = storage.new_session_id()
    emotion_tags = []

    show_welcome()

    while True:
        try:
            user_input = console.input("[bold blue]> [/bold blue]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[cyan]拍拍陪你到这里，下次再聊哦，照顾好自己~ 👋[/cyan]")
            storage.save(bot.messages, session_id, emotion_tags)
            break

        if not user_input:
            continue

        if user_input in ("/quit", "/exit"):
            console.print("[cyan]拍拍陪你到这里，下次再聊哦，照顾好自己~ 👋[/cyan]")
            storage.save(bot.messages, session_id, emotion_tags)
            break

        if user_input == "/new":
            storage.save(bot.messages, session_id, emotion_tags)
            bot.reset()
            session_id = storage.new_session_id()
            emotion_tags = []
            console.print("[green]已开始新对话。[/green]")
            continue

        if user_input == "/history":
            show_history()
            continue

        if user_input.startswith("/load "):
            target_id = user_input[6:].strip()
            data = storage.load(target_id)
            if data is None:
                console.print(f"[red]未找到会话 {target_id}[/red]")
            else:
                bot.load_messages(data["messages"])
                session_id = data["session_id"]
                emotion_tags = data.get("emotion_tags", [])
                console.print(f"[green]已恢复会话 {target_id}，可以继续对话。[/green]")
            continue

        if user_input == "/mood":
            show_mood(emotion_tags)
            continue

        if user_input.startswith("/style "):
            style_name = user_input[7:].strip()
            if bot.switch_style(style_name):
                console.print(f"[green]已切换到 {style_name} 风格。[/green]")
            else:
                console.print(f"[red]未知风格。可选：{', '.join(STYLE_MAP.keys())}[/red]")
            continue

        if user_input.startswith("/"):
            console.print("[yellow]未知命令。输入 /quit 退出，/new 新对话。[/yellow]")
            continue

        # Crisis detection
        if bot.check_crisis(user_input):
            console.print(Panel(CRISIS_RESOURCES, border_style="red bold", title="紧急求助信息"))

        # Stream bot response
        console.print()
        full_response = ""
        with Live("", console=console, refresh_per_second=15) as live:
            for chunk in bot.chat(user_input):
                full_response += chunk
                live.update(Markdown(full_response))
        console.print()

        # Emotion classification (async-like, after response)
        try:
            emotion = bot.classify_emotion(user_input)
        except Exception:
            emotion = "其他"
        emotion_tags.append({"message": user_input, "emotion": emotion})

        # Auto-save after each round
        storage.save(bot.messages, session_id, emotion_tags)


if __name__ == "__main__":
    main()
