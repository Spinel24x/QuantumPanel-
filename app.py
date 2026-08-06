from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import os
import json
from pathlib import Path

app = FastAPI(title="Quantum VLESS Panel")

# ============================================
# اطلاعات
# ============================================
def load_info():
    try:
        return json.loads(Path("/app/data/info.json").read_text())
    except:
        return {
            "uuid": "00000000-0000-0000-0000-000000000000",
            "domain": os.getenv("RAILWAY_PUBLIC_DOMAIN", "localhost"),
            "tcp_proxy_port": os.getenv("RAILWAY_TCP_PROXY_PORT", "8443"),
            "ws_path": "/ws",
            "security": "none"
        }

# ============================================
# API
# ============================================
@app.get("/api/config")
async def get_config():
    info = load_info()
    
    uuid = info["uuid"]
    domain = info["domain"]
    port = info["tcp_proxy_port"]
    ws_path = info["ws_path"]
    
    # VLESS بدون TLS
    vless_link = f"vless://{uuid}@{domain}:{port}?encryption=none&security=none&type=ws&path={ws_path}&host={domain}#Quantum-VLESS"
    
    # کانفیگ JSON
    json_config = {
        "outbounds": [{
            "protocol": "vless",
            "settings": {
                "vnext": [{
                    "address": domain,
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
                    "headers": {
                        "Host": domain
                    }
                }
            },
            "tag": "proxy"
        }]
    }
    
    configs = {
        "vless_link": vless_link,
        "json_config": json.dumps(json_config, indent=2),
        "npv_config": {
            "protocol": "vless",
            "address": domain,
            "port": int(port),
            "id": uuid,
            "encryption": "none",
            "network": "ws",
            "security": "none",
            "path": ws_path,
            "host": domain,
            "type": "ws",
            "remark": "Quantum-VLESS"
        },
        "info": info
    }
    
    return JSONResponse(configs)

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
        
        canvas {{
            position: fixed;
            top: 0;
            left: 0;
            z-index: 0;
        }}
        
        .container {{
            position: relative;
            z-index: 2;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
            pointer-events: none;
        }}
        
        .container > * {{ pointer-events: auto; }}
        
        .blackhole-wrapper {{
            width: 100%;
            max-width: 500px;
            height: 350px;
            position: relative;
            margin-top: 20px;
        }}
        
        .config-section {{
            width: 100%;
            max-width: 750px;
            background: rgba(5, 5, 20, 0.85);
            border: 1px solid rgba(102, 0, 204, 0.3);
            border-radius: 20px;
            padding: 30px;
            backdrop-filter: blur(20px);
            box-shadow: 0 0 60px rgba(102, 0, 204, 0.15), inset 0 0 30px rgba(0, 0, 0, 0.5);
            margin-top: -30px;
            z-index: 3;
        }}
        
        .title {{
            font-size: 3.5em;
            font-weight: bold;
            text-align: center;
            background: linear-gradient(135deg, #6600cc, #00ccff, #ff00cc, #6600cc);
            background-size: 300% 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradientShift 4s ease infinite;
            margin-bottom: 5px;
            letter-spacing: 8px;
        }}
        
        @keyframes gradientShift {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        
        .subtitle {{
            text-align: center;
            color: rgba(102, 0, 204, 0.7);
            margin-bottom: 30px;
            font-size: 0.85em;
            letter-spacing: 4px;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
            gap: 12px;
            margin-bottom: 25px;
        }}
        
        .info-card {{
            background: rgba(0, 0, 0, 0.6);
            border: 1px solid rgba(102, 0, 204, 0.2);
            border-radius: 12px;
            padding: 15px;
            text-align: center;
            transition: all 0.3s;
        }}
        
        .info-card:hover {{
            border-color: rgba(102, 0, 204, 0.6);
            box-shadow: 0 0 20px rgba(102, 0, 204, 0.2);
        }}
        
        .info-card .label {{
            color: #666;
            font-size: 0.7em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }}
        
        .info-card .value {{
            color: #00ccff;
            font-weight: bold;
            font-size: 0.9em;
            word-break: break-all;
        }}
        
        .config-box {{
            background: rgba(0, 0, 0, 0.7);
            border: 1px solid rgba(102, 0, 204, 0.2);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            position: relative;
        }}
        
        .config-label {{
            color: #6600cc;
            font-weight: bold;
            font-size: 0.8em;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}
        
        .config-value {{
            color: #00ff41;
            font-size: 0.8em;
            word-break: break-all;
            line-height: 1.8;
        }}
        
        .copy-btn {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: #6600cc;
            color: white;
            border: none;
            padding: 8px 18px;
            border-radius: 20px;
            cursor: pointer;
            font-family: 'Courier New', monospace;
            font-size: 0.75em;
            transition: all 0.3s;
            letter-spacing: 1px;
        }}
        
        .copy-btn:hover {{
            background: #9900ff;
            box-shadow: 0 0 25px rgba(102, 0, 204, 0.6);
            transform: scale(1.05);
        }}
        
        .copy-btn.copied {{
            background: #00ff41;
            color: #000;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: #333;
            font-size: 0.7em;
            letter-spacing: 3px;
        }}
        
        .pulse-dot {{
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #00ff41;
            border-radius: 50%;
            animation: pulse 1.5s ease-in-out infinite;
            margin-right: 5px;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; box-shadow: 0 0 10px #00ff41; }}
            50% {{ opacity: 0.3; box-shadow: 0 0 30px #00ff41; }}
        }}
        
        @media (max-width: 768px) {{
            .title {{ font-size: 2em; }}
            .config-section {{ padding: 20px; }}
        }}
    </style>
</head>
<body>
    <canvas id="matrixCanvas"></canvas>
    
    <div class="container">
        <div class="blackhole-wrapper">
            <canvas id="blackholeCanvas" width="500" height="350"></canvas>
        </div>
        
        <div class="config-section">
            <h1 class="title">QUANTUM</h1>
            <p class="subtitle"><span class="pulse-dot"></span> VLESS + WS + TCP PROXY <span class="pulse-dot"></span></p>
            
            <div class="info-grid">
                <div class="info-card">
                    <div class="label">Domain</div>
                    <div class="value">{info['domain']}</div>
                </div>
                <div class="info-card">
                    <div class="label">Port</div>
                    <div class="value">{info['tcp_proxy_port']}</div>
                </div>
                <div class="info-card">
                    <div class="label">Protocol</div>
                    <div class="value">VLESS</div>
                </div>
                <div class="info-card">
                    <div class="label">Network</div>
                    <div class="value">WS</div>
                </div>
            </div>
            
            <div class="config-box">
                <div class="config-label">🔗 VLESS Link (v2rayNG / Nekobox / Streisand)</div>
                <button class="copy-btn" onclick="copyVLESS(this)">COPY</button>
                <div class="config-value" id="vless-link">Loading...</div>
            </div>
            
            <div class="config-box">
                <div class="config-label">📱 NapsternetV / JSON Config</div>
                <button class="copy-btn" onclick="copyJSON(this)">COPY JSON</button>
                <div class="config-value" id="json-config" style="max-height: 300px; overflow-y: auto;">Loading...</div>
            </div>
        </div>
        
        <p class="footer">⬡ QUANTUM VLESS ⬡ NO CLOUDFLARE ⬡ TCP PROXY ⬡</p>
    </div>
    
    <script>
        // ============================================
        // Matrix Lines Canvas
        // ============================================
        const matrixCanvas = document.getElementById('matrixCanvas');
        const matrixCtx = matrixCanvas.getContext('2d');
        
        matrixCanvas.width = window.innerWidth;
        matrixCanvas.height = window.innerHeight;
        
        const lines = [];
        const maxLines = 50;
        
        class Line {{
            constructor() {{
                this.reset();
            }}
            
            reset() {{
                this.x1 = Math.random() * matrixCanvas.width;
                this.y1 = Math.random() * matrixCanvas.height;
                this.x2 = Math.random() * matrixCanvas.width;
                this.y2 = Math.random() * matrixCanvas.height;
                this.progress = 0;
                this.speed = Math.random() * 0.003 + 0.002;
                this.color = this.randomColor();
                this.maxLength = Math.random() * 0.5 + 0.1;
            }}
            
            randomColor() {{
                const colors = [
                    [102, 0, 204], [153, 0, 255], [0, 204, 255],
                    [255, 0, 204], [0, 255, 204], [255, 102, 0]
                ];
                return colors[Math.floor(Math.random() * colors.length)];
            }}
            
            update() {{
                this.progress += this.speed;
                if (this.progress > 1 + this.maxLength) this.reset();
            }}
            
            draw(ctx) {{
                const start = Math.max(0, this.progress - this.maxLength);
                const end = Math.min(1, this.progress);
                if (start >= end) return;
                
                const sx = this.x1 + (this.x2 - this.x1) * start;
                const sy = this.y1 + (this.y2 - this.y1) * start;
                const ex = this.x1 + (this.x2 - this.x1) * end;
                const ey = this.y1 + (this.y2 - this.y1) * end;
                
                const alpha = (1 - Math.abs(this.progress - 0.5) * 2) * 0.4;
                
                ctx.beginPath();
                ctx.moveTo(sx, sy);
                ctx.lineTo(ex, ey);
                ctx.strokeStyle = `rgba(${{this.color[0]}},${{this.color[1]}},${{this.color[2]}},${{alpha}})`;
                ctx.lineWidth = 1.5;
                ctx.shadowBlur = 8;
                ctx.shadowColor = `rgba(${{this.color[0]}},${{this.color[1]}},${{this.color[2]}},0.5)`;
                ctx.stroke();
                ctx.shadowBlur = 0;
            }}
        }}
        
        for (let i = 0; i < maxLines; i++) lines.push(new Line());
        
        function animateMatrix() {{
            matrixCtx.fillStyle = 'rgba(0, 0, 0, 0.05)';
            matrixCtx.fillRect(0, 0, matrixCanvas.width, matrixCanvas.height);
            lines.forEach(line => {{ line.update(); line.draw(matrixCtx); }});
            requestAnimationFrame(animateMatrix);
        }}
        
        animateMatrix();
        
        window.addEventListener('resize', () => {{
            matrixCanvas.width = window.innerWidth;
            matrixCanvas.height = window.innerHeight;
        }});
        
        // ============================================
        // Blackhole Canvas
        // ============================================
        const bhCanvas = document.getElementById('blackholeCanvas');
        const bhCtx = bhCanvas.getContext('2d');
        const cx = 250, cy = 175;
        
        function drawBlackhole(time) {{
            bhCtx.clearRect(0, 0, bhCanvas.width, bhCanvas.height);
            
            for (let i = 5; i >= 0; i--) {{
                const radius = 90 + i * 25 + Math.sin(time * 0.02 + i) * 8;
                const gradient = bhCtx.createRadialGradient(cx, cy, radius * 0.3, cx, cy, radius);
                gradient.addColorStop(0, 'rgba(102, 0, 204, 0)');
                gradient.addColorStop(0.5, `rgba(102, 0, 204, ${{0.08 - i * 0.01}})`);
                gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
                bhCtx.beginPath();
                bhCtx.arc(cx, cy, radius, 0, Math.PI * 2);
                bhCtx.fillStyle = gradient;
                bhCtx.fill();
            }}
            
            const diskGradient = bhCtx.createLinearGradient(cx - 120, cy, cx + 120, cy);
            diskGradient.addColorStop(0, 'rgba(0, 204, 255, 0)');
            diskGradient.addColorStop(0.3, 'rgba(102, 0, 204, 0.6)');
            diskGradient.addColorStop(0.5, 'rgba(255, 255, 255, 0.4)');
            diskGradient.addColorStop(0.7, 'rgba(255, 0, 204, 0.6)');
            diskGradient.addColorStop(1, 'rgba(0, 204, 255, 0)');
            
            bhCtx.save();
            bhCtx.translate(cx, cy);
            bhCtx.rotate(time * 0.01);
            bhCtx.beginPath();
            bhCtx.ellipse(0, 0, 100, 20, 0, 0, Math.PI * 2);
            bhCtx.fillStyle = diskGradient;
            bhCtx.fill();
            bhCtx.restore();
            
            const horizonGradient = bhCtx.createRadialGradient(cx, cy, 0, cx, cy, 45);
            horizonGradient.addColorStop(0, '#000000');
            horizonGradient.addColorStop(0.7, '#0a0015');
            horizonGradient.addColorStop(1, 'rgba(102, 0, 204, 0.3)');
            bhCtx.beginPath();
            bhCtx.arc(cx, cy, 45, 0, Math.PI * 2);
            bhCtx.fillStyle = horizonGradient;
            bhCtx.fill();
            
            bhCtx.beginPath();
            bhCtx.arc(cx, cy, 48, 0, Math.PI * 2);
            bhCtx.strokeStyle = `rgba(153, 0, 255, ${{0.4 + Math.sin(time * 0.03) * 0.2}})`;
            bhCtx.lineWidth = 3;
            bhCtx.shadowBlur = 20;
            bhCtx.shadowColor = '#6600cc';
            bhCtx.stroke();
            bhCtx.shadowBlur = 0;
            
            for (let i = 0; i < 12; i++) {{
                const angle = (i / 12) * Math.PI * 2 + time * 0.005;
                const particleRadius = 55 + Math.sin(time * 0.04 + i) * 15;
                const px = cx + Math.cos(angle) * particleRadius;
                const py = cy + Math.sin(angle) * particleRadius * 0.3;
                bhCtx.beginPath();
                bhCtx.arc(px, py, 2, 0, Math.PI * 2);
                bhCtx.fillStyle = `rgba(0, 204, 255, ${{0.6 + Math.sin(time * 0.05 + i) * 0.4}})`;
                bhCtx.fill();
            }}
        }}
        
        function animateBlackhole(time) {{
            drawBlackhole(time);
            requestAnimationFrame(animateBlackhole);
        }}
        
        requestAnimationFrame(animateBlackhole);
        
        // ============================================
        // Load Configs
        // ============================================
        async function loadConfigs() {{
            try {{
                const res = await fetch('/api/config');
                const data = await res.json();
                
                document.getElementById('vless-link').textContent = data.vless_link;
                document.getElementById('json-config').textContent = data.json_config;
                
                window.vlessLink = data.vless_link;
                window.jsonConfig = data.json_config;
            }} catch(e) {{
                document.getElementById('vless-link').textContent = 'Error loading...';
            }}
        }}
        
        function copyVLESS(btn) {{
            if (window.vlessLink) {{
                navigator.clipboard.writeText(window.vlessLink).then(() => {{
                    btn.textContent = '✓ COPIED';
                    btn.classList.add('copied');
                    setTimeout(() => {{ btn.textContent = 'COPY'; btn.classList.remove('copied'); }}, 2000);
                }});
            }}
        }}
        
        function copyJSON(btn) {{
            if (window.jsonConfig) {{
                navigator.clipboard.writeText(window.jsonConfig).then(() => {{
                    btn.textContent = '✓ COPIED';
                    btn.classList.add('copied');
                    setTimeout(() => {{ btn.textContent = 'COPY'; btn.classList.remove('copied'); }}, 2000);
                }});
            }}
        }}
        
        loadConfigs();
    </script>
</body>
</html>"""
    return HTMLResponse(html)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
