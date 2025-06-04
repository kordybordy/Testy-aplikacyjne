import sqlite3

conn = sqlite3.connect("pytania_egzaminacyjne.db")
c = conn.cursor()

# Dodanie brakujących kolumn, jeśli nie istnieją
try:
    c.execute("ALTER TABLE pytania ADD COLUMN poprawna_odpowiedz TEXT;")
except sqlite3.OperationalError:
    print("Kolumna 'poprawna_odpowiedz' już istnieje.")

try:
    c.execute("ALTER TABLE pytania ADD COLUMN podstawa_prawna TEXT;")
except sqlite3.OperationalError:
    print("Kolumna 'podstawa_prawna' już istnieje.")

conn.commit()
conn.close()
