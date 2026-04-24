"""
🤖 AGENT 3: Insight Generator Agent
--------------------------------------
This agent is responsible for:
- Receiving analysis results from the Analysis Agent
- Converting numbers into human-readable insights
- Highlighting interesting patterns and anomalies
- Suggesting which charts to display
- Producing a final report for the frontend
"""


class InsightGeneratorAgent:
    """
    The Insight Generator Agent is the final step.
    It takes raw statistics and turns them into plain-English insights
    that anyone (even non-technical users) can understand.
    """

    def __init__(self):
        self.name = "Insight Generator Agent"
        self.log = []

    def _record(self, message):
        """Helper to log each insight step."""
        self.log.append(message)
        print(f"[{self.name}] {message}")

    def run(self, analysis_package: dict) -> dict:
        """
        Main method: converts analysis results into human-readable insights.

        Args:
            analysis_package: dict from AnalysisAgent with all stats

        Returns:
            dict with 'insights' (list of strings) and chart suggestions
        """
        self.log = []
        self._record("Generating insights from analysis results...")

        insights = []
        overview           = analysis_package.get("overview", {})
        numeric_stats      = analysis_package.get("numeric_stats", {})
        categorical_stats  = analysis_package.get("categorical_stats", {})
        correlations       = analysis_package.get("correlations", {})
        trend              = analysis_package.get("trend")

        # ── 1. Dataset overview ──────────────────────────────────────────────
        insights.append(
            f"📊 Your dataset contains {overview.get('total_rows', 0)} rows and "
            f"{overview.get('total_columns', 0)} columns."
        )
        self._record("Added overview insight.")

        # ── 2. Numeric column insights ───────────────────────────────────────
        for col, stats in numeric_stats.items():
            mean   = stats["mean"]
            median = stats["median"]
            std    = stats["std"]
            rng    = stats["range"]

            insight = f"🔢 Column '{col}': average is {mean}, median is {median}."

            # Check for skewness (mean vs median difference)
            if abs(mean - median) > 0.1 * abs(mean + median + 0.001):
                skew_dir = "higher" if mean > median else "lower"
                insight += f" The mean is {skew_dir} than the median, suggesting the data is skewed."

            # Check for high variability
            if mean != 0 and std / abs(mean) > 0.5:
                insight += f" There's high variability (std={std}), meaning values spread widely."

            insights.append(insight)
            self._record(f"Added numeric insight for '{col}'.")

        # ── 3. Categorical column insights ──────────────────────────────────
        for col, stats in categorical_stats.items():
            top     = stats["top_value"]
            count   = stats["top_count"]
            uniques = stats["unique_count"]
            total   = overview.get("total_rows", 1)
            pct     = round((count / total) * 100, 1)

            insights.append(
                f"🏷️ Column '{col}' has {uniques} unique categories. "
                f"The most common value is '{top}', appearing {count} times ({pct}% of data)."
            )
            self._record(f"Added categorical insight for '{col}'.")

        # ── 4. Correlation insights ──────────────────────────────────────────
        if correlations:
            for pair, value in correlations.items():
                direction = "positive" if value > 0 else "negative"
                strength  = "strong" if abs(value) > 0.7 else "moderate"
                insights.append(
                    f"🔗 {strength.capitalize()} {direction} correlation ({value}) found between {pair}. "
                    f"As one increases, the other tends to {'increase' if value > 0 else 'decrease'}."
                )
            self._record(f"Added {len(correlations)} correlation insight(s).")
        else:
            insights.append("🔗 No strong correlations detected between numeric columns.")

        # ── 5. Trend insight ────────────────────────────────────────────────
        if trend:
            col = trend["column"]
            direction = trend["direction"]
            if direction == "upward":
                insights.append(
                    f"📈 Column '{col}' shows an upward trend — values increase toward the end of the dataset."
                )
            elif direction == "downward":
                insights.append(
                    f"📉 Column '{col}' shows a downward trend — values decrease toward the end of the dataset."
                )
            else:
                insights.append(
                    f"➡️ Column '{col}' appears stable — no strong upward or downward trend detected."
                )
            self._record(f"Added trend insight: {direction}.")

        # ── 6. Data quality insight ──────────────────────────────────────────
        orig = analysis_package.get("original_shape")
        final = analysis_package.get("final_shape")
        if orig and final and orig != final:
            removed = orig[0] - final[0]
            insights.append(
                f"🧹 {removed} duplicate or problematic rows were removed during cleaning, "
                f"leaving {final[0]} clean rows."
            )

        # ── 7. Chart suggestions ─────────────────────────────────────────────
        chart_suggestions = []
        numeric_cols     = overview.get("numeric_cols", [])
        categorical_cols = overview.get("categorical_cols", [])

        # Bar chart: best for categorical data
        if categorical_cols and numeric_cols:
            chart_suggestions.append({
                "type":    "bar",
                "x":       categorical_cols[0],
                "y":       numeric_cols[0],
                "title":   f"Bar Chart: {numeric_cols[0].replace('_',' ').title()} by {categorical_cols[0].replace('_',' ').title()}"
            })

        # Line chart: best for showing trends over rows/index
        if numeric_cols:
            chart_suggestions.append({
                "type":    "line",
                "x":       "index",
                "y":       numeric_cols[0],
                "title":   f"Line Chart: {numeric_cols[0].replace('_',' ').title()} Over Records"
            })

        # Second bar chart if multiple numeric columns
        if len(numeric_cols) >= 2:
            chart_suggestions.append({
                "type":    "bar",
                "x":       "index",
                "y":       numeric_cols[1],
                "title":   f"Bar Chart: {numeric_cols[1].replace('_',' ').title()} Distribution"
            })

        self._record(f"Suggested {len(chart_suggestions)} chart(s).")
        self._record("Insight generation complete!")

        return {
            "insights":         insights,
            "chart_suggestions": chart_suggestions,
            "data":             analysis_package["data"],
            "numeric_stats":    numeric_stats,
            "categorical_stats": categorical_stats,
            "overview":         overview,
            "cleaning_log":     analysis_package.get("cleaning_log", []),
            "analysis_log":     analysis_package.get("analysis_log", []),
            "insight_log":      self.log,
        }
