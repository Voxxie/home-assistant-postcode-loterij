from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Service registreren
    async def handle_refresh(call):
        # Alle entiteiten opnieuw laten updaten
        for entity in hass.data[DOMAIN].get("entities", []):
            entity.schedule_update_ha_state(True)

    hass.services.async_register(DOMAIN, "refresh", handle_refresh)

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


