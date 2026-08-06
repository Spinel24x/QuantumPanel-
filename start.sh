#!/bin/bash
set -e

echo "╔════════════════════════════════════════╗"
echo "║   🕳️  QUANTUM + NGINX + TLS  🕳️     ║"
echo "╚════════════════════════════════════════╝"

DOMAIN=quantumpanel-production.up.railway.app
mkdir -p /app/data /etc/xray /var/log/nginx /app/certs

# UUIDs
if [ ! -f /app/data/uuid.txt ]; then
    cat /proc/sys/kernel/random/uuid > /app/data/uuid.txt
fi
UUID=$(cat /app/data/uuid.txt)

if [ ! -f /app/data/uuid_vmess.txt ]; then
    cat /proc/sys/kernel/random/uuid > /app/data/uuid_vmess.txt
fi
UUID_VMESS=$(cat /app/data/uuid_vmess.txt)

if [ ! -f /app/data/trojan_pass.txt ]; then
    cat /proc/sys/kernel/random/uuid | tr -d '-' | head -c 16 > /app/data/trojan_pass.txt
fi
TROJAN_PASS=$(cat /app/data/trojan_pass.txt)

if [ ! -f /app/data/ss_pass.txt ]; then
    cat /proc/sys/kernel/random/uuid | tr -d '-' | head -c 16 > /app/data/ss_pass.txt
fi
SS_PASS=$(cat /app/data/ss_pass.txt)

echo "🔑 VLESS: $UUID"

# SSL
openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
  -keyout /app/certs/key.pem -out /app/certs/cert.pem \
  -subj "/CN=$DOMAIN" 2>/dev/null
echo "✅ SSL Certificate"

# ============================================
# Xray
# ============================================
cat > /etc/xray/config.json << XRAYEOF
{
    "log": {"loglevel": "warning"},
    "inbounds": [
        {"port": 10000, "listen": "127.0.0.1", "protocol": "vless",
            "settings": {"clients": [{"id": "$UUID", "level": 0}], "decryption": "none"},
            "streamSettings": {"network": "ws", "wsSettings": {"path": "/vless"}}},
        {"port": 10000, "listen": "127.0.0.1", "protocol": "vmess",
            "settings": {"clients": [{"id": "$UUID_VMESS", "level": 0}]},
            "streamSettings": {"network": "ws", "wsSettings": {"path": "/vmess"}}},
        {"port": 10000, "listen": "127.0.0.1", "protocol": "trojan",
            "settings": {"clients": [{"password": "$TROJAN_PASS"}]},
            "streamSettings": {"network": "ws", "wsSettings": {"path": "/trojan"}}},
        {"port": 10000, "listen": "127.0.0.1", "protocol": "shadowsocks",
            "settings": {"method": "aes-256-gcm", "password": "$SS_PASS"},
            "streamSettings": {"network": "ws", "wsSettings": {"path": "/ss"}}}
    ],
    "outbounds": [{"protocol": "freedom", "tag": "direct"}]
}
XRAYEOF

/opt/xray/xray run -config /etc/xray/config.json &
echo "✅ Xray on 127.0.0.1:10000"

# ============================================
# Nginx
# ============================================
cp /app/nginx.conf /etc/nginx/nginx.conf
nginx -g "daemon off;" &
echo "✅ Nginx on 0.0.0.0:8443 (TLS)"

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
    "vless": {"path": "/vless"},
    "vmess": {"path": "/vmess"},
    "trojan": {"path": "/trojan"},
    "ss": {"path": "/ss"}
}
EOF

echo ""
echo "╔════════════════════════════════════════╗"
echo "║   4 PROTOCOLS + TLS + NGINX           ║"
echo "╚════════════════════════════════════════╝"
echo ""

cd /app
exec python3 -m uvicorn app:app --host 0.0.0.0 --port 9000
