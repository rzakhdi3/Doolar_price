import requests
import os
import re

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

def get_dollar_price():
    """Fetch dollar price in Tomans from taban.ir API"""
    url = 'https://api.taban.ir/v1/currency/usd'
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"API Response: {data}")
        
        if 'data' in data and 'sell' in data['data']:
            price = int(data['data']['sell'])
            print(f"Parsed price (Tomans): {price:,}")
            return price
        else:
            print("Could not find price in API response")
            return None
        
    except Exception as e:
        print(f"Error fetching price: {e}")
        import traceback
        traceback.print_exc()
        return None

def send_telegram_message(message):
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        print(f"Telegram response: {response.json()}")
        return True
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return False

def load_last_price():
    """Load the last saved price from file"""
    try:
        if os.path.exists('last_price.txt'):
            with open('last_price.txt', 'r') as f:
                content = f.read().strip()
                if content:
                    return int(content)
        return 0
    except Exception as e:
        print(f"Error loading last price: {e}")
        return 0

def save_price(price):
    """Save price to file"""
    try:
        with open('last_price.txt', 'w') as f:
            f.write(str(price))
        print(f"Saved new price: {price:,}")
        return True
    except Exception as e:
        print(f"Error saving price: {e}")
        return False

def main():
    print("Starting dollar price bot...")
    print(f"Current time: {os.popen('date').read().strip()}")
    
    current_price = get_dollar_price()
    
    if current_price is None:
        print("Failed to fetch current price")
        return
    
    last_price = load_last_price()
    print(f"Last saved price: {last_price:,} Tomans")
    
    if last_price != current_price:
        print(f"Price changed from {last_price:,} to {current_price:,} Tomans")
        
        current_formatted = f"{current_price:,}"
        
        if last_price and last_price > 0:
            last_formatted = f"{last_price:,}"
            change = current_price - last_price
            change_formatted = f"{abs(change):,}"
            percent_change = (change / last_price) * 100
            
            if change > 0:
                emoji = "📈"
                direction = "افزایش"
            else:
                emoji = "📉"
                direction = "کاهش"
            
            message = f"""{emoji} <b>تغییر قیمت دلار</b>

💵 قیمت فعلی: {current_formatted} تومان
📊 قیمت قبلی: {last_formatted} تومان
{emoji} {direction}: {change_formatted} تومان
📊 درصد تغییر: {percent_change:.2f}%

🕐 {os.popen('date "+%Y-%m-%d %H:%M:%S"').read().strip()}"""
        else:
            message = f"""💵 <b>قیمت دلار</b>

قیمت فعلی: {current_formatted} تومان

🕐 {os.popen('date "+%Y-%m-%d %H:%M:%S"').read().strip()}"""
        
        if send_telegram_message(message):
            print("Message sent successfully")
            save_price(current_price)
        else:
            print("Failed to send message")
    else:
        print("Price hasn't changed, not sending message")

if __name__ == "__main__":
    main()
