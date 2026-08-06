#!/bin/bash
set -e

echo "╔════════════════════════════════════════╗"
echo "║   🕳️  QUANTUM MULTI-PROTOCOL  🕳️    ║"
echo "╚════════════════════════════════════════╝"

DOMAIN=${RAILWAY_PUBLIC_DOMAIN:-localhost}
mkdir -p /app/data /etc/xray /var/log

# UUID
if [ ! -f /app/data/uuid.txt ]; then
    cat /proc/sys/kernel/random/uuid > /app/data/uuid.txt
fi
UUID=$(cat /app/data/uuid.txt)

echo "🔑 UUID: $UUID"
echo "🌐 Domain: $DOMAIN"

# ============================================
# ۱. Xray - VLESS + WS (Port 8443)
# ============================================
cat > /etc/xray/config.json << XRAYEOF
{
    "log": {"loglevel": "warning"},
    "inbounds": [{
        "port": 8443,
        "listen": "0.0.0.0",
        "protocol": "vless",
        "settings": {"clients": [{"id": "$UUID", "level": 0}], "decryption": "none"},
        "streamSettings": {"network": "ws", "wsSettings": {"path": "/ws"}}
    }],
    "outbounds": [{"protocol": "freedom"}]
}
XRAYEOF

/opt/xray/xray run -config /etc/xray/config.json &
sleep 1
echo "✅ VLESS on port 8443"

# ============================================
# ۲. SSH Server (Port 2222)
# ============================================
/usr/sbin/sshd -D -e &
sleep 1
echo "✅ SSH on port 2222"

# ============================================
# ۳. Chisel (Port 8443 - same as Xray? No, port 8888)
# ============================================
chisel server --port 8888 --socks5 &
sleep 1
echo "✅ Chisel SOCKS5 on port 8888"

# ============================================
# Save Info
# ============================================
cat > /app/data/info.json << INFOEOF
{
    "uuid": "$UUID",
    "domain": "$DOMAIN",
    "ssh_port": "2222",
    "ssh_user": "root",
    "ssh_pass": "quantum123",
    "vless_port": "8443",
    "chisel_port": "8888",
    "ws_path": "/ws",
    "all_running": true
}
INFOEOF

echo ""
echo "╔════════════════════════════════════════╗"
echo "║   ✅ ALL SERVICES RUNNING             ║"
echo "║   VLESS:  8443                        ║"
echo "║   SSH:    2222                        ║"
echo "║   Chisel: 8888                        ║"
echo "╚════════════════════════════════════════╝"
echo ""

cd /app
exec python3 -m uvicorn app:app --host 0.0.0.0 --port 9000
