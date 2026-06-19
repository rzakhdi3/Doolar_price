import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

def get_dollar_price():
    url = "https://www.tgju.org/profile/price_dollar_rl"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        td = soup.find("td", {"data-col": "info_today_price"})
        if td:
            return td.text.strip().replace(",", "")
    except Exception as e:
        print(f"خطا: {e}")
    return None

def send_telegram(price):
    now = datetime.now().strftime("%H:%M - %Y/%m/%d")
    text = f"💵 <b>قیمت دلار</b>\n\n<code>{int(price):,}</code> ریال\n\n🕐 {now}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    requests.post(url, data=data)

if __name__ == "__main__":
    price = get_dollar_price()
    if price:
        send_telegram(price)
        print(f"ارسال شد: {price}")
    else:
        print("قیمت دریافت نشد")
