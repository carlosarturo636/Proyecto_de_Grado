# -*- coding: utf-8 -*-
"""
PASO 1.3 - PROVEEDORES REGISTRADOS
Del archivo nacional (1,6 millones de proveedores) conserva solo los
proveedores de los contratos del estudio (Contratos."Codigo Proveedor" =
Proveedores."Codigo") y solo columnas sin datos personales: se eliminan
nombre, NIT/cedula, telefonos, correos, direcciones y representante legal.

Salida en 02_DEPURADOS:  proveedores_atlantico.csv
Uso:  python 03_proveedores.py
"""

import pandas as pd
from comun import CRUDOS, DEPURADOS, fecha_iso, registrar, guardar

CONSERVAR = ["Codigo", "Es Entidad", "Es grupo", "Esta Activa", "Fecha Creación",
             "Codigo Categoria Principal", "Departamento", "Municipio",
             "Tipo Empresa", "EsPyme", "Tamaño Entidad"]


def main():
    print("=" * 70 + "\nPASO 1.3 - PROVEEDORES\n" + "=" * 70)
    contratos = DEPURADOS / "contratos_atlantico.csv"
    if not contratos.exists():
        raise SystemExit("No se encontró 02_DEPURADOS/contratos_atlantico.csv: ejecute primero 01_contratos.py.")
    codigos = set(pd.read_csv(contratos, dtype=str, usecols=["Codigo Proveedor"])["Codigo Proveedor"].dropna())

    archivo = next((CRUDOS / "PROVEEDORES").glob("*.csv"))
    partes, leidas = [], 0
    for ch in pd.read_csv(archivo, dtype=str, usecols=CONSERVAR, chunksize=500_000):
        leidas += len(ch)
        partes.append(ch[ch["Codigo"].isin(codigos)])
    p = pd.concat(partes, ignore_index=True)
    exactos = p.duplicated().sum()
    p = p.drop_duplicates()
    repetidos = p["Codigo"].duplicated().sum()
    p["Fecha Creación"] = fecha_iso(p["Fecha Creación"])

    faltan = len(codigos - set(p["Codigo"]))
    print(f"   Proveedores del estudio encontrados: {p['Codigo'].nunique():,} de {len(codigos):,} "
          f"(sin registro: {faltan:,})")
    guardar(p, "proveedores_atlantico.csv")
    registrar("1.3", "Proveedores", "proveedores_atlantico.csv", leidas, len(p),
              f"duplicados exactos: {exactos}; códigos repetidos: {repetidos}; "
              f"proveedores sin registro: {faltan}")
    print("Listo. Siguiente paso: python 04_adiciones.py")


if __name__ == "__main__":
    main()
