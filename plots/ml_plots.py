from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QComboBox, QLabel, QSpinBox, QMessageBox,
                             QPushButton, QDoubleSpinBox, QFileDialog, QGroupBox, QDialog)
from PyQt6.QtCore import Qt, pyqtSignal, QThreadPool
import pandas as pd
import numpy as np
import joblib
import os

from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from xgboost import XGBClassifier, XGBRegressor
from sklearn.metrics import confusion_matrix, r2_score, mean_squared_error, accuracy_score
from sklearn.model_selection import RandomizedSearchCV

import pyqtgraph as pg
from utils.threads import Worker

TAB10_COLORS = [
    (31, 119, 180), (255, 127, 14), (44, 160, 44), (214, 39, 40),
    (148, 103, 189), (140, 86, 75), (227, 119, 194), (127, 127, 127),
    (188, 189, 34), (23, 190, 207)
]

def get_color(index, alpha=200):
    r, g, b = TAB10_COLORS[index % len(TAB10_COLORS)]
    return pg.mkColor(r, g, b, alpha)

def configure_plot(plot_widget):
    plot_widget.showAxis('top')
    plot_widget.showAxis('right')
    plot_widget.getAxis('top').setStyle(showValues=False)
    plot_widget.getAxis('right').setStyle(showValues=False)

class FormattedAxisItem(pg.AxisItem):
    def __init__(self, orientation, decimals=2, **kwargs):
        super().__init__(orientation, **kwargs)
        self.decimals = decimals
        
    def tickStrings(self, values, scale, spacing):
        try:
            return [f"{v:.{self.decimals}f}" for v in values]
        except:
            return super().tickStrings(values, scale, spacing)

class MachineLearningWidget(QWidget):
    model_loaded = pyqtSignal(dict)
    
    def __init__(self, panel, tech, parent=None):
        super().__init__(parent)
        self.panel = panel
        self.tech = tech
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.threadpool = QThreadPool()
        
        # --- Plot Area ---
        self.axis_x = FormattedAxisItem(orientation='bottom')
        self.axis_y = FormattedAxisItem(orientation='left')
        self.plot_widget = pg.PlotWidget(axisItems={'bottom': self.axis_x, 'left': self.axis_y})
        configure_plot(self.plot_widget)
        self.layout.addWidget(self.plot_widget, stretch=1)
        
        self.last_df = None
        self.last_features = []
        self.last_x = None
        self.last_y = None
        self.last_color = None
        self.last_props = {}
        
        self.trained_model = None
        self.model_features = None
        self.last_results_df = None
        
    def populate_target_combo(self, df):
        if df is None: return
        current = self.panel.combo_target.currentText()
        self.panel.combo_target.blockSignals(True)
        self.panel.combo_target.clear()
        self.panel.combo_target.addItems(df.columns.tolist())
        if current in df.columns:
            self.panel.combo_target.setCurrentText(current)
        self.panel.combo_target.blockSignals(False)
        
    def trigger_replot(self):
        if self.last_df is not None:
            self.plot_data(self.last_df, self.last_features, self.last_x, self.last_y, self.last_color, self.last_props)
            
    def _get_clean_data(self, for_training=False):
        if self.last_df is None or self.last_df.empty:
            return None, None, "No data loaded into the ML module. Please click 'Update Plot' to initialize."
            
        valid_features = [f for f in self.last_features if f in self.last_df.columns and pd.api.types.is_numeric_dtype(self.last_df[f])]
        if len(valid_features) < 1:
            return None, None, "Please check at least 1 numeric variable in the 'All Variables' list."
            
        tech = self.tech
        is_unsup = tech in ["PCA", "K-Means"]
        
        needed_cols = list(set(valid_features))
        if not is_unsup and for_training:
            target = self.panel.combo_target.currentText()
            if not target:
                return None, None, "No target variable selected."
            needed_cols.append(target)
            if target in valid_features:
                valid_features.remove(target)
            
        if is_unsup and tech == "K-Means":
            if self.last_x and self.last_x in self.last_df.columns: needed_cols.append(self.last_x)
            if self.last_y and self.last_y in self.last_df.columns: needed_cols.append(self.last_y)
            
        if is_unsup and self.last_color and self.last_color != "None" and self.last_color in self.last_df.columns:
            needed_cols.append(self.last_color)
            
        needed_cols = list(set([c for c in needed_cols if c in self.last_df.columns]))
        clean_df = self.last_df.dropna(subset=needed_cols).copy()
        
        if clean_df.empty:
            return None, None, "All rows contain missing values (NaN) in the selected variables."
            
        return clean_df, valid_features, None

    def _show_error(self, msg):
        self.plot_widget.clear()
        text = pg.TextItem(msg, color='r', anchor=(0.5, 0.5))
        self.plot_widget.addItem(text)

    def plot_data(self, df, features, x_col, y_col, color_col, props):
        self.last_df = df
        self.last_features = features
        self.last_x = x_col
        self.last_y = y_col
        self.last_color = color_col
        self.last_props = props
        
        self.axis_x.decimals = props.get('decimals_x', 2)
        self.axis_y.decimals = props.get('decimals_y', 2)
        
        self.populate_target_combo(df)
        
        tech = self.tech
        if tech in ["PCA", "K-Means"]:
            self._plot_unsupervised()
        else:
            self._plot_supervised_inference()
            
    def _plot_unsupervised(self):
        self.plot_widget.clear()
        clean_df, valid_features, err = self._get_clean_data()
        if err:
            self._show_error(err)
            return
            
        tech = self.tech
        X = clean_df[valid_features].values
        
        c_base = pg.mkColor(self.last_props.get('color_base', '#1f77b4'))
        point_size = self.last_props.get('point_size', 5)
        
        self.plot_widget.showGrid(x=self.last_props.get('show_grid_x', True), y=self.last_props.get('show_grid_y', True), alpha=0.3)
        self.plot_widget.addLegend()
        
        try:
            if tech == "PCA":
                if len(valid_features) < 2:
                    self._show_error("PCA requires at least 2 numeric features.")
                    return
                pca = PCA(n_components=2)
                components = pca.fit_transform(X)
                clean_df['PC1'] = components[:, 0]
                clean_df['PC2'] = components[:, 1]
                var_ratio = pca.explained_variance_ratio_ * 100
                
                hue_val = self.last_color if self.last_color and self.last_color != "None" and self.last_color in clean_df.columns else None
                
                if hue_val:
                    groups = clean_df.groupby(hue_val)
                    i = 0
                    for name, group in groups:
                        scatter = pg.ScatterPlotItem(x=group['PC1'].values, y=group['PC2'].values, 
                                                     size=point_size, pen=None, brush=get_color(i), name=str(name))
                        self.plot_widget.addItem(scatter)
                        i += 1
                else:
                    scatter = pg.ScatterPlotItem(x=clean_df['PC1'].values, y=clean_df['PC2'].values, 
                                                 size=point_size, pen=None, brush=c_base)
                    self.plot_widget.addItem(scatter)
                    
                self.plot_widget.setLabel('bottom', f"PC1 ({var_ratio[0]:.1f}%)")
                self.plot_widget.setLabel('left', f"PC2 ({var_ratio[1]:.1f}%)")
                self.plot_widget.setTitle(self.last_props.get('custom_title') or "PCA Plot")
                
            elif tech == "K-Means":
                k = self.panel.spin_k.value()
                kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
                clusters = kmeans.fit_predict(X)
                clean_df['Cluster'] = [f"Cluster {c+1}" for c in clusters]
                
                plot_x = self.last_x if self.last_x and self.last_x in clean_df.columns else valid_features[0]
                plot_y = self.last_y if self.last_y and self.last_y in clean_df.columns else valid_features[1] if len(valid_features) > 1 else valid_features[0]
                
                groups = clean_df.groupby('Cluster')
                i = 0
                for name, group in groups:
                    scatter = pg.ScatterPlotItem(x=group[plot_x].values, y=group[plot_y].values, 
                                                 size=point_size, pen=None, brush=get_color(i), name=str(name))
                    self.plot_widget.addItem(scatter)
                    i += 1
                    
                if plot_x in valid_features and plot_y in valid_features:
                    idx_x = valid_features.index(plot_x)
                    idx_y = valid_features.index(plot_y)
                    centers_x = kmeans.cluster_centers_[:, idx_x]
                    centers_y = kmeans.cluster_centers_[:, idx_y]
                    centroids = pg.ScatterPlotItem(x=centers_x, y=centers_y, size=point_size*2, pen=pg.mkPen('k', width=2), brush='r', symbol='x', name='Centroids')
                    self.plot_widget.addItem(centroids)
                
                self.plot_widget.setLabel('bottom', self.last_props.get('custom_xlabel') or plot_x)
                self.plot_widget.setLabel('left', self.last_props.get('custom_ylabel') or plot_y)
                self.plot_widget.setTitle(self.last_props.get('custom_title') or f"K-Means Clustering (K={k})")
            
            self.last_results_df = clean_df
        except Exception as e:
            self._show_error(f"Unsupervised Error:\n{str(e)}")

    def train_model(self):
        clean_df, valid_features, err = self._get_clean_data(for_training=True)
        if err:
            QMessageBox.warning(self, "Training Error", err)
            return
            
        target = self.panel.combo_target.currentText()
        task = self.panel.combo_task.currentText()
        tech = self.tech
        
        X = clean_df[valid_features].values
        y = clean_df[target].values
        
        if task == "Classification":
            if pd.api.types.is_numeric_dtype(clean_df[target]) and clean_df[target].nunique() > 20:
                resp = QMessageBox.question(self, "Warning", "Target has many unique numeric values. Are you sure you want Classification?",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if resp == QMessageBox.StandardButton.No: return
                
        self.panel.btn_train.setEnabled(False)
        self.panel.btn_train.setText("Training...")
        self.panel.progress_bar.show()
        
        worker = Worker(self._do_train_model, X, y, clean_df, valid_features, target, task, tech)
        worker.signals.result.connect(self._on_train_success)
        worker.signals.error.connect(self._on_train_error)
        self.threadpool.start(worker)

    def _do_train_model(self, X, y, clean_df, valid_features, target, task, tech):
        if tech == "K-Nearest Neighbors":
            model = KNeighborsClassifier(n_neighbors=self.panel.spin_k.value()) if task == "Classification" else KNeighborsRegressor(n_neighbors=self.panel.spin_k.value())
        elif tech == "Random Forest":
            model = RandomForestClassifier(n_estimators=self.panel.spin_trees.value(), max_depth=self.panel.spin_depth.value(), random_state=42) if task == "Classification" else RandomForestRegressor(n_estimators=self.panel.spin_trees.value(), max_depth=self.panel.spin_depth.value(), random_state=42)
        elif tech == "XGBoost":
            if task == "Classification":
                if not pd.api.types.is_numeric_dtype(y):
                    y = pd.Categorical(y).codes
                model = XGBClassifier(n_estimators=self.panel.spin_trees.value(), max_depth=self.panel.spin_depth.value(), learning_rate=self.panel.spin_lr.value(), random_state=42)
            else:
                model = XGBRegressor(n_estimators=self.panel.spin_trees.value(), max_depth=self.panel.spin_depth.value(), learning_rate=self.panel.spin_lr.value(), random_state=42)
        
        model.fit(X, y)
        return model, valid_features, target, task, tech, clean_df, y

    def _on_train_success(self, result):
        model, valid_features, target, task, tech, clean_df, y_true = result
        self.trained_model = model
        self.model_features = valid_features
        self.model_target = target
        self.model_task = task
        self.model_tech = tech
        
        self.panel.btn_train.setEnabled(True)
        self.panel.btn_train.setText("Train Model")
        self.panel.progress_bar.hide()
        QMessageBox.information(self, "Success", "Model trained successfully!")
        self._plot_supervised_inference(clean_df, valid_features, target, y_true)

    def _on_train_error(self, err_tuple):
        self.panel.btn_train.setEnabled(True)
        self.panel.btn_train.setText("Train Model")
        self.panel.progress_bar.hide()
        QMessageBox.critical(self, "Training Error", str(err_tuple[1]))

    def _plot_supervised_inference(self, clean_df=None, valid_features=None, target=None, y_true=None):
        self.plot_widget.clear()
        if not self.trained_model:
            self._show_error("No model trained or loaded yet.\nClick 'Train Model' or 'Load Model'.")
            return
            
        if clean_df is None:
            clean_df, valid_features, err = self._get_clean_data(for_training=True)
            if err:
                self._show_error(err)
                return
            target = self.panel.combo_target.currentText()
            y_true = clean_df[target].values
            
            if self.model_features and set(self.model_features) != set(valid_features):
                self._show_error(f"Feature mismatch!\nModel was trained on:\n{', '.join(self.model_features)}\n\nCurrently selected:\n{', '.join(valid_features)}")
                return
                
            if self.panel.combo_task.currentText() == "Classification" and self.tech == "XGBoost":
                if not pd.api.types.is_numeric_dtype(clean_df[target]):
                     y_true = pd.Categorical(clean_df[target]).codes

        try:
            X = clean_df[self.model_features].values
            y_pred = self.trained_model.predict(X)
            task = self.panel.combo_task.currentText()
            
            point_size = self.last_props.get('point_size', 5)
            c_base = pg.mkColor(self.last_props.get('color_base', '#1f77b4'))
            self.plot_widget.showGrid(x=self.last_props.get('show_grid_x', True), y=self.last_props.get('show_grid_y', True), alpha=0.3)
            
            if task == "Classification":
                cm = confusion_matrix(y_true, y_pred)
                acc = accuracy_score(y_true, y_pred)
                
                img = pg.ImageItem(cm)
                colormap = pg.colormap.get('plasma', source='matplotlib')
                img.setColorMap(colormap)
                self.plot_widget.addItem(img)
                
                # Add text annotations for confusion matrix
                for i in range(cm.shape[0]):
                    for j in range(cm.shape[1]):
                        txt = pg.TextItem(str(cm[i, j]), color='w' if cm[i,j] < cm.max()/2 else 'k', anchor=(0.5, 0.5))
                        txt.setPos(i + 0.5, j + 0.5)
                        self.plot_widget.addItem(txt)
                
                self.plot_widget.setLabel('bottom', "True Label (reversed axes)")
                self.plot_widget.setLabel('left', "Predicted Label")
                self.plot_widget.setTitle(self.last_props.get('custom_title') or f"Confusion Matrix (Accuracy: {acc:.1%})")
            else:
                r2 = r2_score(y_true, y_pred)
                rmse = np.sqrt(mean_squared_error(y_true, y_pred))
                
                scatter = pg.ScatterPlotItem(x=y_true, y=y_pred, size=point_size, pen=None, brush=c_base)
                self.plot_widget.addItem(scatter)
                
                min_val = min(np.min(y_true), np.min(y_pred))
                max_val = max(np.max(y_true), np.max(y_pred))
                line = pg.PlotDataItem([min_val, max_val], [min_val, max_val], pen=pg.mkPen('r', width=2, style=Qt.PenStyle.DashLine))
                self.plot_widget.addItem(line)
                
                self.plot_widget.setLabel('bottom', self.last_props.get('custom_xlabel') or f"True {target}")
                self.plot_widget.setLabel('left', self.last_props.get('custom_ylabel') or f"Predicted {target}")
                self.plot_widget.setTitle(self.last_props.get('custom_title') or f"Regression Performance (R²={r2:.3f}, RMSE={rmse:.2f})")
                
            res_df = clean_df.copy()
            res_df[f"True_{target}"] = y_true
            res_df[f"Predicted_{target}"] = y_pred
            self.last_results_df = res_df
        except Exception as e:
            self._show_error(f"Inference Error:\n{str(e)}")
            
    def save_model(self):
        if not self.trained_model:
            QMessageBox.warning(self, "Error", "No trained model available to save.")
            return
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Model", "", "Pickle Files (*.pkl)")
        if file_name:
            try:
                data = {
                    'model': self.trained_model,
                    'features': self.model_features,
                    'target': getattr(self, 'model_target', self.panel.combo_target.currentText()),
                    'task': getattr(self, 'model_task', self.panel.combo_task.currentText()),
                    'tech': getattr(self, 'model_tech', self.tech)
                }
                joblib.dump(data, file_name)
                QMessageBox.information(self, "Success", f"Model saved to {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save model:\n{str(e)}")
                
    def load_model(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Model", "", "Pickle Files (*.pkl)")
        if file_name:
            try:
                data = joblib.load(file_name)
                self.trained_model = data['model']
                self.model_features = data['features']
                self.model_target = data.get('target', '')
                self.model_task = data.get('task', '')
                self.model_tech = data.get('tech', '')
                
                QMessageBox.information(self, "Success", f"Model loaded successfully!\nExpected features: {', '.join(self.model_features)}")
                self.model_loaded.emit(data)
                self.trigger_replot()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load model:\n{str(e)}")

    def download_results(self):
        if self.last_results_df is None or self.last_results_df.empty:
            QMessageBox.warning(self, "Error", "No results available to download. Please generate a plot first.")
            return
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Results", "", "CSV Files (*.csv)")
        if file_name:
            try:
                self.last_results_df.to_csv(file_name, index=False)
                QMessageBox.information(self, "Success", f"Results successfully exported to {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export results:\n{str(e)}")

    def show_feature_importance(self):
        if not self.trained_model:
            QMessageBox.warning(self, "Error", "No trained model available.")
            return
        if not hasattr(self.trained_model, 'feature_importances_'):
            QMessageBox.warning(self, "Error", "Feature Importance is only available for Tree-based models.")
            return
            
        importances = self.trained_model.feature_importances_
        features = self.model_features
        indices = np.argsort(importances)[::-1]
        sorted_importances = importances[indices]
        sorted_features = [features[i] for i in indices]
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Feature Importance")
        dialog.resize(600, 400)
        
        layout = QVBoxLayout(dialog)
        plot = pg.PlotWidget()
        layout.addWidget(plot)
        
        bg = pg.BarGraphItem(x=np.arange(len(sorted_features)), height=sorted_importances, width=0.6, brush='b')
        plot.addItem(bg)
        plot.getAxis('bottom').setTicks([list(enumerate(sorted_features))])
        plot.setTitle("Feature Importance")
        
        dialog.exec()

    def auto_tune(self):
        clean_df, valid_features, err = self._get_clean_data(for_training=True)
        if err:
            self._show_error(err)
            return
            
        target = self.panel.combo_target.currentText()
        task = self.panel.combo_task.currentText()
        tech = self.tech
        
        X = clean_df[valid_features].values
        y = clean_df[target].values
        
        if task == "Classification":
            if not pd.api.types.is_numeric_dtype(y):
                y = pd.Categorical(y).codes
                
        param_dist = {}
        if tech == "K-Nearest Neighbors":
            model = KNeighborsClassifier() if task == "Classification" else KNeighborsRegressor()
            param_dist = {'n_neighbors': np.arange(2, 20)}
        elif tech == "Random Forest":
            model = RandomForestClassifier(random_state=42) if task == "Classification" else RandomForestRegressor(random_state=42)
            param_dist = {'n_estimators': [50, 100, 200, 300], 'max_depth': [None, 3, 5, 10, 20]}
        elif tech == "XGBoost":
            model = XGBClassifier(random_state=42) if task == "Classification" else XGBRegressor(random_state=42)
            param_dist = {'n_estimators': [50, 100, 200], 'max_depth': [3, 5, 10], 'learning_rate': [0.01, 0.05, 0.1, 0.2]}
        else: return
            
        self.panel.btn_autotune.setEnabled(False)
        self.panel.btn_autotune.setText("Tuning...")
        self.panel.progress_bar.show()
        
        worker = Worker(self._do_auto_tune, model, param_dist, X, y, tech)
        worker.signals.result.connect(self._on_tune_success)
        worker.signals.error.connect(self._on_tune_error)
        self.threadpool.start(worker)

    def _do_auto_tune(self, model, param_dist, X, y, tech):
        n_iter = 10 if tech != "K-Nearest Neighbors" else 5
        search = RandomizedSearchCV(model, param_distributions=param_dist, n_iter=n_iter, cv=3, random_state=42, n_jobs=-1)
        search.fit(X, y)
        return search.best_params_

    def _on_tune_success(self, best):
        self.panel.btn_autotune.setEnabled(True)
        self.panel.btn_autotune.setText("✨ Auto-Tune")
        self.panel.progress_bar.hide()
        if 'n_neighbors' in best: self.panel.spin_k.setValue(int(best['n_neighbors']))
        if 'n_estimators' in best: self.panel.spin_trees.setValue(int(best['n_estimators']))
        if 'max_depth' in best:
            depth = best['max_depth']
            self.panel.spin_depth.setValue(int(depth) if depth is not None else 50)
        if 'learning_rate' in best: self.panel.spin_lr.setValue(float(best['learning_rate']))
            
        QMessageBox.information(self, "Auto-Tune Complete", f"Best parameters found:\n{best}\n\nTraining final model...")
        self.train_model()

    def _on_tune_error(self, err_tuple):
        self.panel.btn_autotune.setEnabled(True)
        self.panel.btn_autotune.setText("✨ Auto-Tune")
        self.panel.progress_bar.hide()
        QMessageBox.critical(self, "Auto-Tune Error", str(err_tuple[1]))

    def predict_only(self):
        if not self.trained_model:
            QMessageBox.warning(self, "Error", "No trained model available. Train or Load a model first.")
            return
            
        clean_df, valid_features, err = self._get_clean_data(for_training=False)
        if err:
            QMessageBox.warning(self, "Error", err)
            return
            
        if self.model_features and not set(self.model_features).issubset(set(valid_features)):
            missing = set(self.model_features) - set(valid_features)
            QMessageBox.warning(self, "Feature Mismatch", f"Missing features required for prediction:\n{', '.join(missing)}")
            return
            
        try:
            X = clean_df[self.model_features].values
            y_pred = self.trained_model.predict(X)
            
            res_df = clean_df.copy()
            res_df[f"Predicted_{getattr(self, 'model_target', 'Target')}"] = y_pred
            self.last_results_df = res_df
            
            QMessageBox.information(self, "Success", "Predictions generated successfully!\nClick 'Download Results' to save the output CSV.")
        except Exception as e:
            QMessageBox.critical(self, "Prediction Error", str(e))
