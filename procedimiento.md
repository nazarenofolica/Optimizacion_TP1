# TP1 Pastarazzi — Procedimiento (bitácora de desarrollo)

> **Qué es este archivo.** El registro de lo que **efectivamente se hizo** al codificar y
> resolver el modelo, incluyendo **en qué se apartó del plan y por qué**. El plan está en
> [`plan_de_trabajo.md`](plan_de_trabajo.md) y **no se reescribe** para que coincida con esto.
>
> **Estado:** punto a) resuelto. Pendientes: tests de supuestos (§4) y preguntas b), c) y d) (§5).

---

## 1. Implementación

### 1.1. Entorno

Python 3.10.11. Se instaló `pulp 3.3.2` (solver **CBC**, el único disponible en el equipo);
`pandas 2.3.3`, `matplotlib 3.10.9` y `scipy 1.12.0` ya estaban. Ver `requirements.txt`.

### 1.2. Estructura

```
TP1_OPT/
├── plan_de_trabajo.md            esquema (lo que se planeó)
├── procedimiento.md              este archivo (lo que pasó)
├── requirements.txt
├── src/
│   ├── config.py                 datos del enunciado + supuestos S1..S9 + reglas
│   ├── datos.py                  tablas derivadas (mercado, base, coeficientes, cupos)
│   ├── modelo.py                 construcción y resolución del LP
│   └── reportes.py               tablas de salida
├── scripts/
│   ├── 00_verificar_datos.py     31 asserts contra los valores calculados a mano
│   └── 01_modelo_base.py         resuelve el punto a)
└── resultados/tablas/*.csv
```

### 1.3. Diseño del modelo parametrizado

Todo se resuelve con **una sola función**, tal como preveía el plan §13:

```python
modelo.resolver(params, objetivo="neta", epsilon=None, desactivar=())
```

- `params` viene de `config.construir_params(**overrides)`. Los overrides pisan cualquier
  supuesto o regla, y **fallan con `KeyError` si el nombre no existe** — decisión deliberada:
  un typo silencioso en un barrido de 40 corridas es un error caro de encontrar.
- `objetivo` elige entre los tres funcionales del plan §6.
- `desactivar` omite restricciones por nombre → es lo que van a usar las preguntas b) y d).
- `epsilon` agrega el piso de facturación del método ε-constraint → pregunta c).

Las restricciones se declaran **con nombre** (`R1_presupuesto`, `R3_triguetti_min`, …) para
poder leer `.pi` (precio sombra) y `.slack` (holgura) por nombre.

**Detalle de modelado:** los topes de tramo (R7, R8) se codificaron como **restricciones con
nombre y no como cotas superiores de la variable**. Como bounds el solver no devuelve precio
sombra sino costo reducido; como restricciones sí, y eso hace falta para el análisis
post-óptimo.

---

## 2. Desvíos respecto del plan de trabajo

### 2.1. ⚠ Se agregó una restricción que no estaba en el plan: **R10, saturación del mercado**

**Qué pasó.** La primera corrida del modelo tal como estaba planeado dio un resultado
imposible:

```
Segmento   Share inicial   Share final
Alto           14,00 %       123,03 %
```

Rena Speziale captaba **1.308.333 clientes nuevos en un segmento que tiene 1.200.000 personas
en total**. El modelo permitía captar más gente de la que existe.

**Por qué pasó.** El enunciado da un techo de participación **solo para la gama baja** (*"la
suma de ambas no supere aproximadamente el 65 % de participación en el mercado de menor poder
adquisitivo"*, → R5). Para los segmentos medio y alto no dice nada, y el plan tomó esa
ausencia al pie de la letra. Pero la ausencia de un techo *comercial* no elimina el techo
*físico*: ningún segmento puede superar el 100 % de su TAM.

**Qué se hizo.**

1. **Nueva restricción R10**, una por segmento:
   `clientes nuevos del segmento ≤ (tope − share ya ocupado) × TAM`
   con `tope = R10_tope_saturacion = 1.00` (100 % del TAM), parametrizado en `config.REGLAS`.
   Cupos resultantes: bajo 10.105.000 · medio 5.300.000 · alto 1.032.000 clientes.

2. **Tramo de "desperdicio"** para cada marca: un último tramo de tasa 0 y sin tope.
   Sin él el problema se volvía **infactible**: R4 exige `x_RS ≥ 10.200`, pero el segmento
   alto se llena con $8.570MM, así que no había forma de cumplir la regla del directorio.
   Con el tramo de desperdicio, esa plata se puede invertir pero no capta a nadie — que es
   exactamente lo que pasa en la realidad y, además, **el hallazgo más fuerte del punto a)**
   (§3.4).

**Impacto en el resultado.** Cambió el plan óptimo por completo:

| | Sin R10 (incorrecto) | Con R10 (correcto) |
|---|---:|---:|
| Don Carlo / Agnellis | $0 / $0 | **$850 / $850** |
| Candealix | $566,7 | **$0** |
| Rena Speziale | $11.333,3 | **$10.200** |
| Utilidad neta | $79.066,39 MM | **$76.578,60 MM** |
| Share del segmento alto | 123,03 % (imposible) | 100,00 % |

**Limitación que queda abierta.** Un 100 % del segmento alto sigue siendo comercialmente
absurdo: implica que Pastarazzi se queda con **todos** los clientes premium del país. El techo
realista es más bajo. Por eso `R10_tope_saturacion` quedó parametrizado: es un candidato
directo para el barrido de sensibilidad (§4), probando 60 %, 70 %, 80 %.

### 2.2. Cambio de estructura de datos en los tramos

El plan preveía los tramos como tuplas `(límite, tasa)`. Al agregar el tramo de desperdicio
las tuplas se volvieron ilegibles en los reportes, así que pasaron a diccionarios
`{"limite", "tasa", "etiqueta"}`. La etiqueta es la que aparece en la tabla de plan de
inversión ("1er tramo", "hasta saturar", "desperdicio").

### 2.3. Un valor esperado del plan estaba mal calculado

El plan §3.5 informa un market share inicial de "48,10 %" y en el script de verificación se
escribió como `48,1043`. El valor correcto es **48,1025 %** (797.107 / 1.657.100). Error de
redondeo al transcribir, no del modelo: lo detectó `00_verificar_datos.py` en su primera
corrida, que es exactamente para lo que existe ese script.

### 2.4. Tolerancia de los controles cruzados

CBC devuelve las variables con ~7 cifras significativas, así que sobre valores del orden de
$10.000MM arrastra errores de hasta 1e-4. El control manual estaba escrito con tolerancia
1e-6 y marcaba como violada una restricción que se cumplía (`11.333,3333` vs `11.333,33334`).
Se subió la tolerancia a **1e-3 $MM** (mil pesos), muy por debajo de cualquier magnitud
relevante del problema.

---

## 3. Resultados del punto a)

Corrida: `python scripts/01_modelo_base.py` · estado **Optimal** en las tres corridas.

### 3.1. Plan de asignación del presupuesto

| Marca | Tramo | Inversión ($MM) | % del presupuesto |
|---|---|---:|---:|
| Don Carlo | captación | 850,00 | 5,00 % |
| Agnellis | captación | 850,00 | 5,00 % |
| Triguetti | hasta saturar | 5.100,00 | 30,00 % |
| Candealix | — | **0,00** | 0,00 % |
| Rena Speziale | 1er tramo (150 cl/MM) | 3.500,00 | 20,59 % |
| Rena Speziale | 2do tramo (100 cl/MM) | 5.070,00 | 29,82 % |
| Rena Speziale | **desperdicio (0 cl/MM)** | **1.630,00** | **9,59 %** |
| **Total** | | **17.000,00** | 100 % |

### 3.2. Mix comercial resultante

| Marca | Inversión | Clientes nuevos | Fact. base | Fact. increm. | Fact. total | Crec. | Utilidad neta | % de la fact. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Don Carlo | 850 | 340.000 | 320.821 | 13.940 | 334.761 | +4,3 % | 16.738,05 | 32,6 % |
| Agnellis | 850 | 425.000 | 192.626 | 17.425 | 210.051 | +9,1 % | 15.753,82 | 20,5 % |
| Triguetti | 5.100 | 1.020.000 | 186.048 | 59.160 | 245.208 | +31,8 % | 22.068,72 | 23,9 % |
| Candealix | 0 | 0 | 78.600 | 0 | 78.600 | 0,0 % | 6.288,00 | 7,7 % |
| Rena Speziale | 10.200 | 1.032.000 | 19.012 | 138.288 | 157.300 | **+727,4 %** | 15.730,00 | 15,3 % |
| **TOTAL** | **17.000** | **2.817.000** | **797.107** | **228.813** | **1.025.920** | **+28,7 %** | **76.578,60** | 100 % |

*(cifras en $MM/año)*

- **Utilidad neta: $76.578,60 MM** = $55.421,52 de base + $21.157,08 que aporta la campaña.
- **Utilidad operativa: $112.489,49 MM**
- **Market share: 48,10 % → 61,91 %** del mercado de pastas.

### 3.3. Distribución por canales (segmentos)

| Segmento | Mercado | Fact. total | Share inicial | Share final | Clientes nuevos | Cupo usado |
|---|---:|---:|---:|---:|---:|---:|
| Bajo | 881.500 | 498.560 | 53,00 % | 56,56 % | 765.000 | 7,6 % |
| Medio | 614.800 | 366.560 | 50,00 % | 59,62 % | 1.020.000 | 19,3 % |
| Alto | 160.800 | 160.800 | 14,00 % | **100,00 %** | 1.032.000 | **100,0 %** |

El crecimiento se concentra en el segmento alto, que queda **saturado**. Los otros dos
apenas se tocan.

### 3.4. ⚠ Hallazgo principal: las reglas del directorio obligan a quemar $1.630MM

El segmento alto se llena con **$8.570MM** de inversión en Rena Speziale
($3.500 al 150 cl/MM + $5.070 al 100 cl/MM = 1.032.000 clientes, todo el cupo disponible).
Pero R4 exige `x_RS ≥ 2 × (x_CAN + x_TRI) ≥ 2 × 5.100 = 10.200`.

```
10.200 exigidos − 8.570 útiles = $1.630 MM  →  9,59 % del presupuesto
                                               que no capta a un solo cliente
```

No es un error del modelo: es la consecuencia aritmética de combinar la regla del 30 % de
Triguetti (R3) con la del doble de Rena (R4) sobre un segmento premium chico. **Es el
argumento central de la pregunta d)** y hay que llevarlo al informe.

### 3.5. Estado de las restricciones y precios sombra

| Restricción | Holgura | Activa | Precio sombra |
|---|---:|:---:|---:|
| R1 Presupuesto | 0 | **Sí** | **+1,17875** |
| R2 Paridad Don Carlo = Agnellis | 0 | **Sí** | **−0,35875** |
| R3 Triguetti ≥ 30 % | 0 | **Sí** | **−2,49225** |
| R4 Rena ≥ 2×(Can+Tri) | 0 | **Sí** | **−1,17875** |
| R5 Tope 65 % gama baja | 1.815.000 | No | 0 |
| R7 Saturación Triguetti ($6.000MM) | 900 | No | 0 |
| R8a 1er tramo Candealix | 5.000 | No | 0 |
| R8b 1er tramo Rena | 0 | Sí (degenerada) | 0 |
| R10 Saturación bajo | 9.340.000 | No | 0 |
| R10 Saturación medio | 4.280.000 | No | 0 |
| R10 Saturación alto | 0 | **Sí** | **+0,01340** |

**Lectura:**

- **R3 es la restricción más cara del modelo: −$2,49 de utilidad por cada millón** forzado a
  Triguetti. Y no es por Triguetti en sí (rinde 1,044): es por el arrastre de R4.
- **R1 = +1,179**: cada millón adicional de presupuesto daría $1,179MM de utilidad… pero
  ojo, iría al par Don Carlo/Agnellis, el único destino libre que queda.
- **R5 (el 65 % de la gama baja) no está activa**: sobran 1.815.000 clientes de cupo. El
  freno de la gama baja no es el mercado, es que las reglas del directorio no le dejan plata.
- **R2 = −0,359**: la paridad cuesta plata porque obliga a poner en Don Carlo (0,82) lo mismo
  que en Agnellis (1,54).

### 3.6. Comparación de los tres objetivos — resultado inesperado

| | Utilidad neta | Utilidad operativa | Facturación |
|---|---:|---:|---:|
| Don Carlo / Agnellis | 850 / 850 | 850 / 850 | 850 / 850 |
| Triguetti | 5.100 | 5.100 | 5.100 |
| Candealix | 0 | 0 | 0 |
| Rena Speziale | 10.200 | 10.200 | 10.200 |
| Utilidad neta ($MM) | 76.578,60 | 76.578,60 | 76.578,60 |
| Market share (%) | 61,91 | 61,91 | 61,91 |

**Los tres objetivos dan exactamente el mismo plan.** Costo de perseguir facturación en lugar
de utilidad: **$0**.

No es un bug — se verificó a mano. Con R3 y R4 activas, la única decisión libre son los
$1.700MM que sobran, y hay solo dos destinos posibles:

| Destino | Utilidad por $MM | Facturación por $MM |
|---|---:|---:|
| Par Don Carlo + Agnellis | **1,179** | **18,45** |
| Candealix (arrastra 2 $MM estériles a Rena) | 0,464 | 5,80 |

El par gama baja **domina a Candealix en los dos criterios a la vez**, así que no hay nada que
negociar.

**Implicancia para la pregunta c):** bajo las reglas actuales, la frontera de Pareto entre
rentabilidad y market share **colapsa en un solo punto**. La discusión entre accionistas y
directivos es, con estas reglas, una discusión sin objeto: no hay trade-off que resolver
porque el directorio ya fijó el plan. El trade-off recién aparece cuando se relajan R3 y R4 —
y eso es justamente lo que hay que mostrar en c).

---

## 4. Tests de supuestos

*Pendiente.* Ver `plan_de_trabajo.md` §11. Al listado de parámetros a barrer hay que agregarle
**`R10_tope_saturacion`** (probar 60 %, 70 %, 80 %, 100 %), que no existía cuando se escribió
el plan y es de los que más pueden mover el resultado: el segmento alto queda saturado, así
que bajar ese techo reduce directamente lo que Rena puede captar.

## 5. Preguntas b), c) y d)

*Pendiente.* El código ya está preparado:

| Pregunta | Cómo se corre |
|---|---|
| b) Agnellis vs. Don Carlo | `construir_params(S6_paridad_dc_ag=k)` barriendo k, o `desactivar=["R2_paridad"]` |
| c) Frontera de Pareto | `resolver(params, epsilon=…)` barriendo ε |
| d) El 30 % de Triguetti | `desactivar=["R3_triguetti_min"]`, o `construir_params(R3_pct_triguetti=…)` |

---

## 6. Verificaciones realizadas

### 6.1. Datos derivados — `00_verificar_datos.py`

**31 de 31 verificaciones OK.** Cubre: mercado por segmento y total, facturación base de las
cinco marcas y total, market share inicial, cupo de la gama baja, los 8 coeficientes de
facturación por $MM, los 8 coeficientes de utilidad neta, y los tres términos constantes.

### 6.2. Cotas deducidas a mano — `01_modelo_base.py` §1

7 de 7 OK: presupuesto agotado, R2/R3/R4 satisfechas, Triguetti+Rena ≥ 15.300,
resto ≤ 1.700, y `Z > término constante`.

### 6.3. Precios sombra contra cálculo manual

Los cinco duales no nulos se derivaron a mano y coinciden **a cinco decimales**:

| Dual | Modelo | Cálculo manual | Razonamiento |
|---|---:|---:|---|
| R1 | +1,17875 | +1,17875 | `0,5 × (0,82 + 1,5375)` — el peso extra va al par gama baja |
| R3 | −2,49225 | −2,49225 | `1,044 − 1,5 × (0,82 + 1,5375)` — gana Triguetti, pierde el par |
| R4 | −1,17875 | −1,17875 | `−0,5 × (0,82 + 1,5375)` — el $MM extra en Rena es estéril |
| R2 | −0,35875 | −0,35875 | `(0,82 − 1,5375) / 2` |
| R10 alto | +0,01340 | +0,01340 | `1,34 / 100` — un cliente más de cupo a 100 cl/$MM |

Es la verificación más fuerte que se hizo: que los duales se puedan reconstruir con
aritmética de servilleta confirma que el modelo dice lo que creemos que dice.

### 6.4. R6 — umbral de Candealix

**Confirmada la hipótesis del plan §7.3: la restricción NO está activa.** Candealix vende
**43.666.667 paquetes** con inversión cero (solo su facturación base), contra un umbral de
2.500.000 → **17,5 veces** el mínimo. No hace falta el tratamiento por escenarios del plan §8:
el LP puro alcanza.

---

## 7. Conclusiones para el informe

1. **El plan óptimo es**: Don Carlo $850MM, Agnellis $850MM, Triguetti $5.100MM,
   Candealix $0, Rena Speziale $10.200MM. Utilidad neta $76.578,60MM, market share 61,91 %.
2. **Candealix queda fuera del plan** pese a ser rentable por sí sola (1,392 de utilidad por
   $MM): la mata R4, porque cada peso que recibe obliga a poner dos en Rena, que ya está
   saturada. Su costo efectivo es 0,464 por $MM, menos de la mitad que el par gama baja.
3. **$1.630MM (9,59 % del presupuesto) se invierten sin captar un solo cliente**, forzados por
   la combinación de R3 y R4.
4. **Las reglas del directorio, no la optimización, determinan el plan.** Cuatro de las once
   restricciones están activas y entre ellas consumen $15.300 de los $17.000.
5. **No hay conflicto entre accionistas y directivos bajo las reglas actuales**: los tres
   objetivos dan el mismo plan. El conflicto es real solo si se relajan las reglas.
6. **El modelo, tal como lo especificaba el enunciado, permitía captar más clientes de los que
   existen.** Hubo que agregar R10. Vale la pena contarlo en el informe: encontrar un
   resultado imposible y rastrear su causa es parte del criterio "Analizar".
