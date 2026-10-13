"""
Quantyx Documentation System - Master Content Repository (English)
Contains the complete, structured, and exhaustive technical documentation of all modules,
features, algorithms, tutorials, and references in Quantyx.
"""

TOPICS = [
    {
        "id": "intro",
        "title": "1. Introduction & System Overview",
        "category": "Overview",
        "keywords": ["introduction", "quantyx", "overview", "architecture", "eda", "pyqt6", "pyqtgraph", "high performance"],
        "summary": "Overview of Quantyx, its architectural foundation, industrial objectives, and high-performance capabilities.",
        "content_html": r"""
<h2>1. Introduction & System Overview</h2>
<p><b>Quantyx</b> is an enterprise-grade, high-performance desktop platform designed specifically for <b>Exploratory Data Analysis (EDA)</b>, <b>Data Preprocessing</b>, <b>Outlier Remediation</b>, and <b>Machine Learning</b> in industrial, manufacturing, and scientific environments.</p>

<div class="note-box">
    <b>Core Mission:</b> To provide a unified, responsive, and fully interactive desktop environment where process engineers, data scientists, and analysts can ingest large-scale datasets (millions of records), dynamically slice and filter variables, inspect multivariate distributions, train predictive models, and automate executive PowerPoint reports in seconds—without writing a single line of code.
</div>

<h3>Key Architectural Highlights</h3>
<ul>
    <li><b>Hardware-Accelerated Plotting (PyQtGraph & PyQt6):</b> Unlike web-based or pure Matplotlib tools that freeze with large datasets, Quantyx leverages C++ Qt graphics via PyQtGraph, effortlessly rendering scatter and line plots with millions of data points with fluid zooming and panning.</li>
    <li><b>On-Demand Plotting (Freeze Prevention):</b> Plot updates occur explicitly when clicking the blue <code>Update Plot</code> button, preventing UI lockups when toggling between large columns.</li>
    <li><b>Cloud Lakehouse Integration (Databricks SQL):</b> Native connector for Databricks Lakehouses with encrypted Windows Registry credentials and non-blocking background query execution.</li>
    <li><b>Dedicated Machine Learning Hub:</b> An isolated predictive environment supporting both unsupervised learning (PCA, K-Means) and supervised learning (KNN, Random Forest, XGBoost), with native <b>Single-Output</b> and <b>Multi-Output</b> support (simultaneous prediction of multiple sensor targets), <b>✨ Auto-Tune</b> via RandomizedSearchCV, and <b>Feature Importance</b> visualization.</li>
    <li><b>PowerPoint Automation (Gallery):</b> Integrated snapshot gallery that captures high-resolution plots with a single click and automatically compiles them into branded company PowerPoint presentations (<code>.pptx</code>) using custom templates.</li>
    <li><b>Full Project Persistence (.quantyx):</b> Save and restore raw data, active filters, gallery images, and trained ML models into a single portable project file.</li>
</ul>
"""
    },
    {
        "id": "requirements",
        "title": "2. Installation & System Requirements",
        "category": "Setup",
        "keywords": ["requirements", "installation", "hardware", "python", "operating system", "dependencies", "setup", "inno setup"],
        "summary": "Hardware prerequisites, software dependencies, and installation instructions for Quantyx.",
        "content_html": r"""
<h2>2. Installation & System Requirements</h2>

<h3>Hardware Requirements</h3>
<table class="doc-table">
    <tr><th>Component</th><th>Minimum Requirement</th><th>Recommended Specification</th></tr>
    <tr><td>Operating System</td><td>Windows 10 (64-bit)</td><td>Windows 11 (64-bit)</td></tr>
    <tr><td>Processor (CPU)</td><td>Intel Core i3 / AMD Ryzen 3 (Quad-Core)</td><td>Intel Core i7 / AMD Ryzen 7 (8+ cores)</td></tr>
    <tr><td>RAM</td><td>8 GB RAM</td><td>16 GB to 32 GB RAM (for large industrial datasets)</td></tr>
    <tr><td>Free Disk Space</td><td>1 GB free space</td><td>5 GB free space (SSD recommended)</td></tr>
    <tr><td>Display Resolution</td><td>1366 x 768 pixels</td><td>1920 x 1080 (Full HD) or higher</td></tr>
</table>

<h3>Software Dependencies</h3>
<p>Quantyx runs on Python 3.12+ and uses the following core enterprise libraries:</p>
<ul>
    <li><code>PyQt6</code> (>=6.7.0): Native desktop user interface and dock management.</li>
    <li><code>pyqtgraph</code> (>=0.13.7): Real-time, GPU-accelerated 2D graphics engine.</li>
    <li><code>pandas</code> (>=2.2.0) & <code>numpy</code> (>=1.26.0): High-speed vector manipulation and tabular data structures.</li>
    <li><code>scikit-learn</code> (>=1.4.0): Algorithms for PCA, K-Means, KNN, Random Forest, Imputers, Scalers, and metrics.</li>
    <li><code>xgboost</code> (>=2.0.0): State-of-the-art gradient boosted decision tree framework.</li>
    <li><code>pyarrow</code> & <code>fastparquet</code>: High-speed columnar Parquet and Feather I/O.</li>
    <li><code>openpyxl</code> & <code>xlsxwriter</code>: Microsoft Excel (.xlsx) spreadsheet processing.</li>
    <li><code>python-pptx</code>: Automated Microsoft PowerPoint slide compilation.</li>
    <li><code>python-docx</code>: Microsoft Word (.docx) documentation generation and export.</li>
    <li><code>databricks-sql-connector</code>: Secure protocol for Databricks Lakehouse queries.</li>
</ul>

<h3>Distribution & Deployment Formats</h3>
<ol>
    <li><b>Windows Installer (Inno Setup):</b> <code>Quantyx_Installer_vX.X.X.exe</code> installs the software in the user's directory and creates desktop and Start Menu shortcuts.</li>
    <li><b>Standalone Directory (PyInstaller):</b> Portable build folder located in <code>dist/Quantyx</code> generated via <code>build.bat</code>.</li>
    <li><b>Source Code Execution:</b> Activate virtual environment via <code>.venv\\Scripts\\activate</code> and launch using <code>python main.py</code>.</li>
</ol>
"""
    },
    {
        "id": "interface",
        "title": "3. Interface Architecture & Workspace Navigation",
        "category": "Interface",
        "keywords": ["interface", "navigation", "docks", "workspace", "layout", "status bar", "central stack", "toolbar"],
        "summary": "Detailed overview of dockable widgets, the central stack, main menus, and toolbar navigation.",
        "content_html": r"""
<h2>3. Interface Architecture & Workspace Navigation</h2>
<p>Quantyx features an ergonomic, modular layout built on Qt's dockable widget system. Panels can be resized, stacked, detached into floating windows, or tabified based on user preference.</p>

<h3>Primary Workspace Regions</h3>
<ul>
    <li><b>Menu Bar (Top):</b> Access to <code>File</code>, <code>SQL Data</code>, <code>Data Preprocessing</code>, <code>Machine Learning</code>, <code>Settings</code>, and <code>Help</code>.</li>
    <li><b>Main Toolbar:</b> Quick-access button <code>📸 Add Current Plot to Presentation</code> for one-click snapshot capture into the presentation gallery.</li>
    <li><b>Variables Dock (Left):</b>
        <ul>
            <li><code>All Variables</code> list with checkboxes for multi-variable selection (used in nested Boxplots, Parallel Coordinates, Correlation Matrix, and ML features).</li>
            <li><code>X Axis</code> and <code>Y Axis</code> selectors for Cartesian plotting.</li>
            <li><code>Color by</code> dropdown for categorical grouping and legends.</li>
            <li><code>Color Rule</code> text field for on-the-fly mathematical conditional coloring.</li>
            <li>Blue <code>Update Plot</code> button.</li>
        </ul>
    </li>
    <li><b>Central Stack:</b> Dynamically switches between 3 operational modes:
        <ol>
            <li><b>Data Exploration Mode:</b> Standard tabs for Scatter, Histogram, Boxplot, Bar Plot, Line Plot, Parallel Coordinates, and Correlation Matrix.</li>
            <li><b>Data Preprocessing Mode:</b> Outlier scatter plot with interactive click selection and cleaning controls.</li>
            <li><b>Machine Learning Studio Mode:</b> Predictive modeling tabs for PCA, K-Means, KNN, Random Forest, and XGBoost.</li>
        </ol>
    </li>
    <li><b>Data View Dock (Bottom):</b> High-speed virtualized tabular data browser with 4-decimal float formatting and real-time filter synchronization.</li>
    <li><b>Right Dock Stack (Tabified):</b>
        <ul>
            <li><b>Filters:</b> Real-time numerical, categorical, and temporal cascading filters.</li>
            <li><b>Plot Properties:</b> Custom titles, axis labels, horizontal limits, annotations, and color palettes.</li>
            <li><b>Gallery:</b> Presentation gallery showing captured snapshots ready for PowerPoint compilation.</li>
            <li><b>ML Settings:</b> Dedicated ML task, target, and hyperparameter controls (visible in ML mode).</li>
            <li><b>Preprocessing Settings:</b> Missing value imputation, scaling, and outlier removal (visible in Preprocessing mode).</li>
        </ul>
    </li>
    <li><b>Status Bar (Bottom):</b> Real-time operational feedback, row counts, filter stats, and background progress indicators.</li>
</ul>
"""
    },
    {
        "id": "ingestion",
        "title": "4. Data Ingestion & Supported File Formats",
        "category": "Data",
        "keywords": ["import", "csv", "excel", "xlsx", "parquet", "feather", "ingestion", "open file", "data cleaning"],
        "summary": "Importing local datasets, supported formats, and automated data sanitation during ingestion.",
        "content_html": r"""
<h2>4. Data Ingestion & Supported File Formats</h2>

<h3>Supported Local File Formats</h3>
<p>Quantyx supports direct ingestion of the four most common industrial and scientific data formats:</p>
<ul>
    <li><b>CSV (Comma-Separated Values - <code>.csv</code>):</b> Ingested using optimized low-memory parsers to prevent mixed-type warnings on massive files.</li>
    <li><b>Microsoft Excel (<code>.xlsx</code> and <code>.xls</code>):</b> Native spreadsheet ingestion powered by OpenPyXL.</li>
    <li><b>Apache Parquet (<code>.parquet</code>):</b> High-performance columnar storage with snappy compression, ideal for large multi-gigabyte datasets.</li>
    <li><b>Apache Arrow Feather (<code>.feather</code>):</b> Ultra-fast binary memory mapping for near-instantaneous file loading.</li>
</ul>

<h3>How to Load a Dataset</h3>
<ol>
    <li>Navigate to the top menu: <b>File -> Open Data...</b> (or press <code>Ctrl+O</code>).</li>
    <li>Select your file in the standard Windows file browser and click Open.</li>
    <li>The status bar will display loading progress. Once complete, the data table is populated and all column selectors are refreshed.</li>
</ol>

<h3>Automated Data Sanitation During Ingestion</h3>
<p>When loading any dataset, <code>DataManager</code> automatically runs several intelligent cleaning routines:</p>
<div class="tip-box">
    <b>Automatic Cleaning Features:</b>
    <ul>
        <li><b>Column Deduplication:</b> Identical column names are automatically deduplicated to prevent Pandas index collisions.</li>
        <li><b>Decimal Comma Normalization:</b> Number strings using European/Brazilian comma decimals (e.g. "12,50") are converted to dots ("12.50") and cast to numeric floats if all valid entries are numbers.</li>
        <li><b>Whitespace to NaN:</b> Empty strings and whitespace-only cells are automatically mapped to <code>NaN</code>.</li>
        <li><b>Datetime Auto-Detection:</b> Columns with "date" or "data" in their header are automatically converted to native <code>datetime64</code>.</li>
        <li><b>Temporal Sorting & Index Column:</b> If a datetime column is detected, the table is sorted chronologically and a dedicated sequential <code>index</code> column is generated for tracking.</li>
    </ul>
</div>
"""
    },
    {
        "id": "databricks",
        "title": "5. Databricks SQL & Cloud Lakehouse Integration",
        "category": "Data",
        "keywords": ["databricks", "sql", "lakehouse", "cloud", "query", "token", "hostname", "credentials", "saved queries"],
        "summary": "Connecting directly to Databricks SQL, encrypted credential storage, and reusable query management.",
        "content_html": r"""
<h2>5. Databricks SQL & Cloud Lakehouse Integration</h2>
<p>Quantyx includes native connectivity to <b>Databricks SQL Lakehouses</b>, allowing direct execution of SQL queries against cloud Delta tables without exporting intermediary CSVs.</p>

<h3>Step-by-Step Connection</h3>
<ol>
    <li>Navigate to <b>SQL Data -> Import from Databricks SQL...</b>.</li>
    <li>Enter your connection parameters:
        <ul>
            <li><b>Server Hostname:</b> Your Databricks workspace host (e.g., <code>adb-1234567890.1.azuredatabricks.net</code>).</li>
            <li><b>HTTP Path:</b> SQL Warehouse endpoint (e.g., <code>/sql/1.0/warehouses/ab1234cd5678ef90</code>).</li>
            <li><b>Access Token:</b> Personal Access Token (PAT). Masked with password asterisks for visual security.</li>
        </ul>
    </li>
    <li><b>Encrypted Credential Storage:</b> Check <code>Save Credentials</code>. Credentials are saved encrypted in the Windows Registry (<code>Quantyx\\SQLCredentials</code>), never in plain text.</li>
    <li>In the <b>SQL Query</b> box, write your query (e.g. <code>SELECT * FROM gold.sensors WHERE timestamp >= '2026-01-01' LIMIT 200000;</code>).</li>
    <li>Click <b>Run Query</b>. The query executes in a non-blocking background thread (<code>SQLWorker</code>) and injects the resulting dataset directly into Quantyx.</li>
</ol>

<h3>Saved Queries Manager</h3>
<ul>
    <li><b>Save Query:</b> Click <code>Save Query As...</code>, enter an alias, and store the query for future sessions.</li>
    <li><b>Load Query:</b> Select a saved script from the <code>Saved Queries</code> dropdown to populate the SQL editor.</li>
    <li><b>Delete Query:</b> Select a query and click <code>Delete</code> to remove it from saved storage.</li>
</ul>
"""
    },
    {
        "id": "exploration",
        "title": "6. Data Exploration & Data Table View",
        "category": "Exploration",
        "keywords": ["table", "data view", "virtualization", "inspection", "rows", "columns", "formatting", "exploration"],
        "summary": "Inspecting raw data with the virtualized Data View table, 4-decimal formatting, and alignment.",
        "content_html": r"""
<h2>6. Data Exploration & Data Table View</h2>
<p>The <b>Data View</b> dock at the bottom of the window provides real-time tabular inspection of the active dataset.</p>

<h3>High-Performance Virtualization (PandasTableModel)</h3>
<p>Rather than populating tens of thousands of graphical widget cells, Quantyx uses a customized <code>QAbstractTableModel</code>:</p>
<ul>
    <li><b>On-Demand Cell Rendering:</b> Only cells currently visible on screen are rendered, allowing frictionless navigation through 500,000+ rows.</li>
    <li><b>4-Decimal Formatting:</b> Floating-point numbers are automatically formatted to 4 decimals (e.g. <code>12.3456</code>) for clean numerical comparison.</li>
    <li><b>NaN Clean Display:</b> Missing values are displayed cleanly as blank cells.</li>
    <li><b>Alignment Ergonomics:</b> Numeric values are right-aligned; text labels and categories are left-aligned.</li>
    <li><b>Alternating Row Colors:</b> High-contrast alternating rows ensure comfortable reading during long sessions.</li>
    <li><b>Full Row Selection:</b> Click any row header to highlight the entire record.</li>
    <li><b>Instant Synchronization:</b> Filters and outlier removals instantly update the row count and contents of Data View.</li>
</ul>
"""
    },
    {
        "id": "filters",
        "title": "7. Interactive Cascading Filters",
        "category": "Filtering",
        "keywords": ["filters", "cascading", "numeric filter", "categorical filter", "date filter", "active filters", "slicing"],
        "summary": "Slicing data with numerical, categorical, and date filters, cascading logic, and managing active filters.",
        "content_html": r"""
<h2>7. Interactive Cascading Filters</h2>
<p>The <b>Filters</b> dock (right sidebar) enables dynamic multi-condition slicing across numerical, categorical, and temporal dimensions with real-time plot updates.</p>

<h3>Filter Types</h3>
<ol>
    <li><b>Numeric Filter:</b>
        <ul>
            <li>Automatically selected when choosing a numerical column.</li>
            <li>Condition operators: <code>&gt;</code>, <code>&lt;</code>, <code>==</code>, <code>&gt;=</code>, <code>&lt;=</code>, and <code>!=</code>.</li>
            <li>Enter the numeric threshold and click <b>Apply Numeric Filter</b>.</li>
        </ul>
    </li>
    <li><b>Categorical Filter:</b>
        <ul>
            <li>Automatically displayed when selecting a text or categorical column.</li>
            <li>Interactive checkbox list with <code>Select All</code> and <code>Deselect All</code> buttons.</li>
            <li>Safety limit: supports up to 500 unique categories to maintain UI responsiveness.</li>
            <li>Check desired values and click <b>Apply Categorical Filter</b>.</li>
        </ul>
    </li>
    <li><b>Date Range Filter:</b>
        <ul>
            <li>Automatically activated when selecting a <code>datetime64</code> column.</li>
            <li>Calendar popups for <code>Start Date</code> and <code>End Date</code> pre-populated with dataset boundaries.</li>
            <li>Click <b>Apply Date Filter</b> to slice the time window.</li>
        </ul>
    </li>
</ol>

<h3>Cascading Logic</h3>
<p>Filters operate in a cascading hierarchy: applying a filter to one column (e.g., filtering Machine to "M-01") immediately recalculates the available categorical options in all other columns so only remaining values are shown.</p>

<h3>Managing Active Filters</h3>
<ul>
    <li>The <b>Active Filters</b> list displays all applied rules (e.g., <code>Temperature &gt; 120.0</code>).</li>
    <li><b>Remove Specific Filter:</b> Highlight a rule and click <code>Remove Selected</code>.</li>
    <li><b>Clear All:</b> Click <code>Clear All</code> to reset the dataset to its original unfiltered state.</li>
</ul>
"""
    },
    {
        "id": "plots",
        "title": "8. Data Visualization & Statistical Plot Tools",
        "category": "Visualization",
        "keywords": ["plots", "scatter", "histogram", "boxplot", "bar plot", "line plot", "parallel coordinates", "correlation", "regression"],
        "summary": "Comprehensive guide to all 7 exploratory plot types, statistical computations, and interactive features.",
        "content_html": r"""
<h2>8. Data Visualization & Statistical Plot Tools</h2>
<p>Quantyx provides 7 hardware-accelerated plot types in the central exploration tab widget. Remember to click <b>Update Plot</b> to render or refresh graphs with selected variables.</p>

<h3>1. Scatter Plot</h3>
<ul>
    <li><b>Purpose:</b> Analyze relationships, distributions, and correlations between two continuous variables.</li>
    <li><b>Configuration:</b> Select variables in <code>X Axis</code> and <code>Y Axis</code>.</li>
    <li><b>Color by:</b> Choose a categorical column to group points with automatic legend generation.</li>
    <li><b>Linear Regression:</b> Toggle <code>Linear Regression (Scatter)</code> in Plot Properties to calculate ordinary least squares ($y = ax + b$). Displays the fitted line, analytical formula, and $R^2$ in the title.</li>
    <li><b>Horizontal Limits:</b> Add dashed upper and lower specification limit lines with custom colors.</li>
</ul>

<h3>2. Histogram & Descriptive Statistics</h3>
<ul>
    <li><b>Purpose:</b> Assess frequency distributions, normality, skewness, and modality.</li>
    <li><b>Numeric Data:</b> Automatic bin calculation via NumPy with optional semitransparent category overlays via <code>Color by</code>.</li>
    <li><b>Categorical Data:</b> Generates categorical frequency bar charts.</li>
    <li><b>Integrated Statistics Panel:</b> Right-hand text panel automatically computes:
        <ul>
            <li><b>Numeric:</b> Count, Nulls, Mean, Median, Std Dev, Min, Q1, Q3, Max, Skewness, and Kurtosis.</li>
            <li><b>Categorical:</b> Count, Nulls, Unique Count, Mode (Top Value), Frequency, and Top 10 breakdown table.</li>
        </ul>
    </li>
</ul>

<h3>3. Boxplot (Minitab Style Nested Grouping)</h3>
<ul>
    <li><b>Purpose:</b> Inspect median, interquartile range (IQR), and Tukey outliers ($1.5 \times IQR$).</li>
    <li><b>Statistical Annotations:</b> Toggle <code>Show Means</code>, <code>Show Q1</code>, and <code>Show Q3</code> on the boxes with custom colors.</li>
    <li><b>X-Axis Data Table (Minitab Style):</b> Enable <code>Show X-Axis Data Table</code> in Plot Properties and check multiple variables in <code>All Variables</code>. Quantyx builds a nested hierarchical table under the X-axis aligned with each group.</li>
</ul>

<h3>4. Bar Plot</h3>
<ul>
    <li><b>Purpose:</b> Compare aggregated statistics across discrete categories.</li>
    <li><b>Operation:</b> Select a categorical column in <code>X Axis</code>. If <code>Y Axis</code> is empty, counts occurrences. If a numeric column is selected in <code>Y Axis</code>, computes group means.</li>
    <li><b>Sub-grouping:</b> Select a variable in <code>Color by</code> to display grouped side-by-side bars with legends.</li>
</ul>

<h3>5. Line Plot (Time Series & Trends)</h3>
<ul>
    <li><b>Purpose:</b> Monitor continuous trends and time series processes.</li>
    <li><b>Datetime Support:</b> Automatically detects date columns, sorts chronologically, and displays formatted <code>YYYY-MM-DD</code> tick strings.</li>
    <li><b>Multi-Series:</b> Group lines by category using <code>Color by</code>.</li>
</ul>

<h3>6. Parallel Coordinates</h3>
<ul>
    <li><b>Purpose:</b> Visualize high-dimensional relationships across dozens of continuous variables simultaneously.</li>
    <li><b>Operation:</b> Check multiple numeric columns in <code>All Variables</code> and click <code>Update Plot</code>.</li>
    <li><b>Normalized Axes:</b> Each variable is normalized [0, 1] on vertical parallel axes showing original min, mid, and max ticks.</li>
    <li><b>Advanced Interactivity:</b>
        <ul>
            <li><b>Click Line:</b> Highlights the selected line in red and displays its exact numeric values across all axes at the top.</li>
            <li><b>Drag to Select (Box Select):</b> Click and drag a yellow selection box over axes. All lines passing through the rectangle are highlighted in red with total count displayed.</li>
        </ul>
    </li>
</ul>

<h3>7. Correlation Matrix</h3>
<ul>
    <li><b>Purpose:</b> Compute pairwise Pearson linear correlation coefficients.</li>
    <li><b>Operation:</b> Check 2 or more numeric variables in <code>All Variables</code> and click <code>Update Plot</code>.</li>
    <li><b>Heatmap:</b> Color-coded matrix with selectable palettes (viridis, plasma, inferno, magma, coolwarm). Each cell displays its numeric value (-1.0 to +1.0) with dynamic black/white text contrast.</li>
</ul>
"""
    },
    {
        "id": "properties",
        "title": "9. Plot Customization, Limit Lines & Aesthetics",
        "category": "Visualization",
        "keywords": ["properties", "plot properties", "title", "labels", "limits", "colors", "palette", "point size", "decimals"],
        "summary": "Configuring titles, axis labels, upper/lower specification lines, point sizes, and palettes.",
        "content_html": r"""
<h2>9. Plot Customization, Limit Lines & Aesthetics</h2>
<p>The <b>Plot Properties</b> dock (right sidebar) provides fine-grained visual and metrological formatting controls.</p>

<h3>Labels & Titles</h3>
<ul>
    <li><b>Title:</b> Custom chart title (leave empty for automatic generation).</li>
    <li><b>X Axis / Y Axis:</b> Override default horizontal and vertical axis labels.</li>
</ul>

<h3>Limits & Numbers</h3>
<ul>
    <li><b>Horizontal Upper Limit:</b> Enter a numeric value (e.g. <code>980</code>) and select a color to draw a dashed upper specification line.</li>
    <li><b>Horizontal Lower Limit:</b> Enter a numeric value (e.g. <code>720</code>) and select a color to draw a dashed lower specification line.</li>
    <li><b>Decimals X / Decimals Y:</b> Specify decimal precision (0 to 10) on axis ticks.</li>
    <li><b>Boxplot Annotations:</b> Toggle checkboxes and color pickers for Means, Q1, and Q3.</li>
    <li><b>Show X-Axis Data Table:</b> Enable the nested Minitab-style data table for multi-variable Boxplots.</li>
</ul>

<h3>Aesthetics & Palettes</h3>
<ul>
    <li><b>Point Size:</b> Adjust scatter point diameter from 1 to 50 pixels.</li>
    <li><b>Linear Regression (Scatter):</b> Toggle least squares regression line on scatter plots.</li>
    <li><b>Palette:</b> Colormap for heatmaps and correlation matrices (viridis, plasma, inferno, magma, coolwarm).</li>
    <li><b>Base Plot Color:</b> Default color picker for single-series charts.</li>
    <li><b>Categorical Plot Colors:</b> When <code>Color by</code> is active, dynamic color pickers are generated for each unique category.</li>
</ul>
"""
    },
    {
        "id": "preprocessing",
        "title": "10. Data Preprocessing & Cleaning Tools",
        "category": "Preprocessing",
        "keywords": ["preprocessing", "imputation", "nulls", "nan", "mean", "median", "knn", "scaling", "minmax", "standard scaler"],
        "summary": "Imputing missing values (Mean, Median, Mode, KNN) and feature scaling (MinMax, StandardScaler).",
        "content_html": r"""
<h2>10. Data Preprocessing & Cleaning Tools</h2>
<p>Access the <b>Data Preprocessing</b> suite via <code>Data Preprocessing -> Open Preprocessing Tool</code> to prepare and clean raw data before modeling.</p>

<h3>1. Missing Value Imputation</h3>
<p>Handle missing data (NaN) without dropping entire rows:</p>
<table class="doc-table">
    <tr><th>Method</th><th>Mechanism</th><th>Recommended Use</th></tr>
    <tr><td><b>Mean</b></td><td>Replaces NaNs with column arithmetic mean.</td><td>Normally distributed data without extreme outliers.</td></tr>
    <tr><td><b>Median</b></td><td>Replaces NaNs with column 50th percentile.</td><td><b>(Recommended)</b> Skewed variables or data with outliers.</td></tr>
    <tr><td><b>Mode</b></td><td>Replaces NaNs with the most frequent value.</td><td>Discrete counts or categorical-like numeric codes.</td></tr>
    <tr><td><b>KNN</b></td><td>Uses <code>KNNImputer(n_neighbors=5)</code> to estimate values from 5 nearest records.</td><td>Correlated features requiring high fidelity.</td></tr>
</table>
<p><b>How to Apply:</b> Select columns in <code>Select Numeric Columns</code>, choose the method, and click <b>Apply Imputation</b>.</p>

<h3>2. Feature Scaling & Normalization</h3>
<p>Normalize features to equalize scale impact in distance-based algorithms:</p>
<ul>
    <li><b>MinMax Scaler:</b> Rescales values to the range $[0, 1]$ via $X_{norm} = \frac{X - X_{min}}{X_{max} - X_{min}}$. Best for KNN, K-Means, and Neural Networks.</li>
    <li><b>Standard Scaler:</b> Standardizes features to zero mean and unit variance ($\mu = 0, \sigma = 1$) via $X_{std} = \frac{X - \mu}{\sigma}$. Best for linear regressions, PCA, and gradient boosting.</li>
</ul>
<p><b>How to Apply:</b> Select columns, choose the scaler, and click <b>Apply Scaling</b>.</p>

<p>Click <b>🔙 Return to Plots</b> to return to exploration with your clean dataset.</p>
"""
    },
    {
        "id": "outliers",
        "title": "11. Outlier Management (Isolation Forest & Manual Clicks)",
        "category": "Preprocessing",
        "keywords": ["outliers", "isolation forest", "anomalies", "outlier removal", "auto detect", "manual selection"],
        "summary": "Automated anomaly detection via Isolation Forest and manual point selection for outlier removal.",
        "content_html": r"""
<h2>11. Outlier Management (Isolation Forest & Manual Clicks)</h2>
<p>In Preprocessing mode, the central view becomes a dedicated outlier scatter plot (<code>OutlierPlotWidget</code>).</p>

<h3>1. Visual Bivariate Inspection</h3>
<p>Select any two numeric columns in <code>X Axis</code> and <code>Y Axis</code> on the left panel to inspect data points on the Cartesian plane.</p>

<h3>2. Automated Anomaly Detection (Isolation Forest)</h3>
<ul>
    <li>Click <b>Auto Detect Outliers (Isolation Forest)</b>.</li>
    <li>Quantyx runs <code>sklearn.ensemble.IsolationForest(contamination=0.05, random_state=42)</code> in a background thread.</li>
    <li>Isolation Forest builds random decision trees; anomalies require fewer splits to isolate than normal points.</li>
    <li>Detected outliers are highlighted in <b>red</b> on the scatter plot.</li>
    <li>A notification displays the total detected outliers (e.g., <i>"Detected 152 potential outliers."</i>).</li>
</ul>

<h3>3. Interactive Manual Point Selection</h3>
<ul>
    <li>Click directly on any noisy point in the scatter plot to tag it for removal.</li>
    <li>Manually selected points turn <b>orange</b>.</li>
    <li>Clicking a selected point a second time deselects it.</li>
</ul>

<h3>4. Dropping Outlier Rows</h3>
<ul>
    <li>The status label displays total points flagged (e.g., <i>"180 points selected for removal."</i>).</li>
    <li>Click <b>Remove Selected Points</b> (red button) to drop flagged rows permanently from the dataset.</li>
    <li>Click <b>Clear Selection</b> to clear flags without removing data.</li>
</ul>
"""
    },
    {
        "id": "ml_hub",
        "title": "12. Machine Learning Hub Overview",
        "category": "Machine Learning",
        "keywords": ["machine learning", "ml hub", "supervised", "unsupervised", "studio", "workflow"],
        "summary": "Overview of the dedicated ML Studio, workspace isolation, and the 8-step predictive workflow.",
        "content_html": r"""
<h2>12. Machine Learning Hub Overview</h2>
<p>Access the <b>Machine Learning Hub</b> via <code>Machine Learning -> Open ML Hub</code>. When entering the hub, Quantyx adapts its workspace:</p>
<ul>
    <li>Hides standard exploration docks to focus attention on predictive tasks.</li>
    <li>Reveals the <b>ML Settings</b> dock on the right sidebar.</li>
    <li>Displays algorithm tabs: <b>PCA</b>, <b>K-Means</b>, <b>K-Nearest Neighbors</b>, <b>Random Forest</b>, and <b>XGBoost</b>.</li>
    <li>Provides a <code>⬅ Return to Data Exploration</code> button to return to standard plotting at any time.</li>
</ul>

<h3>The 8-Step ML Workflow</h3>
<ol>
    <li><b>Feature Selection ($X$):</b> Check input predictor variables in <code>All Variables</code> on the left.</li>
    <li><b>Target Selection ($Y$):</b> Highlight target variable(s) in <code>Target(s) (Y)</code> (hold Ctrl for multi-output).</li>
    <li><b>Task Definition:</b> Select <code>Classification</code> (discrete labels) or <code>Regression</code> (continuous values).</li>
    <li><b>Algorithm Choice:</b> Switch to the desired model tab (KNN, Random Forest, or XGBoost).</li>
    <li><b>Hyperparameter Setup:</b> Configure values manually or click <code>✨ Auto-Tune</code>.</li>
    <li><b>Model Training:</b> Click <code>Train Model</code> and monitor background progress.</li>
    <li><b>Evaluation:</b> Inspect the residual plot, $R^2$, RMSE, MAE, Confusion Matrix, and Feature Importance.</li>
    <li><b>Deployment & Export:</b> Download the 3-sheet Excel report via <code>Download Results</code> or save model weights with <code>Save Model</code>.</li>
</ol>
"""
    },
    {
        "id": "ml_models",
        "title": "13. Machine Learning Models Reference",
        "category": "Machine Learning",
        "keywords": ["ml models", "pca", "kmeans", "knn", "random forest", "xgboost", "hyperparameters", "advantages", "limitations"],
        "summary": "Individual technical reference for all 5 models: PCA, K-Means, KNN, Random Forest, and XGBoost.",
        "content_html": r"""
<h2>13. Machine Learning Models Reference</h2>
<p>Quantyx includes five machine learning algorithms covering dimensionality reduction, clustering, and ensemble learning.</p>

<div class="model-card">
    <h3>1. PCA (Principal Component Analysis)</h3>
    <p><b>Type:</b> Unsupervised Learning / Dimensionality Reduction.</p>
    <p><b>Description:</b> Orthogonal linear transformation projecting correlated variables onto principal components (PC1, PC2) that capture maximum dataset variance.</p>
    <p><b>Recommended Use:</b> Visualizing high-dimensional clusters in 2D, eliminating sensor collinearity, and feature compression.</p>
    <p><b>Parameters in Quantyx:</b> Requires $\ge 2$ numeric features in <code>All Variables</code>. Supports <code>Color by</code> for class clustering.</p>
    <p><b>Advantages:</b> Fast, deterministic, removes multicollinearity, and visualizes variance distribution.</p>
    <p><b>Limitations:</b> Linear only. Principal components are linear combinations that may lack direct physical interpretation.</p>
    <p><b>Industrial Case:</b> Monitoring 30 chemical reactor sensors simultaneously to identify process drift.</p>
</div>

<div class="model-card">
    <h3>2. K-Means Clustering</h3>
    <p><b>Type:</b> Unsupervised Learning / Clustering.</p>
    <p><b>Description:</b> Iterative partitioning algorithm grouping data into $K$ clusters by minimizing Euclidean distances to cluster centroids.</p>
    <p><b>Recommended Use:</b> Product grade classification, operational regime identification, customer segmentation.</p>
    <p><b>Parameters in Quantyx:</b> <code>K</code> (number of clusters): 2 to 50 via spinbox.</p>
    <p><b>Advantages:</b> Highly scalable for massive datasets; plots exact centroid locations with red 'X' markers.</p>
    <p><b>Limitations:</b> Requires specifying $K$ in advance; assumes spherical clusters of similar variance; sensitive to unscaled data.</p>
    <p><b>Industrial Case:</b> Automatically segmenting manufacturing production batches into distinct quality tiers.</p>
</div>

<div class="model-card">
    <h3>3. K-Nearest Neighbors (KNN)</h3>
    <p><b>Type:</b> Supervised Learning (Classification & Regression).</p>
    <p><b>Description:</b> Non-parametric instance-based algorithm predicting output based on the majority vote or average of the $K$ nearest training records.</p>
    <p><b>Recommended Use:</b> Complex non-linear boundaries, local look-up estimation, low-dimensional datasets.</p>
    <p><b>Parameters in Quantyx:</b> <code>Task</code> (Classification / Regression) and <code>K</code> (recommended: 3 to 15, default: 3).</p>
    <p><b>Advantages:</b> No explicit training phase; simple to interpret; handles irregular decision boundaries.</p>
    <p><b>Limitations:</b> Slow inference on massive datasets; degrades with irrelevant features; requires prior normalization.</p>
    <p><b>Industrial Case:</b> Predicting resin cure duration based on historically similar chemical formulations.</p>
</div>

<div class="model-card">
    <h3>4. Random Forest</h3>
    <p><b>Type:</b> Supervised Learning / Ensemble Learning (Bagging of Decision Trees).</p>
    <p><b>Description:</b> Constructs an ensemble of decorrelated decision trees on bootstrap samples and aggregates outputs via voting or averaging.</p>
    <p><b>Recommended Use:</b> General industrial predictive modeling, defect classification, property regression.</p>
    <p><b>Parameters in Quantyx:</b>
        <ul>
            <li><code>Trees</code> (n_estimators): 10 to 1000 (recommended: 50 to 300, default: 100).</li>
            <li><code>Max Depth</code>: maximum tree depth (recommended: 4 to 12, default: 6).</li>
        </ul>
    </p>
    <p><b>Advantages:</b> Robust against noise; does not require feature scaling; supports multi-output targets; computes reliable Feature Importance.</p>
    <p><b>Limitations:</b> Larger memory footprint; less transparent than single decision trees.</p>
    <p><b>Industrial Case:</b> Predicting tensile strength and yield point in steel manufacturing based on alloy composition and furnace temperatures.</p>
</div>

<div class="model-card">
    <h3>5. XGBoost (Extreme Gradient Boosting)</h3>
    <p><b>Type:</b> Supervised Learning / Gradient Boosted Decision Trees.</p>
    <p><b>Description:</b> Sequentially builds decision trees where each new tree corrects residual errors of prior trees using second-order gradients and $L1/L2$ regularization.</p>
    <p><b>Recommended Use:</b> High-stakes predictive modeling, complex tabular datasets, competition-grade accuracy.</p>
    <p><b>Parameters in Quantyx:</b>
        <ul>
            <li><code>Trees</code> (n_estimators): 10 to 1000 (recommended: 50 to 300, default: 100).</li>
            <li><code>Max Depth</code>: maximum tree depth (recommended: 3 to 8, default: 6).</li>
            <li><code>Learning Rate</code> ($\eta$): shrinkage factor per step (recommended: 0.01 to 0.2, default: 0.1).</li>
        </ul>
    </p>
    <p><b>Advantages:</b> State-of-the-art predictive accuracy on tabular data; fast training; built-in regularization against overfitting.</p>
    <p><b>Limitations:</b> Requires tuning; sensitive to learning rate and depth settings.</p>
    <p><b>Industrial Case:</b> Predicting refinery distillation impurity levels with advance alert thresholds.</p>
</div>
"""
    },
    {
        "id": "ml_training",
        "title": "14. Model Training & Hyperparameter Tuning",
        "category": "Machine Learning",
        "keywords": ["training", "auto-tune", "gridsearch", "randomizedsearch", "hyperparameters", "cross-validation"],
        "summary": "Training predictive models in background threads and automated hyperparameter optimization via Auto-Tune.",
        "content_html": r"""
<h2>14. Model Training & Hyperparameter Tuning</h2>

<h3>How to Train a Model</h3>
<ol>
    <li>Check the desired feature columns in <code>All Variables</code> on the left.</li>
    <li>Highlight the response variable in <code>Target(s) (Y)</code> in ML Settings.</li>
    <li>Set <code>Task</code> to <code>Classification</code> or <code>Regression</code>.</li>
    <li>Adjust parameters manually or use Auto-Tune.</li>
    <li>Click <b>Train Model</b>. Training executes asynchronously using Qt's <code>QThreadPool</code> without UI freezing.</li>
</ol>

<h3>✨ Auto-Tune (Automated Hyperparameter Optimization)</h3>
<p>The <b>Auto-Tune</b> button optimizes model parameters automatically:</p>
<ul>
    <li><b>Engine:</b> Powered by Scikit-Learn's <code>RandomizedSearchCV</code> with <b>3-Fold Cross-Validation</b>.</li>
    <li><b>Threaded Execution:</b> Operates with thread-based backend (<code>joblib.parallel_backend('threading')</code>), ensuring 100% stability in Windows PyInstaller binaries.</li>
    <li><b>Search Spaces:</b>
        <ul>
            <li><b>KNN:</b> Searches neighbor counts from 2 to 19.</li>
            <li><b>Random Forest:</b> Evaluates tree counts [50, 100, 200, 300] and depths [None, 3, 5, 10, 20].</li>
            <li><b>XGBoost:</b> Evaluates tree counts [50, 100, 200], depths [3, 5, 10], and learning rates [0.01, 0.05, 0.1, 0.2].</li>
        </ul>
    </li>
    <li><b>Immediate Application:</b> When complete, best parameters are displayed in a dialog, automatically updated in the UI inputs, and the final model is trained on the full dataset.</li>
</ul>
"""
    },
    {
        "id": "ml_eval",
        "title": "15. Model Evaluation & Performance Metrics",
        "category": "Machine Learning",
        "keywords": ["evaluation", "metrics", "r2", "rmse", "mae", "accuracy", "confusion matrix", "feature importance"],
        "summary": "Interpreting Confusion Matrices, True vs. Predicted plots (45° line), R², RMSE, MAE, and Feature Importance.",
        "content_html": r"""
<h2>15. Model Evaluation & Performance Metrics</h2>
<p>Quantyx renders graphical and numerical validation metrics immediately after training completes.</p>

<h3>1. Regression Evaluation</h3>
<ul>
    <li><b>True vs. Predicted Scatter Plot:</b> Compares actual values ($y_{true}$) on the horizontal axis against model estimates ($y_{pred}$) on the vertical axis.</li>
    <li><b>Ideal 45° Dashed Red Line:</b> Represents perfect prediction ($y_{pred} = y_{true}$). Accurate models tightly cluster points around this line.</li>
    <li><b>Numerical Metrics:</b>
        <ul>
            <li><b>Coefficient of Determination ($R^2$):</b> Proportion of variance explained by the model (ranges from $-\infty$ to $1.0$, where $1.0$ is perfect fit).</li>
            <li><b>RMSE (Root Mean Squared Error):</b> Square root of mean squared errors, in the original target units.</li>
            <li><b>MAE (Mean Absolute Error):</b> Average absolute magnitude of errors across all samples.</li>
        </ul>
    </li>
</ul>

<h3>2. Classification Evaluation</h3>
<ul>
    <li><b>Confusion Matrix:</b> Visual plasma heatmap comparing true labels against predicted labels. The diagonal shows correct predictions; off-diagonal elements show classification errors.</li>
    <li><b>Global Accuracy:</b> Proportion of correct predictions over total samples ($Accuracy = \frac{\text{Correct}}{\text{Total}}$).</li>
</ul>

<h3>3. Feature Importance</h3>
<ul>
    <li>Click <b>Feature Importance</b> (for Random Forest and XGBoost).</li>
    <li>Opens a dialog displaying an ordered bar chart of relative feature contribution to impurity reduction (Gini/Gain).</li>
    <li>Enables engineers to identify which process parameters drive product variance.</li>
</ul>
"""
    },
    {
        "id": "ml_predict",
        "title": "16. Predictions & Production Inference Workflow",
        "category": "Machine Learning",
        "keywords": ["predict", "prediction", "inference", "new data", "production", "download results"],
        "summary": "Generating predictions on new production datasets lacking the target column.",
        "content_html": r"""
<h2>16. Predictions & Production Inference Workflow</h2>
<p>Use trained or loaded models to run batch predictions on new datasets that <b>do not contain the target variable</b>.</p>

<h3>Inference Step-by-Step</h3>
<ol>
    <li>Load your new production dataset via <b>File -> Open Data...</b>.</li>
    <li>Open the <b>Machine Learning Hub</b>.</li>
    <li>If you have a saved model file, click <b>Load Model</b> and select the <code>.pkl</code> file. Task, algorithm, and feature inputs are automatically restored.</li>
    <li>Click <b>Predict</b>.</li>
    <li>Quantyx checks feature compatibility: if any expected feature is missing, a clear warning identifies the missing columns.</li>
    <li>If compatible, predictions are calculated in milliseconds and appended to the dataset as <code>Predicted_<TargetName></code>.</li>
    <li>Click <b>Download Results</b> to export an Excel file with the predictions.</li>
</ol>
"""
    },
    {
        "id": "ml_multioutput",
        "title": "17. Multi-Output Machine Learning & Structured Export",
        "category": "Machine Learning",
        "keywords": ["multi-output", "multiple targets", "multi-target", "download results", "excel export"],
        "summary": "Modeling multiple targets simultaneously and exporting 3-sheet Excel reports.",
        "content_html": r"""
<h2>17. Multi-Output Machine Learning & Structured Export</h2>

<h3>Multi-Output Concept</h3>
<p>Industrial processes often affect multiple quality metrics simultaneously (e.g. heating profile affects both <i>Hardness</i> and <i>Elongation</i>). Quantyx supports native <b>Multi-Output</b> modeling.</p>

<h3>Configuring Multiple Targets</h3>
<ol>
    <li>In <code>Target(s) (Y)</code>, select two or more columns holding <code>Ctrl</code> or <code>Shift</code>.</li>
    <li>Quantyx automatically wraps estimators using Scikit-Learn's <code>MultiOutputRegressor</code> or <code>MultiOutputClassifier</code>.</li>
    <li>Click <b>Train Model</b> to train parallel estimators predicting all targets simultaneously.</li>
    <li>The evaluation plot aggregates outputs and computes individual metrics for each target plus global averages.</li>
</ol>

<h3>Structured 3-Sheet Excel Export (Download Results)</h3>
<p>Clicking <b>Download Results</b> generates a comprehensive Microsoft Excel (<code>.xlsx</code>) workbook with three dedicated sheets:</p>
<table class="doc-table">
    <tr><th>Excel Sheet</th><th>Detailed Contents</th></tr>
    <tr><td><b>Predictions</b></td><td>Contains actual values (<code>True_<Target></code>) and model predictions (<code>Predicted_<Target></code>) for every row.</td></tr>
    <tr><td><b>Metrics</b></td><td>Structured table of individual performance metrics per target (R², RMSE, MAE, or Accuracy) and the 'Global' average.</td></tr>
    <tr><td><b>Settings</b></td><td>Audit report with export timestamp, task type, algorithm, and target variable names.</td></tr>
</table>
"""
    },
    {
        "id": "projects",
        "title": "18. Project Management & Serialization (.quantyx & .pkl)",
        "category": "Projects",
        "keywords": ["projects", ".quantyx", ".pkl", "save project", "load project", "joblib", "persistence"],
        "summary": "Saving complete analysis sessions in .quantyx files and exporting lightweight models in .pkl files.",
        "content_html": r"""
<h2>18. Project Management & Serialization (.quantyx & .pkl)</h2>

<h3>1. Quantyx Project Files (.quantyx)</h3>
<p>The <code>.quantyx</code> file format is a compressed binary container (Joblib) saving your complete session state:</p>
<ul>
    <li><b>Saved State Includes:</b>
        <ul>
            <li>Raw loaded dataset.</li>
            <li>Filtered dataset.</li>
            <li>Active filter rules.</li>
            <li>Presentation gallery snapshots.</li>
            <li>Trained ML model weights, features, targets, task, and algorithm.</li>
        </ul>
    </li>
    <li><b>Save Project:</b> <code>File -> Save Project...</code> (or <code>Ctrl+S</code>).</li>
    <li><b>Load Project:</b> <code>File -> Load Project...</code> restores data, re-applies filters, reloads gallery images, and opens the ML Hub if a model was saved.</li>
</ul>

<h3>2. Standalone Model Files (.pkl)</h3>
<p>Save lightweight model weights for production deployment:</p>
<ul>
    <li><b>Save Model:</b> Exports a dictionary containing the estimator, required features, targets, task, and technique.</li>
    <li><b>Load Model:</b> Imports pre-trained models into new sessions for instant inference.</li>
</ul>
"""
    },
    {
        "id": "gallery",
        "title": "19. Executive Presentation Automation (PowerPoint Gallery)",
        "category": "Reporting",
        "keywords": ["powerpoint", "pptx", "reporting", "gallery", "presentation", "slides", "templates", "camera"],
        "summary": "Capturing plot snapshots with the toolbar camera and auto-compiling PowerPoint presentations.",
        "content_html": r"""
<h2>19. Executive Presentation Automation (PowerPoint Gallery)</h2>
<p>Quantyx automates generating presentation slides directly from your active exploratory and predictive charts.</p>

<h3>Generating Presentations</h3>
<ol>
    <li><b>Capture Snapshots:</b> Click <b>📸 Add Current Plot to Presentation</b> in the toolbar while viewing any plot, outlier view, or ML evaluation.</li>
    <li>The chart is rendered at high resolution and saved as a thumbnail in the <b>Gallery</b> dock.</li>
    <li>Capture multiple charts as needed (e.g. histograms, boxplots with tables, regression scatters).</li>
    <li>In the <b>Gallery</b> dock, select your corporate template in <code>Select Template</code>.</li>
    <li>Click <b>Generate PowerPoint (PPTX)</b>.</li>
    <li>Quantyx loads the template, finds blank slide layouts, and inserts each image centered with 0.5-inch margins.</li>
</ol>

<h3>Template Center</h3>
<ul>
    <li>Access <b>Settings -> Template Center...</b> to manage company presentation templates.</li>
    <li><b>Add Template:</b> Click <code>Add Template...</code> to import a <code>.pptx</code> template into <code>%APPDATA%\\Quantyx\\templates</code>.</li>
    <li><b>Remove Template:</b> Select an existing template and click <code>Remove Selected</code>.</li>
</ul>
"""
    },
    {
        "id": "settings",
        "title": "20. Settings, Theming & Application Updates",
        "category": "Settings",
        "keywords": ["settings", "dark mode", "light mode", "theme", "fusion", "updates", "github releases"],
        "summary": "Toggling dark/light themes, user preferences, and background update checks.",
        "content_html": r"""
<h2>20. Settings, Theming & Application Updates</h2>

<h3>Dark and Light Theme Toggling</h3>
<p>Quantyx features an integrated theming engine (<code>ThemeManager</code>) adapting to bright plant floors or dark control rooms:</p>
<ul>
    <li><b>Toggle Theme:</b> <b>Settings -> Toggle Light/Dark Theme</b>.</li>
    <li><b>Dark Mode:</b> Dark gray UI palette with black plot backgrounds and white axes to minimize eye strain.</li>
    <li><b>Light Mode:</b> Clean Qt Fusion palette with white plot backgrounds and dark axes, ideal for printing and projectors.</li>
    <li><b>Persistence:</b> Theme preference is saved automatically in <code>%APPDATA%\\Quantyx\\settings.json</code>.</li>
</ul>

<h3>Automated Update Checking</h3>
<p>On startup, a non-blocking thread checks the public GitHub releases API:</p>
<ul>
    <li>If a version newer than <code>1.1.0</code> is found, a prompt asks if you would like to download it.</li>
    <li>Clicking <i>Yes</i> opens the browser directly to the download page.</li>
    <li>Checks operate silently in the background without blocking the UI if offline.</li>
</ul>
"""
    },
    {
        "id": "tutorials",
        "title": "21. Step-by-Step Tutorials (Guided Walkthroughs)",
        "category": "Tutorials",
        "keywords": ["tutorials", "first project", "multi-output", "model comparison", "step-by-step", "walkthrough", "guides"],
        "summary": "6 guided, practical tutorials covering full workflows from data loading to multi-output modeling.",
        "content_html": r"""
<h2>21. Step-by-Step Tutorials (Guided Walkthroughs)</h2>

<div class="tutorial-box">
    <h3>Tutorial 1: End-to-End First Project</h3>
    <ol>
        <li><b>Load Data:</b> Open <code>File -> Open Data...</code> and select <code>dummy_data.csv</code> (or generate test data via <code>python utils/generate_dummy.py</code>).</li>
        <li><b>Explore Distributions:</b> Open the <code>Histogram</code> tab, set <code>Temperature</code> in <code>X Axis</code>, and click <code>Update Plot</code>. Check count, mean, and nulls in the statistics panel.</li>
        <li><b>Regression Analysis:</b> Open the <code>Scatter</code> tab, set <code>Temperature</code> in X and <code>Yield</code> in Y. Check <code>Linear Regression (Scatter)</code> in Plot Properties and click <code>Update Plot</code>.</li>
        <li><b>Outlier Cleaning:</b> Go to <code>Data Preprocessing -> Open Preprocessing Tool</code>. Click <code>Auto Detect Outliers (Isolation Forest)</code>. Review the red points, click <code>Remove Selected Points</code>, and click <code>🔙 Return to Plots</code>.</li>
        <li><b>Train Model:</b> Go to <code>Machine Learning -> Open ML Hub</code>. In <code>All Variables</code>, check <code>Temperature</code>, <code>Pressure</code>, <code>Flow_Rate</code>, and <code>Vibration</code>. Select <code>Yield</code> in <code>Target(s) (Y)</code>. Switch to <code>Random Forest</code> and click <code>Train Model</code>.</li>
        <li><b>Evaluate & Export:</b> Inspect the $R^2$ and true vs. predicted plot. Click <code>Download Results</code> to export the Excel report. Save your project via <code>File -> Save Project...</code> as <code>MyProject.quantyx</code>.</li>
    </ol>
</div>

<div class="tutorial-box">
    <h3>Tutorial 2: Advanced Multi-Output Model Training</h3>
    <ol>
        <li>Load a dataset containing multiple continuous target features.</li>
        <li>Open <code>Machine Learning -> Open ML Hub</code> and switch to the <code>XGBoost</code> tab.</li>
        <li>In <code>All Variables</code>, check all predictor features.</li>
        <li>In <code>Target(s) (Y)</code>, hold <code>Ctrl</code> and select multiple targets (e.g. <code>Yield</code> and <code>Temperature</code>).</li>
        <li>Set <code>Task</code> to <code>Regression</code> and click <code>Train Model</code>.</li>
        <li>Review global average metrics in the title and check <code>Feature Importance</code>.</li>
        <li>Click <code>Download Results</code> to generate the 3-sheet Excel workbook.</li>
    </ol>
</div>

<div class="tutorial-box">
    <h3>Tutorial 3: Practical Model Comparison</h3>
    <ol>
        <li>In the ML Hub, keep the same features and target selected.</li>
        <li><b>Model 1:</b> Switch to <code>K-Nearest Neighbors</code> (K=5) and click <code>Train Model</code>. Record $R^2$.</li>
        <li><b>Model 2:</b> Switch to <code>Random Forest</code> (100 trees, depth 6) and click <code>Train Model</code>. Record $R^2$.</li>
        <li><b>Model 3:</b> Switch to <code>XGBoost</code> and click <code>✨ Auto-Tune</code>. Wait for 3-fold cross-validation to find optimal parameters.</li>
        <li>Compare $R^2$, RMSE, and MAE across all three algorithms.</li>
        <li>On the best-performing model tab, click <code>Save Model</code> to export <code>BestModel.pkl</code>.</li>
    </ol>
</div>

<div class="tutorial-box">
    <h3>Tutorial 4: Creating a Minitab-Style Boxplot Table</h3>
    <ol>
        <li>Click the <code>Boxplot</code> tab.</li>
        <li>Select a continuous variable in <code>Y Axis</code> (e.g. <code>Yield</code>).</li>
        <li>In Plot Properties, check <code>Show X-Axis Data Table</code>.</li>
        <li>In <code>All Variables</code>, check multiple grouping columns (e.g. <code>Machine_ID</code> and <code>Operator</code>).</li>
        <li>Check <code>Show Means</code> and <code>Show Q1</code> in Plot Properties.</li>
        <li>Click <code>Update Plot</code> to view the nested statistical table below the X-axis.</li>
    </ol>
</div>

<div class="tutorial-box">
    <h3>Tutorial 5: Parallel Coordinates Investigation</h3>
    <ol>
        <li>Select the <code>Parallel Coordinates</code> tab.</li>
        <li>In <code>All Variables</code>, check 5 to 10 numeric columns.</li>
        <li>Set <code>Color by</code> to a category column (e.g. <code>Machine_ID</code>).</li>
        <li>Click <code>Update Plot</code>.</li>
        <li><b>Single Line Inspection:</b> Click any line to highlight it in red and display exact values at the top.</li>
        <li><b>Box Filtering:</b> Drag a yellow box across axes to select and highlight intersecting lines.</li>
    </ol>
</div>

<div class="tutorial-box">
    <h3>Tutorial 6: Automated Executive Presentation Generation</h3>
    <ol>
        <li>Generate a scatter plot with limit lines and click 📸 on the toolbar.</li>
        <li>Generate a Boxplot with table and click 📸.</li>
        <li>Generate a Correlation Matrix and click 📸.</li>
        <li>Train an ML model and click 📸.</li>
        <li>Open the <code>Gallery</code> dock to review thumbnails.</li>
        <li>Select a template in <code>Select Template</code> and click <code>Generate PowerPoint (PPTX)</code>.</li>
    </ol>
</div>
"""
    },
    {
        "id": "context_help",
        "title": "22. Contextual Help & Field Tooltips Reference",
        "category": "Reference",
        "keywords": ["tooltips", "contextual help", "fields", "recommended range", "field reference"],
        "summary": "Technical reference for interface inputs, recommended ranges, and parameter descriptions.",
        "content_html": r"""
<h2>22. Contextual Help & Field Tooltips Reference</h2>
<p>Every interactive input in Quantyx includes hover tooltips. Below is the technical reference table:</p>

<table class="doc-table">
    <tr><th>Field / Widget</th><th>Location</th><th>Technical Description</th><th>Recommended Range</th><th>Practical Example</th></tr>
    <tr><td><b>Trees (n_estimators)</b></td><td>ML Settings</td><td>Number of trees in the ensemble. Higher counts increase stability but extend compute time.</td><td>50 to 300 (default: 100)</td><td>100 trees for Random Forest or XGBoost.</td></tr>
    <tr><td><b>Max Depth</b></td><td>ML Settings</td><td>Maximum depth per tree. Controls model complexity and prevents overfitting.</td><td>3 to 10 (default: 6)</td><td>Depth 6 captures non-linearities without memorizing noise.</td></tr>
    <tr><td><b>Learning Rate ($\eta$)</b></td><td>ML Settings</td><td>Shrinkage factor per boosting step in XGBoost.</td><td>0.01 to 0.2 (default: 0.1)</td><td>0.05 for refined models with 200 trees.</td></tr>
    <tr><td><b>K (Neighbors / Clusters)</b></td><td>ML Settings</td><td>Number of nearest neighbors (KNN) or cluster count (K-Means).</td><td>3 to 15 (default: 3)</td><td>K=5 in KNN smooths random variance.</td></tr>
    <tr><td><b>Color Rule</b></td><td>Variables Dock</td><td>Boolean mathematical expression evaluated via Pandas eval for conditional point coloring.</td><td>Valid Pandas expression</td><td><code>Temperature > 100 and Pressure < 5</code></td></tr>
    <tr><td><b>Horizontal Upper Limit</b></td><td>Plot Properties</td><td>Draws a dashed horizontal line at the upper engineering specification.</td><td>Any real number</td><td><code>950.0</code> for Upper Specification Limit (USL).</td></tr>
    <tr><td><b>Horizontal Lower Limit</b></td><td>Plot Properties</td><td>Draws a dashed horizontal line at the lower engineering specification.</td><td>Any real number</td><td><code>700.0</code> for Lower Specification Limit (LSL).</td></tr>
    <tr><td><b>Point Size</b></td><td>Plot Properties</td><td>Pixel diameter of scatter and PCA points.</td><td>2 to 10 (default: 5)</td><td>3 for large datasets; 8 for small sets.</td></tr>
    <tr><td><b>Decimals X / Y</b></td><td>Plot Properties</td><td>Number of decimal places displayed on numeric axis ticks.</td><td>0 to 4 (default: 0 or 2)</td><td>2 decimals for voltage readings (e.g. 220.45).</td></tr>
    <tr><td><b>Missing Value Imputation</b></td><td>Preprocessing</td><td>Strategy to replace NaNs in numeric columns.</td><td>Mean, Median, Mode, KNN</td><td>Median for skewed columns or datasets with outliers.</td></tr>
    <tr><td><b>Scaling Method</b></td><td>Preprocessing</td><td>Normalization transformation to equalize variable magnitudes.</td><td>MinMax [0, 1] or Standard ($\mu=0, \sigma=1$)</td><td>StandardScaler for linear models/XGBoost; MinMax for KNN.</td></tr>
    <tr><td><b>Server Hostname</b></td><td>SQL Dialog</td><td>Databricks workspace hostname URL.</td><td>Valid workspace URL</td><td><code>adb-123456789.azuredatabricks.net</code></td></tr>
    <tr><td><b>HTTP Path</b></td><td>SQL Dialog</td><td>Databricks SQL Warehouse endpoint path.</td><td>Valid HTTP warehouse path</td><td><code>/sql/1.0/warehouses/abcdef123456</code></td></tr>
</table>
"""
    },
    {
        "id": "troubleshooting",
        "title": "23. Troubleshooting & Error Diagnostics",
        "category": "Support",
        "keywords": ["troubleshooting", "errors", "diagnostics", "exceptions", "solutions"],
        "summary": "Root cause analysis and resolution steps for all common operational issues.",
        "content_html": r"""
<h2>23. Troubleshooting & Error Diagnostics</h2>
<p>Refer to this diagnostic guide to resolve operational issues:</p>

<table class="doc-table">
    <tr><th>Symptom / Error</th><th>Probable Root Cause</th><th>Resolution Steps</th></tr>
    <tr>
        <td><b>Plot does not update after selecting variables.</b></td>
        <td>Quantyx uses on-demand plotting to prevent freezes with large datasets.</td>
        <td>Click the blue <b>Update Plot</b> button on the left panel to render the graph.</td>
    </tr>
    <tr>
        <td><b>Training Error: "Please check at least 1 numeric variable in 'All Variables'."</b></td>
        <td>No input feature checkboxes are selected in the left list.</td>
        <td>Check the boxes next to numeric predictor columns in <code>All Variables</code> before clicking Train Model.</td>
    </tr>
    <tr>
        <td><b>Training Error: "No target variable(s) selected."</b></td>
        <td>No variable is highlighted in <code>Target(s) (Y)</code>.</td>
        <td>Click your target variable in the <code>Target(s) (Y)</code> list in ML Settings to select it.</td>
    </tr>
    <tr>
        <td><b>Error: "All rows contain missing values (NaN) in selected variables."</b></td>
        <td>Selected features contain nulls across all rows.</td>
        <td>Go to <code>Data Preprocessing -> Open Preprocessing Tool</code> and apply <b>Median</b> or <b>KNN</b> imputation.</td>
    </tr>
    <tr>
        <td><b>Inference Error: "Feature mismatch! Model was trained on... Currently selected..."</b></td>
        <td>The active dataset is missing features used during model training.</td>
        <td>Ensure the new dataset contains the exact feature columns required by the model.</td>
    </tr>
    <tr>
        <td><b>Databricks Connection Failed.</b></td>
        <td>Expired PAT token, invalid HTTP path, or corporate firewall.</td>
        <td>Generate a new PAT token in Databricks, verify warehouse status, and ensure port 443 is unblocked.</td>
    </tr>
    <tr>
        <td><b>Export Error: "Permission denied" on Excel or PowerPoint.</b></td>
        <td>Target file is currently open in Microsoft Excel or PowerPoint.</td>
        <td>Close the open file in Office and retry the export in Quantyx.</td>
    </tr>
    <tr>
        <td><b>PowerPoint Error: "Template not found".</b></td>
        <td>The template was moved, deleted, or renamed on disk.</td>
        <td>Open <code>Settings -> Template Center...</code> and re-add your PowerPoint template.</td>
    </tr>
</table>
"""
    },
    {
        "id": "faq",
        "title": "24. Frequently Asked Questions (FAQ)",
        "category": "Support",
        "keywords": ["faq", "questions", "answers", "how to"],
        "summary": "Answers to frequently asked questions regarding everyday Quantyx operations.",
        "content_html": r"""
<h2>24. Frequently Asked Questions (FAQ)</h2>

<div class="faq-item">
    <h4>1. How do I load large datasets without freezing my computer?</h4>
    <p>Quantyx uses native virtualization and optimized columnar readers. For datasets exceeding 1 million rows, prefer <b>Parquet</b> or <b>Feather</b> formats, which load in milliseconds and use significantly less memory than raw CSVs.</p>
</div>

<div class="faq-item">
    <h4>2. Why don't plots render automatically when I click a variable?</h4>
    <p>This is an architectural safeguard. In datasets with hundreds of thousands of rows, re-plotting on every click causes noticeable lag. Select your inputs first, then click <b>Update Plot</b>.</p>
</div>

<div class="faq-item">
    <h4>3. Are my Databricks credentials stored in plain text?</h4>
    <p><b>No.</b> Credentials are encrypted and stored in the Windows Registry via Qt's <code>QSettings</code> framework. No plain text files or logs store passwords or tokens.</p>
</div>

<div class="faq-item">
    <h4>4. What does the R² score mean in the ML evaluation?</h4>
    <p>The $R^2$ score represents the proportion of target variance explained by the model. An $R^2 = 0.92$ means 92% of process variation is captured by the model.</p>
</div>

<div class="faq-item">
    <h4>5. When should I choose MinMax vs. StandardScaler in preprocessing?</h4>
    <p><b>MinMax</b> scales values to $[0, 1]$, preserving exact min/max bounds (ideal for KNN and K-Means). <b>StandardScaler</b> centers data around mean 0 with unit variance (ideal for linear models and XGBoost).</p>
</div>

<div class="faq-item">
    <h4>6. Can I use a trained model on a new file lacking the target column?</h4>
    <p><b>Yes!</b> Use the <code>Predict</code> button in the ML Hub. Load the new file, load or keep your model, and click <code>Predict</code>. Output columns are added and can be saved via <code>Download Results</code>.</p>
</div>

<div class="faq-item">
    <h4>7. How do I add my company's official PowerPoint template?</h4>
    <p>Go to <code>Settings -> Template Center...</code>, click <code>Add Template...</code>, and select your company <code>.pptx</code> file. It will be copied to <code>%APPDATA%\\Quantyx\\templates</code> and remain available in all sessions.</p>
</div>

<div class="faq-item">
    <h4>8. How do I save and restore an entire analysis session?</h4>
    <p>Go to <code>File -> Save Project...</code> and save a <code>.quantyx</code> file. Loading this file later restores all data, active filters, gallery snapshots, and trained models.</p>
</div>
"""
    },
    {
        "id": "best_practices",
        "title": "25. Best Practices & Analytical Guidelines",
        "category": "Guidelines",
        "keywords": ["best practices", "guidelines", "data science", "engineering", "overfitting"],
        "summary": "Engineering guidelines for data inspection, preventing overfitting, and model validation.",
        "content_html": r"""
<h2>25. Best Practices & Analytical Guidelines</h2>

<h3>1. Data Cleaning Discipline</h3>
<ul>
    <li><b>Inspect distributions before modeling:</b> Use the <code>Histogram</code> tab to check for missing values, severe skewness, or zero-variance sensor columns.</li>
    <li><b>Evaluate outliers with physical context:</b> Use <code>Isolation Forest</code> as an initial screening tool, but inspect scatter plots to verify whether flagged points are sensor noise or genuine physical excursions.</li>
</ul>

<h3>2. Modeling & Overfitting Prevention</h3>
<ul>
    <li><b>Start with baseline models:</b> Test simpler models like <b>Random Forest</b> with default hyperparameters before complex <b>XGBoost</b> architectures.</li>
    <li><b>Limit tree depth (Max Depth):</b> Trees with excessive depth (e.g. $> 15$) memorize training noise. Keep depth between 4 and 10 for optimal generalization.</li>
    <li><b>Use Auto-Tune for validation:</b> The <code>✨ Auto-Tune</code> button applies 3-fold cross-validation, protecting against over-optimistic evaluation metrics.</li>
</ul>

<h3>3. Validation & Reporting</h3>
<ul>
    <li><b>Evaluate multiple metrics:</b> Never rely on $R^2$ alone. Always verify that <b>RMSE</b> and <b>MAE</b> fall within engineering tolerances.</li>
    <li><b>Verify Feature Importance:</b> Review the Feature Importance plot with process engineers to ensure top features align with known physical/chemical principles.</li>
    <li><b>Standardize Executive Reports:</b> Use the <b>Gallery</b> with corporate templates to ensure visual consistency and technical credibility in stakeholder reviews.</li>
</ul>
"""
    }
]

def get_all_topics():
    return TOPICS

def get_topic_by_id(topic_id):
    for t in TOPICS:
        if t["id"] == topic_id:
            return t
    return None

def search_topics(query):
    if not query:
        return TOPICS
    q = query.lower().strip()
    results = []
    for t in TOPICS:
        score = 0
        if q in t["title"].lower():
            score += 10
        if q in t["summary"].lower():
            score += 5
        if any(q in kw for kw in t["keywords"]):
            score += 8
        if q in t["content_html"].lower():
            score += 2
            
        if score > 0:
            results.append((score, t))
    results.sort(key=lambda x: x[0], reverse=True)
    return [t for _, t in results]
