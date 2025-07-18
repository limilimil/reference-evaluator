import re
import json

def normalise_str(string):
    return re.sub(r'\s+', " ",
                  re.sub(r'[^\w\s]', "",
                         re.sub(r'[\s][\s]+', " ",
                                re.sub(r'[\-\–—‒‑]', " ", string.lower().strip()))))


def export_json(data, filename):
    with open(f"{filename}.json", "w") as json_file:
        json.dump(data, json_file, default=lambda o: o.encode(), indent=4)
        print(f"Data saved to {filename}.json")
