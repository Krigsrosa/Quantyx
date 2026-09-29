import pandas as pd

def export_data(df, file_path):
    """
    Exports the given dataframe to a CSV or Excel file.
    """
    if df is not None and not df.empty:
        if file_path.lower().endswith('.xlsx'):
            df.to_excel(file_path, index=False)
        else:
            df.to_csv(file_path, index=False)
