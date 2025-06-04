import json

OUTPUT_FILE = "data.json"

def format_json():
    with open("data.json", "r", encoding="utf-8") as infile, open("new_data.json", "w", encoding="utf-8") as outfile:
        data = json.load(infile)
        json.dump(data, outfile, indent=4, ensure_ascii=False)

def delete_strings(n: int):
    with open(OUTPUT_FILE, "r", encoding="utf-8") as infile:
        data = json.load(infile)
        del data[:n]

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, indent=4, ensure_ascii=False)

# format_json()
delete_strings(1000)