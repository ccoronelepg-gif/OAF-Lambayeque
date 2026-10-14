"""Fase 3W: comprobar TODAS las estaciones GBON/RBON por departamento y distancia.
No calcula lluvia, no certifica equivalencia ni publica registros horarios individuales.
"""
import collections,csv,io,json
from pathlib import Path
import requests
from auditar_gbon_rbon_3w import URL,normal,number,distkm,POINTS,csvwrite

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"datos"

def main():
    with requests.get(URL,timeout=(20,160),headers={"User-Agent":"Mozilla/5.0 OAF-Lambayeque/3W Nationwide Metadata"}) as r:
        r.raise_for_status()
        reader=csv.DictReader(io.StringIO(r.content.decode("utf-8-sig",errors="replace"),newline=""))
        if reader.fieldnames is None:raise ValueError("CSV sin cabecera")
        records={}
        missingcoords=0
        rows=0
        for x in reader:
            rows+=1
            sid=str(x.get("ID") or "").strip()
            name=str(x.get("ESTACION") or "").strip()
            dept=str(x.get("DEPARTAMENTO") or "").strip()
            lat=number(x.get("LATITUD"));lon=number(x.get("LONGITUD"))
            if lat is None or lon is None or not(-90<=lat<=90 and -180<=lon<=180):
                missingcoords+=1;continue
            nearest,ref=min((distkm(lat,lon,*coord),label) for label,coord in POINTS.items())
            key=(sid,name,lat,lon,dept)
            if key not in records:
                records[key]={"id":sid,"nombre":name,"departamento":dept,
                   "latitud":lat,"longitud":lon,"red":str(x.get("RED") or ""),
                   "ubicacion_oaf_mas_cercana":ref,"distancia_oaf_min_km":round(nearest,2),
                   "filas_en_csv":0}
            records[key]["filas_en_csv"]+=1
    allstations=sorted(records.values(),key=lambda x:(x["distancia_oaf_min_km"],x["nombre"]))
    departments=collections.Counter(x["departamento"] for x in allstations)
    closest=allstations[:12]
    in_lambayeque=[x for x in allstations if normal(x["departamento"])=="lambayeque"]
    near=[x for x in allstations if x["distancia_oaf_min_km"]<=160]
    fields=["id","nombre","departamento","latitud","longitud","red",
        "ubicacion_oaf_mas_cercana","distancia_oaf_min_km","filas_en_csv"]
    csvwrite("inventario_nacional_gbon_3w.csv",allstations,fields)
    report={
        "fase":"3W","tipo":"verificacion_geografica_nacional",
        "filas_originales":rows,
        "filas_sin_coordenadas_numericas_validas":missingcoords,
        "estaciones_o_identificadores_unicos":len(allstations),
        "departamentos_en_catalogo":dict(departments),
        "estaciones_con_departamento_declarado_lambayeque":len(in_lambayeque),
        "estaciones_a_160km_de_puntos_oaf":len(near),
        "doce_estaciones_mas_cercanas":closest,
        "no_equivale_a_validacion_independiente":True,
        "las_coordenadas_oaf_son_provisionales":True,
        "relevancia":"La red contenida en ESTE CSV, no toda la red SENAMHI ni todas sus estaciones operativas."
    }
    (DATA/"estado_geografia_3w.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
if __name__=="__main__":
    main()
