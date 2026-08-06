#!/bin/bash
set -e

echo "╔════════════════════════════════════════╗"
echo "║   🕳️  QUANTUM VLESS  🕳️            ║"
echo "╚════════════════════════════════════════╝"

DOMAIN=${RAILWAY_PUBLIC_DOMAIN:-localhost}
PANEL_PORT=${PORT:-8000}
XRAY_PORT=8443

mkdir -p /app/data /etc/xray /var/log/xray

# UUID
if [ ! -f /app/data/uuid.txt ]; then
    cat /proc/sys/kernel/random/uuid > /app/data/uuid.txt
fi
UUID=$(cat /app/data/uuid.txt)

echo "🔑 UUID: $UUID"
echo "🌐 Domain: $DOMAIN"
echo "🔌 Xray Port: $XRAY_PORT"

# ============================================
# Xray Config - VLESS + WS روی 8443
# ============================================
cat > /etc/xray/config.json << XRAYEOF
{
    "log": {"loglevel": "warning"},
    "inbounds": [{
        "port": 8443,
        "listen": "0.0.0.0",
        "protocol": "vless",
        "settings": {
            "clients": [{
                "id": "$UUID",
                "level": 0
            }],
            "decryption": "none"
        },
        "streamSettings": {
            "network": "ws",
            "wsSettings": {
                "path": "/ws",
                "headers": {
                    "Host": "$DOMAIN"
                }
            }
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

XRAY_OK=false
if pgrep -f xray > /dev/null; then
    echo "   ✅ Xray started on port $XRAY_PORT"
    XRAY_OK=true
else
    echo "   ❌ Xray failed"
fi

# ذخیره info
cat > /app/data/info.json << INFOEOF
{
    "uuid": "$UUID",
    "domain": "$DOMAIN",
    "xray_port": "$XRAY_PORT",
    "ws_path": "/ws",
    "xray_running": $XRAY_OK,
    "host": "$DOMAIN",
    "default_sni": "www.google.com"
}
INFOEOF

echo ""
echo "📱 VLESS Link (TCP Proxy):"
echo "vless://$UUID@metro.proxy.rlwy.net:35093?encryption=none&security=none&type=ws&path=/ws&host=$DOMAIN#Quantum-VLESS"
echo ""

cd /app
exec python3 -m uvicorn app:app --host 0.0.0.0 --port ${PANEL_PORT}
