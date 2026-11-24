"""哄睡玩偶 MCP 服务器：通过涂鸦 Wi-Fi 红外遥控器发码。"""
from __future__ import annotations

import os
import time

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from tuya_client import TuyaClient, TuyaError

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

ACCESS_ID = os.environ["ACCESS_ID"]
ACCESS_SECRET = os.environ["ACCESS_SECRET"]
INFRARED_ID = os.environ["INFRARED_ID"]
REMOTE_ID = os.environ["REMOTE_ID"]
CODES = {
    "power": os.getenv("CODE_POWER", ""),
    "pat": os.getenv("CODE_PAT", ""),
    "slow": os.getenv("CODE_SLOW", ""),
    "quick": os.getenv("CODE_QUICK", ""),
}
# 公网路径里带一段随机串，防止别人扫到 URL 就能控制玩偶
MCP_PATH = os.getenv("MCP_PATH", "/mcp")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8765"))

tuya = TuyaClient(ACCESS_ID, ACCESS_SECRET, os.getenv("TUYA_ENDPOINT", "https://openapi.tuyacn.com"))

kwargs = dict(host=HOST, port=PORT, streamable_http_path=MCP_PATH, stateless_http=True)
try:  # 经 Tunnel/Nginx 转发时 Host 头不是 127.0.0.1，关掉 DNS rebinding 校验
    from mcp.server.transport_security import TransportSecuritySettings
    kwargs["transport_security"] = TransportSecuritySettings(enable_dns_rebinding_protection=False)
except ImportError:
    pass

mcp = FastMCP(
    "哄睡玩偶",
    instructions="控制一个会拍打哄睡的玩偶（红外遥控）。用户说「拍我」「哄我睡」时调用 soothe_sleep；"
                 "红外没有状态回传，开关/拍打键都是切换式的。",
    **kwargs,
)


def _press(key: str) -> str:
    code = CODES.get(key)
    if not code:
        return f"❌ .env 里没配置 CODE_{key.upper()}"
    try:
        res = tuya.send_learned(INFRARED_ID, REMOTE_ID, code)
    except (TuyaError, OSError) as e:
        return f"❌ {key}: {e}"
    if res.get("success"):
        return f"✅ {key} 已发送"
    return f"❌ {key}: code={res.get('code')} msg={res.get('msg')}"


@mcp.tool()
def power_on() -> str:
    """按玩偶的电源键（开机；再按一次通常是关机）。"""
    return _press("power")


@mcp.tool()
def pat_toggle() -> str:
    """按拍打键：切换拍打功能开/关。"""
    return _press("pat")


@mcp.tool()
def speed_slow() -> str:
    """按一次减速键，拍打变慢。"""
    return _press("slow")


@mcp.tool()
def speed_quick() -> str:
    """按一次加速键，拍打变快。"""
    return _press("quick")


@mcp.tool()
def soothe_sleep(rounds: int = 1) -> str:
    """哄睡组合：开机 → 等 5 秒 → 开拍打 → 按 rounds 次减速（1-5，越多越慢）。"""
    rounds = max(1, min(int(rounds), 5))
    log = [_press("power")]
    if log[-1].startswith("❌"):
        return "\n".join(log)
    time.sleep(5)
    log.append(_press("pat"))
    for _ in range(rounds):
        time.sleep(1)
        log.append(_press("slow"))
    return "\n".join(log)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
