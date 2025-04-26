import random
import time
from fileinput import filename
from functools import wraps
from typing import List


def is_letter_str(s: str) -> bool:
    for c in s:
        if not c.isalpha():
            return False
    return True


def get_all_english_word(word_size: int) -> List[str]:
    all_word = []
    if word_size == 5:
        filename = "correct5words.csv"
    else:
        filename = "words.csv"

    with open(filename) as f:
        for line in f:
            line = line.rstrip().replace('"', '').lower()
            if len(line) == word_size and is_letter_str(line):
                all_word.append(line)

    return all_word


def measure_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Function '{func.__name__}' took {execution_time:.4f} seconds to execute")
        return result

    return wrapper

