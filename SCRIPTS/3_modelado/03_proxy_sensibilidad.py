"""
Paso 3. Proxy de riesgo contractual y análisis de sensibilidad (secciones 7.4.1 y 8.2).

Regla 1: adiciones en valor >= 40 % del valor inicial.
Regla 2: días de prórroga >= 50 % del plazo inicial.
Regla 3: el contratista concentra >= 30 % del valor contratado por la entidad
         entre 2021 y 2024, en entidades con >= 30 contratos en ese periodo
         (definición de la sección 6.1). Como las reglas 1 y 2, la etiqueta usa
         información posterior a la firma; ningún predictor la usa (sección 4.3.2).
Alerta (Y = 1) si se cumple al menos una regla.

Escenarios comprometidos en el documento: 7.2.2 (sin régimen especial, sin COVID,
mínimos de 10 y 50 contratos para la regla 3) y 4.3.2 (efecto de combinar las reglas
por disyunción: escenario que exige al menos dos reglas).

Escenarios: se cambia el umbral de UNA regla a la vez y las otras dos quedan en su valor base.
Los umbrales alternativos se justifican con percentiles de la distribución observada.
"""
import os
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[2]
MOD = Path(os.environ.get("SALIDA_MODELADO", BASE / "03_MODELADO"))
ANIO_FIN_ENTRENAMIENTO = 2023

BASE_UMBRALES = dict(u1=0.40, u2=0.50, u3=0.30, m3=30, minimo=1)

ESCENARIOS = [
    # nombre, regla variada, cambios, justificación
    ("E0 Base", "—", {}, "Umbrales definidos en la sección 6.1"),
    ("E1 R1 bajo", "Regla 1", dict(u1=0.25), "Percentil 25 de la razón de adición entre contratos con adición"),
    ("E2 R1 alto", "Regla 1", dict(u1=0.50), "Percentil 75 de la razón de adición; tope legal del 50 % (Ley 80 de 1993, art. 40)"),
    ("E3 R2 bajo", "Regla 2", dict(u2=0.40), "Mediana de la razón de prórroga entre contratos prorrogados"),
    ("E4 R2 alto", "Regla 2", dict(u2=0.70), "Percentil 90 de la razón de prórroga entre contratos prorrogados"),
    ("E5 R3 umbral bajo", "Regla 3", dict(u3=0.15), "Mediana de la participación máxima de un contratista por entidad"),
    ("E6 R3 mínimo 10", "Regla 3", dict(m3=10), "Mínimo de contratos por entidad reducido a 10 (sección 7.2.2)"),
    ("E7 R3 mínimo 50", "Regla 3", dict(m3=50), "Mínimo de contratos por entidad aumentado a 50 (sección 7.2.2)"),
    ("E8 Sin régimen especial", "Población", dict(excluir="marca_regimen_especial"), "Contratos no sujetos al tope del art. 40 de la Ley 80 (sección 7.2.2)"),
    ("E9 Sin COVID-19", "Población", dict(excluir="marca_covid"), "Contratos que el Decreto 537 de 2020 permitió adicionar sin límite (sección 7.2.2)"),
    ("E10 Al menos dos reglas", "Combinación", dict(minimo=2), "Alternativa a la disyunción de las reglas (sección 4.3.2)"),
]


def pares_concentrados(entrenamiento, u3, m3):
    """Pares entidad-contratista con participación >= u3 en entidades con >= m3 contratos."""
    n = entrenamiento.groupby("codigo_entidad").size()
    total = entrenamiento.groupby("codigo_entidad")["valor_inicial"].sum()
    p = entrenamiento.groupby(["codigo_entidad", "codigo_proveedor"])["valor_inicial"].sum().reset_index()
    p["participacion"] = p["valor_inicial"] / p["codigo_entidad"].map(total)
    p["contratos_entidad"] = p["codigo_entidad"].map(n)
    return p[(p["participacion"] >= u3) & (p["contratos_entidad"] >= m3)]


def etiquetar(t, u1, u2, u3, m3, minimo=1):
    # Las razones se redondean a 6 decimales para que la comparación con el umbral
    # no dependa de errores de punto flotante (mismo resultado en cualquier equipo).
    r1 = ((t["adiciones_valor"] / t["valor_inicial"]).round(6) >= u1).astype(int)
    r2 = ((t["dias_prorroga"] / t["plazo_inicial_dias"]).round(6) >= u2).astype(int)
    pares = pares_concentrados(t, u3, m3)
    clave = set(zip(pares["codigo_entidad"], pares["codigo_proveedor"]))
    r3 = pd.Series([int(k in clave) for k in zip(t["codigo_entidad"], t["codigo_proveedor"])], index=t.index)
    y = ((r1 + r2 + r3) >= minimo).astype(int)
    return pd.DataFrame({"regla1": r1, "regla2": r2, "regla3": r3, "alerta": y}), len(pares)


def resumen(e, t):
    ent = t["anio_firma"] <= ANIO_FIN_ENTRENAMIENTO
    solo = lambda c: int(((e[c] == 1) & (e[["regla1", "regla2", "regla3"]].sum(axis=1) == 1)).sum())
    return {
        "alertas": int(e["alerta"].sum()),
        "prevalencia_total_%": round(e["alerta"].mean() * 100, 2),
        "prevalencia_entrenamiento_%": round(e.loc[ent, "alerta"].mean() * 100, 2),
        "prevalencia_prueba_%": round(e.loc[~ent, "alerta"].mean() * 100, 2),
        "regla1": int(e["regla1"].sum()), "regla2": int(e["regla2"].sum()), "regla3": int(e["regla3"].sum()),
        "solo_regla1": solo("regla1"), "solo_regla2": solo("regla2"), "solo_regla3": solo("regla3"),
        "regla1_y_regla2": int(((e["regla1"] == 1) & (e["regla2"] == 1)).sum()),
    }


def main():
    t = pd.read_csv(MOD / "tabla_modelado.csv", dtype={"segmento_unspsc": str})

    # Percentiles que justifican los umbrales alternativos
    ra = t["adiciones_valor"] / t["valor_inicial"]
    rp = t["dias_prorroga"] / t["plazo_inicial_dias"]
    todos = pares_concentrados(t, 0, 0)
    n = t.groupby("codigo_entidad").size()
    mx = todos.groupby("codigo_entidad")["participacion"].max()
    q = [.25, .5, .75, .9]
    pct = pd.DataFrame({
        "razon_adicion (contratos con adición)": ra[ra > 0].quantile(q).values,
        "razon_prorroga (contratos prorrogados)": rp[rp > 0].quantile(q).values,
        "participacion_maxima (entidades >= 30 contratos, 2021-2024)": mx[n.reindex(mx.index) >= 30].quantile(q).values,
    }, index=["p25", "p50", "p75", "p90"]).round(3)
    pct.to_csv(MOD / "percentiles_umbrales.csv", encoding="utf-8-sig")

    filas = []
    for nombre, regla, cambios, just in ESCENARIOS:
        u = {**BASE_UMBRALES, **cambios}
        excluir = u.pop("excluir", None)
        ti = t[t[excluir] == 0].reset_index(drop=True) if excluir else t
        e, npares = etiquetar(ti, **u)
        filas.append({"escenario": nombre, "regla_variada": regla, "contratos": len(ti),
                      "umbrales": f"R1 {u['u1']:.0%} · R2 {u['u2']:.0%} · R3 {u['u3']:.0%} (mín. {u['m3']})"
                                  + (" · ≥ 2 reglas" if u["minimo"] == 2 else ""),
                      "justificacion": just, "pares_concentrados": npares, **resumen(e, ti)})
        if nombre.startswith("E0"):
            base = pd.concat([t[["id_contrato", "anio_firma"]], e], axis=1)
            base.to_csv(MOD / "proxy_base.csv", index=False, encoding="utf-8-sig")
            pd.crosstab(t["anio_firma"], e["alerta"], margins=True).to_csv(MOD / "alertas_por_anio.csv", encoding="utf-8-sig")
            for col in ["grupo_vigilancia", "modalidad"]:
                g = pd.concat([t[col], e["alerta"]], axis=1).groupby(col)["alerta"].agg(["size", "sum", "mean"])
                g["mean"] = (g["mean"] * 100).round(2)
                g.to_csv(MOD / f"alertas_por_{col}.csv", encoding="utf-8-sig")
    esc = pd.DataFrame(filas)
    esc.to_csv(MOD / "escenarios_sensibilidad.csv", index=False, encoding="utf-8-sig")

    pd.set_option("display.width", 250)
    print(pct.to_string())
    print(esc.drop(columns=["justificacion"]).to_string(index=False))
    print("Listo: proxy_base.csv, escenarios_sensibilidad.csv, percentiles_umbrales.csv, alertas_por_*.csv")


if __name__ == "__main__":
    main()
