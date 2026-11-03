import os
import threading
from datetime import datetime
from typing import List, Optional

import numpy as np
import pandas as pd
import pyqtgraph as pg
from PyQt6.QtCore import Qt, QObject, QThreadPool, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QFileDialog,
)

from plots.ml_plots import FormattedAxisItem, configure_plot
from utils.threads import Worker
from utils.logger import logger
from analysis.optimization import (
    FitnessLoader,
    OptimizationError,
    FitnessFileError,
    FitnessExecutionError,
    InvalidParameterError,
    OptimizationResult,
    get_optimizer,
    parse_and_validate_bounds,
)


class _OptimizationProgressEmitter(QObject):
    progress = pyqtSignal(int, int, float, object)


class OptimizationHubWidget(QWidget):
    status_message = pyqtSignal(str)

    def __init__(self, settings_panel, parent=None):
        super().__init__(parent)
        self.panel = settings_panel
        self.threadpool = QThreadPool()
        self._cancel_event = threading.Event()
        self.last_result: Optional[OptimizationResult] = None

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(6, 6, 6, 6)
        self.layout.setSpacing(6)

        # --- Summary & Results Header ---
        self.group_summary = QGroupBox("Optimization Hub - Execution Summary & Best Solution")
        grid = QGridLayout(self.group_summary)
        grid.setContentsMargins(10, 10, 10, 10)
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(6)

        grid.addWidget(QLabel("<b>Algorithm:</b>"), 0, 0)
        self.lbl_algo = QLabel(self.panel.get_selected_algorithm() or "—")
        grid.addWidget(self.lbl_algo, 0, 1)

        grid.addWidget(QLabel("<b>Status:</b>"), 0, 2)
        self.lbl_status = QLabel("Idle")
        self.lbl_status.setStyleSheet("font-weight: bold; color: #3498db;")
        grid.addWidget(self.lbl_status, 0, 3)

        grid.addWidget(QLabel("<b>Iterations / Generations:</b>"), 0, 4)
        self.lbl_iterations = QLabel("0 / 0")
        grid.addWidget(self.lbl_iterations, 0, 5)

        grid.addWidget(QLabel("<b>Best Fitness:</b>"), 1, 0)
        self.lbl_best_fitness = QLabel("—")
        self.lbl_best_fitness.setStyleSheet("font-weight: bold; font-size: 13px; color: #2ecc71;")
        grid.addWidget(self.lbl_best_fitness, 1, 1)

        grid.addWidget(QLabel("<b>Average Fitness:</b>"), 1, 2)
        self.lbl_avg_fitness = QLabel("—")
        self.lbl_avg_fitness.setStyleSheet("font-weight: bold; color: #3498db;")
        grid.addWidget(self.lbl_avg_fitness, 1, 3)

        grid.addWidget(QLabel("<b>Population Diversity:</b>"), 1, 4)
        self.lbl_diversity = QLabel("—")
        self.lbl_diversity.setStyleSheet("font-weight: bold; color: #f39c12;")
        grid.addWidget(self.lbl_diversity, 1, 5)

        grid.addWidget(QLabel("<b>Fitness Function:</b>"), 2, 0)
        self.lbl_fitness_fn = QLabel("Not loaded")
        grid.addWidget(self.lbl_fitness_fn, 2, 1, 1, 5)

        grid.addWidget(QLabel("<b>Best Parameters (x*):</b>"), 3, 0)
        self.edit_best_params = QLineEdit()
        self.edit_best_params.setReadOnly(True)
        self.edit_best_params.setPlaceholderText("Run optimization to compute optimal decision variables...")
        grid.addWidget(self.edit_best_params, 3, 1, 1, 5)

        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)
        grid.setColumnStretch(5, 1)

        self.layout.addWidget(self.group_summary)

        # --- Convergence & Diversity Plot Area ---
        self.axis_x = FormattedAxisItem(orientation="bottom", decimals=0)
        self.axis_y = FormattedAxisItem(orientation="left", decimals=4)
        self.axis_y_right = FormattedAxisItem(orientation="right", decimals=4)
        self.plot_widget = pg.PlotWidget(
            axisItems={
                "bottom": self.axis_x,
                "left": self.axis_y,
                "right": self.axis_y_right,
            }
        )
        configure_plot(self.plot_widget)

        self.plot_item = self.plot_widget.getPlotItem()
        self.plot_item.showGrid(x=True, y=True, alpha=0.3)
        self.plot_item.setTitle("Optimization Convergence & Population Diversity")
        self.plot_item.setLabel("bottom", "Iteration / Generation")
        self.plot_item.setLabel("left", "Fitness Value (Best & Average)")

        # Configure Right Axis & Secondary ViewBox for Population Diversity
        right_axis = self.plot_item.getAxis("right")
        right_axis.setStyle(showValues=True)
        self.plot_item.setLabel("right", "Population Diversity (Normalized Spread)", color="#f39c12")

        self.diversity_vb = pg.ViewBox()
        self.plot_item.scene().addItem(self.diversity_vb)
        right_axis.linkToView(self.diversity_vb)
        self.diversity_vb.setXLink(self.plot_item)

        self.plot_item.vb.sigResized.connect(self._update_diversity_view)

        self.layout.addWidget(self.plot_widget, stretch=1)

    def _update_diversity_view(self):
        self.diversity_vb.setGeometry(self.plot_item.vb.sceneBoundingRect())
        self.diversity_vb.linkedViewChanged(self.plot_item.vb, self.diversity_vb.XAxis)

    def _clear_plot(self):
        if self.plot_item.legend is not None:
            try:
                self.plot_item.legend.scene().removeItem(self.plot_item.legend)
            except Exception:
                pass
            self.plot_item.legend = None
        self.plot_widget.clear()
        self.diversity_vb.clear()

    def _connect_signals(self):
        self.panel.algorithm_changed.connect(self._on_algorithm_changed)
        self.panel.fitness_file_selected.connect(self._on_fitness_file_selected)
        self.panel.fitness_function_changed.connect(self._on_fitness_function_changed)
        self.panel.run_requested.connect(self.run_optimization)
        self.panel.cancel_requested.connect(self.cancel_optimization)
        self.panel.export_requested.connect(self.download_results)

    def _on_algorithm_changed(self, algo_name: str):
        self.lbl_algo.setText(algo_name if algo_name else "—")

    def _on_fitness_function_changed(self, fn_name: str):
        file_path = self.panel.fitness_file_path
        if file_path and fn_name:
            base_name = os.path.basename(file_path)
            self.lbl_fitness_fn.setText(f"{base_name} (function: {fn_name})")

    def _on_fitness_file_selected(self, file_path: str):
        if not file_path:
            self.lbl_fitness_fn.setText("Not loaded")
            self.panel.set_available_functions([], "")
            return
        try:
            func_names, default_fn, metadata = FitnessLoader.inspect_functions(file_path)
            self.panel.set_available_functions(func_names, default_fn)
            selected_fn = self.panel.get_selected_fitness_function()
            base_name = os.path.basename(file_path)
            self.lbl_fitness_fn.setText(f"{base_name} (function: {selected_fn})")
            self.panel.lbl_fitness_info.setStyleSheet("color: #2ecc71; font-size: 11px;")
            self.panel.lbl_fitness_info.setText(
                f"{len(func_names)} function(s) found in {base_name}. Selected: '{selected_fn}'"
            )

            if "N_VARS" in metadata and isinstance(metadata["N_VARS"], int) and metadata["N_VARS"] >= 1:
                self.panel.spin_n_vars.setValue(metadata["N_VARS"])
        except OptimizationError as e:
            self.panel.set_available_functions([], "")
            self.lbl_fitness_fn.setText(f"Invalid file ({os.path.basename(file_path)})")
            self.panel.lbl_fitness_info.setStyleSheet("color: #e74c3c; font-size: 11px;")
            self.panel.lbl_fitness_info.setText(str(e).splitlines()[0])
            QMessageBox.warning(self, "Fitness File Error", str(e))

    def cancel_optimization(self):
        self._cancel_event.set()
        self.lbl_status.setText("Cancelling...")
        self.lbl_status.setStyleSheet("font-weight: bold; color: #f39c12;")
        self.panel.lbl_status.setText("Status: Cancelling...")
        self.status_message.emit("Stopping optimization...")

    def run_optimization(self):
        algo_name = self.panel.get_selected_algorithm()
        if not algo_name:
            QMessageBox.warning(self, "Validation Error", "Please select an optimization algorithm.")
            return

        try:
            optimizer = get_optimizer(algo_name)
            raw_params = self.panel.get_algorithm_parameters()
            validated_params = optimizer.validate_parameters(raw_params)

            space_inputs = self.panel.get_search_space_inputs()
            bounds = parse_and_validate_bounds(
                space_inputs["n_vars"],
                space_inputs["lower_bound"],
                space_inputs["upper_bound"],
            )

            file_path = self.panel.fitness_file_path
            selected_fn = self.panel.get_selected_fitness_function()
            fitness_fn, fn_name, _ = FitnessLoader.load(file_path, function_name=selected_fn)
            objective = self.panel.get_objective()

            # Pre-validate that the fitness function executes cleanly on a test vector within bounds
            test_vec = np.array([(b[0] + b[1]) / 2.0 for b in bounds], dtype=float)
            fitness_fn(test_vec)

        except FitnessFileError as e:
            self._set_error_state("Fitness File Error")
            QMessageBox.warning(self, "Fitness Function Error", str(e))
            return
        except InvalidParameterError as e:
            self._set_error_state("Invalid Parameter")
            QMessageBox.warning(self, "Parameter Validation Error", str(e))
            return
        except FitnessExecutionError as e:
            self._set_error_state("Fitness Execution Error")
            QMessageBox.critical(self, "Fitness Execution Error", str(e))
            return
        except Exception as e:
            self._set_error_state("Error")
            QMessageBox.critical(self, "Optimization Error", f"Unexpected validation error:\n{str(e)}")
            return

        # Prepare UI for background execution
        self._cancel_event.clear()
        self.lbl_algo.setText(algo_name)
        self.lbl_status.setText("Running...")
        self.lbl_status.setStyleSheet("font-weight: bold; color: #f39c12;")
        self.lbl_best_fitness.setText("Computing...")
        self.lbl_avg_fitness.setText("—")
        self.lbl_diversity.setText("—")
        self.lbl_iterations.setText("0 / ?")
        self.lbl_fitness_fn.setText(f"{os.path.basename(file_path)} (function: {fn_name})")
        self.edit_best_params.clear()
        self._clear_plot()

        self.panel.set_running_state(True, "Running...")
        self.status_message.emit(f"Running {algo_name}...")

        progress_emitter = _OptimizationProgressEmitter()
        progress_emitter.progress.connect(self._on_iteration_progress)
        self._active_emitter = progress_emitter

        worker = Worker(
            self._execute_in_thread,
            optimizer,
            fitness_fn,
            bounds,
            validated_params,
            objective,
            file_path,
            fn_name,
            progress_emitter,
        )
        worker.signals.result.connect(self._on_optimization_finished)
        worker.signals.error.connect(self._on_optimization_error)
        self.threadpool.start(worker)

    def _execute_in_thread(
        self,
        optimizer,
        fitness_fn,
        bounds,
        validated_params,
        objective,
        file_path,
        fn_name,
        progress_emitter: _OptimizationProgressEmitter,
    ) -> OptimizationResult:
        def on_progress(curr_iter: int, total_iter: int, best_fit: float, best_pos: np.ndarray, hist_best: List[float]):
            step = max(1, total_iter // 100)
            if curr_iter == 1 or curr_iter == total_iter or curr_iter % step == 0:
                progress_emitter.progress.emit(curr_iter, total_iter, best_fit, best_pos.copy())

        result = optimizer.optimize(
            fitness_fn=fitness_fn,
            bounds=bounds,
            params=validated_params,
            objective=objective,
            progress_callback=on_progress,
            cancel_check=self._cancel_event.is_set,
        )
        result.fitness_file = file_path
        result.fitness_func_name = fn_name
        return result

    def _on_iteration_progress(self, curr_iter: int, total_iter: int, best_fit: float, best_pos: np.ndarray):
        pct = int((curr_iter / max(1, total_iter)) * 100)
        self.panel.progress_bar.setValue(pct)
        self.lbl_iterations.setText(f"{curr_iter} / {total_iter}")
        self.lbl_best_fitness.setText(f"{best_fit:.6g}")
        self.edit_best_params.setText(self._format_vector(best_pos))

    def _on_optimization_finished(self, result: OptimizationResult):
        self.last_result = result
        is_cancelled = result.status == "Cancelled"
        status_label = "Cancelled" if is_cancelled else "Completed"
        color = "#f39c12" if is_cancelled else "#2ecc71"

        self.panel.set_running_state(False, status_label)
        self.lbl_status.setText(status_label)
        self.lbl_status.setStyleSheet(f"font-weight: bold; color: {color};")
        self.lbl_algo.setText(result.algorithm_name)
        self.lbl_best_fitness.setText(f"{result.best_fitness:.6g}")
        if result.history_mean:
            self.lbl_avg_fitness.setText(f"{result.history_mean[-1]:.6g}")
        if result.history_diversity:
            self.lbl_diversity.setText(f"{result.history_diversity[-1]:.6g}")
        self.lbl_iterations.setText(f"{result.iterations_executed} / {result.total_iterations}")
        self.edit_best_params.setText(self._format_vector(result.best_position))

        self._plot_convergence(result)
        self.status_message.emit(
            f"Optimization {status_label.lower()}: Best Fitness = {result.best_fitness:.6g} "
            f"({result.iterations_executed}/{result.total_iterations} iterations)."
        )

        if not is_cancelled:
            QMessageBox.information(
                self,
                "Optimization Complete",
                f"Algorithm: {result.algorithm_name}\n"
                f"Status: {result.status}\n"
                f"Iterations Executed: {result.iterations_executed} / {result.total_iterations}\n"
                f"Best Fitness ({result.objective}): {result.best_fitness:.6g}\n"
                f"Final Average Fitness: {(result.history_mean[-1] if result.history_mean else 0.0):.6g}\n"
                f"Final Population Diversity: {(result.history_diversity[-1] if result.history_diversity else 0.0):.6g}\n"
                f"Best Variables: {self._format_vector(result.best_position)}",
            )

    def _on_optimization_error(self, err_tuple):
        _, exc_value, _ = err_tuple
        logger.error(f"Optimization error: {exc_value}")
        self._set_error_state("Error")
        QMessageBox.critical(self, "Optimization Error", str(exc_value))

    def _set_error_state(self, status_text: str):
        self.panel.set_running_state(False, status_text)
        self.lbl_status.setText(status_text)
        self.lbl_status.setStyleSheet("font-weight: bold; color: #e74c3c;")
        self.status_message.emit(f"Optimization failed: {status_text}")

    def _plot_convergence(self, result: OptimizationResult):
        self._clear_plot()
        self.plot_item.showGrid(x=True, y=True, alpha=0.3)

        if not result.history_best:
            return

        iters = np.arange(1, len(result.history_best) + 1, dtype=float)
        best_arr = np.asarray(result.history_best, dtype=float)

        legend = self.plot_widget.addLegend()

        # 1. Best Fitness (Left Y-Axis)
        pen_best = pg.mkPen("#2ecc71", width=2.5)
        self.plot_widget.plot(
            iters,
            best_arr,
            pen=pen_best,
            symbol="o",
            symbolSize=4,
            symbolBrush="#2ecc71",
            name="Best Fitness",
        )

        # 2. Average Fitness of the Population/Swarm (Left Y-Axis)
        if result.history_mean and len(result.history_mean) == len(iters):
            mean_arr = np.asarray(result.history_mean, dtype=float)
            pen_mean = pg.mkPen("#3498db", width=2.0, style=Qt.PenStyle.DashLine)
            self.plot_widget.plot(
                iters,
                mean_arr,
                pen=pen_mean,
                name="Average Fitness",
            )

        # 3. Population Diversity across Generations/Iterations (Right Y-Axis)
        if result.history_diversity and len(result.history_diversity) == len(iters):
            div_arr = np.asarray(result.history_diversity, dtype=float)
            pen_div = pg.mkPen("#f39c12", width=2.0, style=Qt.PenStyle.DotLine)
            div_curve = pg.PlotDataItem(
                iters,
                div_arr,
                pen=pen_div,
                symbol="t",
                symbolSize=4,
                symbolBrush="#f39c12",
                name="Population Diversity (Right Axis)",
            )
            self.diversity_vb.addItem(div_curve)
            legend.addItem(div_curve, "Population Diversity (Right Axis)")
            self.diversity_vb.enableAutoRange()
            self._update_diversity_view()

        xlabel = "Generation" if result.algorithm_key == "GA" else "Iteration"
        self.plot_item.setLabel("bottom", xlabel)
        self.plot_item.setLabel("left", f"Fitness ({result.objective})")
        self.plot_item.setLabel("right", "Population Diversity (Normalized Spread)", color="#f39c12")
        self.plot_item.setTitle(
            f"{result.algorithm_name} — Best Fitness: {result.best_fitness:.6g}"
        )

    @staticmethod
    def _format_vector(vec: np.ndarray) -> str:
        if vec is None or len(vec) == 0:
            return "—"
        parts = [f"x[{i}] = {val:.6g}" for i, val in enumerate(vec)]
        return ", ".join(parts)

    def download_results(self):
        if self.last_result is None:
            QMessageBox.warning(
                self,
                "Export Error",
                "No optimization results available to download. Please run an optimization first.",
            )
            return

        file_name, _ = QFileDialog.getSaveFileName(self, "Save Optimization Results", "", "Excel Files (*.xlsx)")
        if not file_name:
            return
        if not file_name.lower().endswith(".xlsx"):
            file_name += ".xlsx"

        try:
            res = self.last_result
            summary_rows = [
                {"Metric": "Export Date", "Value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                {"Metric": "Algorithm", "Value": res.algorithm_name},
                {"Metric": "Status", "Value": res.status},
                {"Metric": "Objective", "Value": res.objective},
                {"Metric": "Best Fitness", "Value": res.best_fitness},
                {"Metric": "Final Average Fitness", "Value": res.history_mean[-1] if res.history_mean else "N/A"},
                {"Metric": "Final Population Diversity", "Value": res.history_diversity[-1] if res.history_diversity else "N/A"},
                {"Metric": "Iterations Executed", "Value": f"{res.iterations_executed} / {res.total_iterations}"},
                {"Metric": "Fitness File", "Value": res.fitness_file},
                {"Metric": "Fitness Function", "Value": res.fitness_func_name},
            ]
            for k, v in res.parameters.items():
                summary_rows.append({"Metric": f"Param: {k}", "Value": str(v)})

            df_summary = pd.DataFrame(summary_rows)

            df_vars = pd.DataFrame(
                [{"Variable": f"x[{i}]", "Optimal Value": float(val)} for i, val in enumerate(res.best_position)]
            )

            n_steps = len(res.history_best)
            df_history = pd.DataFrame(
                {
                    "Iteration": np.arange(1, n_steps + 1),
                    "Best_Fitness": res.history_best,
                    "Average_Fitness": res.history_mean if len(res.history_mean) == n_steps else res.history_best,
                    "Population_Diversity": (
                        res.history_diversity if len(res.history_diversity) == n_steps else [0.0] * n_steps
                    ),
                }
            )

            with pd.ExcelWriter(file_name, engine="openpyxl") as writer:
                df_summary.to_excel(writer, sheet_name="Summary", index=False)
                df_vars.to_excel(writer, sheet_name="Best_Variables", index=False)
                df_history.to_excel(writer, sheet_name="Convergence_History", index=False)

            QMessageBox.information(self, "Success", f"Optimization results exported to:\n{file_name}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export optimization results:\n{str(e)}")
