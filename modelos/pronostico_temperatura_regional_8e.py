#!/usr/bin/env python3
"""OAF Fase 8E — honest prospective experimental Lambayeque monthly temperature.
A saved issue is never updated. Only temperature; rain/radiation 8D not skilled.
Fixed training: target month <=2022-12, seasonal means 1996-2022; Ridge alpha20.
Predictors: local monthly ERA5-Land air temperature anomaly at t; SST Niño1+2
ERSSTv5 t (OAF-adjusted 1991-2020); T300 GODAS at t-1.
Anomalies in deg C; results convert to target-month 2m air temperature.
Forecast month t+1 computed after t closes is intramonth, not pre-month.
Verification: ERA5-Land (NOT SENAMHI), >=10th of month after target, no
retroactive changes to original issuances. No ENSO/ENFEN warnings.
"""
import argparse
import calendar
import csv
import hashlib
import json
import math
import statistics as st
import sys
import time
from collections import defaultdict
from datetime import date,datetime,timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from zoneinfo import ZoneInfo

from benchmark_atmosferico_8b import fit,predict,shift
LOCAL=ZoneInfo("America/Lima")
DIR=Path("datos")
SOURCE_LOCAL=DIR/"lambayeque_mensual_era5_8d.csv"
SOURCE_SST=DIR/"noaa_ncei_ersstv5_nino12_rebase_1991_2020.csv"
SOURCE_T300=DIR/"noaa_pmel_t300_8c.csv"
ISSUES=DIR/"pronosticos_temperatura_regional_8e"
REPORT=DIR/"verificacion_temperatura_regional_8e.json"
ROWS=DIR/"verificacion_temperatura_regional_8e.csv"
TRAIN_LIMIT="2022-12"
ALPHA=20.
SITES={"Chiclayo":(-6.77140,-79.84090),"Jayanca":(-6.39278,-79.82280),
       "Motupe":(-6.15083,-79.71420),"Olmos":(-5.98825,-79.74723)}
CSV_FIELDS=["emision_utc","mes_origen","mes_objetivo","localidad","horizonte_meses",
            "tipo_emision","pronostico_local_c","pronostico_nino_t300_c",
            "observacion_era5_land_c","error_local_c","error_nino_t300_c"]


def finite(x):
    return type(x) in (float,int) and math.isfinite(x)


def get_monthly(path,required_key):
    with path.open(encoding="utf-8",newline="") as stream:
        reader=csv.DictReader(stream)
        if not reader.fieldnames or not {"mes",required_key}<=set(reader.fieldnames):
            raise ValueError("El esquema mensual no corresponde a "+str(path))
        rows={}
        for row in reader:
            month=row["mes"];val=float(row[required_key])
            if month in rows or not finite(val):
                raise ValueError("Dato oceánico mensual inválido/duplicado "+month)
            rows[month]=val
    return rows


def local_records():
    with SOURCE_LOCAL.open(encoding="utf-8",newline="") as stream:
        reader=csv.DictReader(stream)
        if not reader.fieldnames or not {"localidad","mes","temperatura_c"}<=set(reader.fieldnames):
            raise ValueError("El registro regional 8D cambió de estructura")
        by={city:{} for city in SITES}
        for row in reader:
            city=row["localidad"];month=row["mes"]
            if city not in SITES or month in by[city]:
                raise ValueError("Ciudad no reconocida o mes regional duplicado")
            val=float(row["temperatura_c"])
            if not finite(val) or not -20<val<50:
                raise ValueError("Temperatura regional inexistente/inverosímil")
            by[city][month]=val
    months=[sorted(values) for values in by.values()]
    if not all(len(m)>=369 and m[0]=="1996-01" for m in months):
        raise ValueError("No existen las series regionales históricas completas")
    if any(m!=months[0] for m in months[1:]):
        raise ValueError("Las ciudades no tienen meses idénticos")
    for a,b in zip(months[0],months[0][1:]):
        if shift(a,1)!=b:raise ValueError("Hay meses regionales sin observación")
    return by


def full_months_between(start,end):
    result=[];current=start
    while current<=end:
        result.append(current);current=shift(current,1)
    return result


def fetch_monthly_era5_land(start,end,month_cities):
    """Four coords, one request, strict full calendar months; no silent fills."""
    cities=list(SITES)
    params={"latitude":",".join(str(SITES[c][0]) for c in cities),
            "longitude":",".join(str(SITES[c][1]) for c in cities),
            "start_date":start+"-01",
            "end_date":end+"-"+str(calendar.monthrange(*map(int,end.split("-")))[1]).zfill(2),
            "daily":"temperature_2m_mean","models":"era5_land",
            "timezone":"America/Lima"}
    url="https://archive-api.open-meteo.com/v1/archive?"+urlencode(params)
    last_error=None
    for retry in range(3):
        try:
            with urlopen(Request(url,headers={"User-Agent":"OAF-Lambayeque-temperature-vintage-8E/1.0"}),timeout=110) as res:
                raw=json.load(res)
            if not isinstance(raw,list) or len(raw)!=4:
                raise ValueError("El reanálisis no devolvió cuatro cuadrículas")
            expected=full_months_between(start,end)
            output={}
            for city,payload in zip(cities,raw):
                if payload.get("error") or payload.get("timezone")!="America/Lima":
                    raise ValueError("Datos ERA5-Land no íntegros para "+city)
                loc_lat,loc_lon=SITES[city]
                if (abs(float(payload.get("latitude",999))-loc_lat)>1 or
                    abs(float(payload.get("longitude",999))-loc_lon)>1):
                    raise ValueError("Celda ERA5-Land fuera del área de "+city)
                if payload.get("daily_units",{}).get("temperature_2m_mean")!="°C":
                    raise ValueError("Unidad no reconocida para temperatura diaria")
                stamps=payload.get("daily",{}).get("time",[])
                values=payload.get("daily",{}).get("temperature_2m_mean",[])
                if len(stamps)!=len(values) or len(stamps)!=len(set(stamps)):
                    raise ValueError("Tiempos diarios ausentes o duplicados")
                groups=defaultdict(list)
                for stamp,value in zip(stamps,values):
                    if not finite(value) or not -20<value<55:
                        raise ValueError("Temperatura ERA5-Land faltante")
                    groups[stamp[:7]].append((stamp,value))
                summarized={}
                for month in expected:
                    yyyy,mm=map(int,month.split("-"))
                    n=calendar.monthrange(yyyy,mm)[1]
                    rows=sorted(groups.get(month,[]))
                    if len(rows)!=n or [x for x,_ in rows]!=[
                       f"{month}-{day:02d}" for day in range(1,n+1)]:
                        raise ValueError("ERA5-Land no completó "+month+" en "+city)
                    summarized[month]=st.mean(v for _,v in rows)
                output[city]=summarized
            return output
        except (OSError,ValueError) as e:
            last_error=e
            if retry<2:time.sleep(18 if retry==0 else 55)
    raise RuntimeError("El dato ERA5-Land no está listo: "+str(last_error))


def extend_local(by,now):
    """If NOAA and T300 advanced, obtain newly closed months before issuing.
    This does not overwrite or backfill the earlier model-training source CSV.
    """
    expected=shift(now.astimezone(LOCAL).strftime("%Y-%m"),-1)
    last=max(by["Chiclayo"])
    if last>expected:raise ValueError("Hay un mes futuro en el CSV local")
    if last<expected:
        # No issuing until truly released, with zero made-up monthly values.
        supplemental=fetch_monthly_era5_land(shift(last,1),expected,by)
        for city,months in supplemental.items():by[city].update(months)
    if any(max(by[c])!=expected for c in SITES):
        raise ValueError("La última observación local no corresponde al mes ya cerrado")
    return expected


def seasonal_means(by):
    averages={}
    for city,obs in by.items():
        averages[city]={}
        for month in range(1,13):
            series=[x for m,x in obs.items() if "1996-01"<=m<=TRAIN_LIMIT and int(m[-2:])==month]
            if len(series)!=27:raise ValueError("La normal 1996-2022 no está completa")
            averages[city][month]=st.mean(series)
    return averages


def models_and_issue(by,sea,heat,now,origin,was_supplemented=False):
    if now.tzinfo is None:raise ValueError("Se requiere un sello con huso horario")
    if origin!=shift(now.astimezone(LOCAL).strftime("%Y-%m"),-1):
        raise ValueError("No emitir si el origen no es el mes anterior terminado")
    if origin not in sea or shift(origin,-1) not in heat:
        raise ValueError("Los índices Niño1+2 y T300 publicados no llegan al origen")
    if any(max(by[c])!=origin for c in SITES):
        raise ValueError("No existen meses locales completos hasta el origen")
    means=seasonal_means(by)
    source_hashes={name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in {
        "serie_local_8d":SOURCE_LOCAL,"sst_nino12_6d":SOURCE_SST,
        "t300_8c":SOURCE_T300,"codigo_8e":Path(__file__)}.items()}
    local=now.astimezone(LOCAL)
    response={
        "fase":"8E",
        "tipo":"emision_oaf_temperatura_regional_experimental_inmutable",
        "emision_utc":now.astimezone(timezone.utc).isoformat(timespec="seconds"),
        "emision_peru":local.isoformat(timespec="seconds"),
        "mes_origen":origin,"periodo_entrenamiento_maximo_objetivo":TRAIN_LIMIT,
        "normal_para_entrenamiento":"1996–2022",
        "normal_publica_descriptiva":"1996–2025, no utilizada en ajuste",
        "fuente_local":"ERA5-Land 2m via Open-Meteo Historical Weather; celda de reanálisis",
        "fuente_nino12":"NOAA NCEI ERSSTv5 Niño1+2 reconstruido por OAF referencia 1991–2020",
        "fuente_t300":"NOAA/PMEL GODAS anomalía 0–300 m referencia 1981–2010; mes t−1",
        "sha256_fuentes_y_codigo":source_hashes,
        "serie_local_suplementaria":bool(was_supplemented),
        "modelo":"Ridge con regularización fija alpha=20; local frente a local+Niño1+2+T300",
        "ultimos_datos_predictores":{},
        "pronosticos":[],
        "es_icen_oficial":False,
        "es_alerta_enfen":False,
        "es_alerta_senamhi":False,
        "validacion_instrumental":False,
        "habilidad_prospectiva_demostrada":False,
        "probabilidad_calibrada":False,
        "avisos":[
           "La temperatura es del reanálisis ERA5-Land, NO de estación SENAMHI o finca.",
           "La anomalía oceánica de mes de origen suele estar disponible tras cerrar ese mes, por lo que h1 es ahora-cast intramensual.",
           "Nunca actualizar una emisión ya archivada, aunque NOAA/ERA5-Land revisen el pasado.",
           "El valor de temperatura para los próximos meses es hipótesis experimental, no alerta agrícola.",
           "La ventaja 8D es retrospectiva, con incertidumbre; no garantiza habilidad futura."
        ]
    }
    for city in SITES:
        climatology=means[city]
        anomaly={month:value-climatology[int(month[-2:])] for month,value in by[city].items()}
        values=[anomaly[origin],sea[origin],heat[shift(origin,-1)]]
        response["ultimos_datos_predictores"][city]={
            "temperatura_era5_land_origen_c":by[city][origin],
            "anomalia_era5_land_origen_c":anomaly[origin],
            "anomalia_nino12_origen_c":sea[origin],
            "t300_anomalia_mes_anterior_c":heat[shift(origin,-1)]
        }
        for h in (1,2,3):
            training=[]
            for month in sorted(anomaly):
                target=shift(month,h)
                prev=shift(month,-1)
                if target<=TRAIN_LIMIT and target in anomaly and month in sea and prev in heat:
                    training.append(([anomaly[month],sea[month],heat[prev]],anomaly[target]))
            if len(training)<250:raise ValueError("Insuficiente entrenamiento sin futuro "+city+" h"+str(h))
            m1=fit([([x[0]],y) for x,y in training],20.)
            m3=fit(training,20.)
            target=shift(origin,h)
            normal=climatology[int(target[-2:])]
            local_anomaly=predict(m1,[values[0]])
            ocean_anomaly=predict(m3,values)
            prior=local.date()<date(*map(int,target.split("-")),1)
            response["pronosticos"].append({
                "localidad":city,"horizonte_meses":h,"mes_objetivo":target,
                "tipo_emision":"pronostico_antes_inicio_mes" if prior else "estimacion_intramensual",
                "emitido_antes_inicio_mes":prior,
                "n_entrenamiento":len(training),
                "climatologia_fija_mes_objetivo_c":round(normal,5),
                "anomalia_local_c":round(local_anomaly,5),
                "anomalia_nino_t300_c":round(ocean_anomaly,5),
                "pronostico_local_c":round(normal+local_anomaly,5),
                "pronostico_nino_t300_c":round(normal+ocean_anomaly,5),
                "persistencia_anomalia_c":round(normal+values[0],5),
                "climatologia_cero_c":round(normal,5),
                "verificacion_prospectiva":False
            })
    if len(response["pronosticos"])!=12:raise ValueError("No hay 12 pronósticos completos")
    return response


def snapshot(now=None):
    now=now or datetime.now(timezone.utc)
    by=local_records()
    origin=shift(now.astimezone(LOCAL).strftime("%Y-%m"),-1)
    path=ISSUES/(origin+".json")
    if path.exists():
        original=json.loads(path.read_text(encoding="utf-8"))
        if original.get("fase")!="8E" or original.get("mes_origen")!=origin:
            raise ValueError("Conflicto en emisión, no se sobreescribe")
        print("Pronóstico regional 8E ya emitido y congelado:",path)
        return original,False
    # Check source publications before creating any new prediction.
    sea=get_monthly(SOURCE_SST,"anomalia_ersstv5_c")
    heat=get_monthly(SOURCE_T300,"t300_anomalia_c")
    if origin not in sea or shift(origin,-1) not in heat:
        print("SIN EMISIÓN NUEVA: índices NOAA/PMEL todavía no publicaron valores necesarios "+origin)
        return None,False
    original_last=max(by["Chiclayo"])
    try:
        last=extend_local(by,now)
    except (RuntimeError,ValueError) as e:
        print("SIN EMISIÓN NUEVA: referencia local no disponible "+str(e))
        return None,False
    if last!=origin:raise ValueError("Último mes local no corresponde al origen")
    data=models_and_issue(by,sea,heat,now,origin,last>original_last)
    ISSUES.mkdir(parents=True,exist_ok=True)
    if path.exists():raise ValueError("No sobrescribir una emisión previa")
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Primer archivo regional 8E inmutable:",path,
          "ciudades",len(SITES),"pronósticos",len(data["pronosticos"]))
    return data,True


def verify(now=None):
    now=now or datetime.now(timezone.utc)
    now_local=now.astimezone(LOCAL).date()
    stored=[]
    for path in sorted(ISSUES.glob("????-??.json")) if ISSUES.exists() else []:
        issue=json.loads(path.read_text(encoding="utf-8"))
        if (issue.get("fase")!="8E" or issue.get("mes_origen")!=path.stem or
            issue.get("es_alerta_enfen") is not False or
            issue.get("es_alerta_senamhi") is not False or
            issue.get("validacion_instrumental") is not False or
            len(issue.get("pronosticos",[]))!=12):
            raise ValueError("Emisión original inválida "+str(path))
        issued=datetime.fromisoformat(issue["emision_utc"].replace("Z","+00:00"))
        if issued.tzinfo is None:raise ValueError("Sin huso de emisión")
        for forecast in issue["pronosticos"]:
            month=forecast["mes_objetivo"];h=forecast["horizonte_meses"]
            if forecast["localidad"] not in SITES or h not in (1,2,3) or month!=shift(issue["mes_origen"],h):
                raise ValueError("Mes, ciudad o horizonte alterados")
            pre=issued.astimezone(LOCAL).date()<date(*map(int,month.split("-")),1)
            if pre is not forecast["emitido_antes_inicio_mes"]:
                raise ValueError("Fecha de pronóstico incompatible")
            ready=shift(month,1)
            eligible=now_local>=date(*map(int,ready.split("-")),10)
            stored.append({"emision_utc":issue["emision_utc"],
                "mes_origen":issue["mes_origen"],"mes_objetivo":month,
                "localidad":forecast["localidad"],"horizonte_meses":h,
                "tipo_emision":forecast["tipo_emision"],
                "emitido_antes_inicio_mes":pre,
                "pronostico_local_c":forecast["pronostico_local_c"],
                "pronostico_nino_t300_c":forecast["pronostico_nino_t300_c"],
                "observacion_era5_land_c":None,
                "error_local_c":None,"error_nino_t300_c":None,
                "fecha_minima_verificacion":date(*map(int,ready.split("-")),10).isoformat(),
                "estado":"esperando_reanalisis" if eligible else "mes_objetivo_aun_no_maduro"})
    mature=sorted(set(x["mes_objetivo"] for x in stored if x["estado"]=="esperando_reanalisis"))
    observed={}
    if mature:
        # One batched download for all mature months. If API not ready,
        # do not mark any month verified or create values from thin air.
        try:
            observed=fetch_monthly_era5_land(mature[0],mature[-1],SITES)
        except (RuntimeError,ValueError) as exc:
            print("Verificación pendiente por proveedor ERA5-Land: "+str(exc))
    for rec in stored:
        month=rec["mes_objetivo"];city=rec["localidad"]
        if month in observed.get(city,{}):
            actual=observed[city][month]
            rec["observacion_era5_land_c"]=round(actual,5)
            rec["error_local_c"]=round(rec["pronostico_local_c"]-actual,5)
            rec["error_nino_t300_c"]=round(rec["pronostico_nino_t300_c"]-actual,5)
            rec["estado"]="comparado_con_era5_land_revisable"
    completed=[x for x in stored if x["estado"]=="comparado_con_era5_land_revisable"]
    genuinely_prior=[x for x in completed if x["emitido_antes_inicio_mes"]]
    report={
        "fase":"8E",
        "estado":"con_comparaciones_prospectivas_experimentales" if completed else "esperando_cierre_y_reanalisis",
        "generado_utc":now.astimezone(timezone.utc).isoformat(timespec="seconds"),
        "numero_emisiones_originales":len(set(x["emision_utc"] for x in stored)),
        "pronosticos_originales_archivados":len(stored),
        "pronosticos_anteriores_al_mes":sum(x["emitido_antes_inicio_mes"] for x in stored),
        "estimaciones_intramensuales":sum(not x["emitido_antes_inicio_mes"] for x in stored),
        "pronosticos_comparados":len(completed),
        "comparados_realmente_previos_al_mes":len(genuinely_prior),
        "primera_verificacion_posible":min((x["fecha_minima_verificacion"] for x in stored),default=None),
        "ultima_emision":max((x["mes_origen"] for x in stored),default=None),
        "mae_previo_por_localidad_horizonte":{},
        "clasificacion_ensayo":"temperatura mensual modelada ERA5-Land, no validación instrumental SENAMHI",
        "es_icen_oficial":False,"es_alerta_enfen":False,"es_alerta_senamhi":False,
        "validacion_instrumental":False,"habilidad_prospectiva_demostrada":False,
        "probabilidades_calibradas":False,
        "cautelas":[
           "Hasta acumular meses completos de pronóstico anterior al evento no es posible demostrar habilidad futura.",
           "ERA5-Land es un reanálisis actualizable, NO observación SENAMHI de estación.",
           "El modelo de Niño/T300 muestra beneficio histórico irregular; no sustituye alertas oficiales.",
           "h1 emitido tras el inicio del objetivo es ahora-cast y nunca integra la MAE de predicciones realmente previas."
        ]}
    for city in SITES:
        report["mae_previo_por_localidad_horizonte"][city]={}
        for h in (1,2,3):
            q=[x for x in genuinely_prior if x["localidad"]==city and x["horizonte_meses"]==h]
            def mae(key):return round(st.mean(abs(x[key]) for x in q),5) if q else None
            report["mae_previo_por_localidad_horizonte"][city][str(h)]={
                "n":len(q),"mae_local_c":mae("error_local_c"),"mae_nino_t300_c":mae("error_nino_t300_c"),
                "habilidad_comprobada":False}
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    with ROWS.open("w",encoding="utf-8",newline="") as file:
        writer=csv.DictWriter(file,fieldnames=CSV_FIELDS);writer.writeheader()
        for r in completed:writer.writerow({k:r[k] for k in CSV_FIELDS})
    print("Fase8E",report["estado"],"archivados",len(stored),"comparados",len(completed))
    return report


def self_test():
    assert shift("2026-09",1)=="2026-10"
    assert shift("2026-12",1)=="2027-01"
    now=datetime(2026,10,15,10,15,tzinfo=LOCAL)
    # Synthetic, completely local. Never publish mock values as evidence.
    demo={city:{} for city in SITES}
    for city in SITES:
        for year in range(1996,2027):
            for mo in range(1,13 if year!=2026 else 10):
                month=f"{year:04d}-{mo:02d}"
                demo[city][month]=20+mo*.12+year*.001
    means=seasonal_means(demo)
    assert len(means["Olmos"])==12
    assert abs(means["Olmos"][9]-st.mean(demo["Olmos"][f"{year}-09"] for year in range(1996,2023)))<1e-9
    sst={m:1.0 for m in demo["Olmos"]}
    heat={m:.5 for m in demo["Olmos"]}
    # Test issuance in a mock isolated environment with temporary files.
    import tempfile
    original=(SOURCE_LOCAL,SOURCE_SST,SOURCE_T300)
    try:
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            globals()["SOURCE_LOCAL"]=root/"local.csv"
            globals()["SOURCE_SST"]=root/"sea.csv"
            globals()["SOURCE_T300"]=root/"t300.csv"
            for path in (SOURCE_LOCAL,SOURCE_SST,SOURCE_T300):
                path.write_text("source mocked only for checksum test",encoding="utf-8")
            issue=models_and_issue(demo,sst,heat,now,"2026-09")
    finally:
        globals()["SOURCE_LOCAL"],globals()["SOURCE_SST"],globals()["SOURCE_T300"]=original
    assert len(issue["pronosticos"])==12
    assert sum(x["emitido_antes_inicio_mes"] for x in issue["pronosticos"])==8
    assert sum(not x["emitido_antes_inicio_mes"] for x in issue["pronosticos"])==4
    assert {x["mes_objetivo"] for x in issue["pronosticos"]}=={"2026-10","2026-11","2026-12"}
    assert all(x["n_entrenamiento"]>=250 for x in issue["pronosticos"])
    assert not issue["habilidad_prospectiva_demostrada"]
    print("8E PASS: train limit, four sites, 4 nowcasts + 8 true pre-month emissions, unit checks")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--snapshot",action="store_true")
    parser.add_argument("--verify",action="store_true")
    parser.add_argument("--run",action="store_true")
    args=parser.parse_args()
    if args.self_test:self_test();return
    if args.snapshot or args.run or not args.verify:snapshot()
    if args.verify or args.run or not args.snapshot:verify()


if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("8E ERROR:",str(exc),file=sys.stderr)
        raise SystemExit(1)
