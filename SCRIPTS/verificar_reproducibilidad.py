"""
Verificación de reproducibilidad (sección 7.4.7).

Vuelve a ejecutar, desde los datos crudos, todos los scripts de consolidación y de modelado,
pero escribe los resultados en una carpeta aparte (VERIFICACION_MODELOS) sin tocar los
originales (02_DEPURADOS y 03_MODELADO). Al final compara, archivo por archivo, cada CSV
nuevo con el original y escribe el informe VERIFICACION_MODELOS/comparacion.csv.

Uso (desde la carpeta SCRIPTS):
    python verificar_reproducibilidad.py

Tarda cerca de una hora: la consolidación de Modificaciones lee unos 25 GB y 04_modelos.py
repite la búsqueda de hiperparámetros desde cero. Si se interrumpe, al volver a ejecutarlo
retoma: cada script guarda sus propios puntos de control dentro de VERIFICACION_MODELOS.
"""
import os
import sys
import time
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

SCRIPTS = Path(__file__).resolve().parent
BASE = SCRIPTS.parent
VER = BASE / "VERIFICACION_MODELOS"
DEP_ORIG, MOD_ORIG = BASE / "02_DEPURADOS", BASE / "03_MODELADO"
DEP_VER, MOD_VER = VER / "02_DEPURADOS", VER / "03_MODELADO"

PASOS = [
    ("2_consolidacion", "01_contratos.py"),
    ("2_consolidacion", "02_procesos.py"),
    ("2_consolidacion", "03_proveedores.py"),
    ("2_consolidacion", "04_adiciones.py"),
    ("2_consolidacion", "05_modificaciones.py"),
    ("3_modelado", "01_tabla_modelado.py"),
    ("3_modelado", "01b_revision_calidad.py"),
    ("3_modelado", "02_caracterizacion.py"),
    ("3_modelado", "03_proxy_sensibilidad.py"),
    ("3_modelado", "04_modelos.py"),
    ("3_modelado", "04b_diagnostico_particiones.py"),
    ("3_modelado", "05_shap.py"),
    ("3_modelado", "06_priorizacion.py"),
]

# Columnas que cambian en cada ejecución y no forman parte de los resultados
IGNORAR = {"fecha_hora", "minutos", "minutos_busqueda", "mean_fit_time", "std_fit_time",
           "mean_score_time", "std_score_time"}
TOLERANCIA = 1e-6


def ejecutar():
    VER.mkdir(exist_ok=True)
    entorno = {**os.environ, "SALIDA_DEPURADOS": str(DEP_VER), "SALIDA_MODELADO": str(MOD_VER),
               "PYTHONIOENCODING": "utf-8"}
    entorno.pop("PRUEBA_RAPIDA", None)
    hechos = VER / "_pasos_terminados.txt"
    terminados = set(hechos.read_text(encoding="utf-8").split()) if hechos.exists() else set()
    tiempos = []
    for carpeta, script in PASOS:
        clave = f"{carpeta}/{script}"
        if clave in terminados:
            print(f"{clave} ya se había ejecutado. Se omite.", flush=True)
            continue
        print(f"Ejecutando {clave}", flush=True)
        t0 = time.time()
        with open(VER / f"salida_{script.replace('.py', '')}.txt", "w", encoding="utf-8") as log:
            r = subprocess.run([sys.executable, script], cwd=SCRIPTS / carpeta, env=entorno,
                               stdout=log, stderr=subprocess.STDOUT)
        minutos = (time.time() - t0) / 60
        tiempos.append({"script": clave, "minutos": round(minutos, 2), "codigo_salida": r.returncode})
        if r.returncode != 0:
            raise SystemExit(f"   ERROR: {clave} terminó con error. El detalle está en {VER / f'salida_{script[:-3]}.txt'}")
        print(f"   listo en {minutos:.1f} min", flush=True)
        with open(hechos, "a", encoding="utf-8") as f:
            f.write(clave + "\n")
    if tiempos:
        pd.DataFrame(tiempos).to_csv(VER / "tiempos_verificacion.csv", index=False, encoding="utf-8-sig",
                                     mode="a", header=not (VER / "tiempos_verificacion.csv").exists())


def comparar_csv(a, b):
    """Devuelve (resultado, detalle) al comparar dos CSV."""
    x = pd.read_csv(a, dtype=str, keep_default_na=False)
    y = pd.read_csv(b, dtype=str, keep_default_na=False)
    if x.shape != y.shape:
        return "Diferente", f"tamaño {x.shape} frente a {y.shape}"
    if list(x.columns) != list(y.columns):
        return "Diferente", "columnas distintas"
    diferencias, max_dif = [], 0.0
    for col in x.columns:
        if col in IGNORAR or "time" in col:
            continue
        if (x[col] == y[col]).all():
            continue
        nx, ny = pd.to_numeric(x[col], errors="coerce"), pd.to_numeric(y[col], errors="coerce")
        numericas = nx.notna() & ny.notna()
        texto_igual = (x[col] == y[col]) | numericas
        if not texto_igual.all():
            diferencias.append(f"{col}: {int((~texto_igual).sum())} celdas de texto distintas")
            continue
        d = float(np.nanmax(np.abs(nx[numericas] - ny[numericas]))) if numericas.any() else 0.0
        max_dif = max(max_dif, d)
        if d > TOLERANCIA:
            diferencias.append(f"{col}: diferencia máxima {d:.6g}")
    if diferencias:
        return "Diferente", "; ".join(diferencias[:5])
    return ("Idéntico" if max_dif == 0 else "Igual dentro de la tolerancia"), (
        "" if max_dif == 0 else f"diferencia numérica máxima {max_dif:.2g}")


def comparar():
    filas = []
    for orig, ver in ((DEP_ORIG, DEP_VER), (MOD_ORIG, MOD_VER)):
        for a in sorted(orig.rglob("*.csv")):
            rel = a.relative_to(orig)
            if "_parciales" in rel.parts or "prueba_rapida" in str(rel):
                continue
            b = ver / rel
            if a.name == "resumen_consolidacion.csv":
                resultado, detalle = comparar_resumen(a, b)
            elif not b.exists():
                resultado, detalle = "Falta en la verificación", ""
            else:
                try:
                    resultado, detalle = comparar_csv(a, b)
                except Exception as e:  # archivo ilegible o vacío
                    resultado, detalle = "Error al comparar", str(e)
            filas.append({"carpeta": orig.name, "archivo": str(rel).replace("\\", "/"),
                          "resultado": resultado, "detalle": detalle})
    rep = pd.DataFrame(filas)
    rep.to_csv(VER / "comparacion.csv", index=False, encoding="utf-8-sig")
    print("\nRESUMEN DE LA COMPARACIÓN")
    print(rep["resultado"].value_counts().to_string())
    distintos = rep[~rep["resultado"].isin(["Idéntico", "Igual dentro de la tolerancia"])]
    if len(distintos):
        print("\nArchivos con diferencias:")
        print(distintos.to_string(index=False))
    print(f"\nInforme completo: {VER / 'comparacion.csv'}")


def comparar_resumen(a, b):
    """El resumen de consolidación acumula filas en cada ejecución: se comparan las últimas."""
    if not b.exists():
        return "Falta en la verificación", ""
    cols = ["paso", "fuente", "archivo", "filas_leidas", "filas_conservadas", "observacion"]
    x = pd.read_csv(a, dtype=str)[cols].drop_duplicates(["paso", "archivo"], keep="last").reset_index(drop=True)
    y = pd.read_csv(b, dtype=str)[cols].drop_duplicates(["paso", "archivo"], keep="last").reset_index(drop=True)
    return ("Idéntico", "") if x.equals(y) else ("Diferente", "conteos de consolidación distintos")


if __name__ == "__main__":
    inicio = time.time()
    ejecutar()
    comparar()
    print(f"Tiempo total: {(time.time() - inicio) / 60:.1f} minutos")
