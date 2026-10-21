/** Prueba sin dependencias: fotografías locales, externas y fallback del visor OAF. */
const fs=require("node:fs"),vm=require("node:vm"),assert=require("node:assert/strict"),path=require("node:path");
const root=path.resolve(__dirname,"..");
const js=fs.readFileSync(path.join(root,"assets/oaf-galeria-mecanismos-2026.js"),"utf8");
function makeNode(tag){
 const node={tag,children:[],dataset:{},classList:{classes:new Set(),add(c){this.classes.add(c)}},
  append(...parts){this.children.push(...parts)},prepend(...parts){this.children.unshift(...parts)},
  removeAttribute(name){delete this[name]},setAttribute(name,value){this[name]=value},
  remove(){this.removed=true},querySelector(name){return this.children.find(x=>x.tag===name)||null}};
 return node;
}
const doc={readyState:"loading",createElement:makeNode,getElementById(){return null},addEventListener(){}};
const testCode=js.replace(/\}\)\(\);\s*$/,"return {photographic,validLocalPhoto,validPhoto};})();");
assert.notEqual(testCode,js,"No se puede extraer el renderizador para probarlo");
const suite=vm.runInNewContext(testCode,{document:doc,console,Promise,MutationObserver:class {}});
const gallery=JSON.parse(fs.readFileSync(path.join(root,"datos/galeria_sanidad_2026.json"),"utf8"));
let local=0,remote=0;
for(const [id,record] of Object.entries(gallery.organismos)){
 assert.ok(record.source,id+" sin fuente científica");
 const figure=suite.photographic(record,"modelo");
 const img=figure.children.find(x=>x.tag==="img");
 assert.ok(img,id+": debe mostrar imagen o recurso local");
 assert.equal(img.src,record.url,id+": ruta incorrecta");
 if(record.url.startsWith("assets/")){
  local++;
  assert.ok(suite.validLocalPhoto(record.url),id+": el visor rechaza la ruta local");
  assert.ok(fs.existsSync(path.join(root,record.url)),id+": archivo local ausente");
 }else{remote++;assert.ok(suite.validPhoto(record.url),id+": URL malformada")}
 assert.equal(typeof img.onerror,"function",id+": sin sustitución ante error");
}
const figure=suite.photographic({url:"https://ejemplo.org/imagen-inexistente.jpg",caption:"Prueba",source:"https://ejemplo.org/fuente"},"manejo");
const img=figure.children.find(x=>x.tag==="img");
img.onerror();
assert.equal(img.src,"assets/oaf-sin-foto-patogeno.svg","Fallback incorrecto");
const fallback=suite.photographic(null,"producto");
assert.equal(fallback.children.find(x=>x.tag==="img").src,"assets/oaf-sin-foto-envase.svg");
assert.equal(suite.validPhoto("javascript:alert(1)"),false);
console.log("Sanidad OAF: "+local+" fotos locales, "+remote+" externas, fallback OK");
