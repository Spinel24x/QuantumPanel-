#!/bin/bash
set -e

echo "╔════════════════════════════════════════╗"
echo "║   🕳️  QUANTUM PANEL v6  🕳️         ║"
echo "╚════════════════════════════════════════╝"

DOMAIN=quantumpanel-production.up.railway.app
mkdir -p /app/data /etc/xray /var/log /var/run/sshd /etc/wireguard

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

echo "🔑 VLESS: $UUID"
echo "🔑 VMess: $UUID_VMESS"

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
            "streamSettings": {"network": "ws", "wsSettings": {"path": "/trojan"}}}
    ],
    "outbounds": [{"protocol": "freedom", "tag": "direct"}]
}
XRAYEOF

/opt/xray/xray run -config /etc/xray/config.json &
echo "✅ Xray: VLESS, VMess, Trojan on 8443"

# WireGuard
PRIVATE_KEY=$(wg genkey)
PUBLIC_KEY=$(echo "$PRIVATE_KEY" | wg pubkey)
CLIENT_PRIVATE=$(wg genkey)
CLIENT_PUBLIC=$(echo "$CLIENT_PRIVATE" | wg pubkey)

ip link add wg0 type wireguard 2>/dev/null || true
ip addr add 10.0.0.1/24 dev wg0 2>/dev/null || true

cat > /etc/wireguard/wg0.conf << WGEOF
[Interface]
PrivateKey = $PRIVATE_KEY
ListenPort = 51820
Address = 10.0.0.1/24
PostUp = iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

[Peer]
PublicKey = $CLIENT_PUBLIC
AllowedIPs = 10.0.0.2/32
WGEOF

wg-quick up wg0 2>/dev/null || true
echo "✅ WireGuard on UDP 51820"

# udp2raw
udp2raw -s -l 0.0.0.0:5555 -r 127.0.0.1:51820 --raw-mode faketcp -k "wgkey123" &
echo "✅ udp2raw on TCP 5555"

# SSH
/usr/sbin/sshd -D -e > /var/log/sshd.log 2>&1 &
echo "✅ SSH on port 22"

cat > /app/data/info.json << EOF
{
    "uuid": "$UUID",
    "uuid_vmess": "$UUID_VMESS",
    "trojan_pass": "$TROJAN_PASS",
    "domain": "$DOMAIN",
    "server_public_key": "$PUBLIC_KEY",
    "client_private_key": "$CLIENT_PRIVATE",
    "vless": {"host": "metro.proxy.rlwy.net", "port": 35093, "path": "/vless"},
    "vmess": {"host": "metro.proxy.rlwy.net", "port": 35093, "path": "/vmess"},
    "trojan": {"host": "metro.proxy.rlwy.net", "port": 35093, "path": "/trojan"},
    "wireguard": {"host": "sakura.proxy.rlwy.net", "port": 53742},
    "ssh": {"host": "sakura.proxy.rlwy.net", "port": 53742, "user": "root", "pass": "quantum123"}
}
EOF

echo ""
echo "╔════════════════════════════════════════╗"
echo "║   5 PROTOCOLS RUNNING                 ║"
echo "╚════════════════════════════════════════╝"
echo ""

cd /app
exec python3 -m uvicorn app:app --host 0.0.0.0 --port 9000
