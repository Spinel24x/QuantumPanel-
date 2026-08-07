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

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return HTMLResponse("""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Quantum Pro</title>
<style>
body{background:#000;color:#fff;font-family:'Courier New',monospace;padding:20px;margin:0}
h1{text-align:center;font-size:2.5em;background:linear-gradient(135deg,#60c,#0cf);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:20px 0}
.cf-row{text-align:center;margin:15px 0}
.cf-row label{color:#aaa;cursor:pointer}
.inputs{text-align:center;margin:15px 0}
.inputs input{padding:10px;margin:5px;background:#111;border:1px solid #333;border-radius:15px;color:#0cf;text-align:center;font-family:'Courier New',monospace}
#genBtn{display:block;width:100%;max-width:400px;margin:15px auto;padding:14px;background:#60c;color:#fff;border:none;border-radius:25px;font-size:1em;cursor:pointer;font-family:'Courier New',monospace;letter-spacing:3px}
#genBtn:hover{background:#90f}
.tab-row{display:flex;flex-wrap:wrap;gap:5px;justify-content:center;margin:15px 0}
.tab-btn{padding:10px 15px;background:#111;border:1px solid #333;border-radius:20px;color:#aaa;cursor:pointer;font-size:0.8em;font-family:'Courier New',monospace}
.tab-btn.active{background:#60c;color:#fff;border-color:#60c}
.tab-content{display:none;background:#111;border:1px solid #333;border-radius:15px;padding:20px;margin:10px 0}
.tab-content.active{display:block}
.config-link{color:#0f0;font-size:0.75em;word-break:break-all;line-height:1.8;position:relative}
.copy-btn{position:absolute;top:5px;right:5px;background:#60c;color:#fff;border:none;padding:5px 12px;border-radius:10px;cursor:pointer;font-size:0.7em}
.copy-btn:hover{background:#90f}
.info{text-align:center;color:#666;margin:10px 0;font-size:0.7em}
</style></head>
<body>
<h1>QUANTUM PRO</h1>
<div class="cf-row">
<label><input type="checkbox" id="cfCheck" onchange="toggleCF()"> Cloudflare / IP Tamiz</label>
</div>
<div class="inputs">
<input id="addr" placeholder="IP Tamiz (optional)" style="width:250px">
<input id="sni" placeholder="SNI (auto)" style="width:200px">
</div>
<button id="genBtn" onclick="generate()">GENERATE</button>
<div class="info" id="infoBar"></div>
<div class="tab-row" id="tabRow"></div>
<div id="configs"></div>
<script>
var data={};
function toggleCF(){
  var cf=document.getElementById('cfCheck').checked;
  document.getElementById('addr').style.display=cf?'inline-block':'none';
}
function generate(){
  var a=document.getElementById('addr').value;
  var s=document.getElementById('sni').value;
  var cf=document.getElementById('cfCheck').checked?'1':'0';
  fetch('/api/configs?address='+encodeURIComponent(a)+'&sni='+encodeURIComponent(s)+'&cf='+cf)
    .then(function(r){return r.json()})
    .then(function(d){data=d;show();})
    .catch(function(e){document.getElementById('infoBar').textContent='Error: '+e;});
}
function show(){
  var tabRow=document.getElementById('tabRow'),configs=document.getElementById('configs'),infoBar=document.getElementById('infoBar');
  tabRow.innerHTML='';configs.innerHTML='';
  if(data.connection){var c=data.connection;infoBar.textContent=c.address+':'+c.port+' | '+c.security.toUpperCase()+' | Host:'+c.host;}
  var first=true;
  for(var k in data){
    if(k==='settings'||k==='connection')continue;
    var v=data[k];
    var tb=document.createElement('div');tb.className='tab-btn'+(first?' active':'');tb.textContent=v.name;tb.setAttribute('data-key',k);
    tb.onclick=function(){var key=this.getAttribute('data-key');document.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active')});document.querySelectorAll('.tab-content').forEach(function(x){x.classList.remove('active')});this.classList.add('active');document.getElementById('content-'+key).classList.add('active')};
    tabRow.appendChild(tb);
    var tc=document.createElement('div');tc.className='tab-content'+(first?' active':'');tc.id='content-'+k;
    var txt=v.link||'';
    tc.innerHTML='<h3>'+v.icon+' '+v.name+'</h3><div class="config-link"><button class="copy-btn" onclick="copyText(this)">COPY</button>'+txt+'</div>';
    configs.appendChild(tc);first=false;
  }
}
function copyText(btn){var txt=btn.parentElement.textContent.replace('COPY','').trim();navigator.clipboard.writeText(txt);btn.textContent='OK';btn.style.background='#0f0';var s=btn;setTimeout(function(){s.textContent='COPY';s.style.background='#60c'},2000)}
setTimeout(generate,300);
</script></body></html>""")

if __name__=="__main__":
    uvicorn.run(app,host="0.0.0.0",port=9000)
