"""Support for Vemmio binary sensors."""

from __future__ import annotations

from vemmio import Capability

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import VemmioConfigEntry
from .const import LOGGER
from .coordinator import VemmioDataUpdateCoordinator
from .entity import VemmioEntity, async_setup_attribute_entities_by_capability


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VemmioConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Vemmio switches based on a config entry."""
    coordinator = entry.runtime_data
    LOGGER.debug("Setting up Vemmio binary sensor for host %s", entry.data["host"])

    async_setup_attribute_entities_by_capability(
        hass, entry, async_add_entities, coordinator, VemmioBinarySensor, "openClose"
    )

    async_setup_attribute_entities_by_capability(
        hass,
        entry,
        async_add_entities,
        coordinator,
        VemmioMotionSensor,
        "motionDetector",
    )

    async_setup_attribute_entities_by_capability(
        hass,
        entry,
        async_add_entities,
        coordinator,
        VemmioFloodBinarySensor,
        "floodDetector",
    )


class VemmioBinarySensor(VemmioEntity, BinarySensorEntity):
    """Defines a Vemmio binary sensor."""

    def __init__(
        self,
        coordinator: VemmioDataUpdateCoordinator,
        capability: Capability,
        entities_names: dict,
    ) -> None:
        """Initialize."""

        self._attr_device_class = BinarySensorDeviceClass.DOOR
        LOGGER.debug("Initializing Vemmio binary sensor")
        LOGGER.debug(str(coordinator.data))
        LOGGER.debug("Host: %s", coordinator.vemmio.host)

        super().__init__(
            coordinator=coordinator,
            capability=capability,
            entities_names=entities_names,
        )
        self._attr_unique_id = f"binary_sensor_{capability.get_uuid_with_id()}"
        self._capability = capability
        self._coordinator = coordinator

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return self.coordinator.data.get_input_state(
            self._capability.node_uuid, self._capability.id
        )

    async def async_update(self) -> None:
        """Update entity."""
        await self._coordinator.data.get_status()

    @property
    def should_poll(self) -> bool:
        """Return True if entity has to be polled for state."""
        return True


class VemmioMotionSensor(VemmioEntity, BinarySensorEntity):
    """Defines a Vemmio binary sensor."""

    def __init__(
        self,
        coordinator: VemmioDataUpdateCoordinator,
        capability: Capability,
        entities_names: dict,
    ) -> None:
        """Initialize."""

        self._attr_device_class = BinarySensorDeviceClass.MOTION

        LOGGER.debug("Initializing Vemmio motion sensor")
        LOGGER.debug(str(coordinator.data))
        LOGGER.debug("Host: %s", coordinator.vemmio.host)

        super().__init__(
            coordinator=coordinator,
            capability=capability,
            entities_names=entities_names,
        )
        self._attr_unique_id = f"motion_sensor_{capability.get_uuid_with_id()}"
        self._capability = capability
        self._coordinator = coordinator

    @property
    def is_on(self) -> bool:
        """Return true if the motion sensor is on."""
        return self.coordinator.data.get_motion_status_state()

    async def async_update(self) -> None:
        """Update entity."""
        await self._coordinator.data.get_status()

    @property
    def should_poll(self) -> bool:
        """Return True if entity has to be polled for state."""
        return True


class VemmioFloodBinarySensor(VemmioEntity, BinarySensorEntity):
    """Defines a Vemmio Flood binary sensor."""

    def __init__(
        self,
        coordinator: VemmioDataUpdateCoordinator,
        capability: Capability,
        entities_names: dict,
    ) -> None:
        """Initialize."""

        self._attr_device_class = BinarySensorDeviceClass.MOISTURE

        LOGGER.debug("Initializing Vemmio flood binary sensor")
        LOGGER.debug(str(coordinator.data))
        LOGGER.debug("Host: %s", coordinator.vemmio.host)

        super().__init__(
            coordinator=coordinator,
            capability=capability,
            entities_names=entities_names,
        )
        self._attr_unique_id = f"binary_sensor_{capability.get_uuid_with_id()}"
        self._capability = capability
        self._coordinator = coordinator

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return self.coordinator.data.get_flood_status_state()

    async def async_update(self) -> None:
        """Update entity."""
        await self._coordinator.data.get_status()

    @property
    def should_poll(self) -> bool:
        """Return True if entity has to be polled for state."""
        return True
