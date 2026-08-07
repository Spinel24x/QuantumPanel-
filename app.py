from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn, os, json
from pathlib import Path
from config_generator import generate_all, load_info, load_ips

app = FastAPI(title="Quantum Panel Pro")

@app.get("/api/configs")
async def configs(address: str = "", sni: str = "", cf: str = "0"):
    info = load_info()
    ips = load_ips()
    
    use_cf = cf == "1"
    
    configs = generate_all(
        uuid=info.get("uuid", ""),
        uuid_vmess=info.get("uuid_vmess", ""),
        trojan_pass=info.get("trojan_pass", ""),
        ss_pass=info.get("ss_pass", ""),
        use_cf=use_cf,
        clean_ip=address if address else "",
        sni=sni if sni else ""
    )
    
    configs["settings"] = {
        "cf": use_cf,
        "clean_ips": ips.get("clean_ips", []),
        "connection": configs.get("connection", {})
    }
    
    return JSONResponse(configs)

@app.get("/api/hydtun")
async def hydtun():
    return JSONResponse({
        "status": "coming_soon",
        "port": 8888,
        "message": "HYD.TUN will be available soon"
    })

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return HTMLResponse("""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Quantum Pro</title>
<style>
body{background:#000;color:#fff;font-family:'Courier New',monospace;padding:20px;margin:0}
h1{text-align:center;font-size:2.5em;background:linear-gradient(135deg,#60c,#0cf);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:20px 0}
.main-tabs{display:flex;justify-content:center;gap:10px;margin:20px 0}
.main-tab{padding:15px 30px;background:#111;border:1px solid #333;border-radius:30px;cursor:pointer;color:#aaa;font-size:0.9em;font-family:'Courier New',monospace;transition:all 0.3s}
.main-tab:hover{background:rgba(102,0,204,0.2);color:#fff}
.main-tab.active{background:#60c;color:#fff;border-color:#60c;box-shadow:0 0 20px rgba(102,0,204,0.4)}
.tab-content{display:none}
.tab-content.active{display:block}
#genBtn{display:block;width:100%;max-width:400px;margin:15px auto;padding:14px;background:#60c;color:#fff;border:none;border-radius:25px;font-size:1em;cursor:pointer;font-family:'Courier New',monospace;letter-spacing:3px}
#genBtn:hover{background:#90f}
.proto-tabs{display:flex;flex-wrap:wrap;gap:5px;justify-content:center;margin:15px 0}
.proto-tab{padding:10px 15px;background:#111;border:1px solid #333;border-radius:20px;color:#aaa;cursor:pointer;font-size:0.8em;font-family:'Courier New',monospace}
.proto-tab.active{background:#60c;color:#fff;border-color:#60c}
.proto-content{display:none;background:#111;border:1px solid #333;border-radius:15px;padding:20px;margin:10px 0}
.proto-content.active{display:block}
.config-link{color:#0f0;font-size:0.75em;word-break:break-all;line-height:1.8;position:relative}
.copy-btn{position:absolute;top:5px;right:5px;background:#60c;color:#fff;border:none;padding:5px 12px;border-radius:10px;cursor:pointer;font-size:0.7em}
.copy-btn:hover{background:#90f}
.info{text-align:center;color:#666;margin:10px 0;font-size:0.7em}
.coming-soon{text-align:center;padding:50px;color:#666;font-size:1.2em}
</style></head>
<body>
<h1>QUANTUM PRO</h1>

<!-- Main Tabs -->
<div class="main-tabs">
<div class="main-tab active" onclick="switchMainTab('railway',this)">🚀 RailwayTunnel</div>
<div class="main-tab" onclick="switchMainTab('hydtun',this)">⚡ HYD.TUN</div>
</div>

<!-- RailwayTunnel Tab -->
<div class="tab-content active" id="tab-railway">
<button id="genBtn" onclick="generate()">GENERATE CONFIGS</button>
<div class="info" id="infoBar"></div>
<div class="proto-tabs" id="protoTabs"></div>
<div id="protoContents"></div>
</div>

<!-- HYD.TUN Tab -->
<div class="tab-content" id="tab-hydtun">
<div class="coming-soon">⚡ HYD.TUN<br><br>Port 8888<br><br>Coming Soon...</div>
</div>

<script>
var data={};

function switchMainTab(tab,el){
  document.querySelectorAll('.main-tab').forEach(function(t){t.classList.remove('active')});
  document.querySelectorAll('.tab-content').forEach(function(t){t.classList.remove('active')});
  el.classList.add('active');
  document.getElementById('tab-'+tab).classList.add('active');
  if(tab==='railway') generate();
}

function generate(){
  fetch('/api/configs?address=&sni=&cf=0')
    .then(function(r){return r.json()})
    .then(function(d){data=d;show();})
    .catch(function(e){document.getElementById('infoBar').textContent='Error: '+e;});
}

function show(){
  var protoTabs=document.getElementById('protoTabs'),protoContents=document.getElementById('protoContents'),infoBar=document.getElementById('infoBar');
  protoTabs.innerHTML='';protoContents.innerHTML='';
  if(data.connection){var c=data.connection;infoBar.textContent=c.address+':'+c.port+' | '+c.security.toUpperCase()+' | Host:'+c.host;}
  var first=true;
  for(var k in data){
    if(k==='settings'||k==='connection')continue;
    var v=data[k];
    var tb=document.createElement('div');tb.className='proto-tab'+(first?' active':'');tb.textContent=v.name;tb.setAttribute('data-key',k);
    tb.onclick=function(){var key=this.getAttribute('data-key');document.querySelectorAll('.proto-tab').forEach(function(x){x.classList.remove('active')});document.querySelectorAll('.proto-content').forEach(function(x){x.classList.remove('active')});this.classList.add('active');document.getElementById('proto-'+key).classList.add('active')};
    protoTabs.appendChild(tb);
    var tc=document.createElement('div');tc.className='proto-content'+(first?' active':'');tc.id='proto-'+k;
    var txt=v.link||'';
    tc.innerHTML='<h3>'+v.icon+' '+v.name+'</h3><div class="config-link"><button class="copy-btn" onclick="copyText(this)">COPY</button>'+txt+'</div>';
    protoContents.appendChild(tc);first=false;
  }
}

function copyText(btn){var txt=btn.parentElement.textContent.replace('COPY','').trim();navigator.clipboard.writeText(txt);btn.textContent='OK';btn.style.background='#0f0';var s=btn;setTimeout(function(){s.textContent='COPY';s.style.background='#60c'},2000)}

// Auto-generate on load
generate();
</script></body></html>""")

if __name__=="__main__":
    uvicorn.run(app,host="0.0.0.0",port=9000)
