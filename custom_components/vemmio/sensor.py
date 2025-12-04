"""Support for Vemmio sensors."""

from __future__ import annotations

from vemmio import Capability

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import UnitOfTemperature
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
    """Set up Vemmio sensors based on a config entry."""
    coordinator = entry.runtime_data
    LOGGER.debug("Setting up Vemmio sensors for host %s", entry.data["host"])

    async_setup_attribute_entities_by_capability(
        hass, async_add_entities, coordinator, VemmioTemperatureSensor, "temperature"
    )
    async_setup_attribute_entities_by_capability(
        hass, async_add_entities, coordinator, VemmioIlluminationSensor, "illumination"
    )


class VemmioTemperatureSensor(VemmioEntity, SensorEntity):
    """Defines a Vemmio Temperature sensor."""

    def __init__(
        self, coordinator: VemmioDataUpdateCoordinator, capability: Capability
    ) -> None:
        """Initialize."""
        LOGGER.debug("Initializing Vemmio temperature sensor")
        LOGGER.debug(str(coordinator.data))
        LOGGER.debug("Host: %s", coordinator.vemmio.host)

        super().__init__(coordinator=coordinator, capability=capability)
        self._attr_unique_id = f"temperature_sensor_{capability.get_uuid_with_id()}"
        self._coordinator = coordinator
        self._capability = capability
        self.update_measurement_unit()
        self._attr_native_value = None
        self._attr_icon = "mdi:thermometer"
        self._attr_device_class = SensorDeviceClass.TEMPERATURE

    @property
    def native_value(self) -> float | None:
        """Return the state of the temperature sensor."""
        return self.coordinator.data.get_temperature_status_value()

    async def refresh_task(self):
        """Refresh state of the temperature sensor."""
        await self._coordinator.data.get_status()
        self.update_measurement_unit()

    def update_measurement_unit(self):
        """Update the measurement unit based on device-reported units."""
        device_reported_unit = self.coordinator.data.get_temperature_status_units()
        if device_reported_unit == "C":
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        else:
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS


class VemmioIlluminationSensor(VemmioEntity, SensorEntity):
    """Defines a Vemmio Temperature sensor."""

    _capability: Capability
    _coordinator: VemmioDataUpdateCoordinator

    def __init__(
        self, coordinator: VemmioDataUpdateCoordinator, capability: Capability
    ) -> None:
        """Initialize."""
        LOGGER.debug("Initializing Vemmio illumination sensor")
        LOGGER.debug(str(coordinator.data))
        LOGGER.debug("Host: %s", coordinator.vemmio.host)

        super().__init__(coordinator=coordinator, capability=capability)
        self._attr_unique_id = f"illumination_sensor_{capability.get_uuid_with_id()}"
        self._coordinator = coordinator
        # self.update_measurement_unit()
        self._attr_native_value = None
        self._attr_icon = "mdi:brightness-5"
        self._attr_device_class = SensorDeviceClass.ILLUMINANCE

    @property
    def native_value(self) -> float | None:
        """Return the state of the temperature sensor."""
        return self.coordinator.data.get_illumination_status_value()

    async def refresh_task(self):
        """Refresh state of the temperature sensor."""
        await self._coordinator.data.get_status()
        self.update_measurement_unit()

    def update_measurement_unit(self):
        """Update the measurement unit based on device-reported units."""
        self._attr_native_unit_of_measurement = (
            self.coordinator.data.get_illumination_status_units()
        )
