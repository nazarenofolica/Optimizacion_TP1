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
        "Presencia relativa Don Carlo (%)".
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
        tabla["Presencia relativa Don Carlo (%)"],
        color="black",
        marker="s",
        linestyle="--",
        linewidth=1.3,
        label="Presencia relativa de Don Carlo (%)",
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
