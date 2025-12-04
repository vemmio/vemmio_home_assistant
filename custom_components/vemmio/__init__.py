"""The Vemmio integration."""

from __future__ import annotations

from typing import Final

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, LOGGER
from .coordinator import VemmioDataUpdateCoordinator

PLATFORMS: Final = [Platform.BINARY_SENSOR, Platform.SENSOR, Platform.SWITCH]

type VemmioConfigEntry = ConfigEntry[VemmioDataUpdateCoordinator]
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Vemmio integration."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: VemmioConfigEntry) -> bool:
    """Set up Vemmio from a config entry."""
    entry.runtime_data = VemmioDataUpdateCoordinator(hass, entry=entry)
    LOGGER.debug("[async_setup_entry] Entry data: %s", str(entry.data))
    LOGGER.debug(
        "[async_setup_entry] Setting up Vemmio for host %s", entry.data["host"]
    )
    LOGGER.debug(
        "[async_setup_entry] Coordinator data: %s", str(entry.runtime_data.data)
    )

    await entry.runtime_data.async_config_entry_first_refresh()

    # Set up all platforms for this device/entry.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: VemmioConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
