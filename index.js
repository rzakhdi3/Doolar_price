
const axios = require("axios");
const fs = require("fs");

const BOT_TOKEN = process.env.BOT_TOKEN;
const CHAT_ID = process.env.CHAT_ID;

const FILE = "prices.json";

function loadPrices() {
  try { return JSON.parse(fs.readFileSync(FILE)); }
  catch { return {}; }
}

function savePrices(data) {
  fs.writeFileSync(FILE, JSON.stringify(data, null, 2));
}

async function fetchData() {
  // TODO: Replace endpoints with your preferred sources.
  // Template structure is ready.
  return {
    dollar: 0,
    usdt: 0,
    gold18: 0,
    silver: 0
  };
}

(async () => {
  const current = await fetchData();
  const old = loadPrices();

  const changed = JSON.stringify(current) !== JSON.stringify(old);

  if (!changed) {
    console.log("No change");
    process.exit(0);
  }

  const text = `📈 بروزرسانی بازار

💵 دلار: ${current.dollar.toLocaleString()}
₮ تتر: ${current.usdt.toLocaleString()}
🥇 طلای 18 عیار: ${current.gold18.toLocaleString()}
🥈 نقره: ${current.silver.toLocaleString()}

🕒 ${new Date().toLocaleString("fa-IR")}`;

  await axios.post(
    `https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`,
    { chat_id: CHAT_ID, text }
  );

  savePrices(current);
})();
