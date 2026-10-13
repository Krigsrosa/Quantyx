from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QFormLayout, 
                             QComboBox, QPushButton, QLabel, QMessageBox, QListWidget, QAbstractItemView)
from PyQt6.QtCore import Qt, pyqtSignal
import pandas as pd

class MultiSelectComboBox(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.setMaximumHeight(100)

class PreprocessingPanel(QWidget):
    # Signals for actions
    impute_requested = pyqtSignal(list, str) # columns, method
    scale_requested = pyqtSignal(list, str) # columns, method
    auto_outlier_requested = pyqtSignal()
    remove_outliers_requested = pyqtSignal()
    clear_outliers_requested = pyqtSignal()
    return_to_plots_requested = pyqtSignal()
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.layout = QVBoxLayout(self)
        
        self.setup_ui()
        
    def setup_ui(self):
        # --- Top Button ---
        self.btn_return = QPushButton("🔙 Return to Plots")
        self.btn_return.setToolTip("Returns to the main plotting environment with the cleaned dataset.")
        self.btn_return.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; font-size: 14px; padding: 10px;")
        self.btn_return.clicked.connect(self.return_to_plots_requested.emit)
        self.layout.addWidget(self.btn_return)
        
        # --- Imputation ---
        group_impute = QGroupBox("Missing Value Imputation")
        lay_impute = QVBoxLayout(group_impute)
        
        lay_impute.addWidget(QLabel("Select Numeric Columns:"))
        self.list_impute_cols = MultiSelectComboBox()
        self.list_impute_cols.setToolTip("Select numeric columns containing missing values (NaN) to apply imputation.")
        lay_impute.addWidget(self.list_impute_cols)
        
        form_impute = QFormLayout()
        self.combo_impute_method = QComboBox()
        self.combo_impute_method.addItems(["Mean", "Median", "Mode", "KNN"])
        self.combo_impute_method.setToolTip("Imputation strategy:\n• Mean: Arithmetic mean.\n• Median: Robust against skewed distributions.\n• Mode: Most frequent value.\n• KNN: Multivariate imputation based on 5 nearest neighbors.")
        form_impute.addRow("Method:", self.combo_impute_method)
        lay_impute.addLayout(form_impute)
        
        self.btn_impute = QPushButton("Apply Imputation")
        self.btn_impute.setToolTip("Applies the selected imputation strategy in the background.")
        self.btn_impute.clicked.connect(self.on_impute_clicked)
        lay_impute.addWidget(self.btn_impute)
        self.layout.addWidget(group_impute)
        
        # --- Scaling ---
        group_scale = QGroupBox("Scaling & Normalization")
        lay_scale = QVBoxLayout(group_scale)
        
        lay_scale.addWidget(QLabel("Select Numeric Columns:"))
        self.list_scale_cols = MultiSelectComboBox()
        self.list_scale_cols.setToolTip("Select numeric columns to scale or standardize.")
        lay_scale.addWidget(self.list_scale_cols)
        
        form_scale = QFormLayout()
        self.combo_scale_method = QComboBox()
        self.combo_scale_method.addItems(["MinMax", "Standard"])
        self.combo_scale_method.setToolTip("Scaling method:\n• MinMax: Linearly rescales features to [0, 1].\n• Standard: Zero-mean, unit-variance standardization.")
        form_scale.addRow("Method:", self.combo_scale_method)
        lay_scale.addLayout(form_scale)
        
        self.btn_scale = QPushButton("Apply Scaling")
        self.btn_scale.setToolTip("Applies the scaling transformation to the selected columns.")
        self.btn_scale.clicked.connect(self.on_scale_clicked)
        lay_scale.addWidget(self.btn_scale)
        self.layout.addWidget(group_scale)
        
        # --- Outliers ---
        group_outliers = QGroupBox("Outliers Management")
        lay_outliers = QVBoxLayout(group_outliers)
        
        self.btn_auto_outlier = QPushButton("Auto Detect Outliers (Isolation Forest)")
        self.btn_auto_outlier.setToolTip("Automatically identifies anomalous rows using the Isolation Forest algorithm (5% contamination rate).")
        self.btn_auto_outlier.clicked.connect(self.auto_outlier_requested.emit)
        lay_outliers.addWidget(self.btn_auto_outlier)
        
        self.lbl_selected_outliers = QLabel("0 points selected for removal.")
        lay_outliers.addWidget(self.lbl_selected_outliers)
        
        self.btn_remove_outliers = QPushButton("Remove Selected Points")
        self.btn_remove_outliers.setToolTip("Permanently drops all selected outlier rows (manual orange points and auto-detected red points) from the dataset.")
        self.btn_remove_outliers.setStyleSheet("background-color: #e74c3c; color: white;")
        self.btn_remove_outliers.clicked.connect(self.remove_outliers_requested.emit)
        lay_outliers.addWidget(self.btn_remove_outliers)
        
        self.btn_clear_outliers = QPushButton("Clear Selection")
        self.btn_clear_outliers.setToolTip("Clears all outlier selections from the plot without modifying the dataset.")
        self.btn_clear_outliers.clicked.connect(self.clear_outliers_requested.emit)
        lay_outliers.addWidget(self.btn_clear_outliers)
        
        self.layout.addWidget(group_outliers)
        self.layout.addStretch()
        
    def update_columns(self):
        """Update column lists from DataManager."""
        self.list_impute_cols.clear()
        self.list_scale_cols.clear()
        
        if self.data_manager.df is not None:
            num_cols = self.data_manager.get_numeric_columns()
            self.list_impute_cols.addItems(num_cols)
            self.list_scale_cols.addItems(num_cols)
            
    def on_impute_clicked(self):
        selected = [item.text() for item in self.list_impute_cols.selectedItems()]
        if not selected:
            QMessageBox.warning(self, "Warning", "Select at least one column.")
            return
        method = self.combo_impute_method.currentText()
        self.impute_requested.emit(selected, method)
        
    def on_scale_clicked(self):
        selected = [item.text() for item in self.list_scale_cols.selectedItems()]
        if not selected:
            QMessageBox.warning(self, "Warning", "Select at least one column.")
            return
        method = self.combo_scale_method.currentText()
        self.scale_requested.emit(selected, method)
        
    def update_selection_count(self, selection):
        count = len(selection) if isinstance(selection, list) else selection
        self.lbl_selected_outliers.setText(f"{count} points selected for removal.")

