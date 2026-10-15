/* OAF-Lambayeque · Interactividad de la fase 8F-Web · Sin datos sintéticos */
(()=>{'use strict';
const $=s=>document.querySelector(s), pts={Chiclayo:[-6.7714,-79.8409],Jayanca:[-6.39278,-79.8228],Motupe:[-6.15083,-79.7142],Olmos:[-5.98825,-79.74723]};
const vars={
temp:{key:'temperature_2m_max',label:'Temperatura máxima',unit:'°C',type:'line'},
min:{key:'temperature_2m_min',label:'Temperatura mínima',unit:'°C',type:'line'},
hum:{key:'relative_humidity_2m_mean',label:'Humedad relativa media',unit:'%',type:'line'},
prec:{key:'precipitation_sum',label:'Precipitación prevista',unit:'mm',type:'bar'},
rad:{key:'shortwave_radiation_sum',label:'Radiación global diaria',unit:'MJ/m²',type:'bar'},
wind:{key:'wind_speed_10m_max',label:'Viento máximo',unit:'km/h',type:'line'},
vpd:{key:'vapour_pressure_deficit_max',label:'DPV máximo',unit:'kPa',type:'line'},
et0:{key:'et0_fao_evapotranspiration',label:'ET₀ FAO',unit:'mm',type:'bar'}
};
const fmt=(n,d=1)=>Number.isFinite(n)?n.toLocaleString('es-PE',{maximumFractionDigits:d}):'—';
let cache=new Map(),state={place:'Chiclayo',var:'temp'};
const api=(place)=>{const [lat,lon]=pts[place];return 'https://api.open-meteo.com/v1/forecast?'+new URLSearchParams({latitude:String(lat),longitude:String(lon),current:'temperature_2m,relative_humidity_2m,precipitation,shortwave_radiation',daily:Object.values(vars).map(v=>v.key).join(','),timezone:'America/Lima',forecast_days:'7'});};
async function fetchWeather(place){if(cache.has(place)&&Date.now()-cache.get(place).at<12*60*1000)return cache.get(place).data;const r=await fetch(api(place),{cache:'no-store'});if(!r.ok)throw Error('Respuesta '+r.status);const j=await r.json();if(!j.daily||!Array.isArray(j.daily.time)||j.daily.time.length!==7||!j.current)throw Error('La API devolvió datos incompletos');cache.set(place,{at:Date.now(),data:j});return j}
function isSeries(a){return Array.isArray(a)&&a.length===7&&a.every(x=>x!==null&&typeof x==='number'&&Number.isFinite(x))}
function chart(j,variable){const v=vars[variable],ys=j.daily[v.key],dates=j.daily.time;if(!isSeries(ys))throw Error('Serie '+v.label+' no disponible');const W=740,H=300,L=59,R=22,T=27,B=54,wi=W-L-R,he=H-T-B;
let low=Math.min(0,...ys),hi=Math.max(...ys);if(v.type==='line'){low=Math.min(...ys);hi=Math.max(...ys);const margin=Math.max((hi-low)*.15,.5);low-=margin;hi+=margin}else hi=Math.max(hi*1.12,.5);const diff=hi-low||1;const x=i=>L+wi*(i+.5)/7,y=z=>T+he-(z-low)*he/diff;
const el=(tag,attrs,txt)=>{const z=document.createElementNS('http://www.w3.org/2000/svg',tag);Object.entries(attrs||{}).forEach(([k,val])=>z.setAttribute(k,String(val)));if(txt!==undefined)z.textContent=txt;return z};const s=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':`Gráfico de ${v.label} para ${state.place}, siete días futuros, fuente Open-Meteo`,'preserveAspectRatio':'xMidYMid meet'});s.classList.add('oaf-chart');
for(let k=0;k<5;k++){const vv=low+diff*k/4,yy=y(vv);s.append(el('line',{x1:L,y1:yy,x2:W-R,y2:yy,class:'gridline'}),el('text',{x:48,y:yy+4,'text-anchor':'end',class:'axis'},fmt(vv,1)));}
dates.forEach((d,i)=>s.append(el('text',{x:x(i),y:H-24,'text-anchor':'middle',class:'axis'},d.slice(5).replace('-','/'))));
if(v.type==='bar'){ys.forEach((n,i)=>{const rec=el('rect',{x:x(i)-wi/7*.32,y:y(n),width:wi/7*.64,height:Math.max(0,y(low)-y(n)),rx:5,class:'bar'});rec.append(el('title',{},`${dates[i]}: ${fmt(n)} ${v.unit}`));s.append(rec);});}
else{const pts_=ys.map((n,i)=>`${x(i)},${y(n)}`).join(' ');s.append(el('polyline',{points:pts_,class:'line'}));ys.forEach((n,i)=>{const c=el('circle',{cx:x(i),cy:y(n),r:5,fill:'#0a8798',stroke:'white','stroke-width':2,tabindex:0});c.append(el('title',{},`${dates[i]}: ${fmt(n)} ${v.unit}`));s.append(c)});}
s.append(el('text',{x:L,y:16,class:'axis'},v.unit));return {svg:s,vals:ys}}
function setText(sel,val){const n=$(sel);if(n)n.textContent=val}
async function render(){const status=$('#oaf-dash-status'),chartBox=$('#oaf-plot');if(!chartBox)return;status.textContent='Consultando datos meteorológicos externos…';status.classList.remove('error');chartBox.replaceChildren();
try{const j=await fetchWeather(state.place),v=vars[state.var],res=chart(j,state.var);chartBox.append(res.svg);setText('#oaf-chart-caption',`${v.label} · ${state.place} · ${j.daily.time[0]} a ${j.daily.time[6]} · ${v.unit}`);setText('#oaf-series-mean',fmt(res.vals.reduce((a,b)=>a+b,0)/7)+(v.unit==='°C'?' °C':' '+v.unit));setText('#oaf-series-min',fmt(Math.min(...res.vals))+' '+v.unit);setText('#oaf-series-max',fmt(Math.max(...res.vals))+' '+v.unit);
setText('#oaf-live-temp',fmt(j.current.temperature_2m)+' °C');setText('#oaf-live-hum',fmt(j.current.relative_humidity_2m,0)+' %');setText('#oaf-live-prec',fmt(j.current.precipitation)+' mm');setText('#oaf-live-rad',fmt(j.current.shortwave_radiation,0)+' W/m²');
setText('#oaf-home-source',`Open-Meteo · ${state.place} · ${j.current.time} (America/Lima)`);
const rr=j.daily.precipitation_sum;if(isSeries(rr)){const mx=Math.max(...rr,1);const b=$('#oaf-mini-bars');b.replaceChildren();rr.forEach((x,i)=>{const div=document.createElement('div');div.style.height=(Math.max(4,x/mx*100))+'%';div.title=`${j.daily.time[i]}: ${fmt(x)} mm`;const sp=document.createElement('span');sp.textContent=j.daily.time[i].slice(8);div.append(sp);b.append(div);});setText('#oaf-rain-sum',fmt(rr.reduce((a,b)=>a+b,0))+' mm');}
status.textContent=`Modelo externo · ${j.current.time} · 7 días. No corresponde a una medición de estación ni a una alerta OAF.`;
}catch(e){status.textContent='No hay datos disponibles: '+e.message+'. No se mostrarán valores simulados.';status.classList.add('error');setText('#oaf-home-source','Datos externos no disponibles; no se reemplazan con valores ficticios.')}
}
function initDash(){const place=$('#oaf-dash-place'),variable=$('#oaf-dash-var');if(!place)return;place.addEventListener('change',()=>{state.place=place.value;render()});variable.addEventListener('change',()=>{state.var=variable.value;render()});$('#oaf-dash-reload')?.addEventListener('click',()=>{cache.delete(state.place);render()});render();
fetch('datos/verificacion_temperatura_regional_8e.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error();return r.json()}).then(d=>{setText('#oaf-model-status',Number(d.comparados_realmente_previos_al_mes||0)+' verificaciones prospectivas completas');setText('#oaf-model-note',d.habilidad_prospectiva_demostrada?'Se dispone de evaluación prospectiva documentada.':'La habilidad prospectiva aún no ha sido demostrada; emisiones 8E archivadas para comparación posterior.');}).catch(()=>setText('#oaf-model-status','Verificación aún no consultable'));
}
const SEN='https://servicios.senasa.gob.pe/SIGIAWeb/sigia_consulta_cultivo.html';
const REG='https://servicios.senasa.gob.pe/SIGIAWeb/sigia_consulta_producto.html';
const sources={
uf:'https://ask.ifas.ufl.edu/publication/PP366',
botvid:'https://ipm.ucanr.edu/agriculture/grape/botrytis-bunch-rot/',
oidvid:'https://ipm.ucanr.edu/agriculture/grape/powdery-mildew/',
mildvid:'https://ipm.ucanr.edu/agriculture/grape/downy-mildew/',
frac:'https://www.frac.info/publications/all-downloads/',
sen:SEN};
const products={
switch:{name:'SWITCH ONE',active:'Fludioxonil',kind:'quimico',frac:'FRAC 12',source:'https://servicios.senasa.gob.pe/sig/upload?C=DL&f=12459132.1.pdf',status:'Etiqueta SENASA publicada; confirmar vigencia SIGIA',cultivos:['Arándano','Vid'],diseases:['botrytis']},
sekiro:{name:'SEKIRO',active:'Bacillus subtilis',kind:'biologico',frac:'Biocontrol microbiano',source:'https://servicios.senasa.gob.pe/sig/upload?C=DL&f=02575165.3.pdf',status:'Etiqueta SENASA con Reg. 0183-PBA-ACBM; confirmar vigencia',cultivos:['Arándano','Vid'],diseases:['botrytis']},
topas:{name:'TOPAS 100 EC',active:'Penconazol',kind:'quimico',frac:'FRAC 3 (DMI)',source:'https://servicios.senasa.gob.pe/sig/upload?C=DL&f=00002321.5.pdf',status:'Etiqueta SENASA publicada; confirmar vigencia SIGIA',cultivos:['Vid'],diseases:['oidio']},
teosim:{name:'TEOSIM',active:'Bacillus subtilis',kind:'biologico',frac:'Biocontrol microbiano',source:'https://servicios.senasa.gob.pe/sig/upload?C=DL&f=00153942.2.pdf',status:'Etiqueta SENASA publicada; confirmar vigencia SIGIA',cultivos:['Vid'],diseases:['oidio']}
};
const diseases=[
{id:'botrytis',crop:'Arándano',name:'Moho gris (Botrytis cinerea)',cultural:['Retirar fruta y tejidos enfermos conforme a medidas sanitarias.','Favorecer ventilación y evitar humedad prolongada sobre flores y frutos.','Monitorear floración, heridas y condiciones de humectación.'],src:sources.uf},
{id:'antracnosis',crop:'Arándano',name:'Antracnosis (Colletotrichum spp.)',cultural:['Reducir riego por aspersión y salpicaduras sobre frutos.','Mantener copa aireada y retirar restos afectados.','Cosechar oportunamente y enfriar la fruta después de cosecha.'],src:sources.uf},
{id:'corynespora',crop:'Arándano',name:'Mancha diana (Corynespora cassiicola)',cultural:['Inspeccionar hojas y registrar incidencia por lote.','Reducir humedad persistente y retirar material severamente afectado según diagnóstico.'],src:'https://ask.ifas.ufl.edu/publication/PP348'},
{id:'oidio',crop:'Arándano',name:'Oídio del arándano',cultural:['Inspeccionar brotes y hojas para identificar colonias.','Favorecer aireación del dosel; evitar exceso de vigor.'],src:'https://extension.oregonstate.edu/catalog/pub/em-9149-blueberry-diseases'},
{id:'phytophthora',crop:'Arándano',name:'Pudrición radicular (Phytophthora spp.)',cultural:['Mejorar drenaje y revisar saturación del suelo.','Evitar exceso de riego y movimiento de suelo o material contaminado.','Confirmar diagnóstico antes de intervenir.'],src:'https://extension.oregonstate.edu/catalog/pub/em-9149-blueberry-diseases'},
{id:'oidio',crop:'Vid',name:'Oídio de la vid (Erysiphe necator)',cultural:['Monitorear brotación, floración y racimos.','Optimizar exposición y ventilación del follaje sin producir golpe de sol.','Ajustar decisiones al estado fenológico y riesgo local.'],src:sources.oidvid},
{id:'mildiu',crop:'Vid',name:'Mildiu (Plasmopara viticola)',cultural:['Revisar manchas en hojas y condiciones de humectación.','Ajustar riego, ventilación y manejo del dosel.'],src:sources.mildvid},
{id:'botrytis',crop:'Vid',name:'Podredumbre gris (Botrytis cinerea)',cultural:['Favorecer aireación de racimos con manejo cuidadoso de canopia.','Evitar daños en bayas y exceso de riego/nitrógeno.','Inspeccionar racimos en periodos húmedos y cerca de cosecha.'],src:sources.botvid},
{id:'blackrot',crop:'Vid',name:'Podredumbre negra (Guignardia bidwellii)',cultural:['Retirar frutos momificados y material infectado en manejo sanitario.','Vigilar condiciones húmedas y síntomas en racimos.'],src:'https://extension.psu.edu/grape-disease-black-rot'}
];
function card(d){const art=document.createElement('article');art.className='oaf-control-card';const prods=Object.values(products).filter(p=>p.cultivos.includes(d.crop)&&p.diseases.includes(d.id));const title=document.createElement('h3');title.textContent=d.name;const top=document.createElement('div');top.innerHTML='<span class="oaf-chip"></span><span class="oaf-chip pending">Manejo integrado · orientación</span>';top.firstChild.textContent=d.crop;art.append(top,title);const sm=document.createElement('p');sm.innerHTML='<b>Prevención y manejo cultural</b>';art.append(sm);const ul=document.createElement('ul');d.cultural.forEach(v=>{const li=document.createElement('li');li.textContent=v;ul.append(li)});art.append(ul);const h=document.createElement('p');h.innerHTML='<b>Opciones con etiqueta SENASA publicada</b>';art.append(h);
if(!prods.length){const p=document.createElement('p');p.textContent='Sin producto específico documentado en esta ficha. Consultar SIGIA para verificar opciones autorizadas por cultivo y enfermedad; no se extrapolan registros.';art.append(p);}
prods.forEach(p=>{const row=document.createElement('p');const a=document.createElement('a');a.href=p.source;a.target='_blank';a.rel='noopener noreferrer';a.textContent=p.name+' ↗';const t=document.createElement('span');t.textContent=` · ${p.kind==='quimico'?'Químico':'Biológico'} · ${p.active} · ${p.frac}`;row.append(a,t);const sm=document.createElement('small');sm.style.display='block';sm.textContent=p.status;row.append(sm);art.append(row)});
const links=document.createElement('div');links.className='links';for(const [url,label] of [[d.src,'Respaldo científico ↗'],[SEN,'Verificar en SENASA ↗']]){const a=document.createElement('a');a.href=url;a.target='_blank';a.rel='noopener noreferrer';a.textContent=label;links.append(a)}art.append(links);return art}
function renderControls(){const c=$('#oaf-control-crop'),t=$('#oaf-control-type'),out=$('#oaf-control-cards');if(!out)return;out.replaceChildren();const filtered=diseases.filter(d=>(c.value==='Todos'||d.crop===c.value)&&(!t||t.value==='todos'||Object.values(products).some(p=>p.cultivos.includes(d.crop)&&p.diseases.includes(d.id)&&p.kind===t.value)));for(const d of filtered)out.append(card(d));setText('#oaf-control-count',filtered.length+' enfermedades · '+(t.value==='todos'?'opciones documentadas o en verificación':t.value));}
function initControls(){$('#oaf-control-crop')?.addEventListener('change',renderControls);$('#oaf-control-type')?.addEventListener('change',renderControls);renderControls()}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>{initDash();initControls()});else{initDash();initControls()}
})();
