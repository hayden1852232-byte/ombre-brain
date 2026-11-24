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

## 部署（Windows 本地）

1. 安装 Python 3.10+（python.org，勾选 Add to PATH）
2. 双击 `setup_windows.bat`
3. 记事本打开 `.env` 填凭证 → 双击 `list_codes_windows.bat` 拿 remote_id 和学习码 → 填回 `.env`
4. 双击 `start_windows.bat` 启动；开机自启：Win+R 输入 `shell:startup`，把它的快捷方式放进去
5. Cloudflare 后台 Zero Trust → Networks → Tunnels 建 Tunnel，Public Hostname 指向 `http://localhost:8765`
6. Connector URL = `https://你的子域名` + `MCP_PATH`
7. 代理软件用规则模式，`openapi.tuyacn.com` 必须直连

## 安全

URL 本身就是钥匙：知道 URL 的人都能控制玩偶。`MCP_PATH` 用随机串，不要公开截图 URL。
