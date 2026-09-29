from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, 
                             QPushButton, QHBoxLayout, QStackedWidget, QListWidget, QListWidgetItem, QDateEdit)
from PyQt6.QtCore import pyqtSignal, Qt, QDate
import pandas as pd
import numpy as np

class FilterPanel(QWidget):
    filter_applied = pyqtSignal(object)  # Emits filtered dataframe
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.active_filters = [] # Store list of dicts: {'type': 'numeric'/'cat'/'date', 'col': col, ...}
        
        self.layout = QVBoxLayout(self)
        
        # 1. Column Selection
        self.layout.addWidget(QLabel("Select Column to Filter:"))
        self.combo_col = QComboBox()
        self.combo_col.currentIndexChanged.connect(self.on_column_changed)
        self.layout.addWidget(self.combo_col)
        
        # 2. Stacked Widget for Numeric vs Categorical input
        self.stacked = QStackedWidget()
        
        # Page 0: Numeric
        self.page_num = QWidget()
        num_layout = QVBoxLayout(self.page_num)
        num_layout.setContentsMargins(0, 0, 0, 0)
        self.combo_cond = QComboBox()
        self.combo_cond.addItems([">", "<", "==", ">=", "<=", "!="])
        num_layout.addWidget(self.combo_cond)
        self.val_input = QLineEdit()
        num_layout.addWidget(self.val_input)
        self.btn_add_num = QPushButton("Add Numeric Filter")
        self.btn_add_num.clicked.connect(self.add_numeric_filter)
        num_layout.addWidget(self.btn_add_num)
        self.stacked.addWidget(self.page_num)
        
        # Page 1: Categorical
        self.page_cat = QWidget()
        cat_layout = QVBoxLayout(self.page_cat)
        cat_layout.setContentsMargins(0, 0, 0, 0)
        
        btn_sel_layout = QHBoxLayout()
        self.btn_sel_all = QPushButton("Select All")
        self.btn_desel_all = QPushButton("Deselect All")
        btn_sel_layout.addWidget(self.btn_sel_all)
        btn_sel_layout.addWidget(self.btn_desel_all)
        cat_layout.addLayout(btn_sel_layout)
        
        self.btn_sel_all.clicked.connect(self.select_all_cat)
        self.btn_desel_all.clicked.connect(self.deselect_all_cat)
        
        self.list_cat = QListWidget()
        cat_layout.addWidget(self.list_cat)
        self.btn_add_cat = QPushButton("Apply Categorical Filter")
        self.btn_add_cat.clicked.connect(self.add_categorical_filter)
        cat_layout.addWidget(self.btn_add_cat)
        self.stacked.addWidget(self.page_cat)
        
        # Page 2: Date Range
        self.page_date = QWidget()
        date_layout = QVBoxLayout(self.page_date)
        date_layout.setContentsMargins(0, 0, 0, 0)
        date_layout.addWidget(QLabel("Start Date:"))
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        date_layout.addWidget(self.date_start)
        date_layout.addWidget(QLabel("End Date:"))
        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        date_layout.addWidget(self.date_end)
        self.btn_add_date = QPushButton("Apply Date Filter")
        self.btn_add_date.clicked.connect(self.add_date_filter)
        date_layout.addWidget(self.btn_add_date)
        self.stacked.addWidget(self.page_date)
        
        self.layout.addWidget(self.stacked)
        
        # 3. Active Filters Group
        self.group_active = QWidget()
        active_layout = QVBoxLayout(self.group_active)
        active_layout.setContentsMargins(0, 10, 0, 0)
        
        active_layout.addWidget(QLabel("Active Filters:"))
        self.list_active_filters = QListWidget()
        active_layout.addWidget(self.list_active_filters)
        
        # Buttons to manage active filters
        btn_layout = QHBoxLayout()
        self.btn_remove = QPushButton("Remove Selected")
        self.btn_clear = QPushButton("Clear All")
        
        btn_layout.addWidget(self.btn_remove)
        btn_layout.addWidget(self.btn_clear)
        active_layout.addLayout(btn_layout)
        
        self.layout.addWidget(self.group_active)
        self.group_active.hide()
        
        self.btn_remove.clicked.connect(self.remove_selected_filter)
        self.btn_clear.clicked.connect(self.clear_all_filters)
        
    def select_all_cat(self):
        for i in range(self.list_cat.count()):
            self.list_cat.item(i).setCheckState(Qt.CheckState.Checked)
            
    def deselect_all_cat(self):
        for i in range(self.list_cat.count()):
            self.list_cat.item(i).setCheckState(Qt.CheckState.Unchecked)
        
    def update_columns(self):
        if self.data_manager.df is not None:
            self.combo_col.blockSignals(True)
            self.combo_col.clear()
            self.combo_col.addItems(self.data_manager.df.columns.tolist())
            self.combo_col.blockSignals(False)
            if self.combo_col.count() > 0:
                self.on_column_changed()
            self.clear_all_filters()
            
    def on_column_changed(self):
        if self.data_manager.df is None:
            return
            
        col = self.combo_col.currentText()
        if not col:
            return
            
        if pd.api.types.is_datetime64_any_dtype(self.data_manager.df[col]):
            self.stacked.setCurrentIndex(2)
            df_to_use = self.data_manager.filtered_df if self.data_manager.filtered_df is not None else self.data_manager.df
            min_date = df_to_use[col].min()
            max_date = df_to_use[col].max()
            if pd.notnull(min_date):
                self.date_start.setDate(QDate(min_date.year, min_date.month, min_date.day))
            if pd.notnull(max_date):
                self.date_end.setDate(QDate(max_date.year, max_date.month, max_date.day))
        elif pd.api.types.is_numeric_dtype(self.data_manager.df[col]):
            self.stacked.setCurrentIndex(0)
        else:
            self.stacked.setCurrentIndex(1)
            self.populate_categorical_list(col)
            
    def populate_categorical_list(self, col):
        self.list_cat.clear()
        df_to_use = self.data_manager.filtered_df if self.data_manager.filtered_df is not None else self.data_manager.df
        unique_vals = df_to_use[col].dropna().unique()
        # Sort if possible
        try:
            unique_vals = sorted(unique_vals)
        except Exception:
            pass
            
        # Limit to 500 items to avoid UI freeze
        for val in list(unique_vals)[:500]:
            item = QListWidgetItem(str(val))
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            item.setData(Qt.ItemDataRole.UserRole, val) # Store original value
            self.list_cat.addItem(item)
            
    def add_numeric_filter(self):
        col = self.combo_col.currentText()
        cond = self.combo_cond.currentText()
        val_str = self.val_input.text()
        
        try:
            val = float(val_str)
            filter_def = {
                'type': 'numeric',
                'col': col,
                'cond': cond,
                'val': val
            }
            self.active_filters.append(filter_def)
            self.refresh_active_filters_ui()
            self.apply_all_filters()
        except ValueError:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid number.")
            
    def add_categorical_filter(self):
        col = self.combo_col.currentText()
        checked_vals = []
        for i in range(self.list_cat.count()):
            item = self.list_cat.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                checked_vals.append(item.data(Qt.ItemDataRole.UserRole))
                
        self.active_filters = [f for f in self.active_filters if not (f['type'] == 'cat' and f['col'] == col)]
        
        filter_def = {
            'type': 'cat',
            'col': col,
            'val': checked_vals
        }
        self.active_filters.append(filter_def)
        self.refresh_active_filters_ui()
        self.apply_all_filters()
        
    def add_date_filter(self):
        col = self.combo_col.currentText()
        start_date = self.date_start.date().toPyDate()
        end_date = self.date_end.date().toPyDate()
        
        self.active_filters = [f for f in self.active_filters if not (f['type'] == 'date' and f['col'] == col)]
        
        filter_def = {
            'type': 'date',
            'col': col,
            'start': pd.Timestamp(start_date),
            'end': pd.Timestamp(end_date)
        }
        self.active_filters.append(filter_def)
        self.refresh_active_filters_ui()
        self.apply_all_filters()
        
    def refresh_active_filters_ui(self):
        self.list_active_filters.clear()
        
        if not self.active_filters:
            self.group_active.hide()
            return
            
        self.group_active.show()
        for f in self.active_filters:
            if f['type'] == 'numeric':
                desc = f"{f['col']} {f['cond']} {f['val']}"
            elif f['type'] == 'date':
                desc = f"{f['col']} from {f['start'].strftime('%Y-%m-%d')} to {f['end'].strftime('%Y-%m-%d')}"
            else:
                desc = f"{f['col']} in ({len(f['val'])} selected)"
            self.list_active_filters.addItem(desc)
            
    def remove_selected_filter(self):
        row = self.list_active_filters.currentRow()
        if row >= 0:
            del self.active_filters[row]
            self.refresh_active_filters_ui()
            
            # Reset df to start clean then re-apply
            if self.data_manager.df is not None:
                self.data_manager.filtered_df = self.data_manager.df.copy()
            
            self.apply_all_filters()
            
    def clear_all_filters(self):
        self.active_filters.clear()
        self.refresh_active_filters_ui()
        if self.data_manager.df is not None:
            self.data_manager.filtered_df = self.data_manager.df.copy()
            self.filter_applied.emit(self.data_manager.filtered_df)
            
    def apply_all_filters(self):
        if self.data_manager.df is None:
            return
            
        df = self.data_manager.df
        for f in self.active_filters:
            col = f['col']
            if f['type'] == 'numeric':
                cond = f['cond']
                val = f['val']
                if cond == ">": df = df[df[col] > val]
                elif cond == "<": df = df[df[col] < val]
                elif cond == "==": df = df[df[col] == val]
                elif cond == ">=": df = df[df[col] >= val]
                elif cond == "<=": df = df[df[col] <= val]
                elif cond == "!=": df = df[df[col] != val]
            elif f['type'] == 'date':
                df = df[(df[col] >= f['start']) & (df[col] <= f['end'])]
            elif f['type'] == 'cat':
                df = df[df[col].isin(f['val'])]
                
        self.data_manager.filtered_df = df
        
        # Repopulate current category list to cascade
        curr_col = self.combo_col.currentText()
        if curr_col and not pd.api.types.is_numeric_dtype(self.data_manager.df[curr_col]) and not pd.api.types.is_datetime64_any_dtype(self.data_manager.df[curr_col]):
            self.populate_categorical_list(curr_col)
            
        self.filter_applied.emit(self.data_manager.filtered_df)
