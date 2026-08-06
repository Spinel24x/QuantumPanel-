@app.get("/api/config")
async def get_config(
    address: str = "",
    port: str = ""
):
    info = load_info()
    
    uuid = info.get("uuid", "")
    domain = info.get("domain", "localhost")
    host = info.get("host", domain)
    ws_path = info.get("ws_path", "/ws")
    
    # مقادیر پیش‌فرض برای TCP Proxy
    if not address:
        address = "metro.proxy.rlwy.net"
    if not port:
        port = "35093"
    
    # کانفیگ خروجی
    vless_link = f"vless://{uuid}@{address}:{port}?encryption=none&security=none&type=ws&path={ws_path}&host={host}#Quantum-VLESS"
    
    json_config = {
        "outbounds": [{
            "protocol": "vless",
            "settings": {
                "vnext": [{
                    "address": address,
                    "port": int(port),
                    "users": [{
                        "id": uuid,
                        "encryption": "none",
                        "level": 0
                    }]
                }]
            },
            "streamSettings": {
                "network": "ws",
                "security": "none",
                "wsSettings": {
                    "path": ws_path,
                    "headers": {"Host": host}
                }
            },
            "tag": "proxy"
        }]
    }
    
    return JSONResponse({
        "vless_link": vless_link,
        "json_config": json_config,
        "config": {
            "address": address,
            "port": port,
            "uuid": uuid,
            "host": host,
            "path": ws_path
        }
    })
