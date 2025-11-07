import json
import requests
import pandas as pd

url = "http://127.0.0.1:8000/recommend"


df = pd.read_csv("data/raw/tickets3.csv")
tickets = df.to_dict(orient="records")

for ticket in tickets:
    response = requests.post(url, json=ticket)
    print("Recommended Articles:", json.dumps(response.json(), indent=2))
