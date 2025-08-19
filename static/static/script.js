document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("trade-form");
  const resultBox = document.getElementById("result");
  const chartCanvas = document.getElementById("trendChart");
  let chart;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const stock = document.getElementById("stock").value;
    const action = document.getElementById("action").value;

    resultBox.textContent = "Loading...";

    try {
      const res = await fetch("/trade", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ stock, action })
      });
      const data = await res.json();
      resultBox.textContent = data.message;

      // update chart
      if (chart) chart.destroy();
      chart = new Chart(chartCanvas, {
        type: "line",
        data: {
          labels:
