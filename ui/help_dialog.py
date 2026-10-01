from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton
from PyQt6.QtCore import Qt

HELP_HTML = """
<h1>Quantyx - Industrial Data Analysis User Guide</h1>
<p>Welcome to <b>Quantyx</b>, a professional desktop application designed for exploratory data analysis (EDA), preprocessing, and machine learning in industrial environments.</p>

<h2>1. Getting Started & Data Loading</h2>
<ul>
    <li><b>Local Files:</b> Go to <i>File -> Open Data...</i> to load CSV, XLSX, Parquet, or Feather files.</li>
    <li><b>Databricks SQL:</b> Go to <i>SQL Data -> Import from Databricks SQL...</i> to write custom queries and securely download data directly from your Data Lakehouse. Your connection credentials and executed queries are securely saved locally, allowing you to quickly reuse previous scripts from the dropdown menu.</li>
    <li><b>The Interface:</b> The application uses dockable panels (Variables, Filters, Data View, Properties). You can drag, stack, or detach them.</li>
</ul>

<h2>2. Data Preprocessing</h2>
<p>Go to <i>Data Preprocessing -> Open Preprocessing Tool</i> to clean your data before plotting. Operations are processed as fast background tasks with progress indicators, ensuring the interface remains fluid:</p>
<ul>
    <li><b>Missing Value Imputation:</b> Replace NaNs with the Mean, Median, Mode, or use advanced <b>KNN Imputation</b> for intelligent filling.</li>
    <li><b>Scaling:</b> Normalize your numeric columns using <i>MinMax</i> or <i>StandardScaler</i>.</li>
    <li><b>Outlier Management:</b> Verify variables using the central plot. Manually select noisy points on the interactive scatter plot to remove them, or use the <b>Auto Detect Outliers</b> button (powered by <i>Isolation Forest</i>) to automatically highlight and remove anomalies.</li>
</ul>

<h2>3. Plotting & Visualization</h2>
<p><i>Note: To prevent freezing with large datasets, plots do not render automatically. Select your variables and click <b>Update Plot</b> to render the graph.</i></p>
<ul>
    <li><b>Scatter Plot:</b> Render huge datasets fast. Supports color-coding by categories.</li>
    <li><b>Line Plot:</b> Great for time-series. Automatically detects datetime columns and formats the X-axis dynamically to prevent overlap.</li>
    <li><b>Color Rules:</b> You can color-code your plots based on mathematical conditions without modifying the dataset. Just type a rule in the <i>Color by</i> text box (e.g., <code>Temperature > 100</code>).</li>
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
    <li><b>Dynamic Theming:</b> Change the base palette, and override individual category colors using the dynamic color pickers at the bottom of the properties panel.</li>
</ul>

<h2>5. Filtering Data</h2>
<p>The <b>Filters</b> dock allows you to slice your dataset dynamically. Elements are tightly packed at the top for faster access. All plots and tables update automatically to reflect the subset.</p>
<ul>
    <li><b>Numeric Filters:</b> Set mathematical conditions (e.g., &gt;, &lt;).</li>
    <li><b>Categorical Filters:</b> Check or uncheck values. Uses cascading logic (filtering one column automatically prunes the available options for subsequent columns). Use the <i>Select All / Deselect All</i> buttons for speed.</li>
    <li><b>Date Filters:</b> When selecting a datetime column, the filter panel automatically adapts to a calendar-based Date Range picker for seamless slicing.</li>
</ul>

<h2>6. Machine Learning Hub</h2>
<p>Navigate to <i>Machine Learning -> Open ML Hub</i> to access the dedicated predictive environment. The interface intelligently isolates itself, revealing the <b>ML Settings</b> dock where you can manage Targets, Tasks, and Hyperparameters.</p>
<ul>
    <li><b>Supervised Learning:</b> Train classification or regression models using <b>KNN, Random Forest, or XGBoost</b>. Check input features in the <i>All Variables</i> list on the left, select your <i>Target</i>, and hit <b>Train Model</b>. View confusion matrices, scatter plots, and R² scores.</li>
    <li><b>Prediction & Inference:</b> Use the <b>Predict</b> button to run new data through a loaded or trained model (even if the dataset lacks the Target column). The predictions can then be saved using <b>Download Results</b>.</li>
    <li><b>Unsupervised Learning:</b> Use <b>K-Means Clustering</b> or <b>PCA</b> to find hidden patterns. PCA uniquely keeps the <i>Color By</i> option visible to help visualize your principal components!</li>
    <li><b>Auto-Tune:</b> Automatically optimize model hyperparameters using GridSearchCV.</li>
    <li><b>Feature Importance:</b> Extract the most critical variables driving your model's predictions.</li>
    <li><b>Save/Load Projects:</b> Entire sessions (Data, Filters, and ML Models) are saved into `.quantyx` files. Loading a project intelligently returns you straight to the ML Hub if a model was saved!</li>
</ul>

<h2>7. Settings & Theming</h2>
<ul>
    <li><b>Dark / Light Mode:</b> Go to <i>Settings -> Toggle Dark/Light Mode</i> to switch the application theme. Your preference is automatically saved and remembered for the next launch.</li>
    <li><b>Template Center:</b> Manage your PowerPoint templates directly in <i>Settings -> Open Template Directory</i> to add or remove your own `.pptx` files.</li>
</ul>

<h2>8. Gallery & Exporting</h2>
<ul>
    <li><b>Generate PowerPoint:</b> Click the 📸 camera icon in the toolbar. The system detects if you are viewing Standard Plots, Preprocessing, or the ML Hub, and captures the exact visualization you see! Inside the <b>Gallery</b> tab on the right sidebar, select your custom template and click "Generate PowerPoint" to compile a professional <code>.pptx</code> presentation automatically.</li>
    <li><b>Export Single Plots:</b> Go to <i>File -> Export Plot (PNG/PDF)</i> for high-res images.</li>
    <li><b>Export Filtered Data:</b> Save your cleaned, preprocessed, and filtered dataset to a new Excel file (<code>.xlsx</code>).</li>
</ul>
"""

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Quantyx - User Guide")
        self.resize(800, 700)
        
        layout = QVBoxLayout(self)
        
        browser = QTextBrowser()
        browser.setHtml(HELP_HTML)
        browser.setOpenExternalLinks(True)
        layout.addWidget(browser)
        
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)
