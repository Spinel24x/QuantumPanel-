#!/bin/bash
set -e

echo "╔════════════════════════════════════════╗"
echo "║     🕳️  QUANTUM CORE v2.0  🕳️        ║"
echo "╚════════════════════════════════════════╝"

mkdir -p /app/data /var/log

# UUID
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
echo "🔐 Password: $PASSWORD"

# ============================================
# استارت SSH Server
# ============================================
echo "🔐 Starting SSH Server..."
/usr/sbin/sshd -D -e &
sleep 1
echo "   ✅ SSH on ports: 2222, 443, 80"

# ============================================
# تولید کانفیگ
# ============================================
echo "📝 Generating config..."
python3 -c "
import json, os
from pathlib import Path

domain = os.getenv('RAILWAY_PUBLIC_DOMAIN', 'localhost')
tcp_port = os.getenv('RAILWAY_TCP_PORT', '2222')
password = 'Quantum2024!@#'
uuid = Path('/app/data/uuid.txt').read_text().strip()

configs = {
    'domain': domain,
    'tcp_port': tcp_port,
    'password': password,
    'uuid': uuid
}

Path('/app/data').mkdir(exist_ok=True)
with open('/app/data/configs.json', 'w') as f:
    json.dump(configs, f, indent=2)

print(f'   ✅ Config saved: {domain}:{tcp_port}')
"

echo ""
echo "╔════════════════════════════════════════╗"
echo "║   ✅ ALL SERVICES STARTED             ║"
echo "║   SSH:     2222, 443, 80              ║"
echo "║   PANEL:   $RAILWAY_HTTP_PORT         ║"
echo "╚════════════════════════════════════════╝"

# استارت پنل
cd /app
exec python3 -m uvicorn app:app --host 0.0.0.0 --port $RAILWAY_HTTP_PORT
