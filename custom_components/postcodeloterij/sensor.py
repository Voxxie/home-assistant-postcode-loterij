import logging
from datetime import datetime, timedelta
import dateutil.relativedelta
import requests

from homeassistant.helpers.entity import Entity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, CONF_POSTCODE

_LOGGER = logging.getLogger(__name__)

_RESOURCE = (
    "https://www.postcodeloterij.nl/public/rest/drawresults/winnings/NPL/P_MT_P%s/?resultSize=10"
)

SCAN_INTERVAL = timedelta(minutes=30)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up Postcodeloterij sensors from config entry."""
    postcode = entry.data[CONF_POSTCODE]

    # Shared fetcher instance
    fetcher = PostcodeLoterijFetcher(postcode)

    sensors = [
        PostcodeloterijPrizeCountSensor(postcode, fetcher),
        PostcodeloterijPrizeListSensor(postcode, fetcher),
        PostcodeloterijPeriodSensor(postcode, fetcher),
    ]

    # Register sensors so the refresh service can update them
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault("entities", [])
    hass.data[DOMAIN]["entities"].extend(sensors)

    async_add_entities(sensors, True)


# ---------------------------------------------------------
# SHARED FETCHER (1 API CALL VOOR ALLE SENSOREN)
# ---------------------------------------------------------

class PostcodeLoterijFetcher:
    """Shared data fetcher so we only call the API once."""

    def __init__(self, postcode):
        self.postcode = postcode
        self.data = None

    def update(self):
        """Fetch data from the Postcodeloterij API."""
        moment = datetime.today() - dateutil.relativedelta.relativedelta(months=1)
        if moment.day < 8:
            moment -= dateutil.relativedelta.relativedelta(months=1)

        moment_fmt = moment.strftime("%Y%m")
        url = _RESOURCE % moment_fmt

        try:
            req = requests.post(
                url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/112.0.0.0 Safari/537.36"
                    )
                },
                data={"query": self.postcode},
                timeout=10,
            )
            self.data = req.json()
            self.data["period"] = moment.strftime("%m-%Y")

        except Exception as ex:
            _LOGGER.error("Error fetching data: %s", ex)
            self.data = None


# ---------------------------------------------------------
# BASE SENSOR MET DEVICE INFO
# ---------------------------------------------------------

class BasePostcodeloterijSensor(Entity):
    """Base class with shared device info."""

    def __init__(self, postcode, fetcher):
        self._postcode = postcode
        self.fetcher = fetcher

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._postcode)},
            "name": f"Postcodeloterij {self._postcode}",
            "manufacturer": "Postcodeloterij",
            "model": "Winnings API",
        }

    def update(self):
        """Trigger shared fetcher update."""
        self.fetcher.update()


# ---------------------------------------------------------
# SENSOR 1: AANTAL PRIJZEN
# ---------------------------------------------------------

class PostcodeloterijPrizeCountSensor(BasePostcodeloterijSensor):

    @property
    def name(self):
        return f"Postcodeloterij prijs {self._postcode}"

    @property
    def unique_id(self):
        return f"postcodeloterij_{self._postcode}_prizecount"

    @property
    def icon(self):
        return "mdi:trophy"

    @property
    def state(self):
        if not self.fetcher.data:
            return None
        return self.fetcher.data.get("prizeCount")


# ---------------------------------------------------------
# SENSOR 2: LIJST MET PRIJZEN
# ---------------------------------------------------------

class PostcodeloterijPrizeListSensor(BasePostcodeloterijSensor):

    @property
    def name(self):
        return f"Postcodeloterij prijzen {self._postcode}"

    @property
    def unique_id(self):
        return f"postcodeloterij_{self._postcode}_prizelist"

    @property
    def icon(self):
        return "mdi:format-list-bulleted"

    @property
    def state(self):
        if not self.fetcher.data:
            return None
        prizes = [p["description"] for p in self.fetcher.data.get("wonPrizes", [])]
        return ", ".join(prizes) if prizes else "Geen prijzen"


# ---------------------------------------------------------
# SENSOR 3: PERIODE
# ---------------------------------------------------------

class PostcodeloterijPeriodSensor(BasePostcodeloterijSensor):

    @property
    def name(self):
        return f"Postcodeloterij periode {self._postcode}"

    @property
    def unique_id(self):
        return f"postcodeloterij_{self._postcode}_period"

    @property
    def icon(self):
        return "mdi:calendar"

    @property
    def state(self):
        if not self.fetcher.data:
            return None
        return self.fetcher.data.get("period")