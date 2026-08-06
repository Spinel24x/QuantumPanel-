#!/bin/bash
set -e

echo "╔════════════════════════════════════════╗"
echo "║   🕳️  QUANTUM PRO  🕳️              ║"
echo "╚════════════════════════════════════════╝"

mkdir -p /app/data /etc/xray /var/log /var/run/sshd

DOMAIN=${RAILWAY_PUBLIC_DOMAIN:-localhost}

[ ! -f /app/data/uuid.txt ] && cat /proc/sys/kernel/random/uuid > /app/data/uuid.txt
UUID=$(cat /app/data/uuid.txt)

[ ! -f /app/data/uuid_vmess.txt ] && cat /proc/sys/kernel/random/uuid > /app/data/uuid_vmess.txt
UUID_VMESS=$(cat /app/data/uuid_vmess.txt)

[ ! -f /app/data/trojan_pass.txt ] && cat /proc/sys/kernel/random/uuid | tr -d '-' | head -c 16 > /app/data/trojan_pass.txt
TROJAN_PASS=$(cat /app/data/trojan_pass.txt)

[ ! -f /app/data/ss_pass.txt ] && cat /proc/sys/kernel/random/uuid | tr -d '-' | head -c 16 > /app/data/ss_pass.txt
SS_PASS=$(cat /app/data/ss_pass.txt)

echo "🔑 VLESS UUID: $UUID"
echo "🔑 VMess UUID: $UUID_VMESS"
echo "🔑 Trojan Pass: $TROJAN_PASS"
echo "🔑 SS Pass: $SS_PASS"

# ============================================
# Xray روی 8443
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
            "settings": {"method": "aes-256-gcm", "password": "$SS_PASS"},
            "streamSettings": {"network": "ws", "wsSettings": {"path": "/ss"}}}
    ],
    "outbounds": [{"protocol": "freedom", "tag": "direct"}]
}
XRAYEOF

/opt/xray/xray run -config /etc/xray/config.json &
echo "✅ Xray on 8443"

# SSH
/usr/sbin/sshd -D -e > /var/log/sshd.log 2>&1 &
echo "✅ SSH on 22"

# Save UUIDs and passwords
cat > /app/data/info.json << EOF
{
    "uuid": "$UUID",
    "uuid_vmess": "$UUID_VMESS",
    "trojan_pass": "$TROJAN_PASS",
    "ss_pass": "$SS_PASS"
}
EOF

echo "✅ Info saved"
echo ""
cd /app
exec python3 -m uvicorn app:app --host 0.0.0.0 --port 9000
