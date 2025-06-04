import json
import os
import random
from typing import Literal

base_path = os.path.dirname(os.path.abspath(__file__))
print(base_path)


def generate_promo_code(
    series: Literal[
        "ProductLow",
        "ProductMiddle",
        "ProductHigh",
        "DiscountLow",
        "DiscountMiddle",
        "DiscountHigh",
        "Partner",
    ],
    json_file=base_path + "/promocodes.json",
):
    # Загрузка данных из JSON файла
    with open(json_file, "r") as f:
        promo_data = json.load(f)

    # Поиск промокодов для данной серии и извлечение их
    for idx in range(len(promo_data)):
        if promo_data[idx]["series"] == series:
            promo_code = promo_data.pop(idx)
            break

    # Проверка, есть ли промокоды для данной серии
    if not promo_code:
        print("Нет доступных промокодов для данной серии.")
        return None

    # # Обновление JSON файла
    # with open(json_file, "w") as f:
    #     json.dump(promo_data, f, indent=4)

    return promo_code["number"]


if __name__ == "__main__":
    series = "ProductLow"
    promo_code = generate_promo_code(series)
    if promo_code:
        print(f"Сгенерированный промокод: {promo_code}")
