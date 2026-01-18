import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_POSTCODE

_LOGGER = logging.getLogger(__name__)

_RESOURCE = (
    "https://www.postcodeloterij.nl/public/rest/drawresults/winnings/NPL/P_MT_P%s/?resultSize=10"
)


# ---------------------------------------------------------
# FETCHER (async wrapper)
# ---------------------------------------------------------

class PostcodeLoterijFetcher:
    """Shared fetcher used by the coordinator."""

    def __init__(self, hass, postcode):
        self.hass = hass
        self.postcode = postcode
        self.data = None

    def _sync_update(self):
        """Synchronous API call executed in executor."""
        moment = datetime.today() - relativedelta(months=1)
        if moment.day < 8:
            moment -= relativedelta(months=1)

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
            _LOGGER.error("Error fetching Postcodeloterij data: %s", ex)
            self.data = None

        return self.data

    async def update_async(self):
        """Async wrapper."""
        return await self.hass.async_add_executor_job(self._sync_update)


# ---------------------------------------------------------
# BASE SENSOR
# ---------------------------------------------------------

class BasePostcodeloterijSensor(CoordinatorEntity, Entity):
    """Base class for all sensors."""

    def __init__(self, coordinator, postcode):
        super().__init__(coordinator)
        self._postcode = postcode

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._postcode)},
            "name": f"Postcodeloterij {self._postcode}",
            "manufacturer": "Postcodeloterij",
            "model": "Winnings API",
        }


# ---------------------------------------------------------
# SENSOR 1: NUMBER OF PRICES WON
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
        data = self.coordinator.data
        return data.get("prizeCount") if data else None


# ---------------------------------------------------------
# SENSOR 2: lIST WITH PRICES WON
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
        data = self.coordinator.data
        if not data:
            return None
        prizes = [p["description"] for p in data.get("wonPrizes", [])]
        return ", ".join(prizes) if prizes else "Geen prijzen"


# ---------------------------------------------------------
# SENSOR 3: PERIOD
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
        data = self.coordinator.data
        return data.get("period") if data else None


# ---------------------------------------------------------
# SETUP ENTRY
# ---------------------------------------------------------

async def async_setup_entry(hass, entry, async_add_entities):
    """Create sensors."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    postcode = data["postcode"]

    sensors = [
        PostcodeloterijPrizeCountSensor(coordinator, postcode),
        PostcodeloterijPrizeListSensor(coordinator, postcode),
        PostcodeloterijPeriodSensor(coordinator, postcode),
    ]

    async_add_entities(sensors)