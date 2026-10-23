"""
Paso 4b. Diagnóstico de la fuga de información en la validación cruzada (secciones 7.4.3 y 8.3.1).

Compara, con los mismos modelos e hiperparámetros seleccionados en 04_modelos.py, dos formas de
formar las 15 particiones de la validación cruzada dentro del conjunto de entrenamiento (2021-2023):
  - aleatoria estratificada: los contratos se reparten al azar entre particiones;
  - estratificada y agrupada (la usada en el estudio): los contratos de una misma entidad firmados
    en un mismo mes de un mismo año quedan siempre en la misma partición.
Y las contrasta con el desempeño en el conjunto de prueba (2024), que ninguna de las dos toca.

También describe los grupos entidad-año-mes (cuántos contratos reúnen y cómo se concentran las
alertas en ellos) y vuelve a dibujar la figura de ventaja frente a prevalencia de 04_modelos.py.

Requiere haber ejecutado antes 04_modelos.py.
"""
import sys
import time
import importlib
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
from sklearn.base import clone
from sklearn.metrics import average_precision_score
from sklearn.model_selection import StratifiedKFold

sys.path.insert(0, str(Path(__file__).resolve().parent))
m4 = importlib.import_module("04_modelos")
XGBPonderado = m4.XGBPonderado   # para leer los modelos guardados por 04_modelos.py
proxy = m4.proxy


def log(msg):
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def auc_pr_cv(pipe, params, X, y, particiones):
    valores = []
    for tr, va in particiones:
        m = clone(pipe).set_params(**params).fit(X.iloc[tr], y[tr])
        valores.append(average_precision_score(y[va], m.predict_proba(X.iloc[va])[:, 1]))
    return np.array(valores)


def main():
    inicio = time.time()
    log("PASO 4b - DIAGNÓSTICO DE LAS PARTICIONES")
    t, cat, binarias, num, _ = m4.cargar()
    X = t[cat + binarias + num]
    y = proxy.etiquetar(t, **proxy.BASE_UMBRALES)[0]["alerta"].to_numpy()
    ent, ytr, yte = m4.partir(t, y)
    tent = t[ent].reset_index(drop=True)
    Xtr = X[ent].reset_index(drop=True)
    agrupadas = m4.particiones_agrupadas(tent, Xtr, ytr)
    aleatorias = []
    for r in range(m4.R):
        aleatorias += list(StratifiedKFold(n_splits=m4.K, shuffle=True, random_state=m4.SEMILLA + r).split(Xtr, ytr))
    pipes = m4.modelos(cat, binarias, num)

    filas = []
    for k in m4.NOMBRES:
        params = joblib.load(m4.CACHE / f"busqueda_{k}.joblib")["params"]
        prueba = average_precision_score(yte, joblib.load(m4.CACHE / f"base_{k}.joblib")["p_prueba"])
        log(f"  {m4.NOMBRES[k]}: validación aleatoria ({len(aleatorias)} particiones)")
        a = auc_pr_cv(pipes[k], params, Xtr, ytr, aleatorias)
        log(f"  {m4.NOMBRES[k]}: validación agrupada ({len(agrupadas)} particiones)")
        g = auc_pr_cv(pipes[k], params, Xtr, ytr, agrupadas)
        filas.append({"modelo": m4.NOMBRES[k],
                      "AUC_PR_cv_aleatoria_media": a.mean(), "AUC_PR_cv_aleatoria_desv": a.std(ddof=1),
                      "AUC_PR_cv_agrupada_media": g.mean(), "AUC_PR_cv_agrupada_desv": g.std(ddof=1),
                      "AUC_PR_prueba_2024": prueba,
                      "sobrestimacion_aleatoria_vs_prueba": a.mean() - prueba,
                      "sobrestimacion_agrupada_vs_prueba": g.mean() - prueba})
    res = pd.DataFrame(filas).round(4)
    res.to_csv(m4.SAL / "diagnostico_particiones.csv", index=False, encoding="utf-8-sig")
    print(res.to_string(index=False))

    # Grupos entidad-año-mes en el conjunto de entrenamiento
    grupo = (tent["codigo_entidad"].astype(str) + "_" + tent["anio_firma"].astype(str) + "_"
             + tent["mes_firma"].astype(str))
    tam = grupo.map(grupo.value_counts())
    alertas_grupo = pd.Series(ytr).groupby(grupo.to_numpy()).transform("sum").to_numpy()
    con_alerta = ytr == 1
    desc = pd.DataFrame([
        {"indicador": "Grupos entidad-año-mes en entrenamiento", "valor": grupo.nunique()},
        {"indicador": "Contratos por grupo (mediana)", "valor": float(grupo.value_counts().median())},
        {"indicador": "Contratos por grupo (máximo)", "valor": int(grupo.value_counts().max())},
        {"indicador": "Contratos en grupos de 10 o más contratos (%)", "valor": round((tam >= 10).mean() * 100, 1)},
        {"indicador": "Contratos con alerta cuyo grupo tiene otras alertas (%)",
         "valor": round((alertas_grupo[con_alerta] >= 2).mean() * 100, 1)},
        {"indicador": "Contratos con alerta cuyo grupo tiene 10 o más alertas (%)",
         "valor": round((alertas_grupo[con_alerta] >= 10).mean() * 100, 1)},
    ])
    desc.to_csv(m4.SAL / "diagnostico_grupos.csv", index=False, encoding="utf-8-sig")
    print(desc.to_string(index=False))

    # Figura de ventaja frente a prevalencia, con rótulos sin superposición
    esc = pd.read_csv(m4.SAL / "escenarios_modelos.csv")
    m4.figura_ventaja(esc)
    log(f"Listo en {(time.time() - inicio) / 60:.1f} minutos. Resultados en {m4.SAL}")


if __name__ == "__main__":
    main()
