from typing import Dict, Optional, List
from urllib.parse import urlparse

def is_url(url_string: str) -> bool:
    scheme = urlparse(url_string).scheme
    return scheme == "http" or scheme == "https"


def ask_boolean_question(question: str):
    choices: List[str] = ["yes", "y", "no", "n"]

    while True:
        answer = input(question + " (y/n) ").lower()
        if answer in choices:
            return answer