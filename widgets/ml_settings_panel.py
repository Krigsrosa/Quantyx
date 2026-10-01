from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QComboBox, QLabel, 
                             QSpinBox, QPushButton, QDoubleSpinBox, QProgressBar, QHBoxLayout)
from PyQt6.QtCore import pyqtSignal

class MLSettingsPanel(QWidget):
    # We will emit signals that main_window catches to call the correct function on the active MachineLearningWidget
    train_requested = pyqtSignal()
    predict_requested = pyqtSignal()
    autotune_requested = pyqtSignal()
    importance_requested = pyqtSignal()
    save_requested = pyqtSignal()
    load_requested = pyqtSignal()
    download_requested = pyqtSignal()
    return_requested = pyqtSignal()
    update_plot_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        self.combo_task = QComboBox()
        self.combo_task.addItems(["Classification", "Regression"])
        
        self.combo_target = QComboBox()
        
        self.spin_k = QSpinBox()
        self.spin_k.setRange(2, 50)
        self.spin_k.setValue(3)
        self.lbl_k = QLabel("K:")
        
        self.spin_trees = QSpinBox()
        self.spin_trees.setRange(10, 1000)
        self.spin_trees.setValue(100)
        self.lbl_trees = QLabel("Trees:")
        
        self.spin_depth = QSpinBox()
        self.spin_depth.setRange(1, 100)
        self.spin_depth.setValue(6)
        self.lbl_depth = QLabel("Max Depth:")
        
        self.spin_lr = QDoubleSpinBox()
        self.spin_lr.setRange(0.001, 1.0)
        self.spin_lr.setSingleStep(0.05)
        self.spin_lr.setValue(0.1)
        self.lbl_lr = QLabel("Learning Rate:")
        
        self.btn_train = QPushButton("Train Model")
        self.btn_train.clicked.connect(self.train_requested.emit)
        
        self.btn_predict = QPushButton("Predict")
        self.btn_predict.clicked.connect(self.predict_requested.emit)
        
        self.btn_autotune = QPushButton("✨ Auto-Tune")
        self.btn_autotune.clicked.connect(self.autotune_requested.emit)
        
        self.btn_importance = QPushButton("Feature Importance")
        self.btn_importance.clicked.connect(self.importance_requested.emit)
        
        self.btn_save = QPushButton("Save Model")
        self.btn_save.clicked.connect(self.save_requested.emit)
        
        self.btn_load = QPushButton("Load Model")
        self.btn_load.clicked.connect(self.load_requested.emit)
        
        self.btn_download = QPushButton("Download Results")
        self.btn_download.clicked.connect(self.download_requested.emit)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()
        
        # Layouts

        self.btn_return = QPushButton("⬅ Return to Data Exploration")
        self.btn_return.setStyleSheet("background-color: #2c3e50; color: white; font-weight: bold;")
        self.btn_return.clicked.connect(self.return_requested.emit)
        self.layout.addWidget(self.btn_return)
        self.layout.addSpacing(10)
        

        self.btn_update = QPushButton("Update Plot")
        self.btn_update.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
        self.btn_update.clicked.connect(self.update_plot_requested.emit)
        self.layout.addWidget(self.btn_update)
        
        self.w_task = QWidget()


        l_task = QHBoxLayout(self.w_task)
        l_task.setContentsMargins(0,0,0,0)
        l_task.addWidget(QLabel("Task:"))
        l_task.addWidget(self.combo_task)
        self.layout.addWidget(self.w_task)
        
        self.w_target = QWidget()
        l_target = QHBoxLayout(self.w_target)
        l_target.setContentsMargins(0,0,0,0)
        l_target.addWidget(QLabel("Target (Y):"))
        l_target.addWidget(self.combo_target)
        self.layout.addWidget(self.w_target)
        
        self.layout.addSpacing(15)
        self.layout.addWidget(self.lbl_k)
        self.layout.addWidget(self.spin_k)
        self.layout.addWidget(self.lbl_trees)
        self.layout.addWidget(self.spin_trees)
        self.layout.addWidget(self.lbl_depth)
        self.layout.addWidget(self.spin_depth)
        self.layout.addWidget(self.lbl_lr)
        self.layout.addWidget(self.spin_lr)
        
        self.layout.addSpacing(15)
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.btn_train)
        self.layout.addWidget(self.btn_autotune)
        self.layout.addWidget(self.btn_predict)
        self.layout.addWidget(self.btn_importance)
        self.layout.addWidget(self.btn_save)
        self.layout.addWidget(self.btn_load)
        self.layout.addWidget(self.btn_download)
        
        self.layout.addStretch()
        
    def set_technique(self, tech):
        is_unsup = tech in ["PCA", "K-Means"]
        
        self.w_task.setVisible(not is_unsup)
        self.w_target.setVisible(not is_unsup)
        self.btn_train.setVisible(not is_unsup)
        self.btn_autotune.setVisible(not is_unsup)
        self.btn_predict.setVisible(not is_unsup)
        self.btn_save.setVisible(not is_unsup)
        self.btn_load.setVisible(not is_unsup)
        
        self.lbl_k.setVisible(tech in ["K-Means", "K-Nearest Neighbors"])
        self.spin_k.setVisible(tech in ["K-Means", "K-Nearest Neighbors"])
        self.lbl_trees.setVisible(tech in ["Random Forest", "XGBoost"])
        self.spin_trees.setVisible(tech in ["Random Forest", "XGBoost"])
        self.lbl_depth.setVisible(tech in ["Random Forest", "XGBoost"])
        self.spin_depth.setVisible(tech in ["Random Forest", "XGBoost"])
        self.lbl_lr.setVisible(tech == "XGBoost")
        self.spin_lr.setVisible(tech == "XGBoost")
        self.lbl_lr.setVisible(tech == "XGBoost")
        self.spin_lr.setVisible(tech == "XGBoost")
        self.btn_importance.setVisible(tech in ["Random Forest", "XGBoost"])
        self.btn_update.setVisible(tech in ["PCA", "K-Means"])
        
    def populate_target(self, df):
        if df is None: return
        current = self.combo_target.currentText()
        self.combo_target.blockSignals(True)
        self.combo_target.clear()
        self.combo_target.addItems(df.columns.tolist())
        if current in df.columns:
            self.combo_target.setCurrentText(current)
        self.combo_target.blockSignals(False)
