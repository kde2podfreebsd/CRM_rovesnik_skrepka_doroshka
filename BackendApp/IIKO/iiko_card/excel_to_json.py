import json
import os

import pandas
from tqdm import tqdm

if __name__ == "__main__":

    PATH = os.path.dirname(os.path.abspath(__file__))

    print("\nПерекачка данных из excel в json...")
    for file in tqdm(os.listdir(f"{PATH}/card_data/cards_excel")):
        problems_count = 0
        try:
            excel_data_df = pandas.read_excel(f"{PATH}/card_data/cards_excel/{file}", sheet_name="Page 1")
            thisisjson = excel_data_df.to_json(orient="records", force_ascii=False)
            thisisjson_dict = json.loads(thisisjson)
            if not os.path.exists(f"{PATH}/card_data/cards_info.json"):
                with open(f"{PATH}/card_data/cards_info.json", "w") as json_file:
                    json.dump(thisisjson_dict, json_file, ensure_ascii=False)
            else:
                data = json.load(open(f"{PATH}/card_data/cards_info.json"))
                data += thisisjson_dict
                with open(f"{PATH}/card_data/cards_info.json", "w") as json_file:
                    json.dump(data, json_file, ensure_ascii=False)
                os.remove(f"{PATH}/card_data/cards_excel/{file}")
        except Exception as e:
            problems_count += 1
            pass

    print(f"Перегрузка закончена. Кол-во проблем: {problems_count}\n")
