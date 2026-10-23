# -*- coding: utf-8 -*-
"""
PASO 2 - TABLA DE MODELADO (una fila por contrato)
======================================================================
Aplica sobre 02_DEPURADOS lo definido en Metodologia:
  7.2.1  Poblacion: entidades territoriales del Atlantico
  7.2.2  Criterios de exclusion y tratamientos especificos
  7.3.3  Valor y plazo iniciales, adiciones, prorrogas, descriptores
  6.1    Reglas 1 y 2 del proxy (la regla 3 se calcula en 03_proxy_sensibilidad.py
         con los contratos de 2021 a 2024, ver 6.1 y 7.3.3)

Salidas en 03_MODELADO:
  tabla_modelado.csv           una fila por contrato de la poblacion final
  flujo_poblacion.csv          contratos que quedan despues de cada criterio (8.1.1)
  clasificacion_entidades.csv  grupo de vigilancia asignado a cada entidad (7.2.1)

Uso:  python 01_tabla_modelado.py
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[2]
# Las carpetas pueden cambiarse con variables de entorno (las usa verificar_reproducibilidad.py)
DEP = Path(os.environ.get("SALIDA_DEPURADOS", BASE / "02_DEPURADOS"))
SAL = Path(os.environ.get("SALIDA_MODELADO", BASE / "03_MODELADO"))
SAL.mkdir(parents=True, exist_ok=True)

FECHA_CORTE = pd.Timestamp("2026-08-31")
UMBRAL_ADICION = 0.40   # regla 1 (6.1)
UMBRAL_PRORROGA = 0.50  # regla 2 (6.1)

# Ventanas de restriccion de la Ley 996 de 2005 en el periodo (7.3.3)
VENTANAS_GARANTIAS = [(pd.Timestamp("2021-11-13"), pd.Timestamp("2022-06-19")),
                      (pd.Timestamp("2023-06-29"), pd.Timestamp("2023-10-29"))]
MARGEN_GARANTIAS = pd.Timedelta(weeks=8)

PALABRAS_COVID = r"covid|coronavirus|pandemia|emergencia sanitaria|sars-cov"
TIPOS_CAMBIO_VALOR = {"Adicion en el valor"}  # tipologia de Adiciones que altera el valor

flujo = []


def paso(nombre, df, nota=""):
    flujo.append({"paso": len(flujo), "criterio": nombre, "contratos": len(df), "nota": nota})
    print(f"   {nombre:<60} {len(df):>8,}")


# ----------------------------------------------------------------------
# 1. Clasificacion de entidades por contraloria que las vigila (7.2.1)
# ----------------------------------------------------------------------
def grupo_vigilancia(nombre, orden):
    n = str(nombre).upper()
    if orden == "Nacional" or "POLICIA" in n or "CENAC" in n:
        return "Nacional (Contraloría General)"
    if orden == "Corporación Autónoma":
        return "Corporación autónoma o privada"
    if any(k in n for k in ["DISTRIT", "BARRANQUILLA VERDE", "IED ", "INEDISSA",
                            "EMPRESA DE DESARROLLO URBANO DE BARRANQUILLA",
                            "INSTITUCION UNIVERSITARIA DE BARRANQUILLA", "SIEMBRA MAS",
                            "NIÑO JESUS DE BARRANQUILLA"]):
        return "Distrito de Barranquilla (Contraloría Distrital)"
    if "AREA METROPOLITANA" in n.replace("Á", "A"):
        return "Área Metropolitana de Barranquilla"
    if ("SOLEDAD" in n or n == "HMI" or n.startswith("IET ") or "INOBASOL" in n
            or "MANUELA BELTRAN" in n or "MIGUEL ANTONIO CARO" in n or "VILLA ESTADIO" in n
            or "JESUS MAESTRO" in n or "ALBERTO PUMAREJO" in n or "JOSEFA DONADO" in n
            or "TAJAMAR" in n or "JOSE CASTILLO BOLIVAR" in n or "SAN ANTONIO DE PADUA" in n):
        return "Municipio de Soledad (Contraloría Municipal)"
    return "Departamento y otros municipios (Contraloría Departamental)"


TERRITORIALES = {"Distrito de Barranquilla (Contraloría Distrital)",
                 "Área Metropolitana de Barranquilla",
                 "Municipio de Soledad (Contraloría Municipal)",
                 "Departamento y otros municipios (Contraloría Departamental)"}


def a_dias(cantidad, unidad):
    cant = pd.to_numeric(cantidad, errors="coerce")
    u = unidad.astype("string").str.lower().fillna("")
    factor = np.select([u.str.startswith("d"), u.str.startswith("mes"), u.str.startswith("a"),
                        u.str.startswith("sem"), u.str.startswith("h")],
                       [1, 30, 365, 7, 1 / 24], default=np.nan)
    return cant * factor


def main():
    print("=" * 75 + "\nPASO 2 - TABLA DE MODELADO\n" + "=" * 75)
    c = pd.read_csv(DEP / "contratos_atlantico.csv", dtype=str, low_memory=False)
    c["valor_vigente"] = pd.to_numeric(c["Valor del Contrato"])
    c["fecha_firma"] = pd.to_datetime(c["Fecha de Firma"], errors="coerce")
    c["fecha_inicio"] = pd.to_datetime(c["Fecha de Inicio del Contrato"], errors="coerce")
    paso("Contratos del Atlántico firmados 2021-2024", c)

    # --- 7.2.1 Poblacion -------------------------------------------------
    c["grupo_vigilancia"] = [grupo_vigilancia(n, o) for n, o in zip(c["Nombre Entidad"], c["Orden"])]
    ent = (c.groupby(["Nombre Entidad", "Orden", "grupo_vigilancia"]).size()
             .reset_index(name="contratos").sort_values("contratos", ascending=False))
    ent.to_csv(SAL / "clasificacion_entidades.csv", index=False, encoding="utf-8-sig")
    c = c[c["grupo_vigilancia"].isin(TERRITORIALES)].copy()
    paso("Población: entidades territoriales (7.2.1)", c)

    # --- 7.2.2 Exclusiones directas ---------------------------------------
    c = c[c["Estado Contrato"].str.lower() != "cancelado"]
    paso("Excluye contratos cancelados", c)
    c = c[c["valor_vigente"] > 0]
    paso("Excluye contratos con valor igual a cero", c)

    # --- Modificaciones validas (7.3.3) ----------------------------------
    m = pd.read_csv(DEP / "modificaciones_atlantico.csv", dtype=str, low_memory=False)
    m = m[m["estado_modificacion"].isin(["Publicado", "Aprobado"]) & m["id_contrato"].isin(c["ID Contrato"])].copy()
    m["valor_version"] = pd.to_numeric(m["valor_modificacion"])
    m["dias_extendidos"] = pd.to_numeric(m["dias_extendidos"]).fillna(0)
    m["numero_version"] = pd.to_numeric(m["numero_version"])
    # Orden total y estable: el resultado no depende del orden en que se leyeron los archivos
    # ni del sistema operativo (reproducibilidad, sección 7.4.7).
    m = m.sort_values(list(m.columns), kind="mergesort", na_position="first")
    # Si una modificación aparece repetida con distintos días de extensión (registros del
    # portal que solo difieren en ese campo), se conserva la de mayor número de días.
    m = (m.sort_values(["id_contrato", "fecha_de_aprobacion", "numero_version", "dias_extendidos"], kind="mergesort")
           .drop_duplicates("identificador_modificacion", keep="last"))
    a = pd.read_csv(DEP / "adiciones_atlantico.csv", dtype=str, usecols=["identificador", "tipo"])
    a = a.sort_values(["identificador", "tipo"], kind="mergesort").drop_duplicates("identificador")
    m["tipo"] = m["identificador_modificacion"].map(a.set_index("identificador")["tipo"])

    # --- Procesos: una fila por proceso ----------------------------------
    p = pd.read_csv(DEP / "procesos_atlantico.csv", dtype=str)
    for col in ["precio_base", "valor_total_adjudicacion", "duracion"]:
        p[col] = pd.to_numeric(p[col])
    p["prioridad"] = ((p["adjudicado"] == "Si") & (p["valor_total_adjudicacion"] > 0)).astype(int)
    p = p.sort_values(list(p.columns), kind="mergesort", na_position="first")
    p = p.sort_values("prioridad", ascending=False, kind="mergesort").drop_duplicates("id_del_portafolio")
    p["valor_proceso"] = np.where(p["prioridad"] == 1, p["valor_total_adjudicacion"], p["precio_base"])
    p["plazo_proceso_dias"] = a_dias(p["duracion"], p["unidad_de_duracion"])
    todos = pd.read_csv(DEP / "contratos_atlantico.csv", dtype=str, usecols=["Proceso de Compra"])
    contratos_por_proceso = todos["Proceso de Compra"].value_counts()
    c["contratos_en_proceso"] = c["Proceso de Compra"].map(contratos_por_proceso)
    c = c.merge(p[["id_del_portafolio", "valor_proceso", "plazo_proceso_dias"]],
                left_on="Proceso de Compra", right_on="id_del_portafolio", how="left")

    # --- Valor inicial (7.3.3) -------------------------------------------
    hist = {}
    for cid, g in m.groupby("id_contrato", sort=False):
        vals = g["valor_version"].tolist()
        tipos = g["tipo"].tolist()
        hist[cid] = (vals, tipos)

    def reconstruir(cid, vigente):
        if cid not in hist:
            return vigente, "sin modificaciones"
        vals, tipos = hist[cid]
        cambio = None
        for i, v in enumerate(vals):
            prev = vals[i - 1] if i > 0 else None
            if tipos[i] in TIPOS_CAMBIO_VALOR or (prev is not None and not np.isclose(v, prev)):
                cambio = i
                break
        if cambio is None:
            return (vals[0] if not np.isnan(vals[0]) else vigente), "sin cambio de valor"
        if cambio == 0:
            return np.nan, "no determinable"
        return vals[cambio - 1], "versión previa al primer cambio"

    v0, fuente = [], []
    for cid, vig, n_proc, vproc in zip(c["ID Contrato"], c["valor_vigente"], c["contratos_en_proceso"], c["valor_proceso"]):
        if n_proc == 1 and pd.notna(vproc) and vproc > 0:
            v0.append(vproc); fuente.append("Procesos")
        else:
            val, f = reconstruir(cid, vig)
            v0.append(val); fuente.append("Historial: " + f)
    c["valor_inicial"] = v0
    c["fuente_valor_inicial"] = fuente

    # --- Plazo inicial (7.3.3) -------------------------------------------
    dur = c["Duración del contrato"].str.extract(r"(\d+)\s*(\D+)")
    plazo_vigente = a_dias(dur[0], dur[1])
    dias_ext = m.groupby("id_contrato")["dias_extendidos"].sum()
    c["dias_prorroga"] = c["ID Contrato"].map(dias_ext).fillna(0)
    respaldo = plazo_vigente - c["dias_prorroga"]
    c["plazo_inicial_dias"] = np.where(c["plazo_proceso_dias"] > 0, c["plazo_proceso_dias"],
                                       np.where(respaldo > 0, respaldo, np.nan))
    c["fuente_plazo_inicial"] = np.where(c["plazo_proceso_dias"] > 0, "Procesos", "Contrato menos prórrogas")

    c = c[c["valor_inicial"] > 0]
    paso("Excluye contratos sin valor inicial determinable", c)
    c = c[c["plazo_inicial_dias"] > 0]
    paso("Excluye contratos sin plazo inicial determinable", c)

    # --- Censura (7.2.2): plazo inicial vencido al corte ----------------
    inicio = c["fecha_inicio"].fillna(c["fecha_firma"])
    c["fin_pactado"] = inicio + pd.to_timedelta(c["plazo_inicial_dias"].round(), unit="D")
    c = c[c["fin_pactado"] <= FECHA_CORTE]
    paso("Excluye contratos con plazo inicial no vencido al 31/08/2026", c)

    # --- Adiciones en valor: incrementos entre versiones -----------------
    adic = {}
    for cid, vini in zip(c["ID Contrato"], c["valor_inicial"]):
        if cid not in hist:
            adic[cid] = 0.0
            continue
        prev, total = vini, 0.0
        for v in hist[cid][0]:
            if not np.isnan(v):
                total += max(0.0, v - prev)
                prev = v
        adic[cid] = total
    c["adiciones_valor"] = c["ID Contrato"].map(adic)

    # --- Reglas 1 y 2 (6.1) ---------------------------------------------
    # Razones con seis decimales: la comparación con el umbral no depende del redondeo de
    # centavos ni del equipo (mismo criterio que 03_proxy_sensibilidad.py; sección 8.1.1)
    c["ratio_adicion"] = (c["adiciones_valor"] / c["valor_inicial"]).round(6)
    c["ratio_prorroga"] = (c["dias_prorroga"] / c["plazo_inicial_dias"]).round(6)
    c["regla1_adicion"] = (c["ratio_adicion"] >= UMBRAL_ADICION).astype(int)
    c["regla2_prorroga"] = (c["ratio_prorroga"] >= UMBRAL_PRORROGA).astype(int)

    # --- Descriptores (Tabla 2) -----------------------------------------
    mod = c["Modalidad de Contratacion"].str.lower()
    c["modalidad"] = np.select([mod.str.contains("directa"), mod.str.contains("especial")],
                               ["Directa", "Régimen especial"], default="Competitiva")
    c["causal_directa"] = np.where(c["modalidad"] == "Directa",
                                   c["Justificacion Modalidad de Contratacion"], "No aplica")
    c["tipo_contrato"] = c["Tipo de Contrato"]
    c["segmento_unspsc"] = c["Codigo de Categoria Principal"].str.extract(r"(\d{2})")[0].fillna("Sin dato")
    c["sector_entidad"] = c["Sector"]
    c["orden_entidad"] = c["Orden"]
    prov = pd.read_csv(DEP / "proveedores_atlantico.csv", dtype=str, usecols=["Codigo", "Fecha Creación"])
    reg = pd.to_datetime(prov.set_index("Codigo")["Fecha Creación"], errors="coerce")
    c["antiguedad_proveedor_dias"] = (c["fecha_firma"] - c["Codigo Proveedor"].map(reg)).dt.days
    c.loc[c["antiguedad_proveedor_dias"] < 0, "antiguedad_proveedor_dias"] = 0
    c["es_pyme"] = (c["Es Pyme"].str.upper() == "SI").astype(int)
    c["persona_natural"] = (c["TipoDocProveedor"] != "NIT").astype(int)
    c["mes_firma"] = c["fecha_firma"].dt.month
    f = c["fecha_firma"]
    estado = pd.Series("Fuera", index=c.index)
    for ini, fin in VENTANAS_GARANTIAS:
        estado[(f >= ini - MARGEN_GARANTIAS) & (f < ini)] = "Previo"
        estado[(f > fin) & (f <= fin + MARGEN_GARANTIAS)] = "Posterior"
    for ini, fin in VENTANAS_GARANTIAS:
        estado[(f >= ini) & (f <= fin)] = "Durante"
    c["ley_garantias"] = estado

    # --- Marcas para escenarios de sensibilidad (7.2.2 y 7.4.1) ---------
    # Palabras clave buscadas en el objeto del contrato (sección 7.2.2)
    texto = c["Objeto del Contrato"].fillna("").str.lower()
    c["marca_covid"] = texto.str.contains(PALABRAS_COVID, regex=True).astype(int)
    c["marca_regimen_especial"] = (c["modalidad"] == "Régimen especial").astype(int)
    c["anio_firma"] = f.dt.year

    columnas = ["ID Contrato", "Codigo Entidad", "Nombre Entidad", "grupo_vigilancia", "Codigo Proveedor",
                "anio_firma", "Fecha de Firma", "fin_pactado",
                "valor_inicial", "fuente_valor_inicial", "plazo_inicial_dias", "fuente_plazo_inicial",
                "valor_vigente", "adiciones_valor", "dias_prorroga", "ratio_adicion", "ratio_prorroga",
                "regla1_adicion", "regla2_prorroga",
                "modalidad", "causal_directa", "tipo_contrato", "segmento_unspsc", "sector_entidad",
                "orden_entidad", "antiguedad_proveedor_dias", "es_pyme", "persona_natural",
                "mes_firma", "ley_garantias", "marca_covid", "marca_regimen_especial"]
    t = c[columnas].rename(columns={"ID Contrato": "id_contrato", "Codigo Entidad": "codigo_entidad",
                                    "Nombre Entidad": "nombre_entidad", "Codigo Proveedor": "codigo_proveedor",
                                    "Fecha de Firma": "fecha_firma"})
    t.to_csv(SAL / "tabla_modelado.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(flujo).to_csv(SAL / "flujo_poblacion.csv", index=False, encoding="utf-8-sig")

    print("\n   Población final:", f"{len(t):,}", "contratos ·", t["codigo_entidad"].nunique(), "entidades")
    print("   Por año de firma:", t["anio_firma"].value_counts().sort_index().to_dict())
    print("   Por grupo:", t["grupo_vigilancia"].value_counts().to_dict())
    print("   Fuente del valor inicial:", t["fuente_valor_inicial"].value_counts().to_dict())
    print(f"   Regla 1 (adición ≥ 40 %): {t['regla1_adicion'].mean():.1%} · "
          f"Regla 2 (prórroga ≥ 50 %): {t['regla2_prorroga'].mean():.1%} · "
          f"Regla 1 o 2: {((t['regla1_adicion'] + t['regla2_prorroga']) > 0).mean():.1%}")
    print(f"   COVID: {t['marca_covid'].sum():,} · Régimen especial: {t['marca_regimen_especial'].sum():,}")
    print("Listo: 03_MODELADO/tabla_modelado.csv, flujo_poblacion.csv, clasificacion_entidades.csv")


if __name__ == "__main__":
    main()
