from typing import List


def ask_boolean_question(question: str):
    choices: List[str] = ["yes", "y", "no", "n"]

    while True:
        answer = input(question + " (y/n) ").lower()
        if answer in choices:
            return answer
