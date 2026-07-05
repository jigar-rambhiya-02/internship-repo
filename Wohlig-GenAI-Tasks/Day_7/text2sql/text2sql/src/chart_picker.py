"""
src/chart_picker.py

Responsibilities:
  1. pick_chart: Ask Groq which chart type best represents the DataFrame's data.
  2. render_chart: Use matplotlib to generate and save a PNG of the chosen chart.

Design decisions:
  - We send column names and dtypes to Groq (not the full data), since chart
    type selection depends on the data structure, not the values.
  - Groq is constrained to return exactly one of: bar, line, pie, scatter, table.
    Open-ended chart type selection leads to hallucinated values like "heatmap"
    or "waterfall" that we don't support.
  - Fallback chain in render_chart:
      pie with >10 unique values → bar (too many slices is unreadable)
      bar with 0 rows → table
      scatter with non-numeric data → table
      any matplotlib exception → table
  - The "table" chart type renders the first 20 rows of the DataFrame using
    matplotlib's table renderer, saved as PNG. This is the universal fallback.
"""

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend — required for server environments
import matplotlib.pyplot as plt
import groq as groq_sdk

from config.settings import (
    GROQ_API_KEY,
    GROQ_MODEL,
    CHART_TEMPERATURE,
    MAX_TOKENS,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Groq client — module-level singleton
_groq_client = groq_sdk.Groq(api_key=GROQ_API_KEY)

# Allowed chart types — constraining the output prevents hallucination
VALID_CHART_TYPES = {"bar", "line", "pie", "scatter", "table"}

# Colour palette for charts — professional, accessible
PALETTE = ["#2563EB", "#16A34A", "#DC2626", "#D97706", "#7C3AED"]


def pick_chart(df: pd.DataFrame) -> str:
    """
    Ask Groq which chart type best fits the DataFrame's structure.

    Sends column names and their data types as a lightweight descriptor.
    This avoids sending actual data values while still giving the LLM
    enough context to make a meaningful chart type decision.

    Args:
        df: The DataFrame containing query results.

    Returns:
        One of: "bar", "line", "pie", "scatter", "table".
        Defaults to "table" if the Groq response is not one of the valid types.
    """
    if df.empty:
        logger.info("DataFrame is empty; defaulting to 'table' chart type.")
        return "table"

    # Build a compact descriptor: "col_name (dtype), ..."
    col_descriptor = ", ".join(
        f"{col} ({str(df[col].dtype)})" for col in df.columns
    )
    row_count = len(df)

    system_prompt = (
        "You are a data visualisation expert. "
        "Given a description of a DataFrame's columns and their types, "
        "and the number of rows, decide which chart type best visualises the data. "
        "Reply with EXACTLY ONE word from this list: bar, line, pie, scatter, table. "
        "Nothing else — no explanation, no punctuation."
    )

    user_prompt = (
        f"DataFrame columns: {col_descriptor}\n"
        f"Number of rows: {row_count}\n\n"
        f"Which chart type is best?"
    )

    logger.info(
        f"Calling Groq API for chart type selection. "
        f"Columns: {col_descriptor}. Rows: {row_count}."
    )

    try:
        response = _groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=CHART_TEMPERATURE,
            max_tokens=10,  # We only need one word
        )

        chart_type = response.choices[0].message.content.strip().lower()

        if chart_type not in VALID_CHART_TYPES:
            logger.warning(
                f"Groq returned unrecognized chart type '{chart_type}'; "
                f"falling back to 'bar'."
            )
            chart_type = "bar"

        logger.info(f"Chart type selected: {chart_type}")
        return chart_type

    except Exception as exc:
        logger.error(f"Groq chart selection API call failed: {exc}. Defaulting to 'table'.")
        return "table"


def render_chart(df: pd.DataFrame, chart_type: str, output_path: str) -> None:
    """
    Render a matplotlib chart of the specified type and save it as PNG.

    Fallback chain:
      - pie with > 10 unique values → bar
      - any chart with empty DataFrame → table
      - any matplotlib exception → table

    Args:
        df: The DataFrame to visualise.
        chart_type: One of "bar", "line", "pie", "scatter", "table".
        output_path: Absolute path where the PNG should be saved.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if df.empty:
        logger.warning("DataFrame is empty; rendering table fallback chart.")
        _render_table(df, output_path, note="(No data returned)")
        return

    # Identify numeric and categorical columns for chart axes
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    non_numeric_cols = df.select_dtypes(exclude=["number"]).columns.tolist()

    logger.info(
        f"Rendering chart type '{chart_type}'. "
        f"Output: {output_path}. "
        f"Shape: {df.shape}."
    )

    try:
        if chart_type == "pie":
            _render_pie(df, non_numeric_cols, numeric_cols, output_path)
        elif chart_type == "bar":
            _render_bar(df, non_numeric_cols, numeric_cols, output_path)
        elif chart_type == "line":
            _render_line(df, non_numeric_cols, numeric_cols, output_path)
        elif chart_type == "scatter":
            _render_scatter(df, numeric_cols, output_path)
        else:
            _render_table(df, output_path)

        logger.info(f"Chart saved successfully: {output_path}")

    except Exception as exc:
        logger.warning(
            f"Chart rendering failed for type '{chart_type}': {exc}. "
            f"Falling back to table chart."
        )
        _render_table(df, output_path, note=f"(Chart rendering failed: {exc})")


# ---------------------------------------------------------------------------
# Internal chart renderers
# ---------------------------------------------------------------------------

def _render_bar(
    df: pd.DataFrame,
    non_numeric_cols: list[str],
    numeric_cols: list[str],
    output_path: str,
) -> None:
    """Render a horizontal bar chart. Uses first categorical col as labels,
    first numeric col as values."""
    fig, ax = plt.subplots(figsize=(10, max(4, len(df) * 0.4)))

    label_col = non_numeric_cols[0] if non_numeric_cols else df.columns[0]
    value_col = numeric_cols[0] if numeric_cols else df.columns[min(1, len(df.columns) - 1)]

    plot_df = df[[label_col, value_col]].head(20)  # Cap at 20 bars for readability
    labels = plot_df[label_col].astype(str)
    values = pd.to_numeric(plot_df[value_col], errors="coerce").fillna(0)

    bars = ax.barh(labels, values, color=PALETTE[0])
    ax.set_xlabel(str(value_col))
    ax.set_title(f"{value_col} by {label_col}", fontsize=13, fontweight="bold")
    ax.bar_label(bars, fmt="%.1f", padding=3, fontsize=8)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _render_line(
    df: pd.DataFrame,
    non_numeric_cols: list[str],
    numeric_cols: list[str],
    output_path: str,
) -> None:
    """Render a line chart. Uses first col as x-axis, first numeric col as y."""
    fig, ax = plt.subplots(figsize=(12, 5))

    x_col = df.columns[0]
    y_col = numeric_cols[0] if numeric_cols else df.columns[min(1, len(df.columns) - 1)]

    x_vals = df[x_col].astype(str)
    y_vals = pd.to_numeric(df[y_col], errors="coerce").fillna(0)

    ax.plot(x_vals, y_vals, marker="o", color=PALETTE[0], linewidth=2, markersize=4)
    ax.set_xlabel(str(x_col))
    ax.set_ylabel(str(y_col))
    ax.set_title(f"{y_col} over {x_col}", fontsize=13, fontweight="bold")
    plt.xticks(rotation=45, ha="right", fontsize=7)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _render_pie(
    df: pd.DataFrame,
    non_numeric_cols: list[str],
    numeric_cols: list[str],
    output_path: str,
) -> None:
    """Render a pie chart. Falls back to bar if too many slices."""
    label_col = non_numeric_cols[0] if non_numeric_cols else df.columns[0]
    value_col = numeric_cols[0] if numeric_cols else df.columns[min(1, len(df.columns) - 1)]

    unique_labels = df[label_col].nunique()
    if unique_labels > 10:
        logger.warning(
            f"Pie chart requested but {unique_labels} unique values in '{label_col}'. "
            f"Falling back to bar chart."
        )
        _render_bar(df, non_numeric_cols, numeric_cols, output_path)
        return

    fig, ax = plt.subplots(figsize=(8, 8))
    labels = df[label_col].astype(str)
    values = pd.to_numeric(df[value_col], errors="coerce").fillna(0)

    ax.pie(
        values,
        labels=labels,
        autopct="%1.1f%%",
        colors=PALETTE * (len(labels) // len(PALETTE) + 1),
        startangle=140,
    )
    ax.set_title(f"Distribution of {value_col}", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _render_scatter(
    df: pd.DataFrame,
    numeric_cols: list[str],
    output_path: str,
) -> None:
    """Render a scatter plot. Requires at least 2 numeric columns."""
    if len(numeric_cols) < 2:
        logger.warning("Scatter requires 2 numeric columns; falling back to table.")
        _render_table(df, output_path, note="(Scatter requires 2 numeric columns)")
        return

    fig, ax = plt.subplots(figsize=(9, 6))
    x_col, y_col = numeric_cols[0], numeric_cols[1]
    x_vals = pd.to_numeric(df[x_col], errors="coerce")
    y_vals = pd.to_numeric(df[y_col], errors="coerce")

    ax.scatter(x_vals, y_vals, color=PALETTE[0], alpha=0.6, edgecolors="white", s=40)
    ax.set_xlabel(str(x_col))
    ax.set_ylabel(str(y_col))
    ax.set_title(f"{y_col} vs {x_col}", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _render_table(
    df: pd.DataFrame,
    output_path: str,
    note: str = "",
) -> None:
    """
    Render the first 20 rows of a DataFrame as a styled table PNG.
    This is the universal fallback when other chart types are unsuitable.
    """
    preview = df.head(20)
    n_rows, n_cols = preview.shape

    fig_height = max(2, n_rows * 0.45 + 1.5)
    fig_width = max(6, n_cols * 2.0)

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.axis("off")

    if preview.empty:
        ax.text(0.5, 0.5, note or "No data", ha="center", va="center", fontsize=12)
    else:
        tbl = ax.table(
            cellText=preview.astype(str).values,
            colLabels=list(preview.columns),
            cellLoc="center",
            loc="center",
        )
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(8)
        tbl.auto_set_column_width(col=list(range(n_cols)))

        # Style header row
        for col_idx in range(n_cols):
            cell = tbl[0, col_idx]
            cell.set_facecolor("#2563EB")
            cell.set_text_props(color="white", fontweight="bold")

    if note:
        fig.text(0.5, 0.01, note, ha="center", fontsize=7, color="grey")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
