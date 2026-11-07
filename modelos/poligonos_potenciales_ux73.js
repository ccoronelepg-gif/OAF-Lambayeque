/* OAF UX73 · Cobertura cartográfica de indicadores mediante polígonos de proximidad.
 * NO ES un modelo de distribución de plagas ni de incidencia o riesgo validado.
 * Polígonos geométricos = mosaico regular de celdas completamente interiores
 * al contorno simplificado; cada celda se asigna a la muestra más cercana.
 */
(function(root){"use strict";
const rad=Math.PI/180;
function distanceKm(a,b){
 const dlat=(b.lat-a.lat)*rad,dlon=(b.lon-a.lon)*rad;
 const h=Math.sin(dlat/2)**2+Math.cos(a.lat*rad)*Math.cos(b.lat*rad)*Math.sin(dlon/2)**2;
 return 12742*Math.asin(Math.min(1,Math.sqrt(h)));
}
function ringsValid(rings){
 return Array.isArray(rings)&&rings.length&&rings.every(r=>Array.isArray(r)&&r.length>=4&&r.every(p=>Array.isArray(p)&&p.length>=2&&Number.isFinite(p[0])&&Number.isFinite(p[1])));
}
function zones(rings,samples,opts={}){
 if(!ringsValid(rings))throw Error("No hay un contorno válido para generar polígonos");
 if(!Array.isArray(samples)||!samples.length)throw Error("No hay estaciones/puntos modelados");
 const step=opts.step||.055,maxKm=opts.maxKm||28;
 if(!(step>=.02&&step<=.15&&maxKm>=5&&maxKm<=60))throw Error("Resolución o distancia no admitida");
 const inside=opts.inside||((lon,lat)=>{let val=false;for(const ring of rings){let hit=false;
  for(let i=0,j=ring.length-1;i<ring.length;j=i++){
   const a=ring[i],b=ring[j];
   if((a[1]>lat)!==(b[1]>lat)&&lon<(b[0]-a[0])*(lat-a[1])/(b[1]-a[1])+a[0])hit=!hit;
  }if(hit)val=true;
 }return val});
 const pts=rings.flat();
 const west=Math.min(...pts.map(p=>p[0])),east=Math.max(...pts.map(p=>p[0]));
 const south=Math.min(...pts.map(p=>p[1])),north=Math.max(...pts.map(p=>p[1]));
 const countX=Math.ceil((east-west)/step),countY=Math.ceil((north-south)/step);
 const grid=[];
 const validSquare=(x0,y0,x1,y1)=>{
  // Dejar sin mapear celdas costeras / limítrofes: geometrías nunca fuera
  // del límite referencial. Sin extrapolar a ubicaciones no muestreadas.
  const epsilon=1e-7;
  return [[x0+epsilon,y0+epsilon],[x1-epsilon,y0+epsilon],[x1-epsilon,y1-epsilon],[x0+epsilon,y1-epsilon],
   [(x0+x1)/2,(y0+y1)/2]].every(p=>inside(p[0],p[1]));
 };
 for(let j=0;j<countY;j++){
  const y0=south+j*step,y1=Math.min(north,y0+step);
  let row=[];
  for(let i=0;i<countX;i++){
   const x0=west+i*step,x1=Math.min(east,x0+step),c={lon:(x0+x1)/2,lat:(y0+y1)/2};
   if(!validSquare(x0,y0,x1,y1)){row.push(null);continue}
   let point=null,nearest=Infinity;
   for(const sample of samples){
    const d=distanceKm(c,sample);
    if(d<nearest){point=sample;nearest=d}
   }
   row.push(nearest<=maxKm?{id:point.id,x0,x1,y0,y1,distanceKm:nearest}:null);
  }
  // Unir cuadrados contiguos de igual modelo por fila: reduce nodos SVG
  for(let i=0;i<row.length;){
   const current=row[i];if(!current){i++;continue}
   let end=i+1,far=current.distanceKm;
   while(end<row.length&&row[end]?.id===current.id&&Math.abs(row[end].x0-row[end-1].x1)<1e-7){
    far=Math.max(far,row[end].distanceKm);end++;
   }
   const x0=current.x0,x1=row[end-1].x1;
   grid.push({id:"Z"+String(grid.length+1).padStart(3,"0"),pointId:current.id,
    representativeDistanceKm:+far.toFixed(2),
    geometry:{type:"Polygon",coordinates:[[[x0,y0],[x1,y0],[x1,y1],[x0,y1],[x0,y0]].map(p=>p.map(v=>+v.toFixed(6)))]}});
   i=end;
  }
 }
 if(!grid.length)throw Error("Sin polígonos completamente interiores a la región para esta resolución");
 return grid;
}
function geometryCheck(zones,rings,inside){
 const check=inside||((lon,lat)=>{let inArea=false;for(const ring of rings){let hit=false;
  for(let i=0,j=ring.length-1;i<ring.length;j=i++){
   const a=ring[i],b=ring[j];
   if((a[1]>lat)!==(b[1]>lat)&&lon<(b[0]-a[0])*(lat-a[1])/(b[1]-a[1])+a[0])hit=!hit;
  }if(hit)inArea=true;
 }return inArea});
 return zones.every(z=>{
  const ring=z.geometry?.coordinates?.[0],mid=ring&&[(ring[0][0]+ring[2][0])/2,(ring[0][1]+ring[2][1])/2];
  return ring?.length===5&&mid&&check(mid[0],mid[1])&&z.representativeDistanceKm<=60;
 });
}
root.OAFPotentialPolygons={zones,distanceKm,geometryCheck,version:"UX73"};
})(typeof window!=="undefined"?window:globalThis);
