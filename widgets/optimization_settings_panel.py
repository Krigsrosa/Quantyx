import os
from typing import Any, Dict, List
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QGroupBox,
    QComboBox,
    QLabel,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QLineEdit,
    QPushButton,
    QProgressBar,
    QFileDialog,
)
from PyQt6.QtCore import pyqtSignal
from analysis.optimization import OPTIMIZER_REGISTRY, ParameterSpec


class OptimizationSettingsPanel(QWidget):
    run_requested = pyqtSignal()
    cancel_requested = pyqtSignal()
    export_requested = pyqtSignal()
    return_requested = pyqtSignal()
    algorithm_changed = pyqtSignal(str)
    fitness_file_selected = pyqtSignal(str)
    fitness_function_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self._param_widgets: Dict[str, Dict[str, QWidget]] = {}
        self._algo_containers: Dict[str, QWidget] = {}
        self.fitness_file_path: str = ""

        self._setup_ui()

    def _setup_ui(self):
        # Return Button (same pattern as MLSettingsPanel)
        self.btn_return = QPushButton("⬅ Return to Data Exploration")
        self.btn_return.setToolTip("Returns to the primary data exploration and plotting view.")
        self.btn_return.setStyleSheet("background-color: #2c3e50; color: white; font-weight: bold;")
        self.btn_return.clicked.connect(self.return_requested.emit)
        self.layout.addWidget(self.btn_return)
        self.layout.addSpacing(8)

        # 1. Algorithm Selection
        group_algo = QGroupBox("Optimization Algorithm")
        form_algo = QFormLayout(group_algo)

        self.combo_algorithm = QComboBox()
        self.combo_algorithm.addItems(list(OPTIMIZER_REGISTRY.keys()))
        self.combo_algorithm.setToolTip("Select the metaheuristic optimization algorithm (GA or PSO).")
        self.combo_algorithm.currentTextChanged.connect(self._on_algorithm_changed)
        form_algo.addRow("Algorithm:", self.combo_algorithm)

        self.combo_objective = QComboBox()
        self.combo_objective.addItems(["Minimize", "Maximize"])
        self.combo_objective.setToolTip("Optimization direction: Minimize or Maximize the fitness function.")
        form_algo.addRow("Objective:", self.combo_objective)

        self.layout.addWidget(group_algo)

        # 2. Dynamic Algorithm Parameters
        self.group_params = QGroupBox("Algorithm Parameters")
        self.params_layout = QVBoxLayout(self.group_params)
        self.params_layout.setContentsMargins(8, 8, 8, 8)

        for algo_name, optimizer_cls in OPTIMIZER_REGISTRY.items():
            container = QWidget()
            form = QFormLayout(container)
            form.setContentsMargins(0, 0, 0, 0)
            self._param_widgets[algo_name] = {}

            for spec in optimizer_cls.get_parameter_specs():
                widget = self._create_param_widget(spec)
                self._param_widgets[algo_name][spec.name] = widget
                form.addRow(spec.label, widget)

            self._algo_containers[algo_name] = container
            self.params_layout.addWidget(container)

        self.layout.addWidget(self.group_params)

        # 3. Search Space Configuration
        group_space = QGroupBox("Search Space (Decision Variables)")
        form_space = QFormLayout(group_space)

        self.spin_n_vars = QSpinBox()
        self.spin_n_vars.setRange(1, 1000)
        self.spin_n_vars.setValue(2)
        self.spin_n_vars.setToolTip("Number of decision variables (dimension of vector x passed to fitness function).")
        form_space.addRow("Variables (N):", self.spin_n_vars)

        self.edit_lower_bound = QLineEdit("-10.0")
        self.edit_lower_bound.setPlaceholderText("e.g. -10.0 or -10, -5")
        self.edit_lower_bound.setToolTip(
            "Lower bound(s) for decision variables.\n"
            "Enter a single value for all variables (e.g. -10.0) or comma-separated values per variable."
        )
        form_space.addRow("Lower Bound(s):", self.edit_lower_bound)

        self.edit_upper_bound = QLineEdit("10.0")
        self.edit_upper_bound.setPlaceholderText("e.g. 10.0 or 10, 5")
        self.edit_upper_bound.setToolTip(
            "Upper bound(s) for decision variables.\n"
            "Enter a single value for all variables (e.g. 10.0) or comma-separated values per variable."
        )
        form_space.addRow("Upper Bound(s):", self.edit_upper_bound)

        self.layout.addWidget(group_space)

        # 4. Fitness Function (.py import + function dropdown)
        group_fitness = QGroupBox("Fitness Function")
        lay_fitness = QVBoxLayout(group_fitness)

        self.btn_browse_fitness = QPushButton("📂 Select Fitness File (.py)...")
        self.btn_browse_fitness.setToolTip("Import an external Python (.py) file containing one or more fitness functions.")
        self.btn_browse_fitness.clicked.connect(self._browse_fitness_file)
        lay_fitness.addWidget(self.btn_browse_fitness)

        self.edit_fitness_file = QLineEdit()
        self.edit_fitness_file.setReadOnly(True)
        self.edit_fitness_file.setPlaceholderText("No .py file selected")
        self.edit_fitness_file.setToolTip("Path to the selected Python fitness function file.")
        lay_fitness.addWidget(self.edit_fitness_file)

        func_form = QFormLayout()
        func_form.setContentsMargins(0, 2, 0, 2)
        self.combo_fitness_func = QComboBox()
        self.combo_fitness_func.setEnabled(False)
        self.combo_fitness_func.setToolTip("Select which Python function from the imported .py file will be optimized.")
        self.combo_fitness_func.currentTextChanged.connect(self.fitness_function_changed.emit)
        func_form.addRow("Function:", self.combo_fitness_func)
        lay_fitness.addLayout(func_form)

        self.lbl_fitness_info = QLabel("Expected: Python file (.py) defining one or more functions.")
        self.lbl_fitness_info.setWordWrap(True)
        self.lbl_fitness_info.setStyleSheet("color: gray; font-size: 11px;")
        lay_fitness.addWidget(self.lbl_fitness_info)

        self.layout.addWidget(group_fitness)

        # 5. Execution Controls
        self.layout.addSpacing(8)
        self.lbl_status = QLabel("Status: Ready")
        self.lbl_status.setStyleSheet("font-weight: bold;")
        self.layout.addWidget(self.lbl_status)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        self.layout.addWidget(self.progress_bar)

        btn_row = QHBoxLayout()
        self.btn_run = QPushButton("▶ Run Optimization")
        self.btn_run.setToolTip("Validates inputs and starts the optimization in the background.")
        self.btn_run.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; padding: 6px;")
        self.btn_run.clicked.connect(self.run_requested.emit)
        btn_row.addWidget(self.btn_run)

        self.btn_cancel = QPushButton("⏹ Stop")
        self.btn_cancel.setToolTip("Interrupts the running optimization at the current iteration/generation.")
        self.btn_cancel.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold; padding: 6px;")
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self.cancel_requested.emit)
        btn_row.addWidget(self.btn_cancel)

        self.layout.addLayout(btn_row)

        self.btn_export = QPushButton("Download Results")
        self.btn_export.setToolTip("Exports optimization summary, best variables, and convergence history to Excel (.xlsx).")
        self.btn_export.clicked.connect(self.export_requested.emit)
        self.layout.addWidget(self.btn_export)

        self.layout.addStretch()

        # Initialize visibility for default algorithm
        self._on_algorithm_changed(self.combo_algorithm.currentText())

    def _create_param_widget(self, spec: ParameterSpec) -> QWidget:
        if spec.param_type == "int":
            w = QSpinBox()
            w.setRange(int(spec.min_val or 1), int(spec.max_val or 100000))
            w.setValue(int(spec.default))
            w.setToolTip(spec.tooltip)
            return w

        elif spec.param_type == "float":
            w = QDoubleSpinBox()
            w.setDecimals(spec.decimals)
            w.setRange(float(spec.min_val if spec.min_val is not None else -1e9),
                       float(spec.max_val if spec.max_val is not None else 1e9))
            w.setSingleStep(float(spec.step or 0.1))
            w.setValue(float(spec.default))
            w.setToolTip(spec.tooltip)
            return w

        elif spec.param_type == "choice":
            w = QComboBox()
            if spec.choices:
                w.addItems(spec.choices)
                idx = w.findText(str(spec.default))
                if idx >= 0:
                    w.setCurrentIndex(idx)
            w.setToolTip(spec.tooltip)
            return w

        elif spec.param_type == "bool":
            w = QCheckBox("Enabled")
            w.setChecked(bool(spec.default))
            w.setToolTip(spec.tooltip)
            return w

        elif spec.param_type == "seed":
            w = QLineEdit(str(spec.default) if spec.default is not None else "")
            w.setPlaceholderText("None (Random)")
            w.setToolTip(spec.tooltip)
            return w

        else:
            w = QLineEdit(str(spec.default))
            w.setToolTip(spec.tooltip)
            return w

    def _on_algorithm_changed(self, algo_name: str):
        for name, container in self._algo_containers.items():
            container.setVisible(name == algo_name)
        self.algorithm_changed.emit(algo_name)

    def _browse_fitness_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Fitness Function File",
            "",
            "Python Files (*.py);;All Files (*)",
        )
        if file_path:
            self.set_fitness_file(file_path)

    def set_fitness_file(self, file_path: str):
        self.fitness_file_path = file_path.strip()
        self.edit_fitness_file.setText(self.fitness_file_path)
        self.edit_fitness_file.setToolTip(self.fitness_file_path)
        if not self.fitness_file_path:
            self.set_available_functions([], "")
            self.lbl_fitness_info.setText("Expected: Python file (.py) defining one or more functions.")
        self.fitness_file_selected.emit(self.fitness_file_path)

    def set_available_functions(self, functions: List[str], default_fn: str = ""):
        self.combo_fitness_func.blockSignals(True)
        self.combo_fitness_func.clear()
        if functions:
            self.combo_fitness_func.addItems(functions)
            idx = self.combo_fitness_func.findText(default_fn)
            if idx >= 0:
                self.combo_fitness_func.setCurrentIndex(idx)
            self.combo_fitness_func.setEnabled(True)
        else:
            self.combo_fitness_func.setEnabled(False)
        self.combo_fitness_func.blockSignals(False)

    def get_selected_fitness_function(self) -> str:
        return self.combo_fitness_func.currentText().strip()

    def get_selected_algorithm(self) -> str:
        return self.combo_algorithm.currentText().strip()

    def get_objective(self) -> str:
        return self.combo_objective.currentText().strip()

    def get_algorithm_parameters(self) -> Dict[str, Any]:
        algo = self.get_selected_algorithm()
        widgets = self._param_widgets.get(algo, {})
        params: Dict[str, Any] = {}
        for name, w in widgets.items():
            if isinstance(w, (QSpinBox, QDoubleSpinBox)):
                params[name] = w.value()
            elif isinstance(w, QComboBox):
                params[name] = w.currentText()
            elif isinstance(w, QCheckBox):
                params[name] = w.isChecked()
            elif isinstance(w, QLineEdit):
                params[name] = w.text().strip()
        return params

    def get_search_space_inputs(self) -> Dict[str, Any]:
        return {
            "n_vars": self.spin_n_vars.value(),
            "lower_bound": self.edit_lower_bound.text().strip(),
            "upper_bound": self.edit_upper_bound.text().strip(),
        }

    def set_running_state(self, running: bool, status_text: str = ""):
        self.btn_run.setEnabled(not running)
        self.btn_cancel.setEnabled(running)
        self.combo_algorithm.setEnabled(not running)
        self.combo_objective.setEnabled(not running)
        self.spin_n_vars.setEnabled(not running)
        self.edit_lower_bound.setEnabled(not running)
        self.edit_upper_bound.setEnabled(not running)
        self.btn_browse_fitness.setEnabled(not running)
        self.combo_fitness_func.setEnabled((not running) and self.combo_fitness_func.count() > 0)
        for container in self._algo_containers.values():
            container.setEnabled(not running)

        if running:
            self.progress_bar.setValue(0)
            self.progress_bar.show()
        else:
            self.progress_bar.hide()

        if status_text:
            self.lbl_status.setText(f"Status: {status_text}")
