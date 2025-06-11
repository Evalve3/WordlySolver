import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from util import get_all_english_word


def check_word(word):
    try:
        res = requests.get(
            url=f"https://wordfind.org/ajax/find?params%5Bletters%5D={word}&params%5Bdictionary%5D=",
            cookies={
                "XSRF-TOKEN": "eyJpdiI6InFLdjg2M0ZnbFM0Rk9kc1FNYW5BakE9PSIsInZhbHVlIjoiM3Y5QktGQmxkWG1hRC9aY29tM2VPdFN1RU1ZeU9VWEM2dDhUb3RUTEIxOHM4UDQzMjdrcmxwbTk5dzY5VHB6NXJBcTVWa0l5VElQVmlQZ3hXODZhWnp5bVhXYnFNTXY3Y21VOXFrNG9CZkRtbXpxTlZCbEoxWCs4MkZjYUpHYWIiLCJtYWMiOiIyM2JmYzhjOWEyN2MxYTQzYTEzMWIzMjkxYWNkMjYzYTRiNzkwODAxMzMxOTBhYTFlMzBmM2E0ZDlmYzZkMWU5In0%3D",
                "httpswordfindorg_session": "yJpdiI6Im9KVkgyMEhFbTRUOWdZSVpLeStKMEE9PSIsInZhbHVlIjoiMUlHb29vRncrOVY1a3ZxbG9rZ3M3ZWZQcFdlZVh0cFNPOU1nQS9QUmE3UkY0WkIvLzJaV213akFKWDNVa1FNUU1PVFpvU04wTGlOSzJRRC9WeXdJQ29EdUNLM2xGdjBzSzd1cGVzWmYwelJPRHVpaDQycjZpME9RcklpN1ZpOWciLCJtYWMiOiI3ODkwNTUxMTFiNWJhZmJhMjRmMzNiM2YxYWE0OTA3MTI4MjRjZGQ0N2Q2NzZlODRkYWJmMTc2MjQ0Njk3OWQ0In0%3D",
                "hemOytEZ8gyrMsTVEfHX6LErv2KzD4AGyn9W3Mw2": "eyJpdiI6IllTdks1cDMvUWEzNHZaQmhsTG02MUE9PSIsInZhbHVlIjoicUIzYTg1RTRVVGY3dVdUOC9YeUN5MFJFVXVjSU1LTFNzS3N4RWVqRzJqb1dieHA3WDc3SFBQTnVCcUIwenZKcWUzeFpmQmZDbW1KRHBLSU9hdWNRckFiYnh1aXBZTVlTR1NETUxvNENlNlJFQUtSVHQzWUV1NHFtR3VsWUVEM2xGcm5BLzJUb0c4bVJNbzg4bDV6TjJuanJmM3ROMDJHRUUyV3dDUVZkUkxCSkVEUHNGRzkrQ25OVWhlM3Y4N0ZVS1l0UGVpTWtoRWZGbEVHSDdTa2V6OEtWT1dMOEtsa1ZHU2FvNUdpSTVsOVFVVlJqbTR3SHZCTi9qcWROaktmSmk2QTRYR1lNTlZ1K2VFcW9uK0t2SGJJd0puMnJjM2JiaEJycFZmazZqc2kvZm9YVTh2NkM0U0t1MlltVVp1YmlVMEJOY3pSdjhmS1Y2U1dqOFJucU9GNGtPTjlWODdKM0NuT2g1UU9Ncy9ON051QVJtcEtRNGltbmtjUG8xRTI5IiwibWFjIjoiNTdiZWI2ZWQyMTc5ZGNiMDUyMDgxM2E0ZmM4N2E0YTY3NzAwNDIwNWNiOTcyMDJhYzBlMGNiYmM0MDhiNzNhMiJ9",
                "TOKEN": "eyJpdiI6ImtKaWFyZEl3OThpVkx1aWs0dmlBRXc9PSIsInZhbHVlIjoid0pXcW9YUEpEblhsZ0hsWmRVMHNFc2tHcUJUZ1dqWS94MzRsQ21mZ0Q1UE1pcVFncW52T3lYNHFuTWNFL0pROE0veXFJT3FRNjF0cExyWU5CellQaDY5Y1pkK1g5eGZlOTZ6N01RWXpCbjZsam11bU91em9kaEtNekgvMXIvSk4iLCJtYWMiOiI2YzNmOWU2Y2M3MGFlZmE5MGQyN2FhY2E4OGMyZmYzM2QwMGUxZGQ4NDliNTRiYTEyMTQ4Nzc1NzY5OTc1ZWE0In0%3D; httpswordfindorg_session=eyJpdiI6IkhrQndVVHQ1d3VLN2RLeXIwbkRXTWc9PSIsInZhbHVlIjoiTytxK05XWXhnejV3cGZuUDZ0OGJpcDJNMW9vMnN2SVl5dXpPR0lUaGFPUXBpY3Nnejd0dk9YMTNDWE4zNk5rN2Q3aHc0UWNvZExhNS84Q1NHTURmLzBBWHo4ZFV4ZmdiU2NoeEYrRmpiRzZ0Zm5GOUtlL2I3TmhhVzFSREhBUGEiLCJtYWMiOiJmOWZmN2UzZjhiNTYwMTFmNmVhYjMxMTMxMzZkNmI4ODBmYjBiMjRkMzlkYzQxYWQ4MGM0MDJjNjg4MmQwMzk2In0%3D",
            },
            timeout=10
        )
        json_res = res.json()

        if not json_res.get('data', {}).get("total_words"):
            return (word, "incorrect")

        if any(w['word'] == word for s in json_res['data']['sections'] for w in s['words']):
            return (word, "correct")
        else:
            return (word, "incorrect")

    except Exception as e:
        return (word, f"error: {str(e)}")


def process_words(words_list, num_threads=4):
    incorrect_words = []
    correct_words = []
    errors = []

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(check_word, word)
                   for word in words_list]

        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing words"):
            word, result = future.result()
            if result == "correct":
                correct_words.append(word)
            elif result == "incorrect":
                incorrect_words.append(word)
            else:
                errors.append((word, result))

    print("\nDone!")
    return correct_words, incorrect_words, errors


words_to_check = get_all_english_word(5)
correct, incorrect, errors = process_words(words_to_check)

print(f"\nResults: Correct: {len(correct)}, Incorrect: {len(incorrect)}, Errors: {len(errors)}")

with open("correct5words.csv", 'w') as f:
    for word in correct:
        f.write(word)
        f.write("\n")

with open("incorrect5words.csv", 'w') as f:
    for word in incorrect:
        f.write(word)
        f.write("\n")
