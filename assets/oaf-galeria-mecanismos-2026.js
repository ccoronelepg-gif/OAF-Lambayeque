(function(){
'use strict';
const $=id=>document.getElementById(id);
const create=(tag,cls,txt)=>{const el=document.createElement(tag);if(cls)el.className=cls;if(txt!==undefined)el.textContent=String(txt);return el};
const validLink=x=>typeof x==='string'&&/^https:\/\//.test(x);
const a=(title,url)=>{const node=create('a',null,title);if(validLink(url)){node.href=url;node.target='_blank';node.rel='noopener noreferrer'}return node};
let gallery=null,cat=null;
function photographic(media,scope){
 const figure=create('figure','oaf-ux12-photo '+(scope==='producto'?'oaf-ux12-envase':'oaf-ux12-fauna'));
 if(!media||!validLink(media.url))return figure;
 const img=create('img');img.src=media.url;img.alt=media.caption||'Fotografía real de referencia';img.loading=scope==='modelo'?'eager':'lazy';img.decoding='async';
 const caption=create('figcaption');caption.append(create('span',null,media.caption||'Fotografía documentada'));
 if(media.exact===false)caption.append(create('small',null,'Fotografía ilustrativa de una especie o síntoma; no confirma diagnóstico.'));
 if(validLink(media.source))caption.append(a('Crédito: '+(media.credit||'Fuente técnica')+' ↗',media.source));
 img.onerror=()=>{img.remove();figure.classList.add('oaf-ux12-photo-error');const msg=create('div','oaf-ux12-unavailable');
const emblem=create('span','oaf-ux12-unavailable-icon',scope==='producto'?'▣':'✿');
msg.append(emblem,create('span',null,'Fotografía externa temporalmente no disponible. Abre la ficha original para identificar el organismo o el envase.'));
figure.prepend(msg)};
 figure.append(img,caption);return figure;
}
function keyFor(n){
 n=(n||'').toLowerCase();
 if(n.includes('gf-120'))return 'gf-120';
 if(n.includes('amistar')&&n.includes('top'))return 'amistar-top';
 for(const [term,key] of [['amistar','amistar'],['scholar','scholar'],['bio-splent','biosplent'],['akron','akron'],['wonder','wonder'],['vertimec','vertimec'],['luna experience','luna'],['serenade','serenade'],['switch','switch'],['aliette','aliette'],['engeo','engeo'],['score','score'],['quadris','quadris']])if(n.includes(term))return key;
 return '';
}
function pestPhoto(area,id,scope){
 if(!area||!gallery||!id||!gallery.organismos[id])return;
 area.replaceChildren(photographic(gallery.organismos[id],scope));area.classList.add('oaf-ux12-has-photo');
}
function productCard(card,p){
 const wrap=create('div','oaf-ux12-product-layout');const photo=gallery?.productos?.[keyFor(p.nombre)];
 if(photo)wrap.append(photographic(photo,'producto'));
 const info=create('div','oaf-ux12-product-info');
 info.append(create('span','oaf-ux11-badge '+(p.tipo.startsWith('Biol')?'':'amber'),p.tipo));
 info.append(create('strong',null,p.nombre));
 info.append(create('small',null,'Ingrediente activo: '+p.ingrediente));
 if(p.fabricante)info.append(create('small','oaf-ux12-laboratorio','Fabricante o respaldo: '+p.fabricante));
 if(p.grupo)info.append(create('span','oaf-ux12-group',p.grupo));
 const action=create('div','oaf-ux12-mechanism');
 action.append(create('b',null,'¿Cómo actúa sobre el insecto, ácaro o patógeno?'),create('p',null,p.mecanismo||p.modo||'Consultar ficha técnica'));
 info.append(action);
 if(p.registro)info.append(create('p','oaf-ux12-registro',p.registro));
 if(p.nota)info.append(create('p',null,p.nota));
 const links=create('div','oaf-ux12-product-links');
 if(validLink(p.fuente_laboratorio))links.append(a('Ver ficha del laboratorio ↗',p.fuente_laboratorio));
 if(validLink(p.fuente)&&p.fuente!==p.fuente_laboratorio)links.append(a('Documentación complementaria ↗',p.fuente));
 if(!photo)info.append(create('small','oaf-ux12-image-note','Sin fotografía de envase verificada; no se sustituye por otro producto.'));
 info.append(links);wrap.append(info);card.replaceChildren(wrap);card.dataset.oafPhoto12='1';
}
function render(){
 if(!gallery||!cat)return;
 const mid=$('oaf-sm-patogeno')?.value, gid=$('oaf-mg-patogeno')?.value;
 pestPhoto($('oaf-sm-ilustracion'),mid,'modelo');pestPhoto($('oaf-mg-foto'),gid,'manejo');
 const r=cat.organismos.find(x=>x.id===gid), cards=$('oaf-mg-productos')?.querySelectorAll(':scope > .oaf-ux11-product');
 if(!r||!cards)return;
 r.productos.forEach((p,i)=>{if(cards[i]&&cards[i].dataset.oafPhoto12!=='1')productCard(cards[i],p)});
}
async function init(){
 const list=$('oaf-mg-productos');if(!list||list.dataset.oafGallery12)return;list.dataset.oafGallery12='1';
 new MutationObserver(()=>render()).observe(list,{childList:true});
 document.addEventListener('change',event=>{
  const id=event.target?.id||'';
  if(id.startsWith('oaf-sm-')||id.startsWith('oaf-mg-'))queueMicrotask(render);
 });
 try{
  const [c,g]=await Promise.all([
   fetch('datos/sanidad_agroexportadora_2026.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('catálogo '+r.status);return r.json()}),
   fetch('datos/galeria_sanidad_2026.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('galería '+r.status);return r.json()})
  ]);
  if(!Array.isArray(c.organismos)||c.organismos.length!==23)throw Error('catálogo sanitario incompleto');
  cat=c;gallery=g;render();
 }catch(e){console.warn('OAF: fotos y mecanismos no disponibles',e)}
}
document.addEventListener('oaf:ux11-ready',init);
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();