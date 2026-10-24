"""Descarga terremotos de USGS y genera datos/terremotos.json listo para MongoDB.

Fuente: USGS Earthquake Catalog (FDSN Event Web Service)
https://earthquake.usgs.gov/fdsnws/event/1/
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests

URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
PARAMETROS = {
    "format": "geojson",
    "starttime": "2016-01-01",
    "minmagnitude": 5,
    "orderby": "time-asc",
}
SALIDA = Path(__file__).parent / "datos" / "terremotos.json"


def fecha(ms):
    """Milisegundos epoch -> fecha en formato MongoDB Extended JSON."""
    iso = datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat(timespec="milliseconds")
    return {"$date": iso.replace("+00:00", "Z")}


def region(lugar):
    """'45 km SW of Tobelo, Indonesia' -> 'Indonesia'; 'Fiji region' -> 'Fiji'."""
    if not lugar:
        return None
    texto = lugar.split(", ")[-1]
    texto = re.sub(r"^\d+ km [NSEW]{1,3} of ", "", texto)
    texto = re.sub(r"^\d{4} ", "", texto)
    texto = re.sub(r" (Earthquake|region)$", "", texto)
    return texto.strip()


def lista(texto):
    """',us,at,pt,' -> ['us', 'at', 'pt']"""
    return [x for x in (texto or "").split(",") if x]


def sin_nulos(d):
    return {k: v for k, v in d.items() if v is not None}


def transformar(feature):
    p = feature["properties"]
    lon, lat, profundidad = feature["geometry"]["coordinates"]
    doc = {
        "_id": feature["id"],
        "magnitud": p["mag"],
        "tipo_magnitud": p["magType"],
        "lugar": p["place"],
        "region": region(p["place"]),
        "fecha": fecha(p["time"]),
        "ubicacion": {"type": "Point", "coordinates": [lon, lat]},
        "profundidad_km": profundidad,
        "tipo_evento": p["type"],
        "tsunami": bool(p["tsunami"]),
        "alerta": p["alert"],
        "significancia": p["sig"],
        "estado": p["status"],
        "red": p["net"],
        "impacto": sin_nulos({
            "personas_lo_sintieron": p["felt"],
            "intensidad_reportada": p["cdi"],
            "intensidad_instrumental": p["mmi"],
        }),
        "calidad": sin_nulos({
            "num_estaciones": p["nst"],
            "gap_azimutal": p["gap"],
            "distancia_min_grados": p["dmin"],
            "rms": p["rms"],
        }),
        "fuentes": lista(p["sources"]),
        "productos": lista(p["types"]),
        "url": p["url"],
    }
    # Los campos sin dato se omiten (útil para practicar $exists)
    return {k: v for k, v in doc.items() if v not in (None, {})}


def main():
    print("Descargando de USGS...")
    r = requests.get(URL, params=PARAMETROS, timeout=300)
    r.raise_for_status()
    features = r.json()["features"]
    documentos = [transformar(f) for f in features]
    SALIDA.parent.mkdir(exist_ok=True)
    SALIDA.write_text(json.dumps(documentos, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(documentos)} terremotos guardados en {SALIDA}")


if __name__ == "__main__":
    main()
