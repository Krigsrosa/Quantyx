import pandas as pd

def export_data(df, file_path):
    """
    Exports the given dataframe to a CSV file.
    """
    if df is not None and not df.empty:
        df.to_csv(file_path, index=False)
