import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("RTE_CLIENT_ID")
CLIENT_SECRET = os.getenv("RTE_CLIENT_SECRET")

TOKEN_URL = "https://digital.iservices.rte-france.com/token/oauth/"
API_URL = "https://digital.iservices.rte-france.com/open_api/wholesale_market/v3/france_power_exchanges"

def save_to_txt(data: dict, filename: str = "data.txt") -> None:
    exchanges = data.get("france_power_exchanges", [])
    values = []
    for exchange in exchanges:
        values.extend(exchange["values"])
    
    values.sort(key=lambda x: x["start_date"])
    
    with open(filename, "w") as f:
        f.write(f"{'Heure début':<30} {'Heure fin':<30} {'Prix (€/MWh)':<15} {'Volume (MW)'}\n")
        f.write("-" * 85 + "\n")
        for v in values:
            f.write(f"{v['start_date']:<30} {v['end_date']:<30} {v['price']:<15} {v['value']}\n")

def get_token():
    response = requests.post(
        TOKEN_URL,
        auth=(CLIENT_ID, CLIENT_SECRET),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    response.raise_for_status()
    return response.json()["access_token"]


def fetch_prices(start: datetime, end: datetime):
    token = get_token()
    params = {
        "start_date": start.strftime("%Y-%m-%dT%H:%M:%S+02:00"),
        "end_date": end.strftime("%Y-%m-%dT%H:%M:%S+02:00"),
    }
    response = requests.get(
        API_URL,
        headers={"Authorization": f"Bearer {token}"},
        params=params,
    )
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    end = datetime.now()
    #start = end - timedelta(days=3)
    start = end - timedelta(days=7)  # 7 jours dans le passé
    data = fetch_prices(start, end)
    save_to_txt(data)
    print(data)



    '''
    2026-04-11 — date (YYYY-MM-DD)
    T — séparateur date/heure
    00:00:00 — heure (HH:MM:SS)
    +02:00 — timezone (heure de Paris, UTC+2 en été)
    '''

    '''
    https://transparency.entsoe.eu/
    Décu par l'api de RTE, je veux des données historiques sur lesquelles je peux vraiment travailler
    '''