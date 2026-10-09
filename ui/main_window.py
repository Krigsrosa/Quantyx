from PyQt6.QtWidgets import (QMainWindow, QDockWidget, QFileDialog, QMessageBox, 
                             QListWidget, QVBoxLayout, QWidget, QComboBox, QLabel, QTabWidget,
                             QListWidgetItem, QProgressBar, QPushButton, QLineEdit)
from PyQt6.QtCore import Qt, QCoreApplication, QByteArray, QBuffer, QIODevice
from PyQt6.QtGui import QPixmap, QIcon
import joblib
import os
from data.data_manager import DataManager
from widgets.data_table_view import DataTableView
from plots.fast_plots import ScatterPlotWidget
from plots.stat_plots import HistogramWidget, BoxPlotWidget, CorrelationMatrixWidget, BarPlotWidget, LinePlotWidget
from plots.ml_plots import MachineLearningWidget
from plots.parallel_plots import ParallelPlotWidget
from widgets.filter_panel import FilterPanel
from widgets.properties_panel import PropertiesPanel
from widgets.report_panel import ReportPanel
from ui.help_dialog import HelpDialog
from utils.logger import logger

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        from PyQt6.QtCore import QThreadPool
        self.threadpool = QThreadPool()
        
        self.setWindowTitle("Quantyx - Data Analysis & ML")
        self.resize(1200, 800)
        
        self.data_manager = DataManager()
        self.data_manager.data_loaded.connect(self.on_data_loaded)
        self.data_manager.error_occurred.connect(self.on_data_error)
        
        self.plot_properties = {
            'point_size': 5,
            'show_grid_x': True,
            'show_grid_y': True,
            'palette': 'viridis'
        }
        
        self.setup_ui()
        self.setup_menus()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.hide()
        self.statusBar().addPermanentWidget(self.progress_bar)
        
        # Iniciar verificação de nova versão em background
        self.check_updates_async()
        
    def setup_ui(self):
        # Central widget is now a Tab Widget
        self.tab_widget = QTabWidget()
        
        self.plot_scatter = ScatterPlotWidget()
        self.plot_histogram = HistogramWidget()
        self.plot_boxplot = BoxPlotWidget()
        self.plot_barplot = BarPlotWidget()
        self.plot_lineplot = LinePlotWidget()
        self.plot_parallel = ParallelPlotWidget()
        self.plot_corr = CorrelationMatrixWidget()
        
        self.tab_widget.addTab(self.plot_scatter, "Scatter")
        self.tab_widget.addTab(self.plot_histogram, "Histogram")
        self.tab_widget.addTab(self.plot_boxplot, "Boxplot")
        self.tab_widget.addTab(self.plot_barplot, "Bar Plot")
        self.tab_widget.addTab(self.plot_lineplot, "Line Plot")
        self.tab_widget.addTab(self.plot_parallel, "Parallel Coordinates")
        self.tab_widget.addTab(self.plot_corr, "Correlation Matrix")
        
        from widgets.ml_settings_panel import MLSettingsPanel
        
        self.ml_settings_panel = MLSettingsPanel()
        self.ml_tab_widget = QTabWidget()
        
        # Create ML Widgets for each technique
        self.ml_widgets = {}
        techniques = ["PCA", "K-Means", "K-Nearest Neighbors", "Random Forest", "XGBoost"]
        for tech in techniques:
            w = MachineLearningWidget(self.ml_settings_panel, tech)
            w.model_loaded.connect(self.on_ml_model_loaded)
            self.ml_tab_widget.addTab(w, tech)
            self.ml_widgets[tech] = w
            
        self.ml_tab_widget.currentChanged.connect(self.on_ml_tab_changed)
        
        # Connect panel signals to active ML widget
        self.ml_settings_panel.update_plot_requested.connect(self.update_plot)
        self.ml_settings_panel.train_requested.connect(self.on_ml_train_requested)
        self.ml_settings_panel.predict_requested.connect(self.on_ml_predict_requested)
        self.ml_settings_panel.autotune_requested.connect(self.on_ml_autotune_requested)
        self.ml_settings_panel.importance_requested.connect(self.on_ml_importance_requested)
        self.ml_settings_panel.save_requested.connect(lambda: self.get_active_ml_widget().save_model())
        self.ml_settings_panel.load_requested.connect(lambda: self.get_active_ml_widget().load_model())
        self.ml_settings_panel.download_requested.connect(lambda: self.get_active_ml_widget().download_results())
        self.ml_settings_panel.return_requested.connect(self.return_to_plots)
        
        self.report_panel = ReportPanel()
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        from PyQt6.QtWidgets import QStackedWidget
        self.central_stack = QStackedWidget()
        self.setCentralWidget(self.central_stack)
        
        self.central_stack.addWidget(self.tab_widget)
        
        from plots.outlier_plot import OutlierPlotWidget
        self.outlier_plot = OutlierPlotWidget()
        self.central_stack.addWidget(self.outlier_plot)
        self.central_stack.addWidget(self.ml_tab_widget)
        from PyQt6.QtWidgets import QToolBar
        from PyQt6.QtGui import QAction
        self.toolbar = QToolBar("Main Toolbar")
        self.addToolBar(self.toolbar)
        self.action_add_to_report = QAction("📸 Add Current Plot to Presentation", self)
        self.action_add_to_report.triggered.connect(self.add_plot_to_report)
        self.toolbar.addAction(self.action_add_to_report)
        
        # Setup Docks
        self.setup_docks()
        
    def setup_docks(self):
        # 1. Variable List Dock (Left)
        self.var_dock = QDockWidget("Variables & Axes", self)
        self.var_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        
        var_widget = QWidget()
        var_layout = QVBoxLayout(var_widget)
        
        from PyQt6.QtWidgets import QAbstractItemView
        self.var_list = QListWidget()
        self.var_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        
        var_layout.addWidget(QLabel("All Variables:"))
        var_layout.addWidget(self.var_list)
        
        var_layout.addWidget(QLabel("X Axis:"))
        self.combo_x = QComboBox()
        var_layout.addWidget(self.combo_x)
        
        var_layout.addWidget(QLabel("Y Axis:"))
        self.combo_y = QComboBox()
        var_layout.addWidget(self.combo_y)
        
        self.lbl_color_by = QLabel("Color by:")
        var_layout.addWidget(self.lbl_color_by)
        self.combo_color = QComboBox()
        var_layout.addWidget(self.combo_color)
        
        self.edit_color_rule = QLineEdit()
        self.edit_color_rule.setPlaceholderText("Rule e.g. TS > 1000")
        var_layout.addWidget(self.edit_color_rule)
        
        self.btn_update_plot = QPushButton("Update Plot")
        self.btn_update_plot.clicked.connect(self.update_plot)
        self.btn_update_plot.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; padding: 5px;")
        var_layout.addWidget(self.btn_update_plot)
        
        self.var_dock.setWidget(var_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.var_dock)
        
        # 2. Data Table Dock (Bottom)
        self.data_dock = QDockWidget("Data View", self)
        self.data_table = DataTableView()
        self.data_dock.setWidget(self.data_table)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.data_dock)
        
        # 3. Filter Dock (Right)
        self.filter_dock = QDockWidget("Filters", self)
        self.filter_panel = FilterPanel(self.data_manager)
        self.filter_dock.setWidget(self.filter_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.filter_dock)
        
        self.filter_panel.filter_applied.connect(self.on_filter_applied)
        
        # 4. Properties Dock (Right)
        self.props_dock = QDockWidget("Plot Properties", self)
        
        from PyQt6.QtWidgets import QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        self.props_panel = PropertiesPanel()
        scroll_area.setWidget(self.props_panel)
        
        self.props_dock.setWidget(scroll_area)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.props_dock)
        
        self.props_panel.properties_changed.connect(self.on_properties_changed)
        
        # 4.5 Gallery Dock (Right)
        self.gallery_dock = QDockWidget("Gallery", self)
        self.gallery_dock.setWidget(self.report_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.gallery_dock)
        
        # Tabify Filter, Properties, and Gallery
        self.tabifyDockWidget(self.filter_dock, self.props_dock)
        self.tabifyDockWidget(self.props_dock, self.gallery_dock)
        
        # 4.5. ML Settings Dock (Right, hidden by default, tabified between Props and Gallery)
        self.ml_dock = QDockWidget("ML Settings", self)
        
        ml_scroll = QScrollArea()
        ml_scroll.setWidgetResizable(True)
        ml_scroll.setWidget(self.ml_settings_panel)
        self.ml_dock.setWidget(ml_scroll)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.ml_dock)
        self.tabifyDockWidget(self.props_dock, self.ml_dock)
        self.tabifyDockWidget(self.ml_dock, self.gallery_dock)
        self.ml_dock.hide()
        
        self.props_dock.raise_()
        
        # 5. Preprocessing Dock (Right, hidden by default)
        self.prep_dock = QDockWidget("Preprocessing Settings", self)
        from ui.preprocessing_panel import PreprocessingPanel
        self.prep_panel = PreprocessingPanel(self.data_manager)
        
        prep_scroll = QScrollArea()
        prep_scroll.setWidgetResizable(True)
        prep_scroll.setWidget(self.prep_panel)
        
        self.prep_dock.setWidget(prep_scroll)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.prep_dock)
        self.prep_dock.hide()
        
        # Connect prep signals
        self.prep_panel.impute_requested.connect(self.on_impute_requested)
        self.prep_panel.scale_requested.connect(self.on_scale_requested)
        self.prep_panel.auto_outlier_requested.connect(self.on_auto_outlier_requested)
        self.prep_panel.remove_outliers_requested.connect(self.on_remove_outliers_requested)
        self.prep_panel.clear_outliers_requested.connect(self.on_clear_outliers_requested)
        
        # Connect outlier plot signals
        self.outlier_plot.selection_changed.connect(self.prep_panel.update_selection_count)
        self.prep_panel.return_to_plots_requested.connect(self.return_to_plots)
        
    def setup_menus(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        
        open_action = file_menu.addAction("Open Data...")
        open_action.triggered.connect(self.open_file_dialog)
        open_action.setShortcut("Ctrl+O")
        
        save_proj_action = file_menu.addAction("Save Project...")
        save_proj_action.triggered.connect(self.save_project)
        save_proj_action.setShortcut("Ctrl+S")
        
        load_proj_action = file_menu.addAction("Load Project...")
        load_proj_action.triggered.connect(self.load_project)
        
        file_menu.addSeparator()
        
        export_data_act = file_menu.addAction("Export Filtered Data...")
        export_data_act.triggered.connect(self.export_data_xlsx)
        
        export_plot_png_act = file_menu.addAction("Export Plot (PNG)...")
        export_plot_png_act.triggered.connect(self.export_plot_png)
        
        export_plot_pdf_act = file_menu.addAction("Export Plot (PDF)...")
        export_plot_pdf_act.triggered.connect(self.export_plot_pdf)
        
        file_menu.addSeparator()
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        help_menu = menubar.addMenu("Help")
        doc_action = help_menu.addAction("Documentation / User Guide")
        doc_action.triggered.connect(self.show_help_dialog)
        
        help_menu.addSeparator()
        
        contact_action = help_menu.addAction("Contact Developer")
        contact_action.triggered.connect(self.contact_developer)
        
        settings_menu = menubar.addMenu("Settings")
        
        template_action = settings_menu.addAction("Template Center...")
        template_action.triggered.connect(self.open_template_center)
        
        theme_action = settings_menu.addAction("Toggle Light/Dark Theme")
        theme_action.triggered.connect(self.toggle_theme)
        
        sql_menu = menubar.addMenu("SQL Data")
        sql_action = sql_menu.addAction("Import from Databricks SQL...")
        sql_action.triggered.connect(self.open_sql_dialog)
        
        prep_menu = menubar.addMenu("Data Preprocessing")
        prep_action = prep_menu.addAction("Open Preprocessing Tool")
        prep_action.triggered.connect(self.toggle_preprocessing_mode)
        
        ml_menu = menubar.addMenu("Machine Learning")
        ml_action = ml_menu.addAction("Open ML Hub")
        ml_action.triggered.connect(self.toggle_ml_mode)
        
    def on_ml_train_requested(self):
        self.update_plot()
        w = self.get_active_ml_widget()
        if w: w.train_model()
        
    def on_ml_predict_requested(self):
        self.update_plot()
        w = self.get_active_ml_widget()
        if w: w.predict_only()
        
    def on_ml_autotune_requested(self):
        self.update_plot()
        w = self.get_active_ml_widget()
        if w: w.auto_tune()
        
    def on_ml_importance_requested(self):
        self.update_plot()
        w = self.get_active_ml_widget()
        if w: w.show_feature_importance()
        
    def get_active_ml_widget(self):
        return self.ml_tab_widget.currentWidget()
        
    def on_ml_tab_changed(self):
        tech = self.ml_tab_widget.tabText(self.ml_tab_widget.currentIndex())
        self.ml_settings_panel.set_technique(tech)
        self.ml_settings_panel.populate_target(self.data_manager.filtered_df)
        
        if self.data_manager.df is not None and self.central_stack.currentIndex() == 2:
            all_cols = self.data_manager.get_column_names()
            curr_x = self.combo_x.currentText()
            curr_y = self.combo_y.currentText()
            
            self.combo_x.blockSignals(True)
            self.combo_y.blockSignals(True)
            self.combo_x.clear()
            self.combo_y.clear()
            self.combo_x.addItem("None")
            self.combo_x.addItems(all_cols)
            self.combo_y.addItem("None")
            self.combo_y.addItems(all_cols)
            
            idx_x = self.combo_x.findText(curr_x)
            if idx_x >= 0: self.combo_x.setCurrentIndex(idx_x)
            idx_y = self.combo_y.findText(curr_y)
            if idx_y >= 0: self.combo_y.setCurrentIndex(idx_y)
            
            self.combo_x.blockSignals(False)
            self.combo_y.blockSignals(False)
            
            is_pca = (tech == "PCA")
            self.lbl_color_by.setVisible(is_pca)
            self.combo_color.setVisible(is_pca)
            self.edit_color_rule.setVisible(is_pca)
        
    def toggle_ml_mode(self):
        if self.data_manager.df is None:
            QMessageBox.warning(self, "Warning", "Please load data first.")
            return
            
        if self.central_stack.currentIndex() == 2:
            self.return_to_plots()
        else:
            self.central_stack.setCurrentIndex(2)
            self.prep_dock.hide()
            self.filter_dock.hide()
            self.props_dock.hide()
            self.var_dock.show()
            self.lbl_color_by.hide()
            self.combo_color.hide()
            self.edit_color_rule.hide()
            self.btn_update_plot.show()
            self.gallery_dock.show()
            self.ml_dock.show()
            self.ml_dock.raise_()
            self.on_ml_tab_changed()
            
            # Force a replot so the ML widget gets the variables
            self.update_plot()
        
    def open_template_center(self):
        from ui.template_center import TemplateCenterDialog
        dlg = TemplateCenterDialog(self)
        dlg.exec()
        # Update report panel combo box if needed
        self.report_panel.load_templates()
        
    def toggle_theme(self):
        from utils.theme_manager import ThemeManager
        new_is_dark = not ThemeManager.is_dark()
        ThemeManager.set_theme(new_is_dark)
        ThemeManager.apply_to_plots(self)
        self.update_plot()

    def toggle_preprocessing_mode(self):
        if self.data_manager.df is None:
            QMessageBox.warning(self, "Warning", "Please load data first.")
            return
            
        self.central_stack.setCurrentIndex(1)
        self.var_dock.show()
        self.lbl_color_by.hide()
        self.combo_color.hide()
        self.edit_color_rule.hide()
        self.btn_update_plot.show()
        self.filter_dock.hide()
        self.props_dock.hide()
        self.gallery_dock.hide()
        self.ml_dock.hide()
        self.prep_dock.show()
        self.prep_panel.update_columns()
        
        # Override combo_x and combo_y to numeric for the outlier plot
        if self.data_manager.df is not None:
            num_cols = self.data_manager.get_numeric_columns()
            curr_x = self.combo_x.currentText()
            curr_y = self.combo_y.currentText()
            
            self.combo_x.blockSignals(True)
            self.combo_y.blockSignals(True)
            self.combo_x.clear()
            self.combo_y.clear()
            self.combo_x.addItems(num_cols)
            self.combo_y.addItems(num_cols)
            
            idx_x = self.combo_x.findText(curr_x)
            if idx_x >= 0: self.combo_x.setCurrentIndex(idx_x)
            idx_y = self.combo_y.findText(curr_y)
            if idx_y >= 0: self.combo_y.setCurrentIndex(idx_y)
            
            self.combo_x.blockSignals(False)
            self.combo_y.blockSignals(False)
        
        self.update_outlier_plot()
        
    def return_to_plots(self):
        self.central_stack.setCurrentIndex(0)
        self.prep_dock.hide()
        self.ml_dock.hide()
        self.var_dock.show()
        self.lbl_color_by.show()
        self.combo_color.show()
        self.edit_color_rule.show()
        self.btn_update_plot.show()
        self.filter_dock.show()
        self.props_dock.show()
        self.gallery_dock.show()
        # Force combo boxes to reset to the standard plots rules
        self.on_tab_changed(self.tab_widget.currentIndex())
        # Force a replot on the current tab
        self.update_plot()
        
    def on_impute_requested(self, cols, method):
        self.progress_bar.setRange(0, 0)
        self.progress_bar.show()
        self.statusBar().showMessage("Imputing missing data...")
        self.prep_dock.setEnabled(False)
        
        from utils.threads import Worker
        worker = Worker(self._do_impute, cols, method)
        worker.signals.result.connect(self._on_impute_success)
        worker.signals.error.connect(self._on_prep_error)
        self.threadpool.start(worker)
        
    def _do_impute(self, cols, method):
        self.data_manager.impute_missing(cols, method)
        return cols, method
        
    def _on_impute_success(self, result):
        cols, method = result
        self.data_table.set_dataframe(self.data_manager.filtered_df)
        self.update_outlier_plot()
        self.progress_bar.hide()
        self.prep_dock.setEnabled(True)
        self.statusBar().showMessage(f"Imputed {method} for columns: {', '.join(cols)}", 5000)
        QMessageBox.information(self, "Success", f"Imputed {method} for columns: {', '.join(cols)}")
        
    def _on_prep_error(self, err_tuple):
        self.progress_bar.hide()
        self.prep_dock.setEnabled(True)
        self.statusBar().showMessage("Error during preprocessing.", 5000)
        QMessageBox.critical(self, "Error", str(err_tuple[1]))
        
    def on_scale_requested(self, cols, method):
        self.progress_bar.setRange(0, 0)
        self.progress_bar.show()
        self.statusBar().showMessage("Scaling data...")
        self.prep_dock.setEnabled(False)
        
        from utils.threads import Worker
        worker = Worker(self._do_scale, cols, method)
        worker.signals.result.connect(self._on_scale_success)
        worker.signals.error.connect(self._on_prep_error)
        self.threadpool.start(worker)
        
    def _do_scale(self, cols, method):
        self.data_manager.scale_columns(cols, method)
        return cols, method
        
    def _on_scale_success(self, result):
        cols, method = result
        self.data_table.set_dataframe(self.data_manager.filtered_df)
        self.update_outlier_plot()
        self.progress_bar.hide()
        self.prep_dock.setEnabled(True)
        self.statusBar().showMessage(f"Applied {method} scaling to: {', '.join(cols)}", 5000)
        QMessageBox.information(self, "Success", f"Applied {method} scaling to: {', '.join(cols)}")
        
    def on_auto_outlier_requested(self):
        if self.data_manager.df is None: return
        num_cols = self.data_manager.get_numeric_columns()
        if not num_cols: return
        
        # Determine which columns to use based on selection in 'All Variables'
        selected_items = self.var_list.selectedItems()
        selected_cols = [item.text() for item in selected_items]
        
        # Filter selected_cols to only include numeric ones
        valid_cols = [c for c in selected_cols if c in num_cols]
        
        # If no numeric columns were manually selected, fallback to using all numeric columns
        if not valid_cols:
            valid_cols = num_cols
            QMessageBox.information(self, "Auto Detect", "Nenhuma variável selecionada em 'All Variables'. A análise usará todas as variáveis numéricas disponíveis.")
        
        # Use isolation forest on selected numeric columns. Fill NaNs with median to avoid dropping all rows.
        df = self.data_manager.filtered_df if self.data_manager.filtered_df is not None else self.data_manager.df
        df_clean = df[valid_cols].copy()
        
        # Fill missing values with median for outlier detection purposes
        for col in valid_cols:
            df_clean[col] = df_clean[col].fillna(df_clean[col].median())
            
        df_clean = df_clean.dropna() # Drop any completely empty columns
        
        if df_clean.empty:
            QMessageBox.warning(self, "Auto Detect", "Não foi possível analisar os dados (as colunas estão vazias ou inválidas).")
            return
            
        self.progress_bar.setRange(0, 0)
        self.progress_bar.show()
        self.statusBar().showMessage("Detecting outliers...")
        self.prep_dock.setEnabled(False)
        
        from utils.threads import Worker
        worker = Worker(self._do_auto_outlier, df_clean)
        worker.signals.result.connect(self._on_auto_outlier_success)
        worker.signals.error.connect(self._on_prep_error)
        self.threadpool.start(worker)
        
    def _do_auto_outlier(self, df_clean):
        from sklearn.ensemble import IsolationForest
        iso = IsolationForest(contamination=0.05, random_state=42)
        preds = iso.fit_predict(df_clean)
        outlier_mask = preds == -1
        outlier_indices = df_clean.index[outlier_mask].tolist()
        return outlier_indices
        
    def _on_auto_outlier_success(self, outlier_indices):
        self.progress_bar.hide()
        self.prep_dock.setEnabled(True)
        self.statusBar().showMessage("Outlier detection complete.", 5000)
        self.outlier_plot.set_auto_outliers(outlier_indices)
        QMessageBox.information(self, "Auto Detect", f"Detectados {len(outlier_indices)} outliers potenciais. Verifique no gráfico.")
        
    def on_clear_outliers_requested(self):
        self.outlier_plot.clear_selections()
        
    def on_remove_outliers_requested(self):
        selected = self.outlier_plot.selected_indices
        auto = self.outlier_plot.auto_outlier_indices
        to_drop = list(selected.union(auto))
        
        if not to_drop:
            QMessageBox.information(self, "Info", "No outliers selected to remove.")
            return
            
        self.data_manager.drop_rows(to_drop)
        self.data_table.set_dataframe(self.data_manager.filtered_df)
        self.outlier_plot.clear_selections()
        self.update_outlier_plot()
        QMessageBox.information(self, "Success", f"Removed {len(to_drop)} outlier rows.")
        
    def update_outlier_plot(self):
        x_col = self.combo_x.currentText()
        y_col = self.combo_y.currentText()
        df = self.data_manager.filtered_df if self.data_manager.filtered_df is not None else self.data_manager.df
        self.outlier_plot.plot_data(df, x_col, y_col)
        
    def open_file_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Data File", "", 
            "Data Files (*.csv *.xlsx *.parquet *.feather);;All Files (*)"
        )
        if file_name:
            self.statusBar().showMessage(f"Loading {file_name}...")
            self.progress_bar.setRange(0, 0) # Indeterminate spinning
            self.progress_bar.show()
            
            self.data_manager.load_data(file_name)
            
    def open_sql_dialog(self):
        from ui.sql_dialog import SQLDialog
        dialog = SQLDialog(self)
        dialog.data_fetched.connect(self.data_manager.load_dataframe)
        dialog.exec()
            
    def on_data_loaded(self, df):
        self.progress_bar.hide()
        self.statusBar().showMessage(f"Loaded {df.shape[0]} rows, {df.shape[1]} columns.")
        
        # Update Table
        self.data_table.set_dataframe(df)
        
        # Update Variables
        num_cols = self.data_manager.get_numeric_columns()
        
        try:
            self.var_list.itemChanged.disconnect(self.update_plot)
        except TypeError:
            pass
            
        self.var_list.clear()
        
        for col in df.columns.tolist():
            item = QListWidgetItem(col)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.var_list.addItem(item)
            
        self.combo_x.blockSignals(True)
        self.combo_y.blockSignals(True)
        self.combo_x.clear()
        self.combo_y.clear()
        
        self.combo_x.addItems(num_cols)
        self.combo_y.addItems(num_cols)
        
        self.combo_color.blockSignals(True)
        self.combo_color.clear()
        self.combo_color.addItem("None")
        self.combo_color.addItems(df.columns.tolist())
        self.combo_color.blockSignals(False)
        
        if len(num_cols) > 0:
            self.combo_x.setCurrentIndex(0)
        if len(num_cols) > 1:
            self.combo_y.setCurrentIndex(1)
            
        self.combo_x.blockSignals(False)
        self.combo_y.blockSignals(False)
        
        self.filter_panel.update_columns()
        self.ml_settings_panel.populate_target(df)
        # Don't plot automatically on data load to avoid freezing with large datasets
        self.props_panel.update_visibility(self.tab_widget.currentIndex())
        
    def on_tab_changed(self, index):
        self.props_panel.edit_xlabel.blockSignals(True)
        self.props_panel.edit_ylabel.blockSignals(True)
        self.props_panel.edit_title.blockSignals(True)
        
        self.props_panel.edit_xlabel.setText("")
        self.props_panel.edit_ylabel.setText("")
        self.props_panel.edit_title.setText("")
        
        self.props_panel.edit_xlabel.blockSignals(False)
        self.props_panel.edit_ylabel.blockSignals(False)
        self.props_panel.edit_title.blockSignals(False)
        
        # Switch variable lists based on tab
        if self.data_manager.df is not None:
            num_cols = self.data_manager.get_numeric_columns()
            cat_cols = self.data_manager.get_categorical_columns()
            all_cols = self.data_manager.get_column_names()
            
            curr_x = self.combo_x.currentText()
            curr_y = self.combo_y.currentText()
            
            self.combo_x.blockSignals(True)
            self.combo_y.blockSignals(True)
            self.combo_x.clear()
            self.combo_y.clear()
            
            if index == 3: # Bar Plot
                self.combo_x.addItems(cat_cols)
                self.combo_y.addItem("None")
                self.combo_y.addItems(num_cols)
            elif index == 4: # Line Plot
                self.combo_x.addItems(all_cols)
                self.combo_y.addItems(num_cols)
            elif index == 2: # Boxplot
                self.combo_x.addItem("None")
                self.combo_x.addItems(all_cols)
                self.combo_y.addItems(num_cols)
            else:
                self.combo_x.addItems(num_cols)
                self.combo_y.addItems(num_cols)
                
            idx_x = self.combo_x.findText(curr_x)
            if idx_x >= 0: self.combo_x.setCurrentIndex(idx_x)
            
            idx_y = self.combo_y.findText(curr_y)
            if idx_y >= 0: self.combo_y.setCurrentIndex(idx_y)
            
            self.combo_x.blockSignals(False)
            self.combo_y.blockSignals(False)
            


        # Don't plot automatically on tab change to avoid heavy processing
        # Just update the properties panel visibility
        self.props_panel.update_visibility(index)
        
    def on_ml_model_loaded(self, data):
        if not data: return
        
        features = data.get('ml_features', data.get('features', []))
        
        # Retrocompatibility: fetch new 'targets' or fallback to old 'target'
        targets = data.get('ml_targets', data.get('targets', []))
        if not targets:
            legacy_target = data.get('ml_target', data.get('target', ''))
            if legacy_target:
                targets = [legacy_target]
                
        task = data.get('ml_task', data.get('task', ''))
        tech = data.get('ml_tech', data.get('tech', ''))
        
        # 1. Update side variables
        self.var_list.blockSignals(True)
        for i in range(self.var_list.count()):
            item = self.var_list.item(i)
            if item.text() in features:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
        self.var_list.blockSignals(False)
        
        # 2. Ensure we are in ML mode
        if self.central_stack.currentIndex() != 2:
            self.toggle_ml_mode()
        
        # 3. Update ML panel combos
        if tech:
            for i in range(self.ml_tab_widget.count()):
                if self.ml_tab_widget.tabText(i) == tech:
                    self.ml_tab_widget.setCurrentIndex(i)
                    break
            
        if task:
            idx = self.ml_settings_panel.combo_task.findText(task)
            if idx >= 0: self.ml_settings_panel.combo_task.setCurrentIndex(idx)
            
        if targets:
            self.ml_settings_panel.set_selected_targets(targets)
            
        ml_model = data.get('ml_model')
        if ml_model:
            active_ml = self.get_active_ml_widget()
            if active_ml:
                active_ml.trained_model = ml_model
                active_ml.model_features = features
                active_ml.model_targets = targets
                active_ml.model_task = task
                active_ml.model_tech = tech
                active_ml.model_loaded.emit({
                    'features': features,
                    'targets': targets,
                    'task': task,
                    'tech': tech
                })
            
        self.update_plot()
        
    def update_plot(self):
        if self.data_manager.df is None:
            return
            
        x_col = self.combo_x.currentText()
        y_col = self.combo_y.currentText()
        color_col = self.combo_color.currentText()
        color_rule = self.edit_color_rule.text().strip()
        
        df = self.data_manager.filtered_df if self.data_manager.filtered_df is not None else self.data_manager.df
        
        if color_rule:
            try:
                df = df.copy()
                for col_name in df.columns:
                    if " " in col_name and col_name in color_rule:
                        if f"`{col_name}`" not in color_rule:
                            color_rule = color_rule.replace(col_name, f"`{col_name}`")
                df['_color_rule'] = df.eval(color_rule).astype(str)
                color_col = '_color_rule'
            except Exception as e:
                from utils.logger import logger
                logger.error(f"Error evaluating color rule: {e}")

        if not hasattr(self, 'last_color_col') or self.last_color_col != color_col:
            self.last_color_col = color_col
            if color_col and color_col != "None" and color_col in df.columns:
                unique_cats = df[color_col].dropna().unique().tolist()
                self.props_panel.update_categorical_colors(unique_cats)
            else:
                self.props_panel.update_categorical_colors([])
                
        # Get properties AFTER updating categories, so we get the new dictionary
        self.plot_properties = self.props_panel.get_current_properties()
        
        if self.central_stack.currentIndex() == 1:
            self.update_outlier_plot()
            return
        elif self.central_stack.currentIndex() == 2:
            selected_cols = []
            for i in range(self.var_list.count()):
                item = self.var_list.item(i)
                if item.checkState() == Qt.CheckState.Checked:
                    selected_cols.append(item.text())
            active_ml = self.get_active_ml_widget()
            if active_ml:
                active_ml.plot_data(df, selected_cols, x_col, y_col, color_col, self.plot_properties)
            return
            
        current_idx = self.tab_widget.currentIndex()
        self.props_panel.update_visibility(current_idx)
        
        if current_idx == 0: # Scatter
            self.plot_scatter.plot_data(df, x_col, y_col, color_col, self.plot_properties)
        elif current_idx == 1: # Histogram
            self.plot_histogram.plot_data(df, x_col, color_col, self.plot_properties)
        elif current_idx == 2: # Boxplot
            selected_cols = []
            for i in range(self.var_list.count()):
                item = self.var_list.item(i)
                if item.checkState() == Qt.CheckState.Checked:
                    selected_cols.append(item.text())
            
            props = self.plot_properties.copy()
            props['box_group_cols'] = selected_cols
            self.plot_boxplot.plot_data(df, x_col, y_col, color_col, props)
        elif current_idx == 3: # Bar Plot
            self.plot_barplot.plot_data(df, x_col, y_col, color_col, self.plot_properties)
        elif current_idx == 4: # Line Plot
            self.plot_lineplot.plot_data(df, x_col, y_col, color_col, self.plot_properties)
        elif current_idx == 5: # Parallel Coordinates
            selected_cols = []
            for i in range(self.var_list.count()):
                item = self.var_list.item(i)
                if item.checkState() == Qt.CheckState.Checked:
                    selected_cols.append(item.text())
            self.plot_parallel.plot_data(df, selected_cols, color_col, self.plot_properties)
        elif current_idx == 6: # Correlation
            selected_cols = []
            for i in range(self.var_list.count()):
                item = self.var_list.item(i)
                if item.checkState() == Qt.CheckState.Checked:
                    selected_cols.append(item.text())
            self.plot_corr.plot_data(df, selected_cols, self.plot_properties)

    def on_data_error(self, err_msg):
        self.progress_bar.hide()
        QMessageBox.critical(self, "Error Loading Data", f"An error occurred:\n{err_msg}")
        self.statusBar().showMessage("Error loading data.")
        
    def on_filter_applied(self, filtered_df):
        self.data_table.set_dataframe(filtered_df)
        self.statusBar().showMessage(f"Filtered: {filtered_df.shape[0]} rows visible.")
        self.update_plot()
        
    def on_properties_changed(self, props):
        self.plot_properties = props
        self.update_plot()
        
    def export_data_xlsx(self):
        df = self.data_manager.filtered_df if self.data_manager.filtered_df is not None else self.data_manager.df
        if df is None or df.empty:
            QMessageBox.warning(self, "Export Error", "No data available to export.")
            return
            
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Data", "", "Excel Files (*.xlsx)")
        if file_name:
            if not file_name.endswith('.xlsx'):
                file_name += '.xlsx'
            from exports.exporter import export_data
            export_data(df, file_name)
            self.statusBar().showMessage(f"Data exported to {file_name}")

    def get_current_plot_widget(self):
        if self.central_stack.currentIndex() == 1:
            return self.outlier_plot
        elif self.central_stack.currentIndex() == 2:
            return self.get_active_ml_widget()
            
        current_idx = self.tab_widget.currentIndex()
        if current_idx == 0: return self.plot_scatter
        elif current_idx == 1: return self.plot_histogram
        elif current_idx == 2: return self.plot_boxplot
        elif current_idx == 3: return self.plot_barplot
        elif current_idx == 4: return self.plot_lineplot
        elif current_idx == 5: return self.plot_parallel
        elif current_idx == 6: return self.plot_corr
        return None

    def export_plot(self, ext="png"):
        if self.data_manager.df is None:
            QMessageBox.warning(self, "Export Error", "No plot available to export.")
            return
            
        file_name, _ = QFileDialog.getSaveFileName(self, f"Save Plot", "", f"{ext.upper()} Files (*.{ext})")
        if not file_name:
            return
            
        try:
            widget = self.get_current_plot_widget()
            
            
            if widget is None: return
                
            if ext == "png":
                pixmap = widget.grab()
                pixmap.save(file_name, 'PNG')
            elif ext == "pdf":
                from PyQt6.QtPrintSupport import QPrinter
                from PyQt6.QtGui import QPainter
                printer = QPrinter(QPrinter.PrinterMode.PrinterResolution)
                printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
                printer.setOutputFileName(file_name)
                painter = QPainter(printer)
                widget.render(painter)
                painter.end()
                
            self.statusBar().showMessage(f"Plot exported to {file_name}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export plot:\n{str(e)}")

    def export_plot_png(self):
        self.export_plot("png")
        
    def export_plot_pdf(self):
        self.export_plot("pdf")
        
    def add_plot_to_report(self):
        if self.data_manager.df is None:
            QMessageBox.warning(self, "Warning", "No data loaded!")
            return
            
        import os
        

            
        img_name = f"plot_{len(self.report_panel.images) + 1}.png"
        img_path = os.path.join(self.report_panel.temp_dir, img_name)
        
        try:
            widget = self.get_current_plot_widget()
            
            
            if widget:
                pixmap = widget.grab()
                pixmap.save(img_path, 'PNG')
                
                self.report_panel.add_image(img_path)
                self.statusBar().showMessage(f"Plot added to Gallery.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add plot to report:\n{str(e)}")

    def show_help_dialog(self):
        dialog = HelpDialog(self)
        dialog.exec()

    def contact_developer(self):
        from PyQt6.QtGui import QDesktopServices
        from PyQt6.QtCore import QUrl
        url = QUrl("mailto:quantyx-team@outlook.com.br?subject=Suporte Quantyx&body=Hello,%0D%0A%0D%0AI would to like to talk about the Quantyx.")
        QDesktopServices.openUrl(url)

    def save_project(self):
        if self.data_manager.df is None:
            QMessageBox.warning(self, "Warning", "No data to save.")
            return
            
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Project", "", "Quantyx Project (*.quantyx)")
        if not file_name: return
        
        try:
            gallery_bytes = []
            for path in self.report_panel.images:
                try:
                    with open(path, "rb") as f:
                        gallery_bytes.append(f.read())
                except:
                    pass
                
            active_ml = self.get_active_ml_widget()
            ml_data = {}
            if active_ml:
                ml_data = {
                    'ml_model': active_ml.trained_model,
                    'ml_features': active_ml.model_features,
                    'ml_targets': getattr(active_ml, 'model_targets', []),
                    'ml_task': getattr(active_ml, 'model_task', ''),
                    'ml_tech': getattr(active_ml, 'model_tech', '')
                }
            
            data = {
                'df': self.data_manager.df,
                'filtered_df': self.data_manager.filtered_df,
                'filters': self.filter_panel.active_filters,
                'gallery_bytes': gallery_bytes,
                **ml_data
            }
            
            joblib.dump(data, file_name)
            QMessageBox.information(self, "Success", "Project saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def load_project(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Project", "", "Quantyx Project (*.quantyx)")
        if not file_name: return
        
        try:
            data = joblib.load(file_name)
            
            # 1. Data
            df = data['df']
            self.data_manager.df = df
            self.data_manager.filtered_df = data['filtered_df']
            
            # Repopulate variables in UI (similar to on_data_loaded)
            self.var_list.clear()
            for col in df.columns.tolist():
                item = QListWidgetItem(col)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                self.var_list.addItem(item)
                
            num_cols = self.data_manager.get_numeric_columns()
            self.combo_x.blockSignals(True)
            self.combo_y.blockSignals(True)
            self.combo_color.blockSignals(True)
            
            self.combo_x.clear()
            self.combo_y.clear()
            self.combo_x.addItems(num_cols)
            self.combo_y.addItems(num_cols)
            
            self.combo_color.clear()
            self.combo_color.addItem("None")
            self.combo_color.addItems(df.columns.tolist())
            
            self.combo_x.blockSignals(False)
            self.combo_y.blockSignals(False)
            self.combo_color.blockSignals(False)
            
            self.data_table.set_dataframe(self.data_manager.filtered_df if self.data_manager.filtered_df is not None else self.data_manager.df)
            
            # 2. Filters
            self.filter_panel.active_filters = data.get('filters', [])
            self.filter_panel.list_active_filters.clear()
            for f in self.filter_panel.active_filters:
                if f['type'] == 'numeric':
                    self.filter_panel.list_active_filters.addItem(f"{f['col']} {f['cond']} {f['val']}")
                else:
                    self.filter_panel.list_active_filters.addItem(f"{f['col']} in {f['val']}")
            self.filter_panel.update_columns()
            
            # 3. Variables Panel - Handled above
            
            # 4. Gallery
            self.report_panel.list_widget.clear()
            self.report_panel.images = []
            
            if not os.path.exists(self.report_panel.temp_dir):
                os.makedirs(self.report_panel.temp_dir)
                
            for idx, b in enumerate(data.get('gallery_bytes', [])):
                img_name = f"plot_loaded_{idx}.png"
                img_path = os.path.join(self.report_panel.temp_dir, img_name)
                
                with open(img_path, "wb") as f:
                    f.write(b)
                    
                self.report_panel.add_image(img_path)
                
            # 5. ML Model
            ml_model = data.get('ml_model')
            if ml_model:
                self.on_ml_model_loaded(data)
            QMessageBox.information(self, "Success", "Project loaded successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def check_updates_async(self):
        from utils.threads import Worker
        worker = Worker(self._fetch_latest_version)
        worker.signals.result.connect(self._on_update_check_result)
        self.threadpool.start(worker)

    def _fetch_latest_version(self):
        import urllib.request
        import json
        try:
            # Consulta a API de releases do repositório público
            api_url = "https://api.github.com/repos/Krigsrosa/quantyx-releases/releases/latest"
            
            req = urllib.request.Request(api_url, headers={'User-Agent': 'Quantyx-App'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                # O título da release está em 'name' (ex: "Quantyx 1.1.0")
                # Extraímos a versão removendo a palavra "Quantyx "
                release_name = data.get('name', '')
                latest_version = release_name.replace('Quantyx ', '').strip()
                if not latest_version:
                    latest_version = data.get('tag_name', '').replace('v', '').strip()
                    
                # A URL que abriremos é a página da release para o usuário baixar o executável
                release_url = data.get('html_url', '')
                
                return latest_version, release_url
        except Exception as e:
            logger.error(f"Error checking updates on GitHub: {e}")
            return None

    def _on_update_check_result(self, result):
        if not result:
            return
            
        latest_version, release_url = result
        if not latest_version:
            return
            
        from utils.version import __version__
        
        # Comparação simples (ex: "1.2" > "1.1")
        try:
            def parse_v(v): return tuple(map(int, v.split('.')))
            has_update = parse_v(latest_version) > parse_v(__version__)
        except ValueError:
            has_update = latest_version != __version__
            
        if has_update:
            msg = QMessageBox(self)
            msg.setWindowTitle("New Version Available")
            msg.setText(f"A new version of Quantyx ({latest_version}) is available!\n\nYour current version: {__version__}")
            msg.setInformativeText("Do you want to download the new version now?")
            msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg.setDefaultButton(QMessageBox.StandardButton.Yes)
            
            if msg.exec() == QMessageBox.StandardButton.Yes:
                import webbrowser
                if release_url:
                    webbrowser.open(release_url)
