"""
Quantyx Documentation System - Interactive User Guide Dialog
Interactive help window with topic navigation, real-time search,
styled documentation viewer, and PDF/DOCX export capabilities.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget, QListWidgetItem,
    QTextBrowser, QLineEdit, QPushButton, QLabel, QWidget, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QKeySequence, QShortcut

from ui.help_content import get_all_topics, get_topic_by_id, search_topics
from ui.doc_exporter import build_full_html_document, export_to_pdf, export_to_docx
from utils.version import __version__
from utils.theme_manager import ThemeManager

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Quantyx - User Guide & Technical Documentation (v{__version__})")
        self.resize(1150, 780)
        self.setMinimumSize(850, 600)
        
        self.is_dark = ThemeManager.is_dark()
        self.current_topic_id = "intro"
        self.all_topics = get_all_topics()
        
        self.setup_ui()
        self.apply_theme()
        self.populate_topics()
        self.load_topic("intro")
        
        # Shortcut Ctrl+F to focus search
        self.shortcut_find = QShortcut(QKeySequence("Ctrl+F"), self)
        self.shortcut_find.activated.connect(self.focus_search)
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(10)
        
        # --- 1. Top Bar (Header & Actions) ---
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)
        
        # Guide Title
        title_box = QVBoxLayout()
        title_box.setSpacing(1)
        lbl_title = QLabel("📘 Quantyx Documentation Center")
        lbl_title.setStyleSheet("font-size: 17px; font-weight: bold; color: #3498db;")
        lbl_subtitle = QLabel(f"Comprehensive User Guide & Technical Reference • v{__version__}")
        lbl_subtitle.setStyleSheet("font-size: 11px; color: gray;")
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_subtitle)
        top_bar.addLayout(title_box)
        
        top_bar.addStretch()
        
        # Real-time search field
        self.edit_search = QLineEdit()
        self.edit_search.setPlaceholderText("🔍 Search guide (Ctrl+F)... e.g. Isolation Forest, Multi-Output, PCA")
        self.edit_search.setMinimumWidth(340)
        self.edit_search.setClearButtonEnabled(True)
        self.edit_search.textChanged.connect(self.on_search_text_changed)
        top_bar.addWidget(self.edit_search)
        
        # Export Buttons
        self.btn_export_pdf = QPushButton("📄 Export PDF")
        self.btn_export_pdf.setToolTip("Export the complete formatted manual as a high-resolution PDF document.")
        self.btn_export_pdf.setStyleSheet("font-weight: bold; padding: 6px 12px; background-color: #2980b9; color: white; border-radius: 4px;")
        self.btn_export_pdf.clicked.connect(lambda: export_to_pdf(self))
        top_bar.addWidget(self.btn_export_pdf)
        
        self.btn_export_docx = QPushButton("📝 Export Word")
        self.btn_export_docx.setToolTip("Export the complete manual as a structured Microsoft Word (.docx) document.")
        self.btn_export_docx.setStyleSheet("font-weight: bold; padding: 6px 12px; background-color: #27ae60; color: white; border-radius: 4px;")
        self.btn_export_docx.clicked.connect(lambda: export_to_docx(self))
        top_bar.addWidget(self.btn_export_docx)
        
        main_layout.addLayout(top_bar)
        
        # Divider line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)
        
        # --- 2. Central Splitter (Topics on left, Content on right) ---
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left Panel (Topic List)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)
        
        self.lbl_topics_count = QLabel(f"Documentation Topics ({len(self.all_topics)})")
        self.lbl_topics_count.setStyleSheet("font-weight: bold; font-size: 12px; color: #7f8c8d;")
        left_layout.addWidget(self.lbl_topics_count)
        
        self.topic_list = QListWidget()
        self.topic_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.topic_list.itemClicked.connect(self.on_topic_selected)
        left_layout.addWidget(self.topic_list)
        
        # Button to switch between single topic and full manual
        self.btn_full_manual = QPushButton("📖 View Full Manual")
        self.btn_full_manual.setToolTip("Display all 25 sections in a continuous scroll view.")
        self.btn_full_manual.clicked.connect(self.load_full_manual)
        left_layout.addWidget(self.btn_full_manual)
        
        self.splitter.addWidget(left_widget)
        
        # Right Panel (Documentation Browser)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)
        
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.browser.setSearchPaths([])
        right_layout.addWidget(self.browser)
        
        self.splitter.addWidget(right_widget)
        self.splitter.setSizes([320, 800])
        main_layout.addWidget(self.splitter, stretch=1)
        
        # --- 3. Bottom Bar (Status & Close) ---
        bottom_bar = QHBoxLayout()
        lbl_hint = QLabel("💡 Tip: Use quick search to locate specific parameters, or click 'Export' to generate an offline manual.")
        lbl_hint.setStyleSheet("font-size: 11px; color: gray;")
        bottom_bar.addWidget(lbl_hint)
        
        bottom_bar.addStretch()
        
        self.btn_close = QPushButton("Close")
        self.btn_close.setFixedWidth(100)
        self.btn_close.clicked.connect(self.accept)
        bottom_bar.addWidget(self.btn_close)
        
        main_layout.addLayout(bottom_bar)
        
    def focus_search(self):
        self.edit_search.setFocus()
        self.edit_search.selectAll()

    def apply_theme(self):
        bg = "#1e1e1e" if self.is_dark else "#ffffff"
        fg = "#f0f0f0" if self.is_dark else "#2c3e50"
        list_bg = "#252526" if self.is_dark else "#f8f9fa"
        border_col = "#3e3e42" if self.is_dark else "#dcdde1"
        item_hover = "#2a2d2e" if self.is_dark else "#e8ecf1"
        item_selected = "#094771" if self.is_dark else "#3498db"
        
        self.topic_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {list_bg};
                color: {fg};
                border: 1px solid {border_col};
                border-radius: 4px;
                padding: 4px;
                font-size: 12px;
            }}
            QListWidget::item {{
                padding: 7px 8px;
                border-radius: 4px;
                margin-bottom: 2px;
            }}
            QListWidget::item:hover {{
                background-color: {item_hover};
            }}
            QListWidget::item:selected {{
                background-color: {item_selected};
                color: white;
                font-weight: bold;
            }}
        """)
        
        self.browser.setStyleSheet(f"""
            QTextBrowser {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {border_col};
                border-radius: 4px;
                padding: 12px;
            }}
        """)
        
        self.edit_search.setStyleSheet(f"""
            QLineEdit {{
                padding: 6px 10px;
                border: 1px solid {border_col};
                border-radius: 4px;
                background-color: {list_bg};
                color: {fg};
                font-size: 12px;
            }}
        """)

    def populate_topics(self, filtered_topics=None):
        self.topic_list.blockSignals(True)
        self.topic_list.clear()
        
        topics_to_show = filtered_topics if filtered_topics is not None else self.all_topics
        self.lbl_topics_count.setText(f"Documentation Topics ({len(topics_to_show)})")
        
        for topic in topics_to_show:
            item = QListWidgetItem(topic["title"])
            item.setData(Qt.ItemDataRole.UserRole, topic["id"])
            item.setToolTip(topic["summary"])
            self.topic_list.addItem(item)
            
        self.topic_list.blockSignals(False)
        
        # Selecionar o primeiro item se houver
        if self.topic_list.count() > 0:
            self.topic_list.setCurrentRow(0)

    def on_search_text_changed(self, text):
        query = text.strip()
        if not query:
            self.populate_topics()
            self.load_topic(self.current_topic_id)
            return
            
        filtered = search_topics(query)
        self.populate_topics(filtered)
        
        if filtered:
            self.load_topic(filtered[0]["id"])
            # Tentar destacar a busca no texto do navegador
            self.browser.find(query)

    def on_topic_selected(self, item):
        topic_id = item.data(Qt.ItemDataRole.UserRole)
        if topic_id:
            self.load_topic(topic_id)

    def get_styled_html_for_topic(self, topic):
        bg_color = "#1e1e1e" if self.is_dark else "#ffffff"
        text_color = "#e0e0e0" if self.is_dark else "#2c3e50"
        heading_color = "#63b3ed" if self.is_dark else "#1a365d"
        subheading_color = "#90cdf4" if self.is_dark else "#2b6cb0"
        border_color = "#4a5568" if self.is_dark else "#e2e8f0"
        box_bg = "#2d3748" if self.is_dark else "#f7fafc"
        tip_bg = "#2a4365" if self.is_dark else "#ebf8ff"
        table_hdr_bg = "#2d3748" if self.is_dark else "#edf2f7"
        
        css = f"""
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            font-size: 13px;
            line-height: 1.6;
            color: {text_color};
            background-color: {bg_color};
            margin: 15px;
        }}
        h2 {{
            color: {heading_color};
            font-size: 20px;
            border-bottom: 2px solid {border_color};
            padding-bottom: 6px;
            margin-top: 5px;
            margin-bottom: 12px;
        }}
        h3 {{
            color: {subheading_color};
            font-size: 15px;
            margin-top: 18px;
            margin-bottom: 8px;
        }}
        h4 {{
            color: {subheading_color};
            font-size: 13px;
            margin-top: 12px;
            margin-bottom: 4px;
        }}
        p {{
            margin-bottom: 10px;
        }}
        ul, ol {{
            margin-top: 4px;
            margin-bottom: 12px;
            padding-left: 24px;
        }}
        li {{
            margin-bottom: 4px;
        }}
        code {{
            background-color: {box_bg};
            padding: 2px 5px;
            border-radius: 4px;
            font-family: "Cascadia Code", Consolas, "Courier New", monospace;
            font-size: 12px;
        }}
        .note-box {{
            background-color: {box_bg};
            border-left: 4px solid #3182ce;
            padding: 10px 14px;
            margin: 12px 0;
            border-radius: 3px;
        }}
        .tip-box {{
            background-color: {tip_bg};
            border-left: 4px solid #38a169;
            padding: 10px 14px;
            margin: 12px 0;
            border-radius: 3px;
        }}
        .tutorial-box {{
            background-color: {box_bg};
            border: 1px solid {border_color};
            border-left: 4px solid #d69e2e;
            padding: 12px 16px;
            margin: 16px 0;
            border-radius: 4px;
        }}
        .model-card {{
            background-color: {box_bg};
            border: 1px solid {border_color};
            border-left: 4px solid #805ad5;
            padding: 12px 16px;
            margin: 16px 0;
            border-radius: 4px;
        }}
        .faq-item {{
            background-color: {box_bg};
            border: 1px solid {border_color};
            padding: 10px 14px;
            margin: 10px 0;
            border-radius: 4px;
        }}
        table.doc-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 14px 0;
            font-size: 12px;
        }}
        table.doc-table th {{
            background-color: {table_hdr_bg};
            color: {heading_color};
            font-weight: bold;
            text-align: left;
            padding: 8px 10px;
            border: 1px solid {border_color};
        }}
        table.doc-table td {{
            padding: 7px 10px;
            border: 1px solid {border_color};
            vertical-align: top;
        }}
        """
        
        html = f"""<!DOCTYPE html><html><head><meta charset='utf-8'><style>{css}</style></head><body>
        <div style='margin-bottom: 10px;'>
            <span style='background-color: #3182ce; color: white; padding: 2px 8px; border-radius: 3px; font-size: 10px; font-weight: bold; text-transform: uppercase;'>{topic['category']}</span>
        </div>
        {topic['content_html']}
        </body></html>"""
        return html

    def load_topic(self, topic_id):
        self.current_topic_id = topic_id
        topic = get_topic_by_id(topic_id)
        if topic:
            html = self.get_styled_html_for_topic(topic)
            self.browser.setHtml(html)
            
            # Sincronizar seleção na lista se necessário
            for i in range(self.topic_list.count()):
                item = self.topic_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == topic_id:
                    self.topic_list.setCurrentItem(item)
                    break

    def load_full_manual(self):
        html = build_full_html_document(is_dark=self.is_dark)
        self.browser.setHtml(html)
