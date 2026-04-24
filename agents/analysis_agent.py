"""
🤖 AGENT 2: Analysis Agent
---------------------------
This agent is responsible for:
- Receiving clean data from the Cleaning Agent
- Calculating statistics (mean, median, std, etc.)
- Identifying numeric and categorical columns
- Detecting trends and correlations
- Passing analysis results to the Insight Generator Agent
"""

import pandas as pd
import numpy as np


class AnalysisAgent:
    """
    The Analysis Agent performs all statistical computations.
    It figures out what kind of data each column contains
    and applies the appropriate analysis.
    """

    def __init__(self):
        self.name = "Analysis Agent"
        self.log = []

    def _record(self, message):
        """Helper to log each analysis step."""
        self.log.append(message)
        print(f"[{self.name}] {message}")

    def run(self, cleaned_package: dict) -> dict:
        """
        Main method: receives clean data package, runs analysis.

        Args:
            cleaned_package: dict from DataCleaningAgent containing 'data' and 'log'

        Returns:
            dict with all analysis results, plus original package data
        """
        self.log = []
        df = cleaned_package["data"]
        self._record("Starting analysis...")

        # Separate columns by data type
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

        self._record(f"Found {len(numeric_cols)} numeric columns: {numeric_cols}")
        self._record(f"Found {len(categorical_cols)} categorical columns: {categorical_cols}")

        # === NUMERIC ANALYSIS ===
        numeric_stats = {}
        if numeric_cols:
            for col in numeric_cols:
                stats = {
                    "mean":   round(df[col].mean(), 2),
                    "median": round(df[col].median(), 2),
                    "std":    round(df[col].std(), 2),
                    "min":    round(df[col].min(), 2),
                    "max":    round(df[col].max(), 2),
                    "range":  round(df[col].max() - df[col].min(), 2),
                }
                numeric_stats[col] = stats
                self._record(f"  '{col}' → mean={stats['mean']}, median={stats['median']}, std={stats['std']}")

        # === CATEGORICAL ANALYSIS ===
        categorical_stats = {}
        if categorical_cols:
            for col in categorical_cols:
                value_counts = df[col].value_counts()
                categorical_stats[col] = {
                    "unique_count": df[col].nunique(),
                    "top_value":    value_counts.index[0] if len(value_counts) > 0 else "N/A",
                    "top_count":    int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                    "value_counts": value_counts.head(10).to_dict()  # Top 10 categories
                }
                self._record(f"  '{col}' → {categorical_stats[col]['unique_count']} unique values, most common: '{categorical_stats[col]['top_value']}'")

        # === CORRELATION ANALYSIS (numeric only) ===
        correlations = {}
        if len(numeric_cols) >= 2:
            corr_matrix = df[numeric_cols].corr()
            # Find strong correlations (absolute value > 0.5, not self-correlation)
            for i in range(len(numeric_cols)):
                for j in range(i + 1, len(numeric_cols)):
                    col_a = numeric_cols[i]
                    col_b = numeric_cols[j]
                    corr_value = round(corr_matrix.loc[col_a, col_b], 2)
                    if abs(corr_value) > 0.5:
                        correlations[f"{col_a} vs {col_b}"] = corr_value
                        self._record(f"  Strong correlation: '{col_a}' & '{col_b}' = {corr_value}")

        # === TREND DETECTION (for first numeric column as a proxy) ===
        trend = None
        if numeric_cols:
            first_num_col = numeric_cols[0]
            series = df[first_num_col].dropna()
            if len(series) > 1:
                # Simple linear trend: compare first half avg vs second half avg
                mid = len(series) // 2
                first_half_mean = series.iloc[:mid].mean()
                second_half_mean = series.iloc[mid:].mean()
                if second_half_mean > first_half_mean * 1.05:
                    trend = {"column": first_num_col, "direction": "upward", "change": round(second_half_mean - first_half_mean, 2)}
                elif second_half_mean < first_half_mean * 0.95:
                    trend = {"column": first_num_col, "direction": "downward", "change": round(first_half_mean - second_half_mean, 2)}
                else:
                    trend = {"column": first_num_col, "direction": "stable", "change": 0}
                self._record(f"  Trend for '{first_num_col}': {trend['direction']}")

        # === DATASET OVERVIEW ===
        overview = {
            "total_rows":    len(df),
            "total_columns": len(df.columns),
            "numeric_cols":  numeric_cols,
            "categorical_cols": categorical_cols,
            "column_names":  df.columns.tolist(),
        }

        self._record("Analysis complete!")

        # Pass everything forward to the Insight Agent
        return {
            "data":               df,
            "overview":           overview,
            "numeric_stats":      numeric_stats,
            "categorical_stats":  categorical_stats,
            "correlations":       correlations,
            "trend":              trend,
            "cleaning_log":       cleaned_package.get("log", []),
            "analysis_log":       self.log,
        }
