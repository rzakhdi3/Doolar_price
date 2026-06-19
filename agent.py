import os
import requests
from bs4 import BeautifulSoup

def get_dollar_price():
    """دریافت قیمت دلار از سایت tgju.org"""
    try:
        url = "https://www.tgju.org/profile/price_dollar_rl"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # جستجو با سلکتورهای مختلف
        selectors = [
            'span.info-price',
            'div.price-value',
            'span[data-col="info.last_trade.PDrCotVal"]',
            'span.text-center'
        ]
        
        price_element = None
        for selector in selectors:
            price_element = soup.select_one(selector)
            if price_element:
                break
        
        if price_element:
            price_text = price_element.text.strip().replace(',', '')
            price = int(''.join(filter(str.isdigit, price_text)))
            return price
        else:
            print("خطا: المان قیمت پیدا نشد")
            return None
            
    except Exception as e:
        print(f"خطا در دریافت قیمت: {e}")
        return None

def load_last_price():
    """خواندن آخرین قیمت ذخیره شده"""
    try:
        if os.path.exists('last_price.txt'):
            with open('last_price.txt', 'r') as f:
                content = f.read().strip()
                if content:
                    return int(content)
        return 0
    except Exception as e:
        print(f"خطا در خواندن قیمت قبلی: {e}")
        return 0

def save_price(price):
    """ذخیره قیمت جدید"""
    try:
        with open('last_price.txt', 'w') as f:
            f.write(str(price))
    except Exception as e:
        print(f"خطا در ذخیره قیمت: {e}")

def send_telegram_message(message):
    """ارسال پیام به تلگرام"""
    try:
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        chat_id = os.environ.get('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            print("خطا: توکن یا chat_id تنظیم نشده است")
            return False
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result.get('ok'):
            print("پیام با موفقیت ارسال شد")
            return True
        else:
            print(f"خطا در ارسال پیام: {result}")
            return False
            
    except Exception as e:
        print(f"خطا در ارسال پیام به تلگرام: {e}")
        return False

def main():
    print("شروع بررسی قیمت دلار...")
    
    # دریافت قیمت فعلی
    current_price = get_dollar_price()
    
    if current_price is None:
        print("خطا: نتوانستم قیمت را دریافت کنم")
        return
    
    print(f"قیمت فعلی: {current_price:,} تومان")
    
    # خواندن قیمت قبلی
    last_price = load_last_price()
    print(f"قیمت قبلی: {last_price:,} تومان")
    
    # بررسی تغییر قیمت
    if last_price == 0:
        # اولین اجرا
        message = f"🤖 <b>ربات قیمت دلار فعال شد</b>\n\n"
        message += f"💵 قیمت فعلی: <b>{current_price:,}</b> تومان"
        send_telegram_message(message)
        save_price(current_price)
        print("پیام اولیه ارسال شد")
    elif current_price != last_price:
        # قیمت تغییر کرده
        difference = current_price - last_price
        if last_price > 0:
            percentage = (difference / last_price) * 100
        else:
            percentage = 0
        
        if difference > 0:
            emoji = "📈"          change_text = "افزایش"
        else:
            emoji = "📉"
            change_text = "کاهش"
        
        message = f"{emoji} <b>تغییر قیمت دلار</b>\n\n"
        message += f"💵 قیمت جدید: <b>{cuent_price:,}</b> تومان\n"
        message += f"💵 قیمت قبلی: <b>{la
