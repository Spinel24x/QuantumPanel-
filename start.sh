#!/bin/bash
set -e

echo "╔════════════════════════════════════════╗"
echo "║   🕳️  QUANTUM v10  🕳️              ║"
echo "║   Xray:8080 | SSH:22 | Panel:9000    ║"
echo "╚════════════════════════════════════════╝"

DOMAIN=quantumpanel-production.up.railway.app
mkdir -p /app/data /etc/xray /var/log /var/run/sshd

# UUIDs
[ ! -f /app/data/uuid.txt ] && cat /proc/sys/kernel/random/uuid > /app/data/uuid.txt
UUID=$(cat /app/data/uuid.txt)

[ ! -f /app/data/uuid_vmess.txt ] && cat /proc/sys/kernel/random/uuid > /app/data/uuid_vmess.txt
UUID_VMESS=$(cat /app/data/uuid_vmess.txt)

[ ! -f /app/data/trojan_pass.txt ] && cat /proc/sys/kernel/random/uuid | tr -d '-' | head -c 16 > /app/data/trojan_pass.txt
TROJAN_PASS=$(cat /app/data/trojan_pass.txt)

[ ! -f /app/data/ss_pass.txt ] && cat /proc/sys/kernel/random/uuid | tr -d '-' | head -c 16 > /app/data/ss_pass.txt
SS_PASS=$(cat /app/data/ss_pass.txt)

echo "🔑 VLESS: $UUID"

# ============================================
# Xray - همه پروتکل‌ها روی پورت 8080
# ============================================
cat > /etc/xray/config.json << XRAYEOF
{
    "log": {"loglevel": "warning"},
    "inbounds": [
        {"port": 8080, "listen": "0.0.0.0", "protocol": "vless",
            "settings": {"clients": [{"id": "$UUID", "level": 0}], "decryption": "none"},
            "streamSettings": {"network": "ws", "wsSettings": {"path": "/vless"}}},
        {"port": 8080, "listen": "0.0.0.0", "protocol": "vmess",
            "settings": {"clients": [{"id": "$UUID_VMESS", "level": 0}]},
            "streamSettings": {"network": "ws", "wsSettings": {"path": "/vmess"}}},
        {"port": 8080, "listen": "0.0.0.0", "protocol": "trojan",
            "settings": {"clients": [{"password": "$TROJAN_PASS"}]},
            "streamSettings": {"network": "ws", "wsSettings": {"path": "/trojan"}}},
        {"port": 8080, "listen": "0.0.0.0", "protocol": "shadowsocks",
            "settings": {"method": "aes-256-gcm", "password": "$SS_PASS"},
            "streamSettings": {"network": "ws", "wsSettings": {"path": "/ss"}}}
    ],
    "outbounds": [{"protocol": "freedom", "tag": "direct"}]
}
XRAYEOF

/opt/xray/xray run -config /etc/xray/config.json &
echo "✅ Xray on 0.0.0.0:8080"

# ============================================
# SSH Server
# ============================================
/usr/sbin/sshd -D -e > /var/log/sshd.log 2>&1 &
echo "✅ SSH on port 22"

# ============================================
# Save Info
# ============================================
cat > /app/data/info.json << EOF
{
    "uuid": "$UUID",
    "uuid_vmess": "$UUID_VMESS",
    "trojan_pass": "$TROJAN_PASS",
    "ss_pass": "$SS_PASS",
    "domain": "$DOMAIN",
    "tcp_host": "metro.proxy.rlwy.net",
    "tcp_port": 35093,
    "ssh_host": "sakura.proxy.rlwy.net",
    "ssh_port": 53742,
    "paths": {
        "vless": "/vless",
        "vmess": "/vmess",
        "trojan": "/trojan",
        "ss": "/ss"
    }
}
EOF

echo ""
echo "╔════════════════════════════════════════╗"
echo "║   ✅ ALL SERVICES RUNNING             ║"
echo "║   Xray:8080 | SSH:22 | Panel:9000     ║"
echo "╚════════════════════════════════════════╝"
echo ""

cd /app
exec python3 -m uvicorn app:app --host 0.0.0.0 --port 9000
