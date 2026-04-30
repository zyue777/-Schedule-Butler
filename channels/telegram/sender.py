import os
import requests

class TelegramSender:
    def __init__(self):
        self.token = os.environ.get("TELEGRAM_BOT_TOKEN")
        self.api_url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        self.proxies = None
        
        http_proxy = os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
        https_proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
        
        if http_proxy or https_proxy:
            self.proxies = {
                "http": http_proxy,
                "https": https_proxy
            }

    def send_card(self, user_id: str, card_data: str):
        if not self.token:
            print("[TelegramSender] 错误: TELEGRAM_BOT_TOKEN 未配置")
            return
            
        payload = {
            "chat_id": user_id,
            "text": card_data,
            "parse_mode": "Markdown"
        }
        
        try:
            resp = requests.post(self.api_url, json=payload, proxies=self.proxies, timeout=10)
            if resp.status_code != 200:
                print(f"[TelegramSender] 发送失败: {resp.text}")
        except Exception as e:
            print(f"[TelegramSender] 请求异常: {e}")
