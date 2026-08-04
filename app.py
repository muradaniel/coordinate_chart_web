"""Aplicacao Streamlit para curvas integradas de protecao ANSI 50/51."""

from __future__ import annotations

import json
from uuid import uuid4

import numpy as np
import plotly.graph_objects as go
import streamlit as st


MINIMUM_OPERATING_TIME = 0.01

DEFAULT_COLORS = (
    "#D62728",
    "#1F77B4",
    "#2CA02C",
    "#F2C94C",
)

EQUATION_VERSION = 3

CURVE_LIBRARY = {
    "Norma IEC": {
        "Inversa": (0.0, 0.14, 0.02),
        "Muito inversa": (0.0, 13.5, 1.0),
        "Extremamente inversa": (0.0, 80.0, 2.0),
        "Tempo longo": (0.0, 120.0, 1.0),
        "Tempo curto": (0.0, 0.05, 0.04),
    },
    "Norma ANSI": {
        "Moderadamente inversa": (0.0226, 0.0104, 0.02),
        "Inversa": (0.180, 5.98, 2.0),
        "Muito inversa": (0.0963, 3.88, 2.0),
        "Extremamente inversa": (0.02434, 5.64, 2.0),
        "Tempo curto": (0.00262, 0.00342, 0.02),
    },
}

DEFAULT_CURVE_TYPES = {
    "Norma IEC": "Extremamente inversa",
    "Norma ANSI": "Moderadamente inversa",
}


FIGURE_FORMATS = {
    "Tela (Responsivo)": {
        "width": None,
        "height": 800,
        "font_size": 14,
        "line_width": 3,
        "export_width": 1600,
        "export_height": 1000,
        "margin": {"l": 80, "r": 35, "t": 55, "b": 75},
    },
    "A4 Retrato": {
        "width": 1240,
        "height": 1754,
        "font_size": 18,
        "line_width": 4,
        "export_width": 1240,
        "export_height": 1754,
        "margin": {"l": 115, "r": 60, "t": 75, "b": 110},
    },
    "A4 Paisagem": {
        "width": 1754,
        "height": 1240,
        "font_size": 18,
        "line_width": 4,
        "export_width": 1754,
        "export_height": 1240,
        "margin": {"l": 115, "r": 60, "t": 70, "b": 105},
    },
}


def new_curve(index: int) -> dict[str, float | str | bool]:
    """Cria uma curva IEC extremamente inversa e independente."""

    return {
        "id": uuid4().hex,
        "NOME": f"Curva {index}",
        "COR": DEFAULT_COLORS[(index - 1) % len(DEFAULT_COLORS)],
        "STANDARD": "Norma IEC",
        "CURVE_TYPE": "Extremamente inversa",
        "IMIN_AT": 100.0,
        "B": 80.0,
        "ALFA": 2.0,
        "A": 0.0,
        "TDS": 1.0,
        "ENABLE_50": False,
        "I50": 1000.0,
        "I_MAX": 20000.0,
    }


def default_curves() -> list[dict[str, float | str | bool]]:
    return [new_curve(1)]


CONFIG_FIELDS = (
    "NOME", "COR", "STANDARD", "CURVE_TYPE", "IMIN_AT",
    "B", "ALFA", "A", "TDS", "ENABLE_50", "I50", "I_MAX",
)


def bounded_number(value: object, default: float, low: float, high: float) -> float:
    """Converte e limita numeros recebidos de arquivos externos."""

    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if not np.isfinite(number):
        return default
    return min(max(number, low), high)


def valid_color(value: object, default: str) -> str:
    color = str(value)
    try:
        if len(color) == 7 and color.startswith("#"):
            int(color[1:], 16)
            return color
    except ValueError:
        pass
    return default


def serialize_configuration(
    curves: list[dict[str, float | str | bool]],
    graph_title: str,
    figure_format: str,
    grid_alpha: float,
) -> str:
    """Serializa apenas configuracoes, sem reaproveitar IDs internos."""

    payload = {
        "version": EQUATION_VERSION,
        "graph_title": graph_title,
        "figure_format": figure_format,
        "grid_alpha": grid_alpha,
        "curves": [
            {field: curve[field] for field in CONFIG_FIELDS} for curve in curves
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def parse_configuration(data: object) -> dict[str, object]:
    """Valida o JSON e converte arquivos de versoes anteriores."""

    if not isinstance(data, dict) or not isinstance(data.get("curves"), list):
        raise ValueError("Arquivo de configura\u00e7\u00e3o inv\u00e1lido.")
    if not data["curves"]:
        raise ValueError("O arquivo precisa conter pelo menos uma curva.")

    config_version = int(data.get("version", 1))
    curves = []
    for index, raw in enumerate(data["curves"], start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"Curva {index} inv\u00e1lida.")

        curve = new_curve(index)
        curve["NOME"] = str(raw.get("NOME", curve["NOME"]))[:200]
        curve["COR"] = valid_color(raw.get("COR"), str(curve["COR"]))
        curve["IMIN_AT"] = bounded_number(
            raw.get("IMIN_AT"), 100.0, 0.000001, 1.0e9
        )

        standard = str(raw.get("STANDARD", "Norma IEC"))
        if standard not in CURVE_LIBRARY:
            standard = "Norma IEC"
        curve_type = str(raw.get("CURVE_TYPE", DEFAULT_CURVE_TYPES[standard]))
        if curve_type not in CURVE_LIBRARY[standard]:
            curve_type = DEFAULT_CURVE_TYPES[standard]
        curve["STANDARD"] = standard
        curve["CURVE_TYPE"] = curve_type
        default_a, default_b, default_alpha = CURVE_LIBRARY[standard][curve_type]

        raw_a = bounded_number(raw.get("A"), default_a, 0.0, 1.0e9)
        raw_b = bounded_number(raw.get("B"), default_b, 0.0, 1.0e9)
        if config_version == 1 and raw_a == 80.0 and raw_b == 0.0:
            raw_a, raw_b = 0.0, 80.0
        curve["A"] = raw_a
        curve["B"] = raw_b
        curve["ALFA"] = bounded_number(
            raw.get("ALFA"), default_alpha, 0.000001, 100.0
        )
        curve["TDS"] = bounded_number(
            raw.get("TDS"), 1.0, 0.000001, 1.0e6
        )
        curve["ENABLE_50"] = raw.get("ENABLE_50") is True
        minimum_current = float(curve["IMIN_AT"]) * 1.001
        curve["I50"] = bounded_number(
            raw.get("I50"), 1000.0, minimum_current, 1.0e12
        )
        curve["I_MAX"] = bounded_number(
            raw.get("I_MAX"), 20000.0, minimum_current, 1.0e12
        )
        curves.append(curve)

    figure_format = str(data.get("figure_format", "Tela (Responsivo)"))
    if figure_format not in FIGURE_FORMATS:
        figure_format = "Tela (Responsivo)"

    return {
        "curves": curves,
        "graph_title": str(
            data.get("graph_title", "Coordenograma de Prote\u00e7\u00e3o")
        )[:300],
        "figure_format": figure_format,
        "grid_alpha": bounded_number(data.get("grid_alpha"), 0.28, 0.0, 1.0),
    }


def initialize_state() -> None:
    """Inicializa a interface atual e aplica imports antes dos widgets."""

    pending_import = st.session_state.pop("_pending_import", None)
    if isinstance(pending_import, dict):
        st.session_state.curves = pending_import["curves"]
        st.session_state.figure_format = pending_import["figure_format"]
        st.session_state.graph_title = pending_import["graph_title"]
        st.session_state.grid_alpha = pending_import["grid_alpha"]
        st.session_state.collapsed_curve_ids = {
            str(curve["id"]) for curve in pending_import["curves"]
        }
        st.session_state.equation_version = EQUATION_VERSION

    if st.session_state.get("equation_version") != EQUATION_VERSION:
        st.session_state.curves = default_curves()
        st.session_state.figure_format = "Tela (Responsivo)"
        st.session_state.graph_title = "Coordenograma de Prote\u00e7\u00e3o"
        st.session_state.grid_alpha = 0.28
        st.session_state.collapsed_curve_ids = set()
        st.session_state.equation_version = EQUATION_VERSION

    required = {
        "id", "NOME", "COR", "STANDARD", "CURVE_TYPE", "IMIN_AT",
        "B", "ALFA", "A", "TDS", "ENABLE_50", "I50", "I_MAX",
    }
    stored = st.session_state.get("curves")
    invalid = (
        not isinstance(stored, list)
        or not stored
        or any(not required.issubset(curve) for curve in stored)
    )
    if invalid:
        st.session_state.curves = default_curves()

    if st.session_state.get("figure_format") not in FIGURE_FORMATS:
        st.session_state.figure_format = "Tela (Responsivo)"
    st.session_state.grid_alpha = bounded_number(
        st.session_state.get("grid_alpha"), 0.28, 0.0, 1.0
    )
    st.session_state.setdefault("collapsed_curve_ids", set())
    st.session_state.setdefault("graph_title", "Coordenograma de Prote\u00e7\u00e3o")


def inverse_time(
    currents: np.ndarray, curve: dict[str, float | str | bool]
) -> np.ndarray:
    """Calcula t = A + (B / (M**ALFA - 1)) * TDS."""

    imin = float(curve["IMIN_AT"])
    alpha = float(curve["ALFA"])
    a_value = float(curve["A"])
    b_value = float(curve["B"])
    tds = float(curve["TDS"])

    multiples = currents / imin
    exponent = alpha * np.log(multiples)

    inverse_term = np.empty_like(exponent)
    regular = exponent < 700.0
    inverse_term[regular] = b_value / np.expm1(exponent[regular])
    inverse_term[~regular] = b_value * np.exp(-exponent[~regular])

    times = a_value + inverse_term * tds
    return np.maximum(times, np.finfo(float).tiny)


def calculate_curve(
    curve: dict[str, float | str | bool], current_max: float, points: int = 1000
) -> tuple[np.ndarray, np.ndarray]:
    """Gera uma curva 51 limitada em corrente ou integrada com a funcao 50."""

    imin = float(curve["IMIN_AT"])
    has_50 = bool(curve["ENABLE_50"])
    requested_end = float(curve["I50"] if has_50 else curve["I_MAX"])
    timed_end = max(requested_end, imin * 1.001)

    timed_currents = np.geomspace(imin * 1.001, timed_end, points)
    timed_times = inverse_time(timed_currents, curve)

    if not has_50:
        return timed_currents, timed_times

    connection_time = float(timed_times[-1])
    instantaneous_time = min(MINIMUM_OPERATING_TIME, connection_time)
    horizontal_end = min(current_max, timed_end * 1.35)
    currents = np.concatenate((timed_currents, [timed_end, horizontal_end]))
    times = np.concatenate(
        (timed_times, [instantaneous_time, instantaneous_time])
    )
    return currents, times



def curve_by_id(curve_id: str) -> dict[str, float | str | bool]:
    return next(
        curve for curve in st.session_state.curves if str(curve["id"]) == curve_id
    )


def apply_selected_factors(
    curve_id: str, standard: str, curve_type: str
) -> None:
    """Atualiza o modelo e os tres widgets antes do rerun."""

    curve = curve_by_id(curve_id)
    a_value, b_value, alpha = CURVE_LIBRARY[standard][curve_type]
    curve["STANDARD"] = standard
    curve["CURVE_TYPE"] = curve_type
    curve["A"] = a_value
    curve["B"] = b_value
    curve["ALFA"] = alpha
    st.session_state[f"a_{curve_id}"] = a_value
    st.session_state[f"b_{curve_id}"] = b_value
    st.session_state[f"alpha_{curve_id}"] = alpha


def on_standard_change(curve_id: str) -> None:
    standard = st.session_state[f"standard_{curve_id}"]
    curve_type = DEFAULT_CURVE_TYPES[standard]
    st.session_state[f"curve_type_{curve_id}"] = curve_type
    apply_selected_factors(curve_id, standard, curve_type)


def on_curve_type_change(curve_id: str) -> None:
    standard = st.session_state[f"standard_{curve_id}"]
    curve_type = st.session_state[f"curve_type_{curve_id}"]
    apply_selected_factors(curve_id, standard, curve_type)

def render_sidebar() -> tuple[str, str, float]:
    """Renderiza somente formato, lista e parametros das curvas."""

    with st.sidebar:
        st.title("Coordenograma")

        if st.button("Adicionar Curva", type="primary", width="stretch"):
            st.session_state.curves.append(new_curve(len(st.session_state.curves) + 1))
            st.rerun()

        graph_title = st.text_input(
            "T\u00edtulo do gr\u00e1fico",
            key="graph_title",
        )
        format_column, grid_column = st.columns((1.35, 1.0))
        with format_column:
            figure_format = st.selectbox(
                "Formato da figura",
                tuple(FIGURE_FORMATS),
                key="figure_format",
            )
        with grid_column:
            grid_alpha = st.slider(
                "Alpha do grid",
                min_value=0.0,
                max_value=1.0,
                step=0.05,
                key="grid_alpha",
                help="Controla a transparência das linhas do grid.",
            )

        curve_to_remove: str | None = None
        for position, curve in enumerate(st.session_state.curves, start=1):
            curve_id = str(curve["id"])
            title = str(curve["NOME"]) or f"Curva {position}"

            with st.expander(
                title,
                expanded=curve_id
                not in st.session_state.collapsed_curve_ids,
            ):
                curve["NOME"] = st.text_input(
                    "Nome", value=str(curve["NOME"]), key=f"name_{curve_id}"
                )
                curve["COR"] = st.color_picker(
                    "Cor", value=str(curve["COR"]), key=f"color_{curve_id}"
                )

                standard_key = f"standard_{curve_id}"
                if (
                    standard_key not in st.session_state
                    or st.session_state[standard_key] not in CURVE_LIBRARY
                ):
                    st.session_state[standard_key] = str(curve["STANDARD"])
                selected_standard = st.selectbox(
                    "Norma",
                    tuple(CURVE_LIBRARY),
                    key=standard_key,
                    on_change=on_standard_change,
                    args=(curve_id,),
                )

                type_options = tuple(CURVE_LIBRARY[selected_standard])
                type_key = f"curve_type_{curve_id}"
                if (
                    type_key not in st.session_state
                    or st.session_state[type_key] not in type_options
                ):
                    current_type = str(curve["CURVE_TYPE"])
                    st.session_state[type_key] = (
                        current_type
                        if current_type in type_options
                        else DEFAULT_CURVE_TYPES[selected_standard]
                    )
                selected_type = st.selectbox(
                    "Tipo de curva",
                    type_options,
                    key=type_key,
                    on_change=on_curve_type_change,
                    args=(curve_id,),
                )
                curve["STANDARD"] = selected_standard
                curve["CURVE_TYPE"] = selected_type

                st.caption("Fatores da curva: A, B e \u03b1")
                a_key = f"a_{curve_id}"
                b_key = f"b_{curve_id}"
                alpha_key = f"alpha_{curve_id}"
                st.session_state.setdefault(a_key, float(curve["A"]))
                st.session_state.setdefault(b_key, float(curve["B"]))
                st.session_state.setdefault(alpha_key, float(curve["ALFA"]))
                curve["A"] = st.number_input(
                    "A",
                    min_value=0.0,
                    max_value=1.0e9,
                    format="%.6f",
                    key=a_key,
                )
                curve["B"] = st.number_input(
                    "B",
                    min_value=0.0,
                    max_value=1.0e9,
                    format="%.6f",
                    key=b_key,
                )
                curve["ALFA"] = st.number_input(
                    "ALFA (\u03b1)",
                    min_value=0.000001,
                    max_value=100.0,
                    format="%.6f",
                    key=alpha_key,
                )
                curve["IMIN_AT"] = st.number_input(
                    "Ip - corrente de pickup (A)",
                    min_value=0.000001,
                    max_value=1.0e9,
                    value=float(curve["IMIN_AT"]),
                    format="%.6f",
                    key=f"imin_{curve_id}",
                )
                curve["TDS"] = st.number_input(
                    "TDS",
                    min_value=0.000001,
                    max_value=1.0e6,
                    value=float(curve["TDS"]),
                    format="%.6f",
                    key=f"tds_{curve_id}",
                )

                curve["ENABLE_50"] = st.checkbox(
                    "Habilitar Fun\u00e7\u00e3o 50",
                    value=bool(curve["ENABLE_50"]),
                    key=f"enable_50_{curve_id}",
                )

                if curve["ENABLE_50"]:
                    minimum_i50 = float(curve["IMIN_AT"]) * 1.001
                    i50_key = f"i50_{curve_id}"
                    if float(curve["I50"]) < minimum_i50:
                        curve["I50"] = minimum_i50
                    if (
                        i50_key in st.session_state
                        and float(st.session_state[i50_key]) < minimum_i50
                    ):
                        del st.session_state[i50_key]

                    curve["I50"] = st.number_input(
                        "I50",
                        min_value=minimum_i50,
                        max_value=1.0e12,
                        value=float(curve["I50"]),
                        format="%.6f",
                        key=i50_key,
                        help="Deve ser maior que Ip.",
                    )
                else:
                    minimum_current_limit = float(curve["IMIN_AT"]) * 1.001
                    current_limit_key = f"imax_{curve_id}"
                    if float(curve["I_MAX"]) < minimum_current_limit:
                        curve["I_MAX"] = minimum_current_limit
                    if (
                        current_limit_key in st.session_state
                        and float(st.session_state[current_limit_key])
                        < minimum_current_limit
                    ):
                        del st.session_state[current_limit_key]

                    curve["I_MAX"] = st.number_input(
                        "Corrente m\u00e1xima da curva (A)",
                        min_value=minimum_current_limit,
                        max_value=1.0e12,
                        value=float(curve["I_MAX"]),
                        format="%.6f",
                        key=current_limit_key,
                        help="A curva 51 termina exatamente neste valor do eixo X.",
                    )

                if st.button(
                    "Remover curva",
                    key=f"remove_{curve_id}",
                    disabled=len(st.session_state.curves) == 1,
                    width="stretch",
                ):
                    curve_to_remove = curve_id

        if curve_to_remove is not None:
            st.session_state.curves = [
                curve
                for curve in st.session_state.curves
                if str(curve["id"]) != curve_to_remove
            ]
            st.rerun()

        st.divider()
        st.subheader("Configura\u00e7\u00f5es")
        config_json = serialize_configuration(
            st.session_state.curves, graph_title, figure_format, grid_alpha
        )
        st.download_button(
            "Baixar configura\u00e7\u00f5es",
            data=config_json.encode("utf-8"),
            file_name="configuracoes_curvas_50_51.json",
            mime="application/json",
            width="stretch",
        )
        uploaded_file = st.file_uploader(
            "Enviar configura\u00e7\u00f5es",
            type=("json",),
            key="config_upload",
        )
        if uploaded_file is not None and st.button(
            "Carregar configura\u00e7\u00f5es",
            width="stretch",
        ):
            try:
                raw_config = json.loads(
                    uploaded_file.getvalue().decode("utf-8-sig")
                )
                st.session_state._pending_import = parse_configuration(raw_config)
                st.rerun()
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
                st.error(str(error))

        st.divider()
        st.markdown(
            "<div style='text-align:center;opacity:.62;font-size:.75rem;'>"
            "Desenvolvido por Daniel Murad de Freitas"
            "</div>",
            unsafe_allow_html=True,
        )

    return figure_format, graph_title, grid_alpha


def build_figure(
    curves: list[dict[str, float | str | bool]],
    figure_format: str,
    grid_alpha: float,
) -> go.Figure:
    """Reconstroi todo o grafico a partir do estado atual."""

    settings = FIGURE_FORMATS[figure_format]
    major_grid_color = f"rgba(128,128,128,{grid_alpha:.3f})"
    minor_grid_color = f"rgba(128,128,128,{grid_alpha * 0.43:.3f})"
    pickups = [float(curve["IMIN_AT"]) for curve in curves]
    curve_limits = [
        float(curve["I50"]) * 1.35
        if bool(curve["ENABLE_50"])
        else float(curve["I_MAX"])
        for curve in curves
    ]

    current_min = min(0.1, min(pickups) * 0.8)
    current_max = max(
        20_000.0,
        max(pickups) * 100.0,
        max(curve_limits) * 1.05,
    )

    figure = go.Figure()
    for curve in curves:
        currents, times = calculate_curve(curve, current_max)
        figure.add_trace(
            go.Scatter(
                x=currents,
                y=times,
                mode="lines",
                name=str(curve["NOME"]) or "Sem nome",
                line={
                    "color": str(curve["COR"]),
                    "width": settings["line_width"],
                },
                hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Icc: %{x:,.3f} A<br>"
                    "Tempo: %{y:,.4f} s<extra></extra>"
                ),
            )
        )

    layout = {
        "height": settings["height"],
        "autosize": settings["width"] is None,
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {
            "family": "Arial, sans-serif",
            "size": settings["font_size"],
        },
        "hovermode": "closest",
        "margin": settings["margin"],
        "legend": {
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
            "bgcolor": "rgba(0,0,0,0)",
        },
        "xaxis": {
            "type": "log",
            "title": "Corrente de curto-circuito - Icc (A)",
            "range": [np.log10(current_min), np.log10(current_max)],
            "showgrid": True,
            "gridcolor": major_grid_color,
            "minor": {"showgrid": True, "gridcolor": minor_grid_color},
            "tickfont": {"color": "#000000"},
            "zeroline": False,
        },
        "yaxis": {
            "type": "log",
            "title": "Tempo (s)",
            "autorange": True,
            "showgrid": True,
            "gridcolor": major_grid_color,
            "minor": {"showgrid": True, "gridcolor": minor_grid_color},
            "tickfont": {"color": "#000000"},
            "zeroline": False,
        },
    }
    if settings["width"] is not None:
        layout["width"] = settings["width"]

    figure.update_layout(**layout)
    return figure


def main() -> None:
    st.set_page_config(
        page_title="Coordenograma",
        page_icon="\u26a1",
        layout="wide",
    )
    initialize_state()
    figure_format, graph_title, grid_alpha = render_sidebar()

    st.title(graph_title or "Curvas de Prote\u00e7\u00e3o ANSI 50/51")
    settings = FIGURE_FORMATS[figure_format]
    figure = build_figure(st.session_state.curves, figure_format, grid_alpha)
    st.plotly_chart(
        figure,
        width="stretch" if settings["width"] is None else "content",
        theme="streamlit",
        config={
            "displaylogo": False,
            "scrollZoom": True,
            "toImageButtonOptions": {
                "format": "png",
                "filename": "curvas_protecao_50_51",
                "width": settings["export_width"],
                "height": settings["export_height"],
                "scale": 2,
            },
        },
    )


if __name__ == "__main__":
    main()
