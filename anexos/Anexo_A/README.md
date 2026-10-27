# Anexo A. Explicaciones locales de los quince contratos de estudio

Este anexo acompaña la sección 8.4.3 del trabajo de grado *Clasificación de Alertas de Riesgo Contractual en el Departamento del Atlántico mediante Aprendizaje Automático Supervisado e Inteligencia Artificial Explicable*.

Presenta el desglose del puntaje de los quince contratos de prueba (2024) con alerta seleccionados al azar, con semilla fija. Cinco solo cumplen la regla de adiciones, cinco solo cumplen la de prórrogas y cinco cumplen ambas. En cada figura, las barras muestran la contribución SHAP de cada descriptor en el modelo XGBoost, en log-odds, y su suma con el valor base del modelo reproduce el puntaje del contrato. Los contratos se identifican solo con un código interno, sin datos del contratista ni de la entidad.

Las figuras se generan con el script `SCRIPTS/3_modelado/05_shap.py`.

## Figura A1. Desglose del puntaje del caso C01 (solo regla de adiciones)

![Figura A1](figuras/Figura_A1_caso_C01.png)

Fuente: Elaboración propia.

## Figura A2. Desglose del puntaje del caso C02 (solo regla de adiciones)

![Figura A2](figuras/Figura_A2_caso_C02.png)

Fuente: Elaboración propia.

## Figura A3. Desglose del puntaje del caso C03 (solo regla de adiciones)

![Figura A3](figuras/Figura_A3_caso_C03.png)

Fuente: Elaboración propia.

## Figura A4. Desglose del puntaje del caso C04 (solo regla de adiciones)

![Figura A4](figuras/Figura_A4_caso_C04.png)

Fuente: Elaboración propia.

## Figura A5. Desglose del puntaje del caso C05 (solo regla de adiciones)

![Figura A5](figuras/Figura_A5_caso_C05.png)

Fuente: Elaboración propia.

## Figura A6. Desglose del puntaje del caso C06 (solo regla de prórrogas)

![Figura A6](figuras/Figura_A6_caso_C06.png)

Fuente: Elaboración propia.

## Figura A7. Desglose del puntaje del caso C07 (solo regla de prórrogas)

![Figura A7](figuras/Figura_A7_caso_C07.png)

Fuente: Elaboración propia.

## Figura A8. Desglose del puntaje del caso C08 (solo regla de prórrogas)

![Figura A8](figuras/Figura_A8_caso_C08.png)

Fuente: Elaboración propia.

## Figura A9. Desglose del puntaje del caso C09 (solo regla de prórrogas)

![Figura A9](figuras/Figura_A9_caso_C09.png)

Fuente: Elaboración propia.

## Figura A10. Desglose del puntaje del caso C10 (solo regla de prórrogas)

![Figura A10](figuras/Figura_A10_caso_C10.png)

Fuente: Elaboración propia.

## Figura A11. Desglose del puntaje del caso C11 (reglas de adiciones y prórrogas)

![Figura A11](figuras/Figura_A11_caso_C11.png)

Fuente: Elaboración propia.

## Figura A12. Desglose del puntaje del caso C12 (reglas de adiciones y prórrogas)

![Figura A12](figuras/Figura_A12_caso_C12.png)

Fuente: Elaboración propia.

## Figura A13. Desglose del puntaje del caso C13 (reglas de adiciones y prórrogas)

![Figura A13](figuras/Figura_A13_caso_C13.png)

Fuente: Elaboración propia.

## Figura A14. Desglose del puntaje del caso C14 (reglas de adiciones y prórrogas)

![Figura A14](figuras/Figura_A14_caso_C14.png)

Fuente: Elaboración propia.

## Figura A15. Desglose del puntaje del caso C15 (reglas de adiciones y prórrogas)

![Figura A15](figuras/Figura_A15_caso_C15.png)

Fuente: Elaboración propia.
