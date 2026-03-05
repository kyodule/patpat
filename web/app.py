import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from patpat.bot import PatPatBot
from patpat.crisis import CrisisDetector, CRISIS_RESOURCES
from patpat.storage import StorageManager

load_dotenv()

app = FastAPI(title="PatPat")
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

storage = StorageManager()
crisis_detector = CrisisDetector()


@app.get("/")
async def index():
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "index.html"))


@app.get("/api/emotions/trend")
async def emotion_trend():
    sessions = storage.list_sessions()
    if len(sessions) < 3:
        return {"status": "insufficient", "message": "数据不足，继续对话后可查看趋势（至少需要3次会话）"}
    trend = []
    for s in reversed(sessions):
        data = storage.load(s["session_id"])
        if data is None:
            continue
        tags = data.get("emotion_tags", [])
        counts = {}
        for t in tags:
            e = t.get("emotion", "其他")
            counts[e] = counts.get(e, 0) + 1
        trend.append({
            "session_id": s["session_id"],
            "created_at": data.get("created_at", "")[:10],
            "emotions": counts,
        })
    return {"status": "ok", "data": trend}


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    bot = PatPatBot()
    session_id = storage.new_session_id()
    emotion_tags = []

    await websocket.send_json({"type": "session", "session_id": session_id})

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "message")

            if msg_type == "load_session":
                target_id = data.get("session_id", "")
                session_data = storage.load(target_id)
                if session_data:
                    bot.load_messages(session_data["messages"])
                    session_id = target_id
                    emotion_tags = session_data.get("emotion_tags", [])
                    history = [m for m in session_data["messages"] if m["role"] != "system"]
                    await websocket.send_json({"type": "history", "messages": history})
                else:
                    await websocket.send_json({"type": "error", "content": f"未找到会话 {target_id}"})
                continue

            if msg_type == "switch_style":
                style = data.get("style", "default")
                if bot.switch_style(style):
                    await websocket.send_json({"type": "info", "content": f"已切换到 {style} 风格"})
                else:
                    await websocket.send_json({"type": "error", "content": "未知风格"})
                continue

            user_input = data.get("content", "").strip()
            if not user_input:
                continue

            # Crisis detection
            if crisis_detector.detect(user_input):
                await websocket.send_json({"type": "crisis", "content": CRISIS_RESOURCES})

            # Stream response
            await websocket.send_json({"type": "stream_start"})
            for chunk in bot.chat(user_input):
                await websocket.send_json({"type": "stream", "content": chunk})
            await websocket.send_json({"type": "stream_end"})

            # Emotion classification
            try:
                emotion = bot.classify_emotion(user_input)
            except Exception:
                emotion = "其他"
            emotion_tags.append({"message": user_input, "emotion": emotion})
            await websocket.send_json({"type": "emotion", "emotion": emotion})

            storage.save(bot.messages, session_id, emotion_tags)

    except WebSocketDisconnect:
        storage.save(bot.messages, session_id, emotion_tags)
