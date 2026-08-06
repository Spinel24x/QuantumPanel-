#!/bin/bash
set -e

echo "╔════════════════════════════════════════╗"
echo "║   🕳️  QUANTUM VLESS + CDN  🕳️      ║"
echo "╚════════════════════════════════════════╝"

DOMAIN=${RAILWAY_PUBLIC_DOMAIN:-localhost}
PANEL_PORT=8000
XRAY_PORT=9000

mkdir -p /app/data /etc/xray /var/log/xray

# UUID
if [ ! -f /app/data/uuid.txt ]; then
    cat /proc/sys/kernel/random/uuid > /app/data/uuid.txt
fi
UUID=$(cat /app/data/uuid.txt)

echo "🔑 UUID: $UUID"
echo "🌐 Domain: $DOMAIN"

# ============================================
# Xray روی پورت 9000
# ============================================
cat > /etc/xray/config.json << XRAYEOF
{
    "log": {"loglevel": "warning"},
    "inbounds": [{
        "port": 9000,
        "listen": "0.0.0.0",
        "protocol": "vless",
        "settings": {
            "clients": [{"id": "$UUID", "level": 0}],
            "decryption": "none"
        },
        "streamSettings": {
            "network": "ws",
            "wsSettings": {"path": "/ws"}
        },
        "sniffing": {
            "enabled": true,
            "destOverride": ["http", "tls"]
        }
    }],
    "outbounds": [{
        "protocol": "freedom",
        "tag": "direct"
    }]
}
XRAYEOF

echo "✅ Xray config created"

# استارت Xray
/opt/xray/xray run -config /etc/xray/config.json > /var/log/xray/xray.log 2>&1 &
sleep 2

if pgrep -f xray > /dev/null; then
    echo "   ✅ Xray started on port 9000"
    XRAY_OK=true
else
    echo "   ❌ Xray failed"
    XRAY_OK=false
fi

# ذخیره info
cat > /app/data/info.json << INFOEOF
{
    "uuid": "$UUID",
    "domain": "$DOMAIN",
    "ws_path": "/ws",
    "xray_running": $XRAY_OK,
    "default_clean_ips": ["104.26.0.1", "1.1.1.1", "speed.cloudflare.com"],
    "default_sni": "www.speedtest.net"
}
INFOEOF

echo ""
echo "╔════════════════════════════════════════╗"
echo "║   ✅ READY - Panel:8000 Xray:9000     ║"
echo "╚════════════════════════════════════════╝"
echo ""

# پنل روی 8000
cd /app
exec python3 -m uvicorn app:app --host 0.0.0.0 --port 8000
