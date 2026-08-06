#!/bin/bash
set -e

echo "╔════════════════════════════════════════╗"
echo "║   🕳️  QUANTUM TCP TUNNEL  🕳️        ║"
echo "║   Direct TCP Tunnel + Proxy          ║"
echo "╚════════════════════════════════════════╝"

DOMAIN=${RAILWAY_PUBLIC_DOMAIN:-localhost}
TCP_PROXY_PORT=${RAILWAY_TCP_PROXY_PORT:-8443}
PANEL_PORT=${PORT:-9000}

mkdir -p /app/data /var/log

# UUID
if [ ! -f /app/data/uuid.txt ]; then
    cat /proc/sys/kernel/random/uuid > /app/data/uuid.txt
fi
UUID=$(cat /app/data/uuid.txt)

# user/pass
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

# ============================================
# استارت TCP Tunnel با socat
# ============================================
echo "🚀 Starting TCP Tunnel..."

# TCP → SOCKS5 (با socat)
socat TCP-LISTEN:8443,fork,reuseaddr SOCKS5:127.0.0.1:1080 &
sleep 1

# یه SOCKS5 ساده با python
python3 -c "
import socket, select, struct, sys

def handle_client(client_socket):
    # SOCKS5 handshake
    client_socket.recv(262)
    client_socket.send(b'\x05\x00')
    data = client_socket.recv(4)
    mode = data[1]
    if mode == 1:  # CONNECT
        addr_type = data[3]
        if addr_type == 3:  # Domain
            domain_len = client_socket.recv(1)[0]
            domain = client_socket.recv(domain_len).decode()
            port = struct.unpack('>H', client_socket.recv(2))[0]
        elif addr_type == 1:  # IPv4
            addr = socket.inet_ntoa(client_socket.recv(4))
            port = struct.unpack('>H', client_socket.recv(2))[0]
            domain = addr
        
        try:
            remote = socket.create_connection((domain, port))
            client_socket.send(b'\x05\x00\x00\x01' + b'\x00\x00\x00\x00' + struct.pack('>H', port))
            
            sockets = [client_socket, remote]
            while True:
                r, _, _ = select.select(sockets, [], [], 30)
                if not r: break
                for s in r:
                    data = s.recv(4096)
                    if not data: return
                    if s is client_socket:
                        remote.send(data)
                    else:
                        client_socket.send(data)
        except:
            client_socket.send(b'\x05\x05\x00\x01\x00\x00\x00\x00\x00\x00')
    client_socket.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('127.0.0.1', 1080))
server.listen(10)
print('SOCKS5 proxy on 127.0.0.1:1080')

while True:
    client, addr = server.accept()
    import threading
    threading.Thread(target=handle_client, args=(client,)).start()
" > /var/log/socks5.log 2>&1 &

sleep 1
echo "✅ TCP Tunnel on 8443 → SOCKS5"

# ذخیره info
cat > /app/data/info.json << INFOEOF
{
    "uuid": "$UUID",
    "domain": "$DOMAIN",
    "port": "$TCP_PROXY_PORT",
    "protocol": "socks5",
    "transport": "tcp",
    "tunnel_running": true,
    "username": "$USERNAME",
    "password": "$PASSWORD"
}
INFOEOF

echo ""
echo "📱 SOCKS5: $DOMAIN:$TCP_PROXY_PORT"
echo ""

cd /app
exec python3 -m uvicorn app:app --host 0.0.0.0 --port ${PANEL_PORT}
