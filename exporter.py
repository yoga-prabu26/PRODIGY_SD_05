"""
exporter.py
-----------
Handles exporting scraped product data into CSV, Excel (.xlsx), and
JSON formats using pandas and openpyxl.
"""

import os
import json
import pandas as pd
from datetime import datetime


class DataExporter:
    """Exports product data to various structured file formats."""

    COLUMNS = ["name", "price", "rating", "reviews_count",
               "availability", "link", "category", "image_url"]

    def __init__(self, export_dir="exports"):
        self.export_dir = export_dir
        os.makedirs(self.export_dir, exist_ok=True)

    def _to_dataframe(self, products):
        if not products:
            return pd.DataFrame(columns=self.COLUMNS)
        if isinstance(products[0], dict):
            return pd.DataFrame(products)
        return pd.DataFrame(products, columns=self.COLUMNS)

    def _timestamped_filename(self, prefix, ext):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.export_dir, f"{prefix}_{ts}.{ext}")

    def export_csv(self, products, filename=None):
        df = self._to_dataframe(products)
        path = filename or self._timestamped_filename("webscrapex_export", "csv")
        df.to_csv(path, index=False, encoding="utf-8")
        return path

    def export_excel(self, products, filename=None):
        df = self._to_dataframe(products)
        path = filename or self._timestamped_filename("webscrapex_export", "xlsx")
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Products")
            workbook = writer.book
            worksheet = writer.sheets["Products"]
            for col_cells in worksheet.columns:
                length = max(len(str(cell.value)) if cell.value else 0 for cell in col_cells)
                worksheet.column_dimensions[col_cells[0].column_letter].width = min(length + 2, 50)
        return path

    def export_json(self, products, filename=None):
        df = self._to_dataframe(products)
        path = filename or self._timestamped_filename("webscrapex_export", "json")
        records = df.to_dict(orient="records")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=4, ensure_ascii=False)
        return path
