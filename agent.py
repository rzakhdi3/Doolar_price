import requests
from bs4 import BeautifulSoup
import os

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def get_dollar_price():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        url = "https://www.tgju.org/profile/price_dollar_rl"
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status code: {response.status_code}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # جستجوی قیمت با سلکتورهای مختلف
        price_element = soup.select_one('span[data-col="info.last_trade.PDrCotVal"]')
        
        if not price_element:
            price_element = soup.select_one('.info-price')
        
        if not price_element:
            price_element = soup.select_one('[data-market-row="price_dollar_rl"] span')
        
        if price_element:
            price = price_element.text.strip()
            return f"💵 قیمت دلار: {price} تومان"
        else:
            print("HTML content sample:")
            print(response.text[:500])
            return None
            
    except Exception as e:
        print(f"خطا: {e}")
        return None

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, json=data)
    print(f"Telegram response: {response.text}")
    return response.json()

if __name__ == "__main__":
    price = get_dollar_price()
    if price:
        result = send_telegram(price)
        print("پیام ارسال شد" if result.get('ok') else f"خطا: {result}")
    else:
        print("قیمت دریافت نشد")
