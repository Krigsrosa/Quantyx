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
        
        self.plot_widget.scene().sigMouseClicked.connect(self.on_mouse_clicked)
        self.original_drag = self.plot_widget.getViewBox().mouseDragEvent
        self.plot_widget.getViewBox().mouseDragEvent = self.custom_drag_event
        
        self.norm_matrix = None
        self.plot_df_orig = None
        self.valid_cols = []
        self.highlight_curve = None
        self.highlight_text = None
        self.selection_box = None

    def custom_drag_event(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            ev.accept()
            vb = self.plot_widget.getViewBox()
            
            if ev.isStart():
                if getattr(self, 'selection_box', None) is None:
                    from PyQt6.QtWidgets import QGraphicsRectItem
                    self.selection_box = QGraphicsRectItem()
                    self.selection_box.setPen(pg.mkPen('y', width=2, style=Qt.PenStyle.DashLine))
                    self.selection_box.setBrush(pg.mkBrush(255, 255, 0, 50))
                    self.selection_box.setZValue(1e6)
                    self.plot_widget.addItem(self.selection_box)
                self.drag_start_pos = vb.mapSceneToView(ev.buttonDownScenePos())
                
            p1 = getattr(self, 'drag_start_pos', vb.mapSceneToView(ev.buttonDownScenePos()))
            p2 = vb.mapSceneToView(ev.scenePos())
            
            rect = pg.QtCore.QRectF(min(p1.x(), p2.x()), min(p1.y(), p2.y()), 
                                    abs(p2.x() - p1.x()), abs(p2.y() - p1.y()))
            if getattr(self, 'selection_box', None) is not None:
                self.selection_box.setRect(rect)
            
            if ev.isFinish():
                if getattr(self, 'selection_box', None) is not None:
                    self.plot_widget.removeItem(self.selection_box)
                    self.selection_box = None
                self.select_lines_in_rect(rect)
        else:
            self.original_drag(ev)

    def select_lines_in_rect(self, rect):
        if self.norm_matrix is None:
            return
            
        xmin, xmax = rect.left(), rect.right()
        ymin, ymax = rect.top(), rect.bottom()
        
        num_rows, num_cols = self.norm_matrix.shape
        start_c = max(0, int(np.floor(xmin)))
        end_c = min(num_cols - 1, int(np.ceil(xmax)))
        
        selected_mask = np.zeros(num_rows, dtype=bool)
        
        for c in range(start_c, end_c):
            y_c = self.norm_matrix[:, c]
            y_next = self.norm_matrix[:, c+1]
            
            seg_xmin = max(c, xmin)
            seg_xmax = min(c+1, xmax)
            
            if seg_xmin > seg_xmax:
                continue
                
            frac_min = seg_xmin - c
            frac_max = seg_xmax - c
            
            y_at_xmin = y_c + frac_min * (y_next - y_c)
            y_at_xmax = y_c + frac_max * (y_next - y_c)
            
            max_y = np.maximum(y_at_xmin, y_at_xmax)
            min_y = np.minimum(y_at_xmin, y_at_xmax)
            
            intersects = (max_y >= ymin) & (min_y <= ymax)
            selected_mask |= intersects
            
        selected_indices = np.where(selected_mask)[0]
        
        if len(selected_indices) > 0:
            if len(selected_indices) == 1:
                self.highlight_line(selected_indices[0])
            else:
                self.highlight_multiple_lines(selected_indices)
        else:
            self.clear_highlight()

    def highlight_multiple_lines(self, indices):
        self.clear_highlight()
        
        num_cols = self.norm_matrix.shape[1]
        x_template = np.arange(num_cols, dtype=float)
        x_template = np.append(x_template, np.nan)
        
        y_group = np.zeros((num_cols + 1, len(indices)), dtype=float)
        for col_idx in range(num_cols):
            y_group[col_idx, :] = self.norm_matrix[indices, col_idx]
        y_group[-1, :] = np.nan
        
        y_flat = y_group.flatten('F')
        x_flat = np.tile(x_template, len(indices))
        
        pen = pg.mkPen('r', width=3)
        self.highlight_curve = pg.PlotDataItem(x_flat, y_flat, pen=pen, connect='finite')
        self.highlight_curve.setZValue(1000)
        self.plot_widget.addItem(self.highlight_curve)
        
        text = f"{len(indices)} lines selected"
        self.highlight_text = pg.TextItem(text, fill=pg.mkBrush(0, 0, 0, 200), color='w')
        self.highlight_text.setZValue(1001)
        self.highlight_text.setPos(0, 1.05)
        self.plot_widget.addItem(self.highlight_text)

    def on_mouse_clicked(self, ev):
        if ev.button() != Qt.MouseButton.LeftButton:
            return
            
        if self.norm_matrix is None:
            return
            
        vb = self.plot_widget.plotItem.vb
        if not vb.sceneBoundingRect().contains(ev.scenePos()):
            return
            
        pos = vb.mapSceneToView(ev.scenePos())
        mx, my = pos.x(), pos.y()
        
        num_cols = self.norm_matrix.shape[1]
        
        if mx < 0 or mx > num_cols - 1:
            self.clear_highlight()
            return
            
        x0 = int(np.floor(mx))
        x1 = int(np.ceil(mx))
        
        if x0 == x1:
            if x1 < num_cols - 1:
                x1 += 1
            elif x0 > 0:
                x0 -= 1
                
        y0 = self.norm_matrix[:, x0]
        y1 = self.norm_matrix[:, x1]
        
        fraction = mx - x0
        y_interp = y0 + fraction * (y1 - y0)
        
        dist = np.abs(y_interp - my)
        min_idx = np.argmin(dist)
        
        if dist[min_idx] < 0.05:
            self.highlight_line(min_idx)
        else:
            self.clear_highlight()

    def clear_highlight(self):
        if self.highlight_curve:
            self.plot_widget.removeItem(self.highlight_curve)
            self.highlight_curve = None
        if self.highlight_text:
            self.plot_widget.removeItem(self.highlight_text)
            self.highlight_text = None

    def highlight_line(self, idx):
        self.clear_highlight()
            
        y_vals = self.norm_matrix[idx, :]
        x_vals = np.arange(len(y_vals))
        
        pen = pg.mkPen('r', width=4)
        self.highlight_curve = pg.PlotDataItem(x_vals, y_vals, pen=pen)
        self.highlight_curve.setZValue(1000)
        self.plot_widget.addItem(self.highlight_curve)
        
        row_data = self.plot_df_orig.iloc[idx]
        lines = []
        for c in self.valid_cols:
            val = row_data[c]
            lines.append(f"{c}: {val:.4g}" if isinstance(val, (int, float)) else f"{c}: {val}")
            
        # If there's a class column, show it too
        if hasattr(self, 'class_col') and self.class_col and self.class_col in row_data:
            val = row_data[self.class_col]
            lines.insert(0, f"Class ({self.class_col}): {val:.4g}" if isinstance(val, (int, float)) else f"Class ({self.class_col}): {val}")
            
        text = "\n".join(lines)
        
        self.highlight_text = pg.TextItem(text, fill=pg.mkBrush(0, 0, 0, 200), color='w')
        self.highlight_text.setZValue(1001)
        
        # Position slightly to the right of the first point, or left of the last point depending on where clicked
        self.highlight_text.setPos(x_vals[0], y_vals[0])
        self.plot_widget.addItem(self.highlight_text)

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
        
        self.norm_matrix = np.column_stack(norm_data)
        self.plot_df_orig = plot_df.copy()
        self.valid_cols = valid_cols
        self.class_col = class_col if has_class else None
        self.clear_highlight()
        
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
