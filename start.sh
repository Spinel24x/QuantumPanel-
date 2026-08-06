#!/bin/bash
set -e

echo "╔════════════════════════════════════════╗"
echo "║   🕳️  QUANTUM CHISEL TUNNEL  🕳️     ║"
echo "║   SOCKS5 + WS + TCP Proxy            ║"
echo "╚════════════════════════════════════════╝"

DOMAIN=${RAILWAY_PUBLIC_DOMAIN:-localhost}
TCP_PROXY_PORT=${RAILWAY_TCP_PROXY_PORT:-8443}
PANEL_PORT=${PORT:-9000}

mkdir -p /app/data

# ============================================
# خوندن user/pass
# ============================================
if [ -f /app/data/users.json ]; then
    USERNAME=$(python3 -c "import json; d=json.load(open('/app/data/users.json')); print(d.get('username',''))")
    PASSWORD=$(python3 -c "import json; d=json.load(open('/app/data/users.json')); print(d.get('password',''))")
else
    USERNAME=""
    PASSWORD=""
fi

echo "🌐 Domain: $DOMAIN"
echo "🔌 TCP Proxy Port: $TCP_PROXY_PORT"
[ -n "$USERNAME" ] && echo "🔐 Auth: $USERNAME" || echo "🔓 No Authentication"

# ============================================
# استارت Chisel Server
# ============================================
if [ -n "$USERNAME" ] && [ -n "$PASSWORD" ]; then
    echo "🚀 Starting Chisel with authentication..."
    chisel server --port 8443 --socks5 --auth "${USERNAME}:${PASSWORD}" > /var/log/chisel.log 2>&1 &
else
    echo "🚀 Starting Chisel without authentication..."
    chisel server --port 8443 --socks5 > /var/log/chisel.log 2>&1 &
fi

sleep 2

CHISEL_OK=false
if pgrep -f chisel > /dev/null; then
    echo "   ✅ Chisel started (PID: $(pgrep -f chisel))"
    CHISEL_OK=true
else
    echo "   ❌ Chisel failed to start"
    cat /var/log/chisel.log
fi

# ============================================
# ذخیره info (همه مقادیر یکسان)
# ============================================
cat > /app/data/info.json << INFOEOF
{
    "domain": "$DOMAIN",
    "port": "$TCP_PROXY_PORT",
    "ws_path": "/ws",
    "protocol": "socks5",
    "security": "ws",
    "chisel_running": $CHISEL_OK,
    "username": "$USERNAME",
    "password": "$PASSWORD"
}
INFOEOF

echo ""
echo "╔════════════════════════════════════════╗"
echo "║   ✅ CHISEL TUNNEL IS READY           ║"
echo "║   Port:    8443 (Internal)            ║"
echo "║   Panel:   $PANEL_PORT                ║"
echo "║   Status:  $CHISEL_OK                 ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "📱 SOCKS5 Address:"
echo "   $DOMAIN:$TCP_PROXY_PORT"
echo ""

cd /app
exec python3 -m uvicorn app:app --host 0.0.0.0 --port ${PANEL_PORT}
