const symbols = ["ACME", "GLOBEX", "INITECH", "Hooli"];
const HISTORY_LENGTH = 100;
const priceHistory = {};
const dashboard = document.getElementById("dashboard");
const charts = {};

symbols.forEach((symbol) => {
  const container = document.createElement("div");
  container.className = "chart-box";
  container.innerHTML = `
        <h3>${symbol}</h3>
        <canvas id="chart-${symbol}"></canvas>
      `;
  dashboard.appendChild(container);

  const ctx = container.querySelector("canvas").getContext("2d");
  priceHistory[symbol] = Array(HISTORY_LENGTH).fill(100.0);
  charts[symbol] = new Chart(ctx, {
    type: "line",
    data: {
      labels: Array(HISTORY_LENGTH).fill(""),
      datasets: [
        {
          label: symbol,
          data: priceHistory[symbol],
          borderColor: "#0000cc",
          borderWidth: 2,
          fill: false,
          tension: 0.2,
          pointRadius: 0,
        },
      ],
    },
    options: {
      animation: false,
      responsive: true,
      scales: {
        x: { display: false },
        y: {
          beginAtZero: false,
          ticks: { precision: 2 },
        },
      },
      plugins: {
        legend: { display: false },
      },
    },
  });
});

const WS_HOST = window.location.hostname;
const WS_PORT = "8765";
const ws = new WebSocket(`ws://${WS_HOST}:${WS_PORT}`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  symbols.forEach((symbol) => {
    const price = data[symbol];
    if (price !== undefined) {
      priceHistory[symbol].push(price);
      if (priceHistory[symbol].length > HISTORY_LENGTH) {
        priceHistory[symbol].shift();
      }
      charts[symbol].data.datasets[0].data = [...priceHistory[symbol]];
      charts[symbol].update();
    }
  });
};

ws.onerror = (e) => console.error("WebSocket error:", e);
ws.onclose = () => console.warn("WebSocket closed.");
