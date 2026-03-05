const trendBtn = document.getElementById("trendBtn");
const trendModal = document.getElementById("trendModal");
const closeTrend = document.getElementById("closeTrend");
const trendBody = document.getElementById("trendBody");

let trendChart = null;

trendBtn.addEventListener("click", async () => {
    trendModal.classList.remove("hidden");
    try {
        const res = await fetch("/api/emotions/trend");
        const json = await res.json();
        if (json.status === "insufficient") {
            trendBody.innerHTML = `<p style="text-align:center;color:#888;padding:40px 0;">${json.message}</p>`;
            return;
        }
        trendBody.innerHTML = '<canvas id="trendChart"></canvas>';
        renderChart(json.data);
    } catch (e) {
        trendBody.innerHTML = '<p style="text-align:center;color:red;">加载失败</p>';
    }
});

closeTrend.addEventListener("click", () => {
    trendModal.classList.add("hidden");
});

trendModal.addEventListener("click", (e) => {
    if (e.target === trendModal) trendModal.classList.add("hidden");
});

function renderChart(data) {
    const labels = data.map((d) => d.created_at);
    const emotionTypes = ["焦虑", "悲伤", "愤怒", "恐惧", "孤独", "疲惫", "平静", "开心", "感恩", "其他"];
    const colors = ["#ef5350", "#5c6bc0", "#d32f2f", "#7b1fa2", "#455a64", "#78909c", "#66bb6a", "#fdd835", "#ff8a65", "#bdbdbd"];

    const datasets = emotionTypes.map((emotion, i) => ({
        label: emotion,
        data: data.map((d) => d.emotions[emotion] || 0),
        borderColor: colors[i],
        backgroundColor: colors[i] + "33",
        tension: 0.3,
        fill: false,
    })).filter((ds) => ds.data.some((v) => v > 0));

    const ctx = document.getElementById("trendChart").getContext("2d");
    if (trendChart) trendChart.destroy();
    trendChart = new Chart(ctx, {
        type: "line",
        data: { labels, datasets },
        options: {
            responsive: true,
            plugins: { legend: { position: "bottom" } },
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1 } },
            },
        },
    });
}
