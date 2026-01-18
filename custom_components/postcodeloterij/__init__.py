import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, CONF_POSTCODE
from .sensor import PostcodeLoterijFetcher

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Postcodeloterij integration."""
    postcode = entry.data[CONF_POSTCODE]

    # Shared fetcher
    fetcher = PostcodeLoterijFetcher(hass, postcode)

    async def async_update():
        """Coordinator update logic with dynamic interval switching."""
        data = await fetcher.update_async()

        now = datetime.now()
        expected_period = (now - relativedelta(months=1)).strftime("%m-%Y")
        current_period = data.get("period") if data else None

        # Dynamisch interval
        if current_period != expected_period:
            coordinator.update_interval = timedelta(hours=1)
        else:
            coordinator.update_interval = timedelta(hours=6)

        return data

    # Coordinator
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"postcodeloterij_{postcode}",
        update_method=async_update,
        update_interval=timedelta(hours=1),  # start snel
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "postcode": postcode,
    }

    # Register refresh service
    async def handle_refresh(call: ServiceCall):
        await coordinator.async_request_refresh()

    hass.services.async_register(DOMAIN, "refresh", handle_refresh)

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload integration."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok