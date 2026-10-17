/* OAF 8V: visualizador de archivo modelado histórico, no predicción. */
(() => {
  'use strict';
  const panel = document.getElementById('oaf-integracion-8v');
  if (!panel) return;
  const get = id => document.getElementById(id);
  const state = get('oaf-8v-status');
  const site = get('oaf-8v-site');
  const variable = get('oaf-8v-variable');
  const windowYears = get('oaf-8v-window');
  const svg = get('oaf-8v-chart');
  const UNITS = {
    temperatura_aire_c:['Temperatura media del aire','°C'],
    precipitacion_mes_mm:['Precipitación mensual','mm'],
    radiacion_mes_mj_m2:['Radiación corta mensual','MJ/m²'],
    viento_10m_m_s:['Viento a 10 m','m/s'],
    viento_u_aprox_m_s:['Viento zonal aproximado (u)','m/s'],
    viento_v_aprox_m_s:['Viento meridional aproximado (v)','m/s'],
    anomalia_nino12_c:['Anomalía SST regional Niño 1+2','°C']
  };
  let rows = [], loaded = false;
  function csv(txt) {
    const lines=txt.trim().split(/\r?\n/), head=lines.shift().split(',');
    return lines.map(line=>{
      const vals=line.split(',');
      return Object.fromEntries(head.map((k,i)=>[k,vals[i]||'']));
    });
  }
  function svgEl(tag, attrs, label) {
    const el=document.createElementNS('http://www.w3.org/2000/svg',tag);
    Object.entries(attrs||{}).forEach(([k,v])=>el.setAttribute(k,String(v)));
    if(label!==undefined) el.textContent=String(label);
    return el;
  }
  function render() {
    if(!loaded) return;
    const key=variable.value, def=UNITS[key], yr=Number(windowYears.value);
    const data=rows.filter(r=>r.localidad===site.value&&Number(r.mes.slice(0,4))>=yr)
      .map(r=>({mes:r.mes,y:Number(r[key])})).filter(r=>Number.isFinite(r.y));
    svg.replaceChildren();
    if(data.length<2){state.textContent='Sin meses suficientes para el gráfico.';return;}
    const W=750,H=300,L=57,R=17,T=18,B=43;
    let low=Math.min(...data.map(r=>r.y)),high=Math.max(...data.map(r=>r.y));
    if(low===high){low-=1;high+=1;}
    const delta=high-low;low-=delta*.06;high+=delta*.06;
    const X=i=>L+(W-L-R)*i/(data.length-1);
    const Y=v=>T+(H-T-B)*(high-v)/(high-low);
    svg.setAttribute('viewBox',`0 0 ${W} ${H}`);
    svg.setAttribute('aria-label',`${def[0]} en ${site.value}, ${data[0].mes} a ${data[data.length-1].mes}. Reanálisis histórico.`);
    for(let i=0;i<=4;i++){
      const y=T+i*(H-T-B)/4;
      svg.append(svgEl('line',{x1:L,x2:W-R,y1:y,y2:y,stroke:'currentColor',opacity:.15}));
      svg.append(svgEl('text',{x:L-8,y:y+4,'text-anchor':'end','font-size':12,fill:'currentColor'},
        (high-i*(high-low)/4).toFixed(key==='precipitacion_mes_mm'?0:1)));
    }
    svg.append(svgEl('polyline',{
      points:data.map((r,i)=>`${X(i).toFixed(2)},${Y(r.y).toFixed(2)}`).join(' '),
      fill:'none',stroke:'#2483b4','stroke-width':2,'stroke-linejoin':'round'
    }));
    [0,Math.floor((data.length-1)/2),data.length-1].forEach(i=>
      svg.append(svgEl('text',{x:X(i),y:H-16,'text-anchor':'middle','font-size':12,fill:'currentColor'},data[i].mes))
    );
    get('oaf-8v-chart-title').textContent=`${def[0]} (${def[1]}) · ${site.value}`;
    state.textContent=`${data.length} meses de archivo histórico. Valores modelados, no alertas; extremos pendientes de cotejo SENAMHI.`;
  }
  async function load(){
    if(loaded) return render();
    state.textContent='Leyendo archivos históricos auditados...';
    try {
      const r=await Promise.all([
        fetch('datos/integracion_8v/matriz_terrestre_8v.csv',{cache:'no-store'}),
        fetch('datos/integracion_8v/estado_integracion_8v.json',{cache:'no-store'})
      ]);
      if(r.some(x=>!x.ok)) throw Error('Archivo de origen no publicado');
      const [text, meta]=await Promise.all([r[0].text(),r[1].json()]);
      if(meta.filas_matriz_terrestre!==1440 || meta.no_hay_validacion_prospectiva_de_prediccion!==true)
        throw Error('Estado de calidad 8V incompatible');
      rows=csv(text);
      if(rows.length!==meta.filas_matriz_terrestre) throw Error('Filas CSV y metadatos no coinciden');
      get('oaf-8v-nland').textContent=String(meta.filas_matriz_terrestre);
      get('oaf-8v-nsea').textContent=String(meta.filas_matriz_marina);
      get('oaf-8v-ncurrent').textContent=String(meta.meses_corriente_geostrofica_integrados);
      get('oaf-8v-nextreme').textContent=String(meta.meses_sitio_lluvia_modelada_ge_1000_mm_revision);
      loaded=true;render();
    }catch(e){state.textContent=`Datos no disponibles: ${e.message}. Comprueba los enlaces al CSV.`;}
  }
  panel.addEventListener('toggle',()=>{if(panel.open) load();});
  [site,variable,windowYears].forEach(el=>el.addEventListener('change',render));
  if(panel.open) load();
})();
