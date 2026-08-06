from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import os
import json
from pathlib import Path

app = FastAPI(title="Quantum Multi-Protocol Panel")

def load_info():
    try:
        return json.loads(Path("/app/data/info.json").read_text())
    except:
        return {
            "uuid": "00000000-0000-0000-0000-000000000000",
            "domain": os.getenv("RAILWAY_PUBLIC_DOMAIN", "localhost"),
            "ssh_port": "2222",
            "ssh_user": "root",
            "ssh_pass": "quantum123",
            "vless_port": "8443",
            "chisel_port": "8888",
            "ws_path": "/ws",
            "all_running": False
        }

@app.get("/api/configs")
async def get_configs(address: str = "", port: str = ""):
    info = load_info()
    uuid = info.get("uuid", "")
    host = info.get("domain", "localhost")
    ws_path = info.get("ws_path", "/ws")
    
    if not address:
        address = host
    if not port:
        port = "35093"
    
    configs = {
        "vless_ws": {
            "name": "VLESS + WebSocket",
            "icon": "🟣",
            "protocol": "vless",
            "link": f"vless://{uuid}@{address}:{port}?encryption=none&security=none&type=ws&path={ws_path}&host={host}#Quantum-VLESS",
            "config": {
                "type": "vless",
                "address": address,
                "port": int(port),
                "uuid": uuid,
                "encryption": "none",
                "network": "ws",
                "security": "none",
                "path": ws_path,
                "host": host
            },
            "v2rayng": {
                "address": address,
                "port": int(port),
                "id": uuid,
                "network": "ws",
                "path": ws_path,
                "host": host
            }
        },
        "socks5_chisel": {
            "name": "SOCKS5 (Chisel Tunnel)",
            "icon": "🟢",
            "protocol": "socks5",
            "link": f"socks5://{address}:{port}#Quantum-Chisel",
            "config": {
                "type": "socks5",
                "address": address,
                "port": int(port),
                "note": "Use with Chisel Client or direct SOCKS5"
            },
            "chisel_command": f"chisel client {address}:{port} 1080:socks"
        },
        "ssh_tunnel": {
            "name": "SSH Tunnel",
            "icon": "🔵",
            "protocol": "ssh",
            "link": f"ssh://{info.get('ssh_user','root')}:{info.get('ssh_pass','quantum123')}@{address}:{port}#Quantum-SSH",
            "config": {
                "type": "ssh",
                "address": address,
                "port": int(port),
                "username": info.get("ssh_user", "root"),
                "password": info.get("ssh_pass", "quantum123")
            },
            "command": f"ssh -D 1080 -p {port} {info.get('ssh_user','root')}@{address}"
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
        .header{{text-align:center;margin-bottom:20px}}
        .title{{font-size:2.5em;background:linear-gradient(135deg,#6600cc,#00ccff,#ff00cc,#6600cc);background-size:300% 300%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:gradientShift 4s ease infinite;letter-spacing:6px}}
        @keyframes gradientShift{{0%{{background-position:0% 50%}}50%{{background-position:100% 50%}}100%{{background-position:0% 50%}}}}
        .panel{{background:rgba(5,5,20,0.9);border:1px solid rgba(102,0,204,0.3);border-radius:20px;padding:30px;margin-bottom:20px;box-shadow:0 0 60px rgba(102,0,204,0.2);backdrop-filter:blur(20px)}}
        .form-row{{display:flex;gap:10px;margin-bottom:15px;flex-wrap:wrap}}
        .form-group{{flex:1;min-width:150px}}
        .form-group label{{display:block;color:#6600cc;font-size:0.7em;margin-bottom:5px;text-transform:uppercase;letter-spacing:2px}}
        .form-group input{{width:100%;padding:12px;background:rgba(0,0,0,0.6);border:1px solid rgba(102,0,204,0.3);border-radius:8px;color:#00ccff;font-family:'Courier New',monospace;font-size:0.9em}}
        .form-group input:focus{{outline:none;border-color:#6600cc;box-shadow:0 0 15px rgba(102,0,204,0.3)}}
        .btn{{background:#6600cc;color:white;border:none;padding:14px;border-radius:15px;cursor:pointer;font-family:'Courier New',monospace;font-size:0.9em;width:100%;transition:all 0.3s}}
        .btn:hover{{background:#9900ff;box-shadow:0 0 25px rgba(102,0,204,0.5)}}
        .tabs{{display:flex;gap:8px;margin:20px 0;flex-wrap:wrap}}
        .tab{{flex:1;min-width:120px;padding:15px;background:rgba(102,0,204,0.2);border:1px solid rgba(102,0,204,0.3);border-radius:15px;text-align:center;cursor:pointer;transition:all 0.3s;color:#aaa}}
        .tab.active{{background:#6600cc;color:white;border-color:#6600cc;box-shadow:0 0 20px rgba(102,0,204,0.4)}}
        .tab:hover:not(.active){{background:rgba(102,0,204,0.4)}}
        .tab .icon{{font-size:1.5em;display:block;margin-bottom:5px}}
        .tab .name{{font-size:0.7em;letter-spacing:1px}}
        .config-box{{background:rgba(0,0,0,0.7);border:1px solid rgba(102,0,204,0.2);border-radius:12px;padding:20px;position:relative;display:none}}
        .config-box.active{{display:block}}
        .config-label{{color:#6600cc;font-size:0.8em;margin-bottom:10px;text-transform:uppercase;letter-spacing:2px}}
        .config-value{{color:#00ff41;font-size:0.75em;word-break:break-all;line-height:1.8;max-height:200px;overflow-y:auto;background:rgba(0,0,0,0.5);padding:15px;border-radius:8px;white-space:pre-wrap}}
        .copy-btn{{position:absolute;top:15px;right:15px;background:#6600cc;color:white;border:none;padding:8px 15px;border-radius:10px;cursor:pointer;font-size:0.7em;transition:all 0.3s}}
        .copy-btn:hover{{background:#9900ff}}
        .info-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(100px,1fr));gap:8px;margin-bottom:15px}}
        .info-card{{background:rgba(0,0,0,0.6);border:1px solid rgba(102,0,204,0.2);border-radius:10px;padding:10px;text-align:center}}
        .info-card .label{{color:#666;font-size:0.6em;text-transform:uppercase}}
        .info-card .value{{color:#00ccff;font-size:0.75em;margin-top:3px;word-break:break-all}}
    </style>
</head>
<body>
    <canvas id="matrixCanvas"></canvas>
    
    <div class="container">
        <div class="panel">
            <div class="header">
                <h1 class="title">QUANTUM PRO</h1>
                <p style="color:#6600cc;margin-top:5px;font-size:0.8em">Multi-Protocol VPN Panel</p>
            </div>
            
            <div class="info-grid">
                <div class="info-card"><div class="label">UUID</div><div class="value">{info.get('uuid','')[:16]}...</div></div>
                <div class="info-card"><div class="label">Domain</div><div class="value">{info.get('domain','')[:20]}...</div></div>
                <div class="info-card"><div class="label">VLESS</div><div class="value">{info.get('vless_port','8443')}</div></div>
                <div class="info-card"><div class="label">SSH</div><div class="value">{info.get('ssh_port','2222')}</div></div>
                <div class="info-card"><div class="label">Chisel</div><div class="value">{info.get('chisel_port','8888')}</div></div>
                <div class="info-card"><div class="label">Status</div><div class="value" style="color:{'#00ff41' if info.get('all_running') else '#ff0040'}">{'🟢 ON' if info.get('all_running') else '🔴 OFF'}</div></div>
            </div>
            
            <div class="form-row">
                <div class="form-group"><label>Address</label><input type="text" id="address" value="metro.proxy.rlwy.net"></div>
                <div class="form-group"><label>Port</label><input type="text" id="port" value="35093"></div>
            </div>
            
            <button class="btn" onclick="generateAll()">🚀 Generate All Configurations</button>
            
            <div class="tabs" id="tabs-container"></div>
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
        
        let allConfigs={{}},activeTab='';
        
        async function generateAll(){{
            const a=document.getElementById('address').value||'metro.proxy.rlwy.net';
            const p=document.getElementById('port').value||'35093';
            const r=await fetch(`/api/configs?address=${{a}}&port=${{p}}`);
            allConfigs=await r.json();
            renderTabs();
        }}
        
        function renderTabs(){{
            const tabsDiv=document.getElementById('tabs-container');
            const configsDiv=document.getElementById('configs-container');
            tabsDiv.innerHTML='';
            configsDiv.innerHTML='';
            
            let first=true;
            for(const[key,cfg] of Object.entries(allConfigs)){{
                const tab=document.createElement('div');
                tab.className='tab'+(first?' active':'');
                tab.onclick=(e)=>switchTab(key,e);
                tab.innerHTML=`<span class="icon">${{cfg.icon}}</span><span class="name">${{cfg.name}}</span>`;
                tabsDiv.appendChild(tab);
                
                const box=document.createElement('div');
                box.className='config-box'+(first?' active':'');
                box.id='box-'+key;
                let displayText=cfg.link;
                if(cfg.command)displayText=cfg.command;
                if(cfg.chisel_command)displayText=cfg.chisel_command;
                box.innerHTML=`<div class="config-label">${{cfg.icon}} ${{cfg.name}}</div><button class="copy-btn" onclick="copyConfig('${{key}}',this)">COPY</button><div class="config-value">${{displayText}}</div>`;
                configsDiv.appendChild(box);
                
                first=false;
            }}
        }}
        
        function switchTab(key,e){{
            document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
            document.querySelectorAll('.config-box').forEach(b=>b.classList.remove('active'));
            e.target.closest('.tab').classList.add('active');
            document.getElementById('box-'+key).classList.add('active');
        }}
        
        function copyConfig(key,btn){{
            if(allConfigs[key]){{
                let text=allConfigs[key].link;
                if(allConfigs[key].command)text=allConfigs[key].command;
                if(allConfigs[key].chisel_command)text=allConfigs[key].chisel_command;
                navigator.clipboard.writeText(text);
                btn.textContent='✓ COPIED';
                btn.style.background='#00ff41';btn.style.color='#000';
                setTimeout(()=>{{btn.textContent='COPY';btn.style.background='#6600cc';btn.style.color='#fff';}},2000);
            }}
        }}
        
        setTimeout(generateAll,300);
    </script>
</body>
</html>"""
    return HTMLResponse(html)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
