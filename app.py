from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn, os, json, base64
from pathlib import Path

app = FastAPI(title="Quantum Panel v8")

def load_info():
    try: return json.loads(Path("/app/data/info.json").read_text())
    except: return {
        "uuid":"x","uuid_vmess":"x","trojan_pass":"x","ss_pass":"x","domain":"localhost",
        "vless":{"path":"/vless"},"vmess":{"path":"/vmess"},
        "trojan":{"path":"/trojan"},"ss":{"path":"/ss"}
    }

@app.get("/api/configs")
async def configs(address: str = "", sni: str = "", tls: str = "1", cdn: str = "0"):
    i = load_info()
    h = i.get("domain","localhost")
    use_tls = tls == "1"
    use_cdn = cdn == "1"
    
    if not sni: sni = "www.speedtest.net"
    
    if use_cdn:
        if not address: address = "speed.cloudflare.com"
        dest = address
        port = 443
    else:
        if not address: address = h
        dest = address
        port = 35093 if not use_tls else 443
    
    security = "tls" if use_tls else "none"
    
    # VMess
    vmess_config = {
        "v": "2", "ps": "Quantum-VMess",
        "add": dest, "port": port, "id": i["uuid_vmess"], "aid": 0,
        "net": "ws", "type": "none", "host": h, "path": i["vmess"]["path"],
        "tls": "tls" if use_tls else "none",
        "sni": sni if use_tls else "",
        "fp": "chrome" if use_tls else ""
    }
    vmess_link = "vmess://" + base64.b64encode(json.dumps(vmess_config).encode()).decode()
    
    # VLESS
    vless_link = f"vless://{i['uuid']}@{dest}:{port}?encryption=none&security={security}"
    if use_tls: vless_link += f"&sni={sni}&fp=chrome"
    vless_link += f"&type=ws&host={h}&path={i['vless']['path']}#Quantum"
    
    # Trojan
    trojan_link = f"trojan://{i['trojan_pass']}@{dest}:{port}?security={security}"
    if use_tls: trojan_link += f"&sni={sni}"
    trojan_link += f"&type=ws&host={h}&path={i['trojan']['path']}#Quantum"
    
    # Shadowsocks
    ss_b64 = base64.b64encode(f"aes-256-gcm:{i['ss_pass']}".encode()).decode()
    ss_link = f"ss://{ss_b64}@{dest}:{port}?path={i['ss']['path']}&host={h}#Quantum"
    
    return JSONResponse({
        "vless": {"name":"VLESS","icon":"🟣","link":vless_link},
        "vmess": {"name":"VMess","icon":"🟠","link":vmess_link},
        "trojan": {"name":"Trojan","icon":"🔴","link":trojan_link},
        "ss": {"name":"Shadowsocks","icon":"🟡","link":ss_link},
        "settings": {"address": dest, "port": port, "sni": sni, "host": h, "tls": use_tls, "cdn": use_cdn}
    })

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return HTMLResponse("""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Quantum v8</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#000;color:#fff;font-family:'Courier New',monospace;min-height:100vh;overflow-x:hidden}
canvas{position:fixed;top:0;left:0;z-index:0}
.container{position:relative;z-index:2;max-width:850px;margin:0 auto;padding:20px}
.title{font-size:3em;text-align:center;background:linear-gradient(135deg,#6600cc,#00ccff,#ff00cc,#6600cc);background-size:300% 300%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:shift 4s ease infinite;letter-spacing:10px;margin:30px 0 10px}
@keyframes shift{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
.subtitle{text-align:center;color:rgba(255,255,255,0.4);margin-bottom:25px;font-size:0.7em;letter-spacing:5px}
.settings-row{display:flex;gap:15px;margin-bottom:20px;flex-wrap:wrap;justify-content:center;align-items:center}
.checkbox-group{display:flex;align-items:center;gap:8px;color:rgba(255,255,255,0.6);font-size:0.75em;letter-spacing:1px;cursor:pointer}
.checkbox-group input{display:none}
.checkbox-custom{width:20px;height:20px;border:2px solid rgba(102,0,204,0.5);border-radius:5px;display:inline-block;position:relative}
.checkbox-group input:checked+.checkbox-custom{background:#6600cc;border-color:#6600cc}
.checkbox-group input:checked+.checkbox-custom::after{content:'\\2713';position:absolute;top:-2px;left:4px;color:#fff;font-size:0.9em}
.address-area{display:none;flex-direction:column;gap:10px;margin:15px 0;text-align:center}
.address-area.show{display:flex}
.address-area textarea{padding:15px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:15px;color:#0cf;font-family:'Courier New',monospace;font-size:0.75em;resize:vertical;min-height:80px}
.address-area textarea:focus{outline:none;border-color:#6600cc}
.address-area .hint{color:rgba(255,255,255,0.3);font-size:0.65em}
.input-row{display:flex;gap:15px;margin-bottom:15px;flex-wrap:wrap;justify-content:center}
.input-row input{padding:12px 20px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:25px;color:#0cf;font-family:'Courier New',monospace;font-size:0.8em;min-width:200px;text-align:center}
.btn{background:#6600cc;color:#fff;border:none;padding:14px 40px;border-radius:25px;cursor:pointer;font-family:'Courier New',monospace;font-size:0.85em;letter-spacing:3px}
.btn:hover{background:#9900ff;box-shadow:0 0 30px rgba(102,0,204,0.5)}
.info-badge{text-align:center;margin:15px 0;padding:10px;border-radius:20px;background:rgba(102,0,204,0.15);border:1px solid rgba(102,0,204,0.2);font-size:0.7em;color:rgba(255,255,255,0.5);display:none}
.info-badge.show{display:block}
.tabs{display:flex;justify-content:center;gap:10px;margin-bottom:25px;flex-wrap:wrap}
.tab{padding:15px 25px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:30px;cursor:pointer;color:rgba(255,255,255,0.5);backdrop-filter:blur(5px)}
.tab:hover{background:rgba(102,0,204,0.2);color:#fff}
.tab.active{background:rgba(102,0,204,0.3);color:#fff;border-color:#6600cc;box-shadow:0 0 30px rgba(102,0,204,0.3)}
.tab .icon{font-size:1.5em;display:block;margin-bottom:5px}
.tab .name{font-size:0.7em;letter-spacing:2px}
.config-item{display:none;padding:20px;margin:10px 0;border-radius:15px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);backdrop-filter:blur(10px);text-align:center}
.config-item.active{display:block}
.config-icon{font-size:2.5em;margin-bottom:10px}
.config-name{color:#fff;font-size:1em;font-weight:bold;letter-spacing:3px;margin-bottom:15px}
.config-value{color:#0f0;font-size:0.7em;word-break:break-all;line-height:2;padding:15px;border-radius:10px;background:rgba(0,0,0,0.4);text-align:left;position:relative}
.copy-btn{position:absolute;top:10px;right:10px;background:#6600cc;color:#fff;border:none;padding:6px 14px;border-radius:15px;cursor:pointer;font-size:0.65em}
.copy-btn:hover{background:#9900ff}
.footer{text-align:center;margin-top:50px;color:rgba(255,255,255,0.1);font-size:0.6em;letter-spacing:5px}
</style></head>
<body><canvas id="c"></canvas>
<div class="container">
<h1 class="title">QUANTUM</h1>
<p class="subtitle">\\u2728 AUTO CONFIG GENERATOR \\u2728</p>
<div class="settings-row">
<label class="checkbox-group">
<input type="checkbox" id="tlsCheck" checked onchange="document.getElementById('sniInput').style.display=this.checked?'inline-block':'none'"><span class="checkbox-custom"></span>TLS
</label>
<label class="checkbox-group">
<input type="checkbox" id="cdnCheck" onchange="document.getElementById('addressArea').classList.toggle('show',this.checked)"><span class="checkbox-custom"></span>Cloudflare CDN
</label>
</div>
<div class="input-row"><input id="sniInput" value="www.speedtest.net" placeholder="SNI"></div>
<div class="address-area" id="addressArea">
<textarea id="addressInput" placeholder="speed.cloudflare.com\\n104.26.0.1\\n..."></textarea>
<p class="hint">\\u2728 One address per line \\u2728</p>
</div>
<button class="btn" onclick="gen()">\\u26a1 GENERATE</button>
<div class="info-badge" id="infoBadge"></div>
<div class="tabs" id="tabs"></div><div id="boxes"></div>
<p class="footer">VLESS \\u2728 VMess \\u2728 Trojan \\u2728 Shadowsocks</p>
</div>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');c.width=window.innerWidth;c.height=window.innerHeight;
const particles=[];
class DNA{constructor(){this.reset()}
reset(){this.x=Math.random()*c.width;this.y=Math.random()*c.height;this.len=Math.random()*150+50;this.angle=Math.random()*Math.PI*2;this.speed=Math.random()*0.5+0.2;this.amplitude=Math.random()*30+10;this.phase=Math.random()*Math.PI*2;this.color=[[102,0,204],[153,0,255],[0,204,255],[255,0,204],[0,255,204]][Math.floor(Math.random()*5)];this.life=0;this.maxLife=300+Math.random()*200}
update(){this.life++;if(this.life>this.maxLife)this.reset();this.phase+=0.02}
draw(ctx){var a=Math.sin(Math.PI*this.life/this.maxLife)*0.4;ctx.strokeStyle='rgba('+this.color[0]+','+this.color[1]+','+this.color[2]+','+a+')';ctx.lineWidth=1.2;ctx.shadowBlur=8;ctx.shadowColor='rgba('+this.color[0]+','+this.color[1]+','+this.color[2]+','+a+')';ctx.beginPath();
for(var i=0;i<=this.len;i+=5){var t=i/this.len;var x1=this.x+Math.cos(this.angle)*i+Math.sin(this.angle+this.phase+t*8)*this.amplitude;var y1=this.y+Math.sin(this.angle)*i+Math.cos(this.angle+this.phase+t*8)*this.amplitude*0.5;
if(i===0)ctx.moveTo(x1,y1);else ctx.lineTo(x1,y1)}
ctx.stroke();ctx.shadowBlur=0}}
for(var i=0;i<25;i++)particles.push(new DNA());
(function a(){ctx.fillStyle='rgba(0,0,0,0.08)';ctx.fillRect(0,0,c.width,c.height);particles.forEach(function(p){p.update();p.draw(ctx)});requestAnimationFrame(a)})();
var configs={};
async function gen(){var tls=document.getElementById('tlsCheck').checked?'1':'0';var cdn=document.getElementById('cdnCheck').checked?'1':'0';var sni=document.getElementById('sniInput').value||'www.speedtest.net';var addr='';if(cdn==='1'){addr=document.getElementById('addressInput').value.split('\\n')[0].trim()||'speed.cloudflare.com'}var r=await fetch('/api/configs?address='+addr+'&sni='+sni+'&tls='+tls+'&cdn='+cdn);configs=await r.json();var s=configs.settings;document.getElementById('infoBadge').textContent=s.host+' :'+s.port+' TLS:'+(s.tls?'ON':'OFF')+' CDN:'+(s.cdn?'ON':'OFF');document.getElementById('infoBadge').classList.add('show');render()}
function render(){var tc=document.getElementById('tabs'),bc=document.getElementById('boxes');tc.innerHTML='';bc.innerHTML='';var first=true;for(var k in configs){if(k==='settings')continue;var v=configs[k];var t=document.createElement('div');t.className='tab'+(first?' active':'');t.innerHTML='<span class="icon">'+v.icon+'</span><span class="name">'+v.name+'</span>';t.onclick=(function(key){return function(){document.querySelectorAll('.tab').forEach(function(x){x.classList.remove('active')});document.querySelectorAll('.config-item').forEach(function(b){b.classList.remove('active')});this.classList.add('active');document.getElementById('item-'+key).classList.add('active')}})(k);tc.appendChild(t);var b=document.createElement('div');b.className='config-item'+(first?' active':'');b.id='item-'+k;b.innerHTML='<div class="config-icon">'+v.icon+'</div><div class="config-name">'+v.name+'</div><div class="config-value"><button class="copy-btn" onclick="copyC(\\''+k+'\\',this)">COPY</button>'+v.link+'</div>';bc.appendChild(b);first=false}}
function copyC(k,btn){if(configs[k]){navigator.clipboard.writeText(configs[k].link);btn.textContent='\\u2713';btn.style.background='#0f0';btn.style.color='#000';setTimeout(function(){btn.textContent='COPY';btn.style.background='#6600cc';btn.style.color='#fff'},2000)}}
setTimeout(gen,300);
</script></body></html>""")

if __name__=="__main__":
    uvicorn.run(app,host="0.0.0.0",port=9000)
