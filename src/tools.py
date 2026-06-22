import pandas as pd
import json
from langchain_core.tools import tool
from ydata_profiling import ProfileReport
from pathlib import Path
import re

@tool
def load_and_profile_csv(file_path: str) -> str:
    """Load CSV and generate detailed profile report."""
    try:
        df = pd.read_csv(file_path)
        profile_summary = {
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "duplicate_rows": int(df.duplicated().sum()),
            "numeric_stats": df.describe(include='all').to_dict() if not df.empty else {}
        }
        
        report_path = Path("reports/profile_report.html")
        report_path.parent.mkdir(exist_ok=True)
        prof = ProfileReport(df, minimal=True, title="Data Profile Report")
        prof.to_file(report_path)
        
        return json.dumps(profile_summary, indent=2, default=str)
    except Exception as e:
        return f"Error loading file: {str(e)}"


@tool
def clean_data(file_path: str) -> str:
    """Advanced data cleaning for cafe sales dataset."""
    try:
        df = pd.read_csv(file_path)
        original_shape = df.shape
        
        # Convert to lowercase and strip spaces
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip().str.lower()
        
        # Replace common dirty values
        dirty_values = ['error', 'unknown', 'nan', 'none', '', ' ']
        for col in df.columns:
            df[col] = df[col].replace(dirty_values, pd.NA)
        
        # Fill missing values
        numeric_cols = df.select_dtypes(include=['number']).columns
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
        
        object_cols = df.select_dtypes(include=['object']).columns
        for col in object_cols:
            df[col] = df[col].fillna("unknown")
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Save cleaned file
        cleaned_path = Path("data/cleaned/cleaned_data.csv")
        cleaned_path.parent.mkdir(exist_ok=True)
        df.to_csv(cleaned_path, index=False)
        
        return f"""✅ Advanced Cleaning Completed!
Original: {original_shape}
After cleaning: {df.shape}
Actions: Standardized text, handled 'error'/'unknown', filled missing values, removed duplicates."""
    except Exception as e:
        return f"❌ Cleaning error: {str(e)}"


@tool
def generate_eda_summary(profile: str) -> str:
    """Generate a rich, professional EDA summary using the LLM."""
    # This tool now just returns a placeholder. The real summary is generated in agent.py
    return "Summary generation triggered."