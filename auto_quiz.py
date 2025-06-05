#!/usr/bin/env python3
"""Automatically complete a web-based quiz by selecting random answers.

Usage:
    python auto_quiz.py <quiz_url>

The script opens the provided URL in a Selenium-controlled browser,
chooses a random answer for each question and proceeds until no more
questions can be found. It then prints the page title of the final
screen. Selectors are generic and might require adjustments for a
specific quiz implementation.
"""

import random
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# Common labels for the next/submit button
NEXT_TEXTS = {
    "next", "dalej", "następne", "następny", "submit", "zakończ", "finish"
}


def find_clickable(driver, selector):
    """Return visible and enabled elements matching CSS selector."""
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
    except NoSuchElementException:
        return []
    return [e for e in elements if e.is_displayed() and e.is_enabled()]


def random_answer(driver):
    """Choose a random answer option if available."""
    options = find_clickable(driver, "input[type=radio], button.answer")
    if not options:
        return False
    random.choice(options).click()
    return True


def click_next(driver):
    """Click a button that looks like a Next/Submit control."""
    buttons = driver.find_elements(By.CSS_SELECTOR, "button, input[type=submit], input[type=button]")
    for btn in buttons:
        label = (btn.text or btn.get_attribute("value") or "").strip().lower()
        if label in NEXT_TEXTS and btn.is_enabled():
            btn.click()
            return True
    return False


def run_quiz(url: str) -> None:
    driver = webdriver.Firefox()
    driver.get(url)

    # Attempt to click a start button if present
    start_clicked = False
    for sel in ("button.start", "input.start"):
        elems = find_clickable(driver, sel)
        if elems:
            elems[0].click()
            start_clicked = True
            break

    while True:
        answered = random_answer(driver)
        moved = click_next(driver)
        if not answered and not moved:
            # Possibly finished
            break
        time.sleep(1)

    print("Quiz finished. Title:", driver.title)
    # Wait for the user to inspect the final screen before closing
    input("Press Enter to close the browser...")
    driver.quit()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python auto_quiz.py <quiz_url>")
        sys.exit(1)
    run_quiz(sys.argv[1])
