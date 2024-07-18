import pandas as pd
import numpy as np
import json


data = pd.read_csv('../data/rats.csv')
data = data.iloc[:, :6] # CSV only hass stuff in the first 7 columns
data = data.replace({np.nan: None})
print(data)
with open('../data/rats.json', 'w') as json_file:
    json.dump(data.to_dict(orient='records', ), json_file, indent=2)