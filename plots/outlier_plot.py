import pyqtgraph as pg
import numpy as np
import pandas as pd
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSignal

class OutlierPlotWidget(QWidget):
    selection_changed = pyqtSignal(list) # Emits the list of selected DataFrame indices
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground("w")
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.layout.addWidget(self.plot_widget)
        
        self.scatter = pg.ScatterPlotItem(size=8, pen=pg.mkPen(None), brush=pg.mkBrush(50, 150, 255, 120))
        self.scatter.sigClicked.connect(self.on_points_clicked)
        self.plot_widget.addItem(self.scatter)
        
        self.df = None
        self.x_col = None
        self.y_col = None
        
        # We store the dataframe indices mapping for the scatter spots
        self.spot_to_index = []
        self.selected_indices = set()
        self.auto_outlier_indices = set()
        
    def plot_data(self, df, x_col, y_col):
        """Plots the data for outlier selection."""
        self.scatter.clear()
        self.df = df
        self.x_col = x_col
        self.y_col = y_col
        self.spot_to_index = []
        self.selected_indices.clear()
        self.auto_outlier_indices.clear()
        self.selection_changed.emit(list(self.selected_indices.union(self.auto_outlier_indices)))
        
        if df is None or df.empty or not x_col or not y_col:
            return
            
        if x_col not in df.columns or y_col not in df.columns:
            return
            
        # Filter NaNs for plotting
        valid_mask = df[x_col].notna() & df[y_col].notna()
        plot_df = df[valid_mask]
        
        if plot_df.empty: return
        
        x_data = plot_df[x_col].values
        y_data = plot_df[y_col].values
        self.spot_to_index = plot_df.index.tolist()
        
        spots = []
        for i in range(len(x_data)):
            spots.append({
                "pos": (x_data[i], y_data[i]),
                "data": i,
                "brush": pg.mkBrush(50, 150, 255, 150)
            })
            
        self.scatter.addPoints(spots)
        self.plot_widget.setLabel("bottom", x_col)
        self.plot_widget.setLabel("left", y_col)
        
    def on_points_clicked(self, plot, points):
        """Toggles selection state of clicked points."""
        for p in points:
            idx = p.data()
            df_index = self.spot_to_index[idx]
            
            if df_index in self.selected_indices:
                self.selected_indices.remove(df_index)
            else:
                self.selected_indices.add(df_index)
                
        self._update_point_colors()
        self.selection_changed.emit(list(self.selected_indices.union(self.auto_outlier_indices)))
        
    def set_auto_outliers(self, indices):
        """Marks specific DataFrame indices as auto-detected outliers."""
        self.auto_outlier_indices = set(indices)
        self._update_point_colors()
        self.selection_changed.emit(list(self.selected_indices.union(self.auto_outlier_indices)))
        
    def clear_selections(self):
        """Clears both manual and auto selections."""
        self.selected_indices.clear()
        self.auto_outlier_indices.clear()
        self._update_point_colors()
        self.selection_changed.emit([])
        
    def _update_point_colors(self):
        """Updates the brushes of points based on selection and auto-outlier status."""
        brushes = []
        for i, df_index in enumerate(self.spot_to_index):
            if df_index in self.selected_indices:
                brushes.append(pg.mkBrush(255, 100, 0, 200)) # Orange for manual selection
            elif df_index in self.auto_outlier_indices:
                brushes.append(pg.mkBrush(255, 0, 0, 200)) # Red for auto outliers
            else:
                brushes.append(pg.mkBrush(50, 150, 255, 120)) # Default blue
                
        self.scatter.setBrush(brushes)

