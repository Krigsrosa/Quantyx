import os
import shutil
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QPushButton, QFileDialog, QMessageBox, QLabel)
from PyQt6.QtCore import Qt
from utils.config import get_templates_dir

class TemplateCenterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Template Center")
        self.resize(500, 400)
        self.templates_dir = get_templates_dir()
        
        self.setup_ui()
        self.load_templates()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        lbl = QLabel("Manage your PowerPoint Templates:")
        layout.addWidget(lbl)
        
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        
        btn_layout = QHBoxLayout()
        
        self.btn_add = QPushButton("Add Template...")
        self.btn_add.clicked.connect(self.add_template)
        
        self.btn_remove = QPushButton("Remove Selected")
        self.btn_remove.clicked.connect(self.remove_template)
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_remove)
        btn_layout.addStretch()
        
        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_close)
        
        layout.addLayout(btn_layout)
        
    def load_templates(self):
        self.list_widget.clear()
        for f in os.listdir(self.templates_dir):
            if f.endswith('.pptx'):
                self.list_widget.addItem(f)
                
    def add_template(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PowerPoint Template", "", "PowerPoint Files (*.pptx)")
        if file_path:
            filename = os.path.basename(file_path)
            dest_path = os.path.join(self.templates_dir, filename)
            
            if os.path.exists(dest_path):
                QMessageBox.warning(self, "Warning", f"Template '{filename}' already exists.")
                return
                
            try:
                shutil.copy2(file_path, dest_path)
                self.load_templates()
                QMessageBox.information(self, "Success", f"Template '{filename}' added successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to copy template: {str(e)}")
                
    def remove_template(self):
        selected = self.list_widget.currentItem()
        if not selected:
            return
            
        filename = selected.text()
        
        if filename == 'GlobalRD_Template.pptx':
            reply = QMessageBox.question(self, "Confirm", "Are you sure you want to remove the default template?", 
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return
                
        filepath = os.path.join(self.templates_dir, filename)
        try:
            os.remove(filepath)
            self.load_templates()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to remove template: {str(e)}")
