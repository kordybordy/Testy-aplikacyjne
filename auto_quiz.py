import sqlite3
import random

DB_PATH = "pytania_egzaminacyjne.db"
QUESTION_LIMIT = 150


def get_random_questions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT tresc, odpowiedz_a, odpowiedz_b, odpowiedz_c, poprawna_odpowiedz FROM pytania"
    )
    all_questions = cursor.fetchall()
    conn.close()
    return random.sample(all_questions, min(QUESTION_LIMIT, len(all_questions)))


def run_quiz():
    questions = get_random_questions()
    score = 0
    wrong_answers = []

    for index, q in enumerate(questions, start=1):
        tresc, a, b, c, correct = q
        chosen = random.choice(["A", "B", "C"])
        correct_letter = (correct or "").strip().upper()

        if chosen == correct_letter:
            score += 1
        else:
            wrong_answers.append((tresc, chosen, correct_letter))

        print(f"{index}/{len(questions)}. Wybrano {chosen}, prawidłowa {correct_letter or 'BRAK'}")

    print("\n===== Koniec quizu =====")
    print(f"Wynik: {score} / {len(questions)}")

    if wrong_answers:
        print(f"\nBłędne odpowiedzi ({len(wrong_answers)}):")
        for tresc, chosen, correct in wrong_answers:
            print(f"- Twoja odpowiedź {chosen}, poprawna {correct or 'BRAK'}")


if __name__ == "__main__":
    run_quiz()
