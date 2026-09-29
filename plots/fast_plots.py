import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QListWidgetItem
import numpy as np
import pandas as pd

class ScatterPlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Pyqtgraph configuration
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.layout.addWidget(self.plot_widget, stretch=1)
        
        self.legend = None
        self.regression_line = None
        
    def _clear_legend(self):
        if self.legend is not None:
            self.plot_widget.removeItem(self.legend)
            self.legend = None
            
    def _clear_regression(self):
        if self.regression_line is not None:
            self.plot_widget.removeItem(self.regression_line)
            self.regression_line = None
            
    def get_discrete_colors(self, num_colors):
        """Generates a list of QColors for categorical data."""
        import matplotlib as mpl
        cmap = mpl.colormaps['tab10']
        colors = []
        for i in range(num_colors):
            rgba = cmap(i % 10)
            colors.append(pg.mkColor(int(rgba[0]*255), int(rgba[1]*255), int(rgba[2]*255), 180))
        return colors
        
    def _clear_limits(self):
        if hasattr(self, 'limit_upper_line') and self.limit_upper_line is not None:
            self.plot_widget.removeItem(self.limit_upper_line)
            self.limit_upper_line = None
        if hasattr(self, 'limit_lower_line') and self.limit_lower_line is not None:
            self.plot_widget.removeItem(self.limit_lower_line)
            self.limit_lower_line = None

    def plot_data(self, df, x_col, y_col, color_col=None, props=None):
        """Plots the scatter data. Very fast even with many points."""
        if x_col not in df.columns or y_col not in df.columns:
            return
            
        if props is None:
            props = {'point_size': 5, 'show_grid': True, 'palette': 'viridis'}
            
        self.plot_widget.showGrid(x=props.get('show_grid', True), y=props.get('show_grid', True), alpha=0.3)
            
        cols_to_extract = [x_col, y_col]
        if color_col and color_col != "None" and color_col in df.columns:
            cols_to_extract.append(color_col)
            
        # Drop NaNs for plotting
        valid_df = df[cols_to_extract].dropna()
        if valid_df.empty:
            self.scatter.clear()
            return
            
        x_data = valid_df[x_col].values
        y_data = valid_df[y_col].values
        
        xl = props.get('custom_xlabel', '') or x_col
        yl = props.get('custom_ylabel', '') or y_col
        
        title = props.get('custom_title', '')
        if not title:
            title = f'{y_col} vs {x_col}'
            if color_col and color_col != "None":
                title += f' (Color: {color_col})'
            
        self.plot_widget.clear()
        
        self.plot_widget.setLabel('bottom', xl)
        self.plot_widget.setLabel('left', yl)
        
        from PyQt6.QtCore import Qt
        
        c_base = props.get('color_base', '#1f77b4')
        c_upper = props.get('color_upper', '#FF0000')
        c_lower = props.get('color_lower', '#FF0000')
        
        if color_col and color_col != "None" and color_col in valid_df.columns:
            unique_cats = valid_df[color_col].unique()
            cat_colors = props.get('cat_colors', {})
            
            self._clear_legend()
            self.legend = self.plot_widget.addLegend(offset=(10, 10))
            
            from PyQt6.QtCore import Qt
            
            for i, cat in enumerate(unique_cats):
                mask = valid_df[color_col] == cat
                hex_color = cat_colors.get(str(cat), '#1f77b4')
                brush = pg.mkBrush(hex_color)
                
                self.plot_widget.plot(valid_df[mask][x_col].values, valid_df[mask][y_col].values, 
                                      pen=None, symbol='o', symbolSize=props.get('point_size', 5), 
                                      symbolBrush=brush, name=str(cat))
        else:
            self._clear_legend()
            
            brush = pg.mkBrush(c_base)
            self.plot_widget.plot(valid_df[x_col].values, valid_df[y_col].values, 
                                  pen=None, symbol='o', symbolSize=props.get('point_size', 5),
                                  symbolBrush=brush)
                                  
        # Limits
        try:
            u_val = float(props.get('limit_upper', ''))
            line = pg.InfiniteLine(pos=u_val, angle=0, pen=pg.mkPen(c_upper, style=Qt.PenStyle.DashLine))
            self.plot_widget.addItem(line)
        except ValueError:
            pass
            
        try:
            l_val = float(props.get('limit_lower', ''))
            line = pg.InfiniteLine(pos=l_val, angle=0, pen=pg.mkPen(c_lower, style=Qt.PenStyle.DashLine))
            self.plot_widget.addItem(line)
        except ValueError:
            pass
        
        if props.get('linear_regression', False):
            if pd.api.types.is_numeric_dtype(df[x_col]) and pd.api.types.is_numeric_dtype(df[y_col]):
                try:
                    from scipy.stats import linregress
                    slope, intercept, r_value, p_value, std_err = linregress(x_data, y_data)
                    
                    x_min, x_max = x_data.min(), x_data.max()
                    line_x = np.array([x_min, x_max])
                    line_y = slope * line_x + intercept
                    
                    from PyQt6.QtCore import Qt
                    self.regression_line = pg.PlotCurveItem(x=line_x, y=line_y, pen=pg.mkPen('r', width=3, style=Qt.PenStyle.DashLine))
                    self.plot_widget.addItem(self.regression_line)
                    
                    sign = "+" if intercept >= 0 else "-"
                    title += f"\nReg: y = {slope:.3g}x {sign} {abs(intercept):.3g}  (R² = {r_value**2:.3g})"
                except Exception as e:
                    from utils.logger import logger
                    logger.error(f"Regression error: {e}")
                    
        self.plot_widget.setTitle(title)
        
        dec_x = props.get('decimals_x', 0)
        dec_y = props.get('decimals_y', 0)
        
        # Override pyqtgraph's tickStrings for formatting
        def fmt_x(values, scale, spacing):
            return [f"{v:.{dec_x}f}" for v in values]
        def fmt_y(values, scale, spacing):
            return [f"{v:.{dec_y}f}" for v in values]
            
        self.plot_widget.getAxis('bottom').tickStrings = fmt_x
        self.plot_widget.getAxis('left').tickStrings = fmt_y
        
        # Auto range
        self.plot_widget.autoRange()
