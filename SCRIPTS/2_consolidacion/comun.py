# -*- coding: utf-8 -*-
"""
Funciones compartidas por los scripts de consolidacion (paso 1 del OE2).
No se corre solo: lo importan 01_contratos.py ... 05_modificaciones.py.
"""

import csv
import datetime as dt
import os
from pathlib import Path

import pandas as pd

# Raiz del proyecto: ...\PROYECTO_DE_GRADO (dos niveles arriba de este archivo)
BASE = Path(__file__).resolve().parents[2]
CRUDOS = BASE / "01_CRUDOS"
DEPURADOS = Path(os.environ.get("SALIDA_DEPURADOS", BASE / "02_DEPURADOS"))
DEPURADOS.mkdir(parents=True, exist_ok=True)

ARCHIVO_IDS = DEPURADOS / "ids_contratos_estudio.csv"
ARCHIVO_RESUMEN = DEPURADOS / "resumen_consolidacion.csv"

FECHA_CORTE = "2026-08-31"   # ultima fecha observada (inclusive)


def fecha_iso(serie):
    """Convierte fechas 'MM/DD/AAAA ...' (portal) o 'AAAA-MM-DDT...' (API) a 'AAAA-MM-DD'."""
    s = serie.astype("string").str.strip()
    iso = s.str.match(r"^\d{4}-\d{2}-\d{2}", na=False)
    salida = pd.Series(pd.NA, index=s.index, dtype="string")
    salida[iso] = s[iso].str[:10]
    resto = s[~iso].str[:10]
    convertidas = pd.to_datetime(resto, format="%m/%d/%Y", errors="coerce")
    salida[~iso] = convertidas.dt.strftime("%Y-%m-%d").astype("string")
    return salida


def numero(serie, estilo="us"):
    """Texto -> float.
    estilo="co": formato colombiano del portal de Contratos ('$18.715.790,67':
                 punto de miles, coma decimal).
    estilo="us": resto de archivos ('47,196,000' o '47196000.5': coma de miles,
                 punto decimal)."""
    s = serie.astype("string").str.strip()
    s = s.str.replace("$", "", regex=False).str.replace(" ", "", regex=False)
    if estilo == "co":
        s = s.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    else:
        s = s.str.replace(",", "", regex=False)
    return pd.to_numeric(s, errors="coerce")


def ids_estudio():
    if not ARCHIVO_IDS.exists():
        raise SystemExit("No se encontró la lista de contratos del estudio: ejecute primero 01_contratos.py, que la genera.")
    return set(pd.read_csv(ARCHIVO_IDS, dtype=str)["id_contrato"])


def registrar(paso, fuente, archivo, leidas, conservadas, observacion=""):
    """Agrega una linea al resumen que luego se reporta en Trabajo de Campo (8.1.1)."""
    nuevo = not ARCHIVO_RESUMEN.exists()
    with open(ARCHIVO_RESUMEN, "a", newline="", encoding="utf-8-sig" if nuevo else "utf-8") as f:
        w = csv.writer(f)
        if nuevo:
            w.writerow(["fecha_hora", "paso", "fuente", "archivo", "filas_leidas",
                        "filas_conservadas", "observacion"])
        w.writerow([dt.datetime.now().strftime("%Y-%m-%d %H:%M"), paso, fuente, archivo,
                    leidas, conservadas, observacion])


def guardar(df, nombre):
    ruta = DEPURADOS / nombre
    df.to_csv(ruta, index=False, encoding="utf-8-sig")
    print(f"   Archivo escrito: {ruta} ({len(df):,} filas)")
    return ruta
