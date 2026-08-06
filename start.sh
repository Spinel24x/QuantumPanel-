from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn, os, json, base64
from pathlib import Path

app = FastAPI(title="Quantum Panel v6")

def load_info():
    try: return json.loads(Path("/app/data/info.json").read_text())
    except: return {
        "uuid":"x","uuid_vmess":"x","trojan_pass":"x","domain":"localhost",
        "server_public_key":"x","client_private_key":"x",
        "vless":{"host":"metro","port":35093,"path":"/vless"},
        "vmess":{"host":"metro","port":35093,"path":"/vmess"},
        "trojan":{"host":"metro","port":35093,"path":"/trojan"},
        "wireguard":{"host":"sakura","port":53742},
        "ssh":{"host":"sakura","port":53742,"user":"root","pass":"quantum123"}
    }

@app.get("/api/configs")
async def configs():
    i = load_info()
    h = i.get("domain","")
    
    vmess_config = {
        "v": "2", "ps": "Quantum-VMess",
        "add": i["vmess"]["host"], "port": i["vmess"]["port"],
        "id": i["uuid_vmess"], "aid": 0, "scy": "auto",
        "net": "ws", "type": "none", "host": h,
        "path": i["vmess"]["path"], "tls": "none"
    }
    vmess_link = "vmess://" + base64.b64encode(json.dumps(vmess_config).encode()).decode()
    
    wg_config = f"""[Interface]
PrivateKey = {i['client_private_key']}
Address = 10.0.0.2/32
DNS = 8.8.8.8

[Peer]
PublicKey = {i['server_public_key']}
Endpoint = {i['wireguard']['host']}:{i['wireguard']['port']}
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25"""
    
    return JSONResponse({
        "vless": {
            "name":"VLESS + WS","icon":"🟣",
            "link":f"vless://{i['uuid']}@{i['vless']['host']}:{i['vless']['port']}?encryption=none&security=none&type=ws&path={i['vless']['path']}&host={h}#Quantum"
        },
        "vmess": {
            "name":"VMess + WS","icon":"🟠",
            "link":vmess_link
        },
        "trojan": {
            "name":"Trojan + WS","icon":"🔴",
            "link":f"trojan://{i['trojan_pass']}@{i['trojan']['host']}:{i['trojan']['port']}?security=none&type=ws&path={i['trojan']['path']}&host={h}#Quantum"
        },
        "wireguard": {
            "name":"WireGuard","icon":"🟢",
            "config": wg_config
        },
        "ssh": {
            "name":"SSH Tunnel","icon":"🔵",
            "command":f"ssh -D 1080 -p {i['ssh']['port']} root@{i['ssh']['host']}",
            "pass":i['ssh']['pass']
        }
    })

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return HTMLResponse("""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Quantum v6</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#000;color:#fff;font-family:'Courier New',monospace;min-height:100vh;overflow-x:hidden}
canvas{position:fixed;top:0;left:0;z-index:0}
.container{position:relative;z-index:2;max-width:950px;margin:0 auto;padding:20px}
.panel{background:rgba(5,5,20,0.88);border:1px solid rgba(102,0,204,0.25);border-radius:24px;padding:35px;margin-bottom:20px;box-shadow:0 0 80px rgba(102,0,204,0.15);backdrop-filter:blur(24px)}
.title{font-size:2.8em;text-align:center;background:linear-gradient(135deg,#6600cc,#00ccff,#ff00cc,#6600cc);background-size:300% 300%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:shift 4s ease infinite;letter-spacing:8px}
@keyframes shift{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
.subtitle{text-align:center;color:rgba(102,0,204,0.7);margin:8px 0 25px;font-size:0.8em;letter-spacing:4px}
.tabs{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:8px;margin-bottom:20px}
.tab{padding:15px 10px;background:rgba(102,0,204,0.12);border:1px solid rgba(102,0,204,0.2);border-radius:14px;text-align:center;cursor:pointer;color:#999;transition:all 0.3s}
.tab:hover{background:rgba(102,0,204,0.25);color:#ccc}
.tab.active{background:#6600cc;color:#fff;border-color:#6600cc;box-shadow:0 0 30px rgba(102,0,204,0.4)}
.tab .icon{font-size:1.8em;display:block;margin-bottom:5px}
.tab .name{font-size:0.65em;letter-spacing:2px;text-transform:uppercase}
.config-box{background:rgba(0,0,0,0.7);border:1px solid rgba(102,0,204,0.2);border-radius:16px;padding:25px;position:relative;display:none;margin-top:15px}
.config-box.active{display:block;animation:fadeIn 0.3s ease}
@keyframes fadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.config-icon{font-size:3em;text-align:center;margin-bottom:10px}
.config-name{text-align:center;color:#6600cc;font-size:1em;font-weight:bold;margin-bottom:5px;text-transform:uppercase;letter-spacing:3px}
.config-value{background:rgba(0,0,0,0.6);border:1px solid rgba(102,0,204,0.2);border-radius:12px;padding:18px;color:#00ff41;font-size:0.78em;word-break:break-all;line-height:1.9;white-space:pre-wrap;position:relative;max-height:300px;overflow-y:auto}
.copy-btn{position:absolute;top:12px;right:12px;background:#6600cc;color:#fff;border:none;padding:8px 16px;border-radius:10px;cursor:pointer;font-family:'Courier New',monospace;font-size:0.7em;transition:all 0.3s;z-index:5}
.copy-btn:hover{background:#9900ff;box-shadow:0 0 20px rgba(102,0,204,0.5)}
.footer{text-align:center;margin-top:30px;color:#333;font-size:0.65em;letter-spacing:4px}
.pulse{display:inline-block;width:8px;height:8px;background:#00ff41;border-radius:50%;animation:pulse 1.5s ease-in-out infinite;margin:0 5px}
@keyframes pulse{0%,100%{opacity:1;box-shadow:0 0 10px #00ff41}50%{opacity:0.3;box-shadow:0 0 30px #00ff41}}
</style></head>
<body><canvas id="c"></canvas>
<div class="container"><div class="panel">
<h1 class="title">QUANTUM v6</h1>
<p class="subtitle"><span class="pulse"></span> 5 PROTOCOLS <span class="pulse"></span></p>
<div class="tabs" id="tabs"></div><div id="boxes"></div>
<p class="footer">⬡ VLESS ⬡ VMess ⬡ Trojan ⬡ WireGuard ⬡ SSH ⬡</p></div></div>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');c.width=window.innerWidth;c.height=window.innerHeight;
const particles=[];
class DNA{constructor(){this.reset()}
reset(){this.x=Math.random()*c.width;this.y=Math.random()*c.height;this.len=Math.random()*150+50;this.angle=Math.random()*Math.PI*2;this.speed=Math.random()*0.5+0.2;this.amplitude=Math.random()*30+10;this.phase=Math.random()*Math.PI*2;this.color=[[102,0,204],[153,0,255],[0,204,255],[255,0,204],[0,255,204]][Math.floor(Math.random()*5)];this.life=0;this.maxLife=300+Math.random()*200}
update(){this.life++;if(this.life>this.maxLife)this.reset();this.phase+=0.02}
draw(ctx){const alpha=Math.sin(Math.PI*this.life/this.maxLife)*0.5;ctx.strokeStyle=`rgba(${this.color[0]},${this.color[1]},${this.color[2]},${alpha})`;ctx.lineWidth=1.5;ctx.shadowBlur=10;ctx.shadowColor=`rgba(${this.color[0]},${this.color[1]},${this.color[2]},${alpha})`;ctx.beginPath();
for(let i=0;i<=this.len;i+=5){const t=i/this.len;const x1=this.x+Math.cos(this.angle)*i+Math.sin(this.angle+this.phase+t*8)*this.amplitude;const y1=this.y+Math.sin(this.angle)*i+Math.cos(this.angle+this.phase+t*8)*this.amplitude*0.5;
if(i===0)ctx.moveTo(x1,y1);else ctx.lineTo(x1,y1);
const x2=this.x+Math.cos(this.angle+Math.PI)*i+Math.sin(this.angle+Math.PI+this.phase+t*8)*this.amplitude;const y2=this.y+Math.sin(this.angle+Math.PI)*i+Math.cos(this.angle+Math.PI+this.phase+t*8)*this.amplitude*0.5;
const dots=[[x1,y1],[x2,y2]];dots.forEach(([dx,dy])=>{if(Math.random()<0.15){ctx.fillStyle=`rgba(${this.color[0]},${this.color[1]},${this.color[2]},${alpha*2})`;ctx.beginPath();ctx.arc(dx,dy,2,0,Math.PI*2);ctx.fill()}})}
ctx.stroke();ctx.shadowBlur=0}}
for(let i=0;i<30;i++)particles.push(new DNA());
(function a(){ctx.fillStyle='rgba(0,0,0,0.06)';ctx.fillRect(0,0,c.width,c.height);particles.forEach(p=>{p.update();p.draw(ctx)});requestAnimationFrame(a)})();
let configs={};
async function load(){const r=await fetch('/api/configs');configs=await r.json();
const tc=document.getElementById('tabs'),bc=document.getElementById('boxes');tc.innerHTML='';bc.innerHTML='';let first=true;
for(const[k,v]of Object.entries(configs)){const t=document.createElement('div');t.className='tab'+(first?' active':'');t.innerHTML=`<span class="icon">${v.icon}</span><span class="name">${v.name}</span>`;t.onclick=(e)=>{document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));e.target.closest('.tab').classList.add('active');document.querySelectorAll('.config-box').forEach(b=>b.classList.remove('active'));document.getElementById('box-'+k).classList.add('active')};tc.appendChild(t);
const b=document.createElement('div');b.className='config-box'+(first?' active':'');b.id='box-'+k;let txt=v.link||v.config||v.command||'';
b.innerHTML=`<div class="config-icon">${v.icon}</div><div class="config-name">${v.name}</div><div class="config-value"><button class="copy-btn" onclick="copy('${k}',this)">COPY</button>${txt}</div>`;bc.appendChild(b);first=false}}
function copy(k,btn){if(configs[k]){let t=configs[k].link||configs[k].config||configs[k].command;navigator.clipboard.writeText(t);btn.textContent='✓';btn.style.background='#00ff41';btn.style.color='#000';setTimeout(()=>{btn.textContent='COPY';btn.style.background='#6600cc';btn.style.color='#fff'},2000)}}
setTimeout(load,300);
</script></body></html>""")

if __name__=="__main__":
    uvicorn.run(app,host="0.0.0.0",port=9000)
