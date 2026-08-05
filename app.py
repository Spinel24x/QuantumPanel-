from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import os
import json
from pathlib import Path

app = FastAPI(title="Quantum Panel")

# ============================================
# اطلاعات پایه
# ============================================
DOMAIN = os.getenv("RAILWAY_PUBLIC_DOMAIN", "localhost")
TCP_PORT = os.getenv("RAILWAY_TCP_PORT", "2222")
PASSWORD = "Quantum2024!@#"
UUID = ""

try:
    UUID = Path("/app/data/uuid.txt").read_text().strip()
except:
    UUID = "00000000-0000-0000-0000-000000000000"

# ============================================
# API: دریافت کانفیگ‌ها
# ============================================
@app.get("/api/configs")
async def get_configs():
    configs = {
        "domain": DOMAIN,
        "tcp_port": TCP_PORT,
        "password": PASSWORD,
        "uuid": UUID,
        "protocols": {
            "ssh_direct": {
                "name": "SSH-Direct",
                "host": DOMAIN,
                "port": int(TCP_PORT) if TCP_PORT else 2222,
                "username": "root",
                "password": PASSWORD,
                "udpgw_port": 7300,
                "command": f"ssh -D 1080 -p {TCP_PORT} root@{DOMAIN}",
                "link": f"ssh://root:{PASSWORD}@{DOMAIN}:{TCP_PORT}#Quantum-Direct"
            },
            "ssh_proxy": {
                "name": "SSH-Proxy",
                "host": DOMAIN,
                "port": int(TCP_PORT) if TCP_PORT else 2222,
                "username": "root",
                "password": PASSWORD,
                "socks5_port": 1080,
                "udpgw_port": 7300,
                "command": f"ssh -D 1080 -p {TCP_PORT} root@{DOMAIN}"
            },
            "ssh_payload": {
                "name": "SSH-Payload",
                "host": DOMAIN,
                "port": int(TCP_PORT) if TCP_PORT else 2222,
                "username": "root",
                "password": PASSWORD,
                "payload": f"GET / HTTP/1.1[crlf]Host: {DOMAIN}[crlf][crlf]",
                "sni": "cloudflare.com",
                "udpgw_port": 7300
            },
            "ssh_proxy_payload": {
                "name": "SSH-Proxy-Payload",
                "host": DOMAIN,
                "port": int(TCP_PORT) if TCP_PORT else 2222,
                "username": "root",
                "password": PASSWORD,
                "payload": f"CONNECT [host] HTTP/1.1[crlf]Host: {DOMAIN}[crlf][crlf]",
                "sni": "cloudflare.com",
                "socks5_port": 1080,
                "udpgw_port": 7300
            },
            "ssh_ws": {
                "name": "SSH-WebSocket",
                "host": "speed.cloudflare.com",
                "port": 443,
                "username": "root",
                "password": PASSWORD,
                "sni": "cloudflare.com",
                "ws_path": "/ws",
                "ws_host": DOMAIN,
                "udpgw_port": 7300
            },
            "npv": {
                "name": "NapsternetV",
                "host": DOMAIN,
                "port": int(TCP_PORT) if TCP_PORT else 2222,
                "username": "root",
                "password": PASSWORD,
                "udpgw_port": 7300,
                "sni": "cloudflare.com"
            },
            "http_injector": {
                "name": "HTTP Injector",
                "host": DOMAIN,
                "port": int(TCP_PORT) if TCP_PORT else 2222,
                "username": "root",
                "password": PASSWORD,
                "payload": f"GET / HTTP/1.1[crlf]Host: {DOMAIN}[crlf][crlf]",
                "sni": "cloudflare.com",
                "udpgw_port": 7300
            },
            "http_custom": {
                "name": "HTTP Custom",
                "host": DOMAIN,
                "port": int(TCP_PORT) if TCP_PORT else 2222,
                "username": "root",
                "password": PASSWORD,
                "payload": f"GET / HTTP/1.1[crlf]Host: {DOMAIN}[crlf][crlf]",
                "sni": "cloudflare.com",
                "udpgw_port": 7300
            },
            "ssh_tls": {
                "name": "SSH-TLS",
                "host": DOMAIN,
                "port": 443,
                "username": "root",
                "password": PASSWORD,
                "sni": DOMAIN,
                "udpgw_port": 7300
            }
        }
    }
    return JSONResponse(configs)

# ============================================
# صفحه اصلی - Quantum Theme
# ============================================
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quantum SSH Panel</title>
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
        
        .container > * {{
            pointer-events: auto;
        }}
        
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
        
        .tab-buttons {{
            display: flex;
            gap: 8px;
            margin-bottom: 20px;
            flex-wrap: wrap;
            justify-content: center;
        }}
        
        .tab-btn {{
            background: rgba(102, 0, 204, 0.1);
            color: #999;
            border: 1px solid rgba(102, 0, 204, 0.2);
            padding: 10px 18px;
            border-radius: 20px;
            cursor: pointer;
            font-family: 'Courier New', monospace;
            font-size: 0.75em;
            transition: all 0.3s;
            letter-spacing: 1px;
        }}
        
        .tab-btn:hover {{
            background: rgba(102, 0, 204, 0.2);
            color: #ccc;
        }}
        
        .tab-btn.active {{
            background: #6600cc;
            color: white;
            border-color: #6600cc;
            box-shadow: 0 0 20px rgba(102, 0, 204, 0.4);
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
            animation: fadeIn 0.3s ease;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
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
            background: rgba(0, 0, 0, 0.7);
            border: 1px solid rgba(102, 0, 204, 0.2);
            border-radius: 12px;
            padding: 20px;
            position: relative;
            word-break: break-all;
            font-size: 0.8em;
            color: #00ff41;
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
            <p class="subtitle"><span class="pulse-dot"></span> SSH TUNNEL PANEL v2.0</p>
            
            <div class="info-grid" id="info-grid">
                <div class="info-card">
                    <div class="label">Host</div>
                    <div class="value">{DOMAIN}</div>
                </div>
                <div class="info-card">
                    <div class="label">SSH Port</div>
                    <div class="value">{TCP_PORT}</div>
                </div>
                <div class="info-card">
                    <div class="label">Username</div>
                    <div class="value">root</div>
                </div>
                <div class="info-card">
                    <div class="label">Password</div>
                    <div class="value">{PASSWORD}</div>
                </div>
            </div>
            
            <div class="tab-buttons" id="tab-buttons"></div>
            <div id="tab-contents"></div>
        </div>
        
        <p class="footer">⬡ QUANTUM CORE ⬡ SSH INTELLIGENT ENGINE ⬡</p>
    </div>
    
    <script>
        // ============================================
        // Matrix Canvas - خطوط رندوم متحرک
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
                    [255, 0, 204], [0, 255, 204], [255, 102, 0],
                    [204, 0, 153], [51, 204, 255], [153, 51, 255]
                ];
                return colors[Math.floor(Math.random() * colors.length)];
            }}
            
            update() {{
                this.progress += this.speed;
                if (this.progress > 1 + this.maxLength) {{
                    this.reset();
                }}
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
        
        for (let i = 0; i < maxLines; i++) {{
            lines.push(new Line());
        }}
        
        function animateMatrix() {{
            matrixCtx.fillStyle = 'rgba(0, 0, 0, 0.05)';
            matrixCtx.fillRect(0, 0, matrixCanvas.width, matrixCanvas.height);
            
            lines.forEach(line => {{
                line.update();
                line.draw(matrixCtx);
            }});
            
            requestAnimationFrame(animateMatrix);
        }}
        
        animateMatrix();
        
        window.addEventListener('resize', () => {{
            matrixCanvas.width = window.innerWidth;
            matrixCanvas.height = window.innerHeight;
        }});
        
        // ============================================
        // Blackhole Canvas - سیاه‌چاله زنده
        // ============================================
        const bhCanvas = document.getElementById('blackholeCanvas');
        const bhCtx = bhCanvas.getContext('2d');
        
        const cx = 250;
        const cy = 175;
        let bhTime = 0;
        
        function drawBlackhole(time) {{
            bhCtx.clearRect(0, 0, bhCanvas.width, bhCanvas.height);
            
            // Outer glow layers
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
            
            // Accretion disk
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
            
            // Event horizon
            const horizonGradient = bhCtx.createRadialGradient(cx, cy, 0, cx, cy, 45);
            horizonGradient.addColorStop(0, '#000000');
            horizonGradient.addColorStop(0.7, '#0a0015');
            horizonGradient.addColorStop(1, 'rgba(102, 0, 204, 0.3)');
            
            bhCtx.beginPath();
            bhCtx.arc(cx, cy, 45, 0, Math.PI * 2);
            bhCtx.fillStyle = horizonGradient;
            bhCtx.fill();
            
            // Photon ring
            bhCtx.beginPath();
            bhCtx.arc(cx, cy, 48, 0, Math.PI * 2);
            bhCtx.strokeStyle = `rgba(153, 0, 255, ${{0.4 + Math.sin(time * 0.03) * 0.2}})`;
            bhCtx.lineWidth = 3;
            bhCtx.shadowBlur = 20;
            bhCtx.shadowColor = '#6600cc';
            bhCtx.stroke();
            bhCtx.shadowBlur = 0;
            
            // Corona particles
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
        // Load Configs and Build Tabs
        // ============================================
        let allConfigs = {{}};
        
        async function loadConfigs() {{
            try {{
                const response = await fetch('/api/configs');
                allConfigs = await response.json();
                buildTabs();
            }} catch (e) {{
                console.error('Error loading configs:', e);
            }}
        }}
        
        function buildTabs() {{
            const tabButtons = document.getElementById('tab-buttons');
            const tabContents = document.getElementById('tab-contents');
            
            const protocols = allConfigs.protocols;
            let first = true;
            
            for (const [key, cfg] of Object.entries(protocols)) {{
                // Tab button
                const btn = document.createElement('button');
                btn.className = 'tab-btn' + (first ? ' active' : '');
                btn.textContent = cfg.name;
                btn.onclick = () => showTab(key);
                tabButtons.appendChild(btn);
                
                // Tab content
                const content = document.createElement('div');
                content.className = 'tab-content' + (first ? ' active' : '');
                content.id = 'tab-' + key;
                
                let displayText = '';
                if (cfg.link) {{
                    displayText = cfg.link;
                }} else if (cfg.command) {{
                    displayText = cfg.command;
                }} else {{
                    displayText = JSON.stringify(cfg, null, 2);
                }}
                
                content.innerHTML = `
                    <div class="config-label">${{cfg.name}} Configuration</div>
                    <div class="config-value">
                        <button class="copy-btn" onclick="copyConfig('${{key}}', this)">COPY</button>
                        <pre style="white-space: pre-wrap; font-family: 'Courier New', monospace;">${{displayText}}</pre>
                    </div>
                `;
                
                tabContents.appendChild(content);
                first = false;
            }}
        }}
        
        function showTab(key) {{
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            
            document.getElementById('tab-' + key).classList.add('active');
            event.target.classList.add('active');
        }}
        
        function copyConfig(key, btn) {{
            const cfg = allConfigs.protocols[key];
            let text = '';
            
            if (cfg.link) text = cfg.link;
            else if (cfg.command) text = cfg.command;
            else text = JSON.stringify(cfg, null, 2);
            
            navigator.clipboard.writeText(text).then(() => {{
                btn.textContent = '✓ COPIED';
                btn.classList.add('copied');
                setTimeout(() => {{
                    btn.textContent = 'COPY';
                    btn.classList.remove('copied');
                }}, 2000);
            }});
        }}
        
        // Load on page ready
        loadConfigs();
    </script>
</body>
</html>"""
    return HTMLResponse(html)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
