# -*- coding: utf-8 -*-
"""
Descarga de SECOP II - Adiciones (cb9c-h8sn), nivel nacional, un archivo por mes.

Filtra por la fecha de registro (`fecharegistro`) y no descarga nada posterior a la
fecha de corte de observación del estudio (31/08/2026).

Uso (desde la carpeta donde se guardarán los archivos):
    python descargar_adiciones_mes.py 2026 3     descarga solo marzo de 2026
    python descargar_adiciones_mes.py 2021       descarga los 12 meses de 2021, uno por archivo

Cada página de 5.000 registros se intenta hasta 3 veces, con 200 s de espera por intento, y el
avance del mes se guarda en un punto de control (checkpoint_adiciones_<AÑO>_<MES>.csv). Si el
portal deja de responder y la descarga se detiene, basta con ejecutar de nuevo el mismo comando:
los meses que ya tienen archivo final se omiten y el mes incompleto continúa desde su punto de
control.

Salida: adiciones_nacional_<AÑO>_<MES>.csv
"""

import io
import os
import sys
import time
import pandas as pd
import requests

try:
    # Credenciales de la API de datos.gov.co: archivo local que NO se sube a GitHub
    from credenciales_api import APP_TOKEN_ID, APP_TOKEN_SECRET
except ImportError:
    APP_TOKEN_ID = os.environ.get("SODA_APP_TOKEN_ID", "")
    APP_TOKEN_SECRET = os.environ.get("SODA_APP_TOKEN_SECRET", "")

URL_QUERY = "https://www.datos.gov.co/api/v3/views/cb9c-h8sn/query.csv"
COLUMNAS = "identificador, id_contrato, tipo, descripcion, fecharegistro"

FECHA_CORTE_EXCLUSIVA = "2026-09-01"   # observacion hasta el 31/08/2026
TAMANO_PAGINA = 5000
TIMEOUT_SEG = 200   # segundos de espera máxima por intento
MAX_INTENTOS = 3    # intentos por página antes de guardar el punto de control y detenerse


def rango_mes(anio, mes):
    inicio = f"{anio:04d}-{mes:02d}-01"
    fin = f"{anio + 1:04d}-01-01" if mes == 12 else f"{anio:04d}-{mes + 1:02d}-01"
    return inicio, min(fin, FECHA_CORTE_EXCLUSIVA)


def descargar_mes(anio, mes):
    etiqueta = f"{anio:04d}_{mes:02d}"
    nombre_final = f"adiciones_nacional_{etiqueta}.csv"
    nombre_checkpoint = f"checkpoint_adiciones_{etiqueta}.csv"

    inicio, fin = rango_mes(anio, mes)
    if inicio >= FECHA_CORTE_EXCLUSIVA:
        print(f"- {etiqueta}: posterior a la fecha de corte (31/08/2026). Se omite.")
        return True
    if os.path.exists(nombre_final):
        print(f"{etiqueta}: ya existe '{nombre_final}'. Se omite.")
        return True

    where = f"`fecharegistro` >= '{inicio}' AND `fecharegistro` < '{fin}'"

    if os.path.exists(nombre_checkpoint):
        todos = pd.read_csv(nombre_checkpoint, dtype=str).to_dict("records")
        offset = len(todos)
        print(f"{etiqueta}: se encontró un punto de control con {offset:,} filas; la descarga continúa desde ahí.")
    else:
        todos, offset = [], 0

    print(f"{etiqueta}: descargando registros del {inicio} hasta antes del {fin}")
    pagina_num = offset // TAMANO_PAGINA

    while True:
        pagina_num += 1
        # ORDER BY identificador: orden estable para que LIMIT/OFFSET no repita ni salte filas
        query = (f"SELECT {COLUMNAS} WHERE {where} ORDER BY identificador "
                 f"LIMIT {TAMANO_PAGINA} OFFSET {offset}")

        r = None
        for intento in range(1, MAX_INTENTOS + 1):
            t0 = time.time()
            try:
                r = requests.get(URL_QUERY, params={"query": query},
                                 auth=(APP_TOKEN_ID, APP_TOKEN_SECRET), timeout=TIMEOUT_SEG)
                r.raise_for_status()
                break
            except requests.exceptions.RequestException as error:
                print(f"   Intento {intento} de {MAX_INTENTOS} fallido en la página que empieza en el registro {offset:,} "
                      f"({type(error).__name__} tras {time.time() - t0:.1f} s)")
                r = None
                if intento < MAX_INTENTOS:
                    time.sleep(10 * intento)

        if r is None:
            pd.DataFrame(todos).to_csv(nombre_checkpoint, index=False, encoding="utf-8-sig")
            print(f"\nADVERTENCIA: la página que empieza en el registro {offset:,} falló {MAX_INTENTOS} veces seguidas "
                  "(el portal no respondió).")
            print(f"   Las {len(todos):,} filas descargadas se guardaron en el punto de control '{nombre_checkpoint}'.")
            print("   Para continuar, vuelva a ejecutar el mismo comando: la descarga se retoma desde ese punto.")
            return False

        pagina = pd.read_csv(io.StringIO(r.text), dtype=str)
        if len(pagina) == 0:
            break

        todos.extend(pagina.to_dict("records"))
        offset += TAMANO_PAGINA

        if pagina_num % 5 == 0 or pagina_num == 1:
            print(f"   Página {pagina_num}: {len(todos):,} filas")
            pd.DataFrame(todos).to_csv(nombre_checkpoint, index=False, encoding="utf-8-sig")

        time.sleep(0.2)
        if len(pagina) < TAMANO_PAGINA:
            break

    df = pd.DataFrame(todos)
    df.to_csv(nombre_final, index=False, encoding="utf-8-sig")
    if os.path.exists(nombre_checkpoint):
        os.remove(nombre_checkpoint)
    print(f"{etiqueta} completo: {len(df):,} filas "
          f"({df['identificador'].nunique():,} identificadores únicos).\n")
    return True


def main():
    if len(sys.argv) == 3:
        meses = [(int(sys.argv[1]), int(sys.argv[2]))]
    elif len(sys.argv) == 2:
        anio = int(sys.argv[1])
        meses = [(anio, m) for m in range(1, 13)]
    else:
        print("Uso: python descargar_adiciones_mes.py <AÑO> [<MES>]")
        return

    print("=" * 80)
    print("DESCARGA ADICIONES (SECOP II - cb9c-h8sn) - corte 31/08/2026")
    print("=" * 80 + "\n")
    for anio, mes in meses:
        if not descargar_mes(anio, mes):
            print(f"La descarga se detuvo en {anio}-{mes:02d}. Al volver a ejecutar el mismo comando, los meses "
                  "terminados se omiten y este mes continúa desde su punto de control.")
            return
        time.sleep(2)


if __name__ == "__main__":
    main()
