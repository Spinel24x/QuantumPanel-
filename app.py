from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn, os, json, base64
from pathlib import Path

app = FastAPI(title="Quantum Panel v10")

def load_info():
    try: return json.loads(Path("/app/data/info.json").read_text())
    except: return {
        "uuid":"x","uuid_vmess":"x","trojan_pass":"x","ss_pass":"x",
        "domain":"localhost","tcp_host":"x","tcp_port":1,"ssh_host":"x","ssh_port":1,
        "paths":{"vless":"/vless","vmess":"/vmess","trojan":"/trojan","ss":"/ss"}
    }

@app.get("/api/configs")
async def configs(address: str = "", sni: str = "", mode: str = "direct"):
    i = load_info()
    h = i.get("domain","")
    paths = i.get("paths",{})
    
    if not sni: sni = "www.speedtest.net"
    
    if mode == "cdn":
        if not address: address = "speed.cloudflare.com"
        dest, port, security = address, 443, "tls"
    elif mode == "tls":
        dest, port, security = i.get("tcp_host",""), i.get("tcp_port",35093), "tls"
    else:
        dest, port, security = i.get("tcp_host",""), i.get("tcp_port",35093), "none"
    
    vless = f"vless://{i['uuid']}@{dest}:{port}?encryption=none&security={security}"
    if security == "tls": vless += f"&sni={sni}&fp=chrome"
    vless += f"&type=ws&host={h}&path={paths.get('vless','/vless')}#Quantum"
    
    vmess_config = {
        "v":"2","ps":"Quantum","add":dest,"port":port,"id":i["uuid_vmess"],"aid":0,
        "net":"ws","type":"none","host":h,"path":paths.get("vmess","/vmess"),
        "tls":security,"sni":sni if security=="tls" else "","fp":"chrome" if security=="tls" else ""
    }
    vmess = "vmess://" + base64.b64encode(json.dumps(vmess_config).encode()).decode()
    
    trojan = f"trojan://{i['trojan_pass']}@{dest}:{port}?security={security}"
    if security == "tls": trojan += f"&sni={sni}"
    trojan += f"&type=ws&host={h}&path={paths.get('trojan','/trojan')}#Quantum"
    
    ss_b64 = base64.b64encode(f"aes-256-gcm:{i['ss_pass']}".encode()).decode()
    ss = f"ss://{ss_b64}@{dest}:{port}?path={paths.get('ss','/ss')}&host={h}#Quantum"
    
    ssh_cmd = f"ssh -D 1080 -p {i.get('ssh_port',53742)} -o ServerAliveInterval=30 root@{i.get('ssh_host','')}"
    
    return JSONResponse({
        "vless":{"name":"VLESS","icon":"🟣","link":vless},
        "vmess":{"name":"VMess","icon":"🟠","link":vmess},
        "trojan":{"name":"Trojan","icon":"🔴","link":trojan},
        "ss":{"name":"Shadowsocks","icon":"🟡","link":ss},
        "ssh":{"name":"SSH Tunnel","icon":"🔵","command":ssh_cmd,"pass":"quantum123"},
        "settings":{"mode":mode,"dest":dest,"port":port,"security":security,"host":h}
    })

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return HTMLResponse("""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Quantum v10</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#000;color:#fff;font-family:'Courier New',monospace;min-height:100vh;overflow-x:hidden}
canvas{position:fixed;top:0;left:0;z-index:0}
.container{position:relative;z-index:2;max-width:850px;margin:0 auto;padding:20px}
.title{font-size:3em;text-align:center;background:linear-gradient(135deg,#60c,#0cf,#f0c,#60c);background-size:300% 300%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:s 4s ease infinite;letter-spacing:10px;margin:30px 0 15px}
@keyframes s{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
.subtitle{text-align:center;color:rgba(255,255,255,0.4);margin-bottom:25px;font-size:0.7em;letter-spacing:5px}
.mode-row{display:flex;gap:10px;margin-bottom:20px;flex-wrap:wrap;justify-content:center}
.mode-btn{padding:12px 25px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.1);border-radius:25px;cursor:pointer;color:rgba(255,255,255,0.5);font-family:'Courier New',monospace;font-size:0.8em;transition:all 0.3s}
.mode-btn:hover{background:rgba(102,0,204,0.2);color:#fff}
.mode-btn.active{background:rgba(102,0,204,0.3);color:#fff;border-color:#60c;box-shadow:0 0 20px rgba(102,0,204,0.3)}
.input-row{display:flex;gap:10px;margin:15px 0;flex-wrap:wrap;justify-content:center}
.input-row input{padding:12px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:25px;color:#0cf;font-family:'Courier New',monospace;text-align:center;min-width:200px}
.btn{background:#60c;color:#fff;border:none;padding:14px 40px;border-radius:25px;cursor:pointer;font-family:'Courier New',monospace;font-size:0.9em;letter-spacing:3px;width:100%}
.btn:hover{background:#90f;box-shadow:0 0 30px rgba(102,0,204,0.5)}
.tabs{display:flex;justify-content:center;gap:10px;margin:20px 0;flex-wrap:wrap}
.tab{padding:15px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.1);border-radius:30px;cursor:pointer;color:rgba(255,255,255,0.5)}
.tab:hover{background:rgba(102,0,204,0.2);color:#fff}
.tab.active{background:rgba(102,0,204,0.3);color:#fff;border-color:#60c}
.tab .icon{font-size:1.5em;display:block;margin-bottom:5px}
.tab .name{font-size:0.7em;letter-spacing:2px}
.config-item{display:none;padding:20px;margin:10px 0;border-radius:15px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);text-align:center}
.config-item.active{display:block}
.config-icon{font-size:2.5em;margin-bottom:10px}
.config-name{font-size:1em;font-weight:bold;letter-spacing:3px;margin-bottom:15px;color:#fff}
.config-value{color:#0f0;font-size:0.7em;word-break:break-all;line-height:2;padding:15px;border-radius:10px;background:rgba(0,0,0,0.4);text-align:left;position:relative}
.copy-btn{position:absolute;top:10px;right:10px;background:#60c;color:#fff;border:none;padding:6px 14px;border-radius:15px;cursor:pointer;font-size:0.65em}
.copy-btn:hover{background:#90f}
.footer{text-align:center;margin-top:30px;color:rgba(255,255,255,0.1);font-size:0.6em;letter-spacing:5px}
</style></head>
<body><canvas id="c"></canvas>
<div class="container">
<h1 class="title">QUANTUM v10</h1>
<p class="subtitle">MULTI-MODE PROTOCOL PANEL</p>
<div class="mode-row">
<div class="mode-btn active" onclick="setMode('direct',this)">Direct</div>
<div class="mode-btn" onclick="setMode('tls',this)">TLS</div>
<div class="mode-btn" onclick="setMode('cdn',this)">CDN</div>
</div>
<div class="input-row"><input id="addr" placeholder="Address (auto)"><input id="sni" value="www.speedtest.net" placeholder="SNI"></div>
<button class="btn" onclick="gen()">GENERATE</button>
<div class="tabs" id="tabs"></div><div id="boxes"></div>
<p class="footer">VLESS | VMess | Trojan | SS | SSH</p>
</div>
<script>
var c=document.getElementById('c'),ctx=c.getContext('2d');c.width=window.innerWidth;c.height=window.innerHeight;
var particles=[];
function DNA(){this.reset()}
DNA.prototype.reset=function(){this.x=Math.random()*c.width;this.y=Math.random()*c.height;this.len=Math.random()*150+50;this.angle=Math.random()*Math.PI*2;this.speed=Math.random()*0.5+0.2;this.amplitude=Math.random()*30+10;this.phase=Math.random()*Math.PI*2;this.color=[[102,0,204],[153,0,255],[0,204,255],[255,0,204],[0,255,204]][Math.floor(Math.random()*5)];this.life=0;this.maxLife=300+Math.random()*200};
DNA.prototype.update=function(){this.life++;if(this.life>this.maxLife)this.reset();this.phase+=0.02};
DNA.prototype.draw=function(ctx){var a=Math.sin(Math.PI*this.life/this.maxLife)*0.4;ctx.strokeStyle='rgba('+this.color[0]+','+this.color[1]+','+this.color[2]+','+a+')';ctx.lineWidth=1.2;ctx.beginPath();for(var i=0;i<=this.len;i+=5){var t=i/this.len;var x=this.x+Math.cos(this.angle)*i+Math.sin(this.angle+this.phase+t*8)*this.amplitude;var y=this.y+Math.sin(this.angle)*i+Math.cos(this.angle+this.phase+t*8)*this.amplitude*0.5;if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y)}ctx.stroke()};
for(var i=0;i<25;i++)particles.push(new DNA());
(function a(){ctx.fillStyle='rgba(0,0,0,0.08)';ctx.fillRect(0,0,c.width,c.height);for(var i=0;i<particles.length;i++){particles[i].update();particles[i].draw(ctx)}requestAnimationFrame(a)})();

var currentMode='direct',configs={};
function setMode(m,el){currentMode=m;var btns=document.querySelectorAll('.mode-btn');for(var i=0;i<btns.length;i++)btns[i].classList.remove('active');el.classList.add('active')}
function gen(){var a=document.getElementById('addr').value;var s=document.getElementById('sni').value;fetch('/api/configs?address='+a+'&sni='+s+'&mode='+currentMode).then(function(r){return r.json()}).then(function(d){configs=d;render()})}
function render(){var tc=document.getElementById('tabs'),bc=document.getElementById('boxes');tc.innerHTML='';bc.innerHTML='';var first=true;for(var k in configs){if(k==='settings')continue;var v=configs[k];var t=document.createElement('div');t.className='tab'+(first?' active':'');t.innerHTML='<span class="icon">'+v.icon+'</span><span class="name">'+v.name+'</span>';t.onclick=(function(key,el){return function(){var tabs=document.querySelectorAll('.tab');for(var i=0;i<tabs.length;i++)tabs[i].classList.remove('active');var items=document.querySelectorAll('.config-item');for(var i=0;i<items.length;i++)items[i].classList.remove('active');el.classList.add('active');document.getElementById('item-'+key).classList.add('active')}})(k,t);tc.appendChild(t);var b=document.createElement('div');b.className='config-item'+(first?' active':'');b.id='item-'+k;var txt=v.link||v.command||'';b.innerHTML='<div class="config-icon">'+v.icon+'</div><div class="config-name">'+v.name+'</div><div class="config-value"><button class="copy-btn" onclick="var t=configs[\''+k+'\'].link||configs[\''+k+'\'].command;navigator.clipboard.writeText(t);this.textContent=\'OK\';this.style.background=\'#0f0\';var s=this;setTimeout(function(){s.textContent=\'COPY\';s.style.background=\'#60c\'},2000)">COPY</button>'+txt+'</div>';bc.appendChild(b);first=false}}
setTimeout(gen,300);
</script></body></html>""")

if __name__=="__main__":
    uvicorn.run(app,host="0.0.0.0",port=9000)
