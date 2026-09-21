import pandas as pd
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal, QThreadPool
from utils.logger import logger
import os
from utils.threads import Worker

class DataManager(QObject):
    data_loaded = pyqtSignal(object)  # Emits the DataFrame when loaded
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.df = None
        self.filtered_df = None
        self.file_path = None
        self.threadpool = QThreadPool()
        
    def _do_load_data(self, file_path):
        logger.info(f"Loading data from {file_path}")
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext == '.csv':
            # Fast CSV reading, low_memory=False to avoid mixed type warnings on large files
            df = pd.read_csv(file_path, low_memory=False)
        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        elif ext == '.parquet':
            df = pd.read_parquet(file_path)
        elif ext == '.feather':
            df = pd.read_feather(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
        
        # Clean Data
        df = self.clean_dataframe(df)
        return df, file_path

    def load_data(self, file_path):
        """Loads data from a file into a Pandas DataFrame."""
        worker = Worker(self._do_load_data, file_path)
        worker.signals.result.connect(self._on_load_success)
        worker.signals.error.connect(self._on_load_error)
        self.threadpool.start(worker)
            
    def _do_load_dataframe(self, df, source_name):
        clean_df = self.clean_dataframe(df.copy())
        return clean_df, source_name

    def load_dataframe(self, df, source_name="SQL Query"):
        """Loads data directly from an existing DataFrame."""
        worker = Worker(self._do_load_dataframe, df, source_name)
        worker.signals.result.connect(self._on_load_success)
        worker.signals.error.connect(self._on_load_error)
        self.threadpool.start(worker)

    def _on_load_success(self, result):
        df, source_name = result
        self.df = df
        self.filtered_df = self.df.copy()
        self.file_path = source_name
        logger.info(f"Successfully loaded {len(self.df)} rows and {len(self.df.columns)} columns.")
        self.data_loaded.emit(self.df)

    def _on_load_error(self, error_tuple):
        exctype, value, tb = error_tuple
        logger.error(f"Error loading data: {str(value)}")
        self.error_occurred.emit(str(value))
            
    def clean_dataframe(self, df):
        """Replaces commas with dots and converts columns to numeric where applicable."""
        # Deduplicate column names to prevent DataFrame indexing issues
        if df.columns.has_duplicates:
            df = df.loc[:, ~df.columns.duplicated()].copy()
            
        for col in df.columns:
            if df[col].dtype == 'object' or pd.api.types.is_string_dtype(df[col]):
                # Vectorized string replace
                # Only operate on actual string objects/cols safely
                s_str = df[col].astype(str)
                s_str = s_str.str.replace(',', '.', regex=False)
                
                # Replace pure whitespace/empty strings with NaN
                s_clean = s_str.replace(r'^\s*$', np.nan, regex=True)
                
                # We need to map back nan correctly. astype(str) casts nan to 'nan'
                s_clean = s_clean.replace('nan', np.nan)
                
                s_numeric = pd.to_numeric(s_clean, errors='coerce')
                
                # If the number of NaNs didn't increase, it means all non-empty strings were valid numbers
                if s_numeric.isna().sum() == s_clean.isna().sum():
                    df[col] = s_numeric
        return df
            
    def get_column_names(self):
        if self.df is not None:
            return self.df.columns.tolist()
        return []
        
    def get_numeric_columns(self):
        if self.df is not None:
            return self.df.select_dtypes(include=[np.number]).columns.tolist()
        return []

    def get_categorical_columns(self):
        if self.df is not None:
            return self.df.select_dtypes(exclude=[np.number]).columns.tolist()
        return []

    # --- Preprocessing Methods ---
    def impute_missing(self, cols, method):
        """Impute missing values in specified columns."""
        if self.df is None or not cols: return
        
        # We perform imputation on self.df
        for col in cols:
            if method == 'Mean':
                if pd.api.types.is_numeric_dtype(self.df[col]):
                    self.df[col] = self.df[col].fillna(self.df[col].mean())
            elif method == 'Median':
                if pd.api.types.is_numeric_dtype(self.df[col]):
                    self.df[col] = self.df[col].fillna(self.df[col].median())
            elif method == 'Mode':
                if not self.df[col].mode().empty:
                    self.df[col] = self.df[col].fillna(self.df[col].mode()[0])
            elif method == 'KNN':
                if pd.api.types.is_numeric_dtype(self.df[col]):
                    from sklearn.impute import KNNImputer
                    imputer = KNNImputer(n_neighbors=5)
                    # Reshape to 2D array for single column imputation
                    col_data = self.df[col].values.reshape(-1, 1)
                    self.df[col] = imputer.fit_transform(col_data)
                    
        # Update filtered df
        if self.filtered_df is not None:
            for col in cols:
                self.filtered_df[col] = self.df.loc[self.filtered_df.index, col]
            
    def scale_columns(self, cols, method):
        """Scale specified numeric columns."""
        if self.df is None or not cols: return
        
        valid_cols = [c for c in cols if pd.api.types.is_numeric_dtype(self.df[c])]
        if not valid_cols: return
        
        if method == 'MinMax':
            from sklearn.preprocessing import MinMaxScaler
            scaler = MinMaxScaler()
            self.df[valid_cols] = scaler.fit_transform(self.df[valid_cols])
        elif method == 'Standard':
            from sklearn.preprocessing import StandardScaler
            scaler = StandardScaler()
            self.df[valid_cols] = scaler.fit_transform(self.df[valid_cols])
            
        if self.filtered_df is not None:
            for col in valid_cols:
                self.filtered_df[col] = self.df.loc[self.filtered_df.index, col]

    def drop_rows(self, indices):
        """Drop specific row indices from the dataframe."""
        if self.df is None or not indices: return
        
        self.df = self.df.drop(index=indices, errors='ignore')
        if self.filtered_df is not None:
            self.filtered_df = self.filtered_df.drop(index=indices, errors='ignore')
