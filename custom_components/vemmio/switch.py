"""Support for Vemmio switches."""

from __future__ import annotations

from typing import Any

from vemmio import Capability

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import VemmioConfigEntry
from .const import LOGGER
from .coordinator import VemmioDataUpdateCoordinator
from .entity import VemmioEntity, async_setup_attribute_entities_switches


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VemmioConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Vemmio switches based on a config entry."""
    coordinator = entry.runtime_data
    LOGGER.debug("Setting up Vemmio switch for host %s", entry.data["host"])

    async_setup_attribute_entities_switches(
        hass, entry, async_add_entities, coordinator, VemmioSwitch
    )


class VemmioSwitch(VemmioEntity, SwitchEntity):
    """Defines a Vemmio switch."""

    def __init__(
        self,
        coordinator: VemmioDataUpdateCoordinator,
        capability: Capability,
        entities_names: dict,
    ) -> None:
        """Initialize."""
        LOGGER.debug("Initializing Vemmio switch")
        LOGGER.debug(str(coordinator.data))
        LOGGER.debug("Host: %s", coordinator.vemmio.host)

        super().__init__(
            coordinator=coordinator,
            capability=capability,
            entities_names=entities_names,
        )
        self._attr_unique_id = f"switch_{capability.get_uuid_with_id()}"
        self._capability = capability
        self._coordinator = coordinator

    async def refresh_task(self):
        """Refresh state of the switch."""
        await self._coordinator.data.get_status()

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        LOGGER.debug(
            f"[VemmioSwitch] Checking if switch is on. my ID is {self._capability.get_uuid_with_id()}"
        )

        is_on = self.coordinator.data.get_relay_state(
            self._capability.node_uuid, self._capability.id
        )

        LOGGER.debug(f"[VemmioSwitch] Switch is_on: {is_on}")
        return is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        LOGGER.debug(
            f"[VemmioSwitch] Switch on. my ID is {self._capability.get_uuid_with_id()}"
        )
        await self._coordinator.data.async_turn_on_switch_by_uuid_and_id(
            self._capability.node_uuid, self._capability.id
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        LOGGER.debug(
            f"[VemmioSwitch] Switch off. my ID is {self._capability.get_uuid_with_id()}"
        )
        await self._coordinator.data.async_turn_off_switch_by_uuid_and_id(
            self._capability.node_uuid, self._capability.id
        )
