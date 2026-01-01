import pandas as pd
import numpy as np
import json
from pathlib import Path

"""
Read the rats csv (from a googledoc) and convert it into the json we
use as our source for the static character info
"""

# Discord,Main Char. Name,Main Char. Spec,Rolled Spec,Role,Challenge Char. Name,,,,,
field_map = {
    "Discord": "discord",
    "Main Char. Name": "main_name",
    "Rolled Spec": "spec",
    "Challenge Char. Name": "name",
}

def main():
    source_csv = Path(Path.cwd() / "data" / "rats.csv")
    data: pd.DataFrame = pd.read_csv(source_csv)
    data = data.iloc[:, :6]  # CSV only has stuff in the first 7 columns
    data = data.rename(columns=field_map)
    data = data.dropna(subset=["name"])
    data = data.replace({np.nan: None})

    print(data)
    with open(Path.cwd() / "data" / "rats.json", "w") as json_file:
        json.dump(
            data.to_dict(
                orient="records",
            ),
            json_file,
            indent=2,
        )

if __name__ == "__main__":
    main()
