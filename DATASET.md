# Dataset: Terremotos de magnitud ≥ 5 (2016 – 2026)

El dataset contiene los **19.217 terremotos de magnitud 5 o superior** registrados en todo el mundo entre el 1 de enero de 2016 y el 24 de octubre de 2026. Se ha obtenido del catálogo **ComCat** del **U.S. Geological Survey (USGS)**, a través de su API pública ([FDSN Event Web Service](https://earthquake.usgs.gov/fdsnws/event/1/)), con una sola consulta:

```
https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2016-01-01&minmagnitude=5
```

El script `generar_dataset.py` descarga esta respuesta y la convierte en documentos para MongoDB, guardados en `datos/terremotos.json`. Los cambios principales son estos:
- Los campos se renombran al español.
- Las fechas pasan a tipo `Date`.
- La ubicación se guarda como un punto GeoJSON.
- Las listas de texto separadas por comas pasan a ser arrays.
- Los campos sin dato se omiten del documento.

Los datos se guardan en la base de datos `terremotos`, en la colección `terremotos`.

## Estructura de un documento

| Campo | Tipo | Descripción |
|---|---|---|
| `_id` | string | Identificador del evento en USGS |
| `magnitud`, `tipo_magnitud` | double, string | Magnitud (de 5,0 a 8,8) y escala usada |
| `lugar`, `region` | string | Descripción del lugar y país o zona (`region` se extrae de `lugar`) |
| `fecha` | date | Fecha y hora del terremoto (UTC) |
| `ubicacion` | GeoJSON Point | Epicentro `[longitud, latitud]` |
| `profundidad_km` | double | Profundidad del hipocentro |
| `tipo_evento` | string | `earthquake`, `volcanic eruption`, `nuclear explosion` o `landslide` |
| `tsunami` | bool | Si USGS emitió indicador de tsunami |
| `alerta` | string | Nivel de alerta por daños estimados: `green`, `yellow`, `orange` o `red` (solo en el 35 % de los documentos) |
| `significancia` | int | Índice de relevancia del evento según USGS |
| `impacto` | subdocumento | `personas_lo_sintieron`, `intensidad_reportada`, `intensidad_instrumental` (solo en el 57 %) |
| `calidad` | subdocumento | `num_estaciones`, `gap_azimutal`, `distancia_min_grados`, `rms` |
| `fuentes`, `productos` | array | Redes sísmicas que registraron el evento y productos científicos publicados (`shakemap`, `losspager`…) |

La estructura combina subdocumentos, arrays, campos opcionales, fechas y coordenadas geográficas, lo que permite practicar todos los tipos de consulta de MongoDB.
