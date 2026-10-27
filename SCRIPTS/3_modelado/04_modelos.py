"""
Paso 4. Entrenamiento, validación y comparación de modelos (secciones 7.4.2 a 7.4.5 y 8.3).

Qué hace, en este orden:
  1. Prepara los predictores de la Tabla 2 (sin los que no varían en la población) y la
     partición temporal: entrenamiento 2021-2023, prueba 2024 (sección 7.4.3).
  2. Búsqueda aleatoria de hiperparámetros con 15 particiones (5 x 3, estratificadas y agrupadas
     por entidad, año y mes de firma), optimizando AUC-PR
     (sección 7.4.4, Tabla 8).
  3. Evaluación del escenario base: métricas por partición, umbral que maximiza el F1 en las
     predicciones fuera de partición, prueba t pareada corregida (Nadeau y Bengio, 2003;
     Bouckaert y Frank, 2004) y evaluación en 2024 con bootstrap pareado (sección 7.4.5).
  4. Escenarios de sensibilidad E1-E11 con los hiperparámetros del base (sección 7.4.1) y
     regla de decisión de la Hipótesis 1 (sección 7.4.5).
  5. Modelo sin valor ni plazo iniciales (sección 7.4.1).
  6. Tablas (CSV) y figuras (PNG) para la sección 8.3.

Tarda unos 35 minutos. Guarda puntos de control en 03_MODELADO/modelos/_cache: si se
interrumpe, al volver a ejecutarlo continúa desde la última etapa terminada.
Prueba rápida (solo para verificar que corre): set PRUEBA_RAPIDA=1 antes de ejecutarlo.
"""
import sys
# Los mensajes usan tildes y símbolos como ≥: se escriben en UTF-8 aunque la salida se redirija a un archivo.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import os
import sys
import time
import json
import importlib
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
from scipy import stats
from scipy.stats import loguniform, randint, uniform
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, FunctionTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedGroupKFold, RandomizedSearchCV
from matplotlib.ticker import FuncFormatter
from sklearn.metrics import (average_precision_score, roc_auc_score, f1_score, precision_score,
                             recall_score, precision_recall_curve, roc_curve, confusion_matrix)
from xgboost import XGBClassifier

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
SEMILLA = 42                       # semilla única para todos los procesos aleatorios (7.4.7)
RAPIDA = os.environ.get("PRUEBA_RAPIDA") == "1"
K, R = 5, (1 if RAPIDA else 3)     # 5 particiones x 3 repeticiones, agrupadas por entidad, año y mes (7.4.3)
N_ITER = {"RL": 2, "RF": 2, "XGB": 2} if RAPIDA else {"RL": 20, "RF": 40, "XGB": 40}
B_BOOT = 50 if RAPIDA else 2000    # remuestras bootstrap (7.4.5)
ALFA = 0.05
ANIO_FIN_ENTRENAMIENTO = 2023
ESC_MATERIALES = ["E1", "E2", "E3", "E4", "E8", "E10"]   # escenarios que cuentan para H1 (7.4.5)
MINIMO_MATERIALES = 4

BASE = Path(__file__).resolve().parents[2]
MOD = Path(os.environ.get("SALIDA_MODELADO", BASE / "03_MODELADO"))
SAL = MOD / ("modelos_prueba_rapida" if RAPIDA else "modelos")
FIG = SAL / "figuras"
CACHE = SAL / "_cache"
for d in (SAL, FIG, CACHE, SAL / "entrenados"):
    d.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(Path(__file__).resolve().parent))
proxy = importlib.import_module("03_proxy_sensibilidad")

CAT = ["modalidad", "causal_directa", "tipo_contrato", "segmento_unspsc", "sector_entidad",
       "orden_entidad", "mes_firma", "ley_garantias"]
BIN = ["es_pyme", "persona_natural"]
NUM = ["valor_inicial", "plazo_inicial_dias", "antiguedad_proveedor_dias"]
NOMBRES = {"RL": "Regresión Logística", "RF": "Random Forest", "XGB": "XGBoost"}
COLORES = {"RL": "#4C72B0", "RF": "#55A868", "XGB": "#C44E52"}
TIEMPOS = {}


def log(msg):
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def en_cache(nombre, funcion):
    """Ejecuta la etapa o la recupera si ya se había terminado antes."""
    archivo = CACHE / f"{nombre}.joblib"
    if archivo.exists():
        log(f"  (recuperado del punto de control: {nombre})")
        return joblib.load(archivo)
    t0 = time.time()
    resultado = funcion()
    TIEMPOS[nombre] = round((time.time() - t0) / 60, 2)
    joblib.dump(resultado, archivo)
    return resultado


# ---------------------------------------------------------------------------
# Modelos y preparación (7.4.2, Tabla 5)
# ---------------------------------------------------------------------------
class XGBPonderado(XGBClassifier):
    """XGBoost con el peso de la clase con alerta calculado en cada partición de entrenamiento (7.4.3)."""

    def fit(self, X, y, **kwargs):
        y = np.asarray(y)
        self.set_params(scale_pos_weight=float((y == 0).sum()) / max(int((y == 1).sum()), 1))
        return super().fit(X, y, **kwargs)


def preparacion(cat, binarias, num, escalar):
    escala = [("esc", StandardScaler())] if escalar else []
    partes = []
    if "valor_inicial" in num:
        partes.append(("valor", Pipeline([("log", FunctionTransformer(np.log1p, feature_names_out="one-to-one")),
                                          ("imp", SimpleImputer(strategy="median"))] + escala), ["valor_inicial"]))
    otras = [c for c in num if c != "valor_inicial"]
    if otras:
        partes.append(("num", Pipeline([("imp", SimpleImputer(strategy="median"))] + escala), otras))
    partes.append(("bin", "passthrough", binarias))
    partes.append(("cat", Pipeline([("imp", SimpleImputer(strategy="constant", fill_value="Sin dato")),
                                    ("ohe", OneHotEncoder(min_frequency=0.01, handle_unknown="ignore",
                                                          sparse_output=False))]), cat))
    return ColumnTransformer(partes, verbose_feature_names_out=False)


def modelos(cat, binarias, num):
    return {
        "RL": Pipeline([("prep", preparacion(cat, binarias, num, True)),
                        ("modelo", LogisticRegression(class_weight="balanced", max_iter=5000))]),
        "RF": Pipeline([("prep", preparacion(cat, binarias, num, False)),
                        ("modelo", RandomForestClassifier(class_weight="balanced", n_jobs=-1,
                                                          random_state=SEMILLA))]),
        "XGB": Pipeline([("prep", preparacion(cat, binarias, num, False)),
                         ("modelo", XGBPonderado(objective="binary:logistic", tree_method="hist",
                                                 device="cpu", n_jobs=-1, random_state=SEMILLA))]),
    }


ESPACIO = {   # Tabla 8 (7.4.4)
    "RL": {"modelo__C": loguniform(1e-3, 1e2)},
    "RF": {"modelo__n_estimators": [200, 300, 500],
           "modelo__max_depth": [10, 20, 30, None],
           "modelo__min_samples_leaf": [1, 2, 5, 10, 20],
           "modelo__max_features": ["sqrt", "log2", 0.3]},
    "XGB": {"modelo__n_estimators": randint(200, 1001),
            "modelo__learning_rate": loguniform(0.01, 0.3),
            "modelo__max_depth": randint(3, 11),
            "modelo__min_child_weight": [1, 3, 5, 10],
            "modelo__subsample": uniform(0.6, 0.4),
            "modelo__colsample_bytree": uniform(0.5, 0.5),
            "modelo__reg_lambda": loguniform(0.1, 10)},
}


# ---------------------------------------------------------------------------
# Métricas y pruebas (7.4.5)
# ---------------------------------------------------------------------------
def umbral_f1(y, p):
    prec, rec, umb = precision_recall_curve(y, p)
    f1 = np.where(prec + rec > 0, 2 * prec * rec / np.maximum(prec + rec, 1e-12), 0)[:-1]
    return float(umb[int(np.argmax(f1))])


def metricas(y, p, umbral):
    pred = (p >= umbral).astype(int)
    return {"AUC_PR": average_precision_score(y, p), "AUC_ROC": roc_auc_score(y, p),
            "F1": f1_score(y, pred, zero_division=0), "Precision": precision_score(y, pred, zero_division=0),
            "Exhaustividad": recall_score(y, pred, zero_division=0)}


def t_corregida(a, b, unilateral=True):
    """Prueba t pareada con varianza corregida para validación cruzada repetida."""
    d = np.asarray(a) - np.asarray(b)
    n = len(d)
    media, var = d.mean(), d.var(ddof=1)
    factor = 1 / n + 1 / (K - 1)          # 1/15 + n_validación/n_entrenamiento (1/4)
    if var == 0:
        t = np.inf if media > 0 else (-np.inf if media < 0 else 0.0)
    else:
        t = media / np.sqrt(factor * var)
    p = stats.t.sf(t, n - 1) if unilateral else 2 * stats.t.sf(abs(t), n - 1)
    return media, t, p


def evaluar(pipe, params, X, y, particiones, Xte, yte):
    """Métricas por partición, umbral por F1 fuera de partición y evaluación en prueba."""
    oof = np.full((R, len(y)), np.nan)
    filas = []
    for i, (tr, va) in enumerate(particiones):
        m = clone(pipe).set_params(**params)
        m.fit(X.iloc[tr], y[tr])
        p = m.predict_proba(X.iloc[va])[:, 1]
        oof[i // K, va] = p
        filas.append({"particion": i + 1, "va": va, "p": p})
    umbral = umbral_f1(np.tile(y, R), oof.ravel())
    por_particion = pd.DataFrame([{"particion": f["particion"], **metricas(y[f["va"]], f["p"], umbral)}
                                  for f in filas])
    final = clone(pipe).set_params(**params).fit(X, y)
    p_te = final.predict_proba(Xte)[:, 1]
    return {"cv": por_particion, "umbral": umbral, "prueba": metricas(yte, p_te, umbral),
            "p_prueba": p_te, "modelo": final}


def supera(res_ens, res_rl):
    """Un ensamble supera a la RL si la ventaja es positiva y significativa en AUC-PR y en F1."""
    salida = {}
    for met in ("AUC_PR", "F1"):
        media, t, p = t_corregida(res_ens["cv"][met], res_rl["cv"][met])
        salida[f"dif_{met}"], salida[f"t_{met}"], salida[f"p_{met}"] = media, t, p
    salida["supera"] = bool(salida["dif_AUC_PR"] > 0 and salida["p_AUC_PR"] < ALFA
                            and salida["dif_F1"] > 0 and salida["p_F1"] < ALFA)
    return salida


def bootstrap(yte, scores, umbrales, grupos):
    """Bootstrap pareado por grupos (7.4.5): cada remuestra extrae con reemplazo grupos completos
    de entidad, año y mes de firma, porque los contratos de un mismo grupo no son independientes
    (7.4.3). Los tres modelos se evalúan sobre los mismos contratos en cada remuestra."""
    rng = np.random.default_rng(SEMILLA)
    _, cod = np.unique(grupos, return_inverse=True)
    miembros = [np.flatnonzero(cod == g) for g in range(cod.max() + 1)]
    registros = []
    for _ in range(B_BOOT):
        idx = np.concatenate([miembros[g] for g in rng.integers(0, len(miembros), len(miembros))])
        if yte[idx].sum() == 0:
            continue
        fila = {}
        for k, p in scores.items():
            met = metricas(yte[idx], p[idx], umbrales[k])
            for nombre, valor in met.items():
                fila[f"{k}_{nombre}"] = valor
        registros.append(fila)
    b = pd.DataFrame(registros)
    for ens in ("RF", "XGB"):
        for met in ("AUC_PR", "F1", "AUC_ROC", "Exhaustividad", "Precision"):
            b[f"{ens}-RL_{met}"] = b[f"{ens}_{met}"] - b[f"RL_{met}"]
    return b


# ---------------------------------------------------------------------------
# Datos
# ---------------------------------------------------------------------------
def cargar():
    t = proxy.preparar(pd.read_csv(MOD / "tabla_modelado.csv", dtype={"segmento_unspsc": str}))
    t["mes_firma"] = t["mes_firma"].astype(str)
    if RAPIDA:
        t = t.groupby("anio_firma", group_keys=False).sample(frac=0.08, random_state=SEMILLA).reset_index(drop=True)
    candidatos = CAT + BIN + NUM
    sin_variacion = [c for c in candidatos if t[c].nunique(dropna=False) <= 1]
    cat = [c for c in CAT if c not in sin_variacion]
    num = [c for c in NUM if c not in sin_variacion]
    binarias = [c for c in BIN if c not in sin_variacion]
    return t, cat, binarias, num, sin_variacion


def particiones_agrupadas(ti, X, y):
    """Validación cruzada estratificada y agrupada (7.4.3): los contratos de una misma entidad
    firmados en un mismo mes quedan siempre en la misma partición, porque suelen compartir
    características y modificaciones (se prorrogan o adicionan en bloque)."""
    grupos = (ti["codigo_entidad"].astype(str) + "_" + ti["anio_firma"].astype(str) + "_"
              + ti["mes_firma"].astype(str)).to_numpy()
    salida = []
    for r in range(R):
        salida += list(StratifiedGroupKFold(n_splits=K, shuffle=True, random_state=SEMILLA + r).split(X, y, grupos))
    return salida


def partir(t, y):
    ent = (t["anio_firma"] <= ANIO_FIN_ENTRENAMIENTO).to_numpy()
    return ent, y[ent], y[~ent]


# ---------------------------------------------------------------------------
# Figuras (sin título dentro de la imagen: el título va en el documento)
# ---------------------------------------------------------------------------
def figuras(base, yte, prevalencia):
    plt.rcParams.update({"font.size": 10, "font.family": "DejaVu Sans"})
    coma = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
    # Distribución del AUC-PR en las particiones
    fig, ax = plt.subplots(figsize=(6, 4))
    datos = [base[k]["cv"]["AUC_PR"] for k in NOMBRES]
    ax.boxplot(datos, tick_labels=list(NOMBRES.values()))
    ax.set_ylabel("AUC-PR en las particiones de validación"); ax.yaxis.set_major_formatter(coma)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout(); fig.savefig(FIG / "fig_boxplot_aucpr_cv.png", dpi=300); plt.close(fig)
    # Curvas precisión-exhaustividad en prueba
    fig, ax = plt.subplots(figsize=(6, 4.5))
    for k in NOMBRES:
        prec, rec, _ = precision_recall_curve(yte, base[k]["p_prueba"])
        ax.plot(rec, prec, color=COLORES[k], label=f"{NOMBRES[k]} (AUC-PR = {base[k]['prueba']['AUC_PR']:.3f})".replace(".", ","))
    ax.axhline(prevalencia, ls="--", color="grey", label=f"Referencia: prevalencia ({prevalencia:.3f})".replace(".", ","))
    ax.set_xlabel("Exhaustividad"); ax.set_ylabel("Precisión"); ax.legend(fontsize=8); ax.grid(alpha=0.3)
    ax.xaxis.set_major_formatter(coma); ax.yaxis.set_major_formatter(coma)
    fig.tight_layout(); fig.savefig(FIG / "fig_curvas_pr_prueba.png", dpi=300); plt.close(fig)
    # Curvas ROC en prueba
    fig, ax = plt.subplots(figsize=(6, 4.5))
    for k in NOMBRES:
        fpr, tpr, _ = roc_curve(yte, base[k]["p_prueba"])
        ax.plot(fpr, tpr, color=COLORES[k], label=f"{NOMBRES[k]} (AUC-ROC = {base[k]['prueba']['AUC_ROC']:.3f})".replace(".", ","))
    ax.plot([0, 1], [0, 1], ls="--", color="grey", label="Clasificador aleatorio")
    ax.set_xlabel("Tasa de falsos positivos"); ax.set_ylabel("Exhaustividad"); ax.legend(fontsize=8); ax.grid(alpha=0.3)
    ax.xaxis.set_major_formatter(coma); ax.yaxis.set_major_formatter(coma)
    fig.tight_layout(); fig.savefig(FIG / "fig_curvas_roc_prueba.png", dpi=300); plt.close(fig)
    # Matrices de confusión
    fig, ejes = plt.subplots(1, 3, figsize=(11, 3.6))
    for ax, k in zip(ejes, NOMBRES):
        cm = confusion_matrix(yte, (base[k]["p_prueba"] >= base[k]["umbral"]).astype(int))
        ax.imshow(cm, cmap="Blues")
        for (i, j), v in np.ndenumerate(cm):
            ax.text(j, i, f"{v:,}".replace(",", "."), ha="center", va="center",
                    color="white" if v > cm.max() / 2 else "black")
        ax.set_xticks([0, 1], ["Sin alerta", "Alerta"]); ax.set_yticks([0, 1], ["Sin alerta", "Alerta"])
        ax.set_xlabel("Predicción"); ax.set_ylabel("Etiqueta del proxy"); ax.set_title(NOMBRES[k], fontsize=10)
    fig.tight_layout(); fig.savefig(FIG / "fig_matrices_confusion.png", dpi=300); plt.close(fig)


def figura_ventaja(esc):
    """Ventaja de cada ensamble sobre la RL frente a la prevalencia del escenario (7.4.5).
    Los escenarios que cuentan para la Hipótesis 1 se rotulan; los demás se dibujan sin relleno."""
    coma = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
    fig, ax = plt.subplots(figsize=(7, 4.8))
    codigo = esc["escenario"].str.split().str[0]
    cuenta = codigo.isin(["E0"] + ESC_MATERIALES)
    x = esc["prevalencia_entrenamiento_%"]
    for ens in ("RF", "XGB"):
        y = esc[f"{ens}_dif_AUC_PR"]
        ax.scatter(x[cuenta], y[cuenta], color=COLORES[ens], s=36, label=f"{NOMBRES[ens]} − Regresión Logística")
        ax.scatter(x[~cuenta], y[~cuenta], facecolors="none", edgecolors=COLORES[ens], s=36)
    for i in esc.index[cuenta]:
        ax.vlines(x[i], esc.loc[i, "RF_dif_AUC_PR"], esc.loc[i, "XGB_dif_AUC_PR"], color="grey", lw=0.6, alpha=0.6)
        tope = max(esc.loc[i, "RF_dif_AUC_PR"], esc.loc[i, "XGB_dif_AUC_PR"])
        ax.annotate(codigo[i], (x[i], tope), fontsize=8, ha="center", xytext=(0, 6), textcoords="offset points")
    for i in esc.index[codigo == "E11"]:
        tope = max(esc.loc[i, "RF_dif_AUC_PR"], esc.loc[i, "XGB_dif_AUC_PR"])
        ax.annotate("E11", (x[i], tope), fontsize=8, ha="center", xytext=(0, 6), textcoords="offset points", color="grey")
    ax.scatter([], [], facecolors="none", edgecolors="grey", label="Escenarios que no cuentan para la H1 (E5–E7, E9 y E11)")
    ax.axhline(0, color="grey", lw=0.8)
    ax.set_xlabel("Prevalencia de alertas en entrenamiento (%)")
    ax.set_ylabel("Diferencia de AUC-PR en validación cruzada")
    ax.legend(fontsize=8, loc="lower right"); ax.grid(alpha=0.3)
    ax.xaxis.set_major_formatter(coma); ax.yaxis.set_major_formatter(coma)
    fig.tight_layout(); fig.savefig(FIG / "fig_ventaja_vs_prevalencia.png", dpi=300); plt.close(fig)


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------
def main():
    inicio = time.time()
    log("PASO 4 - MODELOS" + ("  [PRUEBA RÁPIDA]" if RAPIDA else ""))
    t, cat, binarias, num, sin_var = cargar()
    log(f"  Predictores: {len(cat) + len(binarias) + len(num)} descriptores; sin variación (excluidos): {sin_var}")
    X = t[cat + binarias + num]
    y0, _ = proxy.etiquetar(t, **proxy.BASE_UMBRALES)
    y = y0["alerta"].to_numpy()
    ent, ytr, yte = partir(t, y)
    Xtr, Xte = X[ent].reset_index(drop=True), X[~ent].reset_index(drop=True)
    particiones = particiones_agrupadas(t[ent].reset_index(drop=True), Xtr, ytr)
    log(f"  Entrenamiento: {len(ytr):,} contratos ({ytr.mean():.2%} con alerta) · Prueba: {len(yte):,} ({yte.mean():.2%})")
    pipes = modelos(cat, binarias, num)

    # 1. Búsqueda de hiperparámetros (7.4.4)
    mejores, filas_hp = {}, []
    for k in NOMBRES:
        log(f"Búsqueda de hiperparámetros: {NOMBRES[k]} ({N_ITER[k]} configuraciones x {len(particiones)} particiones)")

        def buscar(k=k):
            b = RandomizedSearchCV(pipes[k], ESPACIO[k], n_iter=N_ITER[k], scoring="average_precision",
                                   cv=particiones, refit=False, random_state=SEMILLA,
                                   n_jobs=(-1 if k == "RL" else 1))
            t0 = time.time()
            b.fit(Xtr, ytr)
            return {"params": b.best_params_, "score": b.best_score_, "std": float(
                b.cv_results_["std_test_score"][b.best_index_]), "min": round((time.time() - t0) / 60, 2),
                "resultados": pd.DataFrame(b.cv_results_)}
        r = en_cache(f"busqueda_{k}", buscar)
        mejores[k] = r["params"]
        r["resultados"].to_csv(SAL / f"busqueda_{k}.csv", index=False, encoding="utf-8-sig")
        filas_hp.append({"modelo": NOMBRES[k], "configuraciones": N_ITER[k],
                         "hiperparametros": json.dumps({p.replace("modelo__", ""): (v if not isinstance(v, (np.floating, float)) else round(float(v), 5))
                                                        for p, v in r["params"].items()}, default=str),
                         "AUC_PR_cv_media": round(r["score"], 4), "AUC_PR_cv_desv": round(r["std"], 4),
                         "minutos_busqueda": r["min"]})
        log(f"  Mejor AUC-PR medio: {r['score']:.4f} · {r['params']}")
    pd.DataFrame(filas_hp).to_csv(SAL / "hiperparametros_seleccionados.csv", index=False, encoding="utf-8-sig")

    # 2. Escenario base (7.4.5)
    base = {}
    for k in NOMBRES:
        log(f"Evaluación del escenario base: {NOMBRES[k]}")
        base[k] = en_cache(f"base_{k}", lambda k=k: evaluar(pipes[k], mejores[k], Xtr, ytr, particiones, Xte, yte))
        joblib.dump(base[k]["modelo"], SAL / "entrenados" / f"modelo_{k}.joblib")
    filas_cv = []
    for k in NOMBRES:
        for met in ("AUC_PR", "F1", "Exhaustividad", "Precision", "AUC_ROC"):
            filas_cv.append({"modelo": NOMBRES[k], "metrica": met, "media": base[k]["cv"][met].mean(),
                             "desv": base[k]["cv"][met].std(ddof=1), "umbral_F1": base[k]["umbral"]})
    pd.DataFrame(filas_cv).round(4).to_csv(SAL / "metricas_validacion_cruzada.csv", index=False, encoding="utf-8-sig")
    pd.concat([base[k]["cv"].assign(modelo=NOMBRES[k]) for k in NOMBRES]).round(4).to_csv(
        SAL / "metricas_por_particion.csv", index=False, encoding="utf-8-sig")

    pruebas = []
    for a, b_, unil in (("RF", "RL", True), ("XGB", "RL", True), ("RF", "XGB", False)):
        for met in ("AUC_PR", "F1", "AUC_ROC", "Exhaustividad"):
            media, tt, p = t_corregida(base[a]["cv"][met], base[b_]["cv"][met], unilateral=unil)
            pruebas.append({"comparacion": f"{NOMBRES[a]} − {NOMBRES[b_]}", "metrica": met,
                            "diferencia_media": media, "t_corregida": tt, "gl": len(particiones) - 1,
                            "p_valor": p, "tipo": "unilateral" if unil else "bilateral",
                            "significativa": bool(p < ALFA and (media > 0 or not unil))})
    pd.DataFrame(pruebas).round(4).to_csv(SAL / "pruebas_pareadas.csv", index=False, encoding="utf-8-sig")

    log(f"Bootstrap pareado por grupos en prueba ({B_BOOT} remuestras)")
    tte = t[~ent]
    grupos_te = (tte["codigo_entidad"].astype(str) + "_" + tte["anio_firma"].astype(str) + "_"
                 + tte["mes_firma"].astype(str)).to_numpy()
    boot = en_cache("bootstrap_agrupado", lambda: bootstrap(yte, {k: base[k]["p_prueba"] for k in NOMBRES},
                                                            {k: base[k]["umbral"] for k in NOMBRES}, grupos_te))
    # Comparación complementaria XGBoost − Random Forest (sección 8.3.3), con las mismas remuestras
    boot = boot.copy()
    for met in ("AUC_PR", "F1", "AUC_ROC", "Exhaustividad", "Precision"):
        boot[f"XGB-RF_{met}"] = boot[f"XGB_{met}"] - boot[f"RF_{met}"]
    filas_te = []
    for col in [c for c in boot.columns]:
        modelo, met = col.split("_", 1)
        if modelo in NOMBRES:
            punto = base[modelo]["prueba"][met]
        else:
            a, b_ = modelo.split("-")
            punto = base[a]["prueba"][met] - base[b_]["prueba"][met]
        filas_te.append({"modelo_o_diferencia": NOMBRES.get(modelo, modelo.replace("RF", "Random Forest")
                                                             .replace("XGB", "XGBoost").replace("RL", "Regresión Logística")),
                         "metrica": met, "valor": punto, "IC95_inf": boot[col].quantile(0.025),
                         "IC95_sup": boot[col].quantile(0.975)})
    pd.DataFrame(filas_te).round(4).to_csv(SAL / "metricas_prueba_2024.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame({"id_contrato": t.loc[~ent, "id_contrato"].to_numpy(), "alerta": yte,
                  **{f"puntaje_{k}": base[k]["p_prueba"] for k in NOMBRES}}).to_csv(
        SAL / "predicciones_prueba.csv", index=False, encoding="utf-8-sig")
    figuras(base, yte, yte.mean())

    # 3. Escenarios de sensibilidad (7.4.1) con los hiperparámetros del base
    filas_esc = []
    escenarios = proxy.ESCENARIOS if not RAPIDA else [e for e in proxy.ESCENARIOS if e[0].split()[0] in ("E0", "E1", "E10")]
    for nombre, regla, cambios, _ in escenarios:
        cod = nombre.split()[0]
        log(f"Escenario {nombre}")
        u = {**proxy.BASE_UMBRALES, **cambios}
        excluir = u.pop("excluir", None)
        mask = (t[excluir] == 0).to_numpy() if excluir else np.ones(len(t), bool)
        ti = t[mask].reset_index(drop=True)
        e, _ = proxy.etiquetar(ti, **u)
        ye = e["alerta"].to_numpy()
        ent_e, ytr_e, yte_e = partir(ti, ye)
        Xi = ti[cat + binarias + num]
        Xtr_e, Xte_e = Xi[ent_e].reset_index(drop=True), Xi[~ent_e].reset_index(drop=True)
        if cod == "E0":
            res = base
        else:
            part_e = particiones_agrupadas(ti[ent_e].reset_index(drop=True), Xtr_e, ytr_e)
            res = {k: en_cache(f"esc_{cod}_{k}", lambda k=k: evaluar(pipes[k], mejores[k], Xtr_e, ytr_e, part_e,
                                                                       Xte_e, yte_e)) for k in NOMBRES}
        fila = {"escenario": nombre, "cuenta_para_H1": cod == "E0" or cod in ESC_MATERIALES,
                "contratos": len(ti), "prevalencia_entrenamiento_%": round(100 * ytr_e.mean(), 2)}
        for k in NOMBRES:
            for met in ("AUC_PR", "F1"):
                fila[f"{k}_{met}_cv"] = res[k]["cv"][met].mean()
                fila[f"{k}_{met}_prueba"] = res[k]["prueba"][met]
        for ens in ("RF", "XGB"):
            s = supera(res[ens], res["RL"])
            fila.update({f"{ens}_{c}": v for c, v in s.items()})
        filas_esc.append(fila)
    esc = pd.DataFrame(filas_esc)
    esc.round(4).to_csv(SAL / "escenarios_modelos.csv", index=False, encoding="utf-8-sig")
    figura_ventaja(esc)

    # 4. Decisión sobre la Hipótesis 1 (7.4.5)
    decision = []
    for ens in ("RF", "XGB"):
        base_ok = bool(esc.loc[esc["escenario"].str.startswith("E0 "), f"{ens}_supera"].iloc[0])
        mat = esc[esc["escenario"].str.split().str[0].isin(ESC_MATERIALES)]
        n_mat = int(mat[f"{ens}_supera"].sum())
        decision.append({"ensamble": NOMBRES[ens], "supera_en_base": base_ok,
                         "escenarios_materiales_superados": n_mat, "escenarios_materiales_evaluados": len(mat),
                         "cumple_H1": base_ok and n_mat >= MINIMO_MATERIALES})
    dec = pd.DataFrame(decision)
    n_cumple = int(dec["cumple_H1"].sum())
    resultado_h1 = {2: "Se valida", 1: "Se valida parcialmente", 0: "Se rechaza"}[n_cumple]
    dec["decision_H1"] = resultado_h1
    dec.to_csv(SAL / "decision_h1.csv", index=False, encoding="utf-8-sig")

    # 5. Modelo sin valor ni plazo iniciales (7.4.1)
    num_sv = [c for c in num if c not in ("valor_inicial", "plazo_inicial_dias")]
    pipes_sv = modelos(cat, binarias, num_sv)
    Xtr_sv, Xte_sv = Xtr[cat + binarias + num_sv], Xte[cat + binarias + num_sv]
    filas_sv = []
    for k in NOMBRES:
        log(f"Modelo sin valor ni plazo: {NOMBRES[k]}")
        r = en_cache(f"sin_valor_plazo_{k}", lambda k=k: evaluar(pipes_sv[k], mejores[k], Xtr_sv, ytr, particiones,
                                                                   Xte_sv, yte))
        joblib.dump(r["modelo"], SAL / "entrenados" / f"modelo_{k}_sin_valor_plazo.joblib")
        for met in ("AUC_PR", "F1"):
            media, tt, p = t_corregida(base[k]["cv"][met], r["cv"][met], unilateral=False)
            filas_sv.append({"modelo": NOMBRES[k], "metrica": met, "con_valor_plazo_cv": base[k]["cv"][met].mean(),
                             "sin_valor_plazo_cv": r["cv"][met].mean(), "diferencia": media, "p_valor_bilateral": p,
                             "con_valor_plazo_prueba": base[k]["prueba"][met],
                             "sin_valor_plazo_prueba": r["prueba"][met]})
    pd.DataFrame(filas_sv).round(4).to_csv(SAL / "modelo_sin_valor_plazo.csv", index=False, encoding="utf-8-sig")

    # 6. Modelo seleccionado para SHAP (7.4.5)
    medias = {k: base[k]["cv"]["AUC_PR"].mean() for k in NOMBRES}
    orden = sorted(medias, key=medias.get, reverse=True)
    _, _, p_sel = t_corregida(base[orden[0]]["cv"]["AUC_PR"], base[orden[1]]["cv"]["AUC_PR"], unilateral=False)
    texto = (f"Modelo seleccionado: {NOMBRES[orden[0]]} (clave {orden[0]})\n"
             f"AUC-PR medio en validación cruzada: " + ", ".join(f"{NOMBRES[k]} {medias[k]:.4f}" for k in orden) + "\n"
             f"Diferencia con el segundo ({NOMBRES[orden[1]]}): p bilateral = {p_sel:.4f} -> "
             + ("significativa" if p_sel < ALFA else "no concluyente") + "\n"
             f"Decisión sobre la Hipótesis 1: {resultado_h1}\n")
    (SAL / "modelo_seleccionado.txt").write_text(texto, encoding="utf-8")

    # Los tiempos de las etapas recuperadas de puntos de control se conservan de la ejecución en que
    # se calcularon; el total es la suma de las etapas (no incluye la lectura de datos ni las figuras).
    archivo_t = SAL / "tiempos_computo.csv"
    previos = pd.read_csv(archivo_t, index_col=0)["minutos"].to_dict() if archivo_t.exists() else {}
    previos.update(TIEMPOS)
    previos.pop("total", None); previos.pop("total_etapas", None)
    if "bootstrap_agrupado" in previos:
        previos.pop("bootstrap", None)
    previos["total_etapas"] = round(sum(previos.values()), 2)
    pd.Series(previos, name="minutos").to_csv(archivo_t, encoding="utf-8-sig")
    TIEMPOS["total"] = round((time.time() - inicio) / 60, 2)
    print("\n" + texto)
    print(dec.to_string(index=False))
    log(f"Listo en {TIEMPOS['total']} minutos. Resultados en {SAL}")


if __name__ == "__main__":
    main()
