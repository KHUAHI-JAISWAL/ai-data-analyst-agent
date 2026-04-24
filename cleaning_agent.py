"""
🤖 AGENT 1: Data Cleaning Agent
--------------------------------
This agent is responsible for:
- Receiving raw CSV data
- Detecting and handling missing values
- Removing duplicates
- Standardizing column names
- Passing clean data to the next agent
"""

import pandas as pd


class DataCleaningAgent:
    """
    The Data Cleaning Agent acts as the first step in the pipeline.
    It takes raw data and returns a clean, ready-to-analyze DataFrame.
    """

    def __init__(self):
        self.name = "Data Cleaning Agent"
        self.log = []  # Stores a record of every action taken

    def _record(self, message):
        """Helper to log each cleaning step."""
        self.log.append(message)
        print(f"[{self.name}] {message}")

    def run(self, df: pd.DataFrame) -> dict:
        """
        Main method: receives raw DataFrame, cleans it, returns results.

        Args:
            df: Raw pandas DataFrame from the uploaded CSV

        Returns:
            dict with 'data' (cleaned DataFrame) and 'log' (list of actions taken)
        """
        self._record("Starting data cleaning process...")
        self.log = []  # Reset log for each new run

        original_shape = df.shape
        self._record(f"Received dataset with {original_shape[0]} rows and {original_shape[1]} columns.")

        # Step 1: Clean column names (strip whitespace, lowercase)
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
        self._record("Standardized column names (lowercase, underscores).")

        # Step 2: Remove fully duplicate rows
        duplicates_removed = df.duplicated().sum()
        df = df.drop_duplicates()
        if duplicates_removed > 0:
            self._record(f"Removed {duplicates_removed} duplicate rows.")
        else:
            self._record("No duplicate rows found.")

        # Step 3: Handle missing values
        missing_before = df.isnull().sum().sum()
        if missing_before > 0:
            self._record(f"Found {missing_before} missing values. Filling them now...")

            for col in df.columns:
                missing_in_col = df[col].isnull().sum()
                if missing_in_col == 0:
                    continue

                if df[col].dtype in ['float64', 'int64']:
                    # For numeric columns: fill with median (robust to outliers)
                    fill_value = df[col].median()
                    df[col].fillna(fill_value, inplace=True)
                    self._record(f"  Column '{col}': filled {missing_in_col} missing values with median ({fill_value:.2f}).")
                else:
                    # For text columns: fill with 'Unknown'
                    df[col].fillna("Unknown", inplace=True)
                    self._record(f"  Column '{col}': filled {missing_in_col} missing values with 'Unknown'.")
        else:
            self._record("No missing values found. Dataset is complete!")

        # Step 4: Reset index after cleaning
        df = df.reset_index(drop=True)

        final_shape = df.shape
        self._record(f"Cleaning complete. Final dataset: {final_shape[0]} rows, {final_shape[1]} columns.")

        # Return a package (dict) to pass to the next agent
        return {
            "data": df,
            "log": self.log,
            "original_shape": original_shape,
            "final_shape": final_shape
        }
