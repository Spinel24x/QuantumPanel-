from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import os
import json
import uuid as uuid_lib
from pathlib import Path

app = FastAPI(title="Quantum Panel")

# ============================================
# ذخیره و خواندن UUID
# ============================================
def get_uuid():
    try:
        return Path("/app/data/uuid.txt").read_text().strip()
    except:
        new_uuid = str(uuid_lib.uuid4())
        Path("/app/data").mkdir(exist_ok=True)
        Path("/app/data/uuid.txt").write_text(new_uuid)
        return new_uuid

def get_ssh_password():
    return "Quantum2024!@#"

def get_domain():
    return os.getenv("RAILWAY_PUBLIC_DOMAIN", "localhost")

# ============================================
# API Routes
# ============================================
@app.get("/api/config")
async def get_config():
    domain = get_domain()
    password = get_ssh_password()
    uuid = get_uuid()
    
    configs = {
        "ssh_link": f"ssh://root:{password}@{domain}:2222#Quantum",
        "ssh_ws_link": f"ssh://root:{password}@speed.cloudflare.com:443?sni=cloudflare.com&type=ws&host={domain}&path=/ws#Quantum-WS",
        "http_injector": {
            "host": "speed.cloudflare.com",
            "port": 443,
            "username": "root",
            "password": password,
            "sni": "cloudflare.com",
            "ws_path": "/ws",
            "ws_host": domain
        },
        "napsternetv": {
            "protocol": "ssh",
            "host": "speed.cloudflare.com",
            "port": 443,
            "username": "root",
            "password": password,
            "sni": "cloudflare.com",
            "ws_path": "/ws",
            "ws_host": domain
        },
        "uuid": uuid,
        "domain": domain
    }
    
    return JSONResponse(configs)

# ============================================
# Main Page - Quantum Theme
# ============================================
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    domain = get_domain()
    password = get_ssh_password()
    uuid = get_uuid()
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quantum Panel</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            background: #000;
            color: #fff;
            font-family: 'Courier New', monospace;
            min-height: 100vh;
            overflow-x: hidden;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        
        canvas {{
            position: fixed;
            top: 0;
            left: 0;
            z-index: 0;
        }}
        
        .container {{
            position: relative;
            z-index: 1;
            width: 100%;
            max-width: 700px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        
        .blackhole {{
            width: 200px;
            height: 200px;
            margin: 0 auto 30px;
            position: relative;
            z-index: 2;
        }}
        
        .blackhole::before {{
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 80px;
            height: 80px;
            background: radial-gradient(circle, #000 0%, #1a0033 30%, #6600cc 50%, transparent 70%);
            border-radius: 50%;
            box-shadow: 0 0 60px #6600cc, 0 0 120px #330066, 0 0 180px #1a0033;
            animation: pulse 2s ease-in-out infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ box-shadow: 0 0 60px #6600cc, 0 0 120px #330066, 0 0 180px #1a0033; }}
            50% {{ box-shadow: 0 0 80px #9900ff, 0 0 160px #6600cc, 0 0 240px #330066; }}
        }}
        
        .title {{
            font-size: 3em;
            font-weight: bold;
            text-align: center;
            background: linear-gradient(135deg, #6600cc, #00ccff, #6600cc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: colorShift 5s linear infinite;
            margin-bottom: 10px;
            z-index: 2;
        }}
        
        @keyframes colorShift {{
            0% {{ filter: hue-rotate(0deg); }}
            100% {{ filter: hue-rotate(360deg); }}
        }}
        
        .subtitle {{
            text-align: center;
            color: #888;
            margin-bottom: 40px;
            font-size: 0.9em;
            z-index: 2;
        }}
        
        .config-box {{
            background: rgba(10, 10, 30, 0.85);
            border: 1px solid #333;
            border-radius: 15px;
            padding: 30px;
            width: 100%;
            backdrop-filter: blur(10px);
            box-shadow: 0 0 30px rgba(102, 0, 204, 0.2);
            z-index: 2;
        }}
        
        .config-section {{
            margin-bottom: 25px;
        }}
        
        .config-label {{
            color: #6600cc;
            font-weight: bold;
            font-size: 0.9em;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}
        
        .config-value {{
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid #333;
            border-radius: 8px;
            padding: 15px;
            word-break: break-all;
            font-size: 0.85em;
            position: relative;
            color: #00ff41;
        }}
        
        .copy-btn {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: #6600cc;
            color: white;
            border: none;
            padding: 5px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-family: 'Courier New', monospace;
            font-size: 0.8em;
            transition: all 0.3s;
        }}
        
        .copy-btn:hover {{
            background: #9900ff;
            box-shadow: 0 0 15px rgba(102, 0, 204, 0.5);
        }}
        
        .tab-buttons {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        
        .tab-btn {{
            background: rgba(102, 0, 204, 0.2);
            color: #aaa;
            border: 1px solid #333;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-family: 'Courier New', monospace;
            transition: all 0.3s;
        }}
        
        .tab-btn.active {{
            background: #6600cc;
            color: white;
            border-color: #6600cc;
            box-shadow: 0 0 15px rgba(102, 0, 204, 0.3);
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .info-card {{
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid #333;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
        }}
        
        .info-card .label {{
            color: #666;
            font-size: 0.8em;
            margin-bottom: 5px;
        }}
        
        .info-card .value {{
            color: #00ccff;
            font-weight: bold;
        }}
        
        .quantum-text {{
            color: #6600cc;
            animation: glow 2s ease-in-out infinite;
        }}
        
        @keyframes glow {{
            0%, 100% {{ text-shadow: 0 0 10px #6600cc; }}
            50% {{ text-shadow: 0 0 30px #9900ff, 0 0 60px #6600cc; }}
        }}
    </style>
</head>
<body>
    <canvas id="hexCanvas"></canvas>
    
    <div class="container">
        <div class="blackhole"></div>
        <h1 class="title">QUANTUM</h1>
        <p class="subtitle">⚡ SSH Tunnel Configuration Panel ⚡</p>
        
        <div class="config-box">
            <div class="info-grid">
                <div class="info-card">
                    <div class="label">Host</div>
                    <div class="value">{domain}</div>
                </div>
                <div class="info-card">
                    <div class="label">SSH Port</div>
                    <div class="value">2222</div>
                </div>
                <div class="info-card">
                    <div class="label">Username</div>
                    <div class="value">root</div>
                </div>
                <div class="info-card">
                    <div class="label">UUID</div>
                    <div class="value" style="font-size:0.7em;">{uuid[:12]}...</div>
                </div>
            </div>
            
            <div class="tab-buttons">
                <button class="tab-btn active" onclick="showTab('ssh')">SSH Link</button>
                <button class="tab-btn" onclick="showTab('ws')">SSH + WS</button>
                <button class="tab-btn" onclick="showTab('injector')">HTTP Injector</button>
                <button class="tab-btn" onclick="showTab('napster')">NapsternetV</button>
            </div>
            
            <div id="tab-ssh" class="tab-content active">
                <div class="config-label">🔗 SSH Direct Link</div>
                <div class="config-value">
                    <button class="copy-btn" onclick="copyText('ssh://root:{password}@{domain}:2222#Quantum')">Copy</button>
                    <span>ssh://root:{password}@{domain}:2222#Quantum</span>
                </div>
            </div>
            
            <div id="tab-ws" class="tab-content">
                <div class="config-label">🌐 SSH + WebSocket Link</div>
                <div class="config-value">
                    <button class="copy-btn" onclick="copyText('ssh://root:{password}@speed.cloudflare.com:443?sni=cloudflare.com&type=ws&host={domain}&path=/ws#Quantum-WS')">Copy</button>
                    <span>ssh://root:{password}@speed.cloudflare.com:443?sni=cloudflare.com&type=ws&host={domain}&path=/ws#Quantum-WS</span>
                </div>
            </div>
            
            <div id="tab-injector" class="tab-content">
                <div class="config-label">📱 HTTP Injector Config</div>
                <div class="config-value">
                    <button class="copy-btn" onclick="copyText(JSON.stringify({{host:'speed.cloudflare.com',port:443,username:'root',password:'{password}',sni:'cloudflare.com',ws_path:'/ws',ws_host:'{domain}'}}))">Copy JSON</button>
                    <span style="font-size:0.75em;">{{
    "host": "speed.cloudflare.com",
    "port": 443,
    "username": "root",
    "password": "{password}",
    "sni": "cloudflare.com",
    "ws_path": "/ws",
    "ws_host": "{domain}"
}}</span>
                </div>
            </div>
            
            <div id="tab-napster" class="tab-content">
                <div class="config-label">📱 NapsternetV Config</div>
                <div class="config-value">
                    <button class="copy-btn" onclick="copyText(JSON.stringify({{protocol:'ssh',host:'speed.cloudflare.com',port:443,username:'root',password:'{password}',sni:'cloudflare.com',ws_path:'/ws',ws_host:'{domain}'}}))">Copy JSON</button>
                    <span style="font-size:0.75em;">{{
    "protocol": "ssh",
    "host": "speed.cloudflare.com",
    "port": 443,
    "username": "root",
    "password": "{password}",
    "sni": "cloudflare.com",
    "ws_path": "/ws",
    "ws_host": "{domain}"
}}</span>
                </div>
            </div>
        </div>
        
        <p class="subtitle" style="margin-top:30px;">
            <span class="quantum-text">⬡</span> Quantum SSH Tunnel <span class="quantum-text">⬡</span>
        </p>
    </div>
    
    <script>
        // ============================================
        // Hex Matrix Canvas
        // ============================================
        const canvas = document.getElementById('hexCanvas');
        const ctx = canvas.getContext('2d');
        
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        
        const hexSize = 30;
        const hexHeight = hexSize * Math.sqrt(3);
        const hexWidth = hexSize * 2;
        let hexagons = [];
        
        class Hexagon {{
            constructor(x, y) {{
                this.x = x;
                this.y = y;
                this.size = hexSize;
                this.opacity = Math.random() * 0.5 + 0.1;
                this.speed = Math.random() * 0.02 + 0.005;
                this.angle = Math.random() * Math.PI * 2;
                this.color = this.randomColor();
                this.distance = Math.sqrt((x - canvas.width/2) ** 2 + (y - canvas.height/2) ** 2) / Math.max(canvas.width, canvas.height);
            }}
            
            randomColor() {{
                const colors = ['#6600cc', '#9900ff', '#00ccff', '#ff00cc', '#00ffcc', '#ff6600'];
                return colors[Math.floor(Math.random() * colors.length)];
            }}
            
            draw(ctx, time) {{
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.angle + time * 0.5);
                
                const alpha = this.opacity + Math.sin(time * 2 + this.distance * 10) * 0.3;
                
                ctx.beginPath();
                for (let i = 0; i < 6; i++) {{
                    const angle = (i * Math.PI) / 3;
                    const x = this.size * Math.cos(angle);
                    const y = this.size * Math.sin(angle);
                    if (i === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                }}
                ctx.closePath();
                ctx.strokeStyle = this.color;
                ctx.globalAlpha = Math.max(0.05, alpha);
                ctx.lineWidth = 1;
                ctx.stroke();
                
                // Inner glow
                ctx.globalAlpha = Math.max(0.02, alpha * 0.5);
                ctx.strokeStyle = '#fff';
                ctx.lineWidth = 0.5;
                ctx.stroke();
                
                ctx.restore();
                
                this.angle += this.speed;
            }}
        }}
        
        function createHexagons() {{
            hexagons = [];
            const cols = Math.ceil(canvas.width / (hexWidth * 0.75)) + 1;
            const rows = Math.ceil(canvas.height / hexHeight) + 1;
            
            for (let row = -1; row < rows; row++) {{
                for (let col = -1; col < cols; col++) {{
                    const x = col * hexWidth * 0.75;
                    const y = row * hexHeight + (col % 2) * hexHeight / 2;
                    hexagons.push(new Hexagon(x, y));
                }}
            }}
        }}
        
        function animate(time) {{
            ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            hexagons.forEach(hex => hex.draw(ctx, time * 0.001));
            
            requestAnimationFrame(animate);
        }}
        
        createHexagons();
        requestAnimationFrame(animate);
        
        window.addEventListener('resize', () => {{
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            createHexagons();
        }});
        
        // ============================================
        // Tab Switching
        // ============================================
        function showTab(tabName) {{
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.getElementById('tab-' + tabName).classList.add('active');
            event.target.classList.add('active');
        }}
        
        // ============================================
        // Copy to Clipboard
        // ============================================
        function copyText(text) {{
            navigator.clipboard.writeText(text).then(() => {{
                const btn = event.target;
                btn.textContent = 'Copied!';
                btn.style.background = '#00ff41';
                btn.style.color = '#000';
                setTimeout(() => {{
                    btn.textContent = 'Copy';
                    btn.style.background = '#6600cc';
                    btn.style.color = '#fff';
                }}, 2000);
            }});
        }}
    </script>
</body>
</html>
"""
    return HTMLResponse(html)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
