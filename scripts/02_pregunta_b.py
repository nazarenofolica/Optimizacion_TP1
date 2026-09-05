"""
Punto b) — Escenarios en que Agnellis aumente su participación.

La restricción R2 del modelo base lee la paridad Don Carlo/Agnellis como igualdad
estricta (supuesto S6, plan_de_trabajo.md §4.2): x_DonCarlo = x_Agnellis. Esta
pregunta es, literalmente, el test de ese supuesto: en lugar de la igualdad se
parametriza x_DonCarlo = k * x_Agnellis y se barre k desde 1.0 (paridad total, el
caso base del punto a) hasta 0.0 (toda la plata libre del par gama baja va a
Agnellis), reutilizando el mismo modelo de src/modelo.py sin copiarlo.

Responde las dos cosas que pide el enunciado:
  - cuánta inversión necesita Don Carlo para no perder presencia significativa
  - qué efecto tiene esto en la utilidad total

    python scripts/02_pregunta_b.py

Salidas: por consola, un gráfico en resultados/graficos/ y una tabla en
resultados/tablas/07_pregunta_b_escenarios_agnellis.csv
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
if hasattr(sys.stdout, "reconfigure"):  # consola de Windows en cp1252
    sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd  # noqa: E402

from src import datos, graficos, modelo, reportes  # noqa: E402
from src.config import construir_params  # noqa: E402

SALIDA = RAIZ / "resultados" / "tablas"

pd.set_option("display.width", 200)
pd.set_option("display.float_format", lambda v: f"{v:,.2f}")

#: k = x_DonCarlo / x_Agnellis. k=1.00 es el caso base (R2 tal como está en el
#: punto a)). Valores menores simulan que Agnellis crece más rápido que Don Carlo;
#: k=0.00 es el extremo en que Don Carlo no recibe nada del presupuesto libre.
VALORES_K = [1.00, 0.90, 0.75, 0.60, 0.50, 0.40, 0.30, 0.20, 0.10, 0.00]


def titulo(texto, caracter="="):
    print(f"\n{caracter * 78}\n{texto}\n{caracter * 78}")


def fila_de(k, res):
    params = res["params"]
    _base, _incremental, total = reportes.facturacion(res)
    clientes = reportes.clientes_captados(res)
    mercado_total = datos.mercado_total(params)
    cl_dc, cl_ag = clientes["DC"], clientes["AG"]
    presencia_dc = cl_dc / (cl_dc + cl_ag) if (cl_dc + cl_ag) else float("nan")
    holgura_r5 = res["holguras"].get("R5_tope_gama_baja")
    return {
        "k": k,
        "Don Carlo ($MM)": res["x"]["DC"],
        "Agnellis ($MM)": res["x"]["AG"],
        "Clientes Don Carlo": cl_dc,
        "Clientes Agnellis": cl_ag,
        "Presencia relativa Don Carlo (%)": 100 * presencia_dc,
        "Utilidad neta ($MM)": res["Z"],
        "Market share (%)": 100 * sum(total.values()) / mercado_total,
        "R5 holgura (clientes)": holgura_r5,
        "R5 activa": holgura_r5 is not None and abs(holgura_r5) < 1e-6,
    }


def main():
    titulo("PUNTO b) — ESCENARIOS DE CRECIMIENTO DE AGNELLIS")
    print(
        "Se reemplaza R2 (x_DonCarlo = x_Agnellis, supuesto S6) por\n"
        "x_DonCarlo = k * x_Agnellis, y se barre k de 1.0 (paridad, caso base)\n"
        "a 0.0 (toda la plata libre del par gama baja va a Agnellis)."
    )

    filas = []
    for k in VALORES_K:
        params = construir_params(S6_paridad_dc_ag=k)
        res = modelo.resolver(params, objetivo="neta")
        if res["status"] != "Optimal":
            print(f"  k={k}: status {res['status']} (se omite)")
            continue
        filas.append(fila_de(k, res))

    tabla = pd.DataFrame(filas)

    titulo("TABLA: UTILIDAD Y REPARTO DON CARLO / AGNELLIS SEGÚN k", "-")
    print(tabla.to_string(index=False))

    base, libre = tabla.iloc[0], tabla.iloc[-1]  # k=1.0 y k=0.0
    ganancia = libre["Utilidad neta ($MM)"] - base["Utilidad neta ($MM)"]
    titulo("LECTURA: DE LA PARIDAD (k=1) A SOLTAR TODO A AGNELLIS (k=0)", "-")
    print(
        f"  Utilidad neta   : ${base['Utilidad neta ($MM)']:,.2f} MM -> "
        f"${libre['Utilidad neta ($MM)']:,.2f} MM  "
        f"(+${ganancia:,.2f} MM, +{100 * ganancia / base['Utilidad neta ($MM)']:.3f}%)\n"
        f"  Don Carlo       : ${base['Don Carlo ($MM)']:,.2f} MM -> "
        f"${libre['Don Carlo ($MM)']:,.2f} MM\n"
        f"  Agnellis        : ${base['Agnellis ($MM)']:,.2f} MM -> "
        f"${libre['Agnellis ($MM)']:,.2f} MM\n"
        f"  Presencia relativa de Don Carlo (dentro del par DC+AG): "
        f"{base['Presencia relativa Don Carlo (%)']:.2f}% -> "
        f"{libre['Presencia relativa Don Carlo (%)']:.2f}%"
    )

    activa = tabla[tabla["R5 activa"]]
    if len(activa):
        print(f"\n  R5 (tope 65% gama baja) se activa a partir de k <= {activa['k'].max()}")
    else:
        print(
            "\n  R5 (tope 65% gama baja) no se activa en ningún escenario del "
            "barrido: el freno nunca es el mercado, es el presupuesto residual "
            "que dejan libre R3 y R4 (ver procedimiento.md §3.5)."
        )

    ruta_grafico = graficos.utilidad_vs_k_paridad(tabla)
    print(f"\nGráfico guardado en: {ruta_grafico.relative_to(RAIZ)}")

    ruta_csv = SALIDA / "07_pregunta_b_escenarios_agnellis.csv"
    tabla.to_csv(ruta_csv, index=False, encoding="utf-8-sig")
    print(f"Tabla guardada en: {ruta_csv.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
