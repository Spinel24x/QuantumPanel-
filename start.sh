#!/bin/bash
set -e

echo "╔════════════════════════════════════════╗"
echo "║     🕳️  QUANTUM CORE v2.0  🕳️        ║"
echo "║   SSH Tunnel Intelligent Engine       ║"
echo "╚════════════════════════════════════════╝"

# ============================================
# ساخت دایرکتوری‌ها
# ============================================
mkdir -p /app/data /var/log

# ============================================
# تولید UUID و کلیدها
# ============================================
if [ ! -f /app/data/uuid.txt ]; then
    python3 -c "import uuid; print(str(uuid.uuid4()))" > /app/data/uuid.txt
fi

if [ ! -f /app/data/ssh_key ]; then
    ssh-keygen -t rsa -b 4096 -f /app/data/ssh_key -N "" -q
fi

UUID=$(cat /app/data/uuid.txt)
PASSWORD="Quantum2024!@#"
DOMAIN=${RAILWAY_PUBLIC_DOMAIN:-localhost}

# ============================================
# دریافت اطلاعات Railway
# ============================================
RAILWAY_TCP_PORT=${RAILWAY_TCP_PORT:-2222}
RAILWAY_HTTP_PORT=${PORT:-8000}

# ============================================
# تنظیم فایروال (باز کردن پورت‌ها)
# ============================================
echo "🔧 Configuring ports..."

# ============================================
# استارت SSH Server (چند پورت)
# ============================================
echo "🔐 Starting SSH Server..."
/usr/sbin/sshd -D -e &
echo "   ✅ SSH on ports: 2222, 443, 80"

# ============================================
# استارت UDP Gateway (BadVPN)
# ============================================
echo "🌊 Starting UDP Gateway..."
badvpn-udpgw --listen-addr 127.0.0.1:7300 --max-clients 100 &
echo "   ✅ UDP Gateway on port 7300"

# ============================================
# استارت WebSocket Tunnel (wstunnel)
# ============================================
echo "🔗 Starting WebSocket Tunnel..."
wstunnel server ws://0.0.0.0:8888 127.0.0.1:2222 &
echo "   ✅ WS Tunnel on port 8888 → SSH 2222"

# ============================================
# تولید همه کانفیگ‌ها
# ============================================
echo "📝 Generating configurations..."

python3 /app/config_generator.py

echo ""
echo "╔════════════════════════════════════════╗"
echo "║   ✅ ALL SERVICES STARTED             ║"
echo "║   SSH:    2222, 443, 80               ║"
echo "║   UDPGW:  7300                        ║"
echo "║   WS:     8888                        ║"
echo "║   PANEL:  $RAILWAY_HTTP_PORT          ║"
echo "╚════════════════════════════════════════╝"

# ============================================
# استارت پنل
# ============================================
cd /app
exec python3 -m uvicorn app:app --host 0.0.0.0 --port $RAILWAY_HTTP_PORT
