import requests
import json
import os
from datetime import datetime

def get_bonbast_prices():
    """دریافت قیمت‌های خرید و فروش دلار از bonbast.com"""
    try:
        url = "https://bonbast.com/json"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        buy_price = int(data.get('usd1', 0))
        sell_price = int(data.get('usd2', 0))
        
        if buy_price > 0 and sell_price > 0:
            return {
                'buy': buy_price,
                'sell': sell_price,
                'average': (buy_price + sell_price) // 2
            }
        return None
        
    except Exception as e:
        print(f"خطا در دریافت قیمت: {e}")
        return None

def send_telegram_message(bot_token, chat_id, message):
    """ارسال پیام به تلگرام"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        print("پیام با موفقیت ارسال شد")
        return True
        
    except Exception as e:
        print(f"خطا در ارسال پیام: {e}")
        return False

def load_last_prices():
    """بارگذاری آخرین قیمت‌های ذخیره شده"""
    try:
        if os.path.exists('last_prices.json'):
            with open('last_prices.json', 'r') as f:
                return json.load(f)
    except:
        pass
    return None

def save_prices(prices):
    """ذخیره قیمت‌های جدید"""
    try:
        with open('last_prices.json', 'w') as f:
            json.dump(prices, f)
    except Exception as e:
        print(f"خطا در ذخیره قیمت: {e}")

def format_price(price):
    """فرمت کردن قیمت با کاما"""
    return f"{price:,}"

def create_message(prices):
    """ساخت پیام تلگرام"""
    now = datetime.now().strftime("%Y/%m/%d - %H:%M:%S")
    
    message = f"""
💵 <b>قیمت دلار آمریکا (بازار آزاد)</b>

🔵 خرید: <b>{format_price(prices['buy'])}</b> تومان
🔴 فروش: <b>{format_price(prices['sell'])}</b> تومان
✅ معامله: <b>{format_price(prices['average'])}</b> تومان

🕐 {now}
"""
    return message.strip()

def main():
    # دریافت توکن و chat_id از متغیرهای محیطی
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("خطا: TELEGRAM_BOT_TOKEN و TELEGRAM_CHAT_ID باید تنظیم شوند")
        return
    
    print("در حال دریافت قیمت دلار...")
    prices = get_bonbast_prices()
    
    if not prices:
        print("خطا: نتوانستیم قیمت را دریافت کنیم")
        return
    
    print(f"قیمت دریافت شد - خرید: {format_price(prices['buy'])}, فروش: {format_price(prices['sell'])}")
    
    # بررسی تغییر قیمت
    last_prices = load_last_prices()
    
    if last_prices is None:
        # اولین اجرا - پیام ارسال می‌شود
        print("اولین اجرا - ارسال پیام...")
        message = create_message(prices)
        send_telegram_message(bot_token, chat_id, message)
        save_prices(prices)
    elif last_prices['buy'] != prices['buy'] or last_prices['sell'] != prices['sell']:
        # قیمت تغییر کرده
        print("قیمت تغییر کرده - ارسال پیام...")
        message = create_message(prices)
        send_telegram_message(bot_token, chat_id, message)
        save_prices(prices)
    else:
        print("قیمت تغییری نکرده - پیامی ارسال نشد")

if __name__ == "__main__":
    main()
