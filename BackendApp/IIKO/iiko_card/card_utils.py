import dataclasses
import json
import os

path = os.path.dirname(os.path.abspath(__file__))


def pop_card_info() -> dict:
    cards_info = json.load(open(f"{path}/card_data/cards_info.json"))
    card_info = cards_info.pop()
    with open(f"{path}/card_data/cards_info.json", "w") as json_file:
        json.dump(cards_info, json_file, ensure_ascii=False)
    return card_info
