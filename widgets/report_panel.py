import os
import shutil
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QListWidget, 
                             QListWidgetItem, QFileDialog, QMessageBox, QLabel)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSize
from pptx import Presentation
from pptx.util import Inches

class ReportPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        self.temp_dir = "temp_report_images"
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
            
        self.images = []
        
        self.label = QLabel("Saved Plots for Presentation:")
        self.layout.addWidget(self.label)
        
        self.list_widget = QListWidget()
        self.list_widget.setViewMode(QListWidget.ViewMode.IconMode)
        self.list_widget.setIconSize(QSize(200, 150))
        self.list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.list_widget.setSpacing(10)
        self.layout.addWidget(self.list_widget)
        
        self.btn_clear = QPushButton("Clear Gallery")
        self.btn_clear.clicked.connect(self.clear_gallery)
        self.layout.addWidget(self.btn_clear)
        
        from PyQt6.QtWidgets import QHBoxLayout, QComboBox
        tpl_layout = QHBoxLayout()
        tpl_layout.addWidget(QLabel("Select Template:"))
        self.combo_template = QComboBox()
        tpl_layout.addWidget(self.combo_template)
        self.layout.addLayout(tpl_layout)
        
        self.btn_generate = QPushButton("Generate PowerPoint (PPTX)")
        self.btn_generate.setStyleSheet("background-color: #217346; color: white; font-weight: bold; padding: 10px;")
        self.btn_generate.clicked.connect(self.generate_pptx)
        self.layout.addWidget(self.btn_generate)
        
        self.load_templates()
        
    def load_templates(self):
        from utils.config import get_templates_dir
        self.combo_template.clear()
        d = get_templates_dir()
        for f in os.listdir(d):
            if f.endswith('.pptx'):
                self.combo_template.addItem(f, os.path.join(d, f))
                
    def add_image(self, file_path):
        self.images.append(file_path)
        item = QListWidgetItem()
        icon = QIcon(file_path)
        item.setIcon(icon)
        item.setText(f"Plot {len(self.images)}")
        self.list_widget.addItem(item)
        
    def clear_gallery(self):
        self.list_widget.clear()
        self.images = []
        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except:
                pass
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
        
    def generate_pptx(self):
        if not self.images:
            QMessageBox.warning(self, "Warning", "No images to add to the presentation!")
            return
            
        template_path = self.combo_template.currentData()
        if not template_path:
            QMessageBox.warning(self, "Warning", "Please select a template from the dropdown.")
            return
        
        if not os.path.exists(template_path):
            QMessageBox.critical(self, "Error", f"Template '{template_path}' not found.")
            return
            
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Presentation", "Analysis_Report.pptx", "PowerPoint (*.pptx)")
        if not save_path:
            return
            
        try:
            prs = Presentation(template_path)
            
            blank_slide_layout = None
            for layout in prs.slide_layouts:
                name = layout.name.lower()
                if 'blank' in name or 'vazio' in name or 'em branco' in name:
                    blank_slide_layout = layout
                    break
            
            if not blank_slide_layout:
                try:
                    blank_slide_layout = prs.slide_layouts[6]
                except:
                    try:
                        blank_slide_layout = prs.slide_layouts[5]
                    except:
                        blank_slide_layout = prs.slide_layouts[1]
            
            for img_path in self.images:
                slide = prs.slides.add_slide(blank_slide_layout)
                
                slide_width = prs.slide_width
                slide_height = prs.slide_height
                
                margin = Inches(0.5)
                max_width = slide_width - margin * 2
                max_height = slide_height - margin * 2
                
                pic = slide.shapes.add_picture(img_path, margin, margin, width=max_width)
                
                if pic.height < max_height:
                    pic.top = int((slide_height - pic.height) / 2)
                    
            prs.save(save_path)
            QMessageBox.information(self, "Success", f"Presentation successfully saved to:\n{save_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error generating PPTX", str(e))