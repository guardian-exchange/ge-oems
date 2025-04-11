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
  <div class="trade-box">
    <input type="number" min="1" placeholder="Quantity" id="${symbol}-qty" />
    <button onclick="tradeStock('${symbol}', 'buy')">Buy</button>
    <button onclick="tradeStock('${symbol}', 'sell')">Sell</button>
  </div>
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
    const price = data[symbol]["price"];
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

function getCSRFToken() {
  const cookie = document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrftoken="));
  return cookie ? cookie.split("=")[1] : "";
}

function updateBalance() {
  fetch("/user/get-balance/")
    .then((res) => res.json())
    .then((data) => {
      const balanceSpan = document.getElementById("user-balance");
      balanceSpan.textContent = data.balance;
    });
}

function showToast(message, ok = true) {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = "toast";
  if (!ok) {
    toast.classList.add("error");
  }
  toast.textContent = message;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => container.removeChild(toast), 500);
  }, 3000);
}

window.tradeStock = function (symbol, action) {
  const qtyInput = document.getElementById(`${symbol}-qty`);
  const quantity = parseInt(qtyInput.value, 10);

  if (!quantity || quantity <= 0) {
    alert("Please enter a valid quantity.");
    return;
  }

  const formData = new FormData();
  formData.append("stock_name", symbol);
  formData.append("stock_quantity", quantity);
  formData.append("stock_side", action);

  fetch("/user/place_order/", {
    method: "POST",
    headers: {
      "X-CSRFToken": getCSRFToken(),
    },
    body: formData,
  })
    .then(async (res) => {
      const text = await res.text();
      updateBalance();
      showToast(text, res.ok);
    })
    .catch((err) => {
      console.error("Trade error:", err);
      showToast("An error occurred while placing the order.");
    });
};
