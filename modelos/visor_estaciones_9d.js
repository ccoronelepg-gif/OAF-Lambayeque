/* OAF Fase 9D: dashboard de estaciones entregadas por usuario.
   Archivo: datos/estaciones_9d/series_mensuales_9d.csv
   Metadatos geograficos pendientes; datos retrospectivos, sin alertas. */
(() => {
  "use strict";
  const el = id => document.getElementById(id);
  const STATION_NAMES={"00000340":"El Espinal","00153114":"Puchaca","00152107":"Virrey"};
  const numeric = x => x === "" || x == null ? null : Number(x);
  const fmt = (n, dp = 1) =>
    n === null || !Number.isFinite(n) ? "Sin datos" :
    n.toLocaleString("es-PE", { maximumFractionDigits: dp, minimumFractionDigits: dp });
  const years = { "1980-1999": [1980, 1999], "1996-2013": [1996, 2013], "2000-2013": [2000, 2013] };
  function parse(text) {
    const lines = text.trim().split(/\r?\n/);
    const keys = lines.shift().split(",");
    return lines.map(line => {
      const a = line.split(","), x = {};
      keys.forEach((k,i) => x[k] = a[i]);
      return x;
    });
  }
  function annual(records, code, start, end, variable) {
    const all = [];
    for(let y=start;y<=end;y++){
      const months=records.filter(r=>r.codigo===code && r.mes.startsWith(y+"-"));
      let v=null;
      if(months.length===12){
        const key=variable==="precip"?"precip_total_mm":variable+"_media_c";
        const good=months.every(x=>numeric(x[key])!==null);
        if(good){
          if(variable==="precip") v=months.reduce((z,x)=>z+Number(x[key]),0);
          else {
            const count=variable+"_dias_validos";
            const denom=months.reduce((z,x)=>z+Number(x[count]),0);
            v=denom?months.reduce((z,x)=>z+Number(x[key])*Number(x[count]),0)/denom:null;
          }
        }
      }
      all.push({year:y,value:v});
    }
    return all;
  }
  function appendText(parent,tag,value){
    const n=document.createElement(tag);n.textContent=value;parent.appendChild(n);return n;
  }
  async function init(){
    if(!el("oaf-9d-estaciones")) return;
    const [monthly, report] = await Promise.all([
      fetch("datos/estaciones_9d/series_mensuales_9d.csv",{cache:"no-store"}).then(r=>r.ok?r.text():Promise.reject(new Error("CSV "+r.status))),
      fetch("datos/estaciones_9d/auditoria_estaciones_9d.json",{cache:"no-store"}).then(r=>r.ok?r.json():Promise.reject(new Error("JSON "+r.status)))
    ]);
    if(report.fase!=="9D"||report.totales.archivos!==3)throw Error("Esquema o version de 9D incorrectos");
    const data=parse(monthly),site=el("oaf-9d-site"),variable=el("oaf-9d-var"),period=el("oaf-9d-period");
    for(const row of report.estaciones){
      const op=document.createElement("option");op.value=row.codigo;op.textContent=(STATION_NAMES[row.codigo]||"Estación")+" · "+row.codigo;site.append(op);
    }
    for(const [value,label] of [["precip","Lluvia acumulada (mm/año)"],["tmax","Temperatura máxima media (°C)"],["tmin","Temperatura mínima media (°C)"]]){
      const op=document.createElement("option");op.value=value;op.textContent=label;variable.append(op);
    }
    for(const [value,label] of [["1980-1999","1980–1999 · grandes episodios"],["1996-2013","1996–2013 · tramo parcial"],["2000-2013","2000–2013 · periodo reciente"]]){
      const op=document.createElement("option");op.value=value;op.textContent=label;period.append(op);
    }
    site.value="00152107";variable.value="precip";period.value="1980-1999";
    function draw(){
      const code=site.value, v=variable.value, range=years[period.value];
      const station=report.estaciones.find(x=>x.codigo===code);
      const annuals=annual(data,code,...range,v),present=annuals.filter(x=>x.value!==null),max=Math.max(1,...present.map(x=>x.value)),plot=el("oaf-9d-chart");
      plot.replaceChildren();
      plot.style.cssText="display:flex;align-items:stretch;gap:5px;overflow-x:auto;margin-top:10px;padding:10px 3px 16px;border-bottom:1px solid #d9e2e8;";
      for(const a of annuals){
        const block=document.createElement("div");
        block.style.cssText="flex:1 0 28px;min-width:28px;display:flex;flex-direction:column;align-items:center;justify-content:end;gap:5px;";
        const value=appendText(block,"span",a.value===null?"—":fmt(a.value,0));
        value.style.cssText="font-size:10px;text-align:center;color:#365267;min-height:16px;";
        const pole=document.createElement("div");
        pole.style.cssText="width:72%;min-height:3px;border-radius:4px 4px 0 0;background:"+
           (a.value===null?"#d4dade": a.year===1998?"#9c6541":"#0e739d")+";";
        pole.style.height=(a.value===null?3:Math.max(3,a.value/max*145))+"px";
        block.title=a.year+": "+(a.value===null?"año incompleto o variable ausente":fmt(a.value,2)+(v==="precip"?" mm":" °C"));
        block.append(pole);
        const year=appendText(block,"span",String(a.year));year.style.cssText="font-size:10px;white-space:nowrap;writing-mode:vertical-rl;transform:rotate(180deg);";
        plot.append(block);
      }
      el("oaf-9d-count").textContent=present.length+" de "+annuals.length+" años con 12 meses válidos";
      const measurement=v==="precip"?"suma anual de precipitación":"media anual ponderada por días de observación";
      el("oaf-9d-caption").textContent="Leyenda: cada barra representa "+measurement+". Una barra gris es falta de datos suficientes, no un valor cero. "+ 
        "Se exige cobertura mensual ≥90 % y 12 meses válidos por año; los extremos conservados requieren verificación instrumental. "+
        "Las tres series solo llegan hasta 2013 o julio de 2014; no sirven para calcular la normal completa 1996–2025. "+
        (STATION_NAMES[code]||"Estación")+" ("+code+"): "+station.extremos_lluvia_150mm.length+" registros de lluvia ≥150 mm/día señalados para revisión.";
      el("oaf-9d-qc").textContent="Precipitación válida en archivo: "+fmt(station.precip_cobertura_total_pct,1)+
        " %. Temperatura máxima: "+fmt(station.tmax_cobertura_total_pct,1)+
        " %. Periodo instrumental: "+station.inicio+" a "+station.fin+". Sin coordenadas ni altitud verificadas.";
    }
    [site,variable,period].forEach(x=>x.addEventListener("change",draw));
    draw();el("oaf-9d-state").textContent="Series 9D cargadas · archivo original y auditoría reproducibles.";
  }
  const run=()=>init().catch(err=>{if(el("oaf-9d-state"))el("oaf-9d-state").textContent="Error de carga de 9D: "+err.message;});
  if(document.readyState==="loading") document.addEventListener("DOMContentLoaded",run);
  else run();
})();
