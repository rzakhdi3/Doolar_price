import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_dollar_price():
    """دریافت قیمت دلار از tgju.org"""
    try:
        url = "https://www.tgju.org/profile/price_dollar_rl"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # جستجو با سلکتورهای مختلف
        selectors = [
            'span.info-price',
            'span[class*="price"]',
            'div.info-price',
            'span.last-price'
        ]
        
        price_element = None
        for selector in selectors:
            price_element = soup.select_one(selector)
            if price_element:
                print(f"Found price with selector: {selector}")
                break
        
        if not price_element:
            print("Could not find price element with any selector")
            print("Page title:", soup.title.string if soup.title else "No title")
            return None
        
        price_text = price_element.text.strip()
        print(f"Raw price text: {price_text}")
        
        # حذف کاماها و تبدیل به عدد
        price_text = price_text.replace(',', '').replace('٬', '')
        price = int(''.join(filter(str.isdigit, price_text)))
        
        print(f"Parsed price: {price}")
        return price
        
    except Exception as e:
        print(f"Error fetching dollar price: {e}")
        return None

def read_last_price():
    """خواندن آخرین قیمت ذخیره شده"""
    try:
        if os.path.exists('last_price.txt'):
            with open('last_price.txt', 'r') as f:
                price = int(f.read().strip())
                print(f"Last saved price: {price}")
                return price
        return 0
    except Exception as e:
        print(f"Error reading last price: {e}")
        return 0

def save_last_price(price):
    """ذخیره قیمت فعلی"""
    try:
        with open('last_price.txt', 'w') as f:
            f.write(str(price))
        print(f"Saved new price: {price}")
    except Exception as e:
        print(f"Error saving price: {e}")

def send_telegram_message(message):
    """ارسال پیام به تلگرام"""
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("Error: Bot token or chat ID not found in environment variables")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Telegram response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending telegram message: {e}")
        return False

def main():
    print("Starting dollar price bot...")
    print(f"Current time: {datetime.now()}")
    
    # دریافت قیمت فعلی
    current_price = get_dollar_price()
    
    if not current_price:
        print("Failed to fetch current price")
        return
    
    # خواندن قیمت قبلی
    last_price = read_last_price()
    
    # بررسی تغییر قیمت
    if current_price == last_price:
        print(f"Price unchanged: {current_price}")
        return
    
    print(f"Price changed from {last_price} to {current_price}")
    
    # ساخت پیام
    if last_price and last_price > 0:
        price_diff = current_price - last_price
        percent_change = (price_diff / last_price) * 100
        
        change_icon = "📈" if price_diff > 0 else "📉"
        
        message = f"""
💵 قیمت دلار به‌روز شد!

قیمت فعلی: {current_price:,} ریال
قیمت قبلی: {last_price:,} ریال
تغییرات: {price_diff:,} ریال ({change_icon} {percent_change:.2f}%)

🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    else:
        # اولین بار که قیمت دریافت میشه
        message = f"""
💵 قیمت دلار ثبت شد!

قیمت فعلی: {current_price:,} ریال

🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    # ارسال به تلگرام
    if send_telegram_message(message):
        print("Message sent successfully")
        # ذخیره قیمت جدید
        save_last_price(current_price)
    else:
        print("Failed to send message")

if __name__ == "__main__":
    main()
