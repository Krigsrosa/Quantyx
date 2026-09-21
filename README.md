# Quantyx

**Quantyx** is a desktop application designed for high-performance Exploratory Data Analysis (EDA), Data Preprocessing, and Machine Learning, built specifically for industrial and scientific environments.

Developed with Python, **PyQt6**, and **PyQtGraph**, Quantyx delivers fast visualization for massive datasets, Databricks integration, and an intuitive interface.

---

## 🚀 Features

### 🔌 Data Ingestion
*   **Local Files:** Native support for .csv, .xlsx, .parquet, and .feather files.
*   **Databricks SQL Connection:** Securely connect to your Data Lakehouse. Write and execute custom SQL queries to pull data directly into the application.
*   **Dynamic Filtering:** Use the interactive *Filters Panel* to instantly slice your dataset using numeric ranges and categorical conditions. All plots and data tables update in real-time.

### 🧹 Data Preprocessing
*   **Missing Value Imputation:** Handle missing data using Mean, Median, Mode, or advanced **KNN Imputation**.
*   **Data Scaling:** Normalize numeric features using MinMaxScaler or StandardScaler.
*   **Outlier Management:** Manually remove noisy data points directly from interactive scatter plots, or use the **Auto Detect Outliers** tool (powered by *Isolation Forest*) to automatically clean anomalies.

### 📊 High-Performance Visualizations (PyQtGraph)
*   **Boxplots:** Advanced multi-variable nesting with Minitab-style statistical tables aligned under the X-axis. Toggle exact statistical values (Means, Q1, Q3) directly on the plot.
*   **Parallel Coordinates:** Visualize highly-dimensional datasets effortlessly.
*   **Scatter & Line Plots:** Capable of rendering millions of points without freezing. Automatic datetime detection for time-series data.
*   **Correlation Matrix & Histograms:** Quick statistical distribution analysis.
*   **Customization:** Fully customizable axes, dynamic color pickers, titles, and horizontal dashed Limit Lines.

### 🧠 Machine Learning Studio
*   **Supervised Learning:** Train classification and regression models using *Random Forest* and *XGBoost*.
*   **Unsupervised Learning:** Discover hidden clusters and patterns using *K-Means* and *PCA*.
*   **Auto-Tune:** Optimize hyperparameters automatically with *GridSearchCV*.
*   **Model Evaluation:** View interactive Confusion Matrices, Residual Plots, R² scores, and Feature Importance graphs.
*   **Deployment:** Save your trained models as .pkl files and reload them later to run predictions on new data.

### 📸 Presentation Gallery & Export
*   **PowerPoint Automation:** Take snapshots of your plots using the 📸 camera tool. Go to the *Presentation Gallery*, select your custom company .pptx template, and automatically generate a professional presentation report.
*   **High-Res Export:** Export individual plots as .png or .pdf.
*   **Export Filtered Data:** Save your cleaned and filtered dataset to a new CSV file.

### ⚙️ Settings & Theming
*   **Dark / Light Mode:** A fully integrated theming engine that automatically saves your preference.
*   **Template Center:** Manage and add your custom PowerPoint templates directly from the settings menu.

---

## 🛠️ Installation & Build

### Requirements
*   Python 3.12+
*   Dependencies listed in requirements.txt

### Running from Source
1. Clone the repository.
2. Create a virtual environment and install the requirements:
   \\cmd
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   \3. Run the application:
   \\cmd
   python main.py
   \
### Building Executables
Quantyx includes an interactive build script (\build.bat\) to easily package the application for distribution. Just run it and choose your preferred output:
1. **PyInstaller (One-Dir):** Recommended for testing.
2. **PyInstaller (One-File):** Generates a single standalone \.exe\.
3. **Pynsist (NSIS Installer):** Generates a professional Windows Setup Installer that installs in the user's \AppData\ directory (Requires no Administrator privileges).

---

## 🔒 Security & Privacy
*   **Credentials:** Databricks SQL tokens and host paths are encrypted and stored safely in the Windows Registry, **never** in local text files.
*   **Preferences:** User settings and custom templates are stored securely in \%APPDATA%\Quantyx\.

---

## 📄 License
This project is licensed under the MIT License. See the \LICENSE\ file for more details.
