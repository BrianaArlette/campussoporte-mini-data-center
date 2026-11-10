'use strict';
const el = (id) => document.getElementById(id);
const estado = {incidencias: [], editando: null, ejecutando: false};
const etiquetasEstado = {Pendiente:'pending','En proceso':'doing',Resuelto:'done'};
const etiquetasPrio = {Alta:'high',Media:'medium',Baja:'low'};
const nodos = ['web1','web2','web3'];
const toast = (msg, error=false) => {const n=el('toast');n.textContent=msg;n.className=`show ${error?'error':''}`;clearTimeout(toast.timer);toast.timer=setTimeout(()=>n.className='',4100);};
function tdText(cell, value) {cell.textContent=value ?? '';}
async function api(ruta, options={}) {
  const res=await fetch(ruta,{cache:'no-store', ...options,headers:{...(options.body?{'Content-Type':'application/json'}:{}),...options.headers}});
  let datos={};try{datos=await res.json();}catch{}
  if(!res.ok)throw new Error(datos.error||`Error HTTP ${res.status}`);
  return datos;
}
function btnAction(text, title, callback, extra='') {
  const b=document.createElement('button');b.className='action-btn '+extra;b.textContent=text;b.title=title;b.type='button';b.addEventListener('click',callback);return b;
}
function celda(tr, text='', extra='') {const d=document.createElement('td');d.className=extra;tdText(d,text);tr.appendChild(d);return d;}
function badge(cell,text,clase){const s=document.createElement('span');s.className=`pill ${clase}`;s.textContent=text;cell.appendChild(s);}
function dibujarIncidencias(filas) {
  const body=el('incidentsBody');body.replaceChildren();
  if(!filas.length){const row=document.createElement('tr');celda(row,'No hay incidencias con estos filtros.','empty').colSpan=5;body.appendChild(row);}
  filas.forEach(item=>{
    const tr=document.createElement('tr');const first=celda(tr);
    const id=document.createElement('span');id.className='ticket-id';id.textContent='#CS-'+String(item.id).padStart(4,'0');
    const title=document.createElement('span');title.className='ticket-title';title.textContent=item.titulo;
    const location=document.createElement('span');location.className='ticket-location';location.textContent=item.ubicacion;
    first.append(id,title,location);
    badge(celda(tr),item.categoria,'');badge(celda(tr),item.prioridad,etiquetasPrio[item.prioridad]||'');
    badge(celda(tr),item.estado,etiquetasEstado[item.estado]||'');
    const actions=celda(tr);actions.append(
      btnAction('Editar','Editar incidencia',()=>abrirForm(item)),
      btnAction('×','Eliminar incidencia',()=>eliminar(item),'delete')
    );body.appendChild(tr);
  });
  el('rowCount').textContent=`${filas.length} incidencias mostradas`;
}
async function cargarIncidencias(){
  try{
    const params=new URLSearchParams();if(el('stateFilter').value)params.set('estado',el('stateFilter').value);
    if(el('categoryFilter').value)params.set('categoria',el('categoryFilter').value);
    const [res,resumen]=await Promise.all([api('/api/incidencias?'+params),api('/api/resumen')]);
    estado.incidencias=res.incidencias;dibujarIncidencias(res.incidencias);
    el('statTotal').textContent=resumen.total;el('statPending').textContent=resumen.estados.Pendiente;
    el('statDoing').textContent=resumen.estados['En proceso'];el('statDone').textContent=resumen.estados.Resuelto;
    el('sideStatus').textContent='API y base de datos conectadas';el('sideDot').classList.remove('off');
  }catch(err){el('incidentsBody').replaceChildren();const r=document.createElement('tr');celda(r,'No se pudo conectar con la API. Verifica Docker Compose.','empty').colSpan=5;el('incidentsBody').append(r);
    el('sideStatus').textContent='API no disponible';el('sideDot').classList.add('off');toast(err.message,true);}
}
function abrirForm(item=null){
  estado.editando=item?.id ?? null;const form=el('reportForm');form.reset();
  el('formTitle').textContent=item?'Editar incidencia':'Nueva incidencia';
  el('submitReport').textContent=item?'Guardar cambios':'Guardar incidencia';
  el('formStatusWrapper').hidden=!item;
  if(item){['titulo','categoria','prioridad','ubicacion','descripcion','estado'].forEach(k=>form.elements[k].value=item[k]);}
  el('reportDialog').showModal();
}
async function guardar(ev){
  ev.preventDefault();const b=el('submitReport');const form=el('reportForm');
  const datos=Object.fromEntries(new FormData(form).entries());
  if(!estado.editando)delete datos.estado;
  b.disabled=true;
  try{
    if(estado.editando){await api(`/api/incidencias/${estado.editando}`,{method:'PATCH',body:JSON.stringify(datos)});toast('Incidencia actualizada correctamente.');}
    else{await api('/api/incidencias',{method:'POST',body:JSON.stringify(datos)});toast('Nueva incidencia registrada en MariaDB.');}
    el('reportDialog').close();await cargarIncidencias();
  }catch(e){toast(e.message,true);}finally{b.disabled=false;}
}
async function eliminar(item){
  if(!confirm(`¿Eliminar la incidencia #CS-${String(item.id).padStart(4,'0')}? Esta acción no se puede deshacer.`))return;
  try{await api(`/api/incidencias/${item.id}`,{method:'DELETE'});toast('Incidencia eliminada.');await cargarIncidencias();}
  catch(e){toast(e.message,true);}
}
async function consultarNodo(registrar=false){
  try{
    const res=await api('/whoami?nonce='+Date.now()+Math.random());
    document.querySelectorAll('[data-node]').forEach(n=>n.classList.toggle('selected',n.dataset.node===res.nodo));
    el('currentNode').textContent=`${res.nodo.toUpperCase()} · ${res.nombre}`;
    if(registrar){await api('/api/visitas',{method:'POST',body:JSON.stringify({nodo:res.nodo})});}
  }catch(e){el('currentNode').textContent='Nodo no disponible';if(registrar)toast(e.message,true);}
}
function pintarCarga(conteos,completadas,total,fallos,tms){
  el('requestFinished').textContent=`${completadas} / ${total}`;
  el('failedRequests').textContent=fallos;
  el('averageMs').textContent=completadas?`${(tms/completadas).toFixed(0)} ms`:'—';
  nodos.forEach((n,i)=>{el(`numWeb${i+1}`).textContent=`${conteos[n]} solicitudes`;el(`barWeb${i+1}`).style.width=`${(conteos[n]/Math.max(1,total))*100}%`;});
}
async function pruebaCarga(){
  if(estado.ejecutando)return;estado.ejecutando=true;
  const btn=el('startLoad');btn.disabled=true;
  const total=Number(el('requestCount').value);const conteos={web1:0,web2:0,web3:0};
  let terminadas=0,fallos=0,acumulado=0;
  pintarCarga(conteos,0,total,0,0);el('labStatus').textContent='Enviando solicitudes...';
  const unTrabajo=async(i)=>{
    const inicio=performance.now();
    try{const res=await api(`/whoami?prueba=${i}&t=${Date.now()}`);if(!nodos.includes(res.nodo))throw new Error('Nodo desconocido');conteos[res.nodo]++;}
    catch{fallos++;}finally{terminadas++;acumulado+=performance.now()-inicio;pintarCarga(conteos,terminadas,total,fallos,acumulado);}
  };
  try{
    // Lotes con 3 solicitudes simultáneas, para no saturar una computadora escolar.
    for(let i=0;i<total;i+=3)await Promise.all(Array.from({length:Math.min(3,total-i)},(_,j)=>unTrabajo(i+j)));
    const data={total,exitos:total-fallos,fallos,t_prom_ms:Number((acumulado/total).toFixed(2)),distribucion:conteos};
    try{await api('/api/pruebas',{method:'POST',body:JSON.stringify(data)});el('labStatus').textContent='Prueba guardada en MariaDB.';}
    catch{el('labStatus').textContent='Prueba terminada, pero no pudo guardarse en MariaDB.';}
    toast(`Prueba finalizada: ${total-fallos} solicitudes exitosas de ${total}.`);
  }finally{estado.ejecutando=false;btn.disabled=false;}
}
function iniciar(){
  el('hoy').textContent=new Intl.DateTimeFormat('es-MX',{dateStyle:'medium'}).format(new Date());
  el('newReport').onclick=()=>abrirForm();el('closeDialog').onclick=el('cancelForm').onclick=()=>el('reportDialog').close();
  el('reportForm').onsubmit=guardar;el('refreshBtn').onclick=cargarIncidencias;
  el('stateFilter').onchange=cargarIncidencias;el('categoryFilter').onchange=cargarIncidencias;
  el('checkNode').onclick=()=>consultarNodo(true);el('startLoad').onclick=pruebaCarga;
  document.querySelectorAll('.nav-link').forEach(a=>a.addEventListener('click',()=>{document.querySelectorAll('.nav-link').forEach(n=>n.classList.remove('active'));a.classList.add('active');}));
  cargarIncidencias();consultarNodo(true);
}
document.addEventListener('DOMContentLoaded',iniciar);
