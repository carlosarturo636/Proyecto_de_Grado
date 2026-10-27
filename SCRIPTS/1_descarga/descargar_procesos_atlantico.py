# -*- coding: utf-8 -*-
"""
Descarga de SECOP II - Procesos de Contratación (p6dx-8zbt), solo Departamento del Atlántico.

Para qué sirve: el conjunto de Contratos guarda el valor y el plazo vigentes, ya actualizados
con adiciones y prórrogas. El valor y el plazo pactados al momento de la firma se toman de
Procesos:
    valor_total_adjudicacion / precio_base  -> valor inicial
    duracion + unidad_de_duracion           -> plazo inicial
Se une con Contratos por: id_del_portafolio == "Proceso de Compra".

El volumen es pequeño (entre 10.000 y 40.000 procesos por año en el Atlántico), así que el
script recorre todos los años de publicación (2019 a 2024, más los procesos sin fecha de
publicación) y guarda un archivo por año.

Uso (desde la carpeta donde se guardarán los archivos):
    python descargar_procesos_atlantico.py

Cada página de 5.000 registros se intenta hasta 3 veces, con 200 s de espera por intento, y el
avance de cada año se guarda en un punto de control (checkpoint_procesos_<AÑO>.csv). Si el portal
deja de responder y la descarga se detiene, basta con ejecutar de nuevo el mismo comando: los
años terminados se omiten y el incompleto continúa desde su punto de control.

Salida: procesos_atlantico_<AÑO>.csv (y procesos_atlantico_sin_fecha.csv)
"""

import io
import os
import time
import pandas as pd
import requests

try:
    # Credenciales de la API de datos.gov.co: archivo local que NO se sube a GitHub
    from credenciales_api import APP_TOKEN_ID, APP_TOKEN_SECRET
except ImportError:
    APP_TOKEN_ID = os.environ.get("SODA_APP_TOKEN_ID", "")
    APP_TOKEN_SECRET = os.environ.get("SODA_APP_TOKEN_SECRET", "")

URL_QUERY = "https://www.datos.gov.co/api/v3/views/p6dx-8zbt/query.csv"
COLUMNAS = (
    "id_del_proceso, id_del_portafolio, referencia_del_proceso, entidad, nit_entidad, "
    "ordenentidad, fecha_de_publicacion_del, modalidad_de_contratacion, "
    "precio_base, valor_total_adjudicacion, adjudicado, duracion, unidad_de_duracion, "
    "respuestas_al_procedimiento, proveedores_unicos_con, estado_del_procedimiento"
)

# Los contratos firmados en 2021 pueden venir de procesos publicados en 2019-2020
AÑOS = [2019, 2020, 2021, 2022, 2023, 2024]
TAMANO_PAGINA = 5000
TIMEOUT_SEG = 200   # segundos de espera máxima por intento
MAX_INTENTOS = 3    # intentos por página antes de guardar el punto de control y detenerse


def descargar(etiqueta, where):
    nombre_final = f"procesos_atlantico_{etiqueta}.csv"
    nombre_checkpoint = f"checkpoint_procesos_{etiqueta}.csv"
    if os.path.exists(nombre_final):
        print(f"{etiqueta}: ya existe '{nombre_final}'. Se omite.")
        return True

    todos, offset = [], 0
    if os.path.exists(nombre_checkpoint):
        try:
            todos = pd.read_csv(nombre_checkpoint, dtype=str).to_dict("records")
            offset = len(todos)
            print(f"{etiqueta}: se encontró un punto de control con {offset:,} filas; la descarga continúa desde ahí.")
        except pd.errors.EmptyDataError:
            pass

    print(f"{etiqueta}: descargando")
    while True:
        query = (f"SELECT {COLUMNAS} WHERE {where} ORDER BY id_del_proceso "
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
            if todos:
                pd.DataFrame(todos).to_csv(nombre_checkpoint, index=False, encoding="utf-8-sig")
            print(f"ADVERTENCIA: la descarga de {etiqueta} falló {MAX_INTENTOS} veces seguidas en la página que empieza "
                  f"en el registro {offset:,} (el portal no respondió). Para continuar, vuelva a ejecutar el mismo "
                  "comando: los años terminados se omiten y este continúa desde su punto de control.")
            return False

        pagina = pd.read_csv(io.StringIO(r.text), dtype=str)
        if len(pagina) == 0:
            break
        todos.extend(pagina.to_dict("records"))
        offset += TAMANO_PAGINA
        pd.DataFrame(todos).to_csv(nombre_checkpoint, index=False, encoding="utf-8-sig")
        time.sleep(0.2)
        if len(pagina) < TAMANO_PAGINA:
            break

    df = pd.DataFrame(todos)
    df.to_csv(nombre_final, index=False, encoding="utf-8-sig")
    if os.path.exists(nombre_checkpoint):
        os.remove(nombre_checkpoint)
    print(f"{etiqueta} completo: {len(df):,} procesos.\n")
    return True


def main():
    print("=" * 80)
    print("DESCARGA PROCESOS DE CONTRATACION - ATLANTICO (SECOP II - p6dx-8zbt)")
    print("=" * 80 + "\n")
    base = "`departamento_entidad` = 'Atlántico'"
    for anio in AÑOS:
        where = (f"{base} AND `fecha_de_publicacion_del` >= '{anio}-01-01' "
                 f"AND `fecha_de_publicacion_del` < '{anio + 1}-01-01'")
        if not descargar(str(anio), where):
            return
        time.sleep(2)
    descargar("sin_fecha", f"{base} AND `fecha_de_publicacion_del` IS NULL")


if __name__ == "__main__":
    main()
