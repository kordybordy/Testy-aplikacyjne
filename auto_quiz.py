import random
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def find_clickable(driver, selector):
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
    except NoSuchElementException:
        return []
    return [e for e in elements if e.is_displayed() and e.is_enabled()]


def random_answer(driver):
    options = find_clickable(driver, "input[type=radio], .stButton")
    if not options:
        print("Brak opcji do kliknięcia.")
        return False
    choice = random.choice(options)
    print("Klikam odpowiedź:", choice.get_attribute("value") or choice.text)
    choice.click()
    return True


def click_by_text(driver, text, timeout=3):
    try:
        WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(., '{text}')]"))
        )
        button = driver.find_element(By.XPATH, f"//button[contains(., '{text}')]")
        if button.is_displayed() and button.is_enabled():
            print(f"Klikam przycisk: {text}")
            button.click()
            return True
    except:
        pass
    return False


def wait_for_buttons(driver, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Zatwierdź odpowiedź')]"))
        )
        print("Znaleziono przycisk 'Zatwierdź odpowiedź'")
    except:
        print("Nie znaleziono przycisku 'Zatwierdź odpowiedź'")


def run_quiz(url: str) -> None:
    driver = webdriver.Firefox()
    driver.get(url)
    wait_for_buttons(driver)

    while True:
        answered = random_answer(driver)
        submitted = click_by_text(driver, "Zatwierdź odpowiedź")
        nexted = click_by_text(driver, "Następne pytanie")

        if not answered and not submitted and not nexted:
            print("Brak dalszych akcji – zakończono.")
            break

        time.sleep(0.3)  # minimal wait to let UI settle

    print("Quiz finished. Title:", driver.title)
    input("Press Enter to close the browser...")
    driver.quit()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python auto_quiz.py <quiz_url>")
        sys.exit(1)
    run_quiz(sys.argv[1])
