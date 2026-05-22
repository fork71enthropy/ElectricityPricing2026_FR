import logging
import os
import django
from datetime import datetime
import sys
from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Energy_Dashboard_France.settings")
django.setup()
from entsoe import EntsoePandasClient
import pandas as pd
from apps.data_collection.models import SpotPrice

logger = logging.getLogger(__name__)

ENTSOE_API_KEY = os.getenv("ENTSOE_API_KEY")


def fetch_prices(start: str, end: str) -> pd.Series:
    """
    Récupère les prix day-ahead depuis ENTSO-E.
    start/end format: 'YYYY-MM-DD'
    """
    client = EntsoePandasClient(api_key=ENTSOE_API_KEY)
    ts_start = pd.Timestamp(start, tz="Europe/Paris")
    ts_end = pd.Timestamp(end, tz="Europe/Paris")
    return client.query_day_ahead_prices("FR", start=ts_start, end=ts_end)


def save_prices(prices: pd.Series) -> int:
    saved = 0
    for timestamp, price in prices.items():
        start_date = timestamp.to_pydatetime()
        end_date = (timestamp + pd.Timedelta("15min")).to_pydatetime()
        _, created = SpotPrice.objects.get_or_create(
            start_date=start_date,
            end_date=end_date,
            defaults={"price_eur_mwh": price, "volume_mw": 0},
        )
        if created:
            saved += 1
    return saved


def collect_day_ahead() -> None:
    """Collecte le day-ahead et le stocke en base."""
    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + pd.Timedelta("1d")).strftime("%Y-%m-%d")
    try:
        prices = fetch_prices(today, tomorrow)
        saved = save_prices(prices)
        logger.info(f"Collecte terminée — {saved} enregistrements")
    except Exception as e:
        logger.error(f"Erreur ENTSO-E: {e}")
        raise


def collect_historical(start: str = "2024-01-01", end: str = None) -> None:
    """Backfill historique depuis ENTSO-E."""
    if end is None:
        end = datetime.now().strftime("%Y-%m-%d")
    try:
        prices = fetch_prices(start, end)
        saved = save_prices(prices)
        logger.info(f"Backfill terminé — {saved} enregistrements")
    except Exception as e:
        logger.error(f"Erreur ENTSO-E: {e}")
        raise



if __name__ == "__main__":
    print("Démarrage du backfill historique...")
    collect_historical()
    print("Terminé")



"""
print("affichage du système : \n")
print(sys.path[0])  # temporaire
"""

