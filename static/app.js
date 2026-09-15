const $ = (s) => document.querySelector(s);
const state = { apps: [], current: null, config: null, editingId: null };

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
  const sel=$('#model'); sel.innerHTML='';
  for(const m of state.config.models){ const o=document.createElement('option');o.value=m;o.textContent=m==='auto'?'Automático (router inteligente)':m;sel.appendChild(o); }
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
  state.current=await api(`/api/apps/${id}`); state.editingId=null; renderApps();
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
  const why=v.routing_reason?` · ${v.routing_reason}`:'';
  $('#versionMeta').textContent=`v${v.version_number} · ${v.input_tokens}+${v.output_tokens} tokens · ${money(v.estimated_cost_usd)}${why}`;
}
function newApp(){
  state.current=null; state.editingId=null; renderApps();
  $('#workspaceTitle').textContent='Crear una nueva app'; $('#workspaceSub').textContent='Describe una herramienta específica. La IA generará un HTML autocontenido.';
  ['#duplicateBtn','#renameBtn','#deleteBtn','#previewCard'].forEach(s=>$(s).classList.add('hidden')); $('#creator').classList.remove('hidden');
  $('#creatorTitle').textContent='¿Qué necesitas crear?'; $('#generateBtn').textContent='Generar app';
  $('#prompt').value=''; $('#title').value=''; $('#generationInfo').textContent=''; $('#prompt').focus();
}
function beginEdit(){
  if(!state.current)return;
  state.editingId=state.current.id;
  $('#creator').classList.remove('hidden');
  $('#creatorTitle').textContent=`Modificar ${state.current.title}`;
  $('#prompt').value='';
  $('#prompt').placeholder='Ej.: Haz los botones más grandes, agrega exportación CSV y conserva el resto igual…';
  $('#title').value=state.current.title;
  $('#generateBtn').textContent='Crear nueva versión';
  $('#generationInfo').textContent='La IA recibirá automáticamente el HTML de la versión actual y tu instrucción de cambio.';
  $('#prompt').focus(); window.scrollTo({top:0,behavior:'smooth'});
}

function parseSSEBuffer(buffer, onEvent){
  const parts=buffer.split('\n\n'); const rest=parts.pop()||'';
  for(const part of parts){
    const line=part.split('\n').find(x=>x.startsWith('data:'));
    if(!line)continue;
    try{onEvent(JSON.parse(line.slice(5).trim()));}catch{}
  }
  return rest;
}

async function generate(){
  const promptText=$('#prompt').value.trim(); if(promptText.length<5){toast('Describe un poco más la app que necesitas.');return;}
  const payload={prompt:promptText,title:$('#title').value.trim()||null,model:$('#model').value,app_id:state.editingId};
  const btn=$('#generateBtn'); btn.disabled=true; const oldText=btn.textContent; btn.textContent='Generando…';
  $('#generationInfo').textContent='Iniciando generación en streaming…';
  let savedApp=null; let streamError=null; let receivedChars=0;
  try{
    const res=await fetch('/api/apps/generate/stream',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
    if(!res.ok) throw new Error(`Streaming no disponible (${res.status})`);
    if(!res.body) throw new Error('El navegador no expuso el stream de respuesta.');
    const reader=res.body.getReader(); const decoder=new TextDecoder(); let buffer='';
    while(true){
      const {value,done}=await reader.read();
      if(done)break;
      buffer+=decoder.decode(value,{stream:true});
      buffer=parseSSEBuffer(buffer,(event)=>{
        if(event.type==='status') $('#generationInfo').textContent=event.message;
        if(event.type==='routing') $('#generationInfo').textContent=`${event.model}: ${event.reason}`;
        if(event.type==='delta') { receivedChars=event.chars||receivedChars+(event.content||'').length; $('#generationInfo').textContent=`Generando con IA… ${receivedChars.toLocaleString()} caracteres recibidos`; }
        if(event.type==='saved') savedApp=event.app;
        if(event.type==='error') streamError=event.message||'Error durante el stream';
      });
    }
    if(streamError) throw new Error(streamError);
    if(!savedApp) throw new Error('La generación terminó sin guardar una app.');
    await loadApps(savedApp.id);
    const v=savedApp.current_version;
    toast(`App lista · ${v.model} · ${money(v.estimated_cost_usd)}`,5000);
  }catch(streamFailure){
    $('#generationInfo').textContent=`Streaming falló (${streamFailure.message}). Intentando modo compatible…`;
    try{
      const data=await api('/api/apps/generate',{method:'POST',body:JSON.stringify(payload)});
      await loadApps(data.id); toast('App creada mediante fallback no-streaming.');
    }catch(fallbackFailure){
      $('#generationInfo').textContent=fallbackFailure.message; toast(fallbackFailure.message,6000);
    }
  }finally{ btn.disabled=false; btn.textContent=oldText; }
}

$('#newBtn').onclick=newApp;
$('#generateBtn').onclick=generate;
$('#versionSelect').onchange=e=>showVersion(e.target.value);
$('#reloadBtn').onclick=()=>showVersion($('#versionSelect').value);
$('#editBtn').onclick=beginEdit;
$('#duplicateBtn').onclick=async()=>{ if(!state.current)return; const d=await api(`/api/apps/${state.current.id}/duplicate`,{method:'POST'}); await loadApps(d.id); toast('App duplicada.'); };
$('#renameBtn').onclick=async()=>{ if(!state.current)return; const name=prompt('Nuevo nombre:',state.current.title); if(!name?.trim())return; await api(`/api/apps/${state.current.id}`,{method:'PATCH',body:JSON.stringify({title:name.trim()})}); await loadApps(state.current.id); toast('Nombre actualizado.'); };
$('#deleteBtn').onclick=async()=>{ if(!state.current)return; if(!confirm(`¿Eliminar "${state.current.title}" y todas sus versiones?`))return; await api(`/api/apps/${state.current.id}`,{method:'DELETE'}); state.current=null; await loadApps(); newApp(); toast('App eliminada.'); };

(async()=>{ try{await loadConfig();await loadApps();newApp();}catch(e){toast(e.message,6000);} })();
