import pandas as pd
import numpy as np


def analyze_dataframe(df: pd.DataFrame) -> dict:

    total_cells = df.shape[0] * df.shape[1]
    missing_total = df.isnull().sum().sum()

    numeric_cols = list(df.select_dtypes(include=[np.number]).columns)

    # Detect date columns
    date_cols = list(df.select_dtypes(include=["datetime64"]).columns)
    for col in df.select_dtypes(include=["object"]).columns:
        sample = df[col].dropna().head(200)
        try:
            parsed = pd.to_datetime(sample, errors="coerce")
            if parsed.notna().mean() > 0.7:
                date_cols.append(col)
        except:
            pass

    categorical_cols = [
        c for c in df.select_dtypes(include=["object"]).columns
        if df[c].nunique() <= 15
    ]

    # Profile
    profile = []
    for col in df.columns:
        profile.append({
            "Column": col,
            "Type": str(df[col].dtype),
            "Unique Values": df[col].nunique(),
            "Missing": df[col].isnull().sum(),
            "Most Common": df[col].mode()[0] if not df[col].mode().empty else None
        })

    # =========================
    # SMART KPI DETECTION
    # =========================
    revenue_col = None
    quantity_col = None

    for col in numeric_cols:
        name = col.lower()

        if any(k in name for k in ["revenue", "sales", "amount", "price"]):
            revenue_col = col

        if any(k in name for k in ["qty", "quantity", "units"]):
            quantity_col = col

    date_col = date_cols[0] if date_cols else None

    return {
        "rows": len(df),
        "cols": len(df.columns),
        "missing_pct": round((missing_total / total_cells) * 100, 2) if total_cells else 0,
        "numeric_cols": numeric_cols,
        "categorical_cols": categorical_cols,
        "date_cols": date_cols,
        "profile": pd.DataFrame(profile),

        # New smart outputs
        "revenue_col": revenue_col,
        "quantity_col": quantity_col,
        "date_col": date_col
    }