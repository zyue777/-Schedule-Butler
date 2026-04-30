import os
import time
import requests
import traceback
import threading
from channels.base import ChannelBase
from core.context import Context, ChannelManifest, ContextStatus

MANIFEST = ChannelManifest(name="telegram", description="Telegram长连接(Long Polling)")

class TelegramChannel(ChannelBase):
    def start(self, runtime):
        self._runtime = runtime
        self._token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.api_url = f"https://api.telegram.org/bot{self._token}"
        
        http_proxy = os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
        https_proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
        self.proxies = None
        if http_proxy or https_proxy:
            self.proxies = {"http": http_proxy, "https": https_proxy}

        if not self._token:
            print(f"[telegram] 错误: 未配置 TELEGRAM_BOT_TOKEN")
            return

        print(f"[telegram] 连接 Telegram... (Proxies: {self.proxies})")
        
        # 简单长轮询循环
        offset = 0
        while True:
            try:
                resp = requests.get(
                    f"{self.api_url}/getUpdates", 
                    params={"offset": offset, "timeout": 30},
                    proxies=self.proxies,
                    timeout=40
                )
                
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("result", []):
                        offset = item["update_id"] + 1
                        message = item.get("message")
                        if not message:
                            continue
                            
                        text = message.get("text", "")
                        chat_id = str(message["chat"]["id"])
                        msg_id = str(message["message_id"])
                        
                        if text:
                            print(f"[telegram] 收到消息: {text[:20]}... from {chat_id}")
                            ctx = self.build_context(runtime,
                                request_id=msg_id, user_id=chat_id,
                                raw_text=text,
                                metadata={'has_image': False}
                            )
                            threading.Thread(target=self._handle, args=(ctx,), daemon=True).start()
                            
            except Exception as e:
                print(f"[telegram] 轮询异常: {e}")
                time.sleep(5)

    def _handle(self, ctx: Context):
        try:
            from core.executor import execute_in_runtime
            ctx = execute_in_runtime(self._runtime, ctx)
            self.send_reply(ctx)
        except Exception as e:
            print(f"[telegram] _handle 异常: {e}")
            traceback.print_exc()

    def send_reply(self, ctx: Context):
        if not ctx.reply_text:
            return
        try:
            from channels.telegram.sender import TelegramSender
            sender = TelegramSender()
            sender.send_card(ctx.user_id, ctx.reply_text)
        except Exception as e:
            print(f"[telegram] send_reply 异常: {e}")

def create_channel():
    return TelegramChannel()
