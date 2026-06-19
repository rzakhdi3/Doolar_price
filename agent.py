import requests
import json
import os
from datetime import datetime
import jdatetime

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
LAST_PRICES_FILE = 'last_prices.json'

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"خطا در ارسال پیام: {e}")
        return False

def get_prices_from_tgju():
    try:
        response = requests.get('https://api.tgju.org/v1/market/indicator/summary-table-data/price_dollar_rl,price_eur,sekee,geram18,mesghal', timeout=10)
        response.raise_for_status()
        data = response.json()
        
        prices = {}
        if 'price_dollar_rl' in data:
            prices['dollar'] = int(data['price_dollar_rl']['p'])
        if 'sekee' in data:
            prices['gold_coin'] = int(data['sekee']['p'])
        if 'geram18' in data:
            prices['gold_18k'] = int(data['geram18']['p'])
        
        return prices
    except Exception as e:
        print(f"خطا در دریافت از tgju: {e}")
        return None

def get_tether_price():
    try:
        response = requests.get('https://api.tetherland.com/currencies', timeout=10)
        response.raise_for_status()
        data = response.json()
        
        for item in data.get('data', {}).get('currencies', []):
            if item.get('code') == 'USDT':
                return int(float(item.get('buy_irr_price', 0)))
        return None
    except Exception as e:
        print(f"خطا در دریافت تتر: {e}")
        return None

def load_last_prices():
    if os.path.exists(LAST_PRICES_FILE):
        try:
            with open(LAST_PRICES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_last_prices(prices):
    with open(LAST_PRICES_FILE, 'w', encoding='utf-8') as f:
        json.dump(prices, f, ensure_ascii=False, indent=2)

def format_price(price):
    return f"{price:,}"

def main():
    print("شروع بررسی قیمت‌ها...")
    
    current_prices = get_prices_from_tgju()
    if not current_prices:
        print("خطا در دریافت قیمت‌ها")
        return
    
    tether = get_tether_price()
    if tether:
        current_prices['tether'] = tether
    
    last_prices = load_last_prices()
    
    changes = []
    for key, value in current_prices.items():
        if key in last_prices and last_prices[key] != value:
            old_price = last_prices[key]
            diff = value - old_price
            percent = (diff / old_price) * 100
            changes.append((key, old_price, value, diff, percent))
    
    if changes or not last_prices:
        now = jdatetime.datetime.now()
        jalali_date = now.strftime('%Y/%m/%d')
        jalali_time = now.strftime('%H:%M')
        
        message = f"📊 <b>گزارش قیمت‌ها</b>\n"
        message += f"🗓 {jalali_date} - ⏰ {jalali_time}\n\n"
        
        names = {
            'dollar': '💵 دلار',
            'tether': '💎 تتر',
            'gold_coin': '🪙 سکه',
            'gold_18k': '✨ طلا 18'
        }
        
        for key, value in current_prices.items():
            name = names.get(key, key)
            price_str = format_price(value)
            
            change_info = next((c for c in changes if c[0] == key), None)
            if change_info:
                _, old, new, diff, percent = change_info
                emoji = "📈" if diff > 0 else "📉"
                sign = "+" if diff > 0 else ""
                message += f"{name}: {price_str} تومان {emoji}\n"
                message += f"   تغییر: {sign}{format_price(diff)} ({sign}{percent:.2f}%)\n\n"
            else:
                message += f"{name}: {price_str} تومان\n\n"
        
        if send_telegram_message(message):
            print("پیام ارسال شد")
            save_last_prices(current_prices)
        else:
            print("خطا در ارسال پیام")
    else:
        print("تغییری نبود")

if __name__ == '__main__':
    main()
