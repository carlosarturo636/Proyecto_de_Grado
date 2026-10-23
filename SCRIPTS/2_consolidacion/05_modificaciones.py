# -*- coding: utf-8 -*-
"""
PASO 1.5 - MODIFICACIONES
Recorre los 26 archivos nacionales de Modificaciones (ene-2021 a ago-2026).
De cada archivo toma SOLO el periodo que le corresponde (ver PLAN), conserva
solo las modificaciones de los contratos del estudio, unifica los dos
esquemas de columnas (pagina: "ID Contrato" / API: "id_contrato") y
normaliza fechas y valores.

Es el script mas pesado (unos 25 GB de lectura). Guarda un archivo parcial
por cada archivo de entrada en 02_DEPURADOS/_parciales/modificaciones, asi
que si se interrumpe, al volver a correrlo continua donde iba.

NO decide todavia que modificaciones cuentan para el proxy (estado,
version vigente): eso es Metodologia 7.3.3 y se aplica en el paso 2.

Salida en 02_DEPURADOS:  modificaciones_atlantico.csv
Uso:  python 05_modificaciones.py
"""

import pandas as pd
from comun import CRUDOS, DEPURADOS, fecha_iso, numero, ids_estudio, registrar, guardar

# archivo -> [desde, hasta) segun fecha de aprobacion
PLAN = {
    "SECOP_II_Modificaciones_a_contratos_2021.csv": ("2021-01-01", "2022-01-01"),
    "SECOP_II_Modificaciones_a_contratos_2022.csv": ("2022-01-01", "2023-01-01"),
    "SECOP_II_Modificaciones_a_contratos_2023.csv": ("2023-01-01", "2024-01-01"),
    "SECOP_II_Modificaciones_a_contratos_2024.csv": ("2024-01-01", "2025-01-01"),
    **{f"modificaciones_nacional_2025_{m:02d}.csv":
       (f"2025-{m:02d}-01", f"2025-{m + 1:02d}-01" if m < 12 else "2026-01-01") for m in range(1, 13)},
    "modificaciones_nacional_2026_01.csv": ("2026-01-01", "2026-02-01"),
    "modificaciones_nacional_2026_02.csv": ("2026-02-01", "2026-03-01"),
    "SECOP_II_Modificaciones_a_contratos_01_03_2026_to_30_06_2026.csv": ("2026-03-01", "2026-06-01"),
    "SECOP_II_-_Modificaciones_a_contratos_2026_06.csv": ("2026-06-01", "2026-07-01"),
    "SECOP_II_Modificaciones_a_contratos_01_07_2026_to_30_09_2026.csv": ("2026-07-01", "2026-08-01"),
    "modificaciones_nacional_2026_08_dias01a27.csv": ("2026-08-01", "2026-08-28"),
    "modificaciones_dia_2026_08_28.csv": ("2026-08-28", "2026-08-29"),
    "modificaciones_dia_2026_08_29.csv": ("2026-08-29", "2026-08-30"),
    "modificaciones_dia_2026_08_30.csv": ("2026-08-30", "2026-08-31"),
    "modificaciones_dia_2026_08_31.csv": ("2026-08-31", "2026-09-01"),
}

# Nombre en la pagina -> nombre en la API (se conservan solo estas columnas)
COLUMNAS = {
    "Identificador": "identificador",
    "ID Contrato": "id_contrato",
    "Identificador modificacion": "identificador_modificacion",
    "Estado modificacion": "estado_modificacion",
    "Fecha de aprobacion": "fecha_de_aprobacion",
    "Fecha creacion": "fecha_creacion",
    "Fecha version": "fecha_version",
    "Numero version": "numero_version",
    "Version anterior del contrato": "version_anterior_del_contrato",
    "Valor Modificacion": "valor_modificacion",
    "Dias extendidos": "dias_extendidos",
    "Fecha inicio contrato": "fecha_inicio_contrato",
    "Fecha fin contrato": "fecha_fin_contrato",
    "Liquidacion": "liquidacion",
    "Proposito modificacion": "proposito_modificacion",
    "Descripcion": "descripcion",
}
API = list(COLUMNAS.values())


def procesar(ruta, desde, hasta, ids):
    encabezado = pd.read_csv(ruta, nrows=0).columns
    es_pagina = "ID Contrato" in encabezado
    usecols = list(COLUMNAS) if es_pagina else API
    leidas, partes, sin_fecha, fuera = 0, [], 0, 0
    for ch in pd.read_csv(ruta, dtype=str, usecols=usecols, chunksize=500_000,
                          on_bad_lines="skip", engine="c"):
        leidas += len(ch)
        if es_pagina:
            ch = ch.rename(columns=COLUMNAS)
        ch = ch[ch["id_contrato"].isin(ids)].copy()
        if ch.empty:
            continue
        ch["fecha_de_aprobacion"] = fecha_iso(ch["fecha_de_aprobacion"])
        sin_fecha += ch["fecha_de_aprobacion"].isna().sum()
        dentro = (ch["fecha_de_aprobacion"] >= desde) & (ch["fecha_de_aprobacion"] < hasta)
        fuera += (~dentro).sum()
        partes.append(ch[dentro][API])
    d = pd.concat(partes, ignore_index=True) if partes else pd.DataFrame(columns=API)
    d["archivo_origen"] = ruta.name
    return d, leidas, sin_fecha, fuera


def main():
    print("=" * 70 + "\nPASO 1.5 - MODIFICACIONES\n" + "=" * 70)
    ids = ids_estudio()
    carpeta = CRUDOS / "MODIFICACIONES"
    parciales = DEPURADOS / "_parciales" / "modificaciones"
    parciales.mkdir(parents=True, exist_ok=True)

    faltantes = [a for a in PLAN if not (carpeta / a).exists()]
    if faltantes:
        raise SystemExit(f"Faltan archivos en 01_CRUDOS/MODIFICACIONES: {faltantes}")

    for nombre, (desde, hasta) in PLAN.items():
        salida = parciales / nombre
        if salida.exists():
            print(f"{nombre}: ya procesado. Se omite.")
            continue
        print(f"{nombre}: modificaciones aprobadas desde {desde} hasta antes de {hasta}")
        d, leidas, sin_fecha, fuera = procesar(carpeta / nombre, desde, hasta, ids)
        d.to_csv(salida, index=False, encoding="utf-8-sig")
        print(f"   leídas {leidas:,} · del estudio y en su periodo {len(d):,}")
        registrar("1.5", "Modificaciones", nombre, leidas, len(d),
                  f"periodo {desde} a {hasta}; fuera del periodo: {fuera}; sin fecha: {sin_fecha}")

    m = pd.concat([pd.read_csv(parciales / n, dtype=str) for n in PLAN], ignore_index=True)
    total = len(m)
    exactos = m.drop(columns="archivo_origen").duplicated().sum()
    m = m[~m.drop(columns="archivo_origen").duplicated()]
    for col in ["fecha_creacion", "fecha_version", "fecha_inicio_contrato", "fecha_fin_contrato"]:
        m[col] = fecha_iso(m[col])
    for col in ["valor_modificacion", "dias_extendidos", "numero_version",
                "version_anterior_del_contrato"]:
        m[col] = numero(m[col])

    print(f"   Modificaciones del estudio: {len(m):,} filas · "
          f"{m['identificador_modificacion'].nunique():,} modificaciones únicas · "
          f"{m['id_contrato'].nunique():,} contratos")
    print("   Por estado:", m["estado_modificacion"].value_counts().to_dict())
    guardar(m, "modificaciones_atlantico.csv")
    registrar("1.5", "Modificaciones", "modificaciones_atlantico.csv", total, len(m),
              f"duplicados exactos eliminados: {exactos}")
    print("Consolidación terminada. Los registros leídos y conservados de cada fuente están en 02_DEPURADOS/resumen_consolidacion.csv")


if __name__ == "__main__":
    main()
