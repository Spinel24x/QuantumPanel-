from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import os
import json
from pathlib import Path

# ============================================
# CREATE APP FIRST!
# ============================================
app = FastAPI(title="Quantum VLESS Panel")

# ============================================
# Helper
# ============================================
def load_info():
    try:
        return json.loads(Path("/app/data/info.json").read_text())
    except:
        return {
            "uuid": "00000000-0000-0000-0000-000000000000",
            "domain": os.getenv("RAILWAY_PUBLIC_DOMAIN", "localhost"),
            "port": "35093",
            "ws_path": "/ws",
            "host": os.getenv("RAILWAY_PUBLIC_DOMAIN", "localhost"),
            "xray_running": False
        }

# ============================================
# API
# ============================================
@app.get("/api/config")
async def get_config(address: str = "", port: str = ""):
    info = load_info()
    
    uuid = info.get("uuid", "")
    domain = info.get("domain", "localhost")
    host = info.get("host", domain)
    ws_path = info.get("ws_path", "/ws")
    
    if not address:
        address = "metro.proxy.rlwy.net"
    if not port:
        port = info.get("port", "35093")
    
    vless_link = f"vless://{uuid}@{address}:{port}?encryption=none&security=none&type=ws&path={ws_path}&host={host}#Quantum-VLESS"
    
    return JSONResponse({
        "vless_link": vless_link,
        "config": {
            "address": address,
            "port": port,
            "uuid": uuid,
            "host": host,
            "path": ws_path
        }
    })

# ============================================
# Main Page
# ============================================
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    info = load_info()
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quantum VLESS</title>
    <style>
        *{{margin:0;padding:0;box-sizing:border-box}}
        body{{background:#000;color:#fff;font-family:'Courier New',monospace;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}}
        .panel{{background:rgba(5,5,20,0.9);border:1px solid rgba(102,0,204,0.3);border-radius:20px;padding:30px;max-width:600px;width:100%;box-shadow:0 0 60px rgba(102,0,204,0.2)}}
        .title{{font-size:2.5em;text-align:center;background:linear-gradient(135deg,#6600cc,#00ccff,#ff00cc,#6600cc);background-size:300% 300%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:gradientShift 4s ease infinite;margin-bottom:20px;letter-spacing:6px}}
        @keyframes gradientShift{{0%{{background-position:0% 50%}}50%{{background-position:100% 50%}}100%{{background-position:0% 50%}}}}
        .form-group{{margin-bottom:15px}}
        .form-group label{{display:block;color:#6600cc;font-size:0.8em;margin-bottom:5px;text-transform:uppercase;letter-spacing:2px}}
        .form-group input{{width:100%;padding:12px;background:rgba(0,0,0,0.6);border:1px solid rgba(102,0,204,0.3);border-radius:8px;color:#00ccff;font-family:'Courier New',monospace;font-size:0.9em}}
        .form-group input:focus{{outline:none;border-color:#6600cc;box-shadow:0 0 15px rgba(102,0,204,0.3)}}
        .btn{{background:#6600cc;color:white;border:none;padding:12px 24px;border-radius:20px;cursor:pointer;font-family:'Courier New',monospace;font-size:0.85em;width:100%;margin-top:10px;transition:all 0.3s}}
        .btn:hover{{background:#9900ff;box-shadow:0 0 20px rgba(102,0,204,0.5)}}
        .result{{background:rgba(0,0,0,0.7);border:1px solid rgba(102,0,204,0.2);border-radius:12px;padding:20px;margin-top:20px;display:none;position:relative}}
        .result .label{{color:#6600cc;font-size:0.8em;margin-bottom:10px;text-transform:uppercase}}
        .result .value{{color:#00ff41;font-size:0.8em;word-break:break-all;line-height:1.8}}
        .copy-btn{{position:absolute;top:10px;right:10px;background:#6600cc;color:white;border:none;padding:8px 18px;border-radius:20px;cursor:pointer;font-family:'Courier New',monospace;font-size:0.75em}}
        .copy-btn:hover{{background:#9900ff}}
        .info{{color:#666;font-size:0.7em;text-align:center;margin-top:15px}}
    </style>
</head>
<body>
    <div class="panel">
        <h1 class="title">QUANTUM</h1>
        
        <div class="form-group">
            <label>Address (IP/Domain)</label>
            <input type="text" id="address" value="metro.proxy.rlwy.net" placeholder="IP or Domain">
        </div>
        
        <div class="form-group">
            <label>Port</label>
            <input type="text" id="port" value="35093" placeholder="Port">
        </div>
        
        <button class="btn" onclick="generate()">🚀 Generate Config</button>
        
        <div class="result" id="result">
            <div class="label">🔗 VLESS Link</div>
            <button class="copy-btn" onclick="copy()">COPY</button>
            <div class="value" id="link"></div>
        </div>
        
        <p class="info">Host: {info.get('host','')} | Path: {info.get('ws_path','/ws')} | UUID: {info.get('uuid','')[:16]}...</p>
    </div>
    
    <script>
        let currentLink = '';
        async function generate(){{
            const a=document.getElementById('address').value;
            const p=document.getElementById('port').value;
            const r=await fetch(`/api/config?address=${{a}}&port=${{p}}`);
            const d=await r.json();
            currentLink=d.vless_link;
            document.getElementById('link').textContent=currentLink;
            document.getElementById('result').style.display='block';
        }}
        function copy(){{
            if(currentLink){{navigator.clipboard.writeText(currentLink);alert('Copied!');}}
        }}
        setTimeout(generate,300);
    </script>
</body>
</html>"""
    return HTMLResponse(html)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
