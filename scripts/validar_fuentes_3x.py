"""Fase 3X: validar estructura de observaciones publicadas en boletines DZ2.
NO confirma visualmente PDFs, identidad instrumental ni recibe nuevos TXT diarios.
"""
import csv,json,math
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"datos"
MONTHS={"2024-07":"03601SENA-144.pdf","2024-10":"03601SENA-147.pdf","2025-02":"03601SENA-151.pdf"}
STATIONS=["Jayanca (La Viña)","Cayaltí","Reque","Lambayeque","Cueva Blanca"]
PDF_BASE="https://www.senamhi.gob.pe/load/file/"

def main():
    with (DATA/"observaciones_publicadas_dz2_3x.csv").open(encoding="utf-8-sig",newline="") as f:
        rows=list(csv.DictReader(f))
    with (DATA/"fuentes_dz2_3x.csv").open(encoding="utf-8-sig",newline="") as f:
        sources=list(csv.DictReader(f))
    if len(rows)!=15 or len(sources)!=10:raise ValueError("Conteo de documentos inesperado")
    sourceurls=[r["url_oficial"] for r in sources]
    if len(set(sourceurls))!=10 or any(not u.startswith("https://") for u in sourceurls):
        raise ValueError("URLs de fuentes inválidas")
    seen=set();counts=Counter();num=0;trace=0
    for r in rows:
        month,station=r["mes"],r["estacion_referencial_oaf"]
        if month not in MONTHS or station not in STATIONS:
            raise ValueError("Mes o estación no documentada")
        key=(month,station)
        if key in seen:raise ValueError("Observación duplicada: "+repr(key))
        seen.add(key)
        expected=PDF_BASE+MONTHS[month]
        if r["fuente_pdf_oficial"]!=expected or expected not in sourceurls:
            raise ValueError("Enlace oficial no compatible con mes")
        raw=r["precipitacion_reportada_texto"].strip()
        if raw.casefold()=="traza":
            if r["precipitacion_mm_numerica"].strip() or r["valor_no_numerico"]!="traza":
                raise ValueError("Una traza no puede codificarse como 0")
            trace+=1
        else:
            try:
                n=float(raw)
                v=float(r["precipitacion_mm_numerica"])
            except ValueError:
                raise ValueError("Lluvia no numerica sin etiqueta traza")
            if not math.isfinite(v) or v<0 or abs(n-v)>1e-6:
                raise ValueError("Valor mensual incompatible")
            if r["valor_no_numerico"]:
                raise ValueError("Incoherencia en campo texto")
            num+=1
        if r["verificacion_identidad_instrumental"]!="pendiente_codigo_y_coordenadas":
            raise ValueError("No puede declararse identidad verificada")
        if r["estado_serie_diaria"]!="no_recibida_2016_2025":
            raise ValueError("No atribuir descarga no realizada")
        counts[month]+=1
    if set(counts)!=set(MONTHS) or any(c!=5 for c in counts.values()):
        raise ValueError("Faltan estaciones en un mes")
    state={
        "fase":"3X","estado":"transcripciones_estructuralmente_validadas",
        "numero_fuentes":len(sources),"meses_de_boletines":sorted(MONTHS),
        "registros_estacion_mes":len(rows),"registros_numericos":num,"trazas_no_numericas":trace,
        "revision_visual_pdf_pendiente":True,
        "datos_diarios_nuevos_recibidos":0,"meses_nuevos_instrumentales_certificados":0,
        "identidad_con_series_1996_2015_demostrada":False,
        "independencia_PISCOp_CHIRPS_demostrada":False,
        "analisis_directo_con_grillas_modelos_hecho":False,
        "advertencia":"QA de transcripciones NO verifica contenido visual del PDF ni codigo de estacion"
    }
    (DATA/"estado_3x.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    by={(r["mes"],r["estacion_referencial_oaf"]):r for r in rows}
    doc=[
      "# OAF-Lambayeque | Fase 3X: fuentes locales DZ2","",
      "Transcripción EXPLORATORIA de acumulados mensuales observados publicados por SENAMHI DZ2.",
      "No es serie diaria completa ni certificación de continuidad con los TXT 1996–2015.",
      "Revisión visual de páginas PDF pendiente; no se ha obtenido acceso a TXT originales 2016–2025.","",
      "## Datos documentales recuperados (mm/mes; traza = no numérico)","",
      "| Mes | Jayanca | Cayaltí | Reque | Lambayeque | Cueva Blanca | Documento oficial |",
      "|---|---:|---:|---:|---:|---:|---|"
    ]
    for month in sorted(MONTHS):
        values=[by[(month,s)]["precipitacion_reportada_texto"] for s in STATIONS]
        doc.append("| "+month+" | "+" | ".join(values)+" | [PDF SENAMHI]("+PDF_BASE+MONTHS[month]+") |")
    doc.extend(["",
      "Los 15 registros son de SOLO tres meses seleccionados: 14 numéricos y una traza. No sumarlos como si fueran secuencia completa 2016–2025.",
      "La traza de Cayaltí en octubre 2024 no se transforma en cero.",
      "Corroborar código instrumental y correspondencia histórica antes de compararlos con PISCOp/CHIRPS/ERA5.","",
      "## Fuentes locales verificadas","",
      "- Descarga oficial Lambayeque: https://www.senamhi.gob.pe/mapas/descarga-datos/map_hist_data.php?dp=lambayeque",
      "- Guía oficial para TXT diarios y cuenta SENAMHI: https://www.gob.pe/9312-conocer-los-datos-hidrometeorologicos-del-peru-descargar-los-datos-meteorologicos",
      "- Compendio de boletines DZ2: https://www.gob.pe/institucion/senamhi/colecciones/47996-boletin-climatico-regional-dz2",
      "- Reportes meteorológicos DZ2: https://www.gob.pe/institucion/senamhi/colecciones/39450-reportes-meteorologicos-dz2","",
      "## Siguiente paso","",
      "Solicitar las series instrumentales y fichas exactas, cotejar PDF visualmente, registrar periodo de medición y datos faltantes, y no atribuir independencia de los productos sin una prueba documental.","",
      "Código: scripts/validar_fuentes_3x.py; archivos: datos/fuentes_dz2_3x.csv, datos/observaciones_publicadas_dz2_3x.csv y datos/estado_3x.json."
    ])
    (ROOT/"FUENTES_DZ2_3X.md").write_text("\n".join(doc)+"\n",encoding="utf-8")
    print(json.dumps(state,ensure_ascii=False,indent=2),flush=True)
if __name__=="__main__":main()
