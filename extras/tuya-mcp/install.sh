#!/usr/bin/env bash
# 在 VPS 上以 root 运行：bash install.sh
set -euo pipefail
DIR=/opt/tuya-mcp
SRC="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$DIR"
cp "$SRC"/{server.py,tuya_client.py,list_codes.py,requirements.txt,tuya-mcp.service} "$DIR"/
[ -f "$DIR/.env" ] || { cp "$SRC/.env.example" "$DIR/.env"; chmod 600 "$DIR/.env"; }
command -v python3 >/dev/null || { apt-get update && apt-get install -y python3; }
python3 -m venv "$DIR/venv" 2>/dev/null || { apt-get update && apt-get install -y python3-venv && python3 -m venv "$DIR/venv"; }
"$DIR/venv/bin/pip" install -q -i https://pypi.tuna.tsinghua.edu.cn/simple -r "$DIR/requirements.txt"
cp "$DIR/tuya-mcp.service" /etc/systemd/system/
systemctl daemon-reload
echo "装好了。下一步：编辑 $DIR/.env 填凭证，跑 $DIR/venv/bin/python $DIR/list_codes.py 拿学习码，然后 systemctl enable --now tuya-mcp"
