"""
Gráficos del TP1 Pastarazzi.

Cada función recibe una tabla ya calculada (nunca vuelve a resolver el modelo) y
guarda un PNG en resultados/graficos/. Estilo matplotlib puro, sin dependencias
extra, pensado para pegarse tal cual en el informe.
"""

from pathlib import Path

import matplotlib.pyplot as plt

CARPETA = Path(__file__).resolve().parents[1] / "resultados" / "graficos"

#: Paleta fija por marca, para que el color de cada una sea el mismo en todos
#: los gráficos del informe.
COLOR = {
    "DC": "#c0504d",
    "AG": "#4f81bd",
    "TRI": "#9bbb59",
    "CAN": "#8064a2",
    "RS": "#f79646",
}
NOMBRE = {
    "DC": "Don Carlo",
    "AG": "Agnellis",
    "TRI": "Triguetti",
    "CAN": "Candealix",
    "RS": "Rena Speziale",
}


def _guardar(fig, nombre):
    CARPETA.mkdir(parents=True, exist_ok=True)
    ruta = CARPETA / f"{nombre}.png"
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return ruta


def utilidad_vs_k_paridad(tabla, nombre_archivo="02_utilidad_vs_k_paridad"):
    """Pregunta b): utilidad total y reparto Don Carlo/Agnellis en función de k.

    Parameters
    ----------
    tabla : pandas.DataFrame
        Columnas: "k", "Utilidad neta ($MM)", "Don Carlo ($MM)", "Agnellis ($MM)",
        "Presencia DC solo campaña (%)", "Presencia DC base+campaña (%)".

    El panel derecho grafica las DOS medidas de presencia a propósito: la brecha
    entre ambas curvas ES la respuesta a la pregunta b). Medida solo sobre la
    campaña, la presencia de Don Carlo se derrumba; medida sobre el mercado real
    (sumando su base instalada de 7,5 millones de clientes) casi no se mueve.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    ax1.plot(tabla["k"], tabla["Utilidad neta ($MM)"], marker="o", color="#1f5c99")
    ax1.set_xlabel("k   (Don Carlo = k · Agnellis)")
    ax1.set_ylabel("Utilidad neta total ($MM)")
    ax1.set_title("Utilidad total vs. paridad Don Carlo / Agnellis")
    ax1.invert_xaxis()
    ax1.grid(alpha=0.3)

    ax2.stackplot(
        tabla["k"],
        tabla["Don Carlo ($MM)"],
        tabla["Agnellis ($MM)"],
        labels=["Don Carlo", "Agnellis"],
        colors=[COLOR["DC"], COLOR["AG"]],
    )
    ax2b = ax2.twinx()
    ax2b.plot(
        tabla["k"],
        tabla["Presencia DC solo campaña (%)"],
        color="black",
        marker="s",
        linestyle="--",
        linewidth=1.3,
        label="Presencia DC — solo campaña (%)",
    )
    ax2b.plot(
        tabla["k"],
        tabla["Presencia DC base+campaña (%)"],
        color="black",
        marker="^",
        linestyle="-",
        linewidth=1.8,
        label="Presencia DC — base + campaña (%)",
    )
    ax2b.set_ylabel("Presencia relativa de Don Carlo (%)")
    ax2b.set_ylim(0, 100)

    ax2.set_xlabel("k   (Don Carlo = k · Agnellis)")
    ax2.set_ylabel("Inversión ($MM)")
    ax2.set_title("Reparto Don Carlo / Agnellis y presencia relativa")
    ax2.invert_xaxis()
    l1, la1 = ax2.get_legend_handles_labels()
    l2, la2 = ax2b.get_legend_handles_labels()
    ax2.legend(l1 + l2, la1 + la2, loc="upper left", fontsize=8)
    ax2.grid(alpha=0.3)

    fig.suptitle("Pregunta b) — Escenarios de crecimiento de Agnellis", fontsize=12)
    fig.tight_layout()
    return _guardar(fig, nombre_archivo)


#: Colores de los escenarios de la pregunta c). El caso real va en negro para que
#: se lea como referencia y los contrafácticos en color.
COLOR_ESCENARIO = {
    "Reglas actuales": "#111111",
    "Sin R3 (30% Triguetti)": "#c0504d",
    "Sin R4 (doble de Rena)": "#4f81bd",
    "Sin R3 ni R4": "#9bbb59",
}


def frontera_pareto(tabla, nombre_archivo="03_frontera_pareto"):
    """Pregunta c): fronteras de Pareto utilidad vs. market share por escenario.

    Parameters
    ----------
    tabla : pandas.DataFrame
        Columnas: "Escenario", "Market share (%)", "Utilidad neta ($MM)".

    El escenario "Reglas actuales" aparece como un punto suelto, no como curva:
    esa es justamente la respuesta a la pregunta. Con las reglas del directorio
    vigentes no hay frontera que recorrer, hay un único plan posible.
    """
    fig, ax = plt.subplots(figsize=(9, 5.5))

    for nombre, grupo in tabla.groupby("Escenario", sort=False):
        color = COLOR_ESCENARIO.get(nombre, "#666666")
        if len(grupo) == 1:
            x = grupo["Market share (%)"].iloc[0]
            y = grupo["Utilidad neta ($MM)"].iloc[0]
            ax.scatter(
                [x],
                [y],
                s=180,
                marker="*",
                color=color,
                zorder=5,
                label=f"{nombre} (frontera colapsada)",
            )
            ax.annotate(
                f"Plan vigente\n{x:.2f}% · ${y:,.0f}MM\nqueda abajo y a la izquierda\nde todas las curvas",
                xy=(x, y),
                xytext=(18, 34),
                textcoords="offset points",
                fontsize=8,
                color="#333333",
                arrowprops=dict(arrowstyle="->", color="#666666", lw=0.9),
            )
        else:
            ax.plot(
                grupo["Market share (%)"],
                grupo["Utilidad neta ($MM)"],
                marker="o",
                markersize=4,
                linewidth=1.8,
                color=color,
                label=nombre,
            )

    ax.set_xlabel("Market share de Pastarazzi (%)")
    ax.set_ylabel("Utilidad neta ($MM)")
    ax.set_title(
        "Pregunta c) — Frontera de Pareto: rentabilidad vs. market share",
        fontsize=12,
    )
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9, loc="upper left")
    fig.text(
        0.5,
        -0.02,
        "Cada curva es el conjunto de planes eficientes: no se puede subir sin "
        "moverse a la derecha.\nLa pendiente es lo que cuesta un punto de "
        "participación, medido en utilidad.",
        ha="center",
        fontsize=8,
        color="#555555",
    )
    fig.tight_layout()
    return _guardar(fig, nombre_archivo)
