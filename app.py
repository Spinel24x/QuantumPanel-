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
    
    # VLESS
    vless = f"vless://{i['uuid']}@{dest}:{port}?encryption=none&security={security}"
    if security == "tls": vless += f"&sni={sni}&fp=chrome"
    vless += f"&type=ws&host={h}&path={paths.get('vless','/vless')}#Quantum"
    
    # VMess
    vmess_config = {
        "v":"2","ps":"Quantum","add":dest,"port":port,"id":i["uuid_vmess"],"aid":0,
        "net":"ws","type":"none","host":h,"path":paths.get("vmess","/vmess"),
        "tls":security,"sni":sni if security=="tls" else "","fp":"chrome" if security=="tls" else ""
    }
    vmess = "vmess://" + base64.b64encode(json.dumps(vmess_config).encode()).decode()
    
    # Trojan
    trojan = f"trojan://{i['trojan_pass']}@{dest}:{port}?security={security}"
    if security == "tls": trojan += f"&sni={sni}"
    trojan += f"&type=ws&host={h}&path={paths.get('trojan','/trojan')}#Quantum"
    
    # Shadowsocks
    ss_b64 = base64.b64encode(f"aes-256-gcm:{i['ss_pass']}".encode()).decode()
    ss = f"ss://{ss_b64}@{dest}:{port}?path={paths.get('ss','/ss')}&host={h}#Quantum"
    
    # SSH
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
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Quantum</title>
<style>
body{background:#000;color:#fff;font-family:'Courier New',monospace;padding:20px;margin:0}
h1{text-align:center;font-size:2.5em;background:linear-gradient(135deg,#60c,#0cf);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:20px 0}
.modes{text-align:center;margin:15px 0}
.modes button{padding:10px 20px;margin:5px;background:#222;color:#fff;border:1px solid #444;border-radius:20px;cursor:pointer;font-family:'Courier New',monospace}
.modes button.active{background:#60c;border-color:#60c}
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
</style></head>
<body>
<h1>QUANTUM</h1>
<div class="modes">
<button id="modeDirect" class="active">Direct</button>
<button id="modeTLS">TLS</button>
<button id="modeCDN">CDN</button>
</div>
<div class="inputs">
<input id="addr" placeholder="Address (auto)" style="width:250px">
<input id="sni" value="www.speedtest.net" placeholder="SNI" style="width:200px">
</div>
<button id="genBtn">GENERATE</button>
<div class="tab-row" id="tabRow"></div>
<div id="configs"></div>
<script>
window.onload = function() {
  var mode='direct',data={};
  
  document.getElementById('modeDirect').onclick = function(){ mode='direct'; setActive(this); };
  document.getElementById('modeTLS').onclick = function(){ mode='tls'; setActive(this); };
  document.getElementById('modeCDN').onclick = function(){ mode='cdn'; setActive(this); };
  
  function setActive(el) {
    var btns = document.querySelectorAll('.modes button');
    for (var i=0; i<btns.length; i++) btns[i].classList.remove('active');
    el.classList.add('active');
  }
  
  document.getElementById('genBtn').onclick = function() {
    var a = document.getElementById('addr').value;
    var s = document.getElementById('sni').value;
    var url = '/api/configs?address=' + encodeURIComponent(a) + '&sni=' + encodeURIComponent(s) + '&mode=' + mode;
    
    fetch(url)
      .then(function(r){ return r.json(); })
      .then(function(d){
        data = d;
        showConfigs();
      })
      .catch(function(e){ console.log(e); });
  };
  
  function showConfigs() {
    var tabRow = document.getElementById('tabRow');
    var configs = document.getElementById('configs');
    tabRow.innerHTML = '';
    configs.innerHTML = '';
    var first = true;
    
    for (var k in data) {
      if (k === 'settings') continue;
      var v = data[k];
      
      var tb = document.createElement('div');
      tb.className = 'tab-btn' + (first ? ' active' : '');
      tb.textContent = v.name;
      tb.setAttribute('data-key', k);
      tb.onclick = function() {
        var key = this.getAttribute('data-key');
        var allTabs = document.querySelectorAll('.tab-btn');
        var allContents = document.querySelectorAll('.tab-content');
        for (var i=0; i<allTabs.length; i++) allTabs[i].classList.remove('active');
        for (var i=0; i<allContents.length; i++) allContents[i].classList.remove('active');
        this.classList.add('active');
        document.getElementById('content-' + key).classList.add('active');
      };
      tabRow.appendChild(tb);
      
      var tc = document.createElement('div');
      tc.className = 'tab-content' + (first ? ' active' : '');
      tc.id = 'content-' + k;
      var txt = v.link || v.command || '';
      tc.innerHTML = '<h3>' + v.icon + ' ' + v.name + '</h3><div class="config-link"><button class="copy-btn" onclick="var t=this.parentElement.textContent.replace(\'COPY\',\'\').trim();navigator.clipboard.writeText(t);this.textContent=\'COPIED\';this.style.background=\'#0f0\';var s=this;setTimeout(function(){s.textContent=\'COPY\';s.style.background=\'#60c\'},2000)">COPY</button>' + txt + '</div>';
      configs.appendChild(tc);
      first = false;
    }
  }
  
  document.getElementById('genBtn').click();
};
</script></body></html>""")

if __name__=="__main__":
    uvicorn.run(app,host="0.0.0.0",port=9000)
