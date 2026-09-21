from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton
from PyQt6.QtCore import Qt

HELP_HTML = """
<h1>Quantyx - Industrial Data Analysis User Guide</h1>
<p>Welcome to <b>Quantyx</b>, a professional desktop application designed for exploratory data analysis (EDA), preprocessing, and machine learning in industrial environments.</p>

<h2>1. Getting Started & Data Loading</h2>
<ul>
    <li><b>Local Files:</b> Go to <i>File -> Open Data...</i> to load CSV, XLSX, Parquet, or Feather files.</li>
    <li><b>Databricks SQL:</b> Go to <i>SQL Data -> Import from Databricks SQL...</i> to write custom queries and securely download data directly from your Data Lakehouse.</li>
    <li><b>The Interface:</b> The application uses dockable panels (Variables, Filters, Data View, Properties). You can drag, stack, or detach them.</li>
</ul>

<h2>2. Data Preprocessing</h2>
<p>Go to <i>Data Preprocessing -> Open Preprocessing Tool</i> to clean your data before plotting:</p>
<ul>
    <li><b>Missing Value Imputation:</b> Replace NaNs with the Mean, Median, Mode, or use advanced <b>KNN Imputation</b> for intelligent filling.</li>
    <li><b>Scaling:</b> Normalize your numeric columns using <i>MinMax</i> or <i>StandardScaler</i>.</li>
    <li><b>Outlier Management:</b> Manually select noisy points on the interactive scatter plot to remove them, or use the <b>Auto Detect Outliers</b> button (powered by <i>Isolation Forest</i>) to automatically highlight and remove anomalies.</li>
</ul>

<h2>3. Plotting & Visualization</h2>
<p><i>Note: To prevent freezing with large datasets, plots do not render automatically. Select your variables and click <b>Update Plot</b> to render the graph.</i></p>
<ul>
    <li><b>Scatter Plot:</b> Render huge datasets fast. Supports color-coding by categories.</li>
    <li><b>Line Plot:</b> Great for time-series. Automatically detects datetime columns and formats the X-axis ticks.</li>
    <li><b>Histogram & Bar Plot:</b> Explore distributions and counts. The Bar Plot specifically supports categorical grouping on the X-axis.</li>
    <li><b>Boxplot:</b> Analyze statistical spread. Check multiple boxes in the <i>All Variables</i> list to create nested/multi-level X-axis groups!</li>
    <li><b>Parallel Coordinates:</b> Select multiple numeric variables to map multidimensional relationships. Features full interactivity:
        <ul>
            <li><b>Click a line:</b> Highlights the specific data profile in red and displays its exact values across all dimensions.</li>
            <li><b>Drag to select:</b> Draw a yellow selection box over the axes to instantly filter and highlight all lines passing through that region.</li>
        </ul>
    </li>
    <li><b>Correlation Matrix:</b> Select multiple numeric variables to analyze their Pearson correlation coefficients.</li>
</ul>

<h2>4. Customizing Plots (Plot Properties)</h2>
<ul>
    <li><b>Titles, Labels & Limits:</b> Set custom titles, axis labels, and draw horizontal dashed Limit Lines.</li>
    <li><b>Boxplot Annotations:</b> Toggle exact statistical values (Means, Q1, Q3) directly over the boxes, or enable the <i>Show X-Axis Data Table</i> for Minitab-style statistical tables (cleanly aligned under the axis with multiple nested variables).</li>
    <li><b>Dynamic Theming:</b> Change the base palette, regression line colors, and override individual category colors using the dynamic color pickers at the bottom of the properties panel.</li>
</ul>

<h2>5. Filtering Data</h2>
<p>The <b>Filters</b> dock allows you to slice your dataset dynamically. Set numeric conditions (e.g., &gt;, &lt;) or check/uncheck categorical values. All plots and tables update automatically to reflect the subset.</p>

<h2>6. Machine Learning</h2>
<p>Navigate to the <i>Machine Learning</i> tab to build and deploy predictive models directly within Quantyx:</p>
<ul>
    <li><b>Supervised Learning:</b> Train classification or regression models using Random Forest or XGBoost. Select your <i>Target</i> and hit <b>Train Model</b>. View confusion matrices, residual plots, and R² scores.</li>
    <li><b>Unsupervised Learning:</b> Use K-Means Clustering or PCA to find hidden patterns.</li>
    <li><b>Auto-Tune:</b> Automatically optimize model hyperparameters using GridSearchCV.</li>
    <li><b>Feature Importance:</b> Extract the most critical variables driving your model's predictions.</li>
    <li><b>Save/Load Models:</b> Export your trained `.pkl` models to use in production or reload them later to predict new data.</li>
</ul>

<h2>7. Settings & Theming</h2>
<ul>
    <li><b>Dark / Light Mode:</b> Go to <i>Settings -> Toggle Dark/Light Mode</i> to switch the application theme. Your preference is automatically saved and remembered for the next launch.</li>
    <li><b>Template Center:</b> Manage your PowerPoint templates directly in <i>Settings -> Open Template Directory</i> to add or remove your own `.pptx` files.</li>
</ul>

<h2>8. Presentation Gallery & Exporting</h2>
<ul>
    <li><b>Generate PowerPoint:</b> Click the 📸 camera icon in the toolbar to snapshot plots. Inside the <i>Presentation Gallery</i> tab, you can select your preferred custom template from the dropdown and click "Generate PowerPoint" to compile a professional <code>.pptx</code> presentation automatically.</li>
    <li><b>Export Single Plots:</b> Go to <i>File -> Export Plot (PNG/PDF)</i> for high-res images.</li>
    <li><b>Export Filtered Data:</b> Save your cleaned, preprocessed, and filtered dataset to a new CSV.</li>
</ul>
"""

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Quantyx - User Guide")
        self.resize(750, 650)
        
        layout = QVBoxLayout(self)
        
        browser = QTextBrowser()
        browser.setHtml(HELP_HTML)
        browser.setOpenExternalLinks(True)
        layout.addWidget(browser)
        
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

