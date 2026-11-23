# Anexo F. Complementos de la discusión

Este anexo complementa el capítulo 9 del documento con los argumentos, cifras y antecedentes que se retiraron del cuerpo para ajustarlo a la extensión de la plantilla. No repite lo que ya se presenta allí. Las obras citadas aquí que no aparecen en la lista de Referencias del documento se listan al final.

## F.1 Desempeño comparativo de los modelos (complemento de la sección 9.1)

- La evidencia sobre la competitividad de los ensambles en datos tabulares incluye también a Shwartz-Ziv y Armon (2022).
- En 2024, el AUC-ROC fue de 0,721 en Random Forest, 0,757 en XGBoost y 0,741 en la Regresión Logística, y ninguna diferencia frente a esta última fue significativa en AUC-PR, F1 ni AUC-ROC.
- La concentración de los descriptores es alta. Por ejemplo, el 91,0 % de los contratos de entrenamiento pertenece a un mismo segmento UNSPSC. La relación casi monótona entre el valor inicial y el puntaje (Figura E7 del Anexo E) puede representarse con un modelo lineal sobre su logaritmo.
- La sobrestimación de la validación aleatoria es una forma de fuga de información, entendida como el uso, al construir el modelo, de información sobre la etiqueta que no estaría disponible al predecir casos nuevos (Kaufman et al., 2012). Al firmar un contrato nuevo no se conocen todavía las modificaciones de los contratos firmados con él. La validación aleatoria subestima el error de predicción cuando los datos tienen una estructura de dependencia (Roberts et al., 2017).
- Sobre la mejora de la Regresión Logística en 2024, dos características de la etiqueta afectan más a ese año, la subestimación de la regla de adiciones y el menor tiempo de observación (secciones 8.2.1 y 8.2.2). El escenario E11 descarta la primera como causa, porque sin los contratos afectados la Regresión Logística mejora igual, aunque muestra que esos contratos reducen la ventaja de los ensambles en prueba. La segunda no pudo comprobarse, y la pregunta de por qué la mejora favorece a la Regresión Logística queda abierta.
- Como la búsqueda de hiperparámetros y la comparación de modelos usan las mismas quince particiones, el desempeño estimado de los modelos más ajustados tiende a ser optimista (Cawley & Talbot, 2010). Ese sesgo favorece a los ensambles, que exploraron 40 configuraciones con un efecto apreciable sobre el AUC-PR, y no a la Regresión Logística, cuyo desempeño apenas varió. Aun con esa ventaja, los ensambles no cumplieron el criterio.
- Entre los dos ensambles, la validación cruzada no permite preferir uno, y solo en 2024 XGBoost supera a Random Forest en AUC-PR y en F1.
- Velarde et al. (2023) muestran que el desempeño de XGBoost se deteriora a medida que la clase positiva se hace más escasa, lo que también se observa aquí en términos absolutos (Tabla E19 del Anexo E), pero ese deterioro afectó todavía más a la Regresión Logística.

## F.2 Factores asociados a las alertas (complemento de la sección 9.2)

- Salazar et al. (2024) asocian los contratos de valor alto e intermedio con una mayor probabilidad de sobrecostos, y Gallego et al. (2021) encuentran que los contratos más costosos tienen un mayor riesgo de resultados problemáticos.
- La expectativa sobre el plazo inicial se basaba en el mecanismo de ofertar plazos inverosímilmente cortos para luego solicitar extensiones (Henao & Isaza, 2018, citado en Gallego et al., 2021).
- La asociación positiva del valor inicial puede reflejar la mayor complejidad de los contratos de obra y suministro, en los que la literatura documenta que la renegociación es frecuente (Bajari et al., 2014).
- La renegociación asociada con la adjudicación competitiva también la documentan Bajari et al. (2014). Medina-Hernández et al. (2026) encuentran que las banderas rojas mejoran la detección sobre todo en los procesos competitivos.
- Con la naturaleza jurídica ocurre algo similar. Los contratos con personas naturales, en su mayoría de prestación de servicios por contratación directa, presentan menos alertas que los celebrados con personas jurídicas (6,3 % frente a 17,4 %).
- Liebman y Mahoney (2017) documentan, en la contratación federal de Estados Unidos, un aumento del gasto en la última semana del año fiscal y una menor calidad de los proyectos de tecnología iniciados en ese momento. En el Atlántico son los contratos firmados entre enero y marzo los que aumentan el puntaje. Una posible explicación, que este estudio no comprobó, es que los contratos de prestación de servicios firmados al inicio de la vigencia se prorrogan o adicionan para cubrir el resto del año.
- El efecto de la Ley de Garantías no pudo evaluarse en 2024, aunque Gallego et al. (2021) encontraron que la distancia a la elección presidencial es uno de los predictores más importantes en sus modelos. La ventana de 2023 corresponde a elecciones territoriales, en las que la restricción solo recae sobre los convenios interadministrativos, por lo que agrupa periodos de distinta intensidad.
- La antigüedad del proveedor actúa en sentido contrario al hallazgo de Salazar et al. (2024), según el cual el riesgo de sobrecostos disminuye después de unos siete meses y medio de registro. Aquí el puntaje es menor en los proveedores con menos de un año de registro y alcanza su máximo alrededor de los dos años y medio. El resultado es más cercano a la relación no lineal descrita por Muñoz-Cancino y Ríos (2025), aunque debe leerse con cautela, porque la fecha de registro corresponde al registro vigente del proveedor.
- El W de Kendall de 0,945 respalda la estabilidad del orden de importancia. Los valores SHAP explican las predicciones del modelo sobre el proxy (Ali et al., 2023).

## F.3 Alcance de la regla de concentración (complemento de la sección 9.3)

- Fazekas et al. (2016) construyeron su indicador de participación del ganador con licitaciones públicas de Hungría.
- Los estudios que incorporan la estructura de red encuentran que esa información es de las más relevantes (Medina-Hernández et al., 2026; Muñoz-Cancino & Ríos, 2025).

## F.4 Implicaciones para el control fiscal territorial (complemento de la sección 9.4)

- Los coeficientes de la Regresión Logística se interpretan directamente (Hosmer et al., 2013), sin pérdida demostrada de desempeño frente a XGBoost en la priorización.
- Un reentrenamiento solo podría usar con seguridad contratos firmados casi dos años antes, lo que impone un rezago a la actualización del modelo (sección 8.2.2).
- El estudio contribuye a dos vacíos que señala la literatura, la escasez de aplicaciones en sistemas reales y la falta de conjuntos de datos disponibles públicamente (Schneider dos Santos et al., 2025), porque trabaja con datos abiertos y publica el código completo. Su evaluación es retrospectiva y no constituye una aplicación en un sistema en operación.

## F.5 Limitaciones (complemento de la sección 9.5)

- La construcción de etiquetas con reglas corresponde también a la programación de datos descrita por Ratner et al. (2016). Las adiciones y prórrogas pueden responder a adaptaciones legítimas del contrato (Bajari et al., 2014).
- La regla de concentración se calcula con todo el periodo, de modo que la etiqueta de algunos contratos de entrenamiento incorpora información de 2024, aunque al calcularla por periodo solo cambian 10 de las 60.001 etiquetas de entrenamiento (sección 8.2.1).
- La condición de pyme, el tipo de documento y la fecha de registro del proveedor provienen del registro vigente del portal y no necesariamente del que existía al firmar el contrato.
- Entre 2021 y 2023, el 52 % de los contratos se firmó alrededor de las restricciones de la Ley de Garantías. En la prueba, la cercanía a la Ley de Garantías funciona como un ajuste común a todos los contratos y no como un factor que los diferencie (sección 8.4.1).
- La búsqueda de hiperparámetros y la comparación de modelos comparten las mismas particiones (Cawley & Talbot, 2010). El conjunto de prueba no intervino en la selección de hiperparámetros ni en la del umbral.
- La regla de decisión de la Hipótesis 1 combina varias métricas y escenarios sin ajustar el nivel de significancia, aunque exige que la ventaja sea significativa en dos métricas y en la mayoría de los escenarios. En la evaluación de la priorización, la única diferencia significativa entre modelos aparece en una de 24 comparaciones.
- Los resultados dependen de la cobertura de SECOP II y no pueden generalizarse sin más a otros departamentos o periodos. Los métodos de detección de anomalías no supervisados no dependen de una etiqueta (Pang et al., 2021).

## Referencias de este anexo

Las demás obras citadas están en la lista de Referencias del documento.

Bajari, P., Houghton, S., & Tadelis, S. (2014). Bidding for incomplete contracts: An empirical analysis of adaptation costs. *American Economic Review, 104*(4), 1288–1319. https://doi.org/10.1257/aer.104.4.1288

Kaufman, S., Rosset, S., Perlich, C., & Stitelman, O. (2012). Leakage in data mining: Formulation, detection, and avoidance. *ACM Transactions on Knowledge Discovery from Data, 6*(4), 1–21. https://doi.org/10.1145/2382577.2382579

Pang, G., Shen, C., Cao, L., & Van Den Hengel, A. (2021). Deep learning for anomaly detection: A review. *ACM Computing Surveys, 54*(2), 1–38. https://doi.org/10.1145/3439950

Schneider dos Santos, E., Machado dos Santos, M., Castro, M., & Tyska Carvalho, J. (2025). Detection of fraud in public procurement using data-driven methods: A systematic mapping study. *EPJ Data Science, 14*(1), 52. https://doi.org/10.1140/epjds/s13688-025-00569-3

Velarde, G., Sudhir, A., Deshmane, S., Deshmunkh, A., Sharma, K., & Joshi, V. (2023). *Evaluating XGBoost for balanced and imbalanced data: Application to fraud detection* [Preprint]. arXiv. https://doi.org/10.48550/arXiv.2303.15218
