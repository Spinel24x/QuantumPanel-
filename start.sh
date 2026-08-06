#!/bin/bash
set -e

echo "╔════════════════════════════════════════╗"
echo "║   🕳️  QUANTUM PANEL v3  🕳️         ║"
echo "╚════════════════════════════════════════╝"

DOMAIN=quantumpanel-production.up.railway.app
mkdir -p /app/data /etc/xray /var/log /var/run/sshd

# UUID
if [ ! -f /app/data/uuid.txt ]; then
    cat /proc/sys/kernel/random/uuid > /app/data/uuid.txt
fi
UUID=$(cat /app/data/uuid.txt)

echo "🔑 UUID: $UUID"

# ============================================
# VLESS + WS on port 8443
# ============================================
cat > /etc/xray/config.json << XRAYEOF
{
    "log": {"loglevel": "warning"},
    "inbounds": [{
        "port": 8443, "listen": "0.0.0.0", "protocol": "vless",
        "settings": {"clients": [{"id": "$UUID", "level": 0}], "decryption": "none"},
        "streamSettings": {"network": "ws", "wsSettings": {"path": "/ws"}}
    }],
    "outbounds": [{"protocol": "freedom"}]
}
XRAYEOF
/opt/xray/xray run -config /etc/xray/config.json &
echo "✅ VLESS on 8443 (metro.proxy.rlwy.net:35093)"

# ============================================
# SSH on port 22
# ============================================
/usr/sbin/sshd -D -e &
echo "✅ SSH on 22 (sakura.proxy.rlwy.net:53742)"

# ============================================
# Chisel on port 8888
# ============================================
chisel server --port 8888 --socks5 &
echo "✅ Chisel on 8888 (tramway.proxy.rlwy.net:29499)"

# Save info
cat > /app/data/info.json << EOF
{
    "uuid": "$UUID",
    "domain": "$DOMAIN",
    "ws_path": "/ws",
    "vless": {"host": "metro.proxy.rlwy.net", "port": 35093},
    "ssh": {"host": "sakura.proxy.rlwy.net", "port": 53742, "user": "root", "pass": "quantum123"},
    "chisel": {"host": "tramway.proxy.rlwy.net", "port": 29499}
}
EOF

echo ""
echo "╔════════════════════════════════════════╗"
echo "║   ✅ ALL SERVICES RUNNING             ║"
echo "║   VLESS:  metro:35093                 ║"
echo "║   SSH:    sakura:53742                ║"
echo "║   Chisel: tramway:29499               ║"
echo "╚════════════════════════════════════════╝"
echo ""

cd /app
exec python3 -m uvicorn app:app --host 0.0.0.0 --port 9000
