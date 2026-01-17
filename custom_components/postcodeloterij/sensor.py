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

ATTR_PRIZES = "prizes"
ATTR_PERIOD = "period"

SCAN_INTERVAL = timedelta(minutes=30)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up sensor from config entry."""
    postcode = entry.data[CONF_POSTCODE]
    sensor = PostcodeloterijSensor(postcode)
    async_add_entities([sensor], True)


class PostcodeloterijSensor(Entity):
    """Representation of the Postcodeloterij sensor."""

    def __init__(self, postcode):
        self._name = "Postcodeloterij prijs"
        self._state = None
        self._postcode = postcode
        self._icon = "mdi:trophy"
        self._prizes = None
        self._period = None

    @property
    def unique_id(self):
        """Return a unique ID for this sensor."""
        return f"postcodeloterij_{self._postcode}"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return self._icon

    @property
    def extra_state_attributes(self):
        return {
            ATTR_PRIZES: self._prizes,
            ATTR_PERIOD: self._period,
        }

    def update(self):
        """Fetch data from Postcodeloterij API."""

        _LOGGER.debug('Fetching data for postcode "%s"', self._postcode)

        # Determine correct month
        moment = datetime.today() - dateutil.relativedelta.relativedelta(months=1)
        #if moment.day < 8:
        #    moment -= dateutil.relativedelta.relativedelta(months=1)

        moment_fmt = moment.strftime("%Y%m")
        _LOGGER.debug("Selected moment: %s", moment_fmt)

        url = _RESOURCE % moment_fmt
        payload = {"query": self._postcode}

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
                data=payload,
                timeout=10,
            )

            data = req.json()
            _LOGGER.debug("API response: %s", data)

            self._state = data.get("prizeCount", 0)

            prizes = [p["description"] for p in data.get("wonPrizes", [])]
            self._prizes = ", ".join(prizes) if prizes else "Geen prijzen"

            self._period = moment.strftime("%m-%Y")

        except Exception as ex:
            _LOGGER.error("Error fetching data from %s: %s", url, ex)
            self._state = None
            self._prizes = None
            self._period = None