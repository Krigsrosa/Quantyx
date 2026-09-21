import pandas as pd
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QTextEdit, QPushButton, QCheckBox, QMessageBox, QProgressBar)
from PyQt6.QtCore import Qt, QSettings, QThread, pyqtSignal
from databricks import sql

class SQLWorker(QThread):
    finished = pyqtSignal(object) # sends df or None
    error = pyqtSignal(str)
    
    def __init__(self, hostname, http_path, token, query):
        super().__init__()
        self.hostname = hostname
        self.http_path = http_path
        self.token = token
        self.query = query
        
    def run(self):
        try:
            connection = sql.connect(
                server_hostname=self.hostname,
                http_path=self.http_path,
                access_token=self.token
            )
            cursor = connection.cursor()
            cursor.execute(self.query)
            
            # Fetch data and column names
            rows = cursor.fetchall()
            cols = [desc[0] for desc in cursor.description]
            
            df = pd.DataFrame(rows, columns=cols)
            
            cursor.close()
            connection.close()
            
            self.finished.emit(df)
            
        except Exception as e:
            self.error.emit(str(e))

class SQLDialog(QDialog):
    data_fetched = pyqtSignal(object) # emit the pandas dataframe
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Data from Databricks SQL")
        self.resize(600, 500)
        self.settings = QSettings("Quantyx", "SQLCredentials")
        
        self.setup_ui()
        self.load_credentials()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Server Hostname
        layout.addWidget(QLabel("Server Hostname:"))
        self.edit_host = QLineEdit()
        layout.addWidget(self.edit_host)
        
        # HTTP Path
        layout.addWidget(QLabel("HTTP Path:"))
        self.edit_path = QLineEdit()
        layout.addWidget(self.edit_path)
        
        # Access Token
        layout.addWidget(QLabel("Access Token:"))
        self.edit_token = QLineEdit()
        self.edit_token.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.edit_token)
        
        # Save credentials
        self.chk_save = QCheckBox("Save Credentials")
        layout.addWidget(self.chk_save)
        
        # Query
        layout.addWidget(QLabel("SQL Query:"))
        self.edit_query = QTextEdit()
        layout.addWidget(self.edit_query)
        
        # Progress Bar (hidden by default)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.hide()
        layout.addWidget(self.progress)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_run = QPushButton("Run Query")
        self.btn_run.clicked.connect(self.run_query)
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_run)
        
        layout.addLayout(btn_layout)
        
    def load_credentials(self):
        saved = self.settings.value("save_creds", False, type=bool)
        if saved:
            self.chk_save.setChecked(True)
            self.edit_host.setText(self.settings.value("hostname", ""))
            self.edit_path.setText(self.settings.value("http_path", ""))
            self.edit_token.setText(self.settings.value("token", ""))
            
    def run_query(self):
        host = self.edit_host.text().strip()
        path = self.edit_path.text().strip()
        token = self.edit_token.text().strip()
        query = self.edit_query.toPlainText().strip()
        
        if not all([host, path, token, query]):
            QMessageBox.warning(self, "Warning", "Please fill in all fields.")
            return
            
        if self.chk_save.isChecked():
            self.settings.setValue("save_creds", True)
            self.settings.setValue("hostname", host)
            self.settings.setValue("http_path", path)
            self.settings.setValue("token", token)
        else:
            self.settings.setValue("save_creds", False)
            self.settings.remove("hostname")
            self.settings.remove("http_path")
            self.settings.remove("token")
            
        self.btn_run.setEnabled(False)
        self.progress.show()
        
        self.worker = SQLWorker(host, path, token, query)
        self.worker.finished.connect(self.on_query_success)
        self.worker.error.connect(self.on_query_error)
        self.worker.start()
        
    def on_query_success(self, df):
        self.progress.hide()
        self.btn_run.setEnabled(True)
        self.data_fetched.emit(df)
        self.accept()
        
    def on_query_error(self, err_msg):
        self.progress.hide()
        self.btn_run.setEnabled(True)
        QMessageBox.critical(self, "Query Error", f"An error occurred while executing the query:\n{err_msg}")
