/* OAF-Lambayeque UX28 · Vías de acceso y servicios para respuesta ante emergencias.
 * Fuentes oficiales IDEP/IGN: MTC/MapServer (8,9,10);
 * infraestructura social/FeatureServer (0 comisarías,2 salud,3 bomberos).
 * Defensa Civil: directorio de sedes oficiales sin coordenadas exactas verificadas.
 * No hay información SENASA. Ni rutas, ni horarios de emergencia operativos.
 */
(function(){"use strict";
const BASE="https://www.idep.gob.pe/geoportal/rest/services/INSTITUCIONALES/";
const MTC=BASE+"MTC/MapServer";
const SOCIAL=BASE+"INFRAESTRUCTURA_SOCIAL/FeatureServer";
const SOURCE="https://www.gob.pe/";
const categories={
 hospital:{name:"Hospitales",color:"#c24b49",group:"salud"},
 posta:{name:"Centros y puestos de salud",color:"#3e9f77",group:"salud"},
 policia:{name:"Comisarías",color:"#315f9c",group:"policia"},
 bomberos:{name:"Compañías de bomberos",color:"#ef9236",group:"bomberos"}
};
const state={
 road:{national:true,regional:true,vecinal:true},
 emergency:{hospital:true,posta:true,policia:true,bomberos:true,defensa:true},
 points:{hospital:[],posta:[],policia:[],bomberos:[]},
 fetched:{salud:false,policia:false,bomberos:false},
 loaded:{salud:false,policia:false,bomberos:false},
 partial:{salud:false,policia:false,bomberos:false},
 scene:null,selection:[],contains:null,roadsStatus:"en espera"
};
const $=id=>document.getElementById(id);
const el=(tag,klass)=>{const e=document.createElement(tag);if(klass)e.className=klass;return e};
function build(){
 const root=$("oaf-territorio-riesgos"),grid=root?.querySelector(".oaf-ux24-grid");
 if(!root||$("oaf-ux28-panel"))return;
 const panel=el("section","oaf-ux28-panel");panel.id="oaf-ux28-panel";
 panel.innerHTML=
 '<header class="oaf-ux28-head"><span class="oaf-ux24-tag">UX28 · Infraestructura y preparación territorial</span>'+
 '<h2>Vías de acceso y respuesta ante emergencias</h2>'+
 '<p>Consulta la red vial publicada por el MTC y la ubicación geográfica de establecimientos de salud, comisarías y compañías de bomberos publicada por IGN/IDEP. Los registros son de referencia cartográfica: <strong>no confirman transitabilidad, atención de urgencia, dotación, horarios ni disponibilidad en tiempo real</strong>.</p></header>'+
 '<div class="oaf-ux28-controls"><fieldset><legend>Red vial y caminos de Lambayeque · MTC</legend>'+
 '<label><input type="checkbox" data-ux28-road="national" checked><span class="oaf-ux28-line oaf-ux28-national"></span>Carreteras nacionales</label>'+
 '<label><input type="checkbox" data-ux28-road="regional" checked><span class="oaf-ux28-line oaf-ux28-regional"></span>Carreteras departamentales</label>'+
 '<label><input type="checkbox" data-ux28-road="vecinal" checked><span class="oaf-ux28-line oaf-ux28-vecinal"></span>Caminos vecinales y rurales</label></fieldset>'+
 '<fieldset><legend>Establecimientos y respuesta ante emergencias · IGN/IDEP</legend>'+
 '<label><input type="checkbox" data-ux28-emergency="hospital" checked><i class="oaf-ux28-dot" style="background:#c24b49"></i>Hospitales</label>'+
 '<label><input type="checkbox" data-ux28-emergency="posta" checked><i class="oaf-ux28-dot" style="background:#3e9f77"></i>Centros y puestos de salud</label>'+
 '<label><input type="checkbox" data-ux28-emergency="policia" checked><i class="oaf-ux28-dot" style="background:#315f9c"></i>Comisarías de Policía</label>'+
 '<label><input type="checkbox" data-ux28-emergency="bomberos" checked><i class="oaf-ux28-dot" style="background:#ef9236"></i>Compañías de bomberos</label>'+
 '<label><input type="checkbox" data-ux28-emergency="defensa" checked><i class="oaf-ux28-dot" style="background:#7763a3"></i>Oficinas de Defensa Civil (directorio)</label></fieldset></div>'+
 '<div class="oaf-ux28-status" id="oaf-ux28-status" role="status">Preparando las capas cartográficas del IGN/IDEP…</div>'+
 '<div class="oaf-ux28-metrics" id="oaf-ux28-metrics" aria-live="polite">Los recuentos corresponden a los registros cargados que quedan dentro del ámbito seleccionado.</div>'+
 '<div id="oaf-ux28-details" class="oaf-ux28-details"><strong>Consulta de ubicaciones</strong><p>Selecciona un símbolo de hospital, centro de salud, comisaría o bomberos en el mapa para consultar el nombre, la categoría y la fuente registrada.</p></div>'+
 '<div id="oaf-ux28-defensa" class="oaf-ux28-defensa"><h3>Oficinas de Defensa Civil y gestión de emergencias</h3>'+
 '<p>La dirección institucional es comprobable, pero no existe en las fuentes consultadas una geocapa completa de oficinas con coordenadas verificadas. Se muestran como directorio, sin marcadores aproximados en el mapa.</p>'+
 '<div class="oaf-ux28-offices"><article><strong>INDECI · Dirección Desconcentrada Lambayeque</strong><span>Calle Los Zapotes N.° 173, Urb. Santa Victoria, Chiclayo</span><a href="https://www.gob.pe/institucion/indeci/sedes?sheet=3" target="_blank" rel="noopener noreferrer">Ver sede oficial de INDECI ↗</a></article>'+
 '<article><strong>Municipalidad Provincial de Chiclayo · Defensa Civil</strong><span>Av. Grau N.° 152, Biblioteca Municipal, Chiclayo</span><a href="https://www.gob.pe/institucion/munichiclayo/sedes" target="_blank" rel="noopener noreferrer">Ver sede oficial municipal ↗</a></article></div>'+
 '<p>Para otras oficinas provinciales y distritales, consulta los directorios de las municipalidades correspondientes antes de acudir. Los horarios pueden variar.</p></div>'+
 '<p class="oaf-ux28-sources">Capas oficiales: <a href="'+MTC+'" target="_blank" rel="noopener noreferrer">MTC · red vial</a> · '+
 '<a href="'+SOCIAL+'" target="_blank" rel="noopener noreferrer">IGN/IDEP · infraestructura social</a> · '+
 '<a href="https://github.com/ccoronelepg-gif/OAF-Lambayeque/blob/main/METODOLOGIA_INFRAESTRUCTURA_EMERGENCIAS_UX28.md" target="_blank" rel="noopener noreferrer">Metodología y limitaciones UX28 ↗</a>.</p>';
 if(grid)grid.before(panel);else root.append(panel);
 for(const input of panel.querySelectorAll("[data-ux28-road]"))input.addEventListener("change",()=>{
  state.road[input.dataset.ux28Road]=input.checked;render();
 });
 for(const input of panel.querySelectorAll("[data-ux28-emergency]"))input.addEventListener("change",()=>{
  const k=input.dataset.ux28Emergency;state.emergency[k]=input.checked;
  if(k==="defensa")$("oaf-ux28-defensa").hidden=!input.checked;
  render();
 });
}
function showStatus(){
 const status=$("oaf-ux28-status");if(!status)return;
 const labels={
  salud:"Establecimientos de salud",policia:"Comisarías",bomberos:"Bomberos"
 };
 status.textContent="Red vial MTC: "+state.roadsStatus+". "+Object.keys(labels).map(key=>{
  const st=state.loaded[key];const count=key==="salud"?state.points.hospital.length+state.points.posta.length:state.points[key].length;
  return labels[key]+": "+(st==="error"?"servicio no disponible":st===true?
   count+" registros cargados"+(state.partial[key]?" (consulta parcial)":""):"cargando");
 }).join(" · ")+".";
}
function qualify(feature,key){
 const p=feature.properties||{};
 const dept=String(p.DEPARTAMENTO||p.DEPARTAMEN||p.dpto||p.DPTO||"").toLocaleUpperCase("es");
 if(dept&&!dept.includes("LAMBAYEQUE"))return null;
 const pt=feature.geometry?.coordinates;
 if(feature.geometry?.type!=="Point"||!Array.isArray(pt)||pt.length<2||
  !Number.isFinite(pt[0])||!Number.isFinite(pt[1]))return null;
 return feature;
}
function subtype(feature){
 const p=feature.properties||{};
 const cat=String(p.CATEGORIA||"").trim().toUpperCase();
 const descr=String(p.NOMBRE||p.TIPO||p.CLASIFICACION||"").toLocaleLowerCase("es");
 // Categoría MINSA/EsSalud: II y III son hospitales; niveles I se agrupan como primer nivel.
 if(/^(II|III|IV)(?:\b|-)/.test(cat)||/hospital/.test(descr))return "hospital";
 return "posta";
}
async function loadGroup(key,id){
 if(state.fetched[key]||!state.scene)return;
 state.fetched[key]=true;
 const b=state.scene.bounds,paramsBase={
  where:"1=1",geometry:[b.minLon,b.minLat,b.maxLon,b.maxLat].join(","),
  geometryType:"esriGeometryEnvelope",inSR:"4326",
  spatialRel:"esriSpatialRelIntersects",
  returnGeometry:"true",outSR:"4326",outFields:"*",
  resultRecordCount:"500",f:"geojson"
 };
 let records=[],error=null,limit=6;
 for(let page=0;page<limit;page++){
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),16000);
  try{
   const url=SOCIAL+"/"+id+"/query?"+new URLSearchParams({...paramsBase,resultOffset:String(page*500)});
   const res=await fetch(url,{cache:"no-store",signal:controller.signal});
   if(!res.ok)throw Error("HTTP "+res.status);
   const body=await res.json();
   if(body.error||!Array.isArray(body.features))throw Error("respuesta incompatible");
   const valid=body.features.map(f=>qualify(f,key)).filter(Boolean);
   records.push(...valid);
   if(body.features.length<500){break}
   if(page===limit-1)state.partial[key]=true;
  }catch(ex){
   error=ex;state.partial[key]=Boolean(records.length);break;
  }finally{clearTimeout(timer)}
 }
 if(error&&!records.length){state.loaded[key]="error"}
 else{
  const dedupe=new Set();
  records=records.filter(f=>{
   const p=f.properties||{};
   const id=p.OBJECTID??p.objectid??p.OBJECTID_1??[f.geometry.coordinates,p.NOMBRE||p.nombre||""].join("-");
   if(dedupe.has(id))return false;
   dedupe.add(id);return true;
  });
  if(key==="salud"){state.points.hospital=records.filter(f=>subtype(f)==="hospital");
   state.points.posta=records.filter(f=>subtype(f)==="posta")}
  else state.points[key]=records;
  state.loaded[key]=true;
 }
 showStatus();render();
}
function selectionContains(pt){
 return state.selection.every(s=>typeof state.contains!=="function"||state.contains(s.geo,pt));
}
function emergencyDetail(feature,key){
 const p=feature.properties||{},def=categories[key],output=$("oaf-ux28-details");
 if(!output)return;
 output.replaceChildren();
 const title=el("strong");title.textContent=String(p.NOMBRE||p.nombre||"Establecimiento sin nombre publicado");
 const badge=el("span","oaf-ux28-recordkind");badge.textContent=def.name+" · IGN/IDEP";
 const address=el("p");address.textContent="Ubicación: "+String(p.DIRECCION||p.direccion||"Solo coordenadas del geoservicio")+
  ". "+String(p.DISTRITO||p.dist||"")+" · "+String(p.PROVINCIA||p.prov||"");
 const detail=el("p");
 const extra=[p.CATEGORIA,p.TIPO,p.INSTITUCIO,p.estado,p.ESTADO].filter(v=>typeof v==="string"&&v.trim());
 detail.textContent=extra.length?"Categoría/estado publicado: "+extra.slice(0,3).join(" · ")+".":"La fuente no detalla capacidad ni servicio actual.";
 const source=el("a");source.href=SOCIAL+"/"+(def.group==="salud"?2:def.group==="policia"?0:3);
 source.target="_blank";source.rel="noopener noreferrer";source.textContent="Ver capa geográfica original ↗";
 output.append(title,badge,address,detail,source);
}
function createSVG(name,attrs){
 const x=document.createElementNS("http://www.w3.org/2000/svg",name);
 Object.entries(attrs).forEach(([k,v])=>x.setAttribute(k,String(v)));return x;
}
function render(){
 const sc=state.scene;
 if(!sc||!$("oaf-ux28-panel"))return;
 const svg=sc.svg;
 svg.querySelectorAll(".oaf-ux28-overlay").forEach(n=>n.remove());
 const layers=[];
 if(state.road.vecinal)layers.push(8);
 if(state.road.regional)layers.push(9);
 if(state.road.national)layers.push(10);
 if(layers.length){
  const b=sc.bounds;
  const url=MTC+"/export?"+new URLSearchParams({
    bbox:[b.minLon,b.minLat,b.maxLon,b.maxLat].join(","),
    bboxSR:"4326",imageSR:"4326",size:"900,438",
    transparent:"true",format:"png32",dpi:"110",layers:"show:"+layers.join(","),f:"image"
  });
  state.roadsStatus="solicitando "+layers.length+" capas";
  const road=createSVG("image",{
   href:url,x:0,y:0,width:700,height:340,opacity:".91","preserveAspectRatio":"none",
   "pointer-events":"none"
  });
  road.classList.add("oaf-ux28-overlay","oaf-ux28-roadimage");
  road.addEventListener("load",()=>{if(road.isConnected){state.roadsStatus="capas del MTC recibidas";showStatus()}});
  road.addEventListener("error",()=>{if(road.isConnected){state.roadsStatus="capa no disponible; consulta servicio MTC";showStatus()}});
  const before=svg.querySelector("circle.oaf-ux25-point");
  svg.insertBefore(road,before||null);
 }else state.roadsStatus="desactivada";
 let visible={hospital:0,posta:0,policia:0,bomberos:0};
 for(const key of Object.keys(categories)){
  if(!state.emergency[key])continue;
  for(const f of state.points[key]){
   const pt=f.geometry.coordinates;
   if(!selectionContains(pt))continue;
   const x=sc.x(pt[0]),y=sc.y(pt[1]);
   if(!Number.isFinite(x)||!Number.isFinite(y)||x<0||x>700||y<0||y>340)continue;
   visible[key]++;
   const marker=createSVG("circle",{
    cx:x.toFixed(2),cy:y.toFixed(2),r:key==="hospital"?5.5:4.1,
    fill:categories[key].color,stroke:"#fff","stroke-width":1.1,tabindex:"0",
    role:"button","aria-label":categories[key].name+": "+String(f.properties?.NOMBRE||f.properties?.nombre||"registro")+"; consultar ficha"
   });
   marker.classList.add("oaf-ux28-overlay","oaf-ux28-emergency-marker");
   const open=()=>emergencyDetail(f,key);
   marker.addEventListener("click",open);
   marker.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();open()}});
   svg.append(marker);
  }
 }
 const kpi=$("oaf-ux28-metrics");
 if(kpi){
  const selected=state.selection.length?state.selection.map(x=>x.name).join(" ∩ "):"Todo el ámbito del visor";
  const l=document.createElement("strong");l.textContent="Selección: "+selected;
  const p=el("p");p.textContent=Object.keys(categories).map(key=>
   categories[key].name+": "+(state.loaded[categories[key].group]===true?visible[key]+" ubicaciones cargadas":
   state.loaded[categories[key].group]==="error"?"no disponible":"en consulta")).join(" · ");
  const note=el("small");note.textContent="Puntos filtrados de las consultas recibidas; no acreditan capacidad de atención ni rutas transitables.";
  kpi.replaceChildren(l,p,note);
 }
 showStatus();
}
function init(){
 build();
 // Se invoca al final del redibujado del mapa principal; evita reconstruir su proyección.
 window.oafUx28AfterDraw=function(context){
  if(!context||!context.scene)return;
  const first=!state.scene;
  state.scene=context.scene;state.selection=context.selected||[];
  state.contains=context.contains;render();
  if(first){
   loadGroup("salud",2);loadGroup("policia",0);loadGroup("bomberos",3);
  }
 };
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();