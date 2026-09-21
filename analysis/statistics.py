import pandas as pd
import numpy as np

def calculate_pearson_correlation(df):
    """
    Stub for correlation calculation.
    In the future, this will run in a separate thread and return the correlation matrix.
    """
    if df is not None:
        numeric_df = df.select_dtypes(include=[np.number])
        return numeric_df.corr(method='pearson')
    return None
