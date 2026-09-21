from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser
import pandas as pd
import numpy as np

class DescriptiveStatsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.browser = QTextBrowser()
        self.layout.addWidget(self.browser)
        
    def plot_data(self, df, col):
        if not col or col == "None" or col not in df.columns:
            self.browser.setHtml("<h3 style='color:gray; font-family:sans-serif;'>Select a variable in 'X Axis' to see its statistics.</h3>")
            return
            
        data = df[col]
        
        # Build HTML
        html = f"<div style='font-family:sans-serif; padding:10px;'>"
        html += f"<h2>Descriptive Statistics for: <span style='color:#2980b9;'>{col}</span></h2>"
        html += "<table border='1' cellspacing='0' cellpadding='8' style='border-collapse: collapse; width:100%; max-width:500px;'>"
        
        if pd.api.types.is_numeric_dtype(data):
            stats = {
                "Count (Non-Null)": data.count(),
                "Missing (Nulls)": data.isna().sum(),
                "Mean": data.mean(),
                "Median": data.median(),
                "Std Deviation": data.std(),
                "Variance": data.var(),
                "Min": data.min(),
                "25% (Q1)": data.quantile(0.25),
                "50% (Q2)": data.median(),
                "75% (Q3)": data.quantile(0.75),
                "Max": data.max(),
                "Skewness": data.skew(),
                "Kurtosis": data.kurtosis()
            }
            
            for k, v in stats.items():
                if isinstance(v, (float, np.floating)):
                    val_str = f"{v:.6g}"
                else:
                    val_str = str(v)
                html += f"<tr><td><b>{k}</b></td><td>{val_str}</td></tr>"
                
        else:
            stats = {
                "Count (Non-Null)": data.count(),
                "Missing (Nulls)": data.isna().sum(),
                "Unique Values": data.nunique(),
                "Top (Most Frequent)": data.mode().iloc[0] if not data.mode().empty else "N/A",
                "Freq (Top Value)": data.value_counts().iloc[0] if not data.value_counts().empty else "N/A"
            }
            
            for k, v in stats.items():
                html += f"<tr><td><b>{k}</b></td><td>{v}</td></tr>"
                
            html += "</table><br/><h3>Top 10 Values Frequency</h3>"
            html += "<table border='1' cellspacing='0' cellpadding='8' style='border-collapse: collapse; width:100%; max-width:500px;'>"
            html += "<tr><th>Value</th><th>Count</th></tr>"
            val_counts = data.value_counts().head(10)
            for val, count in val_counts.items():
                html += f"<tr><td>{val}</td><td>{count}</td></tr>"
                
        html += "</table></div>"
        self.browser.setHtml(html)
