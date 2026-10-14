"""OAF-Lambayeque / Fase 3Y: ampliar tabla documental DZ2 de forma auditable.

Lee la Fase 3X (no la modifica), anexa meses 2024-09, 2025-01,
2025-03 y 2025-06 recuperados de tablas PP obs de boletines DZ2.
No añade datos diarios ni certifica que los códigos de estación coincidan
con la serie histórica 1996-2015. No se publican meses no verificables.
'Traza' permanece literal con campo numérico vacío; nunca 0 mm.
"""
from __future__ import annotations
import csv
import json
import math
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"datos"
STATIONS=["Jayanca (La Viña)","Cayaltí","Reque","Lambayeque","Cueva Blanca"]
PDF_ROOT="https://www.senamhi.gob.pe/load/file/"
YEAR_COLLECTION="https://www.gob.pe/institucion/senamhi/informes-publicaciones/6490504-boletin-climatico-regional-dz2-2025"
# Orden idéntico al de STATIONS. Los valores proceden de la tabla de
# precipitación OBSERVADA (no PP climática ni anomalías) de cada boletín.
ADDED={
 "2024-09":("03601SENA-146.pdf",["2.3","Traza","0","0","30.1"]),
 "2025-01":("03601SENA-150.pdf",["12.4","19","9.5","4.5","117.2"]),
 "2025-03":("03601SENA-152.pdf",["33.5","6.55","3.9","11.2","205.1"]),
 "2025-06":("03601SENA-155.pdf",["0","1.4","0.31","0","48.7"])
}
ORIGINAL={
 "2024-07":"03601SENA-144.pdf",
 "2024-10":"03601SENA-147.pdf",
 "2025-02":"03601SENA-151.pdf"
}
LINKS={**ORIGINAL,**{m:src[0] for m,src in ADDED.items()}}
EXPECTED_MONTHS=set(LINKS)
EXPECTED_YEARS=set(range(2016,2026))

def rows_csv(path):
    with path.open("r",encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def export_csv(path,rows,fields):
    with path.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

def main():
    previous=rows_csv(DATA/"observaciones_publicadas_dz2_3x.csv")
    if len(previous)!=15:
        raise ValueError("Se requieren 15 filas originales de 3X intactas")
    fields=list(previous[0].keys())
    original_snapshot={ (r["mes"],r["estacion_referencial_oaf"]):dict(r) for r in previous }
    if len(original_snapshot)!=len(previous):
        raise ValueError("Datos originales duplicados")
    rows=[dict(r) for r in previous]
    for month,(filename,values) in ADDED.items():
        if len(values)!=len(STATIONS):raise ValueError("Valores estación no emparejados")
        for station,raw in zip(STATIONS,values):
            trace=raw.casefold()=="traza"
            rows.append({
             "mes":month,"estacion_referencial_oaf":station,
             "nombre_en_boletin":"Jayanca" if station=="Jayanca (La Viña)" else station,
             "precipitacion_reportada_texto":raw,
             "precipitacion_mm_numerica":"" if trace else raw,
             "valor_no_numerico":"traza" if trace else "",
             "fuente_pdf_oficial":PDF_ROOT+filename,
             "procedencia":"tabla_precipitacion_observada_boletin_DZ2",
             "verificacion_identidad_instrumental":"pendiente_codigo_y_coordenadas",
             "estado_serie_diaria":"no_recibida_2016_2025"
            })
    rows.sort(key=lambda r:(r["mes"],STATIONS.index(r["estacion_referencial_oaf"])))
    counts=Counter()
    numeric=trace_count=zero=0
    for r in rows:
        month=r["mes"]
        if month not in LINKS:raise ValueError("Mes sin enlace documental")
        if r["fuente_pdf_oficial"]!=PDF_ROOT+LINKS[month]:
            raise ValueError("No coincide URL PDF con el mes")
        if r["estacion_referencial_oaf"] not in STATIONS:
            raise ValueError("Estación ajena al catálogo")
        if r["verificacion_identidad_instrumental"]!="pendiente_codigo_y_coordenadas":
            raise ValueError("Identidad instrumental no debe cambiarse")
        if r["estado_serie_diaria"]!="no_recibida_2016_2025":
            raise ValueError("No atribuir archivos diarios inexistentes")
        raw=r["precipitacion_reportada_texto"].strip()
        if raw.casefold()=="traza":
            if r["precipitacion_mm_numerica"] or r["valor_no_numerico"]!="traza":
                raise ValueError("Traza no equivale a cero")
            trace_count+=1
        else:
            try:value=float(raw);measured=float(r["precipitacion_mm_numerica"])
            except ValueError:raise ValueError("Valor no numérico sin marcar")
            if not math.isfinite(value) or value<0 or abs(value-measured)>1e-7:
                raise ValueError("Lluvia observada ilegal o magnitud cambiada")
            if r["valor_no_numerico"]:raise ValueError("Anotación inválida")
            numeric+=1
            zero+=int(value==0)
        counts[month]+=1
        yyyy,mm=map(int,month.split("-"))
        if yyyy not in EXPECTED_YEARS or not 1<=mm<=12:
            raise ValueError("Mes fuera del periodo instrumental objetivo")
    if set(counts)!=EXPECTED_MONTHS or any(v!=5 for v in counts.values()):
        raise ValueError("No hay exactamente cinco estaciones por mes")
    if len(rows)!=35 or numeric!=33 or trace_count!=2:
        raise ValueError("Conteos inesperados: "+repr((len(rows),numeric,trace_count)))
    for k,r in original_snapshot.items():
        restored=next(x for x in rows if (x["mes"],x["estacion_referencial_oaf"])==k)
        if restored!=r:
            raise ValueError("Las 15 observaciones originales se modificaron")
    export_csv(DATA/"observaciones_documentales_dz2_3y.csv",rows,fields)
    years=[]
    for month in range(1,13):
        date=f"2025-{month:02d}"
        pdf=PDF_ROOT+LINKS[date] if date in LINKS else ""
        years.append({
            "mes":date,"estado":"transcrito_pendiente_de_cotejo_visual" if date in LINKS else "boletin_en_coleccion_pendiente_de_extraccion",
            "filas_estacion_mes":counts.get(date,0),
            "fuente_pdf_senamhi":pdf,
            "coleccion_oficial_2025":YEAR_COLLECTION,
            "control_identidad_instrumental":"pendiente"
        })
    export_csv(DATA/"matriz_boletines_2025_3y.csv",years,list(years[0]))
    status={
        "fase":"3Y","estado":"ampliacion_documental_validada_estructuralmente",
        "meses_documentales_acumulados":len(counts),
        "meses_nuevos_fase_3Y":len(ADDED),
        "meses_2025_documentados":sum(1 for d in counts if d.startswith("2025-")),
        "meses_2025_disponibles_en_indice_oficial":12,
        "filas_estacion_mes_documentales":len(rows),
        "filas_numericas":numeric,"filas_traza_no_numericas":trace_count,
        "filas_lluvia_cero_valido":zero,
        "pdf_descargados_y_revisados_visualmente":0,
        "fuentes_consultadas_para_ampliacion":"tablas PP observada en texto indexado de PDFs oficiales",
        "identidad_instrumental_1996_2015_confirmada":False,
        "meses_diarios_nuevos_2016_2025_certificados":0,
        "comparacion_modelos_2025_efectuada":False,
        "serie_continua_2025":False,
        "faltan_meses_documentales_2025":12-sum(1 for d in counts if d.startswith("2025-")),
        "limitacion":"Los datos son transcripciones documentales preliminares; falta cotejo visual de PDFs e identidad instrumental."
    }
    (DATA/"estado_3y.json").write_text(json.dumps(status,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    header=["# OAF-Lambayeque | Fase 3Y — Ampliación del registro documental de lluvia DZ2","",
      "> **Solo evidencia documental preliminar**, NO serie diaria y NO independencia demostrada.",
      "> Valores recuperados de tablas PP observada indexadas de boletines SENAMHI; cotejo visual PDF pendiente.",
      "> Las estaciones con el mismo nombre no se presumen instrumentos históricos idénticos.","",
      "## Avance de cobertura","",
      f"- {len(counts)} meses documentales (2024–2025), {len(rows)} registros estación-mes.",
      f"- {numeric} valores numéricos, {trace_count} anotaciones Traza y {zero} ceros observados reales.",
      f"- Año 2025: {status['meses_2025_documentados']} meses con tabla transcrita de 12 boletines oficiales publicados.",
      "- **0 meses diarios nuevos certificados**; ningún valor se ha incorporado a los 1 109 meses 1996–2015.","",
      "## Acumulados observados (mm/mes) según boletines publicados","",
      "| Mes | Jayanca | Cayaltí | Reque | Lambayeque | Cueva Blanca | Fuente oficial |",
      "|---|---:|---:|---:|---:|---:|---|"]
    for month in sorted(counts):
        this={r["estacion_referencial_oaf"]:r for r in rows if r["mes"]==month}
        vals=[this[station]["precipitacion_reportada_texto"] for station in STATIONS]
        header.append("| "+month+" | "+" | ".join(vals)+" | [PDF]("+PDF_ROOT+LINKS[month]+") |")
    header+=["","## Cobertura de la colección 2025","",
       "La página institucional enumera los doce boletines mensuales de 2025:",
       YEAR_COLLECTION,
       "Los meses no transcritos no se completaron por interpolación, comparación con modelos ni suposición de cero.",
       "El hecho de figurar el PDF no garantiza por sí solo que la tabla específica esté completa o contenga estas mismas estaciones.","",
       "## Limitaciones técnicas","",
       "- «Traza» es texto, no 0 mm; se conservaron dos casos.",
       "- Estas observaciones no permiten probar la continuidad de estación entre 1996–2015 y 2024–2025.",
       "- La extracción indexada del PDF no reemplaza la revisión de imagen/tabla por página; esa verificación se registra como pendiente.",
       "- No se calculó precipitación anual 2025, ni error frente a CHIRPS/PISCOp/ERA5 en 2025.",
       "- Para crear una serie mensual apta para validación se requieren los registros diarios autorizados, sus códigos y controles SENAMHI, o un protocolo independiente específico para acumulados oficiales.",
       "- Las 15 filas previas de la Fase 3X permanecen idénticas.","",
       "## Reproducibilidad","",
       "Datos: datos/observaciones_documentales_dz2_3y.csv",
       "Matriz de boletines: datos/matriz_boletines_2025_3y.csv",
       "Estado: datos/estado_3y.json",
       "Código y criterios de preservación: scripts/actualizar_boletines_3y.py",
       "Fuentes originales: datos/observaciones_publicadas_dz2_3x.csv y portal oficial SENAMHI DZ2.",""]
    (ROOT/"BOLETINES_DZ2_3Y.md").write_text("\n".join(header)+"\n",encoding="utf-8")
    print(json.dumps(status,ensure_ascii=False),flush=True)

if __name__=="__main__":
    main()
