# -*- coding: utf-8 -*-
"""
PASO 1.2 - PROCESOS DE CONTRATACION
Une los 7 archivos de Procesos (Atlantico, 2019-2024 + sin fecha) y conserva
solo los procesos que corresponden a contratos del estudio
(Contratos."Proceso de Compra" = Procesos.id_del_portafolio).

Si un proceso aparece en varias filas, se conservan todas y se marca
(columna filas_del_portafolio); cual fila usar se decide en el paso 2.

Salida en 02_DEPURADOS:  procesos_atlantico.csv
Uso:  python 02_procesos.py
"""

import pandas as pd
from comun import CRUDOS, DEPURADOS, fecha_iso, numero, registrar, guardar


def main():
    print("=" * 70 + "\nPASO 1.2 - PROCESOS\n" + "=" * 70)
    contratos = DEPURADOS / "contratos_atlantico.csv"
    if not contratos.exists():
        raise SystemExit("No se encontró 02_DEPURADOS/contratos_atlantico.csv: ejecute primero 01_contratos.py.")
    c = pd.read_csv(contratos, dtype=str, usecols=["ID Contrato", "Proceso de Compra"])
    usados = set(c["Proceso de Compra"].dropna())

    p = pd.concat([pd.read_csv(f, dtype=str) for f in sorted((CRUDOS / "PROCESOS").glob("*.csv"))],
                  ignore_index=True)
    leidas = len(p)
    exactos = p.duplicated().sum()
    p = p.drop_duplicates()

    p = p[p["id_del_portafolio"].isin(usados)].copy()
    p["filas_del_portafolio"] = p.groupby("id_del_portafolio")["id_del_portafolio"].transform("size")
    p["fecha_de_publicacion_del"] = fecha_iso(p["fecha_de_publicacion_del"])
    for col in ["precio_base", "valor_total_adjudicacion", "duracion",
                "respuestas_al_procedimiento", "proveedores_unicos_con"]:
        p[col] = numero(p[col])

    sin_proceso = (~c["Proceso de Compra"].isin(set(p["id_del_portafolio"]))).sum()
    multiples = (p["filas_del_portafolio"] > 1).sum()
    print(f"   Procesos conservados: {p['id_del_portafolio'].nunique():,} "
          f"({len(p):,} filas; {multiples:,} filas de procesos repetidos)")
    print(f"   Contratos sin proceso encontrado: {sin_proceso:,} de {len(c):,}")

    guardar(p, "procesos_atlantico.csv")
    registrar("1.2", "Procesos", "procesos_atlantico.csv", leidas, len(p),
              f"duplicados exactos: {exactos}; filas de procesos repetidos: {multiples}; "
              f"contratos sin proceso: {sin_proceso}")
    print("Listo. Siguiente paso: python 03_proveedores.py")


if __name__ == "__main__":
    main()
