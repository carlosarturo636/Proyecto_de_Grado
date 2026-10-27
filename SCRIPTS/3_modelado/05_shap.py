"""
Paso 5. Explicabilidad con valores SHAP y contraste de la Hipótesis 2 (secciones 7.4.6, 8.4 y 8.6).

Requiere haber ejecutado antes 04_modelos.py: usa el modelo seleccionado, sus hiperparámetros,
la misma partición temporal y las mismas 15 particiones de la validación cruzada.

Qué hace, en este orden:
  1. Calcula los valores SHAP del modelo seleccionado sobre los contratos de prueba (2024) y
     suma las columnas one-hot de cada descriptor (aditividad, sección 7.4.6).
  2. Importancia global: promedio del valor absoluto de la contribución de cada descriptor.
  3. Dirección del efecto: correlación de Spearman (numéricos) y contribución media por
     categoría (categóricos y binarios).
  4. Estabilidad: reentrena el modelo en cada una de las 15 particiones, calcula los valores SHAP
     sobre la parte de validación y mide la concordancia de los 15 ordenamientos con la W de
     Kendall; también la proporción de particiones en que cada descriptor queda entre los 5
     primeros.
  5. Explicaciones locales de 15 contratos de prueba con alerta (5 solo por adición, 5 solo por
     prórroga, 5 por ambas), identificados con un código interno (sección 7.4.7).
  6. Consistencia con la literatura (sección 4.3.3) en el modelo base y en el modelo sin valor ni
     plazo iniciales, y decisión sobre la Hipótesis 2.
  7. Tablas (CSV) y figuras (PNG) para la sección 8.4.

Guarda puntos de control en 03_MODELADO/shap/_cache: si se interrumpe, continúa donde iba.
Prueba rápida (solo para verificar que corre): set PRUEBA_RAPIDA=1 antes de ejecutarlo
(usa los resultados de la prueba rápida de 04_modelos.py).
"""
import sys
# Los mensajes usan tildes y símbolos como ≥: se escriben en UTF-8 aunque la salida se redirija a un archivo.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import re
import textwrap
import sys
import time
import importlib
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from sklearn.base import clone
from sklearn.metrics import average_precision_score
import shap

sys.path.insert(0, str(Path(__file__).resolve().parent))
m4 = importlib.import_module("04_modelos")
# Los modelos guardados por 04_modelos.py se crearon con esta clase cuando ese script se ejecutó
# como programa principal; se expone aquí con el mismo nombre para poder leerlos.
XGBPonderado = m4.XGBPonderado
proxy = m4.proxy

SEMILLA = m4.SEMILLA
RAPIDA = m4.RAPIDA
TOP = 5               # descriptores evaluados en la consistencia (7.4.6)
UMBRAL_W = 0.7        # criterio de estabilidad (7.4.6)
N_LOCALES = 5         # contratos por grupo en las explicaciones locales (7.4.6)

SAL = m4.MOD / ("shap_prueba_rapida" if RAPIDA else "shap")
FIG = SAL / "figuras"
CACHE = SAL / "_cache"
for d in (SAL, FIG, CACHE):
    d.mkdir(parents=True, exist_ok=True)

NOMBRE_DESC = {
    "modalidad": "Modalidad de selección",
    "causal_directa": "Causal de contratación directa",
    "tipo_contrato": "Tipo de contrato",
    "segmento_unspsc": "Categoría del bien o servicio",
    "sector_entidad": "Sector de la entidad",
    "orden_entidad": "Orden de la entidad",
    "mes_firma": "Mes de suscripción",
    "ley_garantias": "Cercanía a la Ley de Garantías",
    "es_pyme": "Tamaño del proveedor (pyme)",
    "persona_natural": "Naturaleza jurídica (persona natural)",
    "valor_inicial": "Valor inicial",
    "plazo_inicial_dias": "Plazo inicial",
    "antiguedad_proveedor_dias": "Antigüedad del proveedor",
}

# Dirección esperada según la sección 4.3.3 (fijada antes de calcular los valores SHAP).
#   numéricos: signo esperado de la correlación de Spearman entre el valor y su contribución SHAP
#   categóricos y binarios: categorías señaladas, cuya contribución media se espera mayor que la
#   del resto de categorías
ESPERADA = {
    "modalidad": {"tipo": "cat", "categorias": ["Directa"], "signo": "+",
                  "texto": "Mayor alerta en la contratación directa"},
    "causal_directa": {"tipo": "cat", "categorias": ["Servicios profesionales y apoyo a la gestión"], "signo": "+",
                       "texto": "Mayor alerta en la prestación de servicios profesionales y de apoyo"},
    "valor_inicial": {"tipo": "num", "signo": "+", "texto": "Mayor alerta en valores altos e intermedios"},
    "plazo_inicial_dias": {"tipo": "num", "signo": "-", "texto": "Mayor alerta en plazos cortos"},
    "antiguedad_proveedor_dias": {"tipo": "num", "signo": "-", "texto": "Mayor alerta en proveedores recientes"},
    "persona_natural": {"tipo": "cat", "categorias": [1], "signo": "+",
                        "texto": "Mayor alerta en personas naturales"},
    "mes_firma": {"tipo": "cat", "categorias": ["12"], "signo": "+", "texto": "Mayor alerta en diciembre"},
    "ley_garantias": {"tipo": "cat", "categorias": ["Previo", "Posterior"], "signo": "+",
                      "texto": "Mayor alerta antes y después de la restricción"},
}

coma = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))


def log(msg):
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def en_cache(nombre, funcion):
    archivo = CACHE / f"{nombre}.joblib"
    if archivo.exists():
        return joblib.load(archivo)
    resultado = funcion()
    joblib.dump(resultado, archivo)
    return resultado


def num(v, dec=4):
    return f"{v:.{dec}f}".replace(".", ",")


# ---------------------------------------------------------------------------
# Valores SHAP agregados por descriptor
# ---------------------------------------------------------------------------
def descriptor_de(columna, descriptores):
    """Descriptor al que pertenece una columna del Pipeline (las one-hot llevan el prefijo)."""
    candidatos = [d for d in descriptores if columna == d or columna.startswith(d + "_")]
    return max(candidatos, key=len)


def shap_agregado(modelo, clave, X, X_fondo=None):
    """Valores SHAP de cada contrato, sumados por descriptor. Devuelve (DataFrame, valor base, unidad)."""
    prep, est = modelo.named_steps["prep"], modelo.named_steps["modelo"]
    Z = np.asarray(prep.transform(X), dtype=float)
    columnas = list(prep.get_feature_names_out())
    if clave == "RL":
        fondo = np.asarray(prep.transform(X_fondo), dtype=float)
        expl = shap.LinearExplainer(est, fondo)
        valores = expl.shap_values(Z)
        unidad = "log-odds"
    else:
        expl = shap.TreeExplainer(est)
        valores = expl.shap_values(Z, check_additivity=False)
        unidad = "log-odds" if clave == "XGB" else "probabilidad"
    if isinstance(valores, list):                 # versiones que devuelven una matriz por clase
        valores = valores[1]
    valores = np.asarray(valores)
    if valores.ndim == 3:                         # (contratos, columnas, clases)
        valores = valores[:, :, 1]
    base = np.ravel(expl.expected_value)
    base = float(base[-1])
    descriptores = list(X.columns)
    mapa = [descriptor_de(c, descriptores) for c in columnas]
    agregado = pd.DataFrame(valores, columns=columnas).T.groupby(mapa, sort=False).sum().T
    return agregado[[d for d in descriptores if d in agregado.columns]], base, unidad


def importancia(agregado):
    return agregado.abs().mean().sort_values(ascending=False)


def categoria_modelo(modelo, columna, serie):
    """Categoría con la que el modelo ve cada contrato: las poco frecuentes quedan en 'Otras'."""
    if columna in m4.BIN:
        return serie.map({1: "Sí", 0: "No"}).fillna("Sin dato")
    prep = modelo.named_steps["prep"]
    ohe = prep.named_transformers_["cat"].named_steps["ohe"]
    columnas_cat = next(list(cols) for nombre, _, cols in prep.transformers_ if nombre == "cat")
    i = columnas_cat.index(columna)
    conocidas = set(map(str, ohe.categories_[i]))
    infrecuentes = getattr(ohe, "infrequent_categories_", [None] * len(columnas_cat))[i]
    poco_frecuentes = set(map(str, infrecuentes)) if infrecuentes is not None else set()
    s = serie.fillna("Sin dato").astype(str)
    return s.where(~s.isin(poco_frecuentes), "Otras").where(s.isin(conocidas), "No vista en entrenamiento")


# ---------------------------------------------------------------------------
# Dirección del efecto y consistencia (7.4.6)
# ---------------------------------------------------------------------------
def direccion(agregado, X, descriptor):
    """Dirección observada de un descriptor con dirección esperada."""
    e = ESPERADA[descriptor]
    if e["tipo"] == "num":
        ok = X[descriptor].notna().to_numpy()
        rho, p = stats.spearmanr(X[descriptor].to_numpy()[ok], agregado[descriptor].to_numpy()[ok])
        signo = "+" if rho > 0 else "-"
        detalle = f"Spearman = {num(rho, 3)} (p = {num(p, 4)}; n = {ok.sum()})"
        return signo, rho, detalle
    senal = X[descriptor].astype(str).isin([str(c) for c in e["categorias"]]).to_numpy()
    if senal.sum() == 0 or (~senal).sum() == 0:
        # Sin contratos en alguno de los dos grupos no hay contraste posible: la dirección no
        # puede observarse (p. ej., en 2024 no hubo restricción de la Ley de Garantías).
        return None, np.nan, (f"No evaluable: {senal.sum()} contratos en {' y '.join(map(str, e['categorias']))} "
                              f"y {(~senal).sum()} en el resto")
    media_senal = agregado.loc[senal, descriptor].mean()
    media_resto = agregado.loc[~senal, descriptor].mean()
    dif = media_senal - media_resto
    signo = "+" if dif > 0 else "-"
    detalle = (f"Contribución media: {' y '.join(map(str, e['categorias']))} = {num(media_senal)}; "
               f"resto = {num(media_resto)} (n = {senal.sum()} y {(~senal).sum()})")
    return signo, dif, detalle


def consistencia(agregado, X, etiqueta):
    imp = importancia(agregado)
    filas = []
    for pos, d in enumerate(imp.index[:TOP], start=1):
        fila = {"modelo": etiqueta, "posicion": pos, "descriptor": NOMBRE_DESC[d], "importancia": imp[d]}
        if d in ESPERADA:
            signo, est, detalle = direccion(agregado, X, d)
            fila.update({"direccion_esperada": ESPERADA[d]["texto"], "signo_esperado": ESPERADA[d]["signo"],
                         "signo_observado": signo if signo else "No evaluable", "estadistico": est,
                         "detalle": detalle, "coincide": (signo == ESPERADA[d]["signo"]) if signo else np.nan})
        else:
            fila.update({"direccion_esperada": "Sin dirección esperada (sección 4.3.3)", "coincide": np.nan})
        filas.append(fila)
    tabla = pd.DataFrame(filas)
    evaluables = tabla["coincide"].notna().sum()
    coinciden = int(tabla["coincide"].fillna(False).astype(bool).sum())
    if evaluables < 2:
        resultado = "No evaluable"
    else:
        resultado = "Se cumple" if coinciden > evaluables / 2 else "No se cumple"
    return tabla, {"modelo": etiqueta, "evaluables": int(evaluables), "coinciden": coinciden, "resultado": resultado}


# ---------------------------------------------------------------------------
# Estabilidad (7.4.6)
# ---------------------------------------------------------------------------
def w_kendall(rangos):
    """W de Kendall con corrección por empates. rangos: matriz (particiones x descriptores)."""
    m, n = rangos.shape
    R = rangos.sum(axis=0)
    S = ((R - R.mean()) ** 2).sum()
    T = 0.0
    for fila in rangos:
        _, cuentas = np.unique(fila, return_counts=True)
        T += (cuentas ** 3 - cuentas).sum()
    return float(12 * S / (m ** 2 * (n ** 3 - n) - m * T))


# ---------------------------------------------------------------------------
# Figuras (sin título dentro de la imagen: el título va en el documento)
# ---------------------------------------------------------------------------
def fig_importancia(imp, unidad, archivo):
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    nombres = [NOMBRE_DESC[d] for d in imp.index][::-1]
    ax.barh(nombres, imp.values[::-1], color="#C44E52")
    ax.set_xlabel(f"Contribución SHAP media absoluta ({unidad})")
    ax.xaxis.set_major_formatter(coma); ax.grid(axis="x", alpha=0.3)
    fig.tight_layout(); fig.savefig(FIG / archivo, dpi=300); plt.close(fig)


def fig_numericas(agregado, X, unidad):
    numericas = [d for d in m4.NUM if d in agregado.columns]
    fig, ejes = plt.subplots(1, len(numericas), figsize=(4 * len(numericas), 3.8), squeeze=False)
    rng = np.random.default_rng(SEMILLA)
    idx = rng.choice(len(X), size=min(len(X), 5000), replace=False)
    etiquetas_x = {"valor_inicial": "Valor inicial (pesos, escala logarítmica)",
                   "plazo_inicial_dias": "Plazo inicial (días)",
                   "antiguedad_proveedor_dias": "Antigüedad del proveedor (días)"}
    for ax, d in zip(ejes[0], numericas):
        x = X[d].to_numpy()[idx]; s = agregado[d].to_numpy()[idx]
        ok = ~np.isnan(x)
        ax.scatter(x[ok], s[ok], s=4, alpha=0.35, color="#4C72B0")
        ax.axhline(0, color="grey", lw=0.8)
        if d == "valor_inicial":
            ax.set_xscale("log")
        else:
            ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}".replace(",", ".")))
        ax.set_xlabel(etiquetas_x[d]); ax.yaxis.set_major_formatter(coma); ax.grid(alpha=0.3)
    ejes[0][0].set_ylabel(f"Contribución SHAP ({unidad})")
    fig.tight_layout(); fig.savefig(FIG / "fig_dependencia_numericas.png", dpi=300); plt.close(fig)


def fig_categorias(tabla_cat, unidad):
    descriptores = list(dict.fromkeys(tabla_cat["descriptor"]))
    columnas = 3
    filas = int(np.ceil(len(descriptores) / columnas))
    fig, ejes = plt.subplots(filas, columnas, figsize=(13, 3.3 * filas), squeeze=False)
    for ax, d in zip(ejes.ravel(), descriptores):
        sub = tabla_cat[tabla_cat["descriptor"] == d].sort_values("contribucion_media")
        colores = ["#C44E52" if v > 0 else "#4C72B0" for v in sub["contribucion_media"]]
        ax.barh([textwrap.fill(str(c), 30) for c in sub["categoria"]], sub["contribucion_media"], color=colores)
        ax.axvline(0, color="grey", lw=0.8)
        ax.set_title(d, fontsize=9); ax.tick_params(axis="y", labelsize=7)
        ax.xaxis.set_major_formatter(coma); ax.grid(axis="x", alpha=0.3)
    for ax in ejes.ravel()[len(descriptores):]:
        ax.axis("off")
    fig.supxlabel(f"Contribución SHAP media ({unidad})", fontsize=9)
    fig.tight_layout(); fig.savefig(FIG / "fig_contribucion_categorias.png", dpi=300); plt.close(fig)


def fig_estabilidad(rangos_df):
    orden = rangos_df.mean().sort_values().index
    datos = rangos_df[orden].T
    fig, ax = plt.subplots(figsize=(9, 4.8))
    im = ax.imshow(datos.to_numpy(), cmap="Reds_r", aspect="auto")
    ax.set_yticks(range(len(orden)), [NOMBRE_DESC[d] for d in orden], fontsize=8)
    ax.set_xticks(range(datos.shape[1]), [str(i) for i in range(1, datos.shape[1] + 1)], fontsize=8)
    ax.set_xlabel("Partición de la validación cruzada")
    for (i, j), v in np.ndenumerate(datos.to_numpy()):
        ax.text(j, i, f"{v:g}".replace(".", ","), ha="center", va="center", fontsize=6)
    fig.colorbar(im, ax=ax, label="Posición en el orden de importancia")
    fig.tight_layout(); fig.savefig(FIG / "fig_estabilidad_orden.png", dpi=300); plt.close(fig)


def fig_local(codigo, contrib, base, puntaje, unidad):
    c = contrib.reindex(contrib.abs().sort_values(ascending=False).index)
    principales = c.iloc[:8]
    resto = c.iloc[8:].sum()
    etiquetas = list(principales.index) + (["Demás descriptores"] if len(c) > 8 else [])
    valores = list(principales.values) + ([resto] if len(c) > 8 else [])
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    y = np.arange(len(valores))[::-1]
    ax.barh(y, valores, color=["#C44E52" if v > 0 else "#4C72B0" for v in valores])
    ax.set_yticks(y, etiquetas, fontsize=7)
    ax.axvline(0, color="grey", lw=0.8)
    ax.set_xlabel(f"Contribución SHAP ({unidad})\nValor base = {num(base, 3)}; "
                  f"puntaje del contrato = {num(puntaje, 3)}", fontsize=8)
    ax.xaxis.set_major_formatter(coma); ax.grid(axis="x", alpha=0.3)
    fig.tight_layout(); fig.savefig(FIG / f"fig_local_{codigo}.png", dpi=300); plt.close(fig)


def texto_valor(d, v):
    if pd.isna(v):
        return "sin dato"
    if d == "valor_inicial":
        return f"${v / 1e6:,.1f} millones".replace(",", "X").replace(".", ",").replace("X", ".")
    if d in ("plazo_inicial_dias", "antiguedad_proveedor_dias"):
        return f"{v:,.0f} días".replace(",", ".")
    if d in m4.BIN:
        return "Sí" if int(v) == 1 else "No"
    return str(v)


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------
def main():
    inicio = time.time()
    log("PASO 5 - SHAP" + ("  [PRUEBA RÁPIDA]" if RAPIDA else ""))
    texto_sel = (m4.SAL / "modelo_seleccionado.txt").read_text(encoding="utf-8")
    clave = re.search(r"\(clave (\w+)\)", texto_sel).group(1)
    log(f"  Modelo seleccionado en 04_modelos.py: {m4.NOMBRES[clave]}")

    # Datos, partición y particiones: exactamente los de 04_modelos.py
    t, cat, binarias, numericas, _ = m4.cargar()
    columnas = cat + binarias + numericas
    X = t[columnas]
    reglas, _ = proxy.etiquetar(t, **proxy.BASE_UMBRALES)
    y = reglas["alerta"].to_numpy()
    ent, ytr, yte = m4.partir(t, y)
    Xtr, Xte = X[ent].reset_index(drop=True), X[~ent].reset_index(drop=True)
    tte = t[~ent].reset_index(drop=True)
    reglas_te = reglas[~ent].reset_index(drop=True)
    particiones = m4.particiones_agrupadas(t[ent].reset_index(drop=True), Xtr, ytr)
    base_cache = joblib.load(m4.CACHE / f"base_{clave}.joblib")
    params = joblib.load(m4.CACHE / f"busqueda_{clave}.joblib")["params"]
    modelo, umbral = base_cache["modelo"], base_cache["umbral"]
    puntaje_te = modelo.predict_proba(Xte)[:, 1]
    log(f"  AUC-PR en prueba del modelo leído: {average_precision_score(yte, puntaje_te):.4f} "
        f"(debe coincidir con metricas_prueba_2024.csv)")

    # 1-3. SHAP en prueba, importancia y dirección
    log("Valores SHAP en el conjunto de prueba (2024)")
    agregado, base, unidad = en_cache("shap_prueba", lambda: shap_agregado(modelo, clave, Xte, Xtr))
    imp = importancia(agregado)
    pd.DataFrame({"posicion": range(1, len(imp) + 1), "descriptor": [NOMBRE_DESC[d] for d in imp.index],
                  "importancia_media_absoluta": imp.values,
                  "porcentaje_de_la_importancia_total": imp.values / imp.sum() * 100,
                  "tiene_direccion_esperada": [d in ESPERADA for d in imp.index]}).round(4).to_csv(
        SAL / "importancia_global.csv", index=False, encoding="utf-8-sig")
    fig_importancia(imp, unidad, "fig_importancia_global.png")

    filas_num = []
    for d in [c for c in m4.NUM if c in agregado.columns]:
        ok = Xte[d].notna().to_numpy()
        rho, p = stats.spearmanr(Xte[d].to_numpy()[ok], agregado[d].to_numpy()[ok])
        filas_num.append({"descriptor": NOMBRE_DESC[d], "spearman": rho, "p_valor": p, "contratos": int(ok.sum()),
                          "direccion_esperada": ESPERADA.get(d, {}).get("texto", "Sin dirección esperada"),
                          "signo_esperado": ESPERADA.get(d, {}).get("signo", ""),
                          "signo_observado": "+" if rho > 0 else "-"})
    pd.DataFrame(filas_num).round(4).to_csv(SAL / "direccion_numericas.csv", index=False, encoding="utf-8-sig")
    fig_numericas(agregado, Xte, unidad)

    filas_cat = []
    for d in [c for c in cat + binarias if c in agregado.columns]:
        cats = categoria_modelo(modelo, d, Xte[d])
        g = agregado[d].groupby(cats.to_numpy())
        for categoria, s in g:
            filas_cat.append({"descriptor": NOMBRE_DESC[d], "categoria": categoria, "contratos": len(s),
                              "porcentaje_de_contratos": len(s) / len(Xte) * 100,
                              "contribucion_media": s.mean(), "desviacion": s.std(ddof=1)})
    tabla_cat = pd.DataFrame(filas_cat)
    tabla_cat.round(4).to_csv(SAL / "contribucion_por_categoria.csv", index=False, encoding="utf-8-sig")
    fig_categorias(tabla_cat, unidad)

    # 4. Estabilidad en las 15 particiones
    log(f"Estabilidad del orden de importancia ({len(particiones)} particiones)")
    importancias = []
    for i, (tr, va) in enumerate(particiones, start=1):
        def calcular(tr=tr, va=va):
            m = clone(m4.modelos(cat, binarias, numericas)[clave]).set_params(**params)
            m.fit(Xtr.iloc[tr], ytr[tr])
            a, _, _ = shap_agregado(m, clave, Xtr.iloc[va], Xtr.iloc[tr])
            return importancia(a)
        importancias.append(en_cache(f"particion_{i:02d}", calcular))
        log(f"  partición {i}/{len(particiones)}")
    imp_part = pd.DataFrame(importancias).reset_index(drop=True)[list(imp.index)]
    rangos = imp_part.rank(axis=1, ascending=False, method="average")
    W = w_kendall(rangos.to_numpy())
    top5 = (rangos <= TOP).mean() * 100
    rangos.index = [f"particion_{i}" for i in range(1, len(rangos) + 1)]
    rangos.rename(columns=NOMBRE_DESC).to_csv(SAL / "estabilidad_rangos_por_particion.csv", encoding="utf-8-sig")
    pd.DataFrame({"descriptor": [NOMBRE_DESC[d] for d in imp.index],
                  "posicion_en_prueba": range(1, len(imp) + 1),
                  "posicion_media_en_particiones": rangos.mean().values,
                  "posicion_minima": rangos.min().values, "posicion_maxima": rangos.max().values,
                  "porcentaje_particiones_entre_los_5_primeros": top5.values}).round(2).to_csv(
        SAL / "estabilidad_resumen.csv", index=False, encoding="utf-8-sig")
    fig_estabilidad(rangos)
    log(f"  W de Kendall = {W:.4f}")

    # 5. Explicaciones locales
    log("Explicaciones locales")
    grupos = {"Solo regla de adiciones": (reglas_te["regla1"] == 1) & (reglas_te["regla2"] == 0) & (reglas_te["regla3"] == 0),
              "Solo regla de prórrogas": (reglas_te["regla1"] == 0) & (reglas_te["regla2"] == 1) & (reglas_te["regla3"] == 0),
              "Reglas de adiciones y prórrogas": (reglas_te["regla1"] == 1) & (reglas_te["regla2"] == 1)}
    rng = np.random.default_rng(SEMILLA)
    filas_loc, n = [], 0
    for grupo, mascara in grupos.items():
        candidatos = np.flatnonzero(mascara.to_numpy())
        elegidos = np.sort(rng.choice(candidatos, size=min(N_LOCALES, len(candidatos)), replace=False))
        for idx in elegidos:
            n += 1
            codigo = f"C{n:02d}"
            contrib = agregado.iloc[idx]
            contrib.index = [f"{NOMBRE_DESC[d]} = {texto_valor(d, Xte.iloc[idx][d])}" for d in contrib.index]
            fig_local(codigo, contrib, base, puntaje_te[idx], unidad)
            for d in agregado.columns:
                filas_loc.append({"codigo": codigo, "grupo": grupo, "anio_firma": int(tte.loc[idx, "anio_firma"]),
                                  "puntaje": puntaje_te[idx], "supera_umbral": bool(puntaje_te[idx] >= umbral),
                                  "valor_base": base, "unidad": unidad, "descriptor": NOMBRE_DESC[d],
                                  "valor_del_descriptor": texto_valor(d, Xte.iloc[idx][d]),
                                  "contribucion": agregado.iloc[idx][d]})
    loc = pd.DataFrame(filas_loc)
    loc["posicion_en_el_contrato"] = loc.groupby("codigo")["contribucion"].transform(
        lambda s: s.abs().rank(ascending=False, method="first")).astype(int)
    loc.sort_values(["codigo", "posicion_en_el_contrato"]).round(4).to_csv(
        SAL / "explicaciones_locales.csv", index=False, encoding="utf-8-sig")

    # 6. Consistencia (base y sin valor ni plazo) y decisión de la Hipótesis 2
    log("Consistencia con la literatura y decisión de la Hipótesis 2")
    tabla_base, res_base = consistencia(agregado, Xte, "Modelo base")
    sv_cache = joblib.load(m4.CACHE / f"sin_valor_plazo_{clave}.joblib")
    columnas_sv = [c for c in columnas if c not in ("valor_inicial", "plazo_inicial_dias")]
    agregado_sv, _, _ = en_cache("shap_prueba_sin_valor_plazo",
                                 lambda: shap_agregado(sv_cache["modelo"], clave, Xte[columnas_sv], Xtr[columnas_sv]))
    tabla_sv, res_sv = consistencia(agregado_sv, Xte[columnas_sv], "Modelo sin valor ni plazo iniciales")
    pd.concat([tabla_base, tabla_sv]).round(4).to_csv(SAL / "consistencia_literatura.csv", index=False,
                                                      encoding="utf-8-sig")
    imp_sv = importancia(agregado_sv)
    pd.DataFrame({"posicion": range(1, len(imp_sv) + 1), "descriptor": [NOMBRE_DESC[d] for d in imp_sv.index],
                  "importancia_media_absoluta": imp_sv.values}).round(4).to_csv(
        SAL / "importancia_sin_valor_plazo.csv", index=False, encoding="utf-8-sig")
    fig_importancia(imp_sv, unidad, "fig_importancia_sin_valor_plazo.png")

    cumple_consistencia = res_base["resultado"] == "Se cumple"
    cumple_estabilidad = W >= UMBRAL_W
    n_cumple = int(cumple_consistencia) + int(cumple_estabilidad)
    decision = {2: "Se valida", 1: "Se valida parcialmente", 0: "Se rechaza"}[n_cumple]
    pd.DataFrame([{"criterio": "Consistencia con la literatura (modelo base)",
                   "resultado": res_base["resultado"],
                   "detalle": f"{res_base['coinciden']} de {res_base['evaluables']} descriptores evaluables "
                              f"entre los {TOP} primeros muestran la dirección esperada"},
                  {"criterio": f"Estabilidad (W de Kendall ≥ {UMBRAL_W})",
                   "resultado": "Se cumple" if cumple_estabilidad else "No se cumple",
                   "detalle": f"W = {W:.4f} en {len(particiones)} particiones"},
                  {"criterio": "Consistencia en el modelo sin valor ni plazo (se reporta; no cambia la decisión)",
                   "resultado": res_sv["resultado"],
                   "detalle": f"{res_sv['coinciden']} de {res_sv['evaluables']} descriptores evaluables"},
                  {"criterio": "Decisión sobre la Hipótesis 2", "resultado": decision, "detalle": ""}]).to_csv(
        SAL / "decision_h2.csv", index=False, encoding="utf-8-sig")

    minutos = (time.time() - inicio) / 60
    pd.DataFrame([{"etapa": "05_shap.py completo", "minutos": round(minutos, 2)}]).to_csv(
        SAL / "tiempos_computo.csv", index=False, encoding="utf-8-sig")
    log(f"  Consistencia (base): {res_base['resultado']} · Estabilidad: W = {W:.4f} · "
        f"Sin valor ni plazo: {res_sv['resultado']}")
    log(f"  Decisión sobre la Hipótesis 2: {decision}")
    log(f"Listo en {minutos:.1f} minutos. Resultados en {SAL}")


if __name__ == "__main__":
    main()
