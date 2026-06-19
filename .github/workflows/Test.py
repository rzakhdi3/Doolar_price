import os
import requests

bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

print(f"Bot token exists: {bool(bot_token)}")
print(f"Chat ID exists: {bool(chat_id)}")
print(f"Chat ID value: {chat_id}")

if bot_token and chat_id:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    response = requests.post(url, data={
        'chat_id': chat_id,
        'text': 'تست - ربات کار میکنه ✅'
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
