# tuya-mcp · 哄睡玩偶 MCP

涂鸦 Wi-Fi 红外遥控器 → 哄睡玩偶，接入 Claude Connector。
工具：`power_on` `pat_toggle` `speed_slow` `speed_quick` `soothe_sleep(rounds)`

> 涂鸦中国区 API（openapi.tuyacn.com）只接受**国内 IP**，必须部署在国内 VPS 上。

## 部署（VPS，root）

1. 把本目录传到 VPS（`scp -r extras/tuya-mcp root@VPS:/root/`），然后 `bash /root/tuya-mcp/install.sh`
2. `nano /opt/tuya-mcp/.env` 填 ACCESS_ID / ACCESS_SECRET / INFRARED_ID，`MCP_PATH` 换成随机串
3. `/opt/tuya-mcp/venv/bin/python /opt/tuya-mcp/list_codes.py` → 找到 DIY 遥控器的 remote_id 填入 REMOTE_ID，再跑一次拿四个学习码，填 CODE_*
4. `systemctl enable --now tuya-mcp`，`journalctl -u tuya-mcp -f` 看日志
5. 测试：`cloudflared tunnel --url http://127.0.0.1:8765` → Connector URL = `https://xxx.trycloudflare.com` + `MCP_PATH`

## 安全

URL 本身就是钥匙：知道 URL 的人都能控制玩偶。`MCP_PATH` 用随机串，不要公开截图 URL。
