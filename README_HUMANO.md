# Qué estamos haciendo, explicado fácil

*(Este archivo es el resumen en criollo. El [`README.md`](README.md) es el técnico.)*

---

## El problema

Hay una fábrica de fideos, **Pastarazzi**, con cinco marcas:

| Marca | Qué es |
|---|---|
| Don Carlo | la barata de toda la vida, la que más vende |
| Agnellis | parecida a Don Carlo pero un poco más cara |
| Triguetti | la del medio, "la bandera" de la empresa |
| Candealix | también del medio, pero con trigo importado |
| Rena Speziale | la cara, para pocos clientes con plata |

La empresa tiene **$17.000 millones para gastar en publicidad este año** y la pregunta es una sola:

> **¿Cuánta plata le pongo a cada marca?**

Poner plata en publicidad trae clientes nuevos. Los clientes nuevos compran fideos. Eso es
más facturación. Y de esa facturación queda una ganancia. **Cada marca convierte publicidad
en plata a un ritmo distinto**, así que el reparto importa.

## La complicación

El directorio ya puso tres reglas que hay que cumplir sí o sí:

1. A Don Carlo y a Agnellis hay que darles **lo mismo** a las dos.
2. Triguetti se lleva **como mínimo el 30 %** de la plata.
3. Rena Speziale se lleva **como mínimo el doble** de lo que se lleven Candealix y Triguetti juntos.

Y encima hay una pelea interna: **los accionistas quieren ganancia** (les fue mal últimamente)
y **los gerentes quieren vender más** (sus premios dependen de las ventas, no de la ganancia).

---

## Qué hicimos

Armamos una **calculadora**. Le cargamos todos los datos del enunciado (precios, márgenes,
tamaño del mercado, cuántos clientes trae cada millón invertido) y las reglas del directorio.
La calculadora prueba todos los repartos posibles y devuelve el mejor.

## Qué dice la calculadora

| Marca | Cuánta plata le toca |
|---|---:|
| Don Carlo | $850 millones |
| Agnellis | $850 millones |
| Triguetti | $5.100 millones |
| **Candealix** | **$0 — no le toca nada** |
| Rena Speziale | $10.200 millones |

Con ese reparto la empresa pasa de vender el **48 %** de los fideos del país al **62 %**, y gana
**$76.578 millones**.

---

## Las tres cosas importantes que descubrimos

### 1. Se tiran $1.630 millones a la basura

Las reglas obligan a poner $10.200 millones en Rena Speziale. Pero Rena vende en el segmento
de los clientes con plata, **y ese grupo es chico**: son 1.200.000 personas en todo el país.
Con $8.570 millones ya se les vendió a **todas**.

Los $1.630 millones que sobran hay que gastarlos igual (lo manda la regla) pero **no traen ni
un cliente más**. Es casi el 10 % del presupuesto tirado.

### 2. La pelea del directorio no tiene sentido (por ahora)

Acordate de la pelea: accionistas quieren ganancia, gerentes quieren ventas. Probamos las dos
cosas por separado.

**Dan exactamente el mismo reparto.** Con las reglas que hay, no hay nada que discutir: el
directorio ya decidió todo con sus tres reglas y no queda margen para elegir. La pelea recién
existiría si aflojaran las reglas.

### 3. La regla de Triguetti es carísima

Obligar a poner el 30 % en Triguetti cuesta plata, pero no por Triguetti en sí. Es porque
**cada peso que va a Triguetti obliga a poner dos pesos más en Rena Speziale** (por la regla 3),
y esa plata ya vimos que no sirve para nada.

Si se sacara esa regla, la empresa ganaría unos **$3.500 millones más al año**.

---

## Un problema que encontramos y arreglamos

La primera vez que corrimos la calculadora dio un resultado imposible: decía que Rena Speziale
le vendía a **1.308.333 personas** en un grupo que tiene **1.200.000 personas**. O sea, le
vendía a más gente de la que existe.

El enunciado del TP pone un techo para las marcas baratas pero **se olvida de poner uno para
las caras**. Nosotros lo agregamos. Es un agregado nuestro, no del enunciado, **y hay que
aclararlo en el informe**.

---

## Qué falta hacer

| # | Tarea | Comentario |
|---|---|---|
| 1 | **Probar si nuestras suposiciones aguantan** | Hay datos que el enunciado no da y tuvimos que inventarlos con criterio. Hay que probar qué pasa si estuviéramos equivocados. **Esto va primero.** |
| 2 | Pregunta b) — ¿qué pasa si Agnellis crece? | Depende de la tarea 1 |
| 3 | Pregunta c) — ventas contra ganancia | Ya sabemos la respuesta corta (ver punto 2 de arriba), falta desarrollarla |
| 4 | Pregunta d) — ¿está mal la regla del 30 %? | Ya tenemos los números, falta escribirlo |
| 5 | Hacer los gráficos | No hay ninguno todavía |
| 6 | Dibujar el esquema del proceso | A mano, en draw.io o similar |
| 7 | Escribir el informe | Al final |

---

## Cómo ver los resultados vos mismo

**La forma fácil:** abrí los archivos de la carpeta `resultados/tablas/` con Excel. Son tablas
comunes.

**La forma completa:** abrí una terminal en la carpeta del proyecto y escribí:

```
pip install -r requirements.txt
python scripts/00_verificar_datos.py
python scripts/01_modelo_base.py
```

El primero revisa que los datos estén bien cargados. El segundo hace la cuenta e imprime todo.

---

## Dónde está cada cosa

| Carpeta o archivo | Qué hay adentro |
|---|---|
| `Consigna/` | el enunciado del TP |
| `Material/` | las clases del profesor |
| `resultados/tablas/` | **las tablas con los resultados** (abrilas con Excel) |
| `src/` | la calculadora |
| `scripts/` | los dos programas que se ejecutan |

Y tres documentos escritos:

| Archivo | Para qué |
|---|---|
| **este** | el resumen fácil |
| `README.md` | el técnico: cómo correr todo, qué hay hecho, las trampas |
| `plan_de_trabajo.md` | lo que planeamos hacer antes de empezar |
| `procedimiento.md` | lo que realmente pasó, con los resultados y los números |

**Si vas a tocar el código, leé `README.md` primero** — sobre todo la parte de "trampas
conocidas". Hay cosas del plan que quedaron viejas y están corregidas ahí.

---

## Un tema para hablar entre nosotros

En el repositorio hay dos estructuras de carpetas distintas:

- `codigo/`, `docs/`, `outputs/` — las creó Pedro (por ahora vacías)
- `src/`, `scripts/`, `resultados/` — las que tienen el trabajo hecho

**Hay que ponerse de acuerdo en cuál usamos** antes de seguir, o vamos a terminar con dos
proyectos mezclados en el mismo repositorio.
