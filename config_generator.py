import json, base64

def load_info():
    try:
        with open("/app/data/info.json") as f:
            data_info = json.load(f)
    except:
        data_info = {}
    
    try:
        with open("/app/info.json") as f:
            base_info = json.load(f)
    except:
        base_info = {}
    
    return {**base_info, **data_info}

def load_ips():
    try:
        with open("/app/ips.json") as f:
            return json.load(f)
    except:
        return {"clean_ips": [], "default_sni": ""}

def build_connection(use_cf=False, clean_ip="", sni=""):
    info = load_info()
    ips = load_ips()
    
    railway = info.get("railway_domain", "localhost")
    worker = info.get("worker_domain", railway)
    
    if use_cf:
        if clean_ip:
            address = clean_ip
        elif ips.get("clean_ips"):
            address = ips["clean_ips"][0]
        else:
            address = worker
        
        host = railway
        sni_value = sni if sni else (ips.get("default_sni") or worker)
        port = 443
        security = "tls"
    else:
        address = info.get("tcp_host", railway)
        host = railway
        sni_value = sni if sni else ""
        port = info.get("tcp_port", 35093)
        security = "tls" if sni_value else "none"
    
    return {
        "address": address,
        "host": host,
        "sni": sni_value,
        "port": port,
        "security": security
    }

def generate_vless(uuid, conn):
    link = f"vless://{uuid}@{conn['address']}:{conn['port']}?encryption=none&security={conn['security']}"
    if conn['security'] == "tls":
        link += f"&sni={conn['sni']}&fp=chrome"
    link += f"&type=ws&host={conn['host']}&path=/vless#Quantum"
    return link

def generate_vmess(uuid, conn):
    config = {
        "v": "2", "ps": "Quantum-VMess",
        "add": conn['address'], "port": conn['port'],
        "id": uuid, "aid": 0,
        "net": "ws", "type": "none",
        "host": conn['host'], "path": "/vmess",
        "tls": conn['security'],
        "sni": conn['sni'] if conn['security'] == "tls" else "",
        "fp": "chrome" if conn['security'] == "tls" else ""
    }
    return "vmess://" + base64.b64encode(json.dumps(config).encode()).decode()

def generate_trojan(password, conn):
    link = f"trojan://{password}@{conn['address']}:{conn['port']}?security={conn['security']}"
    if conn['security'] == "tls":
        link += f"&sni={conn['sni']}"
    link += f"&type=ws&host={conn['host']}&path=/trojan#Quantum"
    return link

def generate_ss_ws(password, conn):
    ss_b64 = base64.b64encode(f"aes-256-gcm:{password}".encode()).decode()
    link = f"ss://{ss_b64}@{conn['address']}:{conn['port']}?path=/ss&host={conn['host']}#Quantum"
    return link

def generate_ss_tcp(password, info):
    ss_b64 = base64.b64encode(f"aes-256-gcm:{password}".encode()).decode()
    host = info.get("ss_tcp_host", "")
    port = info.get("ss_tcp_port", 53742)
    link = f"ss://{ss_b64}@{host}:{port}?network=tcp#Quantum-SS-TCP"
    return link

def generate_all(uuid, uuid_vmess, trojan_pass, ss_pass, use_cf=False, clean_ip="", sni=""):
    info = load_info()
    conn = build_connection(use_cf, clean_ip, sni)
    
    return {
        "vless": {"name": "VLESS", "icon": "🟣", "link": generate_vless(uuid, conn)},
        "vmess": {"name": "VMess", "icon": "🟠", "link": generate_vmess(uuid_vmess, conn)},
        "trojan": {"name": "Trojan", "icon": "🔴", "link": generate_trojan(trojan_pass, conn)},
        "ss_ws": {"name": "Shadowsocks WS", "icon": "🟡", "link": generate_ss_ws(ss_pass, conn)},
        "ss_tcp": {"name": "Shadowsocks TCP", "icon": "🟢", "link": generate_ss_tcp(ss_pass, info)},
        "connection": conn
    }
