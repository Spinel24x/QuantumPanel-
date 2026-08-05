#!/usr/bin/env python3
import json
import os
import uuid
from pathlib import Path

# ============================================
# اطلاعات پایه
# ============================================
DOMAIN = os.getenv("RAILWAY_PUBLIC_DOMAIN", "localhost")
TCP_PORT = os.getenv("RAILWAY_TCP_PORT", "2222")
PASSWORD = "Quantum2024!@#"
UUID = Path("/app/data/uuid.txt").read_text().strip()

# ============================================
# دایرکتوری کانفیگ‌ها
# ============================================
CONFIG_DIR = Path("/app/data/configs")
CONFIG_DIR.mkdir(exist_ok=True)

# ============================================
# تولید همه کانفیگ‌ها
# ============================================

configs = {}

# --------------- ۱. SSH-Direct ---------------
configs["ssh_direct"] = {
    "name": "SSH-Direct",
    "protocol": "ssh",
    "link": f"ssh://root:{PASSWORD}@{DOMAIN}:{TCP_PORT}#Quantum-Direct",
    "command": f"ssh -D 1080 -p {TCP_PORT} root@{DOMAIN}",
    "config": {
        "host": DOMAIN,
        "port": int(TCP_PORT),
        "username": "root",
        "password": PASSWORD,
        "udpgw_port": 7300
    }
}

# --------------- ۲. SSH-Proxy ---------------
configs["ssh_proxy"] = {
    "name": "SSH-Proxy",
    "protocol": "ssh-socks5",
    "link": f"ssh://root:{PASSWORD}@{DOMAIN}:{TCP_PORT}?socks5=1080#Quantum-Proxy",
    "command": f"ssh -D 1080 -p {TCP_PORT} root@{DOMAIN}",
    "config": {
        "host": DOMAIN,
        "port": int(TCP_PORT),
        "username": "root",
        "password": PASSWORD,
        "socks5_port": 1080,
        "udpgw_port": 7300
    }
}

# --------------- ۳. SSH-Payload ---------------
payload = f"CONNECT [host] HTTP/1.1[crlf]Host: {DOMAIN}[crlf][crlf]"
configs["ssh_payload"] = {
    "name": "SSH-Payload",
    "protocol": "ssh-payload",
    "config": {
        "host": DOMAIN,
        "port": int(TCP_PORT),
        "username": "root",
        "password": PASSWORD,
        "payload": payload,
        "sni": "cloudflare.com",
        "udpgw_port": 7300
    }
}

# --------------- ۴. SSH-Proxy-Payload ---------------
configs["ssh_proxy_payload"] = {
    "name": "SSH-Proxy-Payload",
    "protocol": "ssh-socks5-payload",
    "config": {
        "host": DOMAIN,
        "port": int(TCP_PORT),
        "username": "root",
        "password": PASSWORD,
        "payload": payload,
        "sni": "cloudflare.com",
        "socks5_port": 1080,
        "udpgw_port": 7300
    }
}

# --------------- ۵. SSH-WebSocket ---------------
configs["ssh_ws"] = {
    "name": "SSH-WebSocket",
    "protocol": "ssh-ws",
    "config": {
        "host": "speed.cloudflare.com",
        "port": 443,
        "username": "root",
        "password": PASSWORD,
        "sni": "cloudflare.com",
        "ws_path": "/ws",
        "ws_host": DOMAIN,
        "udpgw_port": 7300
    }
}

# --------------- ۶. SSH-TLS ---------------
configs["ssh_tls"] = {
    "name": "SSH-TLS",
    "protocol": "ssh-tls",
    "config": {
        "host": DOMAIN,
        "port": 443,
        "username": "root",
        "password": PASSWORD,
        "sni": DOMAIN,
        "udpgw_port": 7300
    }
}

# --------------- ۷. NapsternetV ---------------
configs["napsternetv"] = {
    "name": "NapsternetV",
    "protocol": "ssh",
    "config": {
        "host": DOMAIN,
        "port": int(TCP_PORT),
        "username": "root",
        "password": PASSWORD,
        "udpgw_port": 7300,
        "sni": "cloudflare.com"
    }
}

# --------------- ۸. HTTP Injector ---------------
configs["http_injector"] = {
    "name": "HTTP Injector",
    "protocol": "ssh",
    "config": {
        "host": DOMAIN,
        "port": int(TCP_PORT),
        "username": "root",
        "password": PASSWORD,
        "payload": payload,
        "sni": "cloudflare.com",
        "udpgw_port": 7300
    }
}

# --------------- ۹. HTTP Custom ---------------
configs["http_custom"] = {
    "name": "HTTP Custom",
    "protocol": "ssh",
    "config": {
        "host": DOMAIN,
        "port": int(TCP_PORT),
        "username": "root",
        "password": PASSWORD,
        "payload": payload,
        "sni": "cloudflare.com",
        "udpgw_port": 7300
    }
}

# ============================================
# ذخیره همه کانفیگ‌ها
# ============================================
for key, cfg in configs.items():
    with open(CONFIG_DIR / f"{key}.json", "w") as f:
        json.dump(cfg, f, indent=2)

# ذخیره اطلاعات کلی
info = {
    "domain": DOMAIN,
    "tcp_port": TCP_PORT,
    "password": PASSWORD,
    "uuid": UUID,
    "ssh_ports": [2222, 443, 80],
    "udpgw_port": 7300,
    "ws_port": 8888,
    "panel_port": os.getenv("PORT", "8000"),
    "protocols": list(configs.keys())
}

with open(CONFIG_DIR / "info.json", "w") as f:
    json.dump(info, f, indent=2)

# ============================================
# نمایش خلاصه
# ============================================
print(f"""
╔════════════════════════════════════════╗
║   📋 CONFIGURATIONS GENERATED         ║
║   Domain: {DOMAIN}
║   TCP Port: {TCP_PORT}
║   Password: {PASSWORD}
║   UUID: {UUID[:16]}...
║   Protocols: {len(configs)}
╚════════════════════════════════════════╝
""")

# لیست پروتکل‌ها
for i, (key, cfg) in enumerate(configs.items(), 1):
    print(f"   {i}. {cfg['name']}")
