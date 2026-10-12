# Análisis del problema de optimización de carteras

## 1. Planteamiento

El proyecto estudia cómo ajustar una cartera formada por acciones de Apple, Microsoft y Tesla cuando se tienen en cuenta sus dividendos, la composición de la cartera y distintos supuestos sobre el futuro. Se implementan cinco formulaciones para comparar decisiones bajo información fija, incertidumbre y decisiones que pueden adaptarse después de conocer parte de esa información.

Los modelos son una implementación computacional del caso académico. Sus resultados dependen de los datos y de las restricciones incluidos en el código; no constituyen una recomendación de inversión ni una predicción de precios.

## 2. Datos y supuestos

La cartera inicial y los datos financieros usados por los modelos son:

| Activo | Acciones iniciales | Precio actual por acción | Dividendo por acción | Precio futuro de referencia |
| --- | ---: | ---: | ---: | ---: |
| Apple (A) | 50 | 180 USD | 1,20 USD | 200 USD |
| Microsoft (M) | 80 | 330 USD | 2,50 USD | 350 USD |
| Tesla (T) | 30 | 250 USD | 0 USD | 280 USD |

El valor actual de la cartera es **42.900 USD**. Con los precios futuros de referencia, su valor sin realizar operaciones sería **46.400 USD**. El caso plantea como referencia un valor futuro mínimo un 5 % superior al valor actual: **45.045 USD**.

Estos importes son parámetros del problema, no cotizaciones actuales. Los modelos mantienen fijos los dividendos indicados, salvo cuando estudian expresamente incertidumbre en ellos.

## 3. Decisiones y restricciones principales

### Cambios en la cantidad de acciones

Las variables `x_A`, `x_M` y `x_T` representan el cambio en el número de acciones de cada empresa:

- Un valor positivo indica una compra.
- Un valor negativo indica una venta.
- Las cotas impiden vender más acciones de las que se poseen, por lo que la cartera no queda en posición corta.

En los modelos con decisiones posteriores aparecen además variables para los ajustes que se harían una vez observada la incertidumbre.

### Balance de las operaciones

La igualdad

```text
180 x_A + 330 x_M + 250 x_T = 0
```

expresa que el valor de las compras y las ventas, a precios actuales, se compensa. Así, el modelo no incorpora una aportación externa de dinero.

### Composición de la cartera

Las restricciones de composición requieren que cada activo represente al menos el 20 % del valor de la cartera, según las relaciones de valoración codificadas. Por tanto, expresan un mínimo de diversificación: no permiten que una empresa quede por debajo de ese umbral.

### Valor futuro mínimo

Algunas formulaciones exigen que la cartera alcance el umbral de valor futuro definido para el caso. En los modelos con escenarios, la valoración cambia según el precio futuro supuesto para Apple. Las cotas se incorporan a cada modelo en forma relativa a las acciones iniciales.

## 4. Modelos implementados

### 4.1. Modelo nominal

Supone conocidos los dividendos y los precios futuros de referencia. Elige cuántas acciones comprar o vender para maximizar los dividendos de la cartera, manteniendo las restricciones de balance, composición y valor futuro.

Es la formulación de referencia: no representa explícitamente la incertidumbre en los parámetros.

### 4.2. Incertidumbre en los dividendos

Este modelo introduce la variable `alpha`, que obliga a que el número final de acciones de cada empresa sea, como mínimo, `alpha`. El objetivo maximiza `3.4 * alpha`, de modo que busca elevar la cantidad mínima garantizada entre las tres posiciones.

La interpretación de este objetivo depende del supuesto de incertidumbre usado para los dividendos en el caso. No es el mismo criterio que maximizar directamente los dividendos nominales del primer modelo.

### 4.3. Incertidumbre en los porcentajes

Esta formulación mantiene el objetivo nominal de dividendos, pero trata como inciertos algunos porcentajes empleados en las restricciones de composición. El planteamiento contempla `r` entre 0,15 y 0,25, `s` entre 0,05 y 0,10, y la relación `4s + r <= 0,55`. El código incorpora las restricciones robustas mediante variables auxiliares no negativas (`y1` a `y8`).

La finalidad es que la cartera respete las condiciones del modelo para los valores admisibles de esos porcentajes, en vez de optimizar para un único valor conocido.

### 4.4. Reglas de decisión

Este modelo permite que las operaciones posteriores dependan del precio futuro de Apple, representado por `w_A` y considerado dentro del intervalo de 150 a 280 USD. Los precios de referencia de Microsoft y Tesla se mantienen en 350 y 280 USD. Para cada activo, el ajuste posterior se expresa mediante una regla afín de la forma `m * w_A + k`.

Las variables `m` y `k` definen cómo respondería la cartera a distintos precios. El modelo incorpora las restricciones asociadas a los extremos del intervalo y también la restricción no lineal `Res_21`, que Gurobi representa mediante una restricción no lineal general.

La idea central es decidir una política de ajuste antes de conocer el precio concreto, de modo que esa política pueda adaptarse después.

### 4.5. Modelo estocástico

Considera tres escenarios discretos para el precio futuro de Apple: **150, 200 y 280 USD**; Microsoft y Tesla mantienen precios de 350 y 280 USD. Las variables `x_A`, `x_M` y `x_T` representan las decisiones iniciales, mientras que las variables con sufijo `_d1`, `_d2` o `_d3` representan ajustes específicos para cada escenario.

La variable `b` está acotada por el resultado de cada escenario, y el objetivo la maximiza junto con los dividendos iniciales, aplicando además penalizaciones a la magnitud de los ajustes posteriores. Por ello, el criterio es de tipo **maximin**: favorece un resultado que se sostenga en el peor de los escenarios considerados. No calcula el valor esperado ni asigna probabilidades a los escenarios.

## 5. Cómo interpretar la salida

Al ejecutar el programa, se muestra para cada modelo el valor de su función objetivo y los valores de sus variables.

- En los modelos de una etapa, `x_A`, `x_M` y `x_T` son cambios en las posiciones. Por ejemplo, `x_A = 5` significa comprar cinco acciones de Apple; no significa que la posición final sea de cinco acciones. La posición final es la inicial más el cambio.
- En el modelo de reglas de decisión, `m` y `k` describen la respuesta posterior ante el precio incierto; no son cantidades de acciones por sí solas.
- En el modelo estocástico, las variables con sufijo de escenario son ajustes posteriores. `b` representa el límite común que el objetivo trata de maximizar entre escenarios.
- `alpha` en el modelo de dividendos representa la cota mínima común de acciones finales.

Los valores objetivos de los cinco modelos **no deben compararse como si midieran exactamente lo mismo**. Algunos representan dividendos nominales, mientras que otros optimizan una cota garantizada o combinan esa cota con penalizaciones. Para el análisis conviene revisar conjuntamente el criterio de cada modelo, las decisiones obtenidas y si se cumplen las restricciones.

## 6. Cota de valor futuro

El valor futuro de la cartera sin operaciones es 46.400 USD y el umbral del 5 % sobre el valor inicial es 45.045 USD. Por tanto, el cambio de valor futuro producido por las operaciones debe ser como mínimo **-1.355 USD**. Las restricciones `Res_5` del modelo nominal y `Res_8` del modelo de incertidumbre en dividendos imponen ese mismo umbral de valor futuro.

## 7. Alcance

Los resultados dependen de los precios, dividendos, intervalos, escenarios y restricciones definidos en el programa. El código no incorpora otros factores como costes de transacción, impuestos, cambios de dividendos o probabilidades estimadas de los escenarios. Si se cambian los supuestos, es necesario volver a resolver los modelos y revisar la interpretación de sus objetivos.
