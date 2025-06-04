import fitz  # PyMuPDF
import re
import sqlite3
import os

# Przygotowanie bazy danych
conn = sqlite3.connect("pytania_egzaminacyjne.db")
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS pytania (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numer INTEGER,
        tresc TEXT,
        odpowiedz_a TEXT,
        odpowiedz_b TEXT,
        odpowiedz_c TEXT,
        poprawna_odpowiedz TEXT,
        podstawa_prawna TEXT,
        rok INTEGER
    )
''')
conn.commit()

# Funkcja do ekstrakcji pytań z jednego pliku PDF
def extract_questions_from_pdf(pdf_path):
    rok_match = re.search(r'(\d{4})', pdf_path)
    rok = int(rok_match.group(1)) if rok_match else None

    doc = fitz.open(pdf_path)
    text = ""
    for page_num, page in enumerate(doc):
        # Pomijamy stronę tytułową
        if page_num == 0:
            continue
        # Usuwamy stopki i numerację stron
        blocks = page.get_text("blocks")
        blocks.sort(key=lambda b: (b[1], b[0]))
        for b in blocks:
            line = b[4].strip()
            if not line:
                continue
            # Pomijamy numerację stron i stopki egzaminacyjne
            if re.match(r'^\d+$', line):
                continue
            if "EGZAMIN WSTĘPNY DLA KANDYDATÓW NA APLIKANTÓW ADWOKACKICH I RADCOWSKICH" in line:
                continue
            text += line + "\n"

    # Usuwanie pozostałości stopki jeśli jakiekolwiek przeszły
    text = re.sub(r'EGZAMIN WSTĘPNY DLA KANDYDATÓW NA APLIKANTÓW ADWOKACKICH I RADCOWSKICH \d+\n?', '', text)

    # Parsowanie pytań
    pattern = re.compile(r'(\d+)\.\s*(.*?)\nA\.\s*(.*?)\nB\.\s*(.*?)\nC\.\s*(.*?)(?=\n\d+\.|\Z)', re.DOTALL)
    matches = pattern.findall(text)
    for match in matches:
        numer = int(match[0])
        tresc = match[1].strip()
        odp_a = match[2].strip()
        odp_b = match[3].strip()
        odp_c = match[4].strip()

        c.execute("""
            INSERT INTO pytania (numer, tresc, odpowiedz_a, odpowiedz_b, odpowiedz_c, poprawna_odpowiedz, podstawa_prawna, rok)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (numer, tresc, odp_a, odp_b, odp_c, None, None, rok))
    conn.commit()

# Ścieżki do plików PDF
pdf_files = [
    "Zestaw_pyta\u0144_testowych_na_egzamin_wst\u0119pny_dla_kandydat\u00f3w_na_aplikant\u00f3w_adwokackich_i_radcowskich_28_wrze\u015bnia_2024-1.pdf",
    "Zestaw_pyta\u0144_testowych_na_egzamin_wst\u0119pny_dla_kandydat\u00f3w_na_aplikant\u00f3w_adwokackich_i_radcowskich_30_wrze\u015bnia_2023_r.pdf",
    "Zestaw_pyta\u0144_testowych_na_egzamin_wst\u0119pny_dla_kandydat\u00f3w_na_aplikant\u00f3w_adwokackich_i_radcowskich_26_wrze\u015bnia_2020_r.pdf",
    "Zestaw_pyta\u0144_testowych_na_egzamin_wst\u0119pny_dla_kandydat\u00f3w_na_aplikant\u00f3w_adwokackich_i_radcowskich_28_wrze\u015bnia_2024.pdf"
]

# Wykonanie ekstrakcji
def main():
    for file in pdf_files:
        if os.path.exists(file):
            print(f"Przetwarzanie: {file}")
            extract_questions_from_pdf(file)
        else:
            print(f"Nie znaleziono pliku: {file}")

if __name__ == "__main__":
    main()
    conn.close()
