from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSpinBox, QCheckBox, 
                             QComboBox, QHBoxLayout, QLineEdit, QGroupBox, QFormLayout)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QPushButton, QColorDialog
from PyQt6.QtGui import QColor

class ColorPickerButton(QPushButton):
    colorChanged = pyqtSignal(str)
    
    def __init__(self, color="#000000", parent=None):
        super().__init__(parent)
        self.setFixedSize(24, 24)
        self.color = color
        self.update_style()
        self.clicked.connect(self.pick_color)
        
    def update_style(self):
        self.setStyleSheet(f"background-color: {self.color}; border: 1px solid gray; border-radius: 4px;")
        
    def pick_color(self):
        color = QColorDialog.getColor(QColor(self.color), self)
        if color.isValid():
            self.color = color.name()
            self.update_style()
            self.colorChanged.emit(self.color)

class PropertiesPanel(QWidget):
    properties_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # 1. Custom Labels & Titles
        group_labels = QGroupBox("Labels & Titles")
        form_labels = QFormLayout(group_labels)
        
        self.edit_title = QLineEdit()
        self.edit_title.setPlaceholderText("Auto")
        self.edit_title.editingFinished.connect(self.emit_changes)
        
        self.edit_xlabel = QLineEdit()
        self.edit_xlabel.setPlaceholderText("Auto")
        self.edit_xlabel.editingFinished.connect(self.emit_changes)
        
        self.edit_ylabel = QLineEdit()
        self.edit_ylabel.setPlaceholderText("Auto")
        self.edit_ylabel.editingFinished.connect(self.emit_changes)
        
        self.form_labels = form_labels
        self.form_labels.addRow("Title:", self.edit_title)
        self.form_labels.addRow("X Axis:", self.edit_xlabel)
        self.form_labels.addRow("Y Axis:", self.edit_ylabel)
        self.layout.addWidget(group_labels)
        
        # Limits & Colors
        group_limits = QGroupBox("Limits & Colors")
        form_limits = QFormLayout(group_limits)
        
        # Base Color
        self.color_base = ColorPickerButton("#1f77b4")
        self.color_base.colorChanged.connect(self.emit_changes)
        
        self.edit_upper = QLineEdit()
        self.edit_upper.setPlaceholderText("e.g., 980")
        self.edit_upper.editingFinished.connect(self.emit_changes)
        self.color_upper = ColorPickerButton("#FF0000")
        self.color_upper.colorChanged.connect(self.emit_changes)
        
        self.w_upper = QWidget()
        upper_layout = QHBoxLayout(self.w_upper)
        upper_layout.setContentsMargins(0, 0, 0, 0)
        upper_layout.addWidget(self.edit_upper)
        upper_layout.addWidget(self.color_upper)
        
        self.edit_lower = QLineEdit()
        self.edit_lower.setPlaceholderText("e.g., 700")
        self.edit_lower.editingFinished.connect(self.emit_changes)
        self.color_lower = ColorPickerButton("#FF0000")
        self.color_lower.colorChanged.connect(self.emit_changes)
        
        self.w_lower = QWidget()
        lower_layout = QHBoxLayout(self.w_lower)
        lower_layout.setContentsMargins(0, 0, 0, 0)
        lower_layout.addWidget(self.edit_lower)
        lower_layout.addWidget(self.color_lower)
        
        # Means
        self.chk_means = QCheckBox("Show Means")
        self.chk_means.toggled.connect(self.emit_changes)
        self.color_means = ColorPickerButton("#000000")
        self.color_means.colorChanged.connect(self.emit_changes)
        self.w_means = QWidget()
        means_layout = QHBoxLayout(self.w_means)
        means_layout.setContentsMargins(0, 0, 0, 0)
        means_layout.addWidget(self.chk_means)
        means_layout.addStretch()
        means_layout.addWidget(self.color_means)
        
        # Q1
        self.chk_q1 = QCheckBox("Show Q1 (Lower Box)")
        self.chk_q1.toggled.connect(self.emit_changes)
        self.color_q1 = ColorPickerButton("#333333")
        self.color_q1.colorChanged.connect(self.emit_changes)
        self.w_q1 = QWidget()
        q1_layout = QHBoxLayout(self.w_q1)
        q1_layout.setContentsMargins(0, 0, 0, 0)
        q1_layout.addWidget(self.chk_q1)
        q1_layout.addStretch()
        q1_layout.addWidget(self.color_q1)
        
        # Q3
        self.chk_q3 = QCheckBox("Show Q3 (Upper Box)")
        self.chk_q3.toggled.connect(self.emit_changes)
        self.color_q3 = ColorPickerButton("#333333")
        self.color_q3.colorChanged.connect(self.emit_changes)
        self.w_q3 = QWidget()
        q3_layout = QHBoxLayout(self.w_q3)
        q3_layout.setContentsMargins(0, 0, 0, 0)
        q3_layout.addWidget(self.chk_q3)
        q3_layout.addStretch()
        q3_layout.addWidget(self.color_q3)
        
        self.chk_xtable = QCheckBox("Show X-Axis Data Table")
        self.chk_xtable.toggled.connect(self.emit_changes)
        
        self.spin_decimals_x = QSpinBox()
        self.spin_decimals_x.setRange(0, 10)
        self.spin_decimals_x.setValue(0)
        self.spin_decimals_x.valueChanged.connect(self.emit_changes)
        
        self.spin_decimals_y = QSpinBox()
        self.spin_decimals_y.setRange(0, 10)
        self.spin_decimals_y.setValue(0)
        self.spin_decimals_y.valueChanged.connect(self.emit_changes)
        
        self.form_limits = form_limits
        self.form_limits.addRow("Horizontal Upper Limit:", self.w_upper)
        self.form_limits.addRow("Horizontal Lower Limit:", self.w_lower)
        self.form_limits.addRow("Decimals X:", self.spin_decimals_x)
        self.form_limits.addRow("Decimals Y:", self.spin_decimals_y)
        self.form_limits.addRow("", self.w_means)
        self.form_limits.addRow("", self.w_q1)
        self.form_limits.addRow("", self.w_q3)
        self.form_limits.addRow("", self.chk_xtable)
        self.layout.addWidget(group_limits)
        
        # 3. Aesthetics
        group_aes = QGroupBox("Aesthetics")
        aes_layout = QVBoxLayout(group_aes)
        
        # Point Size
        size_layout = QHBoxLayout()
        self.lbl_point_size = QLabel("Point Size:")
        size_layout.addWidget(self.lbl_point_size)
        self.spin_size = QSpinBox()
        self.spin_size.setRange(1, 50)
        self.spin_size.setValue(5)
        self.spin_size.valueChanged.connect(self.emit_changes)
        size_layout.addWidget(self.spin_size)
        aes_layout.addLayout(size_layout)
        
        # Grid Toggle
        grid_layout = QHBoxLayout()
        self.chk_grid_x = QCheckBox("Grid X")
        self.chk_grid_x.setChecked(True)
        self.chk_grid_x.toggled.connect(self.emit_changes)
        grid_layout.addWidget(self.chk_grid_x)
        
        self.chk_grid_y = QCheckBox("Grid Y")
        self.chk_grid_y.setChecked(True)
        self.chk_grid_y.toggled.connect(self.emit_changes)
        grid_layout.addWidget(self.chk_grid_y)
        aes_layout.addLayout(grid_layout)
        
        # Linear Regression Toggle
        self.chk_regression = QCheckBox("Linear Regression (Scatter)")
        self.chk_regression.setChecked(False)
        self.chk_regression.toggled.connect(self.emit_changes)
        aes_layout.addWidget(self.chk_regression)
        
        # Colormap / Theme
        self.w_theme = QWidget()
        theme_layout = QHBoxLayout(self.w_theme)
        theme_layout.setContentsMargins(0,0,0,0)
        theme_layout.addWidget(QLabel("Palette:"))
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["viridis", "plasma", "inferno", "magma", "coolwarm"])
        self.combo_theme.currentIndexChanged.connect(self.emit_changes)
        theme_layout.addWidget(self.combo_theme)
        aes_layout.addWidget(self.w_theme)
        
        self.layout.addWidget(group_aes)
        
        # Plot Colors
        self.group_cat_colors = QGroupBox("Plot Colors")
        plot_colors_main_layout = QVBoxLayout(self.group_cat_colors)
        
        self.base_color_widget = QWidget()
        base_layout = QFormLayout(self.base_color_widget)
        base_layout.setContentsMargins(0, 0, 0, 0)
        base_layout.addRow("Base Plot Color:", self.color_base)
        
        self.cat_colors_widget = QWidget()
        self.cat_colors_layout = QFormLayout(self.cat_colors_widget)
        self.cat_colors_layout.setContentsMargins(0, 0, 0, 0)
        
        plot_colors_main_layout.addWidget(self.base_color_widget)
        plot_colors_main_layout.addWidget(self.cat_colors_widget)
        
        self.layout.addWidget(self.group_cat_colors)
        self.group_cat_colors.hide() # Hidden by default
        self.cat_color_pickers = {}
        
        self.layout.addStretch()
        
    def _set_visible(self, widget, visible):
        widget.setVisible(visible)
        for form in [getattr(self, 'form_limits', None), getattr(self, 'form_labels', None)]:
            if form:
                label = form.labelForField(widget)
                if label:
                    label.setVisible(visible)
                
    def update_visibility(self, tab_idx):
        # 0: Scatter, 1: Hist, 2: Box, 3: Bar, 4: Line, 5: Parallel, 6: Corr, 7: ML, 8: Gallery
        
        # Labels & Titles
        show_x = tab_idx not in [5, 6]
        show_y = tab_idx not in [1, 5, 6]
        self._set_visible(self.edit_xlabel, show_x)
        self._set_visible(self.edit_ylabel, show_y)
            
        # Upper/Lower Limits
        show_limits = tab_idx in [0, 2, 4] # Maybe lineplot wants limits? Not standard right now, keep 0, 2, 4
        self._set_visible(self.w_upper, tab_idx in [0, 2])
        self._set_visible(self.w_lower, tab_idx in [0, 2])
        
        # Boxplot annotations
        show_box = (tab_idx == 2)
        self._set_visible(self.w_means, show_box)
        self._set_visible(self.w_q1, show_box)
        self._set_visible(self.w_q3, show_box)
        self._set_visible(self.chk_xtable, show_box)
        
        # Decimals
        show_decimals_x = tab_idx in [0, 1, 2]
        show_decimals_y = tab_idx in [0, 2, 3, 4, 6]
        self._set_visible(self.spin_decimals_x, show_decimals_x)
        self._set_visible(self.spin_decimals_y, show_decimals_y)
        
        # Linear Regression
        self.chk_regression.setVisible(tab_idx == 0)
        
        # Point Size
        self.spin_size.setVisible(tab_idx in [0, 7])
        self.lbl_point_size.setVisible(tab_idx in [0, 7])
        
        # Grid
        self.chk_grid_x.setVisible(tab_idx in [0, 1, 2, 3, 4, 7])
        self.chk_grid_y.setVisible(tab_idx in [0, 1, 2, 3, 4, 7])
        
        # Palette (Theme)
        self.w_theme.setVisible(tab_idx == 6)
        
        # Plot Colors logic
        has_cats = len(self.cat_color_pickers) > 0
        
        self.base_color_widget.setVisible(not has_cats)
        
        # Hide the entire Plot Colors group if it's Corr(6)
        if tab_idx in [6]:
            self.group_cat_colors.hide()
        else:
            self.group_cat_colors.show()
            
    def update_categorical_colors(self, categories):
        # Clear layout
        while self.cat_colors_layout.count():
            item = self.cat_colors_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
                
        self.cat_color_pickers.clear()
        
        if not categories:
            self.cat_colors_widget.hide()
            self.base_color_widget.show()
            return
            
        self.base_color_widget.hide()
        import matplotlib as mpl
        try:
            cmap = mpl.colormaps[self.combo_theme.currentText()]
        except:
            cmap = mpl.colormaps['viridis']
            
        for i, cat in enumerate(categories):
            try:
                rgba = cmap(i / max(1, len(categories) - 1))
                r, g, b = int(rgba[0]*255), int(rgba[1]*255), int(rgba[2]*255)
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
            except Exception as e:
                hex_color = "#1f77b4"
            picker = ColorPickerButton(hex_color)
            picker.colorChanged.connect(self.emit_changes)
            self.cat_color_pickers[str(cat)] = picker
            self.cat_colors_layout.addRow(str(cat) + ":", picker)
            
        self.cat_colors_widget.show()
        
    def get_current_properties(self):
        props = {
            'custom_title': self.edit_title.text().strip(),
            'custom_xlabel': self.edit_xlabel.text().strip(),
            'custom_ylabel': self.edit_ylabel.text().strip(),
            'limit_upper': self.edit_upper.text().strip(),
            'limit_lower': self.edit_lower.text().strip(),
            'show_means': self.chk_means.isChecked(),
            'show_q1': self.chk_q1.isChecked(),
            'show_q3': self.chk_q3.isChecked(),
            'show_xtable': self.chk_xtable.isChecked(),
            'decimals_x': self.spin_decimals_x.value(),
            'decimals_y': self.spin_decimals_y.value(),
            'color_base': self.color_base.color,
            'color_upper': self.color_upper.color,
            'color_lower': self.color_lower.color,
            'color_means': self.color_means.color,
            'color_q1': self.color_q1.color,
            'color_q3': self.color_q3.color,
            'point_size': self.spin_size.value(),
            'show_grid_x': self.chk_grid_x.isChecked(),
            'show_grid_y': self.chk_grid_y.isChecked(),
            'linear_regression': self.chk_regression.isChecked(),
            'palette': self.combo_theme.currentText()
        }
        
        cat_colors = {}
        for cat, picker in self.cat_color_pickers.items():
            cat_colors[cat] = picker.color
        props['cat_colors'] = cat_colors
        
        return props
        
    def emit_changes(self):
        self.properties_changed.emit(self.get_current_properties())
