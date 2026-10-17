#!/usr/bin/env python3
"""Fase 9C: reproduce y audita la evaluacion 9A con bloques anuales pareados.

Sin conexion a APIs, sin datos inventados. La salida publicada se contrasta con la
matriz original de GitHub. Entradas: datos/benchmark_9a/*.csv.

python modelos/evaluacion_pareada_9c.py --verificar datos/validacion_9c/resultados_9c.json
"""
import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT_CONT = ROOT / "datos/benchmark_9a/pronosticos_pareados_9a.csv"
INPUT_EVT = ROOT / "datos/benchmark_9a/eventos_p90_pareados_9a.csv"
OUTPUT = ROOT / "datos/validacion_9c/resultados_9c.json"
BASE = "base_viento_sst"
CANDIDATE = "base_mas_rh_vpd"


def read_paired(file, event=False):
    models = ({BASE, CANDIDATE} if event else
              {BASE, CANDIDATE, "base_mas_rh", "base_mas_vpd"})
    found = {}
    n = 0
    with file.open(encoding="utf-8", newline="") as fp:
        for row in csv.DictReader(fp):
            n += 1
            place, horizon, date = row["localidad"], int(row["horizonte_meses"]), row["mes_objetivo"]
            variable = "precipitacion_p90_enero_abril" if event else row["objetivo"]
            key = (place, horizon, variable, date)
            label = float(row["observado"])
            v = found.setdefault(key, {
                "localidad": place, "horizonte": horizon, "variable": variable,
                "mes": date, "fold": row["fold"], "observado": label
            })
            if v["observado"] != label or v["fold"] != row["fold"]:
                raise ValueError(f"Etiquetas o folds incompatibles en {key}")
            model = row["modelo"]
            if model not in models or model in v:
                raise ValueError(f"Modelo inesperado o repetido: {key}, {model}")
            prediction = float(row["prediccion"])
            if not math.isfinite(prediction):
                raise ValueError("Prediccion no finita")
            if event:
                threshold = float(row["umbral_p90_train_mm"])
                if v.get("umbral", threshold) != threshold:
                    raise ValueError("Umbral train P90 distinto entre modelos")
                v["umbral"] = threshold
                if label not in (0, 1) or not 0 <= prediction <= 1:
                    raise ValueError("Probabilidad o clase no valida")
                if date[5:7] not in {"01", "02", "03", "04"}:
                    raise ValueError("P90 fuera de enero-abril")
            v[model] = prediction
    for key, row in found.items():
        if any(m not in row for m in models):
            raise ValueError(f"No existen todas las variantes de 9A para {key}")
    expected = 1440 if event else 17280
    if n != expected:
        raise ValueError(f"Filas 9A: se esperaban {expected} y hay {n}")
    return list(found.values())


def bootstrap(means, block=3, replicas=10000, seed=917):
    state = seed & 0xFFFFFFFF
    n = len(means)
    simulated = []
    for _ in range(replicas):
        total = 0.0
        taken = 0
        while taken < n:
            state = (1664525 * state + 1013904223) & 0xFFFFFFFF
            start = math.floor((state / (2 ** 32)) * n)
            for j in range(block):
                if taken >= n:
                    break
                total += means[(start + j) % n]
                taken += 1
        simulated.append(total / n)
    return sorted(simulated)


def interval(sim, alpha):
    n = len(sim)
    return [
        round(sim[math.floor(alpha / 2 * n)], 9),
        round(sim[min(n - 1, math.floor((1 - alpha / 2) * n))], 9)
    ]


def grouped_scores(paired, event=False):
    groups = defaultdict(list)
    for row in paired:
        groups[(row["localidad"], row["horizonte"], row["variable"])].append(row)
    output = []
    for (loc, horizon, variable), values in sorted(groups.items()):
        values.sort(key=lambda x: x["mes"])
        annual = defaultdict(list)
        ref_sum, new_sum, positives = 0.0, 0.0, 0
        for item in values:
            observation = item["observado"]
            ref = item[BASE]
            new = item[CANDIDATE]
            a = ((ref - observation)**2 if event else abs(ref - observation))
            b = ((new - observation)**2 if event else abs(new - observation))
            ref_sum += a
            new_sum += b
            if event:
                positives += int(observation)
            annual[int(item["mes"][:4])].append(a - b)
        years = [(year, sum(deltas) / len(deltas))
                 for year, deltas in sorted(annual.items())]
        per_year = 4 if event else 12
        if len(years) != 15 or sorted(annual) != list(range(2011, 2026)):
            raise ValueError(f"Periodos 9C incompletos: {loc}/{variable}/{horizon}")
        if any(len(x) != per_year for x in annual.values()):
            raise ValueError("Meses faltantes o duplicados por anio")
        mean_losses = [v for _, v in years]
        three = bootstrap(mean_losses, block=3)
        one = bootstrap(mean_losses, block=1)
        n = len(values)
        row = {
            "localidad": loc, "horizonte_meses": horizon,
            "variable": variable, "meses": n, "anios": 15,
            "referencia_8w": round(ref_sum / n, 9),
            "candidato_rh_vpd": round(new_sum / n, 9),
            "mejora_referencia_menos_candidato": round((ref_sum-new_sum)/n, 9),
            "ic95_bloques_3_anios": interval(three, 0.05),
            "ic95_bloques_1_anio": interval(one, 0.05),
            "ic_familiar_bonferroni_bloques_3_anios": interval(three, 0.05 / (12 if event else 24)),
            "mejora_sin_2017": round(sum(v for y,v in years if y != 2017)/14, 9),
            "mejora_sin_2023": round(sum(v for y,v in years if y != 2023)/14, 9),
        }
        if event:
            row.update({
                "eventos": positives,
                "prevalencia": round(positives/n, 8),
                "evidencia_de_extremos_suficiente": positives >= 20 and (n-positives) >= 20,
            })
        output.append(row)
    return output


def check_against_archive(continuous, extreme, archive):
    for typ, new in [("continuo", continuous), ("extremos", extreme)]:
        old = archive[typ]
        if len(new) != len(old):
            raise AssertionError(f"Numero de grupos diferente para {typ}")
        for i, (a, b) in enumerate(zip(new, old)):
            if a.keys() != b.keys():
                raise AssertionError(f"Campos diferentes en {typ}/{i}")
            for col in a:
                lhs, rhs = a[col], b[col]
                if isinstance(lhs, list):
                    if any(abs(x-y) > 1e-7 for x,y in zip(lhs,rhs)):
                        raise AssertionError(f"Intervalo diferente {typ}/{i}/{col}: {lhs} {rhs}")
                elif isinstance(lhs, float):
                    if abs(lhs-rhs) > 1e-7:
                        raise AssertionError(f"Valor diferente {typ}/{i}/{col}: {lhs} {rhs}")
                elif lhs != rhs:
                    raise AssertionError(f"Campo diferente {typ}/{i}/{col}: {lhs} {rhs}")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--continuos", type=Path, default=INPUT_CONT)
    parser.add_argument("--eventos", type=Path, default=INPUT_EVT)
    parser.add_argument("--verificar", type=Path, default=OUTPUT)
    options = parser.parse_args()
    cont = grouped_scores(read_paired(options.continuos), event=False)
    ext = grouped_scores(read_paired(options.eventos, event=True), event=True)
    if len(cont) != 24 or len(ext) != 12:
        raise ValueError("Combinaciones localidad/horizonte/variable incompletas")
    archive = json.loads(options.verificar.read_text(encoding="utf8"))
    check_against_archive(cont, ext, archive)
    print(json.dumps({
        "fase": "9C", "archivos": "coinciden con matriz archivada",
        "n_comparaciones_continuas": len(cont),
        "n_comparaciones_extremos": len(ext),
        "continuas_ic_bonferroni_positivo": sum(x["ic_familiar_bonferroni_bloques_3_anios"][0]>0 for x in cont),
        "extremos_ic_bonferroni_positivo": sum(x["ic_familiar_bonferroni_bloques_3_anios"][0]>0 for x in ext),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
