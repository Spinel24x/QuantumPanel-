from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import os
import json
from pathlib import Path

app = FastAPI(title="Quantum Panel Pro")

def load_info():
    try:
        return json.loads(Path("/app/data/info.json").read_text())
    except:
        return {
            "uuid": "00000000-0000-0000-0000-000000000000",
            "domain": os.getenv("RAILWAY_PUBLIC_DOMAIN", "localhost"),
            "port": "35093",
            "ws_path": "/ws",
            "xray_running": False,
            "tcp_proxy_host": "metro.proxy.rlwy.net",
            "tcp_proxy_port": "35093"
        }

@app.get("/api/configs")
async def get_all_configs(address: str = "", port: str = "", sni: str = ""):
    info = load_info()
    uuid = info.get("uuid", "")
    host = info.get("domain", "localhost")
    ws_path = info.get("ws_path", "/ws")
    tcp_host = info.get("tcp_proxy_host", "metro.proxy.rlwy.net")
    tcp_port = info.get("tcp_proxy_port", "35093")
    
    if not address:
        address = tcp_host
    if not port:
        port = tcp_port
    if not sni:
        sni = "www.speedtest.net"
    
    configs = {
        # ۱. VLESS + WS + TCP Proxy (بدون TLS)
        "vless_ws_direct": {
            "name": "VLESS + WS (Direct TCP Proxy)",
            "protocol": "vless",
            "link": f"vless://{uuid}@{tcp_host}:{tcp_port}?encryption=none&security=none&type=ws&path={ws_path}&host={host}#Quantum-Direct",
            "config": {
                "address": tcp_host,
                "port": int(tcp_port),
                "uuid": uuid,
                "network": "ws",
                "security": "none",
                "path": ws_path,
                "host": host
            }
        },
        # ۲. VLESS + WS + Custom Address
        "vless_ws_custom": {
            "name": "VLESS + WS (Custom Address)",
            "protocol": "vless",
            "link": f"vless://{uuid}@{address}:{port}?encryption=none&security=none&type=ws&path={ws_path}&host={host}#Quantum-Custom",
            "config": {
                "address": address,
                "port": int(port),
                "uuid": uuid,
                "network": "ws",
                "security": "none",
                "path": ws_path,
                "host": host
            }
        },
        # ۳. VLESS + TLS + WS (Worker/CDN)
        "vless_tls_ws": {
            "name": "VLESS + TLS + WS (CDN/Worker)",
            "protocol": "vless",
            "link": f"vless://{uuid}@{address}:443?encryption=none&security=tls&sni={sni}&fp=chrome&type=ws&path={ws_path}&host={host}#Quantum-TLS",
            "config": {
                "address": address,
                "port": 443,
                "uuid": uuid,
                "network": "ws",
                "security": "tls",
                "sni": sni,
                "fingerprint": "chrome",
                "path": ws_path,
                "host": host
            }
        },
        # ۴. VMess + WS
        "vmess_ws": {
            "name": "VMess + WS",
            "protocol": "vmess",
            "link": f"vmess://{uuid}@{tcp_host}:{tcp_port}?encryption=none&security=none&type=ws&path={ws_path}&host={host}#Quantum-VMess",
            "config": {
                "address": tcp_host,
                "port": int(tcp_port),
                "uuid": uuid,
                "network": "ws",
                "security": "none",
                "path": ws_path,
                "host": host
            }
        }
    }
    
    return JSONResponse(configs)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    info = load_info()
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quantum Panel Pro</title>
    <style>
        *{{margin:0;padding:0;box-sizing:border-box}}
        body{{background:#000;color:#fff;font-family:'Courier New',monospace;min-height:100vh;padding:20px}}
        canvas{{position:fixed;top:0;left:0;z-index:0}}
        .container{{position:relative;z-index:2;max-width:800px;margin:0 auto}}
        .panel{{background:rgba(5,5,20,0.9);border:1px solid rgba(102,0,204,0.3);border-radius:20px;padding:30px;margin-bottom:20px;box-shadow:0 0 60px rgba(102,0,204,0.2);backdrop-filter:blur(20px)}}
        .title{{font-size:2.5em;text-align:center;background:linear-gradient(135deg,#6600cc,#00ccff,#ff00cc,#6600cc);background-size:300% 300%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:gradientShift 4s ease infinite;margin-bottom:10px;letter-spacing:6px}}
        @keyframes gradientShift{{0%{{background-position:0% 50%}}50%{{background-position:100% 50%}}100%{{background-position:0% 50%}}}}
        .subtitle{{text-align:center;color:#6600cc;margin-bottom:20px;font-size:0.8em}}
        .form-row{{display:flex;gap:10px;margin-bottom:15px;flex-wrap:wrap}}
        .form-group{{flex:1;min-width:150px}}
        .form-group label{{display:block;color:#6600cc;font-size:0.7em;margin-bottom:5px;text-transform:uppercase;letter-spacing:2px}}
        .form-group input{{width:100%;padding:12px;background:rgba(0,0,0,0.6);border:1px solid rgba(102,0,204,0.3);border-radius:8px;color:#00ccff;font-family:'Courier New',monospace;font-size:0.9em}}
        .form-group input:focus{{outline:none;border-color:#6600cc;box-shadow:0 0 15px rgba(102,0,204,0.3)}}
        .btn{{background:#6600cc;color:white;border:none;padding:12px 24px;border-radius:20px;cursor:pointer;font-family:'Courier New',monospace;font-size:0.85em;width:100%;margin-top:10px;transition:all 0.3s}}
        .btn:hover{{background:#9900ff;box-shadow:0 0 20px rgba(102,0,204,0.5)}}
        .tabs{{display:flex;gap:5px;margin-bottom:20px;flex-wrap:wrap}}
        .tab{{background:rgba(102,0,204,0.2);color:#aaa;border:1px solid rgba(102,0,204,0.3);padding:10px 15px;border-radius:10px;cursor:pointer;font-family:'Courier New',monospace;font-size:0.75em;transition:all 0.3s}}
        .tab.active{{background:#6600cc;color:white;border-color:#6600cc}}
        .tab:hover{{background:rgba(102,0,204,0.4)}}
        .config-box{{background:rgba(0,0,0,0.7);border:1px solid rgba(102,0,204,0.2);border-radius:12px;padding:20px;margin-top:15px;position:relative;display:none}}
        .config-box.active{{display:block}}
        .config-label{{color:#6600cc;font-size:0.8em;margin-bottom:10px;text-transform:uppercase;letter-spacing:2px}}
        .config-value{{color:#00ff41;font-size:0.75em;word-break:break-all;line-height:1.8;max-height:300px;overflow-y:auto}}
        .copy-btn{{position:absolute;top:10px;right:10px;background:#6600cc;color:white;border:none;padding:8px 15px;border-radius:15px;cursor:pointer;font-family:'Courier New',monospace;font-size:0.7em}}
        .copy-btn:hover{{background:#9900ff}}
        .info-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;margin-bottom:20px}}
        .info-card{{background:rgba(0,0,0,0.6);border:1px solid rgba(102,0,204,0.2);border-radius:10px;padding:12px;text-align:center}}
        .info-card .label{{color:#666;font-size:0.6em;text-transform:uppercase;letter-spacing:1px}}
        .info-card .value{{color:#00ccff;font-weight:bold;font-size:0.8em;margin-top:3px;word-break:break-all}}
    </style>
</head>
<body>
    <canvas id="matrixCanvas"></canvas>
    
    <div class="container">
        <div class="panel">
            <h1 class="title">QUANTUM PRO</h1>
            <p class="subtitle">⚡ Multi-Protocol VPN Panel ⚡</p>
            
            <div class="info-grid">
                <div class="info-card"><div class="label">UUID</div><div class="value">{info.get('uuid','')[:16]}...</div></div>
                <div class="info-card"><div class="label">Host</div><div class="value">{info.get('domain','')}</div></div>
                <div class="info-card"><div class="label">TCP Proxy</div><div class="value">{info.get('tcp_proxy_port','')}</div></div>
                <div class="info-card"><div class="label">Xray</div><div class="value">{'🟢' if info.get('xray_running') else '🔴'}</div></div>
            </div>
            
            <div class="form-row">
                <div class="form-group"><label>Address</label><input type="text" id="address" value="metro.proxy.rlwy.net"></div>
                <div class="form-group"><label>Port</label><input type="text" id="port" value="35093"></div>
                <div class="form-group"><label>SNI</label><input type="text" id="sni" value="www.speedtest.net"></div>
            </div>
            
            <button class="btn" onclick="generateAll()">🚀 Generate All Configs</button>
            
            <div class="tabs" id="tabs"></div>
            <div id="configs-container"></div>
        </div>
    </div>
    
    <script>
        const matrixCanvas=document.getElementById('matrixCanvas'),matrixCtx=matrixCanvas.getContext('2d');
        matrixCanvas.width=window.innerWidth;matrixCanvas.height=window.innerHeight;
        const lines=[];
        class Line{{
            constructor(){{this.reset()}}
            reset(){{this.x1=Math.random()*matrixCanvas.width;this.y1=Math.random()*matrixCanvas.height;this.x2=Math.random()*matrixCanvas.width;this.y2=Math.random()*matrixCanvas.height;this.progress=0;this.speed=Math.random()*0.003+0.002;this.color=[[102,0,204],[153,0,255],[0,204,255],[255,0,204],[0,255,204]][Math.floor(Math.random()*5)];this.maxLength=Math.random()*0.5+0.1}}
            update(){{this.progress+=this.speed;if(this.progress>1+this.maxLength)this.reset()}}
            draw(ctx){{const s=Math.max(0,this.progress-this.maxLength),e=Math.min(1,this.progress);if(s>=e)return;const sx=this.x1+(this.x2-this.x1)*s,sy=this.y1+(this.y2-this.y1)*s,ex=this.x1+(this.x2-this.x1)*e,ey=this.y1+(this.y2-this.y1)*e,alpha=(1-Math.abs(this.progress-0.5)*2)*0.4;ctx.beginPath();ctx.moveTo(sx,sy);ctx.lineTo(ex,ey);ctx.strokeStyle=`rgba(${{this.color[0]}},${{this.color[1]}},${{this.color[2]}},${{alpha}})`;ctx.lineWidth=1.5;ctx.shadowBlur=8;ctx.shadowColor=`rgba(${{this.color[0]}},${{this.color[1]}},${{this.color[2]}},0.5)`;ctx.stroke();ctx.shadowBlur=0}}
        }}
        for(let i=0;i<50;i++)lines.push(new Line());
        function animateMatrix(){{matrixCtx.fillStyle='rgba(0,0,0,0.05)';matrixCtx.fillRect(0,0,matrixCanvas.width,matrixCanvas.height);lines.forEach(l=>{{l.update();l.draw(matrixCtx);}});requestAnimationFrame(animateMatrix);}}
        animateMatrix();
        window.addEventListener('resize',()=>{{matrixCanvas.width=window.innerWidth;matrixCanvas.height=window.innerHeight;}});
        
        let allConfigs={{}};
        let activeTab='';
        
        async function generateAll(){{
            const a=document.getElementById('address').value;
            const p=document.getElementById('port').value;
            const s=document.getElementById('sni').value;
            const r=await fetch(`/api/configs?address=${{a}}&port=${{p}}&sni=${{s}}`);
            allConfigs=await r.json();
            renderTabs();
        }}
        
        function renderTabs(){{
            const tabsDiv=document.getElementById('tabs');
            const configsDiv=document.getElementById('configs-container');
            tabsDiv.innerHTML='';
            configsDiv.innerHTML='';
            
            let first=true;
            for(const[key,cfg] of Object.entries(allConfigs)){{
                const tab=document.createElement('div');
                tab.className='tab'+(first?' active':'');
                tab.textContent=cfg.name;
                tab.onclick=()=>switchTab(key);
                tabsDiv.appendChild(tab);
                
                const box=document.createElement('div');
                box.className='config-box'+(first?' active':'');
                box.id='box-'+key;
                box.innerHTML=`<div class="config-label">${{cfg.name}}</div><button class="copy-btn" onclick="copyConfig('${{key}}',this)">COPY</button><div class="config-value">${{cfg.link}}</div>`;
                configsDiv.appendChild(box);
                
                first=false;
            }}
        }}
        
        function switchTab(key){{
            document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
            document.querySelectorAll('.config-box').forEach(b=>b.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById('box-'+key).classList.add('active');
        }}
        
        function copyConfig(key,btn){{
            if(allConfigs[key]){{
                navigator.clipboard.writeText(allConfigs[key].link);
                btn.textContent='✓ COPIED';
                setTimeout(()=>btn.textContent='COPY',2000);
            }}
        }}
        
        setTimeout(generateAll,300);
    </script>
</body>
</html>"""
    return HTMLResponse(html)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
