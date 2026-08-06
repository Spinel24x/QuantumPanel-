#!/bin/bash
set -e

echo "╔════════════════════════════════════════╗"
echo "║   🕳️  QUANTUM PANEL v5  🕳️         ║"
echo "╚════════════════════════════════════════╝"

DOMAIN=quantumpanel-production.up.railway.app
mkdir -p /app/data /etc/xray /var/log /var/run/sshd /app/certs

# UUIDs
if [ ! -f /app/data/uuid.txt ]; then
    cat /proc/sys/kernel/random/uuid > /app/data/uuid.txt
fi
UUID=$(cat /app/data/uuid.txt)

if [ ! -f /app/data/uuid_vmess.txt ]; then
    cat /proc/sys/kernel/random/uuid > /app/data/uuid_vmess.txt
fi
UUID_VMESS=$(cat /app/data/uuid_vmess.txt)

if [ ! -f /app/data/trojan_pass.txt ]; then
    cat /proc/sys/kernel/random/uuid | tr -d '-' | head -c 16 > /app/data/trojan_pass.txt
fi
TROJAN_PASS=$(cat /app/data/trojan_pass.txt)

if [ ! -f /app/data/ss_pass.txt ]; then
    cat /proc/sys/kernel/random/uuid | tr -d '-' | head -c 16 > /app/data/ss_pass.txt
fi
SS_PASS=$(cat /app/data/ss_pass.txt)

HY_PASS="quantum2024"

echo "🔑 VLESS: $UUID"
echo "🔑 VMess: $UUID_VMESS"

# ============================================
# Xray - 4 پروتکل روی 8443
# ============================================
cat > /etc/xray/config.json << XRAYEOF
{
    "log": {"loglevel": "warning"},
    "inbounds": [
        {"port": 8443, "listen": "0.0.0.0", "protocol": "vless",
            "settings": {"clients": [{"id": "$UUID", "level": 0}], "decryption": "none"},
            "streamSettings": {"network": "ws", "wsSettings": {"path": "/vless"}}},
        {"port": 8443, "listen": "0.0.0.0", "protocol": "vmess",
            "settings": {"clients": [{"id": "$UUID_VMESS", "level": 0}]},
            "streamSettings": {"network": "ws", "wsSettings": {"path": "/vmess"}}},
        {"port": 8443, "listen": "0.0.0.0", "protocol": "trojan",
            "settings": {"clients": [{"password": "$TROJAN_PASS"}]},
            "streamSettings": {"network": "ws", "wsSettings": {"path": "/trojan"}}},
        {"port": 8443, "listen": "0.0.0.0", "protocol": "shadowsocks",
            "settings": {"method": "aes-256-gcm", "password": "$SS_PASS", "network": "tcp,udp"},
            "streamSettings": {"network": "ws", "wsSettings": {"path": "/ss"}}}
    ],
    "outbounds": [{"protocol": "freedom", "tag": "direct"}]
}
XRAYEOF

/opt/xray/xray run -config /etc/xray/config.json &
echo "✅ Xray: VLESS, VMess, Trojan, SS on 8443"

# ============================================
# Hysteria2 روی پورت 8888 (جایگزین Chisel)
# ============================================
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /app/certs/key.pem -out /app/certs/cert.pem \
  -subj "/CN=quantum" 2>/dev/null

cat > /etc/hysteria.yaml << HYEOF
listen: :8888
tls:
  cert: /app/certs/cert.pem
  key: /app/certs/key.pem
auth:
  type: password
  password: $HY_PASS
bandwidth:
  up: 100 mbps
  down: 500 mbps
HYEOF

hysteria server -c /etc/hysteria.yaml > /var/log/hysteria.log 2>&1 &
sleep 1
echo "✅ Hysteria2 on port 8888"

# ============================================
# SSH
# ============================================
/usr/sbin/sshd -D -e > /var/log/sshd.log 2>&1 &
echo "✅ SSH on port 22"

# ============================================
# Save Info
# ============================================
cat > /app/data/info.json << EOF
{
    "uuid": "$UUID",
    "uuid_vmess": "$UUID_VMESS",
    "trojan_pass": "$TROJAN_PASS",
    "ss_pass": "$SS_PASS",
    "hysteria_pass": "$HY_PASS",
    "domain": "$DOMAIN",
    "vless": {"host": "metro.proxy.rlwy.net", "port": 35093, "path": "/vless"},
    "vmess": {"host": "metro.proxy.rlwy.net", "port": 35093, "path": "/vmess"},
    "trojan": {"host": "metro.proxy.rlwy.net", "port": 35093, "path": "/trojan"},
    "ss": {"host": "metro.proxy.rlwy.net", "port": 35093, "path": "/ss"},
    "hysteria": {"host": "tramway.proxy.rlwy.net", "port": 29499, "password": "$HY_PASS"},
    "ssh": {"host": "sakura.proxy.rlwy.net", "port": 53742, "user": "root", "pass": "quantum123"}
}
EOF

echo ""
echo "╔════════════════════════════════════════╗"
echo "║   6 PROTOCOLS RUNNING                 ║"
echo "║   VLESS, VMess, Trojan, SS            ║"
echo "║   Hysteria2, SSH                      ║"
echo "╚════════════════════════════════════════╝"
echo ""

cd /app
exec python3 -m uvicorn app:app --host 0.0.0.0 --port 9000
