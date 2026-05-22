import os
from dotenv import load_dotenv
from entsoe import EntsoePandasClient
import pandas as pd

load_dotenv()

client = EntsoePandasClient(api_key=os.getenv("ENTSOE_API_KEY"))
start = pd.Timestamp("2026-01-01",tz="Europe/Paris")
end = pd.Timestamp("2026-01-08",tz="Europe/Paris")

prices = client.query_day_ahead_prices("FR",start=start, end=end)
print(prices)




































