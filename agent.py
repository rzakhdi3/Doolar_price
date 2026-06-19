import requests
import json
import os
from datetime import datetime

def get_dollar_price_tgju():
    """دریافت قیمت از tgju.org (منبع اول)"""
    try:
        url = "https://call1.tgju.online/ajax.json"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.tgju.org/'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # دلار آمریکا در بازار آزاد
        usd_data = data.get('current', {}).get('price_dollar_rl', {})
        price = int(usd_data.get('p', 0)) // 10  # تبدیل از ریال به تومان
        
        if price > 0:
            return {
                'buy': price,
                'sell': price,
                'average': price
            }
        return None
        
    except Exception as e:
        print(f"خطای tgju: {e}")
        return None

def get_dollar_price_sarafiran():
    """دریافت قیمت از sarafiran.ir (منبع دوم)"""
    try:
        url = "https://publicapi.sarafiran.ir/v2/currencies/price?currency_code=USD"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('ok'):
            item = data.get('data', [])[0] if data.get('data') else {}
            buy_price = int(item.get('buy', 0)) // 10  # تبدیل از ریال به تومان
            sell_price = int(item.get('sell', 0)) // 10
            
            if buy_price > 0 and sell_price > 0:
                return {
                    'buy': buy_price,
                    'sell': sell_price,
                    'average': (buy_price + sell_price) // 2
                }
        return None
        
    except Exception as e:
        print(f"خطای sarafiran: {e}")
        return None

def get_dollar_price_call2api():
    """دریافت قیمت از call2api.ir (منبع سوم)"""
    try:
        url = "https://api.call2api.ir/api/v1/arz"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') == 200:
            usd_data = data.get('data', {}).get('usd', {})
            buy_price = int(usd_data.get('buy', 0))
            sell_price = int(usd_data.get('sell', 0))
            
            if buy_price > 0 and sell_price > 0:
                return {
                    'buy': buy_price,
                    'sell': sell_price,
                    'average': (buy_price + sell_price) // 2
                }
        return None
        
    except Exception as e:
        print(f"خطای call2api: {e}")
        return None

def get_dollar_price():
    """دریافت قیمت دلار با تلاش از چند منبع"""
    sources = [
        ('tgju.org', get_dollar_price_tgju),
        ('sarafiran.ir', get_dollar_price_sarafiran),
        ('call2api.ir', get_dollar_price_call2api),
    ]
    
    for source_name, source_func in sources:
        print(f"تلاش برای دریافت قیمت از {source_name}...")
        prices = source_func()
        if prices:
            print(f"✓ قیمت از {source_name} دریافت شد")
            return prices, source_name
    
    return None, None

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
        print("✓ پیام با موفقیت ارسال شد")
        return True
        
    except Exception as e:
        print(f"✗ خطا در ارسال پیام: {e}")
        return False

def load_last_prices():
    """بارگذاری آخرین قیمت‌های ذخیره شده"""
    try:
        if os.path.exists('last_prices.json'):
            with open('last_prices.json', 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"خطا در خواندن فایل: {e}")
    return None

def save_prices(prices):
    """ذخیره قیمت‌های جدید"""
    try:
        with open('last_prices.json', 'w', encoding='utf-8') as f:
            json.dump(prices, f, ensure_ascii=False, indent=2)
        print("✓ قیمت ذخیره شد")
    except Exception as e:
        print(f"✗ خطا در ذخیره قیمت: {e}")

def format_price(price):
    """فرمت کردن قیمت با کاما"""
    return f"{price:,}"

def create_message(prices, source_name):
    """ساخت پیام تلگرام"""
    now = datetime.now().strftime("%Y/%m/%d - %H:%M:%S")
    
    message = f"""💵 <b>قیمت دلار آمریکا (بازار آزاد)</b>

🔵 خرید: <b>{format_price(prices['buy'])}</b> تومان
🔴 فروش: <b>{format_price(prices['sell'])}</b> تومان
✅ معامله: <b>{format_price(prices['average'])}</b> تومان

📊 منبع: {source_name}
🕐 {now}"""
    
    return message

def main():
    print("=" * 50)
    print("شروع بررسی قیمت دلار...")
    print("=" * 50)
    
    # دریافت توکن و chat_id از متغیرهای محیطی
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("✗ خطا: TELEGRAM_BOT_TOKEN و TELEGRAM_CHAT_ID باید تنظیم شوند")
        return
    
    # دریافت قیمت
    prices, source_name = get_dollar_price()
    
    if not prices:
        print("✗ خطا: نتوانستیم قیمت را از هیچ منبعی دریافت کنیم")
        return
    
    print(f"\n✓ قیمت دریافت شد:")
    print(f"  خرید: {format_price(prices['buy'])} تومان")
    print(f"  فروش: {format_price(prices['sell'])} تومان")
    print(f"  معامله: {format_price(prices['average'])} تومان")
    
    # بررسی تغییر قیمت
    last_prices = load_last_prices()
    
    should_send = False
    reason = ""
    
    if last_prices is None:
        should_send = True
        reason = "اولین اجرا"
    elif (last_prices.get('buy') != prices['buy'] or 
          last_prices.get('sell') != prices['sell']):
        should_send = True
        reason = "قیمت تغییر کرده"
    else:
        reason = "قیمت تغییری نکرده"
    
    print(f"\n→ {reason}")
    
    if should_send:
        message = create_message(prices, source_name)
        if send_telegram_message(bot_token, chat_id, message):
            save_prices(prices)
    
    print("=" * 50)
    print("پایان اجرا")
    print("=" * 50)

if __name__ == "__main__":
    main()
