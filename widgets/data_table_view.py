from PyQt6.QtWidgets import QTableView, QAbstractItemView
from PyQt6.QtCore import QAbstractTableModel, Qt, QModelIndex
import pandas as pd

class PandasTableModel(QAbstractTableModel):
    """
    A custom Pandas table model to lazily load and display large DataFrames.
    """
    def __init__(self, data=None):
        super().__init__()
        self._data = pd.DataFrame() if data is None else data

    def update_data(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return self._data.shape[0]

    def columnCount(self, parent=QModelIndex()):
        return self._data.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid():
            if role == Qt.ItemDataRole.DisplayRole:
                val = self._data.iloc[index.row(), index.column()]
                if pd.isna(val):
                    return ""
                if isinstance(val, float):
                    return f"{val:.4f}"
                return str(val)
            elif role == Qt.ItemDataRole.TextAlignmentRole:
                val = self._data.iloc[index.row(), index.column()]
                if isinstance(val, (int, float)):
                    return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])
            if orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])
        return None

class DataTableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_model = PandasTableModel()
        self.setModel(self.table_model)
        
    def set_dataframe(self, df):
        self.table_model.update_data(df)
        self.resizeColumnsToContents()
