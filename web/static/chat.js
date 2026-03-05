const chatArea = document.getElementById("chatArea");
const chatForm = document.getElementById("chatForm");
const msgInput = document.getElementById("msgInput");
const sendBtn = document.getElementById("sendBtn");
const styleSelect = document.getElementById("styleSelect");

let ws = null;
let currentBubble = null;
let sessionId = null;

function connect() {
    const proto = location.protocol === "https:" ? "wss:" : "ws:";
    ws = new WebSocket(`${proto}//${location.host}/ws/chat`);

    ws.onopen = () => { sendBtn.disabled = false; };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        switch (data.type) {
            case "session":
                sessionId = data.session_id;
                break;
            case "history":
                chatArea.innerHTML = "";
                data.messages.forEach((m) => {
                    addBubble(m.content, m.role === "user" ? "user" : "bot");
                });
                scrollBottom();
                break;
            case "crisis":
                addBubble(data.content, "crisis");
                scrollBottom();
                break;
            case "stream_start":
                currentBubble = addBubble("", "bot");
                break;
            case "stream":
                if (currentBubble) {
                    currentBubble.textContent += data.content;
                    scrollBottom();
                }
                break;
            case "stream_end":
                currentBubble = null;
                sendBtn.disabled = false;
                msgInput.disabled = false;
                break;
            case "emotion":
                const tag = document.createElement("div");
                tag.className = "emotion-tag";
                tag.textContent = `情绪: ${data.emotion}`;
                chatArea.appendChild(tag);
                scrollBottom();
                break;
            case "info":
                addBubble(data.content, "bot");
                scrollBottom();
                break;
            case "error":
                addBubble(`[错误] ${data.content}`, "bot");
                scrollBottom();
                break;
        }
    };

    ws.onclose = () => {
        sendBtn.disabled = true;
        setTimeout(connect, 2000);
    };
}

function addBubble(text, type) {
    const welcome = chatArea.querySelector(".welcome-msg");
    if (welcome) welcome.remove();
    const div = document.createElement("div");
    div.className = `bubble ${type}`;
    div.textContent = text;
    chatArea.appendChild(div);
    return div;
}

function scrollBottom() {
    chatArea.scrollTop = chatArea.scrollHeight;
}

chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const text = msgInput.value.trim();
    if (!text || !ws || ws.readyState !== WebSocket.OPEN) return;
    addBubble(text, "user");
    scrollBottom();
    ws.send(JSON.stringify({ type: "message", content: text }));
    msgInput.value = "";
    sendBtn.disabled = true;
    msgInput.disabled = true;
});

styleSelect.addEventListener("change", () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "switch_style", style: styleSelect.value }));
    }
});

connect();
