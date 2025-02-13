import openpyxl

# Cesta k Excel souboru
excel_path = r"C:\Python projects\Kapacity - projekt\Sample data\Prevod vyrobku.xlsx"
# Cesta k textovému souboru
txt_path = r"C:\Python projects\Kapacity - projekt\CM02.txt"

# Načtení Excelu
wb = openpyxl.load_workbook(excel_path)
sheet = wb.active

# Načteme celý obsah textového souboru do proměnné
with open(txt_path, "r", encoding="cp1250") as f:
    text_content = f.read()

for row in sheet.iter_rows(min_row=2):  # min_row=2 => záhlaví v prvním řádku
    old_value = row[0].value  # Sloupec A
    new_value = row[1].value  # Sloupec B

    if old_value and new_value:
        old_str = str(old_value)
        new_str = str(new_value)

        # Nahrazení všech výskytů stringu
        text_content = text_content.replace(old_str, new_str)

# Uložit zpět do souboru
with open(txt_path, "w", encoding="cp1250") as f:
    f.write(text_content)

print(f"Hotovo! V souboru {txt_path} byly nahrazeny uvedené hodnoty.")