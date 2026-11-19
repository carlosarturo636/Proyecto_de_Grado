# Anexo D. Metodología ampliada

Este anexo acompaña el capítulo 7 (Metodología) del trabajo de grado *Clasificación de Alertas de Riesgo Contractual en el Departamento del Atlántico mediante Aprendizaje Automático Supervisado e Inteligencia Artificial Explicable*. Presenta la versión completa de la metodología, con el detalle de cada decisión, que en el documento se resume para ajustarse a la extensión de la plantilla de monografía. Las secciones conservan la numeración del documento. Las tablas conservan la numeración que tenían en la versión completa; en el documento final, las tablas de librerías, implementación de los algoritmos y espacio de búsqueda solo aparecen en este anexo.

## 7.1 Enfoque y Alcance de la Investigación

### 7.1.1 Tipo y Alcance del Estudio

La presente investigación es un estudio cuantitativo, no experimental y retrospectivo, con un componente de experimentación computacional para la comparación de modelos. Es no experimental porque no se manipulan las condiciones del fenómeno estudiado, pues la contratación pública del Departamento del Atlántico se analiza tal como ocurrió y quedó registrada en el SECOP II. Es retrospectivo, con datos de 2021 a 2024, porque analiza los registros históricos de los contratos firmados en ese periodo, cuya ejecución se observa hasta una fecha de corte común para todas las fuentes, el 31 de agosto de 2026. El componente de experimentación computacional corresponde a los elementos que sí se varían de forma controlada a lo largo del estudio, como los algoritmos de clasificación, sus hiperparámetros y los umbrales del proxy de riesgo; se trata de parámetros del análisis y no de condiciones del fenómeno, por lo que no alteran el carácter no experimental del diseño.

El alcance de la investigación es descriptivo y predictivo. Es descriptivo en la medida en que caracteriza la contratación del periodo de estudio y la frecuencia con que se presentan las alertas de riesgo contractual definidas por el proxy (sección 6.1). Es predictivo en la medida en que entrena y compara modelos de clasificación supervisada, Regresión Logística, Random Forest y XGBoost, para anticipar dichas alertas con la información disponible al momento de la firma del contrato, y analiza mediante valores SHAP los factores asociados a ellas, sin que ello implique relaciones de causalidad, tal como se precisó en el planteamiento de las hipótesis.

### 7.1.2 Fases del Flujo de Trabajo Analítico

El desarrollo metodológico del estudio se organiza en seis fases secuenciales, cada una vinculada a uno de los objetivos específicos (Figura 2). La primera fase corresponde a la sistematización de los referentes teóricos y metodológicos sobre detección de anomalías, supervisión débil, algoritmos de clasificación e inteligencia artificial explicable aplicados a la contratación pública, y responde al Objetivo Específico 1. Su resultado es el Marco Teórico (capítulo 4), que sustenta la formulación del proxy de riesgo, la selección de los descriptores y la elección de los algoritmos. La segunda fase corresponde a la estructuración del conjunto de datos, es decir, al acceso a las fuentes de SECOP II, su consolidación y su depuración, descritas en las secciones 7.2 y 7.3, y responde al Objetivo Específico 2. La tercera fase corresponde a la construcción de la variable proxy de riesgo contractual a partir de las tres reglas definidas en la sección 6.1 y de su análisis de sensibilidad (sección 7.4.1). La cuarta fase corresponde al modelamiento predictivo comparativo, mediante el entrenamiento, la validación y la evaluación de los tres algoritmos de clasificación (secciones 7.4.2 a 7.4.5). Estas dos fases responden conjuntamente al Objetivo Específico 3. La quinta fase corresponde a la aplicación de la inteligencia artificial explicable mediante valores SHAP, para identificar los factores asociados a las alertas en el modelo seleccionado (sección 7.4.6), y la sexta, a la construcción y evaluación del marco de priorización a partir de los puntajes del modelo (sección 7.4.8). Estas dos fases responden conjuntamente al Objetivo Específico 4. Los resultados de las fases dos a seis se presentan, en el mismo orden, en las secciones 8.1 a 8.5 del capítulo de Trabajo de Campo, y los de las fases cuatro y cinco permiten contrastar las hipótesis H1 y H2 en la sección 8.6.

*Figura 2. Fases del flujo de trabajo analítico (ver el documento).*

Fuente: Elaboración propia

## 7.2 Población y Muestra

### 7.2.1 Delimitación de la Población

La población de estudio corresponde a los contratos registrados en el SECOP II por las entidades territoriales del Departamento del Atlántico y firmados entre el 1 de enero de 2021 y el 31 de diciembre de 2024. Se consideran entidades territoriales las sujetas a la vigilancia de las tres contralorías territoriales del departamento: la Contraloría Departamental del Atlántico, que vigila al departamento, a sus entidades descentralizadas y a los municipios que no cuentan con contraloría propia; la Contraloría Distrital de Barranquilla, que vigila al Distrito y a sus entidades; y la Contraloría Municipal de Soledad, que vigila a ese municipio y a sus entidades. Se incluye también el Área Metropolitana de Barranquilla, entidad administrativa de carácter territorial. Se excluyen las entidades del orden nacional con sede en el departamento y la corporación autónoma regional, cuya vigilancia corresponde a la Contraloría General de la República, así como las entidades de naturaleza privada que figuran en la plataforma. La clasificación de cada entidad se realizó a partir del orden y del nombre de la entidad registrados en el SECOP II, y se corrigieron los casos registrados como territoriales que pertenecen al orden nacional, como la Policía Metropolitana de Barranquilla. Cabe advertir que varios municipios del departamento registran pocos o ningún contrato en el SECOP II durante el periodo de estudio, por lo que su representación en la población depende de la cobertura de la plataforma.

### 7.2.2 Criterios de Inclusión y Exclusión

Se incluyen todos los contratos de la población, presenten o no modificaciones, adiciones o prórrogas, dado que los contratos que no activan ninguna regla del proxy conforman la clase sin alerta (Y = 0) y, por tanto, el grupo de comparación de los modelos. Sobre ese conjunto se aplican tres criterios de exclusión. Primero, se excluyen los contratos sin tiempo suficiente de observación, es decir, aquellos cuyo plazo inicial no había vencido en la fecha de corte del 31 de agosto de 2026; en estos contratos, la ausencia de adiciones o prórrogas no permite distinguir entre una gestión sin alertas y una ejecución todavía en curso, de modo que clasificarlos como Y = 0 introduciría censura en la etiqueta. Segundo, se excluyen los contratos registrados con valor igual a cero, principalmente convenios interadministrativos sin cuantía y contratos de comodato, porque no permiten calcular las reglas de adición y de concentración. Tercero, se excluyen los contratos cancelados, porque no llegaron a ejecutarse.

Adicionalmente, se definen tres tratamientos específicos. Los contratos de régimen especial se incluyen y su modalidad se conserva como descriptor. Aunque no están sujetos al límite del 50 % del parágrafo del artículo 40 de la Ley 80 de 1993, una adición de magnitud comparable sigue constituyendo una señal de riesgo en la gestión del contrato, y el efecto de incluirlos se evalúa en un escenario de sensibilidad que los excluye (sección 7.4.1). Los contratos relacionados con la atención de la emergencia sanitaria por COVID-19, que el artículo 8 del Decreto Legislativo 537 de 2020 permitió adicionar sin límite de valor, se identifican mediante palabras clave en el objeto del contrato, como “COVID”, “coronavirus”, “pandemia” o “emergencia sanitaria”, y se evalúa igualmente un escenario que los excluye. Por último, la regla de concentración se calcula solo para las entidades que suscribieron al menos 30 contratos en el periodo, porque en las entidades con muy pocos contratos cualquier contratista alcanza con facilidad el 30 % del valor contratado; en las entidades que no alcanzan ese mínimo, la alerta depende únicamente de las reglas de adición y prórroga, y los mínimos de 10 y 50 contratos se evalúan como escenarios de sensibilidad. Los contratos para los que no es posible determinar el valor o el plazo pactados al momento de la firma se tratan según el procedimiento descrito en la sección 7.3.3.

### 7.2.3 Unidad de Análisis y Censo Transaccional

La unidad de análisis es el contrato individual, identificado por su código único en el SECOP II (ID del contrato). No se realiza muestreo. El estudio trabaja con la población completa (censo) de contratos que cumplen los criterios de la sección 7.2.2. El número de contratos que conforman la población final y el efecto de cada criterio sobre ese número se reportan en la sección 8.1.

## 7.3 Instrumentos y Fuentes de Información

### 7.3.1 Fuentes de Información Secundaria

La información del estudio proviene de fuentes secundarias, en concreto de los registros administrativos que las entidades estatales publican en el SECOP II, la plataforma transaccional de la contratación pública colombiana administrada por la Agencia Nacional de Contratación Pública – Colombia Compra Eficiente (2024), y que se ofrecen como datos abiertos en el portal datos.gov.co. Se emplearon cinco conjuntos de datos, cuyo contenido, cobertura y uso se resumen en la Tabla 4. El conjunto de Contratos Electrónicos constituye la base de la unidad de análisis; los conjuntos de Modificaciones y Adiciones registran la ejecución de cada contrato y permiten calcular las reglas de adición y prórroga, y el segundo aporta además la tipología de cada modificación; el conjunto de Procesos de Contratación aporta el valor y el plazo pactados al momento de la firma, dado que el conjunto de Contratos registra los valores vigentes, actualizados con las modificaciones posteriores; y el conjunto de Proveedores Registrados aporta la fecha de registro de cada proveedor en la plataforma.

**Tabla 4. Conjuntos de datos de SECOP II utilizados**

| Conjunto de datos | Código en datos.gov.co | Cobertura descargada | Uso en el estudio | Llave de unión |
|---|---|---|---|---|
| Contratos Electrónicos | jbjy-vk9h | Contratos del Departamento del Atlántico firmados entre 2021 y 2024 | Unidad de análisis; descriptores de gestión contractual, de la entidad y temporales | ID del contrato |
| Procesos de Contratación | p6dx-8zbt | Procesos del Departamento del Atlántico publicados entre 2019 y 2024, y procesos sin fecha de publicación | Valor y plazo pactados al momento de la firma | Proceso de compra = ID del portafolio |
| Modificaciones a contratos | u8cx-r425 | Modificaciones aprobadas entre el 1 de enero de 2021 y el 31 de agosto de 2026 (nivel nacional) | Reglas de adición y prórroga; reconstrucción del valor inicial | ID del contrato |
| Adiciones | cb9c-h8sn | Registros entre el 1 de enero de 2021 y el 31 de agosto de 2026 (nivel nacional) | Tipología de cada modificación | ID del contrato; identificador de la modificación |
| Proveedores Registrados | qmzu-gj57 | Registro completo de proveedores de SECOP II al 5 de octubre de 2026 | Antigüedad del proveedor | Código del proveedor |

Fuente: Elaboración propia

La ventana temporal de cada conjunto responde a su función en el estudio. Los contratos se delimitan por su fecha de firma, entre 2021 y 2024. Las modificaciones y adiciones, en cambio, se descargaron hasta 2026, con el fin de observar los cambios registrados después del periodo de estudio sobre contratos firmados dentro de él; de no hacerlo, un contrato firmado a finales de 2024 aparecería sin modificaciones únicamente porque su ejecución no había avanzado, lo que constituye una forma de censura temporal en la variable dependiente. Para que todas las fuentes compartan la misma ventana de observación, con independencia del día en que se descargó cada una, se fijó como fecha de corte el 31 de agosto de 2026, último mes completo anterior al inicio de la extracción. Por su parte, los procesos se descargaron desde 2019, porque la publicación de un proceso antecede a la firma del contrato que de él se deriva, y el registro de proveedores se descargó completo, ya que funciona como tabla de consulta.

El acceso a los datos combinó dos métodos complementarios: la exportación directa desde el portal y el acceso programático mediante la interfaz de consulta de datos abiertos (Socrata SODA, punto de acceso query.csv), autenticado con credenciales de clave de API. Los conjuntos de Contratos y Procesos admiten un filtro por departamento, por lo que se descargaron directamente para el Atlántico; los de Modificaciones, Adiciones y Proveedores no lo admiten y se descargaron a nivel nacional, para filtrarlos posteriormente por el identificador de los contratos del estudio en la etapa de consolidación. Dado el volumen de estos conjuntos, del orden de millones de registros por año, y la inestabilidad del portal, la descarga se segmentó por periodos: por año, por mes y, en los casos en que el servicio fallaba de forma reiterada en un mismo punto, por día. Cada consulta programática se realizó en páginas de 5.000 registros, con un tiempo máximo de espera de 200 segundos y hasta tres intentos por página ante fallas del servicio, y con puntos de control que permiten reanudar una descarga interrumpida sin perder el avance. Cada archivo obtenido se verificó contra los conteos oficiales del portal, consultados mediante agregaciones por periodo, y los archivos incompletos o con campos alterados se descartaron y se descargaron de nuevo; el desarrollo de este proceso y sus resultados se presentan en la sección 8.1.1. Finalmente, dado que los dos métodos de acceso entregan los datos con esquemas de columnas distintos (etiquetas del portal frente a nombres de campo de la API), los esquemas se unificaron durante la consolidación.

### 7.3.2 Entorno Tecnológico y Librerías

El procesamiento de los datos y el modelamiento se ejecutan en un equipo portátil de uso personal (ASUS TUF Gaming F15), con procesador Intel Core i7-13620H de 13.ª generación a 2,40 GHz, 32 GB de memoria RAM y sistema operativo Windows 11 Home de 64 bits (versión 26H2). Aunque el equipo cuenta con una tarjeta gráfica NVIDIA GeForce RTX 4060 de 8 GB, los modelos se entrenan únicamente con el procesador, para que los resultados puedan reproducirse en equipos sin aceleración gráfica. Que todo el flujo de trabajo pueda ejecutarse en un equipo de estas características, sin infraestructura de cómputo en la nube ni software propietario, respalda el carácter de bajo costo computacional de la propuesta, condición relevante para contralorías con restricciones presupuestales.

El código se desarrolla en Python 3.14.6, con las librerías de código abierto que se presentan en la Tabla 5, junto con su versión exacta y el uso que se les da en el estudio. Fijar estas versiones es necesario para la reproducibilidad, porque los cambios entre versiones de una librería pueden alterar los resultados al ejecutar el mismo código en otro equipo. Las versiones se registran además en un archivo de requisitos del repositorio del proyecto (sección 7.4.7).

**Tabla 5. Librerías utilizadas y su uso en el estudio**

| Librería | Versión | Uso en el estudio |
|---|---|---|
| requests | 2.34.2 | Descarga programática de los conjuntos de datos desde la API de datos.gov.co |
| pandas | 3.0.5 | Lectura, consolidación, depuración y construcción de las variables a partir de las fuentes tabulares |
| NumPy | 2.5.1 | Operaciones numéricas y vectoriales sobre los datos |
| scikit-learn | 1.9.1 | Pipeline de preparación de datos, Regresión Logística, Random Forest, validación cruzada, búsqueda de hiperparámetros y métricas de evaluación |
| joblib | 1.6.0 | Almacenamiento de los modelos entrenados y de los puntos de control del modelamiento |
| XGBoost | 3.4.1 | Implementación del modelo de aumento de gradiente |
| SHAP | 0.53.0 | Cálculo de los valores SHAP mediante TreeExplainer y análisis de explicabilidad |
| SciPy | 1.18.1 | Pruebas estadísticas para la comparación de modelos |
| Matplotlib | 3.11.2 | Elaboración de gráficos y figuras de resultados |

Fuente: Elaboración propia

Los hiperparámetros de cada modelo, los rangos explorados y el método de búsqueda se presentan en la sección 7.4.4.

### 7.3.3 Protocolos de Calidad y Preprocesamiento

La preparación de los datos se organiza en dos etapas, que se diferencian por el momento en que se ejecutan y por si aprenden o no de los datos.

La primera etapa, de consolidación y depuración, se ejecuta una sola vez sobre el conjunto completo, porque sus operaciones son deterministas, es decir, no estiman ningún parámetro a partir de los datos y, por tanto, no generan fuga de información entre entrenamiento y prueba. En ella se filtran los cinco conjuntos a los contratos del Departamento del Atlántico firmados entre 2021 y 2024, se unifican los esquemas de columnas, se normalizan los formatos de fechas y valores, se eliminan los registros duplicados y se suprimen las columnas con datos personales (sección 7.4.7). Sobre ese conjunto se aplican después los criterios de población y de exclusión de la sección 7.2. En el conjunto de Modificaciones se conservan solo los registros en estado publicado o aprobado, se descartan los demás estados (en edición, en proceso de aprobación, cancelados o rechazados, entre otros), se conserva la última versión aprobada de cada modificación y se excluyen las aprobadas después de la fecha de corte. A partir de esos registros se construyen las variables del contrato.

- Valor inicial: se toma del conjunto de Procesos (valor adjudicado o, en su defecto, precio base) cuando el proceso dio origen a un único contrato. Cuando dio origen a varios, o cuando el contrato no tiene un proceso asociado con un valor mayor que cero, se reconstruye a partir del historial de versiones de Modificaciones: si ninguna modificación altera el valor, el valor inicial coincide con el vigente; si alguna lo altera, corresponde al valor de la versión inmediatamente anterior a la primera modificación que lo cambia, identificada mediante la diferencia entre versiones consecutivas y la tipología registrada en Adiciones. Los contratos para los que no es posible determinarlo se excluyen y se reportan en la sección 8.1.

- Plazo inicial: se toma de la duración registrada en Procesos y se expresa en días; cuando no está disponible o es igual a cero, se calcula restando los días de extensión a la duración vigente del contrato. Los contratos para los que no es posible determinarlo se excluyen y se reportan en la sección 8.1.

- Adiciones y prórrogas: la suma de los incrementos de valor respecto del valor inicial y entre versiones consecutivas, y la suma de los días de extensión, con las que se calculan las reglas 1 y 2 del proxy (sección 6.1).

- Descriptores: se construyen según la Tabla 3. La antigüedad del proveedor se calcula como los días entre su registro en el SECOP II y la firma del contrato, y es cero cuando el registro es posterior a la firma; la categoría del bien o servicio se trunca al segmento del código UNSPSC; y la cercanía a la Ley de Garantías se define respecto de los periodos de restricción de la Ley 996 de 2005 en el periodo de estudio: del 13 de noviembre de 2021 al 19 de junio de 2022, que agrupa la restricción previa a las elecciones de Congreso del 13 de marzo de 2022 (parágrafo del artículo 38) y la de las elecciones presidenciales del 29 de mayo y el 19 de junio de 2022 (artículos 33 y 38), y del 29 de junio al 29 de octubre de 2023, previa a las elecciones territoriales. Cada contrato se clasifica como firmado en las ocho semanas previas a una restricción, durante ella, en las ocho semanas posteriores o fuera de ellas.

La regla de concentración se calcula a partir del conjunto de contratos de cada entidad firmados entre 2021 y 2024, tal como se define en la sección 6.1. Al igual que las reglas de adición y prórroga, emplea información posterior a la firma de cada contrato, lo cual es propio de la construcción de la etiqueta. Sin embargo, como usa todo el periodo, la etiqueta de algunos contratos de entrenamiento incorpora información de contratos del conjunto de prueba. Para medir ese efecto, la regla se calcula también solo con los contratos de 2021 a 2023 en el conjunto de entrenamiento y se cuenta cuántas etiquetas cambian (sección 8.2.1). Ninguno de los predictores incorpora esa información, de modo que se mantiene la separación temporal entre la etiqueta y los predictores descrita en la sección 4.3.2.

La segunda etapa, de preparación para el modelamiento, agrupa los pasos que sí estiman parámetros a partir de los datos (Tabla 6). Todos ellos se ajustan exclusivamente con los datos de entrenamiento de cada partición y luego se aplican a los de validación y prueba, de modo que la información de evaluación no se filtre al entrenamiento ni sobrestime el desempeño reportado. En la práctica, esto se garantiza encapsulando los pasos en un Pipeline de scikit-learn, junto con el modelo, de manera que se ajusten de nuevo en cada partición de la validación cruzada.

**Tabla 6. Pasos de preparación de los datos para el modelamiento**

| Paso | Qué se hace | Cuándo se ajusta | Modelos a los que aplica |
|---|---|---|---|
| Transformación logarítmica | Logaritmo de uno más el valor inicial, para reducir la asimetría de su distribución | No se ajusta, es una transformación fija | Todos |
| Imputación de faltantes | Mediana en variables numéricas; categoría “Sin dato” en categóricas | Solo con entrenamiento | Todos |
| Agrupación de categorías poco frecuentes | Categorías con menos del 1 % de los contratos se agrupan en “Otras” | Solo con entrenamiento | Todos |
| Codificación one-hot | Una variable binaria por categoría; las categorías no vistas en entrenamiento se ignoran | Solo con entrenamiento | Todos |
| Estandarización | Media cero y desviación estándar uno en variables numéricas | Solo con entrenamiento | Solo Regresión Logística, porque los modelos de árboles no dependen de la escala |
| Tratamiento del desbalance | Pesos de clase según la proporción de alertas (sección 7.4.3) | Solo con entrenamiento | Todos |

Fuente: Elaboración propia

## 7.4 Técnicas para el Análisis de la Información y Modelamiento Predictivo

### 7.4.1 Operacionalización y Sensibilidad del Proxy de Riesgo

La variable objetivo se construye aplicando las tres reglas del proxy de riesgo contractual definidas en la sección 6.1 sobre el valor y el plazo iniciales de cada contrato y sobre su historial de modificaciones, obtenidos según el procedimiento de la sección 7.3.3. Un contrato recibe la etiqueta de alerta de riesgo contractual (Y = 1) cuando cumple al menos una de las tres reglas.

Como los umbrales de concentración y de prórroga no provienen de una norma, y el de adición se ubica por debajo del tope legal por decisión metodológica, se hace un análisis de sensibilidad para verificar que las conclusiones no dependen de haber elegido exactamente esos valores. Los umbrales alternativos se toman de percentiles de la distribución observada en los contratos de entrenamiento (2021–2023), para que el conjunto de prueba no intervenga en su definición. Se usan tres distribuciones:

- Para la regla de adiciones, la razón entre el valor adicionado y el valor inicial en los contratos que tuvieron alguna adición.

- Para la regla de prórrogas, la razón entre los días prorrogados y el plazo inicial en los contratos prorrogados.

- Para la regla de concentración, la participación máxima de un contratista en el valor contratado por cada entidad con al menos 30 contratos.

Se definen tres tipos de escenarios (Tabla 7):

- En los escenarios E1 a E7 se modifica el umbral de una sola regla, o en el caso de la regla de concentración también el mínimo de contratos por entidad, y las otras dos reglas se mantienen en su valor base, para atribuir a esa regla cualquier cambio en los resultados.

- En los escenarios E8, E9 y E11 se mantienen los umbrales base y se excluyen de la población, respectivamente, los contratos de régimen especial, los relacionados con la emergencia sanitaria por COVID-19, cuyo tratamiento se definió en la sección 7.2.2, y los contratos cuyo valor inicial se tomó de la primera versión registrada del contrato en SECOP II, en los que la regla de adiciones no puede activarse (sección 8.2.1).

- En el escenario E10 se reemplaza la disyunción de las reglas por la exigencia de cumplir al menos dos de ellas, para evaluar el efecto de la forma de combinarlas descrita en la sección 4.3.2.

**Tabla 7. Escenarios del análisis de sensibilidad del proxy de riesgo contractual**

| Escenario | Regla o aspecto que varía | Umbral o cambio | Justificación | Reglas en valor base |
|---|---|---|---|---|
| E0 Base | - | R1 ≥ 40 %; R2 ≥ 50 %; R3 ≥ 30 % en entidades con ≥ 30 contratos | Umbrales definidos en la sección 6.1 | R1, R2, R3 |
| E1 | Regla 1 | ≥ 25 % | Percentil 25 de la razón de adición | R2, R3 |
| E2 | Regla 1 | ≥ 50 % | Percentil 75 de la razón de adición, coincidente con el tope legal de adición (Ley 80 de 1993, art. 40, parágrafo) | R2, R3 |
| E3 | Regla 2 | ≥ 40 % | Valor cercano a la mediana de la razón de prórroga (43 %) | R1, R3 |
| E4 | Regla 2 | ≥ 70 % | Valor cercano al percentil 90 de la razón de prórroga (67 %) | R1, R3 |
| E5 | Regla 3 | ≥ 15 % | Valor cercano a la mediana de la participación máxima de un contratista por entidad (14,7 %) | R1, R2 |
| E6 | Regla 3 | Mínimo de 10 contratos por entidad | Escenario previsto en la sección 7.2.2 | R1, R2 |
| E7 | Regla 3 | Mínimo de 50 contratos por entidad | Escenario previsto en la sección 7.2.2 | R1, R2 |
| E8 | Población | Sin contratos de régimen especial | No están sujetos al tope del artículo 40 de la Ley 80 de 1993 (sección 7.2.2) | R1, R2, R3 |
| E9 | Población | Sin contratos relacionados con COVID-19 | El Decreto Legislativo 537 de 2020 permitió adicionarlos sin límite (sección 7.2.2) | R1, R2, R3 |
| E10 | Combinación | Alerta si cumple al menos dos reglas | Alternativa a la disyunción (sección 4.3.2) | R1, R2, R3 |
| E11 | Población | Sin contratos en los que la regla de adiciones no puede activarse | Su valor inicial se tomó de la primera versión registrada del contrato (sección 8.2.1) | R1, R2, R3 |

Fuente: Elaboración propia

Nota. R1: adiciones en valor frente al valor inicial; R2: días de prórroga frente al plazo inicial; R3: participación del contratista en el valor contratado por la entidad.

En cada escenario se evalúan tres aspectos:

- Prevalencia: la proporción de contratos con alerta en la población total y en los conjuntos de entrenamiento y prueba.

- Contribución de cada regla: cuántos contratos activan cada regla y cuántos son alerta solo por esa regla.

- Desempeño de los modelos: los tres algoritmos se reentrenan con las etiquetas de cada escenario, con los hiperparámetros seleccionados en el escenario base. Se evalúan en la validación cruzada del conjunto de entrenamiento, donde se aplica el criterio de comparación de la sección 7.4.5, y en el conjunto de prueba.

Como el valor de referencia del AUC-PR cambia con la prevalencia (sección 4.3.5), los modelos se comparan dentro de cada escenario y no entre escenarios. Este diseño permite contrastar la Hipótesis 1, que plantea la superioridad de los modelos de ensamble bajo los distintos umbrales del proxy.

Adicionalmente, en el escenario base los modelos se reentrenan sin el valor inicial y el plazo inicial como predictores. Como ambas variables son denominadores de las reglas de adición y prórroga (sección 4.3.2), la diferencia de desempeño entre el modelo con y sin ellas indica qué parte de la capacidad predictiva puede deberse a esa relación aritmética y no a un patrón de gestión.

### 7.4.2 Algoritmos de Clasificación Supervisada

Los tres algoritmos cuyo fundamento se presentó en la sección 4.3.4 se implementan con las librerías de la Tabla 5 y se comparan en igualdad de condiciones. Los tres usan los mismos predictores, que son los descriptores de la Tabla 3, con excepción de los que no presenten variación en la población de estudio, que no aportan información a ningún modelo. También comparten las mismas particiones de entrenamiento, validación y prueba (sección 7.4.3) y los mismos pasos de preparación de la Tabla 6. Cada algoritmo se encapsula junto con esos pasos en un Pipeline de scikit-learn, y todos los procesos aleatorios usan una semilla fija (sección 7.4.7). Así, las diferencias de desempeño entre modelos pueden atribuirse al algoritmo y no a la forma en que se prepararon los datos. Para conservar esa igualdad, XGBoost recibe las variables categóricas ya codificadas en el Pipeline y no usa su tratamiento nativo de categorías. La Tabla 8 resume la implementación de cada algoritmo y su función en la comparación.

**Tabla 8. Implementación y rol de los algoritmos de clasificación**

| Algoritmo | Implementación | Configuración fija | Rol en la comparación |
|---|---|---|---|
| Regresión Logística | scikit-learn 1.9.1, clase LogisticRegression | Regularización L2; variables numéricas estandarizadas; hasta 5.000 iteraciones del optimizador, con las que el modelo convergió en todas las particiones | Línea base frente a la cual se mide la ganancia de los ensambles (Hipótesis 1) |
| Random Forest | scikit-learn 1.9.1, clase RandomForestClassifier | Árboles entrenados en paralelo con todos los núcleos del procesador; semilla fija | Ensamble por bagging; se compara con la Regresión Logística y con XGBoost |
| XGBoost | XGBoost 3.4.1, clase XGBClassifier | Construcción de árboles por histogramas, ejecución solo en el procesador, función objetivo logística binaria; semilla fija | Ensamble por boosting; se compara con la Regresión Logística y con Random Forest |

Fuente: Elaboración propia

Los hiperparámetros que se ajustan para cada algoritmo se presentan en la sección 7.4.4; el tratamiento del desbalance de clases, en la sección 7.4.3; el criterio para comparar los modelos y elegir el de mejor desempeño, en la sección 7.4.5; y el análisis de ese modelo con valores SHAP, en la sección 7.4.6.

### 7.4.3 Validación y Tratamiento del Desbalance de Clases

La validación combina dos niveles: una partición temporal, que separa los datos con los que se construyen los modelos de los datos con los que se evalúan, y una validación cruzada estratificada y agrupada dentro del periodo de entrenamiento.

En la partición temporal, los contratos firmados entre 2021 y 2023 forman el conjunto de entrenamiento y los firmados en 2024, el conjunto de prueba. Este esquema reproduce el uso previsto del modelo, que es aprender de la contratación pasada para anticipar alertas en contratos nuevos. Además, evita que el desempeño se sobrestime por información de un mismo periodo presente en entrenamiento y en prueba. El conjunto de prueba se usa para evaluar los modelos ya ajustados con todo el conjunto de entrenamiento y no interviene en la selección de hiperparámetros, en el ajuste de los pasos de preparación ni en la elección del umbral de decisión. Sin embargo, se consultó en ejecuciones exploratorias previas a fijar la forma de la validación cruzada, como se explica en la sección 8.3.1, y esa consulta se reporta como limitación.

Dentro del conjunto de entrenamiento se aplica una validación cruzada estratificada y agrupada de cinco particiones, repetida tres veces con semillas distintas, lo que da quince pares de entrenamiento y validación, por las razones expuestas en la sección 4.3.5. Las particiones se forman agrupando los contratos por entidad por mes y año de firma, de modo que todos los contratos que una misma entidad firmó en un mismo mes de un mismo año quedan siempre en la misma partición. Esto se hace porque esos contratos suelen ser casi idénticos en sus características y recibir sus adiciones y prórrogas en bloque, de modo que repartirlos al azar entre entrenamiento y validación permitiría que el modelo reconociera contratos casi iguales a los que ya vio y sobrestimaría su desempeño (sección 8.3.1). Estas quince particiones se usan para tres propósitos: la búsqueda de hiperparámetros (sección 7.4.4), la comparación de modelos (sección 7.4.5) y la evaluación de la estabilidad del orden de importancia de los descriptores (sección 7.4.6).

El desbalance de clases se trata con pesos de clase y no con remuestreo. Los pesos hacen que cada contrato con alerta tenga, durante el entrenamiento, una influencia proporcional a la escasez de su clase, sin crear contratos artificiales ni eliminar contratos reales. El remuestreo, en cambio, modifica la distribución de los datos. El sobremuestreo sintético genera contratos que no existen, cuyas explicaciones SHAP no corresponderían a casos reales, y el submuestreo descarta información de la clase mayoritaria. En la Regresión Logística y en Random Forest, los pesos son inversamente proporcionales a la frecuencia de cada clase. En XGBoost, el peso de la clase con alerta es el cociente entre el número de contratos sin alerta y con alerta. En ambos casos, los pesos se calculan solo con los datos de entrenamiento de cada partición, dentro del Pipeline (Tabla 6), de modo que la proporción de clases del conjunto de validación o de prueba no interviene en el ajuste.

En todos los escenarios del análisis de sensibilidad (sección 7.4.1) se mantiene la misma partición temporal, en la que los contratos de 2021 a 2023 forman el conjunto de entrenamiento y los de 2024 el de prueba. En los escenarios E8, E9 y E11 ambos conjuntos son menores, porque esos escenarios excluyen contratos de la población. Las quince particiones de la validación cruzada se forman de nuevo en cada escenario, con el mismo procedimiento y la misma semilla, porque la estratificación depende de la etiqueta. Así, las diferencias entre escenarios se deben a la etiqueta y a la población de cada uno, y no a la forma de dividir los datos.

### 7.4.4 Optimización de Hiperparámetros

Los hiperparámetros son los valores que controlan la complejidad de cada algoritmo y que no se aprenden directamente de los datos. Las probabilidades que entregan los modelos no se calibran, por las razones que se explican al final de la sección.

Los hiperparámetros se seleccionan mediante búsqueda aleatoria, implementada con la clase RandomizedSearchCV de scikit-learn, que evalúa un número fijo de configuraciones tomadas al azar del espacio de búsqueda. Bergstra y Bengio (2012) muestran que este método es más eficiente que la búsqueda en rejilla, porque en la mayoría de los problemas solo unos pocos hiperparámetros influyen de forma importante en el desempeño, y la rejilla dedica gran parte de sus evaluaciones a combinaciones que solo difieren en hiperparámetros poco influyentes. Los autores encuentran además que los hiperparámetros relevantes cambian de un conjunto de datos a otro, de modo que no pueden identificarse de antemano para fijar una rejilla más estrecha. En sus experimentos con redes neuronales, 8 configuraciones aleatorias superaron a la búsqueda en rejilla en un espacio de búsqueda restringido, 32 lo hicieron de forma consistente en un espacio ampliado y, con 64 o más, la búsqueda aleatoria encontró resultados superiores. Con base en ello, se evalúan 40 configuraciones para Random Forest y para XGBoost, y 20 para la Regresión Logística, que tiene un solo hiperparámetro por ajustar. No se emplea búsqueda bayesiana, para no agregar librerías distintas a las de la Tabla 5.

Cada configuración se evalúa en las quince particiones de la validación cruzada estratificada y agrupada del conjunto de entrenamiento (sección 7.4.3), y se selecciona la de mayor promedio de AUC-PR en las particiones de validación. Esta métrica se calcula con la precisión promedio (average_precision). Se optimiza el AUC-PR y no el F1 porque no depende de un umbral de decisión, y porque, según la sección 4.3.5, es la métrica más informativa cuando la clase de interés es minoritaria. La búsqueda se realiza solo con el conjunto de entrenamiento, y el conjunto de prueba (2024) no interviene en ella. La configuración seleccionada se reentrena después con todo el conjunto de entrenamiento y se usa también en los escenarios del análisis de sensibilidad (sección 7.4.1). Como las mismas quince particiones se usan para elegir los hiperparámetros y para comparar los modelos (sección 7.4.5), el desempeño estimado de los modelos con más hiperparámetros ajustados puede ser algo optimista (Cawley & Talbot, 2010), sesgo que favorecería a los ensambles y que se tiene en cuenta al interpretar la comparación. La Tabla 9 presenta el espacio de búsqueda de cada algoritmo.

**Tabla 9. Espacio de búsqueda de hiperparámetros por algoritmo**

| Algoritmo | Hiperparámetro | Valores explorados | Qué controla |
|---|---|---|---|
| Regresión Logística | C | Entre 0,001 y 100, en escala logarítmica | Inverso de la fuerza de regularización |
| Random Forest | n_estimators | 200, 300 o 500 | Número de árboles |
|  | max_depth | 10, 20, 30 o sin límite | Profundidad máxima de cada árbol |
|  | min_samples_leaf | 1, 2, 5, 10 o 20 | Mínimo de contratos en cada hoja |
|  | max_features | Raíz cuadrada, logaritmo en base 2 o 30 % de los predictores | Predictores considerados en cada división |
| XGBoost | n_estimators | Entre 200 y 1.000 | Número de árboles |
|  | learning_rate | Entre 0,01 y 0,3, en escala logarítmica | Contribución de cada árbol nuevo |
|  | max_depth | Entre 3 y 10 | Profundidad máxima de cada árbol |
|  | min_child_weight | 1, 3, 5 o 10 | Peso mínimo requerido en cada hoja |
|  | subsample | Entre 0,6 y 1,0 | Proporción de contratos usada en cada árbol |
|  | colsample_bytree | Entre 0,5 y 1,0 | Proporción de predictores usada en cada árbol |
|  | reg_lambda | Entre 0,1 y 10, en escala logarítmica | Regularización L2 de los pesos de las hojas |

Fuente: Elaboración propia

Nota. Los pesos de clase de cada algoritmo no forman parte de la búsqueda; se fijan según la sección 7.4.3.

Las probabilidades que entregan los modelos no se calibran. Hay tres razones. Primero, el AUC-PR depende solo del orden en que el modelo clasifica los contratos, y la calibración no cambia ese orden. Segundo, el F1 depende del umbral de decisión, que se define dentro del entrenamiento según la sección 7.4.5. Tercero, el uso previsto del modelo es ordenar los contratos para priorizar la vigilancia, para lo cual basta el orden. Como los pesos de clase desplazan las probabilidades hacia la clase con alerta, la salida de los modelos se interpreta como un puntaje de alerta para ordenar contratos, y no como la probabilidad de que un contrato presente una irregularidad.

### 7.4.5 Métricas de Desempeño y Criterios de Selección

El desempeño de los modelos se mide con las métricas definidas en la sección 4.3.5: el F1 y el AUC-PR como métricas principales, calculando este último como precisión promedio, y la exhaustividad y el AUC-ROC como complementarias. Se reportan además la precisión y la prevalencia de alertas de cada escenario, que sirve de referencia para el AUC-PR.

El AUC-PR y el AUC-ROC no dependen de un umbral de decisión. El F1, la precisión y la exhaustividad sí dependen de él. Para cada modelo y escenario, el umbral se fija como el valor que maximiza el F1 sobre las predicciones fuera de partición del conjunto de entrenamiento. En cada repetición de la validación cruzada (sección 7.4.3), cada contrato recibe la predicción de un modelo que no lo usó para entrenarse, y se usan juntas las tres repeticiones. El umbral se fija una sola vez y se aplica sin cambios al conjunto de prueba. Como se elige con predicciones del mismo conjunto de entrenamiento, el F1 estimado por validación cruzada puede ser levemente optimista. La estimación sin ese sesgo es la del conjunto de prueba.

Para decidir si un modelo es mejor que otro se usa una prueba pareada sobre las quince particiones de la validación cruzada. En cada partición, los tres modelos se entrenan y se evalúan con los mismos contratos, de modo que se puede calcular la diferencia de cada métrica entre dos modelos en cada partición. Como las particiones comparten contratos, sus resultados no son independientes, y la prueba t pareada convencional subestima la varianza y declara diferencias con demasiada frecuencia. Por eso se aplica la prueba t con varianza corregida de Nadeau y Bengio (2003), en su versión para validación cruzada repetida (Bouckaert & Frank, 2004). Esta prueba multiplica la varianza de las diferencias por el factor (1/15 + 1/4), donde 15 es el número de particiones y 1/4 la razón nominal entre el tamaño del conjunto de validación y el de entrenamiento en una validación de cinco particiones, y usa 14 grados de libertad. Como la Hipótesis 1 plantea una dirección (los ensambles superan a la Regresión Logística), la prueba es unilateral, con un nivel de significancia de 0,05. Se implementa con SciPy (Tabla 5).

En el conjunto de prueba (2024) se calculan intervalos de confianza del 95 % mediante bootstrap pareado. Como los contratos que una misma entidad firma en un mismo mes no son independientes (sección 7.4.3), cada una de las 2.000 remuestras se forma extrayendo con reemplazo grupos completos de entidad, año y mes de firma, y en cada una se calculan las métricas de los tres modelos sobre los mismos contratos. Los intervalos se obtienen de los percentiles 2,5 y 97,5 de cada métrica y de cada diferencia entre un ensamble y la Regresión Logística. Estos intervalos muestran si la ventaja observada en la validación cruzada se mantiene en un periodo que los modelos no conocieron.

La regla para contrastar la Hipótesis 1 se fija antes de entrenar los modelos. En un escenario, se considera que un modelo de ensamble supera a la Regresión Logística cuando su ventaja es positiva y significativa en la prueba corregida tanto en AUC-PR como en F1. Para evaluar la hipótesis “bajo los distintos umbrales del proxy” se usan los escenarios que modifican la etiqueta de forma material: E1 a E4, que cambian los umbrales de adición y prórroga; E8, que excluye el régimen especial; y E10, que cambia la forma de combinar las reglas. Los escenarios E5 a E7 y E9 se reportan, pero no cuentan para la decisión, porque modifican la etiqueta de menos del 1 % de los contratos y equivalen en la práctica al escenario base (sección 8.2.2). El escenario E11 tampoco cuenta, porque no modifica los umbrales del proxy, sino que examina un error de medición de la etiqueta (sección 8.2.1). Un ensamble cumple el criterio cuando supera a la Regresión Logística en el escenario base y en al menos cuatro de esos seis escenarios. La decisión sobre la hipótesis, según cuántos ensambles cumplen este criterio, se presenta en la Tabla 1.

Si en el conjunto de prueba el intervalo de la diferencia queda por completo por debajo de cero para un ensamble que cumple la hipótesis, esa discrepancia se reporta en la sección 8.6. Además, para responder al interrogante planteado en el capítulo 5, la ventaja de los ensambles en cada escenario se relaciona con la prevalencia de alertas del escenario, para ver si cambia según el nivel de desbalance.

El modelo que se analiza con valores SHAP (sección 7.4.6) es el de mayor AUC-PR promedio en la validación cruzada del escenario base. Si la diferencia con el segundo no es significativa, se conserva el de mayor promedio y se informa que la diferencia no es concluyente. Con la misma prueba, en su versión bilateral porque no se plantea una dirección esperada, se comparan Random Forest y XGBoost, para evaluar si bagging o boosting resulta más adecuado (sección 4.3.4). También se compara el modelo del escenario base con su versión sin valor ni plazo iniciales, descrita en la sección 7.4.1, con la prueba bilateral.

### 7.4.6 Marco de Inteligencia Artificial Explicable (XAI)

El análisis de explicabilidad se aplica al modelo seleccionado según el criterio de la sección 7.4.5. Si ese modelo es Random Forest o XGBoost, los valores SHAP se calculan con el algoritmo TreeExplainer de la librería SHAP (Tabla 5), que obtiene valores exactos para modelos de árboles (Lundberg et al., 2020). Si es la Regresión Logística, se usa la variante de SHAP para modelos lineales. Los valores se calculan sobre los contratos del conjunto de prueba (2024), que el modelo no usó para entrenarse, y se expresan en la escala del puntaje del modelo; en XGBoost y en la Regresión Logística esa escala es el logaritmo de la razón de momios (log-odds). Un valor positivo aumenta el puntaje de alerta del contrato y uno negativo lo reduce.

Como las variables categóricas ingresan al modelo codificadas en una columna por categoría (Tabla 6), los valores SHAP de las columnas de un mismo descriptor se suman para obtener su contribución total. Esta suma es válida por la propiedad de aditividad de los valores SHAP (sección 4.4) y permite interpretar los resultados en el nivel de los descriptores de la Tabla 3 y no de cada categoría por separado.

Con estos valores se realizan cuatro análisis:

- Importancia global. Para cada descriptor se calcula el promedio del valor absoluto de su contribución SHAP en los contratos de prueba, y los descriptores se ordenan de mayor a menor importancia.

- Dirección del efecto. Para los descriptores numéricos (valor inicial, plazo inicial y antigüedad del proveedor) se examina cómo varía la contribución SHAP a lo largo de sus valores. Para los categóricos se calcula la contribución promedio de cada categoría. Así se establece si cada descriptor aumenta o reduce el puntaje de alerta, y en qué rangos.

- Estabilidad del orden de importancia. En cada una de las quince particiones de la validación cruzada (sección 7.4.3), el modelo se entrena con la parte de entrenamiento y se calculan los valores SHAP sobre la parte de validación, lo que da quince ordenamientos de los descriptores. Su concordancia se mide con el coeficiente W de Kendall, que va de 0 (ningún acuerdo) a 1 (orden idéntico en todas las particiones). Se complementa con la proporción de particiones en las que cada descriptor aparece entre los cinco más importantes.

- Explicaciones locales. Se seleccionan al azar, con semilla fija, quince contratos de prueba con alerta: cinco que solo cumplen la regla de adiciones, cinco que solo cumplen la de prórrogas y cinco que cumplen ambas. Para cada uno se presenta el desglose de su puntaje en las contribuciones de sus descriptores. Los contratos se identifican solo con un código interno, sin datos del contratista ni de la entidad (sección 7.4.7).

Los resultados de importancia y dirección se contrastan con el referente teórico de la sección 4.3.3. Según esa sección, ocho descriptores tienen una dirección esperada del efecto sobre la alerta: la modalidad de selección, la causal de contratación directa, el valor inicial, el plazo inicial, la antigüedad del proveedor, la naturaleza jurídica, el mes de suscripción y la cercanía a la Ley de Garantías. Para el tipo de contrato, la categoría del bien o servicio, el tamaño del proveedor y el sector de la entidad no se planteó una dirección única. El orden institucional no se incluye, porque no presenta variación en la población de estudio (sección 8.1.2).

La Hipótesis 2 se contrasta con dos criterios, fijados antes de calcular los valores SHAP:

- Consistencia con la literatura. Entre los cinco descriptores de mayor importancia global se identifican los que tienen una dirección esperada según la sección 4.3.3. Para los descriptores numéricos, la dirección observada es el signo de la correlación de Spearman entre el valor del descriptor y su contribución SHAP. Para los categóricos, se compara la contribución promedio de la categoría señalada en la sección 4.3.3 con la de las demás categorías. Un descriptor es evaluable cuando su dirección puede observarse en el conjunto de prueba; no lo es cuando la categoría señalada o el resto de categorías no tienen contratos en ese conjunto. El criterio se cumple si hay al menos dos descriptores evaluables y más de la mitad de ellos muestran la dirección esperada. Si hay menos de dos, la consistencia se declara no evaluable. Como el valor y el plazo iniciales pueden mostrar la dirección esperada por su relación aritmética con las reglas (sección 4.3.2), la consistencia se calcula también en el modelo que excluye esas dos variables (sección 7.4.1). Si no se sostiene allí, se reporta como limitación en la sección 8.6.

- Estabilidad. Se cumple si el coeficiente W de Kendall entre los quince ordenamientos es igual o mayor que 0,7.

La decisión sobre la hipótesis, según los criterios que se cumplan, se presenta en la Tabla 1.

La interpretación tiene en cuenta tres precauciones descritas en el marco teórico:

- Los valores SHAP explican las predicciones del modelo y no las causas del riesgo contractual (sección 4.4), por lo que los descriptores se presentan como factores asociados.

- El valor y el plazo iniciales están correlacionados entre sí, por lo que sus contribuciones se interpretan en conjunto y no por separado (Aas et al., 2021).

- Ambas variables son denominadores de las reglas de adición y prórroga (sección 4.3.2). Por eso su importancia se contrasta con el desempeño del modelo que las excluye (sección 7.4.1), para distinguir la parte aritmética de un patrón de gestión.

### 7.4.7 Protocolo de Reproducibilidad y Ética de Datos

Para que los resultados puedan verificarse y reproducirse, todo el código del estudio se publica en un repositorio público de GitHub (https://github.com/carlosarturo636/Proyecto_de_Grado). El repositorio contiene los scripts de descarga, consolidación y modelamiento, organizados por etapas y en el orden en que deben ejecutarse. También incluye el archivo de requisitos con las versiones exactas de las librerías de la Tabla 5, un inventario de los datos utilizados y las instrucciones de ejecución. Los datos no se incluyen, por su volumen (cerca de 26 GB) y porque algunos archivos originales contienen datos personales. Sin embargo, todos provienen de fuentes abiertas (sección 7.3.1) y pueden reconstruirse con las exportaciones del portal y las descargas programáticas descritas en la sección 8.1.1, seguidas de los scripts de consolidación. Como el portal actualiza sus registros, una nueva descarga puede diferir de la utilizada en este estudio, cuyo corte es el 31 de agosto de 2026; la reproducción exacta de los resultados requiere los mismos archivos de origen. Las credenciales de acceso a la interfaz de datos abiertos tampoco se publican: cada usuario debe usar las propias.

Todos los procesos aleatorios usan una semilla fija y declarada en el código: la conformación de las particiones de la validación cruzada, la búsqueda aleatoria de hiperparámetros, el entrenamiento de Random Forest y XGBoost, el bootstrap del conjunto de prueba y la selección de los contratos para las explicaciones locales. Con el mismo código, las mismas versiones de las librerías y los mismos datos de origen, se obtienen los mismos resultados; la única variación posible proviene del cálculo en paralelo de Random Forest, que puede alterar cifras intermedias en magnitudes inferiores a 0,00001, sin efecto sobre los resultados reportados.

En cuanto a la ética de los datos, aunque la información de SECOP II es pública (Ley 1712 de 2014), el 90,1 % de los contratos de la población corresponde a personas naturales (sección 8.1.2), cuyos datos personales están protegidos por la Ley 1581 de 2012. Por eso se adoptan cuatro medidas:

- Supresión de datos personales. Durante la consolidación (sección 7.3.3) se eliminan los nombres, los documentos de identidad, los teléfonos, los correos, las cuentas bancarias y los datos de los representantes legales. Los contratistas quedan identificados solo con el código interno que les asigna SECOP II.

- El contratista no es un predictor. Ni el código del contratista ni el de la entidad ingresan a los modelos, de modo que estos aprenden patrones de los contratos y no la identidad de quien los firma.

- Presentación agregada de los resultados. Los resultados se reportan en forma agregada. En las explicaciones locales (sección 7.4.6), cada contrato se identifica con un código interno, sin el nombre del contratista ni de la entidad. Las entidades públicas solo se nombran en los resultados descriptivos agregados.

- No se publican los modelos entrenados. Un modelo entrenado puede revelar si un registro particular formó parte de sus datos de entrenamiento (Salem et al., 2018), así que no se publica. Quien quiera reproducirlo puede entrenarlo con el código del repositorio.

Finalmente, una alerta de riesgo contractual no implica la existencia de una irregularidad. Como se definió en la sección 6.1, la alerta es una señal construida a partir de reglas observables que agrupa tanto posibles irregularidades como ineficiencias de gestión. Su propósito es ayudar a priorizar la selección de los contratos que serán objeto de vigilancia. Del mismo modo, la clase sin alerta no equivale a un contrato cuya regularidad haya sido verificada, y el puntaje que asigna el modelo no es la probabilidad de que un contrato sea irregular (sección 7.4.4). En consecuencia, los resultados de este estudio no deben usarse para señalar a contratistas o funcionarios específicos ni para sustentar por sí solos una decisión de control. Cualquier contrato priorizado debe seguir el proceso auditor ordinario de la contraloría competente, con las garantías del debido proceso.

### 7.4.8 Evaluación del Marco de Priorización

Una contraloría no puede revisar todos los contratos de su jurisdicción, sino una fracción limitada por su personal y su presupuesto. Por eso, además de las métricas de la sección 7.4.5, el modelo se evalúa como herramienta para ordenar los contratos según una capacidad de revisión fija. Para ello se usan los puntajes que el modelo seleccionado y la Regresión Logística asignan a los contratos del conjunto de prueba (2024). En cada caso, los contratos se ordenan de mayor a menor puntaje (los empates se resuelven por el identificador del contrato) y se supone que la contraloría revisa los primeros. Como no se dispone de información sobre la capacidad de revisión de las contralorías del departamento, se evalúan tres capacidades ilustrativas: el 5 %, el 10 % y el 20 % de los contratos.

Para cada capacidad se calculan dos medidas: la precisión, que es la proporción de los contratos revisados que tienen alerta según el proxy, y la exhaustividad, que es la proporción del total de alertas que queda dentro de los contratos revisados. Como referencia se usa una selección al azar, cuya precisión esperada es igual a la prevalencia de alertas y cuya exhaustividad esperada es igual a la capacidad de revisión. El cálculo se realiza para el conjunto de prueba completo y, por separado, dentro de cada grupo de vigilancia (sección 7.2), lo que corresponde al caso en que cada contraloría ordena solo los contratos de su jurisdicción. Los intervalos de confianza del 95 % de ambas medidas, y de su diferencia entre el modelo seleccionado y la Regresión Logística, se obtienen con el bootstrap pareado por grupos de la sección 7.4.5. Una diferencia se considera significativa cuando su intervalo no incluye el cero.

## Referencias del anexo

- Aas, K., Jullum, M., & Løland, A. (2021). Explaining individual predictions when features are dependent: More accurate approximations to Shapley values. Artificial Intelligence, 298, 103502. doi:10.1016/j.artint.2021.103502
- Agencia Nacional de Contratación Pública - Colombia Compra Eficiente. (2024). ¿Qué es el SECOP II? Obtenido de https://www.colombiacompra.gov.co/archivos/pregunta-frecuente/que-es-el-secop-ii
- Bergstra, J., & Bengio, Y. (2012). Random search for hyper-parameter optimization. Journal of Machine Learning Research, 13, 281-305. Obtenido de https://jmlr.org/papers/v13/bergstra12a.html
- Bouckaert, R. R., & Frank, E. (2004). Evaluating the replicability of significance tests for comparing learning algorithms. En H. Dai, R. Srikant, & C. Zhang (Ed.), Advances in Knowledge Discovery and Data Mining: 8th Pacific-Asia Conference, PAKDD 2004. 3056, págs. 3-12. Springer. doi:10.1007/978-3-540-24775-3_3
- Cawley, G., & Talbot, N. (2010). On over-fitting in model selection and subsequent selection bias in performance evaluation. Journal of Machine Learning Research, 11, 2079-2107. Obtenido de https://jmlr.org/papers/v11/cawley10a.html
- Congreso de la República de Colombia. (1993). Ley 80 de 1993. Por la cual se expide el Estatuto General de Contratación de la Administración Pública. Bogotá: Congreso de Colombia.
- Congreso de la República de Colombia. (2005). Ley 996 de 2005. Por medio de la cual se reglamenta la elección de Presidente de la República, de conformidad con el artículo 152 literal f) de la Constitución Política de Colombia, y de acuerdo con lo establecido en el Acto Legislativo 02 de 2004. Bogotá: Congreso de Colombia.
- Congreso de la República de Colombia. (2014). Ley 1712 de 2014. Ley de Transparencia y del Derecho de Acceso a la Información Pública Nacional. Diario Oficial No. 49.084. Bogotá: Congreso de Colombia.
- Lundberg, S. M., Erion, G., Chen, H., DeGrave, A., Prutkin, J. M., Nair, B., . . . Lee, S.-I. (2020). From local explanations to global understanding with explainable AI for trees. Nature Machine Intelligence, 2(1), 56–67. doi:10.1038/s42256-019-0138-9
- Nadeau, C., & Bengio, Y. (2003). Inference for the generalization error. Machine Learning, 52(3), 239-281. doi:10.1023/A:1024068626366
- Presidencia de la República de Colombia. (2020). Decreto Legislativo 537 de 2020. Por el cual se adoptan medidas en materia de contratación estatal, en el marco del Estado de Emergencia Económica, Social y Ecológica. Bogotá: Presidencia de la República de Colombia.
- Salem, A., Zhang, Y., Humbert, M., Berrang, P., Fritz, M., & Backes, M. (2018). ML-Leaks: Model and data independent membership inference attacks and defenses on machine learning models. arXiv. doi:10.48550/arXiv.1806.01246
