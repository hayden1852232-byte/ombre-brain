"""查询红外转发器下的遥控器和 DIY 学习码，用来填 .env。
用法：python list_codes.py
"""
import json
import os

from dotenv import load_dotenv

from tuya_client import TuyaClient

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
c = TuyaClient(os.environ["ACCESS_ID"], os.environ["ACCESS_SECRET"],
               os.getenv("TUYA_ENDPOINT", "https://openapi.tuyacn.com"))
ir = os.environ["INFRARED_ID"]

print("== 遥控器列表 ==")
remotes = c.list_remotes(ir)
print(json.dumps(remotes, ensure_ascii=False, indent=2))

rid = os.getenv("REMOTE_ID")
if rid:
    print(f"\n== {rid} 的学习码 ==")
    print(json.dumps(c.learning_codes(ir, rid), ensure_ascii=False, indent=2))
else:
    print("\n.env 里还没填 REMOTE_ID：从上面列表里找到 DIY 遥控器的 remote_id 填进去，再跑一次。")
