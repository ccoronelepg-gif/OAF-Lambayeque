#!/usr/bin/env python3
"""OAF-Lambayeque: indicador térmico experimental de oídio de vid.
FUENTE: https://ipm.ucanr.edu/agriculture/grape/powdery-mildew/
Sin diagnóstico, probabilidad calibrada ni recomendaciones de aplicación.
"""
import argparse
import json
import math
from collections import defaultdict
from datetime import date, timedelta
from urllib.parse import urlencode
from urllib.request import urlopen

PUNTOS = {
    "Motupe": (-6.15083, -79.71420),
    "Jayanca": (-6.39278, -79.82280),
    "Olmos": (-5.98825, -79.74723),
    "Chiclayo": (-6.77140, -79.84090),
}
MIN_C, MAX_C = (70 - 32) * 5 / 9, (85 - 32) * 5 / 9


def consultar_pronostico(localidad):
    lat, lon = PUNTOS[localidad]
    params = {
        "latitude": lat, "longitude": lon,
        "hourly": "temperature_2m",
        "timezone": "America/Lima", "forecast_days": 8,
    }
    url = "https://api.open-meteo.com/v1/forecast?" + urlencode(params)
    with urlopen(url, timeout=30) as response:
        return json.load(response)["hourly"]


def indicador_termico(horario):
    tiempos = horario.get("time")
    temperaturas = horario.get("temperature_2m")
    if not isinstance(tiempos, list) or not isinstance(temperaturas, list):
        raise ValueError("Faltan listas horarias")
    if len(tiempos) != len(temperaturas):
        raise ValueError("Series horarias incompatibles")
    grupos = defaultdict(dict)
    vistos = set()
    for marca, temp in zip(tiempos, temperaturas):
        if (not isinstance(marca, str) or len(marca) != 16
                or marca[10] != "T" or marca[13:16] != ":00"
                or marca in vistos):
            raise ValueError("Marca horaria inválida o repetida")
        fecha = date.fromisoformat(marca[:10])
        hora = int(marca[11:13])
        if not 0 <= hora < 24:
            raise ValueError("Hora fuera de rango")
        vistos.add(marca)
        grupos[fecha][hora] = temp

    fechas = sorted(grupos)[1:8]  # hoy se excluye
    if len(fechas) != 7:
        raise ValueError("Faltan siete jornadas futuras")
    detalle = []
    dias_validos = racha = racha_max = 0
    anterior = None
    for fecha in fechas:
        datos = grupos[fecha]
        completo = len(datos) == 24
        corrida = max_horas = 0
        for h in range(24):
            temp = datos.get(h)
            if not isinstance(temp, (float, int)) or not math.isfinite(temp):
                completo = False
                corrida = 0
                continue
            corrida = corrida + 1 if MIN_C <= temp <= MAX_C else 0
            max_horas = max(max_horas, corrida)
        cumple = completo and max_horas >= 6
        if cumple:
            dias_validos += 1
            racha = racha + 1 if anterior and fecha - anterior == timedelta(days=1) else 1
            racha_max = max(racha_max, racha)
        else:
            racha = 0
        detalle.append({
            "fecha": fecha.isoformat(),
            "dia_completo": completo,
            "max_horas_consecutivas": max_horas if completo else None,
            "cumple_patron_termico": cumple if completo else None,
        })
        anterior = fecha
    return {
        "metodo": "UC IPM: patrón térmico, no índice epidemiológico completo",
        "tipo_dato": "pronostico_externo",
        "dias_favorables": dias_validos,
        "max_dias_consecutivos": racha_max,
        "patron_tres_dias": racha_max >= 3,
        "prediccion_de_infeccion": None,
        "advertencia": "El modelo original requiere infección primaria y temperatura en el dosel",
        "detalle": detalle,
    }


def prueba_sintetica():
    origen = date(2026, 10, 14)
    def muestra(dias, hueco=None):
        marcas, temps = [], []
        for d in range(8):
            fecha = (origen + timedelta(days=d)).isoformat()
            for h in range(24):
                if (d, h) == hueco:
                    continue
                marcas.append(f"{fecha}T{h:02d}:00")
                temps.append(24.0 if d in dias and 10 <= h <= 15 else 17.0)
        return {"time": marcas, "temperature_2m": temps}
    a = indicador_termico(muestra({1, 2, 3}))
    assert a["patron_tres_dias"] and a["dias_favorables"] == 3
    b = indicador_termico(muestra({1, 3}))
    assert not b["patron_tres_dias"] and b["max_dias_consecutivos"] == 1
    c = indicador_termico(muestra({1, 2, 3}, (2, 12)))
    assert not c["patron_tres_dias"] and c["detalle"][1]["cumple_patron_termico"] is None
    d = indicador_termico(muestra(set()))
    assert not d["patron_tres_dias"] and d["dias_favorables"] == 0
    print("4 pruebas sintéticas superadas")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--localidad", choices=PUNTOS, default="Motupe")
    parser.add_argument("--prueba", action="store_true")
    args = parser.parse_args()
    if args.prueba:
        prueba_sintetica()
    else:
        salida = indicador_termico(consultar_pronostico(args.localidad))
        salida["localidad"] = args.localidad
        print(json.dumps(salida, ensure_ascii=False, indent=2))
