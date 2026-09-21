from PyQt6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg
import pandas as pd
import numpy as np
from PyQt6.QtCore import Qt

from plots.stat_plots import get_cat_color

class ParallelPlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.showAxis('right')
        self.plot_widget.hideAxis('left')
        self.plot_widget.getAxis('bottom').setStyle(showValues=False)
        self.plot_widget.getAxis('right').setStyle(showValues=False)
        self.plot_widget.getAxis('top').setStyle(showValues=False)
        self.layout.addWidget(self.plot_widget)

    def plot_data(self, df, selected_cols=None, class_col=None, props=None):
        self.plot_widget.clear()
        
        if props is None:
            props = {}
            
        if not selected_cols or len(selected_cols) < 2:
            return
            
        valid_cols = [c for c in selected_cols if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
        if len(valid_cols) < 2:
            return
            
        cols_to_keep = list(valid_cols)
        has_class = False
        if class_col and class_col != "None" and class_col in df.columns:
            if class_col not in cols_to_keep:
                cols_to_keep.append(class_col)
            has_class = True
            
        plot_df = df[cols_to_keep].dropna().copy()
        if plot_df.empty:
            return
            
        # Cap at 5000 lines for performance in Pyqtgraph
        if len(plot_df) > 5000:
            plot_df = plot_df.sample(5000, random_state=42)
            
        # Normalize the columns between 0 and 1
        norm_data = []
        mins = []
        maxs = []
        for c in valid_cols:
            c_min = plot_df[c].min()
            c_max = plot_df[c].max()
            mins.append(c_min)
            maxs.append(c_max)
            
            rng = c_max - c_min
            if rng == 0:
                norm_data.append(np.zeros(len(plot_df)))
            else:
                norm_data.append(((plot_df[c] - c_min) / rng).values)
                
        num_cols = len(valid_cols)
        num_rows = len(plot_df)
        
        x_template = np.arange(num_cols, dtype=float)
        x_template = np.append(x_template, np.nan)
        
        x_all = np.tile(x_template, num_rows)
        
        groups = {}
        if has_class:
            if pd.api.types.is_numeric_dtype(plot_df[class_col]) and len(plot_df[class_col].unique()) > 10:
                # Continuous color: bin into 10 groups
                plot_df['_bin'] = pd.qcut(plot_df[class_col], q=10, labels=False, duplicates='drop')
                unique_bins = plot_df['_bin'].dropna().unique()
                cmap = pg.colormap.get('plasma')
                for b in unique_bins:
                    idx = np.where(plot_df['_bin'].values == b)[0]
                    color = cmap.map(b / max(1, len(unique_bins)-1))
                    color_rgba = pg.mkColor(color)
                    color_rgba.setAlpha(150)
                    groups[b] = (idx, color_rgba)
            else:
                cats = plot_df[class_col].unique()
                self.plot_widget.addLegend()
                for i, c in enumerate(cats):
                    idx = np.where(plot_df[class_col].values == c)[0]
                    color = get_cat_color(c, props, i)
                    color.setAlpha(150)
                    groups[c] = (idx, color)
        else:
            base_color = pg.mkColor(props.get('color_base', '#1f77b4'))
            base_color.setAlpha(150)
            groups['all'] = (np.arange(num_rows), base_color)
            
        for g_name, (indices, color) in groups.items():
            if len(indices) == 0: continue
            
            y_group = np.zeros((num_cols + 1, len(indices)), dtype=float)
            for col_idx in range(num_cols):
                y_group[col_idx, :] = norm_data[col_idx][indices]
            y_group[-1, :] = np.nan
            
            y_flat = y_group.flatten('F')
            x_flat = np.tile(x_template, len(indices))
            
            pen = pg.mkPen(color, width=1.5)
            name_str = str(g_name) if has_class and len(groups) <= 10 else None
            self.plot_widget.plot(x_flat, y_flat, pen=pen, connect='finite', name=name_str)
            
        plot_item = self.plot_widget.getPlotItem()
        axis_color = plot_item.getAxis('bottom').pen().color()
        
        for i, c in enumerate(valid_cols):
            line = pg.InfiniteLine(pos=i, angle=90, pen=pg.mkPen(axis_color, width=1, style=Qt.PenStyle.DashLine))
            self.plot_widget.addItem(line)
            
            lbl = pg.TextItem(c, anchor=(0.5, 1), color=axis_color)
            lbl.setPos(i, 1.05)
            self.plot_widget.addItem(lbl)
            
            lbl_max = pg.TextItem(f"{maxs[i]:.2g}", anchor=(0, 0.5), color=axis_color)
            lbl_max.setPos(i, 1)
            self.plot_widget.addItem(lbl_max)
            
            lbl_min = pg.TextItem(f"{mins[i]:.2g}", anchor=(0, 0.5), color=axis_color)
            lbl_min.setPos(i, 0)
            self.plot_widget.addItem(lbl_min)

        self.plot_widget.getViewBox().setXRange(-0.5, num_cols - 0.5)
        self.plot_widget.getViewBox().setYRange(-0.1, 1.1)
        
        title = props.get('custom_title', 'Parallel Coordinates')
        self.plot_widget.setTitle(title)
