#!/bin/bash
set -e

echo "╔════════════════════════════════════════╗"
echo "║     🕳️  QUANTUM CORE v2.0  🕳️        ║"
echo "║   SSH Tunnel Intelligent Engine       ║"
echo "╚════════════════════════════════════════╝"

mkdir -p /app/data /var/log

# تولید UUID
if [ ! -f /app/data/uuid.txt ]; then
    python3 -c "import uuid; print(str(uuid.uuid4()))" > /app/data/uuid.txt
fi

UUID=$(cat /app/data/uuid.txt)
PASSWORD="Quantum2024!@#"
DOMAIN=${RAILWAY_PUBLIC_DOMAIN:-localhost}
RAILWAY_TCP_PORT=${RAILWAY_TCP_PORT:-2222}
RAILWAY_HTTP_PORT=${PORT:-8000}

echo "🔐 Domain: $DOMAIN"
echo "🔐 TCP Port: $RAILWAY_TCP_PORT"

# ============================================
# استارت SSH Server
# ============================================
echo "🔐 Starting SSH Server..."
/usr/sbin/sshd -D -e &
sleep 1
echo "   ✅ SSH on ports: 2222, 443, 80"

# ============================================
# استارت WebSocket Tunnel
# ============================================
echo "🔗 Starting WebSocket Tunnel..."
wstunnel server ws://0.0.0.0:8888 127.0.0.1:2222 > /var/log/wstunnel.log 2>&1 &
sleep 1
echo "   ✅ WS Tunnel on port 8888 → SSH 2222"

# ============================================
# تولید کانفیگ‌ها
# ============================================
echo "📝 Generating configurations..."
python3 /app/config_generator.py 2>/dev/null || echo "   ⚠️ Config generator skipped"

echo ""
echo "╔════════════════════════════════════════╗"
echo "║   ✅ ALL SERVICES STARTED             ║"
echo "║   SSH:     2222, 443, 80              ║"
echo "║   WS:      8888                       ║"
echo "║   PANEL:   $RAILWAY_HTTP_PORT         ║"
echo "╚════════════════════════════════════════╝"

# استارت پنل
cd /app
exec python3 -m uvicorn app:app --host 0.0.0.0 --port $RAILWAY_HTTP_PORT
