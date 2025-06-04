import sqlite3
import random
import streamlit as st
import time

# Stałe
DB_PATH = "pytania_egzaminacyjne.db"
QUESTION_LIMIT = 150
QUIZ_DURATION_SECONDS = 150 * 60  # 150 minut

# Funkcja do losowania pytań
def get_random_questions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT rok, numer, tresc, odpowiedz_a, odpowiedz_b, odpowiedz_c, poprawna_odpowiedz, podstawa_prawna FROM pytania")
    all_questions = cursor.fetchall()
    conn.close()
    return random.sample(all_questions, min(QUESTION_LIMIT, len(all_questions)))

# Reset sesji
if st.button("🔄 Zagraj od nowa"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()

# Inicjalizacja sesji
if "questions" not in st.session_state:
    st.session_state.questions = get_random_questions()
    st.session_state.current = 0
    st.session_state.score = 0
    st.session_state.answers = []
    st.session_state.start_time = time.time()
    st.session_state.retry_mode = False
    st.session_state.feedback_shown = False
    st.session_state.feedback_message = ""
    st.session_state.legal_basis_text = ""

# Sprawdź czas pozostały
elapsed = time.time() - st.session_state.start_time
remaining = QUIZ_DURATION_SECONDS - elapsed

if remaining <= 0:
    st.warning("⏰ Czas minął!")
    st.session_state.current = len(st.session_state.questions)
    st.rerun()

# Wyświetlenie czasu i paska postępu
minutes = int(remaining // 60)
seconds = int(remaining % 60)
st.write(f"### ⏳ Pozostały czas: {minutes:02d}:{seconds:02d}")
st.progress((st.session_state.current + 1) / max(QUESTION_LIMIT, len(st.session_state.questions)))

questions = st.session_state.questions
current_index = st.session_state.current

if current_index < len(questions):
    q = questions[current_index]
    rok, numer, tresc, a, b, c, correct, legal_basis = q

    correct = (correct or '').strip().upper()

    st.write(f"### Pytanie {current_index + 1} z {len(questions)}")
    st.write(tresc)

    user_answer = st.radio("Wybierz odpowiedź:", [f"A: {a}", f"B: {b}", f"C: {c}"], key=f"user_answer_{current_index}")

    if st.button("Zatwierdź odpowiedź", key=f"submit_{current_index}"):
        if not user_answer:
            st.warning("Proszę wybrać odpowiedź.")
            st.stop()

        user_letter = user_answer[0].upper()

        if user_letter == correct:
            st.session_state.score += 1
            st.session_state.answers.append((q, user_letter, correct))
            st.session_state.feedback_message = "✅ Poprawna odpowiedź!"
        else:
            st.session_state.answers.append((q, user_letter, correct))
            st.session_state.feedback_message = f"❌ Zła odpowiedź. Poprawna to: {correct if correct else 'nieznana'}"

        st.session_state.legal_basis_text = legal_basis if legal_basis else "Brak podstawy prawnej."
        st.session_state.feedback_shown = True

    if st.session_state.feedback_shown:
        st.info(st.session_state.feedback_message)
        if st.session_state.legal_basis_text:
            st.markdown(f"📘 **Podstawa prawna:** {st.session_state.legal_basis_text}", unsafe_allow_html=True)
        if st.button("Następne pytanie", key=f"next_{current_index}"):
            st.session_state.current += 1
            st.session_state.feedback_shown = False
            st.rerun()

else:
    st.write("## ✅ Koniec quizu!")
    st.write(f"Twój wynik: {st.session_state.get('score', 0)} / {len(st.session_state.get('questions', []))}")

    wrong_answers = [(q, ua, ca) for q, ua, ca in st.session_state.answers if ua != ca]
    if wrong_answers:
        st.write(f"🔁 Masz {len(wrong_answers)} błędnych odpowiedzi. Możesz je powtórzyć.")
        if st.button("Tryb powtórki"):
            st.session_state.questions = [q for q, ua, ca in wrong_answers]
            st.session_state.current = 0
            st.session_state.score = 0
            st.session_state.answers = []
            st.session_state.start_time = time.time()
            st.session_state.retry_mode = True
            st.session_state.feedback_shown = False
            st.session_state.feedback_message = ""
            st.session_state.legal_basis_text = ""
            st.rerun()
