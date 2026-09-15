const $ = (s) => document.querySelector(s);
const state = { apps: [], current: null, config: null };

function toast(message, ms=3200){ const el=$('#toast'); el.textContent=message; el.classList.remove('hidden'); setTimeout(()=>el.classList.add('hidden'),ms); }
async function api(path, options={}){
  const res = await fetch(path,{headers:{'Content-Type':'application/json',...(options.headers||{})},...options});
  if(!res.ok){ let msg=`Error ${res.status}`; try{const j=await res.json();msg=j.detail||msg}catch{} throw new Error(msg); }
  if(res.status===204) return null; return res.json();
}
function money(n){ return Number(n||0).toLocaleString(undefined,{style:'currency',currency:'USD',minimumFractionDigits:4,maximumFractionDigits:6}); }

async function loadConfig(){
  state.config=await api('/api/config');
  const status=$('#apiStatus');
  status.textContent=state.config.api_key_configured?'● Cerebras configurado':'● Falta CEREBRAS_API_KEY';
  status.className='status '+(state.config.api_key_configured?'ok':'warn');
  const sel=$('#model');
  sel.innerHTML='';
  for(const m of state.config.models){ const o=document.createElement('option');o.value=m;o.textContent=m==='auto'?'Automático (Qwen por defecto)':m;sel.appendChild(o); }
}

async function loadApps(selectId=null){
  state.apps=await api('/api/apps'); renderApps();
  if(selectId){ const found=state.apps.find(a=>a.id===selectId); if(found) await openApp(found.id); }
}
function renderApps(){
  const box=$('#appList'); box.innerHTML='';
  for(const app of state.apps){
    const b=document.createElement('button'); b.className='app-item'+(state.current?.id===app.id?' active':''); b.dataset.id=app.id;
    b.innerHTML=`<span>${app.is_example?'🧩':'⚡'}</span><span title="${escapeHtml(app.title)}">${escapeHtml(app.title)}</span>`;
    b.onclick=()=>openApp(app.id); box.appendChild(b);
  }
}
function escapeHtml(s){ return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }

async function openApp(id){
  state.current=await api(`/api/apps/${id}`); renderApps();
  $('#workspaceTitle').textContent=state.current.title;
  $('#workspaceSub').textContent=state.current.is_example?'Ejemplo local — no consumió tokens':'App guardada localmente';
  ['#duplicateBtn','#renameBtn','#deleteBtn'].forEach(s=>$(s).classList.remove('hidden'));
  $('#creator').classList.add('hidden'); $('#previewCard').classList.remove('hidden');
  $('#previewTitle').textContent=state.current.title;
  const select=$('#versionSelect'); select.innerHTML='';
  for(const v of state.current.versions){ const o=document.createElement('option');o.value=v.id;o.textContent=`v${v.version_number} · ${v.model}`; if(v.id===state.current.current_version_id)o.selected=true;select.appendChild(o); }
  showVersion(select.value);
}
function showVersion(versionId){
  const v=state.current?.versions?.find(x=>x.id===versionId); if(!v)return;
  $('#appFrame').src=`/api/versions/${encodeURIComponent(versionId)}/html?ts=${Date.now()}`;
  $('#versionMeta').textContent=`v${v.version_number} · ${v.input_tokens}+${v.output_tokens} tokens · ${money(v.estimated_cost_usd)}`;
}
function newApp(){
  state.current=null; renderApps(); $('#workspaceTitle').textContent='Crear una nueva app'; $('#workspaceSub').textContent='Describe una herramienta específica. La IA generará un HTML autocontenido.';
  ['#duplicateBtn','#renameBtn','#deleteBtn','#previewCard'].forEach(s=>$(s).classList.add('hidden')); $('#creator').classList.remove('hidden');
  $('#prompt').value=''; $('#title').value=''; $('#generationInfo').textContent=''; $('#prompt').focus();
}
async function generate(existingId=null){
  const prompt=$('#prompt').value.trim(); if(prompt.length<5){toast('Describe un poco más la app que necesitas.');return;}
  const btn=$('#generateBtn'); btn.disabled=true; btn.textContent='Generando…'; $('#generationInfo').textContent='Solicitando código a Cerebras y validando el HTML…';
  try{
    const data=await api('/api/apps/generate',{method:'POST',body:JSON.stringify({prompt,title:$('#title').value.trim()||null,model:$('#model').value,app_id:existingId})});
    $('#generationInfo').textContent=`Lista: ${data.current_version.output_tokens} tokens de salida · costo estimado ${money(data.current_version.estimated_cost_usd)}`;
    await loadApps(data.id); toast(existingId?'Nueva versión creada.':'App creada y guardada.');
  }catch(e){ $('#generationInfo').textContent=e.message; toast(e.message,6000); }
  finally{ btn.disabled=false; btn.textContent='Generar app'; }
}

$('#newBtn').onclick=newApp;
$('#generateBtn').onclick=()=>generate(null);
$('#versionSelect').onchange=e=>showVersion(e.target.value);
$('#reloadBtn').onclick=()=>showVersion($('#versionSelect').value);
$('#editBtn').onclick=()=>{ const cur=state.current; $('#creator').classList.remove('hidden'); $('#prompt').value='Mejora esta aplicación. Conserva su propósito, pero aplica estos cambios:\n'; $('#title').value=cur.title; $('#generateBtn').onclick=()=>generate(cur.id); $('#prompt').focus(); window.scrollTo({top:0,behavior:'smooth'}); };
$('#duplicateBtn').onclick=async()=>{ if(!state.current)return; const d=await api(`/api/apps/${state.current.id}/duplicate`,{method:'POST'}); await loadApps(d.id); toast('App duplicada.'); };
$('#renameBtn').onclick=async()=>{ if(!state.current)return; const name=prompt('Nuevo nombre:',state.current.title); if(!name?.trim())return; await api(`/api/apps/${state.current.id}`,{method:'PATCH',body:JSON.stringify({title:name.trim()})}); await loadApps(state.current.id); toast('Nombre actualizado.'); };
$('#deleteBtn').onclick=async()=>{ if(!state.current)return; if(!confirm(`¿Eliminar "${state.current.title}" y todas sus versiones?`))return; await api(`/api/apps/${state.current.id}`,{method:'DELETE'}); state.current=null; await loadApps(); newApp(); toast('App eliminada.'); };

(async()=>{ try{await loadConfig();await loadApps();newApp();}catch(e){toast(e.message,6000);} })();
