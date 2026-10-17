/* QA de portada pública; pruebas sin Internet ni datos ficticios en producción. */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const vm=require("node:vm");

const html=fs.readFileSync("index.html","utf8");
const home=html.split('<section data-page="inicio" id="inicio">')[1].split('<section data-page="clima" id="clima" hidden>')[0];
assert.equal((home.match(/<section\b/g)||[]).length+1,(home.match(/<\/section>/g)||[]).length,"Los módulos de inicio y su sección contenedora deben estar balanceados");
assert.equal((home.match(/<div\b/g)||[]).length,(home.match(/<\/div>/g)||[]).length,"DIV balanceados");
assert.equal((home.match(/class="oaf-metric(?:\s|")/g)||[]).length,7);
assert.match(home,/Ciencia Climática al servicio del campo/);
assert.match(home,/Blueberry_close_up\.jpg/);
assert.match(home,/Bunch_Of_Grapes_On_Vine\.jpg/);
assert.match(home,/id="oaf-live-air"/);
assert.match(home,/id="oaf-home-analysis"/);
assert.match(home,/OAF-Lambayeque/);
assert.match(home,/id="oaf-news-chirps"/);
assert.match(home,/id="oaf-altitudinal-map"/);
assert.match(home,/id="oaf-forecast-grid"/);
assert.match(html,/assets\/oaf-inicio-climatico-2026\.js\?v=1/);
assert.match(html,/assets\/oaf-interfaz-clara-2026\.css\?v=1/);
assert.doesNotMatch(html.match(/<summary\b[^>]*>[\s\S]*?<\/summary>/gi)?.join("\n")||"",/\bFase\s+\d+[A-Z]?/i,"Títulos públicos sin códigos");
const nodes={};
for(const id of ["oaf-home-location","oaf-home-refresh","oaf-live-temp","oaf-live-prec",
 "oaf-live-hum","oaf-live-vpd","oaf-live-wind","oaf-live-rad","oaf-live-air",
 "oaf-home-source","oaf-home-analysis"]){
 nodes[id]={value:id==="oaf-home-location"?"Chiclayo":"",textContent:"",disabled:false,
   events:{},addEventListener(name,cb){this.events[name]=cb;}};
}
const doc={readyState:"complete",getElementById(id){return nodes[id]||null;}};
let airFails=false,weatherFails=false;
const fetchMock=async address=>{
 const u=new URL(address);
 assert.equal(u.searchParams.get("timezone"),"America/Lima");
 if(u.hostname.startsWith("air-quality-api")){
   assert.equal(u.searchParams.get("domains"),"cams_global");
   assert.match(u.searchParams.get("current"),/european_aqi/);
   if(airFails)throw Error("simulated");
   return {ok:true,json:async()=>({current:{time:"2026-10-17T12:00",european_aqi:68,pm2_5:25,pm10:50}})};
 }
 if(weatherFails)throw Error("simulated");
 return {ok:true,json:async()=>({current:{time:"2026-10-17T12:00",temperature_2m:34,
  relative_humidity_2m:85,precipitation:0,shortwave_radiation:550,wind_speed_10m:22}})};
};
const context={document:doc,fetch:fetchMock,URLSearchParams,
  Object,Number,Math,Promise,RegExp,String,Error};
vm.runInNewContext(fs.readFileSync("assets/oaf-inicio-climatico-2026.js","utf8"),context);
const settle=()=>new Promise(resolve=>setImmediate(resolve));
(async()=>{
 await settle();
 assert.match(nodes["oaf-live-temp"].textContent,/34/);
 assert.match(nodes["oaf-live-air"].textContent,/mala/);
 assert.match(nodes["oaf-home-source"].textContent,/Chiclayo · 17\/10\/2026 · 12:00/);
 assert.match(nodes["oaf-home-analysis"].textContent,/Temperatura del aire: 34/);
 assert.match(nodes["oaf-home-analysis"].textContent,/Humedad relativa: 85/);
 assert.match(nodes["oaf-home-analysis"].textContent,/índice europeo calculado con CAMS: 68 \(mala\)/);
 airFails=true;
 nodes["oaf-home-location"].value="Motupe";
 nodes["oaf-home-location"].events.change();
 await settle();
 assert.match(nodes["oaf-live-temp"].textContent,/34/);
 assert.equal(nodes["oaf-live-air"].textContent,"—");
 assert.match(nodes["oaf-home-analysis"].textContent,/Calidad del aire: no evaluable/);
 weatherFails=true;airFails=false;
 nodes["oaf-home-refresh"].events.click();
 await settle();
 assert.equal(nodes["oaf-live-temp"].textContent,"—");
 assert.match(nodes["oaf-home-analysis"].textContent,/No se pudo obtener el modelo meteorológico/);
 assert.match(nodes["oaf-live-air"].textContent,/mala/);
 console.log("OK: portada limpia, AQI, fecha/hora, interpretación dinámica y errores parciales.");
})().catch(err=>{console.error(err);process.exitCode=1;});