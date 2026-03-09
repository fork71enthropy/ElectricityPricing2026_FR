import requests
import logging
from datetime import datetime, timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)

RTE_TOKEN_URL = "https://digital.iservices.rte-france.com/token/oauth/"
RTE_API_URL = "https://digital.iservices.rte-france.com/open_api/market_prices/v1/spot_prices"

CLIENT_ID = "your_client_id_here"
CLIENT_SECRET = "your_client_secret_here"


def get_access_token() -> str:
    """Retrieve OAuth2 access token from RTE API."""
    response = requests.post(
        RTE_TOKEN_URL,
        auth=(CLIENT_ID, CLIENT_SECRET),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    response.raise_for_status()
    return response.json()["access_token"]


def fetch_spot_prices(start_date: datetime, end_date: datetime) -> list[dict]:
    """
    Fetch French spot electricity prices from RTE eCO2mix API.

    Args:
        start_date: Start of the time range (UTC)
        end_date: End of the time range (UTC)

    Returns:
        List of dicts with keys: start_date, end_date, value (EUR/MWh)
    """
    token = get_access_token()

    params = {
        "start_date": start_date.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "end_date": end_date.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
    }

    response = requests.get(
        RTE_API_URL,
        headers={"Authorization": f"Bearer {token}"},
        params=params,
    )
    response.raise_for_status()

    data = response.json()
    return data.get("market_prices", [])


def save_spot_prices(prices: list[dict]) -> int:
    """
    Save fetched prices to the database.
    Skips duplicates based on timestamp.

    Args:
        prices: List of price dicts from the RTE API

    Returns:
        Number of new records saved
    """
    # Import here to avoid issues outside Django context
    from apps.data_collection.models import SpotPrice

    saved = 0
    for entry in prices:
        timestamp = datetime.fromisoformat(entry["start_date"])
        value = entry["value"]

        _, created = SpotPrice.objects.get_or_create(
            timestamp=timestamp,
            defaults={"price_eur_mwh": value},
        )
        if created:
            saved += 1

    return saved


def collect_daily_prices() -> None:
    """
    Main collection task — fetches yesterday's hourly spot prices.
    Intended to be run daily via cron or Celery beat.
    """
    end_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=1)

    logger.info(f"Collecting spot prices from {start_date} to {end_date}")

    try:
        prices = fetch_spot_prices(start_date, end_date)
        saved = save_spot_prices(prices)
        logger.info(f"Saved {saved} new price records")

    except requests.HTTPError as e:
        logger.error(f"RTE API error: {e.response.status_code} — {e.response.text}")
    except Exception as e:
        logger.error(f"Unexpected error during price collection: {e}")
        raise