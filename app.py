from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn, os, json, base64
from pathlib import Path

app = FastAPI(title="Quantum Panel v9")

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
    use_cdn = cdn == "0"  # Fix: cdn default off
    
    if not sni: sni = "www.speedtest.net"
    if not address: address = "metro.proxy.rlwy.net"
    
    port = 35093
    security = "none"
    
    if use_tls:
        security = "tls"
        port = 35093
    
    vless = f"vless://{i['uuid']}@{address}:{port}?encryption=none&security={security}"
    if use_tls: vless += f"&sni={sni}&fp=chrome"
    vless += f"&type=ws&host={h}&path={i['vless']['path']}#Quantum"
    
    vmess_config = {
        "v":"2","ps":"Quantum","add":address,"port":port,"id":i["uuid_vmess"],"aid":0,
        "net":"ws","type":"none","host":h,"path":i["vmess"]["path"],
        "tls":"tls" if use_tls else "none","sni":sni if use_tls else ""
    }
    vmess = "vmess://" + base64.b64encode(json.dumps(vmess_config).encode()).decode()
    
    trojan = f"trojan://{i['trojan_pass']}@{address}:{port}?security={security}"
    if use_tls: trojan += f"&sni={sni}"
    trojan += f"&type=ws&host={h}&path={i['trojan']['path']}#Quantum"
    
    ss_b64 = base64.b64encode(f"aes-256-gcm:{i['ss_pass']}".encode()).decode()
    ss = f"ss://{ss_b64}@{address}:{port}?path={i['ss']['path']}&host={h}#Quantum"
    
    return JSONResponse({
        "vless":{"name":"VLESS","icon":"🟣","link":vless},
        "vmess":{"name":"VMess","icon":"🟠","link":vmess},
        "trojan":{"name":"Trojan","icon":"🔴","link":trojan},
        "ss":{"name":"SS","icon":"🟡","link":ss},
        "settings":{"tls":use_tls,"cdn":use_cdn,"host":h}
    })

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return HTMLResponse("""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Quantum</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#000;color:#fff;font-family:'Courier New',monospace;min-height:100vh}
.container{max-width:800px;margin:0 auto;padding:20px}
.title{font-size:3em;text-align:center;background:linear-gradient(135deg,#60c,#0cf,#f0c,#60c);background-size:300% 300%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:s 4s ease infinite;letter-spacing:10px;margin:30px 0}
@keyframes s{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
.row{display:flex;gap:10px;margin:15px 0;flex-wrap:wrap;justify-content:center}
.row input{padding:12px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:25px;color:#0cf;font-family:'Courier New',monospace;text-align:center;min-width:200px}
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
</style></head>
<body>
<div class="container">
<h1 class="title">QUANTUM</h1>
<div class="row"><input id="addr" value="metro.proxy.rlwy.net" placeholder="Address"><input id="sni" value="www.speedtest.net" placeholder="SNI"></div>
<div class="row"><label style="color:#aaa"><input type="checkbox" id="tls" checked> TLS</label></div>
<button class="btn" onclick="gen()">GENERATE</button>
<div class="tabs" id="tabs"></div><div id="boxes"></div>
</div>
<script>
var configs={};
async function gen(){var a=document.getElementById('addr').value,s=document.getElementById('sni').value,t=document.getElementById('tls').checked?'1':'0';var r=await fetch('/api/configs?address='+a+'&sni='+s+'&tls='+t);configs=await r.json();render();}
function render(){var tc=document.getElementById('tabs'),bc=document.getElementById('boxes');tc.innerHTML='';bc.innerHTML='';var first=true;
for(var k in configs){if(k==='settings')continue;var v=configs[k];var t=document.createElement('div');t.className='tab'+(first?' active':'');t.innerHTML='<span class="icon">'+v.icon+'</span><span class="name">'+v.name+'</span>';t.onclick=(function(key){return function(){document.querySelectorAll('.tab').forEach(function(x){x.classList.remove('active')});document.querySelectorAll('.config-item').forEach(function(b){b.classList.remove('active')});this.classList.add('active');document.getElementById('item-'+key).classList.add('active')}})(k);tc.appendChild(t);
var b=document.createElement('div');b.className='config-item'+(first?' active':'');b.id='item-'+k;b.innerHTML='<div class="config-icon">'+v.icon+'</div><div class="config-name">'+v.name+'</div><div class="config-value"><button class="copy-btn" onclick="var t=configs[\''+k+'\'].link;navigator.clipboard.writeText(t);this.textContent=\\'\\u2713\\';this.style.background=\\'#0f0\\';var s=this;setTimeout(function(){s.textContent=\\'COPY\\';s.style.background=\\'#60c\\'},2000)">COPY</button>'+v.link+'</div>';bc.appendChild(b);first=false}}
setTimeout(gen,300);
</script></body></html>""")

if __name__=="__main__":
    uvicorn.run(app,host="0.0.0.0",port=9000)
