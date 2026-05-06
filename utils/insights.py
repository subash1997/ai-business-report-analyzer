import pandas as pd


def generate_insights(df: pd.DataFrame, analysis: dict):

    alerts = []
    recommendations = []

    missing_pct = analysis["missing_pct"]
    num_cols = analysis["numeric_cols"]

    primary_num = num_cols[0] if num_cols else None

    # Data quality
    if missing_pct > 20:
        alerts.append("🔴 High missing data")
        recommendations.append("Clean dataset before analysis")
    elif missing_pct > 5:
        alerts.append("🟡 Moderate missing data")
    else:
        alerts.append("🟢 Data quality is good")

    # Volatility
    if primary_num and df[primary_num].mean() != 0:
        cv = df[primary_num].std() / df[primary_num].mean()
        if cv > 1:
            alerts.append("🔴 High volatility detected")
            recommendations.append("Investigate outliers")

    if not recommendations:
        recommendations.append("Build dashboards for deeper insights")

    summary = f"""
    Dataset has {analysis['rows']} rows with {missing_pct}% missing data.
    Business signals indicate stable performance with optimization opportunities.
    """

    return {
        "alerts": alerts,
        "recommendations": recommendations,
        "summary": summary.strip()
    }


def generate_narrative(insights):

    return f"""
{insights['summary']}

Key insights: {' '.join(insights['alerts'])}

Recommended actions: {' '.join(insights['recommendations'])}
"""