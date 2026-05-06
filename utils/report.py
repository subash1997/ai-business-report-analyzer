import pandas as pd


def generate_excel_report(df, analysis, insights):

    file_name = "AI_Report.xlsx"

    with pd.ExcelWriter(file_name, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Raw Data", index=False)
        analysis["profile"].to_excel(writer, sheet_name="Column Profile", index=False)

        pd.DataFrame({
            "Alerts": insights["alerts"],
            "Recommendations": insights["recommendations"]
        }).to_excel(writer, sheet_name="Insights", index=False)

    return file_name