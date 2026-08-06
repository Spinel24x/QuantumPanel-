from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
import uvicorn
import os
import json
from pathlib import Path

app = FastAPI(title="Quantum Chisel Panel")

# ============================================
# Helper
# ============================================
def load_info():
    try:
        return json.loads(Path("/app/data/info.json").read_text())
    except:
        return {
            "domain": os.getenv("RAILWAY_PUBLIC_DOMAIN", "localhost"),
            "port": os.getenv("RAILWAY_TCP_PROXY_PORT", "8443"),
            "ws_path": "/ws",
            "security": "ws",
            "username": "",
            "password": "",
            "chisel_running": False
        }

def load_users():
    try:
        return json.loads(Path("/app/data/users.json").read_text())
    except:
        return {"username": "", "password": ""}

def save_users(username, password):
    Path("/app/data").mkdir(exist_ok=True)
    Path("/app/data/users.json").write_text(json.dumps({"username": username, "password": password}))

# ============================================
# API
# ============================================
@app.get("/api/config")
async def get_config():
    info = load_info()
    
    domain = info.get("domain", "localhost")
    port = info.get("port", "8443")
    username = info.get("username", "")
    password = info.get("password", "")
    chisel_running = info.get("chisel_running", False)
    security = info.get("security", "ws")
    
    # لینک SOCKS5
    if username and password:
        socks5_link = f"socks5://{username}:{password}@{domain}:{port}#Quantum-Chisel"
    else:
        socks5_link = f"socks5://{domain}:{port}#Quantum-Chisel"
    
    # کانفیگ JSON
    socks5_config = {
        "protocol": "socks5",
        "address": domain,
        "port": int(port),
        "security": security,
        "username": username if username else None,
        "password": password if password else None,
        "chisel_running": chisel_running,
        "note": "Requires Chisel Client on your device"
    }
    
    return JSONResponse({
        "socks5_link": socks5_link,
        "config": socks5_config,
        "status": {
            "chisel_running": chisel_running,
            "domain": domain,
            "port": port,
            "security": security
        }
    })

@app.post("/api/set-auth")
async def set_auth(username: str = Form(...), password: str = Form(...)):
    save_users(username, password)
    
    info = load_info()
    info["username"] = username
    info["password"] = password
    Path("/app/data/info.json").write_text(json.dumps(info))
    
    return RedirectResponse("/", status_code=303)

@app.post("/api/remove-auth")
async def remove_auth():
    save_users("", "")
    
    info = load_info()
    info["username"] = ""
    info["password"] = ""
    Path("/app/data/info.json").write_text(json.dumps(info))
    
    return RedirectResponse("/", status_code=303)

# ============================================
# صفحه اصلی
# ============================================
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    info = load_info()
    users = load_users()
    
    chisel_status = "🟢 Running" if info.get("chisel_running") else "🔴 Stopped"
    auth_status = "🔐 Enabled" if info.get("username") else "🔓 None"
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quantum Chisel Panel</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            background: #000;
            color: #fff;
            font-family: 'Courier New', monospace;
            min-height: 100vh;
            overflow-x: hidden;
        }}
        
        canvas {{ position: fixed; top: 0; left: 0; z-index: 0; }}
        
        .container {{
            position: relative; z-index: 2;
            display: flex; flex-direction: column; align-items: center;
            min-height: 100vh; padding: 20px;
            pointer-events: none;
        }}
        
        .container > * {{ pointer-events: auto; }}
        
        .blackhole-wrapper {{
            width: 100%; max-width: 500px; height: 350px;
            position: relative; margin-top: 20px;
        }}
        
        .panel-section {{
            width: 100%; max-width: 750px;
            background: rgba(5, 5, 20, 0.85);
            border: 1px solid rgba(102, 0, 204, 0.3);
            border-radius: 20px; padding: 30px;
            backdrop-filter: blur(20px);
            box-shadow: 0 0 60px rgba(102, 0, 204, 0.15), inset 0 0 30px rgba(0, 0, 0, 0.5);
            margin-top: -30px; z-index: 3; margin-bottom: 20px;
        }}
        
        .title {{
            font-size: 3.5em; font-weight: bold; text-align: center;
            background: linear-gradient(135deg, #6600cc, #00ccff, #ff00cc, #6600cc);
            background-size: 300% 300%;
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            animation: gradientShift 4s ease infinite;
            margin-bottom: 5px; letter-spacing: 8px;
        }}
        
        @keyframes gradientShift {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        
        .subtitle {{
            text-align: center; color: rgba(102, 0, 204, 0.7);
            margin-bottom: 20px; font-size: 0.85em; letter-spacing: 4px;
        }}
        
        .info-grid {{
            display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
            gap: 12px; margin-bottom: 25px;
        }}
        
        .info-card {{
            background: rgba(0, 0, 0, 0.6);
            border: 1px solid rgba(102, 0, 204, 0.2);
            border-radius: 12px; padding: 15px; text-align: center;
            transition: all 0.3s;
        }}
        
        .info-card:hover {{
            border-color: rgba(102, 0, 204, 0.6);
            box-shadow: 0 0 20px rgba(102, 0, 204, 0.2);
        }}
        
        .info-card .label {{
            color: #666; font-size: 0.7em; text-transform: uppercase;
            letter-spacing: 1px; margin-bottom: 5px;
        }}
        
        .info-card .value {{
            font-weight: bold; font-size: 0.9em; word-break: break-all;
        }}
        
        .config-box {{
            background: rgba(0, 0, 0, 0.7);
            border: 1px solid rgba(102, 0, 204, 0.2);
            border-radius: 12px; padding: 20px; margin-bottom: 15px;
            position: relative;
        }}
        
        .config-label {{
            color: #6600cc; font-weight: bold; font-size: 0.8em;
            margin-bottom: 10px; text-transform: uppercase; letter-spacing: 2px;
        }}
        
        .config-value {{
            color: #00ff41; font-size: 0.85em; word-break: break-all; line-height: 1.8;
        }}
        
        .copy-btn {{
            position: absolute; top: 10px; right: 10px;
            background: #6600cc; color: white; border: none;
            padding: 8px 18px; border-radius: 20px; cursor: pointer;
            font-family: 'Courier New', monospace; font-size: 0.75em;
            transition: all 0.3s; letter-spacing: 1px;
        }}
        
        .copy-btn:hover {{ background: #9900ff; box-shadow: 0 0 25px rgba(102, 0, 204, 0.6); transform: scale(1.05); }}
        .copy-btn.copied {{ background: #00ff41; color: #000; }}
        
        .auth-form {{
            display: flex; flex-direction: column; gap: 12px;
        }}
        
        .auth-form input {{
            background: rgba(0, 0, 0, 0.6);
            border: 1px solid rgba(102, 0, 204, 0.3);
            border-radius: 8px; padding: 12px;
            color: #00ccff; font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        
        .auth-form input:focus {{
            outline: none; border-color: #6600cc;
            box-shadow: 0 0 15px rgba(102, 0, 204, 0.3);
        }}
        
        .btn {{
            background: #6600cc; color: white; border: none;
            padding: 12px 24px; border-radius: 20px; cursor: pointer;
            font-family: 'Courier New', monospace; font-size: 0.85em;
            transition: all 0.3s; letter-spacing: 1px;
        }}
        
        .btn:hover {{ background: #9900ff; box-shadow: 0 0 20px rgba(102, 0, 204, 0.5); }}
        .btn-danger {{ background: #cc0066; }}
        .btn-danger:hover {{ background: #ff0099; }}
        
        .footer {{
            text-align: center; margin-top: 40px; color: #333;
            font-size: 0.7em; letter-spacing: 3px;
        }}
        
        .pulse-dot {{
            display: inline-block; width: 8px; height: 8px;
            background: #00ff41; border-radius: 50%;
            animation: pulse 1.5s ease-in-out infinite; margin-right: 5px;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; box-shadow: 0 0 10px #00ff41; }}
            50% {{ opacity: 0.3; box-shadow: 0 0 30px #00ff41; }}
        }}
        
        @media (max-width: 768px) {{
            .title {{ font-size: 2em; }}
            .panel-section {{ padding: 20px; }}
        }}
    </style>
</head>
<body>
    <canvas id="matrixCanvas"></canvas>
    
    <div class="container">
        <div class="blackhole-wrapper">
            <canvas id="blackholeCanvas" width="500" height="350"></canvas>
        </div>
        
        <div class="panel-section">
            <h1 class="title">QUANTUM</h1>
            <p class="subtitle"><span class="pulse-dot"></span> CHISEL SOCKS5 TUNNEL <span class="pulse-dot"></span></p>
            
            <div class="info-grid">
                <div class="info-card">
                    <div class="label">Domain</div>
                    <div class="value" style="color:#00ccff;">{info['domain']}</div>
                </div>
                <div class="info-card">
                    <div class="label">Port</div>
                    <div class="value" style="color:#00ccff;">{info['port']}</div>
                </div>
                <div class="info-card">
                    <div class="label">Protocol</div>
                    <div class="value" style="color:#00ccff;">SOCKS5</div>
                </div>
                <div class="info-card">
                    <div class="label">Security</div>
                    <div class="value" style="color:#00ccff;">WS</div>
                </div>
                <div class="info-card">
                    <div class="label">Chisel</div>
                    <div class="value" id="chisel-status" style="color:{'#00ff41' if info.get('chisel_running') else '#ff0040'};">{chisel_status}</div>
                </div>
                <div class="info-card">
                    <div class="label">Auth</div>
                    <div class="value" style="color:#00ccff;">{auth_status}</div>
                </div>
            </div>
            
            <div class="config-box">
                <div class="config-label">📱 SOCKS5 Configuration (v2rayNG / Custom)</div>
                <button class="copy-btn" onclick="copyConfig(this)">COPY</button>
                <div class="config-value" id="socks5-config">Loading...</div>
            </div>
            
            <div class="config-box">
                <div class="config-label">🔗 SOCKS5 Link</div>
                <button class="copy-btn" onclick="copyLink(this)">COPY</button>
                <div class="config-value" id="socks5-link">Loading...</div>
            </div>
        </div>
        
        <div class="panel-section">
            <h2 style="color:#6600cc; margin-bottom:15px;">🔐 Authentication Settings</h2>
            
            <form class="auth-form" action="/api/set-auth" method="post">
                <input type="text" name="username" placeholder="Username (optional)" value="{users.get('username', '')}">
                <input type="password" name="password" placeholder="Password (optional)" value="{users.get('password', '')}">
                <div style="display:flex; gap:10px;">
                    <button type="submit" class="btn">💾 Save & Restart</button>
                    <button type="button" class="btn btn-danger" onclick="removeAuth()">🗑️ Remove Auth</button>
                </div>
            </form>
            <p style="color:#666; font-size:0.7em; margin-top:10px;">⚠️ Changing auth requires server restart.</p>
        </div>
        
        <p class="footer">⬡ QUANTUM CHISEL ⬡ SOCKS5 + WS ⬡</p>
    </div>
    
    <script>
        // ============================================
        // Matrix Lines
        // ============================================
        const matrixCanvas = document.getElementById('matrixCanvas');
        const matrixCtx = matrixCanvas.getContext('2d');
        matrixCanvas.width = window.innerWidth;
        matrixCanvas.height = window.innerHeight;
        
        const lines = [];
        class Line {{
            constructor() {{
                this.reset();
            }}
            reset() {{
                this.x1=Math.random()*matrixCanvas.width; this.y1=Math.random()*matrixCanvas.height;
                this.x2=Math.random()*matrixCanvas.width; this.y2=Math.random()*matrixCanvas.height;
                this.progress=0; this.speed=Math.random()*0.003+0.002;
                this.color=[[102,0,204],[153,0,255],[0,204,255],[255,0,204],[0,255,204]][Math.floor(Math.random()*5)];
                this.maxLength=Math.random()*0.5+0.1;
            }}
            update(){{ this.progress+=this.speed; if(this.progress>1+this.maxLength) this.reset(); }}
            draw(ctx){{
                const s=Math.max(0,this.progress-this.maxLength),e=Math.min(1,this.progress);
                if(s>=e)return;
                const sx=this.x1+(this.x2-this.x1)*s,sy=this.y1+(this.y2-this.y1)*s;
                const ex=this.x1+(this.x2-this.x1)*e,ey=this.y1+(this.y2-this.y1)*e;
                const alpha=(1-Math.abs(this.progress-0.5)*2)*0.4;
                ctx.beginPath();ctx.moveTo(sx,sy);ctx.lineTo(ex,ey);
                ctx.strokeStyle=`rgba(${{this.color[0]}},${{this.color[1]}},${{this.color[2]}},${{alpha}})`;
                ctx.lineWidth=1.5;ctx.shadowBlur=8;
                ctx.shadowColor=`rgba(${{this.color[0]}},${{this.color[1]}},${{this.color[2]}},0.5)`;
                ctx.stroke();ctx.shadowBlur=0;
            }}
        }}
        for(let i=0;i<50;i++)lines.push(new Line());
        function animateMatrix(){{matrixCtx.fillStyle='rgba(0,0,0,0.05)';matrixCtx.fillRect(0,0,matrixCanvas.width,matrixCanvas.height);lines.forEach(l=>{{l.update();l.draw(matrixCtx);}});requestAnimationFrame(animateMatrix);}}
        animateMatrix();
        window.addEventListener('resize',()=>{{matrixCanvas.width=window.innerWidth;matrixCanvas.height=window.innerHeight;}});
        
        // Blackhole
        const bhCanvas=document.getElementById('blackholeCanvas'),bhCtx=bhCanvas.getContext('2d'),cx=250,cy=175;
        function drawBlackhole(time){{
            bhCtx.clearRect(0,0,bhCanvas.width,bhCanvas.height);
            for(let i=5;i>=0;i--){{
                const r=90+i*25+Math.sin(time*0.02+i)*8;
                const g=bhCtx.createRadialGradient(cx,cy,r*0.3,cx,cy,r);
                g.addColorStop(0,'rgba(102,0,204,0)');g.addColorStop(0.5,`rgba(102,0,204,${{0.08-i*0.01}})`);g.addColorStop(1,'rgba(0,0,0,0)');
                bhCtx.beginPath();bhCtx.arc(cx,cy,r,0,Math.PI*2);bhCtx.fillStyle=g;bhCtx.fill();
            }}
            const dg=bhCtx.createLinearGradient(cx-120,cy,cx+120,cy);
            dg.addColorStop(0,'rgba(0,204,255,0)');dg.addColorStop(0.3,'rgba(102,0,204,0.6)');dg.addColorStop(0.5,'rgba(255,255,255,0.4)');dg.addColorStop(0.7,'rgba(255,0,204,0.6)');dg.addColorStop(1,'rgba(0,204,255,0)');
            bhCtx.save();bhCtx.translate(cx,cy);bhCtx.rotate(time*0.01);bhCtx.beginPath();bhCtx.ellipse(0,0,100,20,0,0,Math.PI*2);bhCtx.fillStyle=dg;bhCtx.fill();bhCtx.restore();
            const hg=bhCtx.createRadialGradient(cx,cy,0,cx,cy,45);
            hg.addColorStop(0,'#000');hg.addColorStop(0.7,'#0a0015');hg.addColorStop(1,'rgba(102,0,204,0.3)');
            bhCtx.beginPath();bhCtx.arc(cx,cy,45,0,Math.PI*2);bhCtx.fillStyle=hg;bhCtx.fill();
            bhCtx.beginPath();bhCtx.arc(cx,cy,48,0,Math.PI*2);bhCtx.strokeStyle=`rgba(153,0,255,${{0.4+Math.sin(time*0.03)*0.2}})`;bhCtx.lineWidth=3;bhCtx.shadowBlur=20;bhCtx.shadowColor='#6600cc';bhCtx.stroke();bhCtx.shadowBlur=0;
            for(let i=0;i<12;i++){{const a=(i/12)*Math.PI*2+time*0.005,pr=55+Math.sin(time*0.04+i)*15,px=cx+Math.cos(a)*pr,py=cy+Math.sin(a)*pr*0.3;bhCtx.beginPath();bhCtx.arc(px,py,2,0,Math.PI*2);bhCtx.fillStyle=`rgba(0,204,255,${{0.6+Math.sin(time*0.05+i)*0.4}})`;bhCtx.fill();}}
        }}
        function animateBlackhole(time){{drawBlackhole(time);requestAnimationFrame(animateBlackhole);}}
        requestAnimationFrame(animateBlackhole);
        
        // ============================================
        // Load configs
        // ============================================
        let socks5Config, socks5Link;
        async function loadConfigs(){{
            try{{
                const r=await fetch('/api/config'),d=await r.json();
                socks5Config=JSON.stringify(d.config,null,2);
                socks5Link=d.socks5_link;
                document.getElementById('socks5-config').textContent=socks5Config;
                document.getElementById('socks5-link').textContent=socks5Link;
                document.getElementById('chisel-status').textContent=d.status.chisel_running ? '🟢 Running' : '🔴 Stopped';
                document.getElementById('chisel-status').style.color=d.status.chisel_running ? '#00ff41' : '#ff0040';
            }}catch(e){{document.getElementById('socks5-config').textContent='Error loading...';}}
        }}
        function copyConfig(b){{if(socks5Config){{navigator.clipboard.writeText(socks5Config);b.textContent='✓ COPIED';b.classList.add('copied');setTimeout(()=>{{b.textContent='COPY';b.classList.remove('copied');}},2000);}}}}
        function copyLink(b){{if(socks5Link){{navigator.clipboard.writeText(socks5Link);b.textContent='✓ COPIED';b.classList.add('copied');setTimeout(()=>{{b.textContent='COPY';b.classList.remove('copied');}},2000);}}}}
        function removeAuth(){{fetch('/api/remove-auth',{{method:'POST'}}).then(()=>location.reload());}}
        
        loadConfigs();
    </script>
</body>
</html>"""
    return HTMLResponse(html)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
