"""
Paso 2b. Caracterización estadística de la población de estudio (sección 8.1.2).
Lee 03_MODELADO/tabla_modelado.csv y escribe tablas descriptivas en 03_MODELADO/caracterizacion/.
No usa la variable objetivo: solo describe la población.
"""
import sys
# Los mensajes usan tildes y símbolos como ≥: se escriben en UTF-8 aunque la salida se redirija a un archivo.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import os
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[2]
MOD = Path(os.environ.get("SALIDA_MODELADO", BASE / "03_MODELADO"))
SAL = MOD / "caracterizacion"
SAL.mkdir(parents=True, exist_ok=True)

t = pd.read_csv(MOD / "tabla_modelado.csv", dtype={"segmento_unspsc": str})
N = len(t)


def frecuencia(col, nombre):
    f = t[col].value_counts().rename("contratos").to_frame()
    f["porcentaje"] = (f["contratos"] / N * 100).round(1)
    if "valor_inicial" in t:
        v = t.groupby(col)["valor_inicial"].sum()
        f["porcentaje_valor"] = (v / t["valor_inicial"].sum() * 100).round(1)
    f.to_csv(SAL / f"{nombre}.csv", encoding="utf-8-sig")
    return f


for col, nombre in [("anio_firma", "por_anio"), ("grupo_vigilancia", "por_grupo"),
                    ("modalidad", "por_modalidad"), ("causal_directa", "por_causal"),
                    ("tipo_contrato", "por_tipo"), ("sector_entidad", "por_sector"),
                    ("segmento_unspsc", "por_segmento_unspsc"), ("mes_firma", "por_mes"),
                    ("ley_garantias", "por_ley_garantias")]:
    frecuencia(col, nombre)

# Variables numéricas
num = t[["valor_inicial", "plazo_inicial_dias", "antiguedad_proveedor_dias"]].describe(
    percentiles=[.25, .5, .75]).T
num.to_csv(SAL / "numericas.csv", encoding="utf-8-sig")

# Cruces por año y grupo
pd.crosstab(t["anio_firma"], t["modalidad"]).to_csv(SAL / "anio_x_modalidad.csv", encoding="utf-8-sig")
t.groupby("grupo_vigilancia").agg(
    contratos=("valor_inicial", "size"),
    entidades=("codigo_entidad", "nunique"),
    valor_mediano=("valor_inicial", "median"),
    plazo_mediano=("plazo_inicial_dias", "median"),
).to_csv(SAL / "por_grupo_resumen.csv", encoding="utf-8-sig")

# Proveedores (sin identificar a ninguno)
cp = t["codigo_proveedor"].value_counts()
pd.Series({
    "proveedores_distintos": cp.size,
    "contratos_por_proveedor_mediana": cp.median(),
    "contratos_por_proveedor_maximo": cp.max(),
    "porcentaje_persona_natural": round(t["persona_natural"].mean() * 100, 1),
    "porcentaje_pyme": round(t["es_pyme"].mean() * 100, 1),
    "porcentaje_antiguedad_menor_30_dias": round((t["antiguedad_proveedor_dias"] < 30).mean() * 100, 1),
    "antiguedad_faltante": int(t["antiguedad_proveedor_dias"].isna().sum()),
}).to_csv(SAL / "proveedores.csv", header=["valor"], encoding="utf-8-sig")

print(f"Caracterización de {N:,} contratos escrita en {SAL}")
