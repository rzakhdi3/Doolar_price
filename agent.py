import os
import requests
from bs4 import BeautifulSoup

def get_dollar_price():
    """دریافت قیمت دلار از سایت"""
    url = "https://www.tgju.org/profile/price_dollar_rl"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # جستجوی قیمت با سلکتورهای مختلف
        price_element = soup.select_one('span[data-col="info.last_trade.PDrCotVal"]')
        
        if not price_element:
            price_element = soup.select_one('.info-table td')
        
        if price_element:
            price_text = price_element.text.strip().replace(',', '')
            print(f"Found price: {price_text}")
            return int(price_text)
        else:
            print("Could not find price element")
            return None
            
    except Exception as e:
        print(f"Error getting price: {e}")
        return None

def read_last_price():
    """خواندن قیمت قبلی از فایل"""
    try:
        if os.path.exists('last_price.txt'):
            with open('last_price.txt', 'r') as f:
                price = int(f.read().strip())
                print(f"Last saved price: {price}")
                return price
        else:
            print("No previous price found")
            return None
    except Exception as e:
        print(f"Error reading last price: {e}")
        return None

def save_last_price(price):
    """ذخیره قیمت جدید در فایل"""
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
        print("Error: Missing bot token or chat ID")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    try:
        response = requests.post(url, json={
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }, timeout=10)
        
        result = response.json()
        print(f"Telegram response: {result}")
        
        if result.get('ok'):
            print("Message sent successfully!")
            return True
        else:
            print(f"Error sending message: {result.get('description')}")
            return False
            
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

def main():
    print("=== Dollar Price Bot Started ===")
    
    # دریافت قیمت جدید
    current_price = get_dollar_price()
    if not current_price:
        print("Failed to get current price")
        return
    
    # خواندن قیمت قبلی
    last_price = read_last_price()
    
    # اگر قیمت قبلی وجود نداشت، این اولین اجراست
    if last_price is None:
        print("First run - sending initial price")
        message = f"💵 قیمت فعلی دلار: {current_price:,} تومان"
        if send_telegram_message(message):
            save_last_price(current_price)
        return
    
    # مقایسه قیمت‌ها
    if current_price == last_price:
        print(f"Price unchanged: {current_price:,}")
        print("No message sent")
        return
    
    # محاسبه تغییر قیمت
    price_diff = current_price - last_price
    percent_change = (price_diff / last_price) * 100
    
    # آیکون بر اساس تغییر
    if price_diff > 0:
        icon = "📈"
        change_text = "افزایش"
    else:
        icon = "📉"
        change_text = "کاهش"
    
    # ساخت پیام
    message = f"""{icon} <b>تغییر قیمت دلار</b>

💵 قیمت فعلی: {current_price:,} تومان
📊 {change_text}: {abs(price_diff):,} تومان ({abs(percent_change):.2f}%)
⏱ قیمت قبلی: {last_price:,} تومان"""
    
    print(f"Price changed: {last_price:,} → {current_price:,}")
    
    # ارسال پیام و ذخیره قیمت جدید
    if send_telegram_message(message):
        save_last_price(current_price)
    
    print("=== Bot Finished ===")

if __name__ == "__main__":
    main()
