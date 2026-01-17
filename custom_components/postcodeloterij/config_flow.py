import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, CONF_POSTCODE

class PostcodeloterijConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Postcodeloterij."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            # Eventueel validatie toevoegen
            return self.async_create_entry(
                title=f"Postcode {user_input[CONF_POSTCODE]}",
                data=user_input
            )

        schema = vol.Schema({
            vol.Required(CONF_POSTCODE): str
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_POSTCODE, default=self.config_entry.data[CONF_POSTCODE]): str
        })

        return self.async_show_form(step_id="init", data_schema=schema)