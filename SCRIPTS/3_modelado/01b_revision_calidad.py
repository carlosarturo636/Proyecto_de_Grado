"""
Paso 2a. Revisión de la calidad de las fuentes y de la construcción de la tabla de modelado
(sección 8.1.1, Etapas 3 y 5; sección 8.1.2, Tabla 18; sección 8.2.1).

Genera todas las cifras de la revisión de calidad que se reportan en el documento:
  - faltantes, columnas vacías y registros sin información en cada fuente consolidada;
  - procesos no adjudicados, con duración cero o repetidos;
  - estados y versiones repetidas de las modificaciones;
  - detalle de la población (exclusiones por tipo de entidad), del valor y el plazo iniciales
    y de los criterios aplicados a los descriptores;
  - categorías que conserva la agrupación de categorías poco frecuentes (Tabla 5);
  - validación de la reconstrucción del valor inicial con el historial de Modificaciones.

Requiere haber ejecutado 01_tabla_modelado.py. No modifica ningún archivo de entrada.
Salidas en 03_MODELADO/calidad/.
Uso:  python 01b_revision_calidad.py
"""
import sys
# Los mensajes usan tildes y símbolos como ≥: se escriben en UTF-8 aunque la salida se redirija a un archivo.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import os
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[2]
DEP = Path(os.environ.get("SALIDA_DEPURADOS", BASE / "02_DEPURADOS"))
MOD = Path(os.environ.get("SALIDA_MODELADO", BASE / "03_MODELADO"))
SAL = MOD / "calidad"
SAL.mkdir(parents=True, exist_ok=True)

ANIO_FIN_ENTRENAMIENTO = 2023
MIN_FRECUENCIA = 0.01           # agrupación de categorías poco frecuentes (Tabla 5)
TIPO_ADICION = "Adicion en el valor"
filas = []


def anotar(seccion, indicador, valor):
    filas.append({"seccion": seccion, "indicador": indicador, "valor": valor})
    print(f"   [{seccion}] {indicador}: {valor}")


def pct(a, b):
    return round(100 * a / b, 1)


def modificaciones_validas(m, ids):
    """Mismo criterio de 01_tabla_modelado.py: publicadas o aprobadas, una versión por modificación."""
    m = m[m["estado_modificacion"].isin(["Publicado", "Aprobado"]) & m["id_contrato"].isin(ids)].copy()
    m["valor_version"] = pd.to_numeric(m["valor_modificacion"])
    m["dias_extendidos"] = pd.to_numeric(m["dias_extendidos"]).fillna(0)
    m["numero_version"] = pd.to_numeric(m["numero_version"])
    m = m.sort_values(list(m.columns), kind="mergesort", na_position="first")
    return (m.sort_values(["id_contrato", "fecha_de_aprobacion", "numero_version", "dias_extendidos"],
                          kind="mergesort").drop_duplicates("identificador_modificacion", keep="last"))


def main():
    print("=" * 75 + "\nPASO 2a - REVISIÓN DE CALIDAD\n" + "=" * 75)
    c = pd.read_csv(DEP / "contratos_atlantico.csv", dtype=str, low_memory=False)
    p = pd.read_csv(DEP / "procesos_atlantico.csv", dtype=str)
    pr = pd.read_csv(DEP / "proveedores_atlantico.csv", dtype=str)
    a = pd.read_csv(DEP / "adiciones_atlantico.csv", dtype=str)
    m = pd.read_csv(DEP / "modificaciones_atlantico.csv", dtype=str, low_memory=False)
    t = pd.read_csv(MOD / "tabla_modelado.csv", dtype={"segmento_unspsc": str}, low_memory=False)
    ent_cls = pd.read_csv(MOD / "clasificacion_entidades.csv")
    n = len(c)

    # ---------------- Etapa 3: Contratos Electrónicos ----------------
    S = "Etapa 3 - Contratos"
    vacias = [k for k in c.columns if c[k].isna().all()]
    anotar(S, "columnas completamente vacías", f"{len(vacias)}: {'; '.join(vacias)}")
    col_prorroga = next(k for k in c.columns if "notificación" in k.lower() and "prorrog" in k.lower())
    anotar(S, "fecha de notificación de prórroga vacía (%)", pct(c[col_prorroga].isna().sum(), n))
    anotar(S, "fecha de inicio vacía (%)", round(100 * c["Fecha de Inicio del Contrato"].isna().mean(), 2))
    anotar(S, "categoría UNSPSC 'UNSPECIFIED' (contratos; %)",
           f"{(c['Codigo de Categoria Principal'] == 'UNSPECIFIED').sum()}; "
           f"{pct((c['Codigo de Categoria Principal'] == 'UNSPECIFIED').sum(), n)}")
    anotar(S, "tipo de documento del proveedor 'No Definido'", int((c["TipoDocProveedor"] == "No Definido").sum()))
    anotar(S, "tipo de contrato 'No Especificado'", int((c["Tipo de Contrato"] == "No Especificado").sum()))
    anotar(S, "justificación de la modalidad 'No Definido'",
           int((c["Justificacion Modalidad de Contratacion"] == "No Definido").sum()))
    con_adic = t[t["adiciones_valor"] > 0]
    coincide_suma = (np.abs(con_adic["valor_vigente"] / (con_adic["valor_inicial"] + con_adic["adiciones_valor"]) - 1) < 0.01)
    coincide_ini = (np.abs(con_adic["valor_vigente"] / con_adic["valor_inicial"] - 1) < 0.01)
    anotar(S, "contratos de la población con adiciones", len(con_adic))
    anotar(S, "valor de Contratos = valor inicial + adiciones (±1 %) (%)", round(100 * coincide_suma.mean(), 1))
    anotar(S, "valor de Contratos = valor inicial (±1 %) (%)", round(100 * coincide_ini.mean(), 1))

    # ---------------- Etapa 3: Procesos ----------------
    S = "Etapa 3 - Procesos"
    for k in ["precio_base", "valor_total_adjudicacion", "adjudicado", "duracion", "unidad_de_duracion"]:
        anotar(S, f"celdas vacías en {k}", int(p[k].isna().sum()))
    no_adj = p[(p["adjudicado"] == "No")]
    anotar(S, "registros no adjudicados (de total; %)", f"{len(no_adj)} de {len(p)}; {pct(len(no_adj), len(p))}")
    anotar(S, "no adjudicados con valor adjudicado = 0", int((pd.to_numeric(no_adj['valor_total_adjudicacion']) == 0).sum()))
    mod_no_adj = no_adj["modalidad_de_contratacion"].str.lower()
    anotar(S, "no adjudicados de contratación directa o régimen especial (%)",
           round(100 * mod_no_adj.str.contains("directa|especial").mean(), 1))
    p1 = p.drop_duplicates("id_del_portafolio")
    anotar(S, "procesos distintos", len(p1))
    anotar(S, "procesos con duración = 0 (%)",
           f"{(pd.to_numeric(p1['duracion']) == 0).sum()}; {pct((pd.to_numeric(p1['duracion']) == 0).sum(), len(p1))}")
    anotar(S, "filas de procesos registrados más de una vez", int((p["filas_del_portafolio"].astype(int) > 1).sum()))
    anotar(S, "contratos sin proceso asociado", int((~c["Proceso de Compra"].isin(p["id_del_portafolio"])).sum()))

    # ---------------- Etapa 3: Proveedores ----------------
    S = "Etapa 3 - Proveedores"
    anotar(S, "fecha de registro vacía", int(pr["Fecha Creación"].isna().sum()))
    anotar(S, "contratistas sin registro", len(set(c["Codigo Proveedor"].dropna()) - set(pr["Codigo"])))

    # ---------------- Etapa 3: Adiciones ----------------
    S = "Etapa 3 - Adiciones"
    tipos = a["tipo"].value_counts()
    for k, v in tipos.items():
        anotar(S, f"tipo '{k}' (registros; %)", f"{v}; {pct(v, len(a))}")

    # ---------------- Etapa 3: Modificaciones ----------------
    S = "Etapa 3 - Modificaciones"
    est = m["estado_modificacion"].value_counts()
    for k, v in est.items():
        anotar(S, f"estado '{k}' (registros; %)", f"{v}; {pct(v, len(m))}")
    val = m[m["estado_modificacion"].isin(["Publicado", "Aprobado"])].copy()
    anotar(S, "registros publicados o aprobados (%)", f"{len(val)}; {pct(len(val), len(m))}")
    g = val.groupby("identificador_modificacion").agg(n=("numero_version", "size"), versiones=("numero_version", "nunique"))
    anotar(S, "modificaciones publicadas o aprobadas que figuran más de una vez", int((g["n"] > 1).sum()))
    anotar(S, "   de ellas, con números de versión distintos", int(((g["n"] > 1) & (g["versiones"] > 1)).sum()))
    val["dias"] = pd.to_numeric(val["dias_extendidos"]).fillna(0)
    emp = val.groupby(["identificador_modificacion", "fecha_de_aprobacion", "numero_version"])["dias"].agg(["size", "nunique"])
    empates = emp[(emp["size"] > 1) & (emp["nunique"] > 1)].index.get_level_values(0).unique()
    anotar(S, "modificaciones repetidas con igual versión y fecha y distintos días", len(empates))
    anotar(S, "   de ellas, de contratos de la población final",
           int(val[val["identificador_modificacion"].isin(empates) & val["id_contrato"].isin(t["id_contrato"])]
               ["identificador_modificacion"].nunique()))

    # ---------------- Etapa 5: población ----------------
    S = "Etapa 5 - Población"
    for grupo, sub in ent_cls.groupby("grupo_vigilancia"):
        anotar(S, f"{grupo} (entidades; contratos)", f"{len(sub)}; {sub['contratos'].sum()}")
    corregidas = ent_cls[ent_cls["grupo_vigilancia"].str.startswith("Nacional") & (ent_cls["Orden"] != "Nacional")]
    anotar(S, "entidades registradas como territoriales y reclasificadas como nacionales",
           "; ".join(f"{r['Nombre Entidad']} ({r['contratos']})" for _, r in corregidas.iterrows()))
    canc = c[c["Estado Contrato"].str.lower() == "cancelado"]
    anotar(S, "contratos cancelados en el conjunto", len(canc))
    anotar(S, "entidades territoriales antes y después de las exclusiones",
           f"{int((~ent_cls['grupo_vigilancia'].str.startswith(('Nacional', 'Corporación'))).sum())}; "
           f"{t['codigo_entidad'].nunique()}")

    # ---------------- Etapa 5: valor y plazo iniciales ----------------
    S = "Etapa 5 - Valor y plazo"
    N = len(t)
    for k, v in t["fuente_valor_inicial"].value_counts().items():
        anotar(S, f"fuente del valor inicial '{k}' (contratos; %)", f"{v}; {pct(v, N)}")
    pp = p.copy()
    pp["prioridad"] = ((pp["adjudicado"] == "Si") & (pd.to_numeric(pp["valor_total_adjudicacion"]) > 0)).astype(int)
    pp = pp.sort_values("prioridad", ascending=False, kind="mergesort").drop_duplicates("id_del_portafolio")
    x = t.merge(c[["ID Contrato", "Proceso de Compra"]], left_on="id_contrato", right_on="ID Contrato") \
         .merge(pp[["id_del_portafolio", "prioridad", "duracion"]], left_on="Proceso de Compra",
                right_on="id_del_portafolio", how="left")
    proc = x[x["fuente_valor_inicial"] == "Procesos"]
    anotar(S, "valor de Procesos: adjudicado; precio base",
           f"{int((proc['prioridad'] == 1).sum())}; {int((proc['prioridad'] == 0).sum())}")
    sin_ad = proc[proc["adiciones_valor"] == 0]
    anotar(S, "contratos con valor de Procesos y sin adiciones", len(sin_ad))
    anotar(S, "   valor de Procesos = valor de Contratos (±1 %) (%)",
           round(100 * (np.abs(sin_ad["valor_inicial"] / sin_ad["valor_vigente"] - 1) < 0.01).mean(), 1))
    for k, v in t["fuente_plazo_inicial"].value_counts().items():
        anotar(S, f"fuente del plazo inicial '{k}' (contratos; %)", f"{v}; {pct(v, N)}")
    resp = x[x["fuente_plazo_inicial"] != "Procesos"]
    anotar(S, "plazo de respaldo: sin proceso; proceso con duración 0",
           f"{int(resp['id_del_portafolio'].isna().sum())}; {int((pd.to_numeric(resp['duracion']) == 0).sum())}")
    anotar(S, "contratos con plazo inicial menor a un día", int((t["plazo_inicial_dias"] < 1).sum()))

    # ---------------- Etapa 5: descriptores ----------------
    S = "Etapa 5 - Descriptores"
    reg = pd.to_datetime(pr.set_index("Codigo")["Fecha Creación"], errors="coerce")
    ct = c[c["ID Contrato"].isin(t["id_contrato"])]
    ant = (pd.to_datetime(ct["Fecha de Firma"]) - ct["Codigo Proveedor"].map(reg)).dt.days
    anotar(S, "contratos con registro del proveedor posterior a la firma (antigüedad = 0)", int((ant < 0).sum()))
    anotar(S, "contratos con tipo de documento 'Otro' o 'No Definido' (persona natural)",
           int(ct["TipoDocProveedor"].isin(["Otro", "No Definido"]).sum()))
    anotar(S, "contratos con categoría UNSPSC 'Sin dato'", int((t["segmento_unspsc"] == "Sin dato").sum()))
    anotar(S, "contratos sin antigüedad del proveedor (sin registro)",
           f"{int(t['antiguedad_proveedor_dias'].isna().sum())}; "
           f"{t.loc[t['antiguedad_proveedor_dias'].isna(), 'codigo_proveedor'].nunique()} contratistas")

    # ---------------- Tabla 18: categorías tras la agrupación ----------------
    tr = t[t["anio_firma"] <= ANIO_FIN_ENTRENAMIENTO]
    cat_filas = []
    for col in ["modalidad", "causal_directa", "tipo_contrato", "segmento_unspsc", "sector_entidad",
                "ley_garantias", "mes_firma"]:
        vc = tr[col].astype(str).value_counts()
        conservadas = vc[vc >= MIN_FRECUENCIA * len(tr)]
        cat_filas.append({"descriptor": col, "categorias_en_entrenamiento": len(vc),
                          "categorias_conservadas": len(conservadas),
                          "porcentaje_agrupado_en_otras": pct(vc.sum() - conservadas.sum(), len(tr)),
                          "conservadas": "; ".join(f"{k} ({pct(v, len(tr))})" for k, v in conservadas.items())})
    pd.DataFrame(cat_filas).to_csv(SAL / "categorias_conservadas.csv", index=False, encoding="utf-8-sig")
    print(pd.DataFrame(cat_filas).drop(columns="conservadas").to_string(index=False))

    # ---------------- 8.2.1: historial y validación de la regla de adiciones ----------------
    S = "8.2.1 - Historial y regla de adiciones"
    mv = modificaciones_validas(m, t["id_contrato"])
    anotar(S, "contratos con al menos una modificación publicada o aprobada (%)",
           f"{mv['id_contrato'].nunique()}; {pct(mv['id_contrato'].nunique(), N)}")
    anotar(S, "modificaciones de la población", len(mv))
    anotar(S, "contratos con al menos una prórroga (%)", f"{int((t['dias_prorroga'] > 0).sum())}; "
                                                       f"{pct((t['dias_prorroga'] > 0).sum(), N)}")
    anotar(S, "contratos con al menos una adición (%)", f"{int((t['adiciones_valor'] > 0).sum())}; "
                                                      f"{pct((t['adiciones_valor'] > 0).sum(), N)}")
    con_mod = t[t["id_contrato"].isin(mv["id_contrato"])]
    for k, v in con_mod.groupby("fuente_valor_inicial")["regla1_adicion"].agg(["size", "mean"]).iterrows():
        anotar(S, f"regla 1 entre contratos con modificaciones, '{k}' (contratos; %)",
               f"{int(v['size'])}; {round(100 * v['mean'], 1)}")

    # Validación: se aplica el método del historial a los contratos cuyo valor inicial se conoce (Procesos)
    tipos_mod = a.sort_values(["identificador", "tipo"]).drop_duplicates("identificador").set_index("identificador")["tipo"]
    mv["tipo"] = mv["identificador_modificacion"].map(tipos_mod)
    hist = {cid: (g["valor_version"].tolist(), g["tipo"].tolist()) for cid, g in mv.groupby("id_contrato", sort=False)}

    def valor_historial(cid):
        vals, tps = hist[cid]
        for i, v in enumerate(vals):
            if tps[i] == TIPO_ADICION or (i > 0 and not np.isclose(v, vals[i - 1])):
                return np.nan if i == 0 else vals[i - 1]
        return vals[0]

    def adiciones(cid, vini):
        prev, total = vini, 0.0
        for v in hist[cid][0]:
            if not np.isnan(v):
                total += max(0.0, v - prev)
                prev = v
        return total

    val_p = t[(t["fuente_valor_inicial"] == "Procesos") & t["id_contrato"].isin(hist)].copy()
    val_p["vini_hist"] = [valor_historial(k) for k in val_p["id_contrato"]]
    ok = val_p["vini_hist"] > 0
    val_p.loc[ok, "r1_hist"] = [
        int(round(adiciones(k, v) / v, 6) >= 0.40) for k, v in zip(val_p.loc[ok, "id_contrato"], val_p.loc[ok, "vini_hist"])]
    anotar(S, "validación: contratos con valor de Procesos y modificaciones", len(val_p))
    anotar(S, "validación: cumplen la regla 1 con el valor de Procesos", int(val_p["regla1_adicion"].sum()))
    anotar(S, "validación: la cumplen con el método del historial (%)",
           f"{int(val_p['r1_hist'].sum())}; {pct(val_p['r1_hist'].sum(), val_p['regla1_adicion'].sum())}")
    proxy = pd.read_csv(MOD / "proxy_base.csv")
    tp = t.merge(proxy[["id_contrato", "regla3"]], on="id_contrato")
    pm = tp[(tp["fuente_valor_inicial"] == "Procesos") & tp["id_contrato"].isin(hist)]
    solo_r1 = ((pm["regla1_adicion"] == 1) & (pm["regla2_prorroga"] == 0) & (pm["regla3"] == 0)).mean()
    sin_cambio = (t["fuente_valor_inicial"] == "Historial: sin cambio de valor")
    anotar(S, "estimación de alertas no detectadas, referencia: todos los contratos con valor de Procesos (solo regla 1)",
           int(round(solo_r1 * sin_cambio.sum())))
    comparables = pm[(pm["modalidad"] == "Directa") & (pm["tipo_contrato"] == "Prestación de servicios")]
    solo_r1_c = ((comparables["regla1_adicion"] == 1) & (comparables["regla2_prorroga"] == 0)
                 & (comparables["regla3"] == 0)).mean()
    afectados = t[sin_cambio]
    anotar(S, "perfil del grupo afectado: contratación directa (%); prestación de servicios (%)",
           f"{round(100 * (afectados['modalidad'] == 'Directa').mean(), 1)}; "
           f"{round(100 * (afectados['tipo_contrato'] == 'Prestación de servicios').mean(), 1)}")
    anotar(S, "referencia comparable (directa y prestación de servicios): contratos; solo regla 1 (%)",
           f"{len(comparables)}; {round(100 * solo_r1_c, 2)}")
    anotar(S, "estimación de alertas no detectadas, referencia comparable (solo regla 1)",
           int(round(solo_r1_c * sin_cambio.sum())))
    for anio, s in t.groupby("anio_firma"):
        anotar(S, f"contratos de {anio} con valor de la primera versión (%)",
               round(100 * (s["fuente_valor_inicial"] == "Historial: sin cambio de valor").mean(), 1))

    # ---------------- 8.2.2: tiempo de observación y percentiles con solo entrenamiento ----------------
    S = "8.2.2 - Observación y percentiles"
    meses_obs = (pd.Timestamp("2026-08-31") - pd.to_datetime(t["fin_pactado"])).dt.days / 30.44
    for anio, v in meses_obs.groupby(t["anio_firma"]).median().items():
        anotar(S, f"meses de observación después del fin pactado, mediana, contratos de {anio}", round(v, 1))
    mv2 = mv.merge(t[["id_contrato", "fecha_firma", "anio_firma"]], on="id_contrato")
    mv2 = mv2[mv2["dias_extendidos"] > 0]
    meses_ap = (pd.to_datetime(mv2["fecha_de_aprobacion"]) - pd.to_datetime(mv2["fecha_firma"])).dt.days / 30.44
    for anio, v in (meses_ap > 20).groupby(mv2["anio_firma"]).mean().items():
        anotar(S, f"prórrogas aprobadas más de 20 meses después de la firma (%), contratos de {anio}", round(100 * v, 1))
    ent = t["anio_firma"] <= ANIO_FIN_ENTRENAMIENTO
    ra = (t["adiciones_valor"] / t["valor_inicial"])[ent]
    rp = (t["dias_prorroga"] / t["plazo_inicial_dias"])[ent]
    anotar(S, "percentiles 25/50/75/90 de la razón de adición, solo entrenamiento",
           "; ".join(f"{v:.3f}" for v in ra[ra > 0].quantile([.25, .5, .75, .9])))
    anotar(S, "percentiles 25/50/75/90 de la razón de prórroga, solo entrenamiento",
           "; ".join(f"{v:.3f}" for v in rp[rp > 0].quantile([.25, .5, .75, .9])))

    pd.DataFrame(filas).to_csv(SAL / "revision_calidad.csv", index=False, encoding="utf-8-sig")
    print(f"Listo: {SAL / 'revision_calidad.csv'} y {SAL / 'categorias_conservadas.csv'}")


if __name__ == "__main__":
    main()
