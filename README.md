# Clasificación de alertas de riesgo contractual en el Departamento del Atlántico

Código del trabajo de grado **"Clasificación de Alertas de Riesgo Contractual en el Departamento del Atlántico mediante Aprendizaje Automático Supervisado e Inteligencia Artificial Explicable"**, Maestría en Ciencia de Datos, Universidad EAN.

- **Autor:** Carlos Arturo Tamayo Mojica
- **Directora:** Carolina María Luque Zabala

## Propósito

Comparar modelos de aprendizaje supervisado (Regresión Logística, Random Forest y XGBoost) para clasificar alertas de riesgo contractual en los contratos de las entidades territoriales del Departamento del Atlántico firmados entre 2021 y 2024, y explicar sus predicciones mediante valores SHAP. Las alertas se definen con un proxy de tres reglas observables en SECOP II (adiciones, prórrogas y concentración de contratistas). Una alerta **no** implica irregularidad: es un criterio para priorizar la vigilancia.

## Estructura del repositorio

```
├── SCRIPTS/
│   ├── 1_descarga/                 Descarga programática desde datos.gov.co
│   ├── 2_consolidacion/            Un archivo depurado por fuente (→ 02_DEPURADOS)
│   ├── 3_modelado/                 Tabla de modelado, calidad, proxy, modelos, SHAP y priorización (→ 03_MODELADO)
│   └── verificar_reproducibilidad.py   Ejecuta todo de nuevo en una carpeta aparte y compara los resultados
├── INVENTARIO_DATOS.md             Qué contiene cada archivo de datos y qué periodo aporta
├── requirements.txt                Versiones exactas de las librerías
└── README.md
```

Las carpetas de datos (`01_CRUDOS`, `02_DEPURADOS`, `03_MODELADO`) **no se incluyen**: suman cerca de 26 GB y algunos archivos originales contienen datos personales de contratistas. Tampoco se publican los modelos entrenados ni los documentos de referencia. Para reproducir el estudio, las carpetas de datos se crean al lado de `SCRIPTS/`, con los mismos nombres.

## Fuentes de datos (SECOP II, datos abiertos)

| Conjunto | Código | Cobertura usada |
|---|---|---|
| Contratos Electrónicos | `jbjy-vk9h` | Atlántico, contratos firmados 2021–2024 |
| Procesos de Contratación | `p6dx-8zbt` | Atlántico, procesos publicados 2019–2024 y procesos sin fecha |
| Modificaciones a contratos | `u8cx-r425` | Nacional, aprobadas ene-2021 a ago-2026 |
| Adiciones | `cb9c-h8sn` | Nacional, registradas ene-2021 a ago-2026 |
| Proveedores Registrados | `qmzu-gj57` | Registro completo al 5 de octubre de 2026 |

Fecha de corte de observación: **31 de agosto de 2026**.

## Entorno

- Python 3.14.6, Windows 11, ejecución solo en CPU.
- Instalación de librerías: `pip install -r requirements.txt`

## Credenciales de la API

Los scripts de descarga usan una clave de API de datos.gov.co. **Las credenciales no están en el repositorio.** Para ejecutarlos:

1. Copia `SCRIPTS/1_descarga/credenciales_api_ejemplo.py` como `SCRIPTS/1_descarga/credenciales_api.py`.
2. Escribe tu `APP_TOKEN_ID` y tu `APP_TOKEN_SECRET`.

`credenciales_api.py` está en `.gitignore` y nunca se sube.

## Cómo reproducir

**1. Descarga** (desde `SCRIPTS/1_descarga`; los archivos se guardan en la carpeta donde se ejecuta y luego se ubican en `01_CRUDOS/<FUENTE>/`):

| Script | Uso |
|---|---|
| `descargar_procesos_atlantico.py` | `python descargar_procesos_atlantico.py` |
| `descargar_adiciones_mes.py` | `python descargar_adiciones_mes.py 2021` (un año, un archivo por mes) |
| `descargar_modificaciones_mes.py` | `python descargar_modificaciones_mes.py 2025 1` (un mes) |
| `descargar_modificaciones_dias.py` | `python descargar_modificaciones_dias.py 2026-08-28 2026-08-31` (por día) |

Contratos Electrónicos, Proveedores Registrados y las exportaciones anuales de Modificaciones (2021–2024 y periodos de 2026) se exportaron directamente desde el portal datos.gov.co. Cada descarga programática usa páginas de 5.000 registros, 200 s de espera y hasta 3 intentos por página, con puntos de control para reanudar. El archivo que aporta cada periodo está en `INVENTARIO_DATOS.md` y en la sección 8.1.1 del documento.

**2. Consolidación** (desde `SCRIPTS/2_consolidacion`, en este orden):

```
python 01_contratos.py
python 02_procesos.py
python 03_proveedores.py
python 04_adiciones.py
python 05_modificaciones.py
```

Resultado en `02_DEPURADOS/`: un archivo por fuente filtrado a los contratos del estudio, sin columnas con datos personales, y `resumen_consolidacion.csv` con los registros leídos y conservados en cada paso.

**3. Modelado** (desde `SCRIPTS/3_modelado`, en este orden):

```
python 01_tabla_modelado.py
python 01b_revision_calidad.py
python 02_caracterizacion.py
python 03_proxy_sensibilidad.py
python 04_modelos.py
python 04b_diagnostico_particiones.py
python 05_shap.py
python 06_priorizacion.py
```

Resultado en `03_MODELADO/`. El detalle de cada script, sus salidas y la sección del documento a la que corresponden está en `SCRIPTS/3_modelado/README.md`. `04_modelos.py` tarda unos 35 minutos y guarda puntos de control; los demás tardan menos de dos minutos. Para comprobar que todo corre antes de la ejecución completa: `set PRUEBA_RAPIDA=1` (Windows) antes de `04_modelos.py` y `05_shap.py`.

**4. Verificación (opcional)** (desde `SCRIPTS`): `python verificar_reproducibilidad.py` vuelve a ejecutar los pasos 2 y 3 en la carpeta `VERIFICACION_MODELOS/` y compara cada archivo de resultados con el original.

## Reproducibilidad y ética

- Versiones exactas de las librerías en `requirements.txt`; semilla aleatoria fija (42) en todos los procesos aleatorios.
- Se eliminan nombres, documentos de identidad, teléfonos, correos, cuentas bancarias y datos de representantes legales; los proveedores se identifican con el código interno de SECOP II.
- Ni el contratista ni la entidad son predictores de los modelos, y los modelos entrenados no se publican.
- Una alerta de riesgo contractual no implica irregularidad. Los resultados no deben usarse para señalar a contratistas o funcionarios específicos.
