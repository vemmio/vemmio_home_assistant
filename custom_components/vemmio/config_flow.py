"""Config flow for the Vemmio integration."""

from __future__ import annotations

import random
from typing import Any

from vemmio import Device, Vemmio, VemmioConnectionError
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_HOST
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

from .const import DOMAIN, LOGGER


class VemmioConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Vemmio."""

    VERSION = 1
    discovered_host: str
    discovered_device: Device
    discovered_device_name: str
    discovered_device_id: Any | None

    def __init__(self) -> None:
        """Initialize."""
        self.discovered_host = ""
        self.discovered_device = None
        self.discovered_device_name = ""
        self.discovered_device_id = None

    async def async_step_user(self, user_input=None) -> ConfigFlowResult:
        """Handle the initial step."""
        if user_input:
            try:
                identifier = str(random.randint(100000, 999999))
            except Exception:  # noqa: BLE001
                pass
            else:
                await self.async_set_unique_id(identifier)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Vemmio",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("host"): str,
                    vol.Required("port", default=1883): int,
                }
            ),
        )

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Handle zeroconf discovery."""
        LOGGER.debug("Zeroconf discovery_info: %s", discovery_info)

        # Read ID field from discovery info
        self.discovered_host = discovery_info.host

        device_name = discovery_info.hostname.removesuffix(".local.")
        LOGGER.debug("Discovered %s ", device_name)

        try:
            self.discovered_device = await self._async_get_device(discovery_info.host)
            LOGGER.debug("Discovered device %s", str(self.discovered_device))
        except VemmioConnectionError:
            return self.async_abort(reason="cannot_connect")

        await self.async_set_unique_id(device_name)
        self._abort_if_unique_id_configured(updates={CONF_HOST: discovery_info.host})

        # Save discovery info for use in setup
        self.context["title_placeholders"] = {"name": device_name}
        self.discovered_device_name = device_name
        self.discovered_device_id = device_name

        return await self.async_step_zeroconf_confirm()

    async def async_step_zeroconf_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initiated by zeroconf."""

        if user_input is not None:
            return self.async_create_entry(
                title=self.discovered_device_name,
                data={
                    CONF_HOST: self.discovered_host,
                    "device_name": self.discovered_device_name,
                    "device_id": self.discovered_device_name,
                },
            )

        self._set_confirm_only()

        return self.async_show_form(
            step_id="zeroconf_confirm",
            description_placeholders={"name": self.discovered_device_name},
        )

    async def _async_get_device(self, host: str) -> Device:
        """Get device information from Vemmio device."""
        session = async_get_clientsession(self.hass)
        vemmio = Vemmio(host, session)
        # If the device doesn't exist, this will create a new one
        return await vemmio.update()


class OptionsVemmioFlow(OptionsFlow):
    """Handle options flow for Vemmio."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required("option_1"): str,
                    vol.Required("option_2", default=1883): int,
                }
            ),
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
