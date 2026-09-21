import pyqtgraph as pg
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

class ThemeManager:
    _is_dark = True

    @classmethod
    def set_theme(cls, dark: bool):
        cls._is_dark = dark
        
        # Save to settings
        from utils.config import load_settings, save_settings
        settings = load_settings()
        settings['is_dark_theme'] = dark
        save_settings(settings)
        
        app = QApplication.instance()
        if not app:
            return
            
        app.setStyle("Fusion")
        palette = QPalette()
        
        if dark:
            palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
            pg.setConfigOption('background', 'k')
            pg.setConfigOption('foreground', 'w')
        else:
            palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
            palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
            palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(240, 240, 240))
            palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.black)
            palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
            palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
            palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
            palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
            pg.setConfigOption('background', 'w')
            pg.setConfigOption('foreground', 'k')
            
        app.setPalette(palette)
        
    @classmethod
    def apply_to_plots(cls, main_window):
        # Update existing plots
        bg = 'k' if cls._is_dark else 'w'
        fg = 'w' if cls._is_dark else 'k'
        
        plot_widgets = [
            main_window.plot_scatter.plot_widget,
            main_window.plot_histogram.plot_widget,
            main_window.plot_boxplot.plot_widget,
            main_window.plot_barplot.plot_widget,
            main_window.plot_lineplot.plot_widget,
            main_window.plot_parallel.plot_widget,
            main_window.plot_corr.plot_widget,
            main_window.plot_ml.plot_widget,
            main_window.outlier_plot.plot_widget
        ]
        
        for pw in plot_widgets:
            pw.setBackground(bg)
            for axis_name in ['left', 'bottom', 'top', 'right']:
                axis = pw.getAxis(axis_name)
                if axis:
                    axis.setPen(fg)
                    axis.setTextPen(fg)
            # Update title color if needed
            if pw.plotItem.titleLabel.text:
                pw.setTitle(pw.plotItem.titleLabel.text, color=fg)

    @classmethod
    def is_dark(cls):
        return cls._is_dark
