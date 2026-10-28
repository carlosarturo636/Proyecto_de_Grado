# -*- coding: utf-8 -*-
"""
Descarga de SECOP II - Modificaciones a contratos (u8cx-r425), nivel nacional, un mes por archivo.

Usa el punto de acceso de consulta (query.csv) con las credenciales definidas en
credenciales_api.py. Se ejecuta un mes a la vez, a propósito: cada mes queda en su propio
archivo, de modo que si el portal deja de responder a mitad de un mes, solo ese mes se ve afectado.

Uso (desde la carpeta donde se guardarán los archivos):
  Opción A, con el año y el mes en la línea de comandos:
    python descargar_modificaciones_mes.py 2025 1
    python descargar_modificaciones_mes.py 2025 2
    ...
  Opción B, sin argumentos: usa los valores de AÑO y MES definidos más abajo en este archivo.

Cada página de 5.000 registros se intenta hasta 3 veces, con 200 s de espera por intento, y el
avance se guarda en un punto de control (checkpoint_modificaciones_<AÑO>_<MES>.csv). Si el portal
deja de responder y la descarga se detiene, basta con ejecutar de nuevo el mismo comando: la
descarga continúa desde el punto de control sin perder lo ya descargado.

Salida: modificaciones_nacional_<AÑO>_<MES>.csv
"""

import calendar
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

URL_QUERY = "https://www.datos.gov.co/api/v3/views/u8cx-r425/query.csv"

COLUMNAS = (
    "fecha_de_carga, fuente_del_registro, identificador, direccion_de_la_operacion, "
    "fecha_de_aprobacion, codigo_bpin, a_o_bpin, marca_de_tiempo_cdc, "
    "fecha_inicio_contrato, fecha_fin_contrato, version_anterior_del_contrato, "
    "archivo_version_anterior, nombre_aplicacion_creacion, codigo_empresa_creadora, "
    "fecha_creacion, fecha_inicio_entrega, fecha_fin_entrega, descripcion, "
    "dias_extendidos, liquidacion, fecha_inicio_liquidacion, fecha_fin_liquidacion, "
    "acta_de_liquidacion, proposito_modificacion, valor_modificacion, metodo_pago, "
    "identificador_requerimiento, id_contrato, estado_modificacion, "
    "identificador_modificacion, autor_version, codigo_empresa_de_version, "
    "fecha_version, numero_version, sustituto_version"
)

# --- Opcion B: cambia aqui el año y el mes si no pasas argumentos ---
AÑO = 2025
MES = 1
# ---------------------------------------------------------------------

TAMANO_PAGINA = 5000
TIMEOUT_SEG = 200   # segundos de espera máxima por intento
MAX_INTENTOS = 3    # intentos por página antes de guardar el punto de control y detenerse


def credenciales():
    return (APP_TOKEN_ID, APP_TOKEN_SECRET)


def rango_mes(anio, mes):
    inicio = f"{anio:04d}-{mes:02d}-01"
    if mes == 12:
        fin = f"{anio + 1:04d}-01-01"
    else:
        fin = f"{anio:04d}-{mes + 1:02d}-01"
    return inicio, fin


def main():
    if len(sys.argv) == 3:
        anio = int(sys.argv[1])
        mes = int(sys.argv[2])
    else:
        anio = AÑO
        mes = MES

    etiqueta = f"{anio:04d}_{mes:02d}"
    nombre_checkpoint = f"checkpoint_modificaciones_{etiqueta}.csv"
    nombre_final = f"modificaciones_nacional_{etiqueta}.csv"

    print("=" * 80)
    print(f"DESCARGA MODIFICACIONES {anio}-{mes:02d} (SECOP II - u8cx-r425)")
    print("=" * 80 + "\n")

    if os.path.exists(nombre_final):
        conteo = sum(1 for _ in open(nombre_final, encoding="utf-8-sig")) - 1
        print(f"Ya existe '{nombre_final}' con {conteo:,} filas. No se vuelve a descargar.")
        print("  Para descargarlo de nuevo, elimine ese archivo y vuelva a ejecutar el comando.")
        return

    inicio, fin = rango_mes(anio, mes)
    where = f"`fecha_de_aprobacion` >= '{inicio}' AND `fecha_de_aprobacion` < '{fin}'"

    if os.path.exists(nombre_checkpoint):
        checkpoint = pd.read_csv(nombre_checkpoint, low_memory=False)
        todos = checkpoint.to_dict("records")
        offset = len(todos)
        print(f"Se encontró un punto de control con {len(todos):,} filas ya descargadas.")
        print(f"  La descarga continúa desde el registro {offset:,}.\n")
    else:
        todos = []
        offset = 0

    pagina_num = offset // TAMANO_PAGINA

    while True:
        pagina_num += 1
        query = f"SELECT {COLUMNAS} WHERE {where} LIMIT {TAMANO_PAGINA} OFFSET {offset}"

        r = None
        for intento in range(1, MAX_INTENTOS + 1):
            inicio_t = time.time()
            try:
                r = requests.get(
                    URL_QUERY, params={"query": query}, auth=credenciales(), timeout=TIMEOUT_SEG
                )
                r.raise_for_status()
                duracion = time.time() - inicio_t
                if duracion > 15:
                    print(f"   La página que empieza en el registro {offset:,} respondió en el intento "
                          f"{intento}, pero tardó {duracion:.1f} s")
                break
            except requests.exceptions.RequestException as error:
                duracion = time.time() - inicio_t
                print(f"   Intento {intento} de {MAX_INTENTOS} fallido en la página que empieza en el registro {offset:,} "
                      f"({type(error).__name__} tras {duracion:.1f} s)")
                r = None
                if intento < MAX_INTENTOS:
                    time.sleep(10 * intento)

        if r is None:
            print(f"\nADVERTENCIA: la página que empieza en el registro {offset:,} falló {MAX_INTENTOS} veces seguidas "
                  "(el portal no respondió).")
            pd.DataFrame(todos).to_csv(nombre_checkpoint, index=False, encoding="utf-8-sig")
            print(f"   Las {len(todos):,} filas descargadas se guardaron en el punto de control '{nombre_checkpoint}'.")
            print("   Para continuar, vuelva a ejecutar el script con el mismo año y mes: la descarga se retoma desde ese punto.")
            return

        pagina = pd.read_csv(io.StringIO(r.text), low_memory=False)

        if len(pagina) == 0:
            break

        todos.extend(pagina.to_dict("records"))
        offset += TAMANO_PAGINA

        if pagina_num % 5 == 0 or pagina_num == 1:
            print(f"   Página {pagina_num}: {len(todos):,} filas descargadas hasta ahora")
            pd.DataFrame(todos).to_csv(nombre_checkpoint, index=False, encoding="utf-8-sig")

        time.sleep(0.2)

        if len(pagina) < TAMANO_PAGINA:
            break

    df = pd.DataFrame(todos)
    df.to_csv(nombre_final, index=False, encoding="utf-8-sig")
    if os.path.exists(nombre_checkpoint):
        os.remove(nombre_checkpoint)

    print(f"\nCompleto: {len(df):,} filas guardadas en '{nombre_final}'.")
    print("  Para descargar el mes siguiente:")
    siguiente_mes = mes + 1 if mes < 12 else 1
    siguiente_anio = anio if mes < 12 else anio + 1
    print(f"  python descargar_modificaciones_mes.py {siguiente_anio} {siguiente_mes}")


if __name__ == "__main__":
    main()
