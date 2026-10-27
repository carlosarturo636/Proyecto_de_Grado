"""
Paso 6. Evaluación del marco de priorización preventiva (secciones 7.4.8 y 8.5).

No entrena modelos: usa las predicciones del conjunto de prueba (2024) que guardó 04_modelos.py.
Los contratos se ordenan de mayor a menor puntaje y se simula que la contraloría revisa una
fracción fija de ellos (su capacidad de vigilancia): 5 %, 10 % y 20 %. Para cada capacidad
se calculan la precisión (proporción de revisados con alerta según el proxy) y la exhaustividad
(proporción de las alertas que quedan dentro de los revisados), para el modelo seleccionado y
para la Regresión Logística, frente a una selección al azar (precisión esperada = prevalencia).
El cálculo se hace para toda la población de prueba y dentro de cada grupo de vigilancia.
Los intervalos de confianza se obtienen con el bootstrap por grupos de entidad, año y mes de
firma (sección 7.4.5).

Salidas en 03_MODELADO/priorizacion/.
Uso:  python 06_priorizacion.py
"""
import sys
# Los mensajes usan tildes y símbolos como ≥: se escriben en UTF-8 aunque la salida se redirija a un archivo.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import os
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

BASE = Path(__file__).resolve().parents[2]
MOD = Path(os.environ.get("SALIDA_MODELADO", BASE / "03_MODELADO"))
SAL = MOD / "priorizacion"
FIG = SAL / "figuras"
FIG.mkdir(parents=True, exist_ok=True)

SEMILLA = 42
B_BOOT = 2000
CAPACIDADES = [0.05, 0.10, 0.20]       # fracción de contratos que se revisa (7.4.8)
NOMBRES = {"RL": "Regresión Logística", "RF": "Random Forest", "XGB": "XGBoost"}
COLORES = {"RL": "#4C72B0", "XGB": "#C44E52", "RF": "#55A868"}


def log(msg):
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def revisados(puntaje, ids, capacidad):
    """Índices de los contratos revisados: los de mayor puntaje (empates por identificador)."""
    k = int(np.ceil(capacidad * len(puntaje)))
    orden = np.lexsort((ids, -puntaje))
    return orden[:k]


def medidas(y, puntaje, ids, capacidad):
    sel = revisados(puntaje, ids, capacidad)
    vp = y[sel].sum()
    return {"revisados": len(sel), "alertas_encontradas": int(vp),
            "precision": vp / len(sel), "exhaustividad": vp / y.sum() if y.sum() else np.nan}


def evaluar(d, modelos):
    """Medidas para toda la población y dentro de cada grupo de vigilancia."""
    filas = []
    for ambito, sub in [("Total", d)] + list(d.groupby("grupo_vigilancia")):
        y, ids = sub["alerta"].to_numpy(), sub["orden_id"].to_numpy()
        for cap in CAPACIDADES:
            for k in modelos:
                m = medidas(y, sub[f"puntaje_{k}"].to_numpy(), ids, cap)
                filas.append({"ambito": ambito, "capacidad": cap, "modelo": k, **m,
                              "prevalencia": y.mean(), "contratos": len(sub), "alertas": int(y.sum())})
    return pd.DataFrame(filas)


def main():
    inicio = time.time()
    log("PASO 6 - PRIORIZACIÓN PREVENTIVA")
    texto = (MOD / "modelos" / "modelo_seleccionado.txt").read_text(encoding="utf-8")
    clave = re.search(r"\(clave (\w+)\)", texto).group(1)
    modelos = [clave, "RL"] if clave != "RL" else ["RL"]
    log(f"  Modelo seleccionado: {NOMBRES[clave]}; comparación con la Regresión Logística y con una selección al azar")

    p = pd.read_csv(MOD / "modelos" / "predicciones_prueba.csv")
    t = pd.read_csv(MOD / "tabla_modelado.csv", usecols=["id_contrato", "codigo_entidad", "anio_firma",
                                                        "mes_firma", "grupo_vigilancia"])
    d = p.merge(t, on="id_contrato", how="left", validate="one_to_one")
    d["grupo_vigilancia"] = d["grupo_vigilancia"].str.replace(r" \(.*\)$", "", regex=True)
    d["orden_id"] = d["id_contrato"].rank(method="dense").astype(int)
    d["grupo_boot"] = (d["codigo_entidad"].astype(str) + "_" + d["anio_firma"].astype(str) + "_"
                       + d["mes_firma"].astype(str))
    log(f"  Contratos de prueba: {len(d):,} · alertas: {int(d['alerta'].sum()):,} ({d['alerta'].mean():.2%})")

    punto = evaluar(d, modelos)

    # Bootstrap por grupos (7.4.5)
    log(f"  Bootstrap por grupos ({B_BOOT} remuestras)")
    rng = np.random.default_rng(SEMILLA)
    _, cod = np.unique(d["grupo_boot"].to_numpy(), return_inverse=True)
    miembros = [np.flatnonzero(cod == g) for g in range(cod.max() + 1)]
    reps = []
    for b in range(B_BOOT):
        idx = np.concatenate([miembros[g] for g in rng.integers(0, len(miembros), len(miembros))])
        r = evaluar(d.iloc[idx].reset_index(drop=True), modelos)
        r["rep"] = b
        reps.append(r)
    reps = pd.concat(reps, ignore_index=True)
    clave_cols = ["ambito", "capacidad", "modelo"]
    ic = reps.groupby(clave_cols)[["precision", "exhaustividad"]].quantile([0.025, 0.975]).unstack()
    ic.columns = [f"{m}_IC95_{'inf' if q == 0.025 else 'sup'}" for m, q in ic.columns]
    res = punto.merge(ic.reset_index(), on=clave_cols)
    res["veces_la_prevalencia"] = res["precision"] / res["prevalencia"]

    # Diferencia del modelo seleccionado frente a la Regresión Logística
    if clave != "RL":
        piv = reps.pivot_table(index=["ambito", "capacidad", "rep"], columns="modelo",
                               values=["precision", "exhaustividad"])
        dif = pd.DataFrame({m: piv[(m, clave)] - piv[(m, "RL")] for m in ["precision", "exhaustividad"]})
        dic = dif.groupby(["ambito", "capacidad"]).quantile([0.025, 0.975]).unstack()
        dic.columns = [f"dif_{m}_IC95_{'inf' if q == 0.025 else 'sup'}" for m, q in dic.columns]
        pp = punto.pivot_table(index=["ambito", "capacidad"], columns="modelo", values=["precision", "exhaustividad"])
        dpunto = pd.DataFrame({f"dif_{m}": pp[(m, clave)] - pp[(m, "RL")] for m in ["precision", "exhaustividad"]})
        dpunto.join(dic).reset_index().round(4).to_csv(SAL / "diferencia_vs_regresion_logistica.csv",
                                                       index=False, encoding="utf-8-sig")

    res["modelo"] = res["modelo"].map(NOMBRES)
    res.round(4).to_csv(SAL / "priorizacion.csv", index=False, encoding="utf-8-sig")
    print(res[res["ambito"] == "Total"][["capacidad", "modelo", "revisados", "alertas_encontradas", "precision",
                                         "exhaustividad", "veces_la_prevalencia"]].round(3).to_string(index=False))

    # Figura: precisión y exhaustividad según la capacidad de revisión (total de prueba)
    coma = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
    caps = np.linspace(0.01, 0.30, 30)
    y, ids = d["alerta"].to_numpy(), d["orden_id"].to_numpy()
    fig, ejes = plt.subplots(1, 2, figsize=(10, 4))
    for k in modelos:
        curvas = [medidas(y, d[f"puntaje_{k}"].to_numpy(), ids, c) for c in caps]
        ejes[0].plot(caps * 100, [c["precision"] for c in curvas], color=COLORES[k], label=NOMBRES[k])
        ejes[1].plot(caps * 100, [c["exhaustividad"] for c in curvas], color=COLORES[k], label=NOMBRES[k])
    ejes[0].axhline(y.mean(), ls="--", color="grey", label="Selección al azar")
    ejes[1].plot(caps * 100, caps, ls="--", color="grey", label="Selección al azar")
    for ax, nombre in zip(ejes, ["Precisión", "Exhaustividad"]):
        for c in CAPACIDADES:
            ax.axvline(c * 100, color="lightgrey", lw=0.8, zorder=0)
        ax.set_xlabel("Contratos revisados (% de los contratos de prueba)")
        ax.set_ylabel(nombre); ax.grid(alpha=0.3)
        ax.xaxis.set_major_formatter(coma); ax.yaxis.set_major_formatter(coma)
    ejes[0].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(FIG / "fig_priorizacion_capacidad.png", dpi=300); plt.close(fig)

    log(f"Listo en {(time.time() - inicio) / 60:.1f} minutos. Resultados en {SAL}")


if __name__ == "__main__":
    main()
