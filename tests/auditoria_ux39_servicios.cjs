/* UX51 · Auditoría de fuentes: vector INGEMMET y ráster CENEPRED por Identify. */
"use strict";
const fs=require("node:fs"),path=require("node:path");
const point={lat:-6.15083,lon:-79.7142};
const bounds={minLon:point.lon-.0008,maxLon:point.lon+.0008,minLat:point.lat-.0008,maxLat:point.lat+.0008};
const polygon={rings:[[
 [bounds.minLon,bounds.minLat],[bounds.minLon,bounds.maxLat],[bounds.maxLon,bounds.maxLat],
 [bounds.maxLon,bounds.minLat],[bounds.minLon,bounds.minLat]
]],spatialReference:{wkid:4326}};
const samples=[];
for(let i=1;i<=5;i++)for(let j=1;j<=5;j++)samples.push([
 bounds.minLon+i*(bounds.maxLon-bounds.minLon)/6,
 bounds.minLat+j*(bounds.maxLat-bounds.minLat)/6
]);
const cenepred="https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer";
const ingemmet="https://geocatmin.ingemmet.gob.pe/arcgis/rest/services/SERV_SUSCEPTIBILIDAD_INUNDACION_FLUVIAL_MIL1/MapServer";
const sources=[
 {fuente:"Open-Meteo · pronóstico agroclimático 7 días",timeout:25000,
  url:"https://api.open-meteo.com/v1/forecast?"+new URLSearchParams({latitude:String(point.lat),longitude:String(point.lon),timezone:"America/Lima",forecast_days:"7",
   daily:"precipitation_sum,temperature_2m_max,temperature_2m_min,relative_humidity_2m_mean,shortwave_radiation_sum,wind_speed_10m_max,et0_fao_evapotranspiration,vapour_pressure_deficit_max"}),
  valid:j=>Array.isArray(j.daily?.time)&&j.daily.time.length===7&&j.daily.precipitation_sum?.length===7&&j.daily.temperature_2m_max?.length===7,
  details:j=>({dias:j.daily.time.length,celda:[j.latitude,j.longitude],variables:Object.keys(j.daily).filter(k=>k!=="time")})},
 {fuente:"Open-Meteo · condiciones actuales de portada",timeout:20000,
  url:"https://api.open-meteo.com/v1/forecast?"+new URLSearchParams({latitude:String(point.lat),longitude:String(point.lon),timezone:"America/Lima",forecast_days:"1",current:"temperature_2m,relative_humidity_2m,precipitation,shortwave_radiation,wind_speed_10m"}),
  valid:j=>Boolean(j.current?.time)&&Number.isFinite(j.current?.temperature_2m)&&Number.isFinite(j.current?.relative_humidity_2m),
  details:j=>({hora:j.current.time,variables:["temperature_2m","relative_humidity_2m","precipitation","shortwave_radiation","wind_speed_10m"]})},
 {fuente:"Open-Meteo Air Quality · CAMS global",timeout:20000,
  url:"https://air-quality-api.open-meteo.com/v1/air-quality?"+new URLSearchParams({latitude:String(point.lat),longitude:String(point.lon),timezone:"America/Lima",forecast_days:"1",current:"european_aqi,pm2_5,pm10",domains:"cams_global"}),
  valid:j=>Boolean(j.current?.time)&&[j.current?.european_aqi,j.current?.pm2_5,j.current?.pm10].some(Number.isFinite),
  details:j=>({hora:j.current.time,dominio:"cams_global",aqi:j.current.european_aqi,pm25:j.current.pm2_5,pm10:j.current.pm10})},
 {fuente:"Open-Meteo Archive · ERA5-Land",timeout:20000,
  url:"https://archive-api.open-meteo.com/v1/archive?"+new URLSearchParams({latitude:String(point.lat),longitude:String(point.lon),start_date:"2025-01-01",end_date:"2025-01-03",daily:"temperature_2m_mean,precipitation_sum",timezone:"America/Lima",models:"era5_land"}),
  valid:j=>Array.isArray(j.daily?.time)&&j.daily.time.length===3,
  details:j=>({modelo:"era5_land",dias:j.daily.time.length,celda:[j.latitude,j.longitude]})},
 {fuente:"Open-Meteo · ECMWF SEAS5 estacional",timeout:30000,
  url:"https://seasonal-api.open-meteo.com/v1/seasonal?"+new URLSearchParams({latitude:String(point.lat),longitude:String(point.lon),models:"ecmwf_seas5_ensemble_mean",hourly:"precipitation,temperature_2m",forecast_days:"217",timezone:"America/Lima",precipitation_unit:"mm"}),
  valid:j=>Array.isArray(j.hourly?.time)&&j.hourly.time.length>0&&j.hourly.precipitation?.length===j.hourly.time.length&&j.hourly.temperature_2m?.length===j.hourly.time.length,
  details:j=>({modelo:"ecmwf_seas5_ensemble_mean",intervalos_6h:j.hourly.time.length,celda:[j.latitude,j.longitude],unidades:j.hourly_units})}
];
const arcgis=[
 {fuente:"CENEPRED · susceptibilidad regional de inundación · 5010502",kind:"raster",layer:"5010502"},
 {fuente:"CENEPRED · susceptibilidad a movimientos en masa por lluvias fuertes · 5090022",kind:"raster",layer:"5090022"},
 {fuente:"CENEPRED · susceptibilidad a inundaciones por lluvias fuertes · 5090024",kind:"raster",layer:"5090024"},
 {fuente:"INGEMMET · susceptibilidad a inundación fluvial 1:1 000 000 · 0",kind:"vector",layer:"0",base:ingemmet}
];
async function get(url,timeout=20000){
 const controller=new AbortController(),id=setTimeout(()=>controller.abort(),timeout);
 try{
  const response=await fetch(url,{signal:controller.signal,headers:{accept:"application/json"}});
  if(!response.ok)throw Error("HTTP "+response.status);
  const body=await response.json();if(body.error)throw Error(body.error.message||"Servicio devolvió error");
  return body;
 }finally{clearTimeout(id);}
}
async function post(url,params,timeout=30000){
 const controller=new AbortController(),id=setTimeout(()=>controller.abort(),timeout);
 try{
  const response=await fetch(url,{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded;charset=UTF-8",accept:"application/json"},
   body:params.toString(),signal:controller.signal});
  if(!response.ok)throw Error("HTTP "+response.status);
  const body=await response.json();if(body.error)throw Error(body.error.message||"Servicio devolvió error");
  return body;
 }finally{clearTimeout(id);}
}
function pointIdentifyParams(layer){
 return new URLSearchParams({geometry:JSON.stringify({x:point.lon,y:point.lat,spatialReference:{wkid:4326}}),
  geometryType:"esriGeometryPoint",sr:"4326",layers:"all:"+layer,tolerance:"2",
  mapExtent:[point.lon-.04,point.lat-.04,point.lon+.04,point.lat+.04].join(","),
  imageDisplay:"700,340,96",returnGeometry:"false",f:"json"});
}
function multipointIdentifyParams(layer){
 return new URLSearchParams({geometryType:"esriGeometryMultipoint",
  geometry:JSON.stringify({points:samples,spatialReference:{wkid:4326}}),sr:"4326",layers:"all:"+layer,tolerance:"1",
  mapExtent:[bounds.minLon,bounds.minLat,bounds.maxLon,bounds.maxLat].join(","),
  imageDisplay:"1000,1000,96",returnGeometry:"false",f:"json"});
}
function polygonQueryParams(){
 return new URLSearchParams({where:"1=1",geometry:JSON.stringify(polygon),geometryType:"esriGeometryPolygon",
  inSR:"4326",spatialRel:"esriSpatialRelIntersects",outFields:"OBJECTID,GRIDCODE,LEYENDA",
  returnGeometry:"true",outSR:"4326",resultRecordCount:"2000",f:"json"});
}
async function checkWeather(item){
 const timestamp=new Date().toISOString();
 try{const body=await get(item.url,item.timeout);if(!item.valid(body))throw Error("Respuesta sin estructura o cobertura esperada");
  return {fuente:item.fuente,estado:"responde",fecha_utc:timestamp,metadatos:item.details(body)};
 }catch(error){return {fuente:item.fuente,estado:"no_verificable",fecha_utc:timestamp,motivo:String(error.message).slice(0,300)};}
}
async function checkArcGIS(item){
 const timestamp=new Date().toISOString(),base=item.base||cenepred;
 try{
  const metadata=await get(base+"/"+item.layer+"?f=json",20000);
  if(item.kind==="raster"){
   if(metadata.type!=="Raster Layer")throw Error("La metadata no identifica una capa ráster: "+(metadata.type||"tipo no informado"));
   const body=await get(base+"/identify?"+pointIdentifyParams(item.layer),25000);
   if(!Array.isArray(body.results))throw Error("Identify puntual sin arreglo results");
   return {fuente:item.fuente,estado:"responde",fecha_utc:timestamp,
    metadatos:{tipo:metadata.type,metodo:"Identify puntual",resultados:body.results.length,geometryType:metadata.geometryType??null}};
  }
  if(metadata.type!=="Feature Layer"||metadata.geometryType!=="esriGeometryPolygon")
   throw Error("INGEMMET no se identificó como Feature Layer poligonal");
  const body=await get(base+"/"+item.layer+"/query?"+polygonQueryParams(),25000);
  if(!Array.isArray(body.features))throw Error("Query poligonal sin arreglo features");
  return {fuente:item.fuente,estado:body.exceededTransferLimit?"responde_con_limite":"responde",
   fecha_utc:timestamp,metadatos:{tipo:metadata.type,geometryType:metadata.geometryType,
    formato:metadata.supportedQueryFormats||"no informado",poligonos_intersectantes:body.features.length,
    exceededTransferLimit:Boolean(body.exceededTransferLimit),consulta:"intersección con polígono WGS84 real"}};
 }catch(error){return {fuente:item.fuente,estado:"no_verificable",fecha_utc:timestamp,motivo:String(error.message).slice(0,300)};}
}
async function checkRasterParcel(item){
 const timestamp=new Date().toISOString();
 try{
  const metadata=await get(cenepred+"/"+item.layer+"?f=json",20000);
  if(metadata.type!=="Raster Layer")throw Error("No se confirmó la naturaleza ráster de la capa");
  const body=await post(cenepred+"/identify",multipointIdentifyParams(item.layer),30000);
  if(!Array.isArray(body.results))throw Error("Identify multipunto sin arreglo results");
  const categories={};
  for(const result of body.results){
   const a=result.attributes||{},raw=a.n_peligro??a.n_pelig_mm??a.value??a.gridcode??result.value??"Sin clasificar";
   const key=String(raw);categories[key]=(categories[key]||0)+1;
  }
  return {fuente:"CENEPRED · prueba zonal multipunto · capa "+item.layer,
   estado:body.results.length?"responde_con_valores":"responde_sin_valores",fecha_utc:timestamp,
   metadatos:{tipo:metadata.type,metodo:"Identify multipunto",muestras:samples.length,
    resultados:body.results.length,categorias:categories,
    alcance:"distribución de valores devueltos; no equivale a hectáreas exactas"}};
 }catch(error){return {fuente:"CENEPRED · prueba zonal multipunto · capa "+item.layer,
  estado:"no_verificable",fecha_utc:timestamp,motivo:String(error.message).slice(0,300)};}
}
(async()=>{
 const weatherResults=await Promise.all(sources.map(checkWeather));
 const arcResults=await Promise.all(arcgis.map(checkArcGIS));
 const rasterParcelResults=await Promise.all(arcgis.filter(x=>x.kind==="raster"&&["5090022","5090024"].includes(x.layer)).map(checkRasterParcel));
 const results=[...weatherResults,...arcResults,...rasterParcelResults];
 const obj={revision:"UX51",fecha_utc:new Date().toISOString(),coordenada_muestra:point,
  poligono_muestra:{tipo:"cuadrado WGS84",bounds},muestras_multipunto:samples.length,
  alcance:"Disponibilidad técnica, metadata y respuesta de fuentes. CENEPRED es ráster y se consulta mediante Identify multipunto; INGEMMET es vectorial y se consulta con el polígono real. Una consulta vacía no equivale a ausencia de peligro ni a riesgo cero.",
  fuentes:results};
 fs.writeFileSync(path.resolve("ux51-auditoria-geoservicios.json"),JSON.stringify(obj,null,2)+"\n");
 for(const r of results)console.log(r.fuente,":",r.estado,r.motivo||JSON.stringify(r.metadatos));
 const summary=process.env.GITHUB_STEP_SUMMARY;
 if(summary)fs.appendFileSync(summary,["## Auditoría UX51: geoservicios y pronóstico agroclimático","",
  ...results.map(r=>"- "+r.fuente+": **"+r.estado+"**"+(r.motivo?" ("+r.motivo+")":"")),
  "","CENEPRED se evalúa con Identify multipunto; INGEMMET con intersección vectorial del polígono real. Los porcentajes ráster son proporciones de muestras, no hectáreas exactas."].join("\n"));
})().catch(error=>{console.error(error);process.exitCode=1});
