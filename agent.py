import os
import requests
from bs4 import BeautifulSoup
import re

def get_dollar_price():
    """دریافت قیمت دلار از سایت tgju.org"""
    url = "https://www.tgju.org/profile/price_dollar_rl"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # جستجوی سلکتورهای مختلف برای قیمت
        selectors = [
            'span.info-price',
            'div.price-value span',
            'span[data-col="info.last_trade.PDrCotVal"]',
            'div.last-price span'
        ]
        
        price_text = None
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                if price_text and any(c.isdigit() for c in price_text):
                    break
        
        if not price_text:
            raise ValueError("قیمت پیدا نشد")
        
        # حذف کاراکترهای غیرعددی و تبدیل به عدد
        price_clean = re.sub(r'[^\d]', '', price_text)
        price = int(price_clean)
        
        return price  # قیمت به تومان
        
    except Exception as e:
        print(f"خطا در دریافت قیمت: {e}")
        raise

def load_last_price():
    """خواندن آخرین قیمت ذخیره شده"""
    try:
        if os.path.exists('last_price.txt'):
            with open('last_price.txt', 'r') as f:
                content = f.read().strip()
                return int(content) if content else 0
    except:
        pass
    return 0

def save_price(price):
    """ذخیره قیمت جدید"""
    with open('last_price.txt', 'w') as f:
        f.write(str(price))

def send_telegram_message(message):
    """ارسال پیام به تلگرام"""
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        raise ValueError("توکن ربات یا شناسه چت تنظیم نشده است")
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()

def main():
    try:
        # دریافت قیمت فعلی
        current_price = get_dollar_price()
        print(f"قیمت فعلی: {current_price:,} تومان")
        
        # خواندن قیمت قبلی
        last_price = load_last_price()
        print(f"قیمت قبلی: {last_price:,} تومان")
        
        # بررسی تغییر قیمت
        if last_price == 0:
            # اولین اجرا
            message = f"🔔 <b>قیمت دلار</b>\n\n💵 {current_price:,} تومان"
            send_telegram_message(message)
            save_price(current_price)
            print("اولین قیمت ذخیره شد و پیام ارسال گردید")
        if current_price != last_price:
            # قیمت تغییر کرده
            diff = current_price - last_price
            diff_percent = (diff / last_price) * 100
            
            if diff > 0:
                emoji = "📈"
                chnge_text = "افزایش"
            else:
                emoji = "📉"
                change_text = "کاهش"
            
            message = (
                f"{emoji} <b>تغییر قیمت دلار</b>\n\n"
                f"💵 {current_pri:,} تومان\n"
                f"📊 قیمت قبلی: {last_price:,} تومان\n"
                f"📉 {change_text}: {abs(diff):,} تومان ({abs(diff_percent):.2f}%)"
            )
            
            send_telegram_message(message)
