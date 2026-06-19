import requests
from bs4 import BeautifulSoup
import os
import re

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

def get_dollar_price():
    """Fetch dollar price in Rials from tgju.org"""
    url = 'https://www.tgju.org/'
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the dollar row in the main table
        # Look for the row with data-market-row="price_dollar_rl"
        dollar_row = soup.select_one('tr[data-market-row="price_dollar_rl"]')
        
        if not dollar_row:
            print("Could not find dollar row")
            return None
        
        # Get the price from the last_trade column
        price_element = dollar_row.select_one('td[data-col="info.last_trade.PDrCotVal"]')
        
        if not price_element:
            print("Could not find price element")
            return None
            
        price_text = price_element.get_text(strip=True)
        print(f"Raw price text: {price_text}")
        
        # Remove commas and parse
        price_clean = re.sub(r'[,،\s]', '', price_text)
        price = int(price_clean)
        
        print(f"Parsed price (Rials): {price:,}")
        return price
        
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
    
    # Get current price
    current_price = get_dollar_price()
    
    if current_price is None:
        print("Failed to fetch current price")
        return
    
    # Load last saved price
    last_price = load_last_price()
    print(f"Last saved price: {last_price:,} Rials")
    
    # Check if price changed
    if last_price != current_price:
        print(f"Price changed from {last_price:,} to {current_price:,} Rials")
        
        # Format numbers with commas
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

💵 قیمت فعلی: {current_formatted} ریال
📊 قیمت قبلی: {last_formatted} ریال
{emoji} {direction}: {change_formatted} ریال
📊 درصد تغییر: {percent_change:.2f}%

🕐 {os.popen('date "+%Y-%m-%d %H:%M:%S"').read().strip()}"""
        else:
            # First time running
            message = f"""💵 <b>قیمت دلار</b>

قیمت فعلی: {current_formatted} ریال

🕐 {os.popen('date "+%Y-%m-%d %H:%M:%S"').read().strip()}"""
        
        # Send message
        if send_telegram_message(message):
            print("Message sent successfully")
            # Save new price
            save_price(current_price)
        else:
            print("Failed to send message")
    else:
        print("Price hasn't changed, not sending message")

if __name__ == "__main__":
    main()
