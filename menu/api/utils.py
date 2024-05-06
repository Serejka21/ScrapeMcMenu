import json
from pathlib import Path


def get_json_data() -> dict:
    scraped_data = Path(f"menu/data.json")

    if not scraped_data.exists():
        raise FileNotFoundError

    with scraped_data.open(encoding='utf-8') as file:
        all_data = json.load(file)

    return all_data
