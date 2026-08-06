@app.get("/api/configs")
async def configs(address: str = "", sni: str = "", tls: str = "1", cdn: str = "0"):
    i = load_info()
    h = i.get("domain","localhost")
    use_tls = tls == "1"
    use_cdn = cdn == "1"
    
    if not sni: sni = "www.speedtest.net"
    
    # تعیین Address و Port
    if use_cdn and use_tls:
        # CDN + TLS: IP تمیز + 443
        if not address: address = "speed.cloudflare.com"
        port = 443
    elif use_cdn and not use_tls:
        # CDN بدون TLS: IP تمیز + 80
        if not address: address = "speed.cloudflare.com"
        port = 80
    elif not use_cdn and use_tls:
        # TLS بدون CDN: TCP Proxy + TLS
        if not address: address = "metro.proxy.rlwy.net"
        port = 35093
    else:
        # بدون TLS بدون CDN: TCP Proxy مستقیم
        if not address: address = "metro.proxy.rlwy.net"
        port = 35093
    
    security = "tls" if use_tls else "none"
    
    # VMess
    vmess_config = {
        "v": "2", "ps": "Quantum-VMess",
        "add": address, "port": port, "id": i["uuid_vmess"], "aid": 0,
        "net": "ws", "type": "none", "host": h, "path": i["vmess"]["path"],
        "tls": "tls" if use_tls else "none",
        "sni": sni if use_tls else "",
        "fp": "chrome" if use_tls else ""
    }
    vmess_link = "vmess://" + base64.b64encode(json.dumps(vmess_config).encode()).decode()
    
    # VLESS
    vless_link = f"vless://{i['uuid']}@{address}:{port}?encryption=none&security={security}"
    if use_tls: vless_link += f"&sni={sni}&fp=chrome"
    vless_link += f"&type=ws&host={h}&path={i['vless']['path']}#Quantum"
    
    # Trojan
    trojan_link = f"trojan://{i['trojan_pass']}@{address}:{port}?security={security}"
    if use_tls: trojan_link += f"&sni={sni}"
    trojan_link += f"&type=ws&host={h}&path={i['trojan']['path']}#Quantum"
    
    # Shadowsocks
    ss_b64 = base64.b64encode(f"aes-256-gcm:{i['ss_pass']}".encode()).decode()
    ss_link = f"ss://{ss_b64}@{address}:{port}?path={i['ss']['path']}&host={h}#Quantum"
    
    return JSONResponse({
        "vless": {"name":"VLESS","icon":"🟣","link":vless_link},
        "vmess": {"name":"VMess","icon":"🟠","link":vmess_link},
        "trojan": {"name":"Trojan","icon":"🔴","link":trojan_link},
        "ss": {"name":"Shadowsocks","icon":"🟡","link":ss_link},
        "settings": {
            "address": address, "port": port, "sni": sni,
            "host": h, "tls": use_tls, "cdn": use_cdn,
            "mode": f"{'TLS' if use_tls else 'NoTLS'}+{'CDN' if use_cdn else 'Direct'}"
        }
    })
