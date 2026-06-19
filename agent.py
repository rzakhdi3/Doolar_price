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
    """
