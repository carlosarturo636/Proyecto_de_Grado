# Inventario de datos — Trabajo de grado (SECOP II, Atlántico)

Última actualización: 21/10/2026
Periodo de estudio: contratos **firmados entre 2021 y 2024** en el Departamento del Atlántico.
Fecha de corte de observación: **31/08/2026** (modificaciones y adiciones posteriores no se usan).

## Estructura

| Carpeta | Contenido | Regla |
|---|---|---|
| `01_CRUDOS/` | Datos tal como se descargaron de datos.gov.co | Nunca se editan ni se renombran |
| `02_DEPURADOS/` | Un archivo por fuente, filtrado a los contratos del estudio (sufijo `_atlantico`) | Solo los escribe el script de consolidación |
| `03_MODELADO/` | Tabla final: una fila por contrato, con variable dependiente y descriptores | Se construye a partir de `02_DEPURADOS` |
| `SCRIPTS/1_descarga/` | Scripts usados para descargar | Referencia y reproducibilidad |
| `SCRIPTS/2_consolidacion/` | Scripts de filtrado, unión y construcción de la tabla | — |
| `_DESCARTADOS/` | Archivos que no se usan (ver razón abajo) | Se pueden borrar cuando se decida |

## 01_CRUDOS

| Carpeta | Conjunto (código datos.gov.co) | Cobertura | Archivos | Registros | Filtro ya aplicado | Filtro pendiente |
|---|---|---|---|---|---|---|
| `CONTRATOS` | Contratos Electrónicos (jbjy-vk9h) | Firma 2021–2024 | 4 (uno por año) | 109.979 | Departamento = Atlántico | Población de vigilancia (7.2.1) y criterios de inclusión (7.2.2) |
| `PROCESOS` | Procesos de Contratación (p6dx-8zbt) | Publicación 2019–2024 + sin fecha | 7 | 132.334 filas (127.211 procesos) | Departamento = Atlántico | Conservar solo los procesos de los contratos del estudio |
| `PROVEEDORES` | Proveedores Registrados (qmzu-gj57) | Todos los registrados hasta el 05/10/2026 | 1 | 1.619.281 | Ninguno (nacional) | Conservar solo los proveedores de los contratos del estudio y solo las columnas no personales |
| `ADICIONES` | Adiciones (cb9c-h8sn) | Registro ene-2021 a ago-2026 | 68 (uno por mes) | 7.308.238 | Ninguno (nacional) | Conservar solo los contratos del estudio |
| `MODIFICACIONES` | Modificaciones a contratos (u8cx-r425) | Aprobación ene-2021 a ago-2026 | 26 (ver tabla) | — | Ninguno (nacional) | Rango de fechas por archivo + contratos del estudio + estado Publicado/Aprobado + sin duplicados |

### Qué periodo aporta cada archivo de MODIFICACIONES

| Archivo | Periodo que se toma |
|---|---|
| `SECOP_II_Modificaciones_a_contratos_2021.csv` … `_2024.csv` | Año completo |
| `modificaciones_nacional_2025_01.csv` … `_2025_12.csv` | Mes completo |
| `modificaciones_nacional_2026_01.csv`, `_2026_02.csv` | Mes completo |
| `SECOP_II_Modificaciones_a_contratos_01_03_2026_to_30_06_2026.csv` | **Solo marzo, abril y mayo** (junio viene cortado) |
| `SECOP_II_-_Modificaciones_a_contratos_2026_06.csv` | Junio 2026 |
| `SECOP_II_Modificaciones_a_contratos_01_07_2026_to_30_09_2026.csv` | **Solo julio** (agosto viene cortado) |
| `modificaciones_nacional_2026_08_dias01a27.csv` | **1 al 27 de agosto** (antes se llamaba checkpoint_modificaciones_2026_08.csv) |
| `modificaciones_dia_2026_08_28.csv` … `_31.csv` | 28 al 31 de agosto |

Esquemas de columnas: los archivos descargados desde la página usan etiquetas ("ID Contrato") y los descargados por API usan nombres de campo ("id_contrato"). Se unifican en la consolidación.

## Relaciones entre fuentes

| Unión | Llave | Tipo |
|---|---|---|
| Contratos → Procesos | `Proceso de Compra` = `id_del_portafolio` | Muchos contratos a un proceso (5.464 procesos generan más de un contrato); 4.082 contratos sin proceso encontrado |
| Contratos → Modificaciones | `ID Contrato` = `id_contrato` | Un contrato, muchas modificaciones |
| Contratos → Adiciones | `ID Contrato` = `id_contrato` | Un contrato, muchas adiciones |
| Contratos → Proveedores | `Codigo Proveedor` = `codigo` | Muchos contratos a un proveedor |

Hallazgos que condicionan el uso de los datos:
- `Valor del Contrato` y `Duración del contrato` (Contratos) son valores **vigentes**, no iniciales → el valor y el plazo iniciales salen de Procesos (o del historial de Modificaciones en procesos con varios contratos).
- `Valor Modificacion` (Modificaciones) es el valor **total** del contrato en esa versión, no el monto adicionado; `Dias extendidos` sí es incremento.

## 02_DEPURADOS (paso 2_consolidacion)

| Archivo | Origen | Granularidad | Registros |
|---|---|---|---|
| `contratos_atlantico.csv` | CONTRATOS | Una fila por contrato (sin 20 columnas personales) | 109.979 |
| `procesos_atlantico.csv` | PROCESOS | Filas de los procesos de los contratos del estudio | 73.731 (69.974 procesos) |
| `proveedores_atlantico.csv` | PROVEEDORES | Una fila por proveedor del estudio (11 columnas, sin datos personales) | 35.780 |
| `adiciones_atlantico.csv` | ADICIONES | Una fila por registro de adición | 108.962 |
| `modificaciones_atlantico.csv` | MODIFICACIONES | Una fila por registro de modificación (todas las versiones y estados) | 217.115 |
| `resumen_consolidacion.csv` | — | Registros leídos y conservados por archivo | — |

## 03_MODELADO (paso 3_modelado)

| Archivo o carpeta | Contenido |
|---|---|
| `tabla_modelado.csv` | Población final: 80.055 contratos × 32 columnas (identificación, construcción de la etiqueta, 12 predictores y marcas de escenarios) |
| `flujo_poblacion.csv`, `clasificacion_entidades.csv` | Exclusiones paso a paso y grupo de vigilancia de cada entidad |
| `calidad/` | Revisión de calidad de las fuentes y validación de la reconstrucción del valor inicial |
| `caracterizacion/` | Tablas descriptivas de la población |
| `proxy_base.csv`, `escenarios_sensibilidad.csv`, `percentiles_umbrales.csv`, `alertas_por_*.csv` | Proxy de riesgo y escenarios E0–E10 |
| `modelos/` | Búsqueda de hiperparámetros, métricas, pruebas, escenarios, decisión de H1 y figuras |
| `shap/` | Importancia, dirección, estabilidad, explicaciones locales, decisión de H2 y figuras |
| `priorizacion/` | Precisión y exhaustividad según la capacidad de revisión |

## _DESCARTADOS

| Archivo / carpeta | Razón |
|---|---|
| `ADICIONES_POR_AÑO_fechas_dañadas/` | Exportación del portal con la fecha de registro corrupta (mes y día reducidos a un dígito) y filas repetidas; reemplazada por la descarga mensual |
| `MODIFICACIONES_2026_08_manual_cortado.csv` | Exportación manual interrumpida por error 500 del portal en el 28/08; reemplazada por `..._dias01a27` + archivos por día |
