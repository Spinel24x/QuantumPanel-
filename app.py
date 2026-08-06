from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import os
import json
from pathlib import Path

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
            "ws_path": "/ws",
            "xray_running": False,
            "default_clean_ips": ["104.26.0.1", "1.1.1.1"],
            "default_sni": "www.speedtest.net"
        }

# ============================================
# API
# ============================================
@app.get("/api/config")
async def get_config(
    address: str = "",
    sni: str = "",
    host: str = "",
    ws_path: str = ""
):
    info = load_info()
    
    uuid = info.get("uuid", "")
    domain = info.get("domain", "localhost")
    
    # مقادیر پیش‌فرض
    if not address:
        address = info.get("default_clean_ips", ["104.26.0.1"])[0]
    if not sni:
        sni = info.get("default_sni", "www.speedtest.net")
    if not host:
        host = domain
    if not ws_path:
        ws_path = info.get("ws_path", "/ws")
    
    # لینک VLESS با TLS
    vless_link = f"vless://{uuid}@{address}:443?encryption=none&security=tls&sni={sni}&fp=chrome&type=ws&host={host}&path={ws_path}#Quantum-VLESS"
    
    # کانفیگ JSON
    json_config = {
        "outbounds": [{
            "protocol": "vless",
            "settings": {
                "vnext": [{
                    "address": address,
                    "port": 443,
                    "users": [{
                        "id": uuid,
                        "encryption": "none",
                        "level": 0
                    }]
                }]
            },
            "streamSettings": {
                "network": "ws",
                "security": "tls",
                "tlsSettings": {
                    "serverName": sni,
                    "fingerprint": "chrome",
                    "allowInsecure": False
                },
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
            "port": 443,
            "uuid": uuid,
            "sni": sni,
            "host": host,
            "path": ws_path,
            "security": "tls",
            "type": "ws",
            "fingerprint": "chrome"
        }
    })

# ============================================
# صفحه اصلی
# ============================================
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    info = load_info()
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quantum VLESS Panel</title>
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
            font-size: 2.5em; font-weight: bold; text-align: center;
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
        
        .form-group {{
            margin-bottom: 15px;
        }}
        
        .form-group label {{
            display: block; color: #6600cc; font-size: 0.8em;
            text-transform: uppercase; letter-spacing: 2px; margin-bottom: 5px;
        }}
        
        .form-group input {{
            width: 100%; padding: 12px;
            background: rgba(0, 0, 0, 0.6);
            border: 1px solid rgba(102, 0, 204, 0.3);
            border-radius: 8px; color: #00ccff;
            font-family: 'Courier New', monospace; font-size: 0.9em;
        }}
        
        .form-group input:focus {{
            outline: none; border-color: #6600cc;
            box-shadow: 0 0 15px rgba(102, 0, 204, 0.3);
        }}
        
        .btn {{
            background: #6600cc; color: white; border: none;
            padding: 12px 24px; border-radius: 20px; cursor: pointer;
            font-family: 'Courier New', monospace; font-size: 0.85em;
            transition: all 0.3s; letter-spacing: 1px; width: 100%;
            margin-top: 10px;
        }}
        
        .btn:hover {{ background: #9900ff; box-shadow: 0 0 20px rgba(102, 0, 204, 0.5); transform: scale(1.02); }}
        .btn-green {{ background: #00cc66; }}
        .btn-green:hover {{ background: #00ff80; }}
        
        .result-box {{
            background: rgba(0, 0, 0, 0.7);
            border: 1px solid rgba(102, 0, 204, 0.2);
            border-radius: 12px; padding: 20px; margin-top: 20px;
            display: none; position: relative;
        }}
        
        .result-box .label {{
            color: #6600cc; font-size: 0.8em; text-transform: uppercase;
            letter-spacing: 2px; margin-bottom: 10px;
        }}
        
        .result-box .value {{
            color: #00ff41; font-size: 0.8em; word-break: break-all; line-height: 1.8;
        }}
        
        .copy-btn {{
            position: absolute; top: 10px; right: 10px;
            background: #6600cc; color: white; border: none;
            padding: 8px 18px; border-radius: 20px; cursor: pointer;
            font-family: 'Courier New', monospace; font-size: 0.75em;
            transition: all 0.3s;
        }}
        
        .copy-btn:hover {{ background: #9900ff; box-shadow: 0 0 20px rgba(102, 0, 204, 0.5); }}
        .copy-btn.copied {{ background: #00ff41; color: #000; }}
        
        .footer {{
            text-align: center; margin-top: 40px; color: #333;
            font-size: 0.7em; letter-spacing: 3px;
        }}
        
        @media (max-width: 768px) {{
            .title {{ font-size: 1.8em; }}
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
            <p class="subtitle">⚡ VLESS + TLS + WS + Clean IP ⚡</p>
            
            <div class="form-group">
                <label>Address (Clean IP / Domain)</label>
                <input type="text" id="address" value="{info.get('default_clean_ips', ['104.26.0.1'])[0]}" placeholder="104.26.0.1">
            </div>
            
            <div class="form-group">
                <label>SNI</label>
                <input type="text" id="sni" value="{info.get('default_sni', 'www.speedtest.net')}" placeholder="www.speedtest.net">
            </div>
            
            <div class="form-group">
                <label>Host</label>
                <input type="text" id="host" value="{info.get('domain', '')}" placeholder="your-domain.com">
            </div>
            
            <div class="form-group">
                <label>WebSocket Path</label>
                <input type="text" id="ws_path" value="{info.get('ws_path', '/ws')}" placeholder="/ws">
            </div>
            
            <button class="btn" onclick="generateConfig()">🚀 Generate VLESS Config</button>
            
            <div class="result-box" id="result-box">
                <div class="label">🔗 VLESS Link</div>
                <button class="copy-btn" onclick="copyLink()">COPY</button>
                <div class="value" id="vless-link"></div>
            </div>
            
            <div class="result-box" id="json-box">
                <div class="label">📱 JSON Config (v2rayNG)</div>
                <button class="copy-btn" onclick="copyJSON()">COPY</button>
                <div class="value" id="json-config" style="max-height: 300px; overflow-y: auto;"></div>
            </div>
        </div>
        
        <p class="footer">⬡ QUANTUM VLESS ⬡ TLS + WS + CLEAN IP ⬡</p>
    </div>
    
    <script>
        // Matrix Canvas
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
        
        // Config Generator
        let currentLink = '', currentJSON = '';
        
        async function generateConfig() {{
            const address = document.getElementById('address').value || '104.26.0.1';
            const sni = document.getElementById('sni').value || 'www.speedtest.net';
            const host = document.getElementById('host').value || '{info["domain"]}';
            const ws_path = document.getElementById('ws_path').value || '/ws';
            
            const params = new URLSearchParams({{address, sni, host, ws_path}});
            const res = await fetch('/api/config?' + params);
            const data = await res.json();
            
            currentLink = data.vless_link;
            currentJSON = JSON.stringify(data.json_config, null, 2);
            
            document.getElementById('vless-link').textContent = currentLink;
            document.getElementById('json-config').textContent = currentJSON;
            
            document.getElementById('result-box').style.display = 'block';
            document.getElementById('json-box').style.display = 'block';
        }}
        
        function copyLink() {{
            if(currentLink) {{
                navigator.clipboard.writeText(currentLink);
                const btn = event.target;
                btn.textContent = '✓ COPIED'; btn.classList.add('copied');
                setTimeout(() => {{ btn.textContent = 'COPY'; btn.classList.remove('copied'); }}, 2000);
            }}
        }}
        
        function copyJSON() {{
            if(currentJSON) {{
                navigator.clipboard.writeText(currentJSON);
                const btn = event.target;
                btn.textContent = '✓ COPIED'; btn.classList.add('copied');
                setTimeout(() => {{ btn.textContent = 'COPY'; btn.classList.remove('copied'); }}, 2000);
            }}
        }}
        
        // Generate on load
        setTimeout(generateConfig, 500);
    </script>
</body>
</html>"""
    return HTMLResponse(html)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
