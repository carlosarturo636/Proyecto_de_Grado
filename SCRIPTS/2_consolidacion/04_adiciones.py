# -*- coding: utf-8 -*-
"""
PASO 1.4 - ADICIONES
Recorre los 68 archivos mensuales (nacional, ene-2021 a ago-2026) y conserva
solo las adiciones de los contratos del estudio, registradas hasta la
fecha de corte (31/08/2026). Quita las columnas internas del portal
(:id, :version, :created_at, :updated_at).

Salida en 02_DEPURADOS:  adiciones_atlantico.csv
Uso:  python 04_adiciones.py
"""

import pandas as pd
from comun import CRUDOS, FECHA_CORTE, fecha_iso, ids_estudio, registrar, guardar

COLUMNAS = ["identificador", "id_contrato", "tipo", "descripcion", "fecharegistro"]


def main():
    print("=" * 70 + "\nPASO 1.4 - ADICIONES\n" + "=" * 70)
    ids = ids_estudio()
    partes, leidas = [], 0
    for f in sorted((CRUDOS / "ADICIONES").glob("*.csv")):
        d = pd.read_csv(f, dtype=str, usecols=COLUMNAS)
        leidas += len(d)
        d = d[d["id_contrato"].isin(ids)]
        partes.append(d)
        print(f"   {f.name}: {len(d):,} del estudio")
    a = pd.concat(partes, ignore_index=True)
    a["fecharegistro"] = fecha_iso(a["fecharegistro"])
    fuera = (a["fecharegistro"] > FECHA_CORTE).sum()
    a = a[a["fecharegistro"] <= FECHA_CORTE]
    exactos = a.duplicated().sum()
    a = a.drop_duplicates()
    repetidos = a["identificador"].duplicated().sum()

    print(f"   Adiciones del estudio: {len(a):,} en {a['id_contrato'].nunique():,} contratos")
    guardar(a, "adiciones_atlantico.csv")
    registrar("1.4", "Adiciones", "adiciones_atlantico.csv", leidas, len(a),
              f"posteriores al corte: {fuera}; duplicados exactos: {exactos}; "
              f"identificadores repetidos: {repetidos}")
    print("Listo. Siguiente paso: python 05_modificaciones.py")


if __name__ == "__main__":
    main()
