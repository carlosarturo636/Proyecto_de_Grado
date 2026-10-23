# 3_modelado

Scripts que construyen la tabla de modelado, la caracterizan y generan la variable objetivo. Se ejecutan en este orden desde esta carpeta:

| Script | Qué hace | Salida en `03_MODELADO/` | Sección del documento |
|---|---|---|---|
| `01_tabla_modelado.py` | Aplica la población (7.2.1) y los criterios de exclusión (7.2.2); reconstruye valor y plazo iniciales; calcula adiciones, prórrogas y descriptores (Tabla 2) | `tabla_modelado.csv`, `flujo_poblacion.csv`, `clasificacion_entidades.csv` | 7.3.3, 8.1.1 |
| `01b_revision_calidad.py` | Revisión de calidad de cada fuente y de la construcción de la tabla: faltantes, estados, versiones repetidas, fuentes del valor y del plazo, categorías conservadas y validación de la regla de adiciones | `calidad/revision_calidad.csv`, `calidad/categorias_conservadas.csv` | 8.1.1 (Etapas 3 y 5), 8.1.2, 8.2.1 |
| `02_caracterizacion.py` | Tablas descriptivas de la población (sin usar la variable objetivo) | `caracterizacion/*.csv` | 8.1.2 |
| `03_proxy_sensibilidad.py` | Proxy de riesgo contractual (reglas 1 a 3) y escenarios de sensibilidad E0–E10 | `proxy_base.csv`, `escenarios_sensibilidad.csv`, `percentiles_umbrales.csv`, `alertas_por_*.csv` | 7.4.1, 8.2 |
| `04_modelos.py` | Búsqueda de hiperparámetros, validación cruzada agrupada, comparación de modelos, escenarios E1–E10, modelo sin valor ni plazo y decisión de la Hipótesis 1 | `modelos/*.csv`, `modelos/figuras/` | 7.4.2–7.4.5, 8.3 |
| `04b_diagnostico_particiones.py` | Compara la validación cruzada aleatoria con la agrupada (fuga de información) y redibuja la figura de ventaja frente a prevalencia | `modelos/diagnostico_particiones.csv`, `modelos/diagnostico_grupos.csv` | 7.4.3, 8.3.1 |
| `05_shap.py` | Valores SHAP del modelo seleccionado: importancia global, dirección del efecto, estabilidad (W de Kendall), 15 explicaciones locales y decisión de la Hipótesis 2 | `shap/*.csv`, `shap/figuras/` | 7.4.6, 8.4, 8.6 |
| `06_priorizacion.py` | Evaluación del marco de priorización: precisión y exhaustividad al revisar el 5 %, 10 % y 20 % de los contratos de prueba, en total y por grupo de vigilancia, con bootstrap por grupos | `priorizacion/*.csv`, `priorizacion/figuras/` | 7.4.8, 8.5 |

Los resultados son deterministas: no dependen del orden de lectura de los archivos ni del sistema operativo.

`05_shap.py` necesita los resultados de `04_modelos.py`. Ambos admiten una prueba rápida con la variable de entorno `PRUEBA_RAPIDA=1`.
