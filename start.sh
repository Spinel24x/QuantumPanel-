#!/bin/bash
set -e

echo "╔════════════════════════════════════════╗"
echo "║   🕳️  QUANTUM VLESS CORE  🕳️        ║"
echo "║   VLESS + TLS + WS + TCP Proxy       ║"
echo "╚════════════════════════════════════════╝"

# ============================================
# متغیرها
# ============================================
DOMAIN=${RAILWAY_PUBLIC_DOMAIN:-localhost}
TCP_PROXY_PORT=${RAILWAY_TCP_PROXY_PORT:-8443}
PANEL_PORT=${PORT:-8000}

# ============================================
# ساخت دایرکتوری‌ها
# ============================================
mkdir -p /app/data /var/log/nginx /var/log/xray /etc/xray

# ============================================
# تولید UUID
# ============================================
if [ ! -f /app/data/uuid.txt ]; then
    cat /proc/sys/kernel/random/uuid > /app/data/uuid.txt
fi

UUID=$(cat /app/data/uuid.txt)

echo "🔑 UUID: $UUID"
echo "🌐 Domain: $DOMAIN"
echo "🔌 TCP Proxy Port: $TCP_PROXY_PORT"

# ============================================
# ساخت کانفیگ Xray
# ============================================
cat > /etc/xray/config.json << XRAYEOF
{
    "log": {
        "loglevel": "warning"
    },
    "inbounds": [{
        "port": 10000,
        "listen": "127.0.0.1",
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
                "path": "/ws"
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

# ============================================
# کپی nginx.conf
# ============================================
cp /app/nginx.conf /etc/nginx/nginx.conf
echo "✅ Nginx config copied"

# ============================================
# استارت Xray
# ============================================
echo "🚀 Starting Xray..."
/opt/xray/xray run -config /etc/xray/config.json > /var/log/xray/xray.log 2>&1 &
sleep 2

if pgrep -f xray > /dev/null; then
    echo "   ✅ Xray started (PID: $(pgrep -f xray))"
else
    echo "   ❌ Xray failed to start"
fi

# ============================================
# استارت Nginx
# ============================================
echo "🚀 Starting Nginx..."
nginx -t 2>/dev/null && nginx -g "daemon off;" > /var/log/nginx/nginx.log 2>&1 &
sleep 2

if pgrep -f nginx > /dev/null; then
    echo "   ✅ Nginx started (PID: $(pgrep -f nginx | head -1))"
else
    echo "   ❌ Nginx failed to start"
fi

# ============================================
# ذخیره اطلاعات برای پنل
# ============================================
cat > /app/data/info.json << INFOEOF
{
    "uuid": "$UUID",
    "domain": "$DOMAIN",
    "tcp_proxy_port": "$TCP_PROXY_PORT",
    "ws_path": "/ws",
    "sni": "$DOMAIN",
    "protocol": "vless",
    "security": "tls",
    "type": "ws",
    "network": "ws",
    "fingerprint": "chrome"
}
INFOEOF

echo ""
echo "╔════════════════════════════════════════╗"
echo "║   ✅ QUANTUM VLESS IS READY           ║"
echo "║   VLESS Port:  8443 (Nginx)           ║"
echo "║   Xray Port:   10000 (Internal)       ║"
echo "║   Panel Port:  $PANEL_PORT            ║"
echo "║   WS Path:     /ws                    ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "📱 VLESS Link:"
echo "vless://$UUID@$DOMAIN:$TCP_PROXY_PORT?encryption=none&security=tls&sni=$DOMAIN&fp=chrome&type=ws&path=/ws&host=$DOMAIN#Quantum-VLESS"
echo ""

# ============================================
# استارت پنل
# ============================================
cd /app
exec python3 -m uvicorn app:app --host 0.0.0.0 --port 9000
