# Anexo D. Complementos de las variables y de la metodología

Este anexo acompaña los capítulos 6 y 7 del trabajo de grado *Clasificación de Alertas de Riesgo Contractual en el Departamento del Atlántico mediante Aprendizaje Automático Supervisado e Inteligencia Artificial Explicable* (Carlos Arturo Tamayo Mojica, Maestría en Ciencia de Datos, Universidad EAN). No repite esos capítulos. Reúne el detalle que los complementa, organizado según la sección del documento a la que corresponde.

## D.1 Construcción de la variable dependiente (complemento de la sección 6.1)

Las tres reglas se calculan a partir de los conjuntos de datos de Contratos Electrónicos, Procesos de Contratación, Modificaciones y Adiciones de SECOP II.

- **Regla 1.** Se calcula como la suma de las adiciones en valor registradas para el contrato, dividida entre su valor inicial.
- **Regla 2.** Se calcula como la suma de los días de extensión registrados para el contrato, dividida entre su plazo inicial.
- **Regla 3.** Se calcula para cada par contratista–entidad y se asigna a todos los contratos de ese par.

El valor y el plazo pactados al momento de la firma se toman del conjunto de Procesos de Contratación, dado que el conjunto de Contratos Electrónicos registra el valor y el plazo vigentes, actualizados con las modificaciones posteriores. Cuando un mismo proceso dio origen a varios contratos, el valor inicial de cada uno se reconstruye a partir del historial de versiones registrado en el conjunto de Modificaciones (sección 7.3.3). Las adiciones y prórrogas se calculan a partir de los registros únicos de modificación en estado publicado o aprobado, una vez eliminados los registros duplicados, cancelados o rechazados, y se limitan a los registrados hasta la fecha de corte de observación, el 31 de agosto de 2026. El tratamiento de los contratos de régimen especial, de los contratos sin tiempo suficiente de observación y de las entidades con pocos contratos se define en los criterios de inclusión y exclusión de la sección 7.2.2.

## D.2 Descriptores de la variable independiente (complemento de la sección 6.2 y de la Tabla 2)

**Tabla D1**
*Descriptores de la variable independiente*

| Descriptor | Definición | Tipo | Campo de SECOP II | Transformación | Justificación |
|---|---|---|---|---|---|
| Modalidad de selección | Procedimiento de selección del contratista | Categórica: directa, régimen especial, competitiva | Modalidad de Contratacion | Agrupación en tres categorías y codificación one-hot | Menor competencia en la contratación directa |
| Causal de contratación directa | Justificación legal de la modalidad | Categórica: servicios profesionales y de apoyo, convenios interadministrativos, arrendamiento, sin pluralidad de oferentes, otras | Justificación Modalidad de Contratacion | Agrupación de categorías poco frecuentes y one-hot | Mayor riesgo en prestación de servicios con personas naturales y en convenios |
| Tipo de contrato | Naturaleza de la obligación pactada | Categórica: prestación de servicios, suministro, compraventa, obra, arrendamiento, otros | Tipo de Contrato | Agrupación y one-hot | Riesgo diferenciado por tipo |
| Categoría del bien o servicio | Clasificación de lo adquirido | Categórica | Código de Categoría Principal (UNSPSC) | Truncamiento al segmento (dos primeros dígitos) y one-hot | Riesgo diferenciado por sector de gasto |
| Valor inicial | Valor pactado al momento de la firma | Numérica (pesos) | Valor total de adjudicación (Procesos de Contratación) o, si el proceso figura como no adjudicado, precio base; historial de versiones (Modificaciones) en procesos con varios contratos | Logaritmo; escalamiento solo para la Regresión Logística | Mayor riesgo en valores altos e intermedios |
| Plazo inicial | Duración pactada al momento de la firma | Numérica (días) | Duración y unidad de duración (Procesos de Contratación) | Conversión de meses y años a días; escalamiento solo para la Regresión Logística | Mayor riesgo en plazos cortos |
| Sector y orden de la entidad | Sector administrativo y nivel de la entidad | Categórica | Sector; Orden | One-hot | Control de diferencias entre entidades |
| Antigüedad del proveedor | Días entre el registro del proveedor en SECOP II y la firma | Numérica (días) | Fecha de registro (SECOP II – Proveedores Registrados) | Diferencia en días; escalamiento solo para la Regresión Logística | Mayor riesgo en proveedores recientes |
| Tamaño del proveedor | Condición de pequeña o mediana empresa | Binaria | Es Pyme | 1 = Sí; 0 = No | Evidencia mixta; sin dirección esperada |
| Naturaleza jurídica | Persona natural o jurídica | Binaria | TipoDocProveedor | 1 = persona natural (cédula u otro documento personal); 0 = persona jurídica (NIT) | Mayor riesgo en personas naturales con prestación de servicios |
| Mes de suscripción | Mes de firma del contrato | Categórica (12 meses) | Fecha de Firma | One-hot | Mayor riesgo al cierre de la vigencia fiscal |
| Cercanía a la Ley de Garantías | Ubicación de la firma respecto de las restricciones electorales de 2022 y 2023 | Categórica: previo, durante, posterior, fuera | Fecha de Firma y calendario electoral | Ventanas definidas en la sección 7.3.3 | Mayor riesgo antes y después de la restricción |

Fuente: Elaboración propia

*Nota.* El orden de la entidad no varía en la población de estudio, por lo que no ingresa a los modelos (sección 8.1.2). Los doce descriptores que usan los modelos son los de esta tabla, con el sector como único atributo de la entidad.

## D.3 Tipo de estudio y fases (complemento de las secciones 7.1.1 y 7.1.2)

El componente de experimentación computacional corresponde a los elementos que se varían de forma controlada a lo largo del estudio, como los algoritmos de clasificación, sus hiperparámetros y los umbrales del proxy de riesgo. Son parámetros del análisis y no condiciones del fenómeno, por lo que no alteran el carácter no experimental del diseño.

Las seis fases del flujo de trabajo (Figura 2) se vinculan con los objetivos específicos así:

1. **Sistematización de los referentes teóricos y metodológicos** sobre detección de anomalías, supervisión débil, algoritmos de clasificación e inteligencia artificial explicable aplicados a la contratación pública (Objetivo Específico 1). Su resultado es el Marco Teórico (capítulo 4), que sustenta la formulación del proxy, la selección de los descriptores y la elección de los algoritmos.
2. **Estructuración del conjunto de datos**, es decir, el acceso a las fuentes de SECOP II, su consolidación y su depuración (secciones 7.2 y 7.3; Objetivo Específico 2).
3. **Construcción de la variable proxy** con las tres reglas de la sección 6.1 y su análisis de sensibilidad (sección 7.4.1).
4. **Modelamiento predictivo comparativo**, mediante el entrenamiento, la validación y la evaluación de los tres algoritmos (secciones 7.4.2 a 7.4.5). Las fases 3 y 4 responden al Objetivo Específico 3.
5. **Aplicación de los valores SHAP** para identificar los factores asociados a las alertas en el modelo seleccionado (sección 7.4.6).
6. **Construcción y evaluación del marco de priorización** a partir de los puntajes del modelo (sección 7.4.8). Las fases 5 y 6 responden al Objetivo Específico 4.

## D.4 Población y criterios (complemento de las secciones 7.2.1 y 7.2.2)

**Competencia de cada contraloría.**
- La Contraloría Departamental del Atlántico vigila al departamento, a sus entidades descentralizadas y a los municipios que no cuentan con contraloría propia.
- La Contraloría Distrital de Barranquilla vigila al Distrito y a sus entidades.
- La Contraloría Municipal de Soledad vigila a ese municipio y a sus entidades.
- El Área Metropolitana de Barranquilla se incluye por ser una entidad administrativa de carácter territorial.

**Entidades excluidas.** Las entidades del orden nacional con sede en el departamento y la corporación autónoma regional se excluyen porque su vigilancia corresponde a la Contraloría General de la República.

**Clasificación de las entidades.** Se realizó a partir del orden y del nombre de la entidad registrados en el SECOP II. Se corrigieron los casos registrados como territoriales que pertenecen al orden nacional, como la Policía Metropolitana de Barranquilla. Varios municipios del departamento registran pocos o ningún contrato en el SECOP II durante el periodo de estudio, por lo que su representación en la población depende de la cobertura de la plataforma.

**Exclusión por plazo no vencido.** Clasificar esos contratos como Y = 0 introduciría censura en la etiqueta.

**Exclusión por valor cero.** Los contratos con valor igual a cero son principalmente convenios interadministrativos sin cuantía y contratos de comodato. Los contratos cancelados se excluyen porque no llegaron a ejecutarse.

**Régimen especial.** Su modalidad se conserva como descriptor. Aunque no están sujetos al límite del 50 %, una adición de magnitud comparable sigue constituyendo una señal de riesgo en la gestión del contrato.

**COVID-19.** Los contratos se identifican mediante palabras clave en el objeto del contrato, como «COVID», «coronavirus», «pandemia» o «emergencia sanitaria».

**Mínimo de contratos por entidad.** En las entidades que no alcanzan el mínimo de 30 contratos, la alerta depende únicamente de las reglas de adición y prórroga. Los mínimos de 10 y 50 contratos se evalúan como escenarios de sensibilidad.

## D.5 Fuentes, acceso y entorno (complemento de las secciones 7.3.1 y 7.3.2)

**Uso de cada conjunto.**
- El conjunto de Contratos Electrónicos constituye la base de la unidad de análisis.
- Los conjuntos de Modificaciones y Adiciones registran la ejecución de cada contrato, y el segundo aporta además la tipología de cada modificación.
- El conjunto de Procesos de Contratación aporta el valor y el plazo pactados al momento de la firma, porque el de Contratos registra los valores vigentes.
- El conjunto de Proveedores Registrados aporta la fecha de registro de cada proveedor.

**Llaves de unión.**
- Contratos, Modificaciones y Adiciones: ID del contrato. En Adiciones, también el identificador de la modificación.
- Procesos: proceso de compra = ID del portafolio.
- Proveedores: código del proveedor.

**Ventana temporal.** Si las modificaciones no se observaran después del periodo de estudio, un contrato firmado a finales de 2024 aparecería sin modificaciones solo porque su ejecución no había avanzado. Para que todas las fuentes compartan la misma ventana de observación, con independencia del día en que se descargó cada una, se fijó como fecha de corte el 31 de agosto de 2026, último mes completo anterior al inicio de la extracción. Los procesos se descargaron desde 2019, porque la publicación de un proceso antecede a la firma del contrato. El registro de proveedores se descargó completo, al 5 de octubre de 2026, porque funciona como tabla de consulta.

**Acceso programático.**
- Se usó el punto de acceso query.csv de Socrata SODA, autenticado con credenciales de clave de API.
- Los conjuntos de Contratos y Procesos admiten un filtro por departamento. Los de Modificaciones, Adiciones y Proveedores no lo admiten y se descargaron a nivel nacional, para filtrarlos después por el identificador de los contratos del estudio.
- Cada consulta se hizo en páginas de 5.000 registros, con un tiempo máximo de espera de 200 segundos y hasta tres intentos por página. Puntos de control permiten reanudar una descarga interrumpida.
- Los conteos oficiales del portal se consultaron mediante agregaciones por periodo.
- Los esquemas de columnas de los dos métodos de acceso (etiquetas del portal frente a nombres de campo de la API) se unificaron durante la consolidación.

**Equipo.** ASUS TUF Gaming F15, con procesador Intel Core i7-13620H de 13.ª generación a 2,40 GHz, 32 GB de memoria RAM y Windows 11 Home de 64 bits (versión 26H2). Aunque el equipo cuenta con una tarjeta gráfica NVIDIA GeForce RTX 4060 de 8 GB, los modelos se entrenan solo con el procesador, para que los resultados puedan reproducirse en equipos sin aceleración gráfica.

**Tabla D2**
*Librerías utilizadas y su uso en el estudio*

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

## D.6 Preprocesamiento (complemento de la sección 7.3.3)

**Estados de las modificaciones.** Se descartan los estados distintos de publicado o aprobado, como en edición, en proceso de aprobación, cancelados o rechazados. Se conserva la última versión aprobada de cada modificación.

**Valor inicial.** Se toma del conjunto de Procesos (valor adjudicado o, en su defecto, precio base) cuando el proceso dio origen a un único contrato. Cuando dio origen a varios, o cuando el contrato no tiene un proceso asociado con un valor mayor que cero, se reconstruye a partir del historial de versiones de Modificaciones. Si ninguna modificación altera el valor, el valor inicial coincide con el vigente. Si alguna lo altera, corresponde al valor de la versión inmediatamente anterior a la primera modificación que lo cambia, identificada mediante la diferencia entre versiones consecutivas y la tipología registrada en Adiciones.

**Plazo inicial.** Se toma de la duración registrada en Procesos y se expresa en días. Cuando no está disponible o es igual a cero, se calcula restando los días de extensión a la duración vigente del contrato.

**Adiciones y prórrogas.** Corresponden a la suma de los incrementos de valor respecto del valor inicial y entre versiones consecutivas, y a la suma de los días de extensión.

**Descriptores.**
- La antigüedad del proveedor es cero cuando el registro es posterior a la firma.
- La cercanía a la Ley de Garantías se define respecto de dos periodos de restricción de la Ley 996 de 2005:
  - del 13 de noviembre de 2021 al 19 de junio de 2022, que agrupa la restricción previa a las elecciones de Congreso del 13 de marzo de 2022 (parágrafo del artículo 38) y la de las elecciones presidenciales del 29 de mayo y el 19 de junio de 2022 (artículos 33 y 38);
  - del 29 de junio al 29 de octubre de 2023, previa a las elecciones territoriales.

  Cada contrato se clasifica como firmado en las ocho semanas previas a una restricción, durante ella, en las ocho semanas posteriores o fuera de ellas.

**Regla de concentración.** Al igual que las reglas de adición y prórroga, emplea información posterior a la firma, lo cual es propio de la construcción de la etiqueta. Ninguno de los predictores incorpora esa información, de modo que se mantiene la separación temporal descrita en la sección 4.3.2.

**Tabla D3**
*Pasos de preparación de los datos para el modelamiento*

| Paso | Qué se hace | Cuándo se ajusta | Modelos a los que aplica |
|---|---|---|---|
| Transformación logarítmica | Logaritmo de uno más el valor inicial, para reducir la asimetría de su distribución | No se ajusta, es una transformación fija | Todos |
| Imputación de faltantes | Mediana en variables numéricas; categoría «Sin dato» en categóricas | Solo con entrenamiento | Todos |
| Agrupación de categorías poco frecuentes | Categorías con menos del 1 % de los contratos se agrupan en «Otras» | Solo con entrenamiento | Todos |
| Codificación one-hot | Una variable binaria por categoría; las categorías no vistas en entrenamiento se ignoran | Solo con entrenamiento | Todos |
| Estandarización | Media cero y desviación estándar uno en variables numéricas | Solo con entrenamiento | Solo Regresión Logística, porque los modelos de árboles no dependen de la escala |
| Tratamiento del desbalance | Pesos de clase según la proporción de alertas (sección 7.4.3) | Solo con entrenamiento | Todos |

Fuente: Elaboración propia

## D.7 Escenarios de sensibilidad (complemento de la sección 7.4.1)

Los umbrales alternativos se toman de tres distribuciones del conjunto de entrenamiento:

- **Regla de adiciones.** La razón entre el valor adicionado y el valor inicial, en los contratos que tuvieron alguna adición.
- **Regla de prórrogas.** La razón entre los días prorrogados y el plazo inicial, en los contratos prorrogados.
- **Regla de concentración.** La participación máxima de un contratista en el valor contratado por cada entidad con al menos 30 contratos.

En los escenarios E1 a E7 se modifica el umbral de una sola regla (en la regla de concentración, también el mínimo de contratos por entidad) y las otras dos se mantienen en su valor base, para atribuir a esa regla cualquier cambio en los resultados.

En cada escenario se evalúan tres aspectos:

- **Prevalencia.** La proporción de contratos con alerta en la población total y en los conjuntos de entrenamiento y prueba.
- **Contribución de cada regla.** Cuántos contratos activan cada regla y cuántos son alerta solo por esa regla.
- **Desempeño.** Se mide en la validación cruzada del entrenamiento y en la prueba.

Como el valor de referencia del AUC-PR cambia con la prevalencia (sección 4.3.5), los modelos se comparan dentro de cada escenario y no entre escenarios.

**Tabla D4**
*Escenarios del análisis de sensibilidad del proxy de riesgo contractual*

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

*Nota.* R1: adiciones en valor frente al valor inicial; R2: días de prórroga frente al plazo inicial; R3: participación del contratista en el valor contratado por la entidad.

## D.8 Implementación de los algoritmos y validación (complemento de las secciones 7.4.2 y 7.4.3)

Los tres algoritmos usan los mismos predictores, que son los descriptores de la Tabla D1, excepto los que no presentan variación en la población. XGBoost recibe las variables categóricas ya codificadas en el Pipeline y no usa su tratamiento nativo de categorías, para conservar la igualdad de condiciones.

**Tabla D5**
*Implementación y rol de los algoritmos de clasificación*

| Algoritmo | Implementación | Configuración fija | Rol en la comparación |
|---|---|---|---|
| Regresión Logística | scikit-learn 1.9.1, clase LogisticRegression | Regularización L2; variables numéricas estandarizadas; hasta 5.000 iteraciones del optimizador, con las que el modelo convergió en todas las particiones | Línea base frente a la cual se mide la ganancia de los ensambles (Hipótesis 1) |
| Random Forest | scikit-learn 1.9.1, clase RandomForestClassifier | Árboles entrenados en paralelo con todos los núcleos del procesador; semilla fija | Ensamble por bagging; se compara con la Regresión Logística y con XGBoost |
| XGBoost | XGBoost 3.4.1, clase XGBClassifier | Construcción de árboles por histogramas, ejecución solo en el procesador, función objetivo logística binaria; semilla fija | Ensamble por boosting; se compara con la Regresión Logística y con Random Forest |

Fuente: Elaboración propia

**Validación.**
- La partición temporal evita que el desempeño se sobrestime por información de un mismo periodo presente en entrenamiento y en prueba.
- La validación cruzada se repite tres veces con semillas distintas.
- Las quince particiones se usan para la búsqueda de hiperparámetros, la comparación de modelos y la estabilidad del orden de importancia de los descriptores.
- Los contratos que una entidad firma en un mismo mes suelen recibir sus adiciones y prórrogas en bloque (sección 8.3.1).
- En todos los escenarios se mantiene la misma partición temporal. En E8, E9 y E11 ambos conjuntos son menores, porque esos escenarios excluyen contratos.
- Las particiones se forman de nuevo en cada escenario, con el mismo procedimiento y la misma semilla, porque la estratificación depende de la etiqueta.

**Pesos de clase.**
- En la Regresión Logística y en Random Forest, los pesos son inversamente proporcionales a la frecuencia de cada clase.
- En XGBoost, el peso de la clase con alerta es el cociente entre el número de contratos sin alerta y con alerta.
- El sobremuestreo sintético se descartó porque genera contratos que no existen, y el submuestreo porque descarta información de la clase mayoritaria.

## D.9 Hiperparámetros, calibración y criterios (complemento de las secciones 7.4.4 y 7.4.5)

**Búsqueda aleatoria.** Bergstra y Bengio (2012) muestran que es más eficiente que la búsqueda en rejilla, porque en la mayoría de los problemas solo unos pocos hiperparámetros influyen de forma importante y los relevantes cambian de un conjunto de datos a otro. En sus experimentos con redes neuronales, 8 configuraciones aleatorias superaron a la rejilla en un espacio restringido, 32 lo hicieron de forma consistente en un espacio ampliado y, con 64 o más, la búsqueda aleatoria encontró resultados superiores. La búsqueda se implementa con RandomizedSearchCV. La Regresión Logística tiene un solo hiperparámetro por ajustar. No se emplea búsqueda bayesiana, para no agregar librerías. El AUC-PR se calcula como precisión promedio (average_precision) y se optimiza en lugar del F1 porque no depende de un umbral. La configuración seleccionada se reentrena con todo el conjunto de entrenamiento y se usa también en los escenarios de sensibilidad.

**Tabla D6**
*Espacio de búsqueda de hiperparámetros por algoritmo*

| Algoritmo | Hiperparámetro | Valores explorados | Qué controla |
|---|---|---|---|
| Regresión Logística | C | Entre 0,001 y 100, en escala logarítmica | Inverso de la fuerza de regularización |
| Random Forest | n_estimators | 200, 300 o 500 | Número de árboles |
| | max_depth | 10, 20, 30 o sin límite | Profundidad máxima de cada árbol |
| | min_samples_leaf | 1, 2, 5, 10 o 20 | Mínimo de contratos en cada hoja |
| | max_features | Raíz cuadrada, logaritmo en base 2 o 30 % de los predictores | Predictores considerados en cada división |
| XGBoost | n_estimators | Entre 200 y 1.000 | Número de árboles |
| | learning_rate | Entre 0,01 y 0,3, en escala logarítmica | Contribución de cada árbol nuevo |
| | max_depth | Entre 3 y 10 | Profundidad máxima de cada árbol |
| | min_child_weight | 1, 3, 5 o 10 | Peso mínimo requerido en cada hoja |
| | subsample | Entre 0,6 y 1,0 | Proporción de contratos usada en cada árbol |
| | colsample_bytree | Entre 0,5 y 1,0 | Proporción de predictores usada en cada árbol |
| | reg_lambda | Entre 0,1 y 10, en escala logarítmica | Regularización L2 de los pesos de las hojas |

Fuente: Elaboración propia

*Nota.* Los pesos de clase de cada algoritmo no forman parte de la búsqueda; se fijan según la sección 7.4.3.

**Calibración.** Las probabilidades no se calibran, por tres razones:
- el AUC-PR depende solo del orden en que el modelo clasifica los contratos, y la calibración no cambia ese orden;
- el umbral del F1 se define dentro del entrenamiento;
- el uso previsto del modelo es ordenar contratos.

Como los pesos de clase desplazan las probabilidades hacia la clase con alerta, la salida de los modelos se interpreta como un puntaje.

**Umbral de decisión.** En cada repetición de la validación cruzada, cada contrato recibe la predicción de un modelo que no lo usó para entrenarse, y se usan juntas las tres repeticiones. Como el umbral se elige con predicciones del mismo conjunto de entrenamiento, el F1 estimado por validación cruzada puede ser levemente optimista. La estimación sin ese sesgo es la del conjunto de prueba. Se reportan además la precisión y la prevalencia de cada escenario.

**Prueba t corregida.** Multiplica la varianza de las diferencias por el factor (1/15 + 1/4), donde 15 es el número de particiones y 1/4 la razón nominal entre el tamaño del conjunto de validación y el de entrenamiento en una validación de cinco particiones, y usa 14 grados de libertad.

**Bootstrap.** Los intervalos se obtienen de los percentiles 2,5 y 97,5 de cada métrica y de cada diferencia entre un ensamble y la Regresión Logística.

**Escenarios que cuentan para la Hipótesis 1.** E1 a E4 cambian los umbrales de adición y prórroga, E8 excluye el régimen especial y E10 cambia la forma de combinar las reglas. Si en el conjunto de prueba el intervalo de la diferencia queda por completo por debajo de cero para un ensamble que cumple la hipótesis, esa discrepancia se reporta en la sección 8.6. La ventaja de los ensambles en cada escenario se relaciona además con la prevalencia, para ver si cambia según el nivel de desbalance. Si la diferencia entre el mejor modelo y el segundo no es significativa, se conserva el de mayor promedio y se informa que la diferencia no es concluyente.

## D.10 Explicabilidad, reproducibilidad, ética y priorización (complemento de las secciones 7.4.6 a 7.4.8)

**Variante de SHAP.** Si el modelo seleccionado fuera la Regresión Logística, se usaría la variante de SHAP para modelos lineales. Los valores se expresan en la escala del puntaje del modelo, que en XGBoost y en la Regresión Logística es el logaritmo de la razón de momios. Un valor positivo aumenta el puntaje de alerta y uno negativo lo reduce.

**Análisis de explicabilidad.**
- **Dirección del efecto.** Para los descriptores numéricos (valor inicial, plazo inicial y antigüedad del proveedor) se examina cómo varía la contribución SHAP a lo largo de sus valores. Para los categóricos se calcula la contribución promedio de cada categoría.
- **Estabilidad.** En cada partición, el modelo se entrena con la parte de entrenamiento y los valores SHAP se calculan sobre la de validación. El W de Kendall va de 0 (ningún acuerdo) a 1 (orden idéntico). Se complementa con la proporción de particiones en que cada descriptor aparece entre los cinco más importantes.
- **Explicaciones locales.** Los quince contratos se seleccionan al azar con semilla fija y se identifican con un código interno.

**Descriptores con dirección esperada.** Según la sección 4.3.3, ocho descriptores tienen una dirección esperada: la modalidad de selección, la causal de contratación directa, el valor inicial, el plazo inicial, la antigüedad del proveedor, la naturaleza jurídica, el mes de suscripción y la cercanía a la Ley de Garantías. Para la dirección de los numéricos se usa el signo de la correlación de Spearman entre el valor del descriptor y su contribución SHAP. Para los categóricos se compara la contribución promedio de la categoría señalada con la de las demás. Un descriptor no es evaluable cuando la categoría señalada o el resto de categorías no tienen contratos en el conjunto de prueba.

**Reproducibilidad.**
- El repositorio contiene los scripts de descarga, consolidación y modelamiento, en el orden de ejecución, y las instrucciones.
- Como el portal actualiza sus registros, una nueva descarga puede diferir de la utilizada en este estudio, de modo que la reproducción exacta requiere los mismos archivos de origen.
- Las credenciales de acceso a la interfaz de datos abiertos no se publican.
- Usan semilla fija las particiones, la búsqueda de hiperparámetros, el entrenamiento de Random Forest y XGBoost, el bootstrap y la selección de los contratos de las explicaciones locales.
- La única variación posible proviene del cálculo en paralelo de Random Forest, en magnitudes inferiores a 0,00001, sin efecto sobre los resultados.

**Ética de los datos.**
- Se suprimen los nombres, los documentos de identidad, los teléfonos, los correos, las cuentas bancarias y los datos de los representantes legales.
- Los contratistas quedan identificados solo con el código interno de SECOP II.
- Las entidades públicas solo se nombran en los resultados descriptivos agregados.
- La clase sin alerta no equivale a un contrato cuya regularidad haya sido verificada.
- Los resultados no deben usarse para señalar a contratistas o funcionarios específicos ni para sustentar por sí solos una decisión de control.

**Priorización.** Los empates de puntaje se resuelven por el identificador del contrato. Como no se dispone de información sobre la capacidad de revisión de las contralorías del departamento, las capacidades del 5 %, el 10 % y el 20 % son ilustrativas. La precisión esperada de la selección al azar es igual a la prevalencia, y su exhaustividad esperada, igual a la capacidad. El cálculo por grupo de vigilancia corresponde al caso en que cada contraloría ordena solo los contratos de su jurisdicción. Una diferencia es significativa cuando su intervalo no incluye el cero.
