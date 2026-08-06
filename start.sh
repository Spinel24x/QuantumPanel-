#!/bin/bash
set -e

echo "╔════════════════════════════════════════╗"
echo "║   🕳️  QUANTUM SLIPSTREAM  🕳️        ║"
echo "║   TCP Tunnel + WS + TCP Proxy        ║"
echo "╚════════════════════════════════════════╝"

DOMAIN=${RAILWAY_PUBLIC_DOMAIN:-localhost}
TCP_PROXY_PORT=${RAILWAY_TCP_PROXY_PORT:-8443}
PANEL_PORT=${PORT:-9000}

mkdir -p /app/data /var/log

# ============================================
# تولید UUID
# ============================================
if [ ! -f /app/data/uuid.txt ]; then
    cat /proc/sys/kernel/random/uuid > /app/data/uuid.txt
fi
UUID=$(cat /app/data/uuid.txt)

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

echo "🔑 UUID: $UUID"
echo "🌐 Domain: $DOMAIN"
echo "🔌 TCP Proxy Port: $TCP_PROXY_PORT"
[ -n "$USERNAME" ] && echo "🔐 Auth: $USERNAME" || echo "🔓 No Authentication"

# ============================================
# استارت SlipStream Server
# ============================================
echo "🚀 Starting SlipStream Server..."

if [ -n "$USERNAME" ] && [ -n "$PASSWORD" ]; then
    slipstream server --port 8443 --socks5 127.0.0.1:1080 --auth "${USERNAME}:${PASSWORD}" > /var/log/slipstream.log 2>&1 &
else
    slipstream server --port 8443 --socks5 127.0.0.1:1080 > /var/log/slipstream.log 2>&1 &
fi

sleep 3

SLIPSTREAM_OK=false
if pgrep -f slipstream > /dev/null; then
    echo "   ✅ SlipStream started (PID: $(pgrep -f slipstream))"
    SLIPSTREAM_OK=true
else
    echo "   ❌ SlipStream failed to start"
    cat /var/log/slipstream.log
fi

# ============================================
# ذخیره اطلاعات
# ============================================
cat > /app/data/info.json << INFOEOF
{
    "uuid": "$UUID",
    "domain": "$DOMAIN",
    "port": "$TCP_PROXY_PORT",
    "protocol": "slipstream",
    "transport": "ws",
    "slipstream_running": $SLIPSTREAM_OK,
    "username": "$USERNAME",
    "password": "$PASSWORD",
    "server_port": 8443
}
INFOEOF

echo ""
echo "╔════════════════════════════════════════╗"
echo "║   ✅ SLIPSTREAM IS READY              ║"
echo "║   Port:    8443 (Internal)            ║"
echo "║   Panel:   $PANEL_PORT                ║"
echo "║   Status:  $SLIPSTREAM_OK             ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "📱 SlipNet Config:"
echo "   Server: $DOMAIN"
echo "   Port: $TCP_PROXY_PORT"
echo "   UUID: $UUID"
echo ""

cd /app
exec python3 -m uvicorn app:app --host 0.0.0.0 --port ${PANEL_PORT}
