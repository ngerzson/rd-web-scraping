import pandas as pd
import json
from openpyxl import load_workbook
from openpyxl.worksheet.table import Table, TableStyleInfo

# Load JSON file
json_file_path = "ipon_notebooks.json"
with open(json_file_path, "r", encoding="utf-8") as f:
    data = json.load(f)
print("JSON fájl beolvasva")
# Convert to DataFrame
df = pd.DataFrame(data)

# Rename columns for Excel output
df = df.rename(columns={
    'product_link': 'A termék ipon.hu linkje',
    'category_link': 'A gyűjtőoldal linkje',
    'image': 'A termékkép src-je (megnyitható url)',
    'name': 'A termék neve',
    'price': 'A termék ára',
    'pozicio': 'Pozíció',
    'time': 'Az adatgyűjtés időpontja'
})

# Export to Excel
output_excel_path = "ipon_notebooks.xlsx"
df.to_excel(output_excel_path, index=False)
print("Excelbe konvertálva")