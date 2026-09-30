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
        
        # Saved Queries section
        query_layout = QHBoxLayout()
        query_layout.addWidget(QLabel("Saved Queries:"))
        
        from PyQt6.QtWidgets import QComboBox, QInputDialog
        self.combo_queries = QComboBox()
        self.combo_queries.currentIndexChanged.connect(self.on_query_selected)
        query_layout.addWidget(self.combo_queries)
        
        self.btn_save_query = QPushButton("Save Query As...")
        self.btn_save_query.clicked.connect(self.save_current_query)
        query_layout.addWidget(self.btn_save_query)
        
        self.btn_delete_query = QPushButton("Delete")
        self.btn_delete_query.clicked.connect(self.delete_current_query)
        query_layout.addWidget(self.btn_delete_query)
        
        layout.addLayout(query_layout)
        
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
            
        self.load_queries()
        
    def load_queries(self):
        self.combo_queries.blockSignals(True)
        self.combo_queries.clear()
        self.combo_queries.addItem("-- Select a Query --")
        
        self.settings.beginGroup("queries")
        for key in self.settings.childKeys():
            self.combo_queries.addItem(key, self.settings.value(key))
        self.settings.endGroup()
        self.combo_queries.blockSignals(False)

    def on_query_selected(self, index):
        if index > 0:
            query_text = self.combo_queries.itemData(index)
            if query_text:
                self.edit_query.setPlainText(query_text)
                
    def save_current_query(self):
        query_text = self.edit_query.toPlainText().strip()
        if not query_text:
            QMessageBox.warning(self, "Warning", "Cannot save an empty query.")
            return
            
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "Save Query", "Enter a name for this query:")
        if ok and name.strip():
            name = name.strip()
            self.settings.beginGroup("queries")
            self.settings.setValue(name, query_text)
            self.settings.endGroup()
            
            self.load_queries()
            idx = self.combo_queries.findText(name)
            if idx >= 0:
                self.combo_queries.blockSignals(True)
                self.combo_queries.setCurrentIndex(idx)
                self.combo_queries.blockSignals(False)
                
    def delete_current_query(self):
        idx = self.combo_queries.currentIndex()
        if idx > 0:
            name = self.combo_queries.itemText(idx)
            reply = QMessageBox.question(self, "Delete Query", f"Are you sure you want to delete '{name}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.settings.beginGroup("queries")
                self.settings.remove(name)
                self.settings.endGroup()
                self.load_queries()
                self.edit_query.clear()
            
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
