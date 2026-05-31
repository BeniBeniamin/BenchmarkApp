import io
import random
import time
import tracemalloc
import unicodedata
from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    Image as ReportLabImage,
    PageBreak
)

st.set_page_config(page_title="Algorithm Benchmark App", layout="wide", page_icon="📊")

# -----------------------------
# Page style
# -----------------------------
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        [data-testid="stSidebar"] {
            background-color: #131b2a;
        }

        /* Metric cards */
        div[data-testid="stMetric"] {
            background: linear-gradient(180deg, #111827 0%, #162033 100%);
            border: 1px solid #253247;
            border-radius: 16px;
            padding: 14px 16px;
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.20);
        }

        div[data-testid="stMetricLabel"] {
            color: #9fb0c8 !important;
            font-weight: 600;
        }

        div[data-testid="stMetricLabel"] p {
            color: #9fb0c8 !important;
            font-weight: 600;
        }

        div[data-testid="stMetricValue"] {
            color: #f8fafc !important;
        }

        div[data-testid="stMetricValue"] > div {
            color: #f8fafc !important;
        }

        div[data-testid="stMetricDelta"] {
            color: #cbd5e1 !important;
        }

        .subtitle {
            color: #7e91ad;
            font-size: 1.05rem;
            margin-top: -0.4rem;
        }

        .small-note {
            color: #9db0c9;
            font-size: 0.95rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Data generation
# -----------------------------
def generate_sorting_data(size, data_type):
    if data_type == "Random":
        return [random.randint(0, 10000) for _ in range(size)]
    if data_type == "Sorted":
        return list(range(size))
    if data_type == "Reversed":
        return list(range(size, 0, -1))
    if data_type == "Nearly Sorted":
        arr = list(range(size))
        for _ in range(max(1, size // 10)):
            i = random.randint(0, size - 1)
            j = random.randint(0, size - 1)
            arr[i], arr[j] = arr[j], arr[i]
        return arr
    return []


def generate_searching_data(size):
    return sorted(random.sample(range(0, size * 20), size))


def choose_search_target(data, target_case):
    if target_case == "First element":
        return data[0]
    if target_case == "Middle element":
        return data[len(data) // 2]
    if target_case == "Last element":
        return data[-1]
    if target_case == "Random existing element":
        return random.choice(data)
    return data[-1] + 1


# -----------------------------
# Sorting algorithms
# Each algorithm returns: result, comparisons, moves
# -----------------------------
def bubble_sort(arr):
    comparisons = 0
    moves = 0
    n = len(arr)

    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            comparisons += 1
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                moves += 1
                swapped = True
        if not swapped:
            break

    return arr, comparisons, moves


def insertion_sort(arr):
    comparisons = 0
    moves = 0

    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1

        while j >= 0:
            comparisons += 1
            if arr[j] > key:
                arr[j + 1] = arr[j]
                moves += 1
                j -= 1
            else:
                break
        arr[j + 1] = key

    return arr, comparisons, moves


def merge_sort(arr):
    sorted_arr, comparisons, moves = merge_sort_internal(arr)
    return sorted_arr, comparisons, moves


def merge_sort_internal(arr):
    if len(arr) <= 1:
        return arr, 0, 0

    middle = len(arr) // 2
    left, left_comparisons, left_moves = merge_sort_internal(arr[:middle])
    right, right_comparisons, right_moves = merge_sort_internal(arr[middle:])
    merged, merge_comparisons, merge_moves = merge(left, right)

    return (
        merged,
        left_comparisons + right_comparisons + merge_comparisons,
        left_moves + right_moves + merge_moves,
    )


def merge(left, right):
    result = []
    i = 0
    j = 0
    comparisons = 0
    moves = 0

    while i < len(left) and j < len(right):
        comparisons += 1
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
        moves += 1

    result.extend(left[i:])
    result.extend(right[j:])
    moves += len(left) - i + len(right) - j

    return result, comparisons, moves


def quick_sort(arr):
    comparisons, moves = quick_sort_recursive(arr, 0, len(arr) - 1)
    return arr, comparisons, moves


def quick_sort_recursive(arr, low, high):
    if low >= high:
        return 0, 0

    i = low
    j = high
    pivot = arr[(low + high) // 2]
    comparisons = 0
    moves = 0

    while i <= j:
        while arr[i] < pivot:
            comparisons += 1
            i += 1
        comparisons += 1

        while arr[j] > pivot:
            comparisons += 1
            j -= 1
        comparisons += 1

        if i <= j:
            if i != j:
                arr[i], arr[j] = arr[j], arr[i]
                moves += 1
            i += 1
            j -= 1

    left_comparisons, left_moves = quick_sort_recursive(arr, low, j)
    right_comparisons, right_moves = quick_sort_recursive(arr, i, high)

    return (
        comparisons + left_comparisons + right_comparisons,
        moves + left_moves + right_moves,
    )


# -----------------------------
# Searching algorithms
# Each algorithm returns: index, comparisons, unused_secondary_metric
# -----------------------------
def linear_search(arr, target):
    comparisons = 0
    for index, value in enumerate(arr):
        comparisons += 1
        if value == target:
            return index, comparisons, 0
    return -1, comparisons, 0


def binary_search(arr, target):
    low = 0
    high = len(arr) - 1
    comparisons = 0

    while low <= high:
        middle = (low + high) // 2
        comparisons += 1
        if arr[middle] == target:
            return middle, comparisons, 0
        if arr[middle] < target:
            low = middle + 1
        else:
            high = middle - 1

    return -1, comparisons, 0


def jump_search(arr, target):
    n = len(arr)
    step = max(1, int(n ** 0.5))
    previous = 0
    current = step
    comparisons = 0

    while previous < n and arr[min(current, n) - 1] < target:
        comparisons += 1
        previous = current
        current += step
        if previous >= n:
            return -1, comparisons, 0

    while previous < min(current, n):
        comparisons += 1
        if arr[previous] == target:
            return previous, comparisons, 0
        if arr[previous] > target:
            return -1, comparisons, 0
        previous += 1

    return -1, comparisons, 0


def interpolation_search(arr, target):
    low = 0
    high = len(arr) - 1
    comparisons = 0

    while low <= high and arr[low] <= target <= arr[high]:
        if arr[high] == arr[low]:
            comparisons += 1
            if arr[low] == target:
                return low, comparisons, 0
            return -1, comparisons, 0

        position = low + int(
            ((target - arr[low]) * (high - low)) / (arr[high] - arr[low])
        )
        comparisons += 1

        if arr[position] == target:
            return position, comparisons, 0
        if arr[position] < target:
            low = position + 1
        else:
            high = position - 1

    return -1, comparisons, 0


# -----------------------------
# Benchmark utilities
# -----------------------------
def run_algorithm(func, data, problem_type, target=None):
    working_data = data.copy()
    if problem_type == "Sorting":
        return func(working_data)
    return func(working_data, target)


def measure_metrics(func, data, runs, problem_type, target=None):
    total_time = 0.0
    total_comparisons = 0
    total_moves = 0
    last_result = None

    for _ in range(runs):
        start = time.perf_counter()
        result, comparisons, moves = run_algorithm(func, data, problem_type, target)
        end = time.perf_counter()

        total_time += end - start
        total_comparisons += comparisons
        total_moves += moves
        last_result = result

    memory_data = data.copy()
    tracemalloc.start()
    if problem_type == "Sorting":
        func(memory_data)
    else:
        func(memory_data, target)
    _, peak_memory_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "total_time": total_time,
        "avg_time": total_time / runs,
        "avg_comparisons": total_comparisons / runs,
        "avg_moves": total_moves / runs,
        "peak_memory_kb": peak_memory_bytes / 1024,
        "result": last_result,
    }


def make_bar_chart(results_df, column, title, value_format):
    chart_data = results_df[["Algoritm", column]].copy()

    chart = (
        alt.Chart(chart_data)
        .mark_bar(
            size=70,
            cornerRadiusTopLeft=5,
            cornerRadiusTopRight=5
        )
        .encode(
            x=alt.X(
                "Algoritm:N",
                title=None,
                sort=None,
                axis=alt.Axis(
                    labelAngle=0,
                    labelFontSize=13,
                    labelColor="#374151",
                    labelPadding=10,
                    ticks=False,
                    domainColor="#5b6472",
                    domainWidth=1.2
                )
            ),
            y=alt.Y(
                f"{column}:Q",
                title=column,
                axis=alt.Axis(
                    titleFontSize=14,
                    titleFontWeight="bold",
                    titleColor="#374151",
                    titlePadding=14,
                    labelFontSize=12,
                    labelColor="#374151",
                    grid=True,
                    gridColor="#e5e7eb",
                    gridWidth=1,
                    domainColor="#5b6472"
                )
            ),
            color=alt.Color(
                "Algoritm:N",
                scale=alt.Scale(
                    range=["#ef5350", "#29a1e6", "#9bc57d", "#f3cf78"]
                ),
                legend=None
            ),
            tooltip=[
                alt.Tooltip("Algoritm:N", title="Algoritm"),
                alt.Tooltip(f"{column}:Q", title=column, format=value_format)
            ]
        )
    )

    labels = (
        alt.Chart(chart_data)
        .mark_text(
            dy=-12,
            fontSize=13,
            fontWeight="bold",
            color="#374151"
        )
        .encode(
            x=alt.X("Algoritm:N", sort=None),
            y=alt.Y(f"{column}:Q"),
            text=alt.Text(f"{column}:Q", format=value_format)
        )
    )

    return (
        (chart + labels)
        .properties(
            width=650,
            height=420,
            title=alt.TitleParams(
                text=title,
                fontSize=24,
                fontWeight="bold",
                color="#1f2937",
                anchor="middle",
                offset=25
            )
        )
        .configure_view(
            stroke=None,
            fill="#ffffff"
        )
        .configure(
            background="#ffffff",
            padding={
                "left": 16,
                "top": 20,
                "right": 18,
                "bottom": 12
            }
        )
    )

def create_pdf_bar_chart(results_df, column, title, value_format):
    chart_data = results_df[["Algoritm", column]].copy()

    algorithm_colors = {
        "Bubble Sort": "#ef5350",
        "Insertion Sort": "#29a1e6",
        "Merge Sort": "#9bc57d",
        "Quick Sort": "#f3cf78",
        "Linear Search": "#ef5350",
        "Binary Search": "#29a1e6",
        "Jump Search": "#9bc57d",
        "Interpolation Search": "#f3cf78",
    }

    bar_colors = [
        algorithm_colors.get(algorithm, "#29a1e6")
        for algorithm in chart_data["Algoritm"]
    ]

    figure, axis = plt.subplots(figsize=(8, 5.4))

    bars = axis.bar(
        chart_data["Algoritm"],
        chart_data[column],
        color=bar_colors,
        width=0.65
    )

    axis.set_title(title, fontsize=17, fontweight="bold", pad=18)
    axis.set_ylabel(column, fontsize=11)
    axis.grid(axis="y", linestyle="-", linewidth=0.7, alpha=0.35)
    axis.set_axisbelow(True)

    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)

    axis.tick_params(axis="x", labelsize=10)
    axis.tick_params(axis="y", labelsize=10)

    maximum_value = chart_data[column].max()

    for bar, value in zip(bars, chart_data[column]):
        if value_format == ".8f":
            label = f"{value:.8f}"
        elif value_format == ".2f":
            label = f"{value:.2f}"
        else:
            label = f"{value:.0f}"

        offset = maximum_value * 0.025 if maximum_value > 0 else 0.01

        axis.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + offset,
            label,
            ha="center",
            va="bottom",
            fontsize=9
        )

    axis.set_ylim(top=maximum_value * 1.18 if maximum_value > 0 else 1)

    figure.tight_layout()

    image_buffer = io.BytesIO()
    figure.savefig(image_buffer, format="png", dpi=180, bbox_inches="tight")
    plt.close(figure)

    image_buffer.seek(0)
    return image_buffer

def plain_text(text):
    return unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("ascii")


def create_pdf_report(results_df, configuration, winner_text, data_preview, problem_type):
    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=1.3 * cm,
        rightMargin=1.3 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
    )

    styles = getSampleStyleSheet()
    elements = []

    # -----------------------------
    # Title and configuration
    # -----------------------------
    elements.append(
        Paragraph("Algorithm Benchmark App - Raport rezultate", styles["Title"])
    )
    elements.append(Spacer(1, 0.25 * cm))

    elements.append(
        Paragraph(
            plain_text(f"Generat la: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"),
            styles["Normal"],
        )
    )

    elements.append(Spacer(1, 0.4 * cm))
    elements.append(Paragraph("Configuratie benchmark", styles["Heading2"]))

    configuration_table = [["Parametru", "Valoare"]]

    for key, value in configuration.items():
        configuration_table.append([plain_text(key), plain_text(value)])

    config_table = Table(
        configuration_table,
        colWidths=[5.2 * cm, 15.5 * cm]
    )

    config_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f3f6fa")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d2dae5")),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    elements.append(config_table)
    elements.append(Spacer(1, 0.5 * cm))

    # -----------------------------
    # Results table
    # -----------------------------
    elements.append(Paragraph("Rezultate", styles["Heading2"]))

    display_df = results_df.copy()

    for column in display_df.columns:
        if pd.api.types.is_float_dtype(display_df[column]):
            display_df[column] = display_df[column].map(lambda value: f"{value:.6f}")

    table_values = [list(display_df.columns)] + display_df.astype(str).values.tolist()
    table_values = [
        [plain_text(value) for value in row]
        for row in table_values
    ]

    column_width = 25.8 * cm / len(display_df.columns)

    result_table = Table(
        table_values,
        colWidths=[column_width] * len(display_df.columns),
        repeatRows=1
    )

    result_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
                    colors.white,
                    colors.HexColor("#f3f6fa")
                ]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d2dae5")),
                ("FONTSIZE", (0, 0), (-1, -1), 7.5),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    elements.append(result_table)
    elements.append(Spacer(1, 0.45 * cm))
    elements.append(Paragraph(plain_text(winner_text), styles["Normal"]))
    elements.append(Spacer(1, 0.35 * cm))

    elements.append(Paragraph("Esantion date utilizate", styles["Heading2"]))
    elements.append(Paragraph(plain_text(data_preview), styles["Normal"]))

    # -----------------------------
    # Charts page
    # -----------------------------
    elements.append(PageBreak())
    elements.append(Paragraph("Vizualizare grafica a rezultatelor", styles["Title"]))
    elements.append(Spacer(1, 0.4 * cm))

    time_chart = create_pdf_bar_chart(
        results_df,
        "Timp mediu (s)",
        "Timp mediu per rulare" if problem_type == "Sorting" else "Timp mediu per cautare",
        ".8f"
    )

    comparisons_chart = create_pdf_bar_chart(
        results_df,
        "Comparatii medii",
        "Comparatii medii",
        ".0f"
    )

    memory_chart = create_pdf_bar_chart(
        results_df,
        "Memorie varf (KB)",
        "Memorie maxima utilizata",
        ".2f"
    )

    chart_width = 12.2 * cm
    chart_height = 8.0 * cm

    chart_table_rows = [
        [
            ReportLabImage(time_chart, width=chart_width, height=chart_height),
            ReportLabImage(comparisons_chart, width=chart_width, height=chart_height),
        ],
        [
            ReportLabImage(memory_chart, width=chart_width, height=chart_height),
            ""
        ],
    ]

    if problem_type == "Sorting":
        moves_chart = create_pdf_bar_chart(
            results_df,
            "Mutari medii",
            "Mutari medii",
            ".0f"
        )

        chart_table_rows[1][1] = ReportLabImage(
            moves_chart,
            width=chart_width,
            height=chart_height
        )

    chart_table = Table(
        chart_table_rows,
        colWidths=[13.2 * cm, 13.2 * cm],
        rowHeights=[8.6 * cm, 8.6 * cm]
    )

    chart_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    elements.append(chart_table)

    document.build(elements)
    buffer.seek(0)

    return buffer.getvalue()

# -----------------------------
# UI configuration
# -----------------------------
st.title("📊 Algorithm Benchmark App")

st.sidebar.header("Configurare test")
problem_type = st.sidebar.selectbox("Tipul problemei", ["Sorting", "Searching"])
input_size = st.sidebar.selectbox("Dimensiunea setului de date", [100, 1000, 5000, 10000])
num_runs = st.sidebar.slider("Numar de rulari", min_value=1, max_value=20, value=5)

if problem_type == "Sorting":
    input_type = st.sidebar.selectbox(
        "Tipul datelor", ["Random", "Sorted", "Reversed", "Nearly Sorted"]
    )
    target_case = None
    algorithm_options = ["Bubble Sort", "Insertion Sort", "Merge Sort", "Quick Sort"]
    algorithm_map = {
        "Bubble Sort": bubble_sort,
        "Insertion Sort": insertion_sort,
        "Merge Sort": merge_sort,
        "Quick Sort": quick_sort,
    }
else:
    input_type = "Sorted unique values"
    target_case = st.sidebar.selectbox(
        "Pozitia valorii cautate",
        ["First element", "Middle element", "Last element", "Random existing element", "Not found"],
    )
    algorithm_options = ["Linear Search", "Binary Search", "Jump Search", "Interpolation Search"]
    algorithm_map = {
        "Linear Search": linear_search,
        "Binary Search": binary_search,
        "Jump Search": jump_search,
        "Interpolation Search": interpolation_search,
    }
    st.sidebar.caption("Pentru comparatie corecta, algoritmii de cautare ruleaza pe date sortate.")

num_algorithms = st.sidebar.slider(
    "Numar de algoritmi comparati", min_value=2, max_value=4, value=2
)

st.write("## Configuratia curenta")
config_cols = st.columns(4)
config_cols[0].metric("Problema", problem_type)
config_cols[1].metric("Dimensiune", f"{input_size:,}")
config_cols[2].metric("Rulari", num_runs)
config_cols[3].metric("Algoritmi", num_algorithms)

st.write("## Selectarea algoritmilor")
selected_algorithms = []
already_selected = []
selection_columns = st.columns(num_algorithms)

for i in range(num_algorithms):
    with selection_columns[i]:
        available_options = [name for name in algorithm_options if name not in already_selected]
        selected_name = st.selectbox(
            f"Algoritmul {i + 1}",
            available_options,
            key=f"{problem_type}_algo_{i}",
        )
        selected_algorithms.append({"label": selected_name, "func": algorithm_map[selected_name]})
        already_selected.append(selected_name)

if st.button("Run Benchmark", type="primary", use_container_width=True):
    if problem_type == "Sorting":
        data = generate_sorting_data(input_size, input_type)
        target = None
    else:
        data = generate_searching_data(input_size)
        target = choose_search_target(data, target_case)

    benchmark_results = []

    try:
        for item in selected_algorithms:
            metrics = measure_metrics(item["func"], data, num_runs, problem_type, target)
            row = {
                "Algoritm": item["label"],
                "Timp total (s)": metrics["total_time"],
                "Timp mediu (s)": metrics["avg_time"],
                "Comparatii medii": metrics["avg_comparisons"],
                "Memorie varf (KB)": metrics["peak_memory_kb"],
            }
            if problem_type == "Sorting":
                row["Mutari medii"] = metrics["avg_moves"]
            else:
                row["Pozitie rezultat"] = (
                    "Negasit" if metrics["result"] == -1 else str(metrics["result"])
                )
            benchmark_results.append(row)
    except Exception as error:
        st.error(f"A aparut o eroare la rularea benchmark-ului: {error}")
        st.stop()

    results_df = pd.DataFrame(benchmark_results)
    fastest_row = results_df.loc[results_df["Timp mediu (s)"].idxmin()]
    winner_text = (
        f"Cel mai rapid algoritm: {fastest_row['Algoritm']}, "
        f"cu timpul mediu {fastest_row['Timp mediu (s)']:.8f} secunde."
    )

    configuration = {
        "Tip problema": problem_type,
        "Dimensiune set de date": input_size,
        "Numar de rulari": num_runs,
        "Algoritmi comparati": ", ".join(results_df["Algoritm"].tolist()),
    }
    if problem_type == "Sorting":
        configuration["Tip date"] = input_type
    else:
        configuration["Structura date"] = "Valori sortate si unice"
        configuration["Caz cautare"] = target_case
        configuration["Valoare cautata"] = target

    preview = f"Primele 20 valori: {data[:20]}"
    pdf_bytes = create_pdf_report(
    results_df,
    configuration,
    winner_text,
    preview,
    problem_type
)

    st.session_state["benchmark_output"] = {
        "problem_type": problem_type,
        "results_df": results_df,
        "winner_text": winner_text,
        "configuration": configuration,
        "data": data,
        "target": target,
        "pdf_bytes": pdf_bytes,
    }

if "benchmark_output" in st.session_state:
    output = st.session_state["benchmark_output"]
    results_df = output["results_df"]
    current_problem = output["problem_type"]

    st.success("Benchmark executat cu succes.")
    st.write("## Rezultate")

    summary_columns = st.columns(len(results_df))
    for index, (_, row) in enumerate(results_df.iterrows()):
        with summary_columns[index]:
            st.metric(row["Algoritm"], f"{row['Timp mediu (s)']:.8f} s")
            st.caption(f"Memorie: {row['Memorie varf (KB)']:.2f} KB")
            st.caption(f"Comparatii: {row['Comparatii medii']:.0f}")

    st.info(output["winner_text"])

    st.write("### Tabel comparativ")
    table_formats = {
        "Timp total (s)": "{:.8f}",
        "Timp mediu (s)": "{:.8f}",
        "Comparatii medii": "{:.2f}",
        "Memorie varf (KB)": "{:.2f}",
    }
    if "Mutari medii" in results_df.columns:
        table_formats["Mutari medii"] = "{:.2f}"

    st.dataframe(
        results_df.style.format(table_formats, na_rep="-"),
        use_container_width=True,
        hide_index=True,
    )

    st.write("### Vizualizare rezultate")
    if current_problem == "Sorting":
        tab_time, tab_operations, tab_memory = st.tabs(["Timp", "Operatii", "Memorie"])
        with tab_time:
            st.altair_chart(
                make_bar_chart(results_df, "Timp mediu (s)", "Timp mediu per rulare", ".8f"),
                use_container_width=True,
            )
        with tab_operations:
            left_chart, right_chart = st.columns(2)
            with left_chart:
                st.altair_chart(
                    make_bar_chart(results_df, "Comparatii medii", "Comparatii medii", ".0f"),
                    use_container_width=True,
                )
            with right_chart:
                st.altair_chart(
                    make_bar_chart(results_df, "Mutari medii", "Mutari medii", ".0f"),
                    use_container_width=True,
                )
        with tab_memory:
            st.altair_chart(
                make_bar_chart(results_df, "Memorie varf (KB)", "Memorie maxima utilizata", ".2f"),
                use_container_width=True,
            )
    else:
        tab_time, tab_operations, tab_memory = st.tabs(["Timp", "Comparatii", "Memorie"])
        with tab_time:
            st.altair_chart(
                make_bar_chart(results_df, "Timp mediu (s)", "Timp mediu per cautare", ".8f"),
                use_container_width=True,
            )
        with tab_operations:
            st.altair_chart(
                make_bar_chart(results_df, "Comparatii medii", "Comparatii medii", ".0f"),
                use_container_width=True,
            )
        with tab_memory:
            st.altair_chart(
                make_bar_chart(results_df, "Memorie varf (KB)", "Memorie maxima utilizata", ".2f"),
                use_container_width=True,
            )

    st.write("### Date utilizate")
    if current_problem == "Searching":
        st.write(f"**Valoarea cautata:** {output['target']}")
    st.write(f"**Primele 20 valori din set:** {output['data'][:20]}")

    st.download_button(
        label="📄 Descarca raportul PDF",
        data=output["pdf_bytes"],
        file_name=f"benchmark_results_{current_problem.lower()}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
