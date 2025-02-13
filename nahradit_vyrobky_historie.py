import openpyxl
import os

excel_path = r"C:\Python projects\Kapacity - projekt\Sample data\Prevod vyrobku.xlsx"
txt_folder = r"C:\Python projects\Kapacity - projekt\Historie"

# Načtení Excelu a aktivní list
wb = openpyxl.load_workbook(excel_path)
sheet = wb.active

# Funkce, která projde roky a měsíce v zadaném rozsahu
def generate_year_month_files(start_year, start_month, end_year, end_month):

    year = start_year
    month = start_month
    
    while True:
        yield year, month
        month += 1
        if month > 12:
            month = 1
            year += 1

        # Ukončit pokud jsem za posledním měsícem
        if (year > end_year) or (year == end_year and month > end_month):
            break

# Hlavní smyčka pro nahrazení obsahu ve všech souborech
for (year, month) in generate_year_month_files(2024, 1, 2025, 2):
    filename = f"{year}_{month:02d}.txt" # Vytvoření názvu - zajištěno, že měsíc bude vždy dvoumístný
    txt_path = os.path.join(txt_folder, filename)

    # Ověření, že soubor existuje
    if not os.path.isfile(txt_path):
        print(f"Soubor {txt_path} neexistuje, přeskočeno.")
        continue
    
    # Obsah souboru
    with open(txt_path, "r", encoding="cp1250") as f:
        text_content = f.read()

    # Nahrazení: sloupce A = původní, B = nová hodnota
    for row in sheet.iter_rows(min_row=2):  # v prvním řádku je záhlaví
        old_value = row[0].value  # Sloupec A
        new_value = row[1].value  # Sloupec B

        if old_value and new_value:
            old_str = str(old_value)
            new_str = str(new_value)
            text_content = text_content.replace(old_str, new_str)

    # Uložení nového obsahu zpět do souboru
    with open(txt_path, "w", encoding="cp1250") as f:
        f.write(text_content)

    print(f"Hotovo: {txt_path}")

print("Všechny zadané soubory byly zpracovány.")