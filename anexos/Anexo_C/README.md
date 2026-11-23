# Anexo C. Complementos del marco teórico

Este anexo acompaña el capítulo 4 del trabajo de grado *Clasificación de Alertas de Riesgo Contractual en el Departamento del Atlántico mediante Aprendizaje Automático Supervisado e Inteligencia Artificial Explicable* (Carlos Arturo Tamayo Mojica, Maestría en Ciencia de Datos, Universidad EAN). No repite el capítulo. Reúne los antecedentes, precisiones normativas y detalles técnicos que lo complementan, organizados según la sección del documento a la que corresponden.

Las obras citadas aquí que no aparecen en la lista de Referencias del documento se listan al final del anexo.

## C.1 Control fiscal y vigilancia preventiva (complemento de las secciones 4.1.1 y 4.1.3)

Rodríguez-Cubillos (2024) señala que la incorporación de tecnologías de la información y el análisis de grandes volúmenes de datos permitiría a los órganos de control realizar auditorías en tiempo real e identificar patrones de comportamiento sospechosos.

El Acto Legislativo 04 de 2019 reformó el artículo 267 de la Constitución Política. La reforma mantuvo el control fiscal posterior y selectivo como regla general y estableció que, además, podrá ser preventivo y concomitante, realizado en tiempo real mediante el seguimiento permanente de los recursos públicos y el uso de tecnologías de la información. Sin embargo, la misma norma le otorga a este último un carácter excepcional y no vinculante, que se ejerce en forma de advertencia al gestor fiscal, y asigna su ejercicio y coordinación exclusivamente al Contralor General de la República. En desarrollo de la reforma, el Decreto 2037 de 2019 creó en la Contraloría General la Dirección de Información, Análisis y Reacción Inmediata (DIARI), y el Decreto Ley 403 de 2020 dictó las normas para su implementación. Las contralorías territoriales ejercen el control posterior y selectivo en su jurisdicción según el artículo 272 de la Constitución Política.

## C.2 Señales de riesgo y umbrales del proxy (complemento de la sección 4.1.2)

La detección de anomalías en la gestión pública se fundamenta en la premisa de que los comportamientos ineficientes o irregulares dejan huellas identificables en las bases de datos del Estado, susceptibles de ser analizadas mediante algoritmos que proyecten la probabilidad de ocurrencia de eventos adversos. En Colombia, Transparencia por Colombia (2026) recomendó a los órganos de control utilizar análisis de grandes volúmenes de datos para encontrar patrones, banderas rojas y posibles alertas en la contratación pública, en particular alrededor del periodo de restricción que impone la Ley de Garantías.

Literatura adicional sobre las señales de ejecución:

- Bajari et al. (2014) muestran que la renegociación de los contratos públicos es frecuente y que los oferentes responden estratégicamente a la incompletitud contractual, incorporando en sus ofertas los costos de adaptación esperados.
- La normativa colombiana reconoce el riesgo de las ofertas artificialmente bajas. El artículo 2.2.1.1.2.2.4 del Decreto 1082 de 2015 obliga a la entidad estatal a requerir explicaciones al oferente cuando el valor de una oferta parece artificialmente bajo y a continuar con su evaluación solo si dicho valor no pone en riesgo el cumplimiento del contrato.
- Ferwerda et al. (2017) identifican los cambios sustanciales en el alcance o los costos del proyecto después de la adjudicación entre las banderas rojas asociadas significativamente con casos de corrupción.

Sobre el umbral de adiciones, el límite del artículo 40 de la Ley 80 de 1993 admite excepciones, entre ellas la del artículo 8 del Decreto Legislativo 537 de 2020, que permitió adicionar sin límite de valor los contratos relacionados con la atención de la pandemia durante la emergencia sanitaria. Esta situación se considera en los criterios de inclusión y exclusión (sección 7.2.2) y en el escenario E9 del análisis de sensibilidad.

La literatura internacional identifica además patrones de colusión, como la rotación sistemática de ganadores entre un grupo reducido de oferentes (García Rodríguez et al., 2022), que exceden el alcance de este trabajo porque requieren analizar las ofertas presentadas por cada participante en múltiples procesos.

## C.3 Antecedentes de investigación (complemento de las secciones 4.2.1 y 4.2.2)

**México.** El estudio de Medina-Hernández et al. (2026) trabaja con contratos financiados con recursos federales y adjudicados por gobiernos federal, estatales y municipales, y trata como no etiquetados a todos los contratos de proveedores no sancionados. Encuentra que las banderas rojas tradicionales mejoran el desempeño principalmente en los contratos adjudicados mediante procesos competitivos. Los autores advierten que la ausencia de ejemplos negativos confirmados limita el aprendizaje supervisado convencional. En esta investigación ocurre algo análogo, pues la clase sin alerta corresponde a contratos que no activan ninguna regla del proxy y no a contratos cuya regularidad haya sido verificada.

**Mapeo de la literatura.** El mapeo sistemático de Schneider dos Santos et al. (2025), que analizó 93 estudios sobre detección de fraude en contratación pública, encontró que persisten dos vacíos, la escasez de aplicaciones en sistemas reales para detectar nuevos casos y la falta de conjuntos de datos disponibles públicamente.

**Colombia.** Gallego et al. (2021) documentan que en Colombia un mecanismo frecuente para extraer recursos consiste en ofertar por debajo del costo o con plazos de ejecución inverosímilmente cortos para obtener el contrato y luego solicitar extensiones (Henao & Isaza, 2018, citado en Gallego et al., 2021). El estudio de Zuleta et al. (2019) cubrió entidades de nivel nacional y subnacional.

**Nivel subnacional fuera de la región.** Del Sarto et al. (2024) señalan que muchas de las estrategias actuales contra la corrupción en el sector salud no evalúan los riesgos que ocurren a nivel subnacional, y perfilan a 207 autoridades contratantes del sector salud italiano, a partir de 14 banderas rojas, en ocho grupos de riesgo cuya distribución territorial varía de forma notable entre regiones. Esto sugiere que el nivel territorial en el que se construye un modelo de riesgo contractual puede revelar patrones de riesgo que no se observan a escala nacional.

## C.4 Fundamento de la variable proxy (complemento de la sección 4.3.2)

La viabilidad de calcular indicadores de riesgo a escala de contrato a partir de datos administrativos ha sido documentada por Fazekas et al. (2024), quienes consolidaron más de 72 millones de contratos de 42 países e incorporaron indicadores de riesgo de corrupción para cada uno de ellos.

Zhou (2018) distingue tres tipos de supervisión débil, la incompleta, cuando solo una fracción de los datos tiene etiqueta, la inexacta, cuando las etiquetas tienen una granularidad más gruesa que la tarea, y la imprecisa, cuando las etiquetas no siempre corresponden a la verdad. El proxy de este trabajo pertenece a la última.

El índice de Fazekas y Kocsis (2020) se construyó con banderas rojas como la ausencia de publicación de la convocatoria, el uso de procedimientos no abiertos y la duración de los plazos de publicación y de decisión, y se aplicó a millones de contratos de 28 países europeos. Fazekas et al. (2016) distinguen entre los resultados probables de la corrupción, como la adjudicación con un único oferente o la alta participación del ganador en los contratos de la entidad, y las características del proceso que permiten producirlos.

Además del valor y el plazo iniciales, el valor de cada contrato suma a la participación del contratista en la regla de concentración, de modo que también interviene en el cálculo de esa regla.

## C.5 Fundamento de los predictores (complemento de la sección 4.3.3)

- **Gestión contractual.** Gallego et al. (2021) identifican entre las modalidades de mayor riesgo, además de la prestación de servicios con personas naturales, los convenios entre entidades públicas, y señalan como sectores de mayor riesgo los servicios de transporte y los servicios relacionados con el sector público. El orden institucional de la entidad se planteó para capturar diferencias de riesgo entre tipos de entidad.
- **Perfil del proveedor.** En Bogotá, el riesgo de sobrecostos asociado a un menor tiempo de registro del proveedor disminuye a partir de aproximadamente siete meses y medio de registro (Salazar et al., 2024). En Chile, tanto las empresas muy nuevas como las más antiguas resultan más propensas a ser señaladas como atípicas, y tanto las de ventas bajas como las de ventas muy altas (Muñoz-Cancino & Ríos, 2025), por lo que para el tamaño del proveedor no se planteó una dirección única.
- **Temporalidad.** La Ley 996 de 2005 prohíbe la contratación directa durante los cuatro meses anteriores a la elección presidencial (artículo 33) y restringe la celebración de convenios interadministrativos por parte de las autoridades territoriales en los cuatro meses anteriores a las elecciones (parágrafo del artículo 38). Transparencia por Colombia (2026) recomienda a los órganos de control vigilar la contratación celebrada en las semanas previas, durante y posteriores a la restricción.

## C.6 Algoritmos, métricas y explicabilidad (complemento de las secciones 4.3.4, 4.3.5 y 4.4)

**Regresión Logística.** Sus coeficientes, expresados como razones de momios, permiten cuantificar de forma inmediata cuánto incrementa o reduce cada variable la probabilidad de alerta (Hosmer et al., 2013).

**Random Forest.** Además de reducir la varianza, permite estimar la importancia de las variables y provee una estimación interna del error de generalización a partir de las observaciones excluidas de cada submuestra, conocida como error out-of-bag, sin requerir un conjunto de validación separado (Breiman, 2001).

**XGBoost.** Optimiza una aproximación de segundo orden de la función de pérdida, su término de regularización penaliza el número de hojas de cada árbol y la magnitud de sus pesos, y su algoritmo de búsqueda de particiones maneja de forma nativa los valores faltantes y los datos dispersos, conocido como sparsity-aware split finding (Chen & Guestrin, 2016). Evidencia empírica reciente muestra que su desempeño de detección se deteriora a medida que el desbalance de clases se acentúa (Velarde et al., 2023), lo que refuerza el uso de métricas diseñadas para ese escenario.

**Datos tabulares.** Shwartz-Ziv y Armon (2022) confirmaron de forma independiente a Grinsztajn et al. (2022) que XGBoost supera a las arquitecturas de aprendizaje profundo propuestas para datos tabulares en una amplia variedad de conjuntos.

**Validación cruzada.** Divide el conjunto de datos en múltiples particiones de entrenamiento y validación para obtener una estimación más robusta del desempeño y reducir el riesgo de que los resultados dependan de una única partición. La combinación de métricas y de validación permite comparar los tres modelos de forma consistente con el Objetivo Específico 3.

**Opacidad algorítmica.** La implementación de modelos de aprendizaje automático en el sector público enfrenta el dilema de la «caja negra». Para que una alerta pueda utilizarse en la priorización de la vigilancia, el auditor debe poder conocer las razones técnicas que la originan. La propiedad de consistencia de SHAP garantiza que, si una variable aumenta su contribución marginal en un modelo alternativo, su valor SHAP no puede disminuir (Lundberg & Lee, 2017). A nivel global, la importancia SHAP orienta las prioridades de vigilancia de la entidad fiscalizadora.

## Referencias de este anexo

Las demás obras citadas están en la lista de Referencias del documento.

- Asamblea Nacional Constituyente. (1991). *Constitución Política de Colombia*.
- Bajari, P., Houghton, S., & Tadelis, S. (2014). Bidding for incomplete contracts: An empirical analysis of adaptation costs. *American Economic Review, 104*(4), 1288–1319. https://doi.org/10.1257/aer.104.4.1288
- Del Sarto, S., Gnaldi, M., & Salvini, N. (2024). Sustainability and high-level corruption in healthcare procurement: Profiles of Italian contracting authorities. *Socio-Economic Planning Sciences, 95*, 101988. https://doi.org/10.1016/j.seps.2024.101988
- Fazekas, M., Tóth, B., Abdou, A., & Al-Shaibani, A. (2024). Global contract-level public procurement dataset. *Data in Brief, 54*, 110412. https://doi.org/10.1016/j.dib.2024.110412
- Ferwerda, J., Deleanu, I., & Unger, B. (2017). Corruption in public procurement: Finding the right indicators. *European Journal on Criminal Policy and Research, 23*(2), 245–267. https://doi.org/10.1007/s10610-016-9312-3
- García Rodríguez, M. J., Rodríguez-Montequín, V., Ballesteros-Pérez, P., Love, P. E., & Signor, R. (2022). Collusion detection in public procurement auctions with machine learning algorithms. *Automation in Construction, 133*, 104047. https://doi.org/10.1016/j.autcon.2021.104047
- Presidencia de la República de Colombia. (2015). *Decreto 1082 de 2015. Por medio del cual se expide el decreto único reglamentario del sector Administrativo de Planeación Nacional*.
- Rodríguez-Cubillos, G. A. (2024). Impacto del control fiscal en Colombia. *Revista Colombiana de Contabilidad, 12*(24), 77–98. https://doi.org/10.56241/asf.v12n24.313
- Schneider dos Santos, E., Machado dos Santos, M., Castro, M., & Tyska Carvalho, J. (2025). Detection of fraud in public procurement using data-driven methods: A systematic mapping study. *EPJ Data Science, 14*(1), 52. https://doi.org/10.1140/epjds/s13688-025-00569-3
- Transparencia por Colombia. (2026). *Análisis de la contratación del Gobierno Nacional posterior a la Ley de Garantías*.
- Velarde, G., Sudhir, A., Deshmane, S., Deshmunkh, A., Sharma, K., & Joshi, V. (2023). Evaluating XGBoost for balanced and imbalanced data: Application to fraud detection. *arXiv*. https://doi.org/10.48550/arXiv.2303.15218
