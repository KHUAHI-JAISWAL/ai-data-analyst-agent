"""
📊 Chart Generator
-------------------
Generates charts using matplotlib and saves them as PNG files.
Charts are served by Flask as static files to the frontend.
"""

import os
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd

# ✅ Absolute path for charts folder (IMPORTANT for deployment)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHARTS_DIR = os.path.join(BASE_DIR, "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

# 🎨 Colors
PALETTE = ["#6C63FF", "#FF6584", "#43B89C", "#FFB347", "#74B9FF", "#A29BFE"]


# ─────────────────────────────────────────────────────────
def _apply_style(ax, title):
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


# ─────────────────────────────────────────────────────────
def generate_bar_chart(df, suggestion, filename):
    fig, ax = plt.subplots()

    x_col = suggestion["x"]
    y_col = suggestion["y"]

    if x_col == "index":
        x_vals = list(range(len(df)))
        y_vals = df[y_col].tolist()
        labels = [str(i) for i in x_vals]
    else:
        grouped = df.groupby(x_col)[y_col].mean()
        labels = grouped.index.astype(str)
        y_vals = grouped.values

    ax.bar(labels, y_vals, color=PALETTE[0])

    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    _apply_style(ax, suggestion["title"])

    # ✅ SAVE USING ABSOLUTE PATH
    path = os.path.join(CHARTS_DIR, filename)
    plt.savefig(path)
    plt.close()

    return filename


# ─────────────────────────────────────────────────────────
def generate_line_chart(df, suggestion, filename):
    fig, ax = plt.subplots()

    y_col = suggestion["y"]
    series = df[y_col].reset_index(drop=True)

    ax.plot(series, color=PALETTE[1])

    ax.set_xlabel("Index")
    ax.set_ylabel(y_col)
    _apply_style(ax, suggestion["title"])

    # ✅ SAVE USING ABSOLUTE PATH
    path = os.path.join(CHARTS_DIR, filename)
    plt.savefig(path)
    plt.close()

    return filename


# ─────────────────────────────────────────────────────────
def generate_charts(df, chart_suggestions):
    saved = []

    for i, suggestion in enumerate(chart_suggestions):
        filename = f"chart_{i+1}_{suggestion['type']}.png"
        chart_type = suggestion.get("type", "bar")

        try:
            if chart_type == "bar":
                generate_bar_chart(df, suggestion, filename)
            elif chart_type == "line":
                generate_line_chart(df, suggestion, filename)

            saved.append(filename)
            print(f"[ChartGenerator] Saved: {filename}")

        except Exception as e:
            print(f"[ChartGenerator] Error: {e}")

    return saved