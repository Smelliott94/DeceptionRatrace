import pandas as pd
import numpy as np
import json
import libsql
import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")

conn = libsql.connect(database=url, auth_token=auth_token)
print(conn.execute("select * from players").fetchall())

data = pd.read_csv('../data/rats.csv')
data = data.iloc[:, :6] # CSV only has stuff in the first 7 columns
data = data.dropna(subset=['name'])
data = data.replace({np.nan: None})
cols = list(data.columns)
col_names = ", ".join(cols)
placeholders = ", ".join(["?"] * len(cols))
insert_sql = f"INSERT INTO players ({col_names}) VALUES ({placeholders})"

values = [tuple(row) for row in data.itertuples(index=False, name=None)]
conn.executemany(insert_sql, values)
conn.commit()

print(data)
with open('../data/rats.json', 'w') as json_file:
    json.dump(data.to_dict(orient='records', ), json_file, indent=2)