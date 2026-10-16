/* OAF-Lambayeque 8G — visor público de verificación.
 * Únicamente muestra evaluaciones calculadas a partir de emisiones 8E inmutables.
 * Nunca calcula ni presenta resultados sintéticos o habilidad operativa.
 */
(()=>{
  'use strict';
  const pane=document.getElementById('oaf-eval-8g');
  if(!pane)return;
  const $=id=>document.getElementById(id);
  const status=$('oaf-8g-status'),rows=$('oaf-8g-rows'),plot=$('oaf-8g-plot');
  const locality=$('oaf-8g-localidad'),horizon=$('oaf-8g-horizonte'),scope=$('oaf-8g-clase');
  const reload=$('oaf-8g-actualizar');
  const DATA='datos/evaluacion_prospectiva_8g/metricas_8g.json';
  let loaded=null;
  const models=[
    ['local','Referencia local'],
    ['nino_t300','Local + Niño 1+2 + T300'],
    ['climatologia','Climatología fija'],
    ['persistencia','Persistencia']
  ];
  const format=(x,d=2)=>typeof x==='number'&&Number.isFinite(x)
    ?x.toLocaleString('es-PE',{minimumFractionDigits:d,maximumFractionDigits:d}):'No evaluable';
  const set=(id,value)=>{$(id).textContent=value};
  function addCell(tr,value){const cell=document.createElement('td');cell.textContent=value;tr.appendChild(cell)}
  function selectMetric(root){
    const x=root.metricas[scope.value];
    const city=locality.value,h=horizon.value;
    if(city!=='todos'&&h!=='todos')return x.por_localidad_horizonte[city][h];
    if(city!=='todos')return x.por_localidad[city];
    if(h!=='todos')return x.por_horizonte[h];
    return x.total;
  }
  function plotComparisons(info){
    plot.replaceChildren();
    if(info.n===0){
      const p=document.createElement('p');
      p.className='small';
      p.textContent='Todavía no existen observaciones posteriores elegibles para dibujar una comparación de errores. No se muestran barras ficticias.';
      plot.appendChild(p);
      return;
    }
    const filtered=models.map(([key,label])=>({key,label,value:info.modelos[key]?.mae_c}))
      .filter(x=>typeof x.value==='number'&&Number.isFinite(x.value));
    if(!filtered.length)return;
    const width=750,height=245,left=200,right=70,top=20,bottom=22;
    const hi=Math.max(...filtered.map(x=>x.value),.01)*1.1;
    const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
    svg.setAttribute('viewBox',`0 0 ${width} ${height}`);
    svg.setAttribute('role','img');svg.setAttribute('aria-label','Gráfico MAE por modelo con valores observados posteriores');
    svg.classList.add('oaf-chart');svg.style.height='245px';
    const make=(tag,attrs,text)=>{
      const n=document.createElementNS('http://www.w3.org/2000/svg',tag);
      for(const [k,v] of Object.entries(attrs||{}))n.setAttribute(k,String(v));
      if(text!==undefined)n.textContent=text;return n;
    };
    filtered.forEach((x,i)=>{
      const y=22+i*53,valWidth=(width-left-right)*x.value/hi;
      svg.append(make('text',{x:left-9,y:y+25,'text-anchor':'end',fill:'#395c71','font-size':12},x.label));
      svg.append(make('rect',{x:left,y:y+6,width:valWidth,height:27,rx:5,fill:i===1?'#39a876':'#1984a5'}));
      svg.append(make('text',{x:left+valWidth+8,y:y+25,'font-size':12,fill:'#395c71'},format(x.value)+' °C'));
    });
    plot.appendChild(svg);
  }
  function draw(){
    if(!loaded)return;
    const d=loaded;
    const selected=selectMetric(d);
    set('oaf-8g-archivados',String(d.n_registros_archivados));
    set('oaf-8g-previos',String(d.n_premes_archivados));
    set('oaf-8g-evaluados',String(d.n_verificados_premes));
    set('oaf-8g-cut',d.evaluado_con_corte_utc||'—');
    set('oaf-8g-selected-n',String(selected.n));
    rows.replaceChildren();
    models.forEach(([key,label])=>{
      const m=selected.modelos[key],tr=document.createElement('tr');
      addCell(tr,label);addCell(tr,String(selected.n));
      addCell(tr,format(m.mae_c));addCell(tr,format(m.rmse_c));
      addCell(tr,format(m.sesgo_c));addCell(tr,'No evaluable');
      rows.appendChild(tr);
    });
    plotComparisons(selected);
    const percent=selected.mejora_mae_nino_vs_local_pct;
    set('oaf-8g-improvement',percent===null||percent===undefined
      ?'No evaluable: faltan contrastes posteriores o referencia comparable.'
      :`Variación descriptiva de MAE Niño/T300 respecto al modelo local: ${format(percent,1)} %. No demuestra habilidad operativa.`);
    status.textContent=d.n_verificados_total===0
      ?'Sin verificaciones disponibles: ninguna predicción archivada se ha comparado aún con un mes objetivo completo. Próxima fecha mínima de consulta: '+d.primera_fecha_elegible+'.'
      :'Resultados descriptivos de '+d.n_verificados_total+' comparaciones con reanálisis ERA5-Land. Sin validación instrumental ni habilidad prospectiva demostrada.';
  }
  async function load(){
    reload.disabled=true;
    status.textContent='Consultando el informe 8G publicado…';
    try{
      const r=await fetch(DATA,{cache:'no-store'});
      if(!r.ok)throw Error('HTTP '+r.status);
      const d=await r.json();
      if(d.fase!=='8G'||d.habilidad_prospectiva_demostrada!==false||
         d.validacion_instrumental!==false||d.intervalos_calibrados_disponibles!==false||
         !d.metricas?.premes?.total?.modelos?.local||!d.metricas?.intramensual?.total?.modelos?.nino_t300)
        throw Error('Informe incompatible con el protocolo de transparencia');
      loaded=d;draw();
    }catch(err){
      loaded=null;rows.replaceChildren();plot.replaceChildren();
      status.textContent='No fue posible verificar los datos 8G: '+err.message+'. No se sustituyen por valores estimados.';
    }finally{reload.disabled=false}
  }
  locality.addEventListener('change',draw);
  horizon.addEventListener('change',draw);
  scope.addEventListener('change',draw);
  reload.addEventListener('click',load);
  let started=false;
  pane.addEventListener('toggle',()=>{
    if(pane.open&&!started){started=true;load()}
  });
})();
