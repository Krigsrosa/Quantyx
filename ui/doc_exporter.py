"""
Quantyx Documentation Exporter
Official User Guide exporter for PDF (via QPrinter) and DOCX (via python-docx) formats.
"""

import os
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtGui import QTextDocument
from PyQt6.QtPrintSupport import QPrinter
from ui.help_content import get_all_topics
from utils.version import __version__

def build_full_html_document(is_dark=False):
    """
    Constructs a complete unified HTML document containing all 25 sections,
    professional typographic styling, and headers for export or continuous reading.
    """
    topics = get_all_topics()
    
    bg_color = "#ffffff" if not is_dark else "#1e1e1e"
    text_color = "#2c3e50" if not is_dark else "#e0e0e0"
    heading_color = "#1a365d" if not is_dark else "#63b3ed"
    subheading_color = "#2b6cb0" if not is_dark else "#90cdf4"
    border_color = "#e2e8f0" if not is_dark else "#4a5568"
    box_bg = "#f7fafc" if not is_dark else "#2d3748"
    tip_bg = "#ebf8ff" if not is_dark else "#2a4365"
    table_hdr_bg = "#edf2f7" if not is_dark else "#2d3748"
    
    css = f"""
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-size: 13px;
        line-height: 1.6;
        color: {text_color};
        background-color: {bg_color};
        margin: 20px;
    }}
    h1 {{
        color: {heading_color};
        font-size: 24px;
        border-bottom: 2px solid {border_color};
        padding-bottom: 8px;
        margin-top: 20px;
        margin-bottom: 12px;
    }}
    h2 {{
        color: {heading_color};
        font-size: 18px;
        border-bottom: 1px solid {border_color};
        padding-bottom: 6px;
        margin-top: 30px;
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
    
    html_parts = [
        f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{css}</style></head><body>",
        f"<div style='text-align: center; margin-bottom: 30px; padding: 20px; background-color: {box_bg}; border-radius: 6px; border: 1px solid {border_color};'>",
        f"<h1 style='border: none; margin: 0; color: #2b6cb0; font-size: 26px;'>Quantyx - Official User Guide & Technical Manual</h1>",
        f"<p style='color: gray; margin-top: 5px; font-size: 14px;'>Industrial High-Performance Platform for Exploratory Data Analysis (EDA) & Machine Learning</p>",
        f"<p style='margin: 0; font-size: 12px;'><b>System Version:</b> {__version__} | <b>Author:</b> Quantyx Development Team</p>",
        "</div>"
    ]
    
    for t in topics:
        html_parts.append(f"<div id='{t['id']}' style='margin-bottom: 35px;'>")
        html_parts.append(t["content_html"])
        html_parts.append("</div>")
        html_parts.append(f"<hr style='border: 0; border-top: 1px dashed {border_color}; margin: 25px 0;'/>")
        
    html_parts.append("</body></html>")
    return "".join(html_parts)


def export_to_pdf(parent_widget=None):
    """
    Exports the complete documentation content directly to a formatted PDF document.
    """
    file_name, _ = QFileDialog.getSaveFileName(
        parent_widget,
        "Export User Guide to PDF",
        f"Quantyx_User_Guide_v{__version__}.pdf",
        "PDF Files (*.pdf)"
    )
    if not file_name:
        return
        
    if not file_name.lower().endswith('.pdf'):
        file_name += '.pdf'
        
    try:
        html_content = build_full_html_document(is_dark=False)
        doc = QTextDocument()
        doc.setHtml(html_content)
        
        printer = QPrinter(QPrinter.PrinterMode.PrinterResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(file_name)
        
        # Standard 15mm margins
        from PyQt6.QtCore import QMarginsF
        from PyQt6.QtGui import QPageLayout, QPageSize
        layout = QPageLayout(
            QPageSize(QPageSize.PageSizeId.A4),
            QPageLayout.Orientation.Portrait,
            QMarginsF(15, 15, 15, 15)
        )
        printer.setPageLayout(layout)
        
        doc.print(printer)
        
        if parent_widget:
            QMessageBox.information(
                parent_widget,
                "Export Completed",
                f"The User Guide has been successfully exported to PDF:\n\n{file_name}"
            )
    except Exception as e:
        if parent_widget:
            QMessageBox.critical(
                parent_widget,
                "PDF Export Error",
                f"An error occurred while generating the PDF document:\n{str(e)}"
            )


def export_to_docx(parent_widget=None):
    """
    Exports the complete documentation content to structured Microsoft Word (.docx).
    """
    file_name, _ = QFileDialog.getSaveFileName(
        parent_widget,
        "Export User Guide to Word",
        f"Quantyx_User_Guide_v{__version__}.docx",
        "Word Documents (*.docx)"
    )
    if not file_name:
        return
        
    if not file_name.lower().endswith('.docx'):
        file_name += '.docx'
        
    try:
        import docx
        from docx.shared import Inches, Pt, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.enum.table import WD_TABLE_ALIGNMENT
        from docx.oxml import OxmlElement, parse_xml
        from docx.oxml.ns import nsdecls, qn
        import re

        doc = docx.Document()
        
        # Configure A4 margins
        for section in doc.sections:
            section.top_margin = Inches(0.8)
            section.bottom_margin = Inches(0.8)
            section.left_margin = Inches(0.8)
            section.right_margin = Inches(0.8)

        # Title / Cover Page
        title_p = doc.add_paragraph()
        title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_run = title_p.add_run("Quantyx")
        title_run.font.size = Pt(28)
        title_run.font.bold = True
        title_run.font.color.rgb = RGBColor(41, 128, 185)
        
        sub_p = doc.add_paragraph()
        sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        sub_run = sub_p.add_run("Industrial Data Analysis & Machine Learning Studio")
        sub_run.font.size = Pt(15)
        sub_run.font.italic = True
        sub_run.font.color.rgb = RGBColor(80, 80, 80)
        
        meta_p = doc.add_paragraph()
        meta_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        meta_run = meta_p.add_run(f"Official User Manual • Version {__version__}")
        meta_run.font.size = Pt(11)
        meta_run.font.bold = True
        
        doc.add_paragraph().paragraph_format.space_after = Pt(20)

        # Executive summary
        doc.add_heading("Manual Overview", level=1)
        intro_desc = doc.add_paragraph(
            "This document is the official and comprehensive reference guide for the Quantyx platform. "
            "It details all available features, interface panels, controls, statistical models, machine learning techniques, "
            "hyperparameter configurations, step-by-step procedures, and error troubleshooting diagnostics available across the system."
        )
        intro_desc.paragraph_format.space_after = Pt(14)

        topics = get_all_topics()
        
        for topic in topics:
            # Section Title
            h = doc.add_heading(topic["title"], level=1)
            h.paragraph_format.space_before = Pt(16)
            h.paragraph_format.space_after = Pt(6)
            
            # Topic Summary
            p_sum = doc.add_paragraph()
            r_sum = p_sum.add_run(f"Objective: {topic['summary']}")
            r_sum.font.italic = True
            r_sum.font.color.rgb = RGBColor(100, 100, 100)
            p_sum.paragraph_format.space_after = Pt(8)

            # Textual processing of HTML structure
            raw_html = topic["content_html"]
            
            # Helper to strip HTML tags
            def strip_tags(text):
                text = re.sub(r'<[^>]+>', '', text)
                text = text.replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&').replace('&times;', 'x')
                return text.strip()

            paragraphs_raw = raw_html.split('</p>')
            for p_chunk in paragraphs_raw:
                if '<h3' in p_chunk:
                    sub_title = re.search(r'<h3>(.*?)</h3>', p_chunk, re.DOTALL)
                    if sub_title:
                        sh = doc.add_heading(strip_tags(sub_title.group(1)), level=2)
                        sh.paragraph_format.space_before = Pt(10)
                        sh.paragraph_format.space_after = Pt(4)
                
                # List items
                if '<li>' in p_chunk:
                    li_items = re.findall(r'<li>(.*?)</li>', p_chunk, re.DOTALL)
                    for li in li_items:
                        item_text = strip_tags(li)
                        if item_text:
                            p_bullet = doc.add_paragraph(item_text, style='List Bullet')
                            p_bullet.paragraph_format.space_after = Pt(3)
                            
                # Normal paragraph text
                p_text_search = re.search(r'<p>(.*)', p_chunk, re.DOTALL)
                if p_text_search:
                    clean_p = strip_tags(p_text_search.group(1))
                    if clean_p and not clean_p.startswith('Objective:') and not clean_p.startswith('Objetivo:'):
                        p_normal = doc.add_paragraph(clean_p)
                        p_normal.paragraph_format.space_after = Pt(6)

            # Tables to Word table
            if '<table' in raw_html:
                table_match = re.search(r'<table.*?>(.*?)</table>', raw_html, re.DOTALL)
                if table_match:
                    rows = re.findall(r'<tr>(.*?)</tr>', table_match.group(1), re.DOTALL)
                    if rows:
                        first_row_cells = re.findall(r'<t[hd]>(.*?)</t[hd]>', rows[0], re.DOTALL)
                        num_cols = len(first_row_cells)
                        if num_cols > 0:
                            w_table = doc.add_table(rows=len(rows), cols=num_cols)
                            w_table.alignment = WD_TABLE_ALIGNMENT.CENTER
                            w_table.style = 'Light Shading Accent 1'
                            
                            for r_idx, r_content in enumerate(rows):
                                cells = re.findall(r'<t[hd]>(.*?)</t[hd]>', r_content, re.DOTALL)
                                for c_idx, c_content in enumerate(cells[:num_cols]):
                                    cell_text = strip_tags(c_content)
                                    w_table.cell(r_idx, c_idx).text = cell_text
                            doc.add_paragraph().paragraph_format.space_after = Pt(8)

        doc.save(file_name)
        
        if parent_widget:
            QMessageBox.information(
                parent_widget,
                "Export Completed",
                f"The User Guide has been successfully exported to Word (.docx):\n\n{file_name}"
            )
    except Exception as e:
        if parent_widget:
            QMessageBox.critical(
                parent_widget,
                "DOCX Export Error",
                f"An error occurred while generating the Word document:\n{str(e)}"
            )
