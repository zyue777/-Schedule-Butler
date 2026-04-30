import requests
import json
import base64
from tools.feishu_token import FeishuTokenManager

class FeishuOCR:
    def __init__(self, token_manager: FeishuTokenManager):
        self.token_manager = token_manager
        
    def recognize_image_from_bytes(self, image_bytes: bytes) -> str:
        token = self.token_manager.get_tenant_access_token()
        url = "https://open.feishu.cn/open-apis/optical_char_recognition/v1/image/basic_recognize"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 将图片转为 base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        payload = {
            "image": image_base64
        }
        
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 0:
                    text_list = data.get("data", {}).get("text_list", [])
                    return "\n".join(text_list)
                else:
                    print(f"[FeishuOCR] 识别失败: {data}")
            else:
                print(f"[FeishuOCR] HTTP错误: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"[FeishuOCR] 异常: {e}")
            
        return ""
