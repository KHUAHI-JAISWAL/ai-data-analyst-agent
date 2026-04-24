"""
🔄 Agent Pipeline
------------------
This module is the "orchestrator" — it connects all three agents
and runs them in sequence, passing data from one to the next.

Flow:
  CSV File
    ↓
  [DataCleaningAgent]  →  clean data
    ↓
  [AnalysisAgent]      →  statistics + trends
    ↓
  [InsightGeneratorAgent]  →  human-readable insights + chart suggestions
    ↓
  Final Result (returned to Flask backend)
"""

import pandas as pd
from agents.cleaning_agent import DataCleaningAgent
from agents.analysis_agent  import AnalysisAgent
from agents.insight_agent   import InsightGeneratorAgent


class AgentPipeline:
    """
    Orchestrates all three agents in sequence.
    Each agent receives the output of the previous one.
    """

    def __init__(self):
        # Instantiate each agent once
        self.cleaner   = DataCleaningAgent()
        self.analyzer  = AnalysisAgent()
        self.insighter = InsightGeneratorAgent()

    def run(self, df: pd.DataFrame) -> dict:
        """
        Run the full pipeline on a DataFrame.

        Args:
            df: Raw pandas DataFrame

        Returns:
            Final result dict from InsightGeneratorAgent
        """
        print("\n" + "="*50)
        print("🚀 AGENT PIPELINE STARTED")
        print("="*50)

        # ── Step 1: Clean ────────────────────────────────
        print("\n--- STEP 1: Data Cleaning ---")
        cleaned_package = self.cleaner.run(df)

        # ── Step 2: Analyse ──────────────────────────────
        print("\n--- STEP 2: Analysis ---")
        analysis_package = self.analyzer.run(cleaned_package)

        # ── Step 3: Generate insights ────────────────────
        print("\n--- STEP 3: Insight Generation ---")
        final_result = self.insighter.run(analysis_package)

        print("\n" + "="*50)
        print("✅ PIPELINE COMPLETE")
        print("="*50 + "\n")

        return final_result
