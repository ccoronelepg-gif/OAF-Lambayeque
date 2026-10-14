"""OAF Fase 3O: agregar 5 registros diarios SENAMHI a meses de lluvia completos.
No confundir ausencia con 0 mm ni asumir que un mes parcialmente observado es total real.
Uso: python preparar_observaciones_3o.py --origen /ruta/TXT --salida /ruta/datos
"""
from pathlib import Path
import calendar
import argparse
import pandas as pd

NOMBRES = {
    "JAYANCA.txt": "Jayanca (La Viña)",
    "CAYALTI.txt": "Cayaltí",
    "REQUE.txt": "Reque",
    "LAMBAYEQUE.txt": "Lambayeque",
    "CUEVA BLANCA.txt": "Cueva Blanca",
}


def ejecutar(origen: Path, salida: Path):
    salida.mkdir(exist_ok=True, parents=True)
    bloques = []
    for archivo, nombre in NOMBRES.items():
        f = origen / archivo
        if not f.is_file():
            raise FileNotFoundError(f)
        df = pd.read_csv(f, sep=r"\s+", header=None, names=["anio", "mes", "dia", "p_mm", "tmax", "tmin"])
        df = df.loc[(df.anio >= 1996) & (df.anio <= 2015)].copy()
        df["fecha"] = pd.to_datetime(df[["anio", "mes", "dia"]].rename(columns={"anio": "year", "mes": "month", "dia": "day"}), errors="raise")
        if df.fecha.duplicated().any():
            raise ValueError(f"Fecha diaria duplicada en {nombre}")
        df["p_mm"] = pd.to_numeric(df["p_mm"], errors="coerce")
        df.loc[df.p_mm < 0, "p_mm"] = float("nan")
        df["mes"] = df.fecha.dt.strftime("%Y-%m")
        grp = df.groupby("mes", as_index=False).agg(
            observado_mm=("p_mm", lambda s: round(s.sum(min_count=1), 3)),
            dias_validos=("p_mm", "count"),
            dias_registrados=("p_mm", "size"),
        )
        grp["dias_mes"] = grp.mes.map(lambda s: calendar.monthrange(int(s[:4]), int(s[5:]))[1])
        grp["estacion"] = nombre
        # Conservar todos los meses, pero invalidar el acumulado de meses incompletos.
        grp["mes_completo"] = (grp.dias_validos == grp.dias_mes) & (grp.dias_registrados == grp.dias_mes)
        grp.loc[~grp.mes_completo, "observado_mm"] = float("nan")
        bloques.append(grp)
    todo = pd.concat(bloques, ignore_index=True)
    todo = todo[["estacion", "mes", "observado_mm", "dias_validos", "dias_registrados", "dias_mes", "mes_completo"]]
    validos = todo[todo.mes_completo].drop(columns=["mes_completo", "dias_registrados"]).sort_values(["estacion", "mes"])
    assert len(validos) == 1109, len(validos)
    assert len(validos.query("mes >= '1998-01' and mes <= '1998-12'")) == 60
    validos.to_csv(salida / "senamhi_mensual_completo_1996_2015.csv", index=False, float_format="%.3f")
    todo.to_csv(salida / "auditoria_cobertura_mensual_1996_2015.csv", index=False, float_format="%.3f")
    resumen = []
    for estacion, d in todo.groupby("estacion"):
        n = d.mes.str[:4].value_counts().sort_index()
        y = d[d.mes_completo].copy()
        completos = y.mes.str[:4].value_counts().sort_index()
        resumen.append({
            "estacion": estacion,
            "meses_calendario_con_registros": len(d),
            "meses_completos": len(y),
            "meses_incompletos": (~d.mes_completo).sum(),
            "anios_completos": int((completos == 12).sum()),
            "primer_mes_con_registros": d.mes.min(),
            "ultimo_mes_con_registros": d.mes.max(),
        })
    resumen = pd.DataFrame(resumen)
    resumen.to_csv(salida / "resumen_cobertura.csv", index=False)
    print(resumen.to_string(index=False))
    print("Meses completos (mes-estación):", len(validos))
    print("Observación 1998 total:", validos[validos.mes.str.startswith("1998")].groupby("estacion").observado_mm.sum().round(2).to_dict())


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--origen", type=Path, default=Path(__file__).resolve().parents[1])
    a.add_argument("--salida", type=Path, default=Path(__file__).resolve().parent)
    arg = a.parse_args()
    ejecutar(arg.origen, arg.salida)
