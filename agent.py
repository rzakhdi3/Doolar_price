import requests
import os
from bs4 import BeautifulSoup

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

def get_dollar_price():
    """Fetch dollar price in Tomans from bonbast.com"""
    url = 'https://bonbast.com'
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # bonbast uses a table with currency data
        # USD row has id or specific class
        usd_row = soup.find('tr', {'data-name': 'usd'})
        if not usd_row:
            # fallback: find by searching for USD text
            for row in soup.find_all('tr'):
                cells = row.find_all('td')
                if cells and 'USD' in row.get_text():
                    usd_row = row
                    break
        
        if usd_row:
            cells = usd_row.find_all('td')
            print(f"USD row cells: {[c.get_text(strip=True) for c in cells]}")
            # sell price is typically the second price cell
            for cell in cells:
                text = cell.get_text(strip=True).replace(',', '')
                if text.isdigit() and len(text) >= 5:
                    price = int(text)
                    print(f"Parsed price (Tomans): {price:,}")
                    return price
        
        print("Could not find USD price row")
        print(f"Page preview: {response.text[:500]}")
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
            
            message = (
                f"{emoji} <b>تغییر قیمت دلار</b>\n\n"
                f"💵 قیمت فعلی: {current_formatted} تومان\n"
                f"📊 قیمت قبلی: {last_formatted} تومان\n"
                f"{emoji} {direction}: {change_formatted} تومان\n"
                f"📊 درصد تغییر: {percent_change:.2f}%"
            )
        else:
            message = (
                f"💵 <b>قیمت دلار</b>\n\n"
                f"قیمت فعلی: {current_formatted} تومان"
            )
        
        if send_telegram_message(message):
            print("Message sent successfully")
            save_price(current_price)
        else:
            print("Failed to send message")
    else:
        print("Price hasn't changed, not sending message")

if __name__ == "__main__":
    main()
