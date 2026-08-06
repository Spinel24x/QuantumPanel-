#!/bin/bash
set -e

echo "╔════════════════════════════════════════╗"
echo "║   🕳️  QUANTUM GOST TUNNEL  🕳️      ║"
echo "║   SOCKS5 + WSS + TCP Proxy           ║"
echo "╚════════════════════════════════════════╝"

DOMAIN=${RAILWAY_PUBLIC_DOMAIN:-localhost}
TCP_PROXY_PORT=${RAILWAY_TCP_PROXY_PORT:-8443}
PANEL_PORT=${PORT:-8000}

mkdir -p /app/data

# ============================================
# خوندن user/pass (اگر تنظیم شده باشه)
# ============================================
if [ -f /app/data/users.json ]; then
    USERNAME=$(python3 -c "import json; print(json.load(open('/app/data/users.json')).get('username',''))")
    PASSWORD=$(python3 -c "import json; print(json.load(open('/app/data/users.json')).get('password',''))")
else
    USERNAME=""
    PASSWORD=""
fi

echo "🌐 Domain: $DOMAIN"
echo "🔌 TCP Proxy Port: $TCP_PROXY_PORT"
[ -n "$USERNAME" ] && echo "🔐 Auth: $USERNAME" || echo "🔓 No Authentication"

# ============================================
# استارت GOST
# ============================================
if [ -n "$USERNAME" ] && [ -n "$PASSWORD" ]; then
    echo "🚀 Starting GOST with authentication..."
    gost -L "wss://${USERNAME}:${PASSWORD}@:8443?path=/ws" -F "socks5://:1080" > /var/log/gost.log 2>&1 &
else
    echo "🚀 Starting GOST without authentication..."
    gost -L "wss://:8443?path=/ws" -F "socks5://:1080" > /var/log/gost.log 2>&1 &
fi

sleep 2

if pgrep -f gost > /dev/null; then
    echo "   ✅ GOST started (PID: $(pgrep -f gost))"
else
    echo "   ❌ GOST failed to start"
fi

# ============================================
# ذخیره info
# ============================================
cat > /app/data/info.json << INFOEOF
{
    "domain": "$DOMAIN",
    "port": "$TCP_PROXY_PORT",
    "ws_path": "/ws",
    "protocol": "socks5",
    "security": "wss",
    "username": "$USERNAME",
    "password": "$PASSWORD"
}
INFOEOF

echo ""
echo "╔════════════════════════════════════════╗"
echo "║   ✅ GOST TUNNEL IS READY             ║"
echo "║   Port:    8443 (Internal)            ║"
echo "║   Panel:   $PANEL_PORT                ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "📱 SOCKS5 Address:"
echo "   $DOMAIN:$TCP_PROXY_PORT"
echo "   Path: /ws"
echo ""

cd /app
exec python3 -m uvicorn app:app --host 0.0.0.0 --port 9000
