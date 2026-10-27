# -*- coding: utf-8 -*-
"""
PASO 1.1 - CONTRATOS
Une los 4 archivos anuales (2021-2024, ya filtrados al Atlantico), verifica
que no haya contratos repetidos, quita las columnas con datos personales
y normaliza fechas y valores. NO aplica todavia los criterios de poblacion
ni de inclusion (eso es Metodologia 7.2, se aplica en el paso 2).

Salida en 02_DEPURADOS:
    contratos_atlantico.csv        una fila por contrato
    ids_contratos_estudio.csv      lista de ID de contrato (la usan los demas scripts)

Uso:  python 01_contratos.py
"""

import pandas as pd
from comun import CRUDOS, ARCHIVO_IDS, fecha_iso, numero, registrar, guardar

# Columnas con datos de personas: no se conservan (ética de datos, sección 7.4.7)
PERSONALES = [
    "Documento Proveedor", "Proveedor Adjudicado",
    "Nombre Representante Legal", "Nacionalidad Representante Legal",
    "Domicilio Representante Legal", "Tipo de Identificación Representante Legal",
    "Identificación Representante Legal", "Género Representante Legal",
    "Nombre del banco", "Tipo de cuenta", "Número de cuenta",
    "Nombre ordenador del gasto", "Tipo de documento Ordenador del gasto",
    "Número de documento Ordenador del gasto",
    "Nombre supervisor", "Tipo de documento supervisor", "Número de documento supervisor",
    "Nombre Ordenador de Pago", "Tipo de documento Ordenador de Pago",
    "Número de documento Ordenador de Pago",
]


def main():
    print("=" * 70 + "\nPASO 1.1 - CONTRATOS\n" + "=" * 70)
    partes = []
    for f in sorted((CRUDOS / "CONTRATOS").glob("*.csv")):
        d = pd.read_csv(f, dtype=str, low_memory=False)
        print(f"   {f.name}: {len(d):,} filas")
        registrar("1.1", "Contratos", f.name, len(d), len(d), "lectura")
        partes.append(d)
    c = pd.concat(partes, ignore_index=True)
    leidas = len(c)

    exactos = c.duplicated().sum()
    c = c.drop_duplicates()
    repetidos = c["ID Contrato"].duplicated().sum()
    if repetidos:
        print(f"   ADVERTENCIA: {repetidos} ID de contrato aparecen más de una vez con datos distintos "
              "(se conservan todos; revisar en el paso 2)")

    quitar = [k for k in PERSONALES if k in c.columns]
    c = c.drop(columns=quitar)

    for col in ["Fecha de Firma", "Fecha de Inicio del Contrato", "Fecha de Fin del Contrato",
                "Ultima Actualizacion", "Fecha Inicio Liquidacion", "Fecha Fin Liquidacion"]:
        if col in c.columns:
            c[col] = fecha_iso(c[col])
    for col in ["Valor del Contrato", "Valor de pago adelantado", "Valor Facturado",
                "Valor Pendiente de Pago", "Valor Pagado", "Valor Amortizado",
                "Valor Pendiente de Amortizacion", "Valor Pendiente de Ejecucion",
                "Saldo CDP", "Saldo Vigencia"]:
        if col in c.columns:
            c[col] = numero(c[col], estilo="co")

    anio = c["Fecha de Firma"].str[:4]
    print("   Contratos por año de firma:", anio.value_counts().sort_index().to_dict())

    guardar(c, "contratos_atlantico.csv")
    ids = pd.DataFrame({"id_contrato": sorted(c["ID Contrato"].dropna().unique())})
    ids.to_csv(ARCHIVO_IDS, index=False, encoding="utf-8-sig")
    print(f"   Archivo escrito: {ARCHIVO_IDS} ({len(ids):,} contratos)")

    registrar("1.1", "Contratos", "contratos_atlantico.csv", leidas, len(c),
              f"duplicados exactos eliminados: {exactos}; ID repetidos: {repetidos}; "
              f"columnas personales eliminadas: {len(quitar)}")
    print("Listo. Siguiente paso: python 02_procesos.py")


if __name__ == "__main__":
    main()
