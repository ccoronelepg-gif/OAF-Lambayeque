/* OAF App UX20: PWA installability, parity and scientific cache policy. */
const fs=require("node:fs"),path=require("node:path"),assert=require("node:assert/strict");
const root=path.resolve(__dirname,"..");
const content=p=>fs.readFileSync(path.join(root,p),"utf8");
const m=JSON.parse(content("manifest.webmanifest"));
const html=content("index.html"),sw=content("sw.js");
for(const key of ["name","short_name","start_url","scope","display","icons"])assert.ok(m[key],"Falta campo: "+key);
assert.equal(m.start_url,"./?app=pwa#inicio");
assert.equal(m.scope,"./");
assert.equal(m.display,"standalone");
assert.equal(m.prefer_related_applications,false);
assert.equal(m.lang,"es-PE");
const png=m.icons.filter(x=>x.type==="image/png");
assert.ok(png.some(x=>x.sizes==="192x192"&&x.purpose==="any"));
assert.ok(png.some(x=>x.sizes==="512x512"&&x.purpose==="any"));
assert.ok(png.some(x=>x.sizes==="512x512"&&x.purpose==="maskable"));
for(const icon of png){
 const file=path.join(root,icon.src),buf=fs.readFileSync(file);
 assert.ok(buf.subarray(0,8).equals(Buffer.from("89504e470d0a1a0a","hex")),"No es PNG: "+icon.src);
 const [w,h]=[buf.readUInt32BE(16),buf.readUInt32BE(20)];
 const expected=Number(icon.sizes.split("x")[0]);
 assert.deepEqual([w,h],[expected,expected],"Dimensiones incorrectas: "+icon.src);
}
assert.ok(fs.existsSync(path.join(root,"assets/oaf-apple-touch-icon-180.png")));
for(const route of ["inicio","clima","autor","cultivos","nino","verificaciones"]){
 assert.ok(html.includes('data-page="'+route+'"'),"Falta contenido: "+route);
}
assert.match(html,/rel="manifest" href="manifest\.webmanifest/);
assert.match(html,/rel="apple-touch-icon"/);
assert.match(html,/assets\/oaf-pwa\.js\?v=/);
assert.match(html,/assets\/oaf-pwa\.css\?v=/);
assert.match(sw,/isScientificData/);
assert.match(sw,/if\(isScientificData\(url\)\)return;/);
assert.match(sw,/if\(req\.mode==="navigate"\)/);
assert.match(sw,/SKIP_WAITING/);
assert.ok(!sw.includes("self.addEventListener(\"push\""),"Se añadieron avisos automáticos sin autorización");
new Function(content("assets/oaf-pwa.js"));
new Function(sw);
assert.ok(content("offline.html").includes("no se actualizan")||content("offline.html").includes("necesitas Internet"));
console.log("OAF App PWA: 6 pestañas idénticas, PNG 192/512, máscara, iOS y seguridad del caché OK");
