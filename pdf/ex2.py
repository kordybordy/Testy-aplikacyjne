import fitz  # PyMuPDF
import re
import sqlite3
import os

# Przygotowanie bazy danych
conn = sqlite3.connect("pytania_egzaminacyjne.db")
c = conn.cursor()

# Upewnienie się, że kolumny istnieją
c.execute("PRAGMA table_info(pytania)")
columns = [row[1] for row in c.fetchall()]

if "poprawna_odpowiedz" not in columns:
    try:
        c.execute("ALTER TABLE pytania ADD COLUMN poprawna_odpowiedz TEXT")
    except sqlite3.OperationalError:
        pass

if "podstawa_prawna" not in columns:
    try:
        c.execute("ALTER TABLE pytania ADD COLUMN podstawa_prawna TEXT")
    except sqlite3.OperationalError:
        pass

# Utworzenie tabeli jeśli nie istnieje
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
        if page_num == 0:
            continue
        blocks = page.get_text("blocks")
        blocks.sort(key=lambda b: (b[1], b[0]))
        for b in blocks:
            line = b[4].strip()
            if not line:
                continue
            if re.match(r'^\d+$', line):
                continue
            if "EGZAMIN WSTĘPNY DLA KANDYDATÓW NA APLIKANTÓW ADWOKACKICH I RADCOWSKICH" in line:
                continue
            text += line + "\n"

    text = re.sub(r'EGZAMIN WSTĘPNY DLA KANDYDATÓW NA APLIKANTÓW ADWOKACKICH I RADCOWSKICH \d+\n?', '', text)

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

def extract_answers_from_pdf(answers_pdf_path):
    rok_match = re.search(r'(\d{4})', answers_pdf_path)
    rok = int(rok_match.group(1)) if rok_match else None

    doc = fitz.open(answers_pdf_path)
    text = "\n".join([page.get_text() for page in doc])
    pattern = re.compile(r'(\d+)\.\s+([ABC])\s+(.*?)\s*(?=\n\d+\.|\Z)', re.DOTALL)
    matches = pattern.findall(text)

    for nr, litera, podstawa in matches:
        c.execute("""
            UPDATE pytania
            SET poprawna_odpowiedz = ?, podstawa_prawna = ?
            WHERE numer = ? AND rok = ?
        """, (litera, podstawa.strip(), int(nr), rok))
    conn.commit()

# Pliki z odpowiedziami i podstawami prawnymi
answer_files = [
    "Wykaz_prawid\u0142owych_odpowiedzi_do_zestawu_pyta\u0144_testowych_na_egzamin_wst\u0119pny_na_aplikacj\u0119_adwokack\u0105_i_radcowsk\u0105_28_wrze\u015bnia_2024_.pdf",
    "Wykaz_prawid\u0142owych_odpowiedzi_do_zestawu_pyta\u0144_testowych_na_egzamin_wst\u0119pny_na_aplikacj\u0119_adwokack\u0105_i_radcowsk\u0105_30_wrze\u015bnia_2023_r.pdf",
    "Wykaz_prawid\u0142owych_odpowiedzi_do_zestawu_pyta\u0144_testowych_na_egzamin_wst\u0119pny_na_aplikacj\u0119_adwokack\u0105_i_radcowsk\u0105_25_wrze\u015bnia_2021_r.pdf",
    "Wykaz_prawid\u0142owych_odpowiedzi_do_zestawu_pyta\u0144_testowych_na_egzamin_wst\u0119pny_na_aplikacj\u0119_adwokack\u0105_i_radcowsk\u0105_24_wrze\u015bnia_2022_r.pdf"
]

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

    for ans_file in answer_files:
        if os.path.exists(ans_file):
            print(f"Uzupełnianie odpowiedzi: {ans_file}")
            extract_answers_from_pdf(ans_file)
        else:
            print(f"Nie znaleziono pliku z odpowiedziami: {ans_file}")

if __name__ == "__main__":
    main()
    conn.close()
