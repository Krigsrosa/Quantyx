import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTextBrowser
from PyQt6.QtCore import Qt
import pandas as pd
import numpy as np

# Configuration
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

TAB10_COLORS = [
    (31, 119, 180), (255, 127, 14), (44, 160, 44), (214, 39, 40),
    (148, 103, 189), (140, 86, 75), (227, 119, 194), (127, 127, 127),
    (188, 189, 34), (23, 190, 207)
]

def get_color(index, alpha=200):
    r, g, b = TAB10_COLORS[index % len(TAB10_COLORS)]
    return pg.mkColor(r, g, b, alpha)

def get_cat_color(cat_name, props, default_idx=0, alpha=200):
    cat_colors = props.get('cat_colors', {})
    hex_color = cat_colors.get(str(cat_name))
    if hex_color:
        from PyQt6.QtGui import QColor
        c = QColor(hex_color)
        return pg.mkColor(c.red(), c.green(), c.blue(), alpha)
    return get_color(default_idx, alpha)

def configure_plot(plot_widget):
    plot_widget.showAxis('top')
    plot_widget.showAxis('right')
    plot_widget.getAxis('top').setStyle(showValues=False)
    plot_widget.getAxis('right').setStyle(showValues=False)

class FormattedAxisItem(pg.AxisItem):
    def __init__(self, orientation, decimals=2, **kwargs):
        super().__init__(orientation, **kwargs)
        self.decimals = decimals
        self.is_date = False
        
    def tickStrings(self, values, scale, spacing):
        if getattr(self, 'is_date', False):
            import datetime
            strings = []
            for v in values:
                try:
                    strings.append(datetime.datetime.fromtimestamp(v).strftime('%Y-%m-%d'))
                except:
                    strings.append("")
            return strings
        try:
            return [f"{v:.{self.decimals}f}" for v in values]
        except:
            return super().tickStrings(values, scale, spacing)

class HistogramWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Custom axes
        self.axis_x = FormattedAxisItem(orientation='bottom')
        self.axis_y = FormattedAxisItem(orientation='left')
        self.plot_widget = pg.PlotWidget(axisItems={'bottom': self.axis_x, 'left': self.axis_y})
        configure_plot(self.plot_widget)
        
        self.browser = QTextBrowser()
        self.browser.setMaximumWidth(400)
        
        self.splitter.addWidget(self.plot_widget)
        self.splitter.addWidget(self.browser)
        self.splitter.setSizes([700, 300])
        self.layout.addWidget(self.splitter)
        
    def plot_data(self, df, x_col, hue_col=None, props=None):
        self.plot_widget.clear()
        if props is None: props = {}
        
        self.axis_x.decimals = props.get('decimals_x', 2)
        self.axis_y.decimals = props.get('decimals_y', 2)
        
        if not x_col or x_col == "None" or x_col not in df.columns:
            self.browser.setHtml("<h3 style='color:gray; font-family:sans-serif;'>Select a variable in 'X Axis' to see its statistics.</h3>")
            return
            
        data = df[x_col]
        html = f"<div style='font-family:sans-serif; padding:10px;'>"
        html += f"<h2>Stats: <span style='color:#2980b9;'>{x_col}</span></h2>"
        html += "<table border='1' cellspacing='0' cellpadding='8' style='border-collapse: collapse; width:100%;'>"
        
        if pd.api.types.is_numeric_dtype(data):
            stats = {
                "Count": data.count(), "Nulls": data.isna().sum(),
                "Mean": data.mean(), "Median": data.median(),
                "Std Dev": data.std(), "Min": data.min(),
                "25% (Q1)": data.quantile(0.25), "75% (Q3)": data.quantile(0.75),
                "Max": data.max(), "Skew": data.skew(), "Kurtosis": data.kurtosis()
            }
            for k, v in stats.items():
                val_str = f"{v:.5g}" if isinstance(v, (float, np.floating)) else str(v)
                html += f"<tr><td><b>{k}</b></td><td>{val_str}</td></tr>"
        else:
            stats = {
                "Count": data.count(), "Nulls": data.isna().sum(),
                "Unique": data.nunique(), 
                "Top": data.mode().iloc[0] if not data.mode().empty else "N/A",
                "Freq": data.value_counts().iloc[0] if not data.value_counts().empty else "N/A"
            }
            for k, v in stats.items():
                html += f"<tr><td><b>{k}</b></td><td>{v}</td></tr>"
                
            html += "</table><br/><h3>Top Values</h3>"
            html += "<table border='1' cellspacing='0' cellpadding='8' style='border-collapse: collapse; width:100%;'>"
            html += "<tr><th>Value</th><th>Count</th></tr>"
            for val, count in data.value_counts().head(10).items():
                html += f"<tr><td>{val}</td><td>{count}</td></tr>"
        html += "</table></div>"
        self.browser.setHtml(html)
        
        cols = [x_col]
        if hue_col and hue_col != "None" and hue_col in df.columns:
            cols.append(hue_col)
        valid_df = df[cols].dropna()
        if valid_df.empty: return
        
        self.plot_widget.showGrid(x=props.get('show_grid_x', True), y=props.get('show_grid_y', True), alpha=0.3)
        self.plot_widget.setTitle(props.get('custom_title', f'Histogram of {x_col}'))
        self.plot_widget.setLabel('bottom', props.get('custom_xlabel', x_col))
        self.plot_widget.setLabel('left', 'Count')
        
        hue_val = hue_col if hue_col and hue_col != "None" else None
        
        if pd.api.types.is_numeric_dtype(valid_df[x_col]):
            # Numeric histogram
            if hue_val:
                self.plot_widget.addLegend()
                groups = valid_df.groupby(hue_val)
                i = 0
                for name, group in groups:
                    y, x = np.histogram(group[x_col], bins='auto')
                    bg = pg.BarGraphItem(x0=x[:-1], x1=x[1:], height=y, brush=get_cat_color(name, props, i, 150), name=str(name))
                    self.plot_widget.addItem(bg)
                    i += 1
            else:
                y, x = np.histogram(valid_df[x_col], bins='auto')
                bg = pg.BarGraphItem(x0=x[:-1], x1=x[1:], height=y, brush=pg.mkColor(props.get('color_base', '#1f77b4')), alpha=0.7)
                self.plot_widget.addItem(bg)
        else:
            # Categorical histogram (Bar chart basically)
            # Disable formatted axis for categorical
            self.axis_x.tickStrings = lambda values, scale, spacing: [str(v) for v in values]
            if hue_val:
                self.plot_widget.addLegend()
                counts = valid_df.groupby([x_col, hue_val]).size().unstack(fill_value=0)
                cats = list(counts.index)
                x_ticks = [list(enumerate(cats))]
                self.plot_widget.getAxis('bottom').setTicks(x_ticks)
                
                n_hues = len(counts.columns)
                width = 0.8 / n_hues
                for i, hue in enumerate(counts.columns):
                    x_pos = np.arange(len(cats)) + (i - n_hues/2 + 0.5) * width
                    bg = pg.BarGraphItem(x=x_pos, height=counts[hue].values, width=width, brush=get_cat_color(hue, props, i), name=str(hue))
                    self.plot_widget.addItem(bg)
            else:
                counts = valid_df[x_col].value_counts()
                cats = list(counts.index)
                x_ticks = [list(enumerate(cats))]
                self.plot_widget.getAxis('bottom').setTicks(x_ticks)
                bg = pg.BarGraphItem(x=np.arange(len(cats)), height=counts.values, width=0.6, brush=pg.mkColor(props.get('color_base', '#1f77b4')))
                self.plot_widget.addItem(bg)

class BoxPlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.axis_y = FormattedAxisItem(orientation='left')
        self.plot_widget = pg.PlotWidget(axisItems={'left': self.axis_y})
        configure_plot(self.plot_widget)
        self.layout.addWidget(self.plot_widget)
        self.row_header_label = None

    def plot_data(self, df, x_col, y_col, hue_col=None, props=None):
        self.plot_widget.clear()
        if self.row_header_label is not None:
            try:
                self.plot_widget.getPlotItem().layout.removeItem(self.row_header_label)
            except Exception:
                pass
            self.row_header_label.setParentItem(None)
            self.row_header_label.deleteLater()
            self.row_header_label = None
            
        self.plot_widget.getAxis('left').setMinimumWidth(0)
            
        if not y_col or y_col == "None" or y_col not in df.columns: return
        if props is None: props = {}
        
        dec_y = props.get('decimals_y', 2)
        self.axis_y.decimals = dec_y
        
        x_val = x_col if x_col and x_col != "None" else None
        hue_val = hue_col if hue_col and hue_col != "None" else None
        show_xtable = props.get('show_xtable', False)
        box_group_cols = props.get('box_group_cols', [])
        
        x_groups = []
        if show_xtable and box_group_cols:
            x_groups = [c for c in box_group_cols if c in df.columns]
        else:
            if x_val: x_groups.append(x_val)
            if hue_val: x_groups.append(hue_val)
            
        cols = [y_col] + x_groups
        valid_df = df[cols].dropna()
        if valid_df.empty: return
        
        valid_df = valid_df.loc[:, ~valid_df.columns.duplicated()].copy()
        
        self.plot_widget.showGrid(x=props.get('show_grid_x', True), y=props.get('show_grid_y', True), alpha=0.3)
        self.plot_widget.setTitle(props.get('custom_title', f"Box Plot: {y_col}"))
        self.plot_widget.setLabel('left', props.get('custom_ylabel', y_col))
        
        show_means = props.get('show_means', False)
        show_q1 = props.get('show_q1', False)
        show_q3 = props.get('show_q3', False)
        
        import numpy as np
        import pyqtgraph as pg
        
        if show_xtable and x_groups:
            self.plot_widget.setLabel('bottom', '')
            groups = valid_df.groupby(x_groups)
            tick_list = []
            i = 0
            
            for group_keys, data_group in groups:
                if not isinstance(group_keys, tuple): group_keys = (group_keys,)
                data = data_group[y_col].values
                if len(data) == 0: continue
                
                q1, med, q3 = np.percentile(data, [25, 50, 75])
                iqr = q3 - q1
                min_val, max_val = data[data >= q1 - 1.5*iqr].min(), data[data <= q3 + 1.5*iqr].max()
                
                label_parts = [str(val) for val in group_keys]
                tick_list.append((i, "\n".join(label_parts)))
                
                color = pg.mkColor(props.get('color_base', '#1f77b4'))
                box = pg.BarGraphItem(x=[i], y0=[q1], y1=[q3], width=0.6, brush=color, pen='k')
                self.plot_widget.addItem(box)
                self.plot_widget.addItem(pg.PlotDataItem([i-0.3, i+0.3], [med, med], pen=pg.mkPen('k', width=2)))
                self.plot_widget.addItem(pg.PlotDataItem([i, i], [min_val, q1], pen='k'))
                self.plot_widget.addItem(pg.PlotDataItem([i, i], [q3, max_val], pen='k'))
                self.plot_widget.addItem(pg.PlotDataItem([i-0.15, i+0.15], [min_val, min_val], pen='k'))
                self.plot_widget.addItem(pg.PlotDataItem([i-0.15, i+0.15], [max_val, max_val], pen='k'))
                
                outliers = data[(data < min_val) | (data > max_val)]
                if len(outliers) > 0:
                    self.plot_widget.addItem(pg.ScatterPlotItem(x=[i]*len(outliers), y=outliers, size=5, pen=None, brush='k'))
                    
                if show_means:
                    mean_val = np.mean(data)
                    text = pg.TextItem(f"{mean_val:.{dec_y}f}", color=props.get('color_means', '#000000'), anchor=(0, 0.5))
                    text.setPos(i + 0.35, mean_val)
                    self.plot_widget.addItem(text)
                if show_q1:
                    text = pg.TextItem(f"Q1: {q1:.{dec_y}f}", color=props.get('color_q1', '#333333'), anchor=(1, 0.5))
                    text.setPos(i - 0.35, q1)
                    self.plot_widget.addItem(text)
                if show_q3:
                    text = pg.TextItem(f"Q3: {q3:.{dec_y}f}", color=props.get('color_q3', '#333333'), anchor=(1, 0.5))
                    text.setPos(i - 0.35, q3)
                    self.plot_widget.addItem(text)
                i += 1
                
            self.plot_widget.getAxis('bottom').setTicks([tick_list])
            
            header_str = "\n".join([str(c) for c in x_groups])
            from PyQt6.QtWidgets import QGraphicsTextItem
            self.row_header_label = QGraphicsTextItem()
            color_str = self.plot_widget.getAxis('bottom').pen().color().name()
            self.row_header_label.setHtml(f"<div style='text-align: right; color: {color_str}; line-height: 1.0;'>{header_str.replace(chr(10), '<br>')}</div>")
            
            axis = self.plot_widget.getAxis('bottom')
            self.row_header_label.setParentItem(axis)
            rect = self.row_header_label.boundingRect()
            
            tick_offset = axis.style.get('tickTextOffset', 5)
            if isinstance(tick_offset, (list, tuple)):
                tick_offset = tick_offset[1]
                
            y_offset = max(0, axis.style.get('tickLength', 5)) + tick_offset - 3
            self.row_header_label.setPos(-rect.width() - 5, y_offset)
            
            left_axis = self.plot_widget.getAxis('left')
            if left_axis.width() < rect.width() + 15:
                left_axis.setMinimumWidth(rect.width() + 15)
                
        else:
            self.plot_widget.setLabel('bottom', props.get('custom_xlabel', x_val if x_val else ''))
            
            if x_val and hue_val:
                import pandas as pd
                x_series = valid_df[x_val].iloc[:, 0] if isinstance(valid_df[x_val], pd.DataFrame) else valid_df[x_val]
                hue_series = valid_df[hue_val].iloc[:, 0] if isinstance(valid_df[hue_val], pd.DataFrame) else valid_df[hue_val]
                cats_x = list(x_series.dropna().unique())
                cats_hue = list(hue_series.dropna().unique())
                self.plot_widget.addLegend()
                
                n_hues = len(cats_hue)
                width = 0.8 / n_hues
                tick_list = []
                
                for j, hue in enumerate(cats_hue):
                    color = get_cat_color(hue, props, j)
                    for i, cat_x in enumerate(cats_x):
                        data = valid_df[(valid_df[x_val] == cat_x) & (valid_df[hue_val] == hue)][y_col].values
                        if len(data) == 0: continue
                        q1, med, q3 = np.percentile(data, [25, 50, 75])
                        iqr = q3 - q1
                        min_val, max_val = data[data >= q1 - 1.5*iqr].min(), data[data <= q3 + 1.5*iqr].max()
                        
                        x_pos = i + (j - n_hues/2 + 0.5) * width
                        tick_list.append((x_pos, str(cat_x)))
                        
                        box = pg.BarGraphItem(x=[x_pos], y0=[q1], y1=[q3], width=width*0.8, brush=color, pen='k', name=str(hue) if i==0 else None)
                        self.plot_widget.addItem(box)
                        self.plot_widget.addItem(pg.PlotDataItem([x_pos-width*0.4, x_pos+width*0.4], [med, med], pen=pg.mkPen('k', width=2)))
                        self.plot_widget.addItem(pg.PlotDataItem([x_pos, x_pos], [min_val, q1], pen='k'))
                        self.plot_widget.addItem(pg.PlotDataItem([x_pos, x_pos], [q3, max_val], pen='k'))
                        self.plot_widget.addItem(pg.PlotDataItem([x_pos-width*0.2, x_pos+width*0.2], [min_val, min_val], pen='k'))
                        self.plot_widget.addItem(pg.PlotDataItem([x_pos-width*0.2, x_pos+width*0.2], [max_val, max_val], pen='k'))
                        
                        outliers = data[(data < min_val) | (data > max_val)]
                        if len(outliers) > 0:
                            self.plot_widget.addItem(pg.ScatterPlotItem(x=[x_pos]*len(outliers), y=outliers, size=5, pen=None, brush='k'))
                            
                x_ticks = list(enumerate([str(c) for c in cats_x]))
                self.plot_widget.getAxis('bottom').setTicks([x_ticks])
                
            elif x_val or hue_val:
                group_col = x_val if x_val else hue_val
                groups = valid_df.groupby(group_col)
                cats = list(groups.groups.keys())
                x_ticks = list(enumerate([str(c) for c in cats]))
                self.plot_widget.getAxis('bottom').setTicks([x_ticks])
                
                for i, cat in enumerate(cats):
                    data = groups.get_group(cat)[y_col].values
                    if len(data) == 0: continue
                    q1, med, q3 = np.percentile(data, [25, 50, 75])
                    iqr = q3 - q1
                    min_val, max_val = data[data >= q1 - 1.5*iqr].min(), data[data <= q3 + 1.5*iqr].max()
                    
                    color = get_cat_color(cat, props, i) if hue_val else pg.mkColor(props.get('color_base', '#1f77b4'))
                    box = pg.BarGraphItem(x=[i], y0=[q1], y1=[q3], width=0.4, brush=color, pen='k')
                    self.plot_widget.addItem(box)
                    self.plot_widget.addItem(pg.PlotDataItem([i-0.2, i+0.2], [med, med], pen=pg.mkPen('k', width=2)))
                    self.plot_widget.addItem(pg.PlotDataItem([i, i], [min_val, q1], pen='k'))
                    self.plot_widget.addItem(pg.PlotDataItem([i, i], [q3, max_val], pen='k'))
                    self.plot_widget.addItem(pg.PlotDataItem([i-0.1, i+0.1], [min_val, min_val], pen='k'))
                    self.plot_widget.addItem(pg.PlotDataItem([i-0.1, i+0.1], [max_val, max_val], pen='k'))
                    
                    outliers = data[(data < min_val) | (data > max_val)]
                    if len(outliers) > 0:
                        self.plot_widget.addItem(pg.ScatterPlotItem(x=[i]*len(outliers), y=outliers, size=5, pen=None, brush='k'))
                        
                    if show_means:
                        mean_val = np.mean(data)
                        text = pg.TextItem(f"{mean_val:.{dec_y}f}", color=props.get('color_means', '#000000'), anchor=(0, 0.5))
                        text.setPos(i+0.25, mean_val)
                        self.plot_widget.addItem(text)
                    if show_q1:
                        text = pg.TextItem(f"Q1: {q1:.{dec_y}f}", color=props.get('color_q1', '#333333'), anchor=(1, 0.5))
                        text.setPos(i-0.25, q1)
                        self.plot_widget.addItem(text)
                    if show_q3:
                        text = pg.TextItem(f"Q3: {q3:.{dec_y}f}", color=props.get('color_q3', '#333333'), anchor=(1, 0.5))
                        text.setPos(i-0.25, q3)
                        self.plot_widget.addItem(text)
            else:
                data = valid_df[y_col].values
                q1, med, q3 = np.percentile(data, [25, 50, 75])
                iqr = q3 - q1
                min_val, max_val = data[data >= q1 - 1.5*iqr].min(), data[data <= q3 + 1.5*iqr].max()
                
                box = pg.BarGraphItem(x=[0], y0=[q1], y1=[q3], width=0.4, brush=pg.mkColor(props.get('color_base', '#1f77b4')), pen='k')
                self.plot_widget.addItem(box)
                self.plot_widget.addItem(pg.PlotDataItem([-0.2, 0.2], [med, med], pen=pg.mkPen('k', width=2)))
                self.plot_widget.addItem(pg.PlotDataItem([0, 0], [min_val, q1], pen='k'))
                self.plot_widget.addItem(pg.PlotDataItem([0, 0], [q3, max_val], pen='k'))
                self.plot_widget.addItem(pg.PlotDataItem([-0.1, 0.1], [min_val, min_val], pen='k'))
                self.plot_widget.addItem(pg.PlotDataItem([-0.1, 0.1], [max_val, max_val], pen='k'))
                
                outliers = data[(data < min_val) | (data > max_val)]
                if len(outliers) > 0:
                    self.plot_widget.addItem(pg.ScatterPlotItem(x=[0]*len(outliers), y=outliers, size=5, pen=None, brush='k'))
                self.plot_widget.getAxis('bottom').setTicks([[(0, y_col)]])


class CorrelationMatrixWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.plot_widget = pg.PlotWidget()
        configure_plot(self.plot_widget)
        self.layout.addWidget(self.plot_widget)

    def plot_data(self, df, selected_cols=None, props=None):
        self.plot_widget.clear()
        if props is None: props = {}
        
        if selected_cols:
            valid_cols = [c for c in selected_cols if c in df.columns]
            df = df[valid_cols]
            
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty or numeric_df.shape[1] < 2: return
        
        corr = numeric_df.corr(method='pearson').values
        cols = list(numeric_df.columns)
        
        img = pg.ImageItem(corr)
        try:
            colormap = pg.colormap.get(props.get('palette', 'plasma'), source='matplotlib')
        except:
            colormap = pg.colormap.get('plasma', source='matplotlib')
        img.setColorMap(colormap)
        self.plot_widget.addItem(img)
        
        dec_x = props.get('decimals_x', 2)
        dec_y = props.get('decimals_y', 2)
        mean_val = np.nanmean(corr)
        for i in range(corr.shape[0]):
            for j in range(corr.shape[1]):
                val = corr[i, j]
                color = 'w' if val < mean_val else 'k'
                text = pg.TextItem(f"{val:.{dec_y}f}", color=color, anchor=(0.5, 0.5))
                text.setPos(i + 0.5, j + 0.5)
                self.plot_widget.addItem(text)
        
        self.plot_widget.getAxis('bottom').setTicks([list(enumerate(cols))])
        self.plot_widget.getAxis('left').setTicks([list(enumerate(cols))])
        self.plot_widget.setTitle(props.get('custom_title', 'Correlation Matrix'))

class BarPlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.axis_y = FormattedAxisItem(orientation='left')
        self.plot_widget = pg.PlotWidget(axisItems={'left': self.axis_y})
        configure_plot(self.plot_widget)
        self.layout.addWidget(self.plot_widget)

    def plot_data(self, df, x_col, y_col, hue_col=None, props=None):
        self.plot_widget.clear()
        if not x_col or x_col == "None" or x_col not in df.columns: return
        if props is None: props = {}
        
        self.axis_y.decimals = props.get('decimals_y', 2)
        
        cols = [x_col]
        hue_val = hue_col if hue_col and hue_col != "None" else None
        y_val = y_col if y_col and y_col != "None" else None
        if hue_val and hue_val in df.columns: cols.append(hue_val)
        if y_val and y_val in df.columns: cols.append(y_val)
            
        valid_df = df[cols].dropna()
        if valid_df.empty: return
        
        self.plot_widget.showGrid(x=props.get('show_grid_x', False), y=props.get('show_grid_y', True), alpha=0.3)
        self.plot_widget.setTitle(props.get('custom_title', 'Bar Plot'))
        self.plot_widget.setLabel('bottom', props.get('custom_xlabel', x_col))
        self.plot_widget.setLabel('left', props.get('custom_ylabel', y_val if y_val else 'Count'))
        
        if hue_val:
            self.plot_widget.addLegend()
            if y_val:
                counts = valid_df.groupby([x_col, hue_val])[y_val].mean().unstack()
            else:
                counts = valid_df.groupby([x_col, hue_val]).size().unstack()
                
            cats = list(counts.index)
            self.plot_widget.getAxis('bottom').setTicks([list(enumerate(cats))])
            
            n_hues = len(counts.columns)
            width = 0.8 / n_hues
            for i, hue in enumerate(counts.columns):
                x_pos = np.arange(len(cats)) + (i - n_hues/2 + 0.5) * width
                bg = pg.BarGraphItem(x=x_pos, height=counts[hue].fillna(0).values, width=width, brush=get_cat_color(hue, props, i), name=str(hue))
                self.plot_widget.addItem(bg)
        else:
            if y_val:
                counts = valid_df.groupby(x_col)[y_val].mean()
            else:
                counts = valid_df[x_col].value_counts()
                
            cats = list(counts.index)
            self.plot_widget.getAxis('bottom').setTicks([list(enumerate(cats))])
            bg = pg.BarGraphItem(x=np.arange(len(cats)), height=counts.values, width=0.6, brush=pg.mkColor(props.get('color_base', '#1f77b4')))
            self.plot_widget.addItem(bg)

class LinePlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.axis_x = FormattedAxisItem(orientation='bottom')
        self.axis_y = FormattedAxisItem(orientation='left')
        self.plot_widget = pg.PlotWidget(axisItems={'bottom': self.axis_x, 'left': self.axis_y})
        configure_plot(self.plot_widget)
        self.layout.addWidget(self.plot_widget)

    def plot_data(self, df, x_col, y_col, hue_col=None, props=None):
        self.plot_widget.clear()
        if not x_col or x_col == "None" or x_col not in df.columns: return
        if not y_col or y_col == "None" or y_col not in df.columns: return
        if props is None: props = {}
        
        self.axis_x.decimals = props.get('decimals_x', 2)
        self.axis_y.decimals = props.get('decimals_y', 2)
        
        cols = [x_col, y_col]
        hue_val = hue_col if hue_col and hue_col != "None" else None
        if hue_val and hue_val in df.columns: cols.append(hue_val)
            
        valid_df = df[cols].dropna().sort_values(by=x_col)
        if valid_df.empty: return
        
        is_date = pd.api.types.is_datetime64_any_dtype(valid_df[x_col])
        if not pd.api.types.is_numeric_dtype(valid_df[x_col]) and not is_date:
            try:
                valid_df[x_col] = pd.to_datetime(valid_df[x_col])
                is_date = True
            except: pass
            
        self.axis_x.is_date = is_date
        
        if is_date:
            x_data = valid_df[x_col].astype('int64').to_numpy() // 10**9 # seconds for pyqtgraph
        else:
            x_data = valid_df[x_col].to_numpy()
            
        self.plot_widget.showGrid(x=props.get('show_grid_x', True), y=props.get('show_grid_y', True), alpha=0.3)
        self.plot_widget.setTitle(props.get('custom_title', f"Line Plot: {y_col} over {x_col}"))
        self.plot_widget.setLabel('bottom', props.get('custom_xlabel', x_col))
        self.plot_widget.setLabel('left', props.get('custom_ylabel', y_col))
        
        if hue_val:
            self.plot_widget.addLegend()
            groups = valid_df.groupby(hue_val)
            i = 0
            for name, group in groups:
                if is_date:
                    gx = group[x_col].astype('int64').to_numpy() // 10**9
                else:
                    gx = group[x_col].values
                color = get_cat_color(name, props, i)
                self.plot_widget.plot(gx, group[y_col].values, pen=pg.mkPen(color, width=2), symbol='o', symbolBrush=color, name=str(name))
                i += 1
        else:
            self.plot_widget.plot(x_data, valid_df[y_col].values, pen=pg.mkPen(props.get('color_base', '#1f77b4'), width=2), symbol='o', symbolBrush=props.get('color_base', '#1f77b4'))