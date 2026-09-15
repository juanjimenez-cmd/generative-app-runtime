from __future__ import annotations

import uuid

from .config import GENERATED_DIR
from .db import db, utcnow
from .security import extract_html

EXAMPLES = [
    (
        "Calculadora",
        "Ejemplo local preinstalado: calculadora básica.",
        """<!doctype html><html><head><meta charset='utf-8'><title>Calculadora</title><style>
        *{box-sizing:border-box}body{margin:0;font-family:system-ui;background:#eef2ff;display:grid;place-items:center;min-height:100vh}.c{width:min(360px,92vw);background:white;padding:18px;border-radius:22px;box-shadow:0 18px 50px #0002}.d{background:#111827;color:#fff;border-radius:14px;padding:18px;text-align:right;font-size:30px;min-height:72px;overflow:auto}.g{display:grid;grid-template-columns:repeat(4,1fr);gap:9px;margin-top:12px}button{border:0;border-radius:12px;padding:17px;font-size:18px;background:#e5e7eb;cursor:pointer}button.op{background:#c7d2fe}button.eq{background:#4f46e5;color:white}.w{grid-column:span 2}</style></head><body><div class='c'><div id='d' class='d'>0</div><div class='g'><button class='w' onclick='clr()'>C</button><button onclick='put("/")' class='op'>÷</button><button onclick='put("*")' class='op'>×</button><button onclick='put("7")'>7</button><button onclick='put("8")'>8</button><button onclick='put("9")'>9</button><button onclick='put("-")' class='op'>−</button><button onclick='put("4")'>4</button><button onclick='put("5")'>5</button><button onclick='put("6")'>6</button><button onclick='put("+")' class='op'>+</button><button onclick='put("1")'>1</button><button onclick='put("2")'>2</button><button onclick='put("3")'>3</button><button onclick='calc()' class='eq'>=</button><button class='w' onclick='put("0")'>0</button><button onclick='put(".")'>.</button></div></div><script>let s='';const d=document.getElementById('d');function put(x){s+=x;d.textContent=s}function clr(){s='';d.textContent='0'}function calc(){try{if(!/^[0-9+\-*/.() ]+$/.test(s))throw 0;s=String(Function('return ('+s+')')());d.textContent=s}catch(e){d.textContent='Error';s=''}}</script></body></html>""",
    ),
    (
        "Calculadora de caudales",
        "Ejemplo local preinstalado: suma l/s y convierte a m³/s.",
        """<!doctype html><html><head><meta charset='utf-8'><title>Caudales</title><style>*{box-sizing:border-box}body{font-family:system-ui;margin:0;background:#ecfeff;color:#164e63;padding:28px}.card{max-width:720px;margin:auto;background:#fff;padding:28px;border-radius:22px;box-shadow:0 16px 45px #155e7522}textarea{width:100%;min-height:180px;padding:14px;border:1px solid #a5f3fc;border-radius:12px;font:inherit}button{background:#0e7490;color:#fff;border:0;padding:12px 18px;border-radius:10px;font-weight:700;margin-top:10px}.r{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:18px}.k{background:#cffafe;padding:18px;border-radius:14px}.n{font-size:28px;font-weight:800}</style></head><body><div class='card'><h1>💧 Calculadora de caudales</h1><p>Ingresa valores en litros por segundo, uno por línea o separados por coma.</p><textarea id='v' placeholder='8.30\n0.10\n2.50'></textarea><br><button onclick='go()'>Calcular</button><div class='r'><div class='k'>Total l/s<div id='ls' class='n'>0</div></div><div class='k'>Total m³/s<div id='m3' class='n'>0</div></div></div></div><script>function go(){const a=document.getElementById('v').value.split(/[\n,; ]+/).map(Number).filter(Number.isFinite);const t=a.reduce((x,y)=>x+y,0);ls.textContent=t.toLocaleString(undefined,{maximumFractionDigits:4});m3.textContent=(t/1000).toLocaleString(undefined,{maximumFractionDigits:6})}</script></body></html>""",
    ),
    (
        "Visor CSV simple",
        "Ejemplo local preinstalado: abre un CSV local dentro del navegador.",
        """<!doctype html><html><head><meta charset='utf-8'><title>CSV</title><style>*{box-sizing:border-box}body{font-family:system-ui;margin:0;background:#f8fafc;padding:24px;color:#0f172a}.card{background:white;border-radius:18px;padding:22px;box-shadow:0 12px 35px #0001;max-width:1000px;margin:auto}.wrap{overflow:auto;max-height:65vh;margin-top:18px;border:1px solid #e2e8f0;border-radius:12px}table{border-collapse:collapse;width:100%;font-size:13px}th,td{border-bottom:1px solid #e2e8f0;padding:9px;text-align:left;white-space:nowrap}th{position:sticky;top:0;background:#e2e8f0}</style></head><body><div class='card'><h1>📊 Visor CSV</h1><p>El archivo se procesa localmente en tu navegador.</p><input id='f' type='file' accept='.csv,text/csv'><div id='out' class='wrap'></div></div><script>f.onchange=()=>{const file=f.files[0];if(!file)return;const r=new FileReader();r.onload=()=>{const rows=String(r.result).split(/\r?\n/).filter(Boolean).map(x=>x.split(','));if(!rows.length)return;let h='<table><thead><tr>'+rows[0].map(c=>'<th>'+esc(c)+'</th>').join('')+'</tr></thead><tbody>';for(const row of rows.slice(1,501))h+='<tr>'+row.map(c=>'<td>'+esc(c)+'</td>').join('')+'</tr>';out.innerHTML=h+'</tbody></table>'};r.readAsText(file)};function esc(s){return String(s).replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]))}</script></body></html>""",
    ),
]


def seed_examples() -> None:
    with db() as conn:
        count = conn.execute("SELECT COUNT(*) AS n FROM apps").fetchone()["n"]
        if count:
            return

        for title, prompt, raw_html in EXAMPLES:
            app_id = str(uuid.uuid4())
            version_id = str(uuid.uuid4())
            now = utcnow()
            html = extract_html(raw_html)
            folder = GENERATED_DIR / app_id
            folder.mkdir(parents=True, exist_ok=True)
            path = folder / "v1.html"
            path.write_text(html, encoding="utf-8")
            conn.execute(
                "INSERT INTO apps(id,title,created_at,updated_at,current_version_id,is_example) VALUES(?,?,?,?,?,1)",
                (app_id, title, now, now, version_id),
            )
            conn.execute(
                """INSERT INTO versions(id,app_id,version_number,prompt,model,input_tokens,output_tokens,estimated_cost_usd,html_path,created_at)
                   VALUES(?,?,?,?,?,?,?,?,?,?)""",
                (version_id, app_id, 1, prompt, "local-example", 0, 0, 0.0, str(path), now),
            )
