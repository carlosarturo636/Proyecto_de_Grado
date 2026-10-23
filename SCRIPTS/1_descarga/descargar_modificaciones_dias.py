# -*- coding: utf-8 -*-
"""
Descarga de SECOP II - Modificaciones a contratos (u8cx-r425), nivel nacional, un archivo por día.

Se usó para los días 28 a 31 de agosto de 2026, porque la exportación desde el portal y la
descarga mensual fallaban siempre a partir del 28 de agosto (sección 8.1.1 del documento).
Cada día se descarga en un archivo propio; si la descarga de un día completo falla, el script
lo divide automáticamente en bloques de una hora.

Uso (desde la carpeta donde se guardarán los archivos):
    python descargar_modificaciones_dias.py 2026-08-28 2026-08-31

Salida: modificaciones_dia_2026_08_28.csv, ..._29, ..._30, ..._31
(si un día se divide por horas: modificaciones_dia_2026_08_28_h00.csv, ...)

Cada página de 5.000 registros se intenta hasta 3 veces, con 200 s de espera por intento, y el
avance se guarda en un punto de control (checkpoint_dia_<FECHA>.csv). Si el portal deja de
responder y la descarga se detiene, basta con ejecutar de nuevo el mismo comando: los días y
bloques terminados se omiten y el incompleto continúa desde su punto de control.
"""

import datetime as dt
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

TAMANO_PAGINA = 5000
TIMEOUT_SEG = 200   # segundos de espera máxima por intento
MAX_INTENTOS = 3    # intentos por página antes de guardar el punto de control y detenerse


def bajar_ventana(etiqueta, desde, hasta):
    """Descarga [desde, hasta) en un archivo. Devuelve True si termina."""
    nombre_final = f"modificaciones_dia_{etiqueta}.csv"
    nombre_checkpoint = f"checkpoint_dia_{etiqueta}.csv"
    if os.path.exists(nombre_final):
        print(f"{etiqueta}: ya existe. Se omite.")
        return True

    todos, offset = [], 0
    if os.path.exists(nombre_checkpoint):
        try:
            todos = pd.read_csv(nombre_checkpoint, dtype=str).to_dict("records")
            offset = len(todos)
            print(f"{etiqueta}: se encontró un punto de control con {offset:,} filas; la descarga continúa desde ahí.")
        except pd.errors.EmptyDataError:
            pass

    where = f"`fecha_de_aprobacion` >= '{desde}' AND `fecha_de_aprobacion` < '{hasta}'"
    print(f"{etiqueta}: descargando aprobaciones desde {desde} hasta antes de {hasta}")
    while True:
        query = f"SELECT {COLUMNAS} WHERE {where} LIMIT {TAMANO_PAGINA} OFFSET {offset}"
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
            if todos:
                pd.DataFrame(todos).to_csv(nombre_checkpoint, index=False, encoding="utf-8-sig")
            return False

        pagina = pd.read_csv(io.StringIO(r.text), dtype=str)
        if len(pagina) == 0:
            break
        todos.extend(pagina.to_dict("records"))
        offset += TAMANO_PAGINA
        if (offset // TAMANO_PAGINA) % 5 == 0:
            print(f"   {len(todos):,} filas")
            pd.DataFrame(todos).to_csv(nombre_checkpoint, index=False, encoding="utf-8-sig")
        time.sleep(0.2)
        if len(pagina) < TAMANO_PAGINA:
            break

    pd.DataFrame(todos).to_csv(nombre_final, index=False, encoding="utf-8-sig")
    if os.path.exists(nombre_checkpoint):
        os.remove(nombre_checkpoint)
    print(f"{etiqueta} completo: {len(todos):,} filas.\n")
    return True


def main():
    if len(sys.argv) != 3:
        print("Uso: python descargar_modificaciones_dias.py AAAA-MM-DD AAAA-MM-DD")
        return
    inicio = dt.date.fromisoformat(sys.argv[1])
    fin = dt.date.fromisoformat(sys.argv[2])

    dia = inicio
    while dia <= fin:
        etq = dia.strftime("%Y_%m_%d")
        sig = dia + dt.timedelta(days=1)
        horas_hechas = any(f.startswith(f"modificaciones_dia_{etq}_h") for f in os.listdir("."))
        if not horas_hechas and bajar_ventana(etq, dia.isoformat(), sig.isoformat()):
            dia = sig
            continue
        # El dia completo se resistio: se parte en bloques de 1 hora
        print(f"   {etq}: la descarga del día completo falló; se intenta por bloques de una hora")
        for h in range(24):
            desde = f"{dia.isoformat()}T{h:02d}:00:00"
            hasta = f"{dia.isoformat()}T{h + 1:02d}:00:00" if h < 23 else f"{sig.isoformat()}T00:00:00"
            if not bajar_ventana(f"{etq}_h{h:02d}", desde, hasta):
                print(f"\nADVERTENCIA: el bloque {etq}, hora {h:02d}, falló {MAX_INTENTOS} veces seguidas (el portal no "
                      "respondió). Para continuar, vuelva a ejecutar el mismo comando: los días y bloques "
                      "terminados se omiten y el incompleto continúa desde su punto de control.")
                return
        dia = sig

    print("Listo. Ubica los archivos en 01_CRUDOS/MODIFICACIONES y verifica los conteos contra el portal.")


if __name__ == "__main__":
    main()
