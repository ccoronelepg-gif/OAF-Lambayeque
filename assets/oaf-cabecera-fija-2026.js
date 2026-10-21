(function(){
'use strict';
function init(){
 const header=document.querySelector('body > header');
 if(!header||header.dataset.oafFixed12)return;
 header.dataset.oafFixed12='1';
 const refresh=()=>{
  const height=Math.ceil(header.getBoundingClientRect().height);
  if(height>0&&height<450)document.documentElement.style.setProperty('--oaf-header-fijo-altura',height+'px');
 };
 refresh();
 if(typeof ResizeObserver!=='undefined')new ResizeObserver(refresh).observe(header);
 window.addEventListener('resize',refresh,{passive:true});
 document.fonts?.ready?.then(refresh).catch(()=>{});
 const menu=document.querySelector('#oaf-primary-nav');
 if(menu)menu.addEventListener('click',event=>{
  if(event.target.closest('a[href^="#"]'))menu.classList.remove('oaf-menu-open');
 });
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();