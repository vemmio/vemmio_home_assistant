"""Base entity for Vemmio."""

from collections.abc import Callable

from vemmio import Capability, DeviceModel

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, LOGGER
from .coordinator import VemmioDataUpdateCoordinator
from . import VemmioConfigEntry


@callback
def async_setup_attribute_entities_by_capability(
    hass: HomeAssistant,
    config_entry: VemmioConfigEntry,
    async_add_entities: AddEntitiesCallback,
    coordinator: VemmioDataUpdateCoordinator,
    entity_class: Callable,
    capability_type: str,
) -> None:
    """Set up Vemmio entities based on device capabilities."""
    entities = []

    LOGGER.debug(
        "[async_setup_attribute_entities_by_capability] Add entities of capability type: %s",
        capability_type,
    )

    device_capabilities = coordinator.data.get_capabilities(capability_type)

    LOGGER.debug(
        "[async_setup_attribute_entities_by_capability] Device capabilities: %s",
        str(device_capabilities),
    )

    for capability in device_capabilities:
        LOGGER.debug(
            "[async_setup_attribute_entities_by_capability] Adding entity for capability: %s",
            str(capability),
        )
        entities.append(
            entity_class(coordinator, capability, config_entry.data["entities_names"])
        )

    async_add_entities(entities, True)


@callback
def async_setup_attribute_entities_switches(
    hass: HomeAssistant,
    config_entry: VemmioConfigEntry,
    async_add_entities: AddEntitiesCallback,
    coordinator: VemmioDataUpdateCoordinator,
    entity_class: Callable,
) -> None:
    """Set up Vemmio switch entities based on device capabilities."""
    entities = []

    device_capabilities = coordinator.data.get_capabilities("switch")

    LOGGER.debug(
        "[async_setup_attribute_entities_switches] Device capabilities: %s",
        str(device_capabilities),
    )

    for capability in device_capabilities:
        LOGGER.debug(
            "[async_setup_attribute_entities_switches] Adding entity for capability: %s",
            str(capability),
        )
        entities.append(
            entity_class(coordinator, capability, config_entry.data["entities_names"])
        )

    async_add_entities(entities, True)


class VemmioEntity(CoordinatorEntity[VemmioDataUpdateCoordinator]):
    """Defines a base Vemmio entity."""

    def __init__(
        self,
        coordinator: VemmioDataUpdateCoordinator,
        capability: Capability,
        entities_names: dict,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._capability = capability
        self._coordinator = coordinator
        coordinator.device.register_status_update_callback(
            self._capability.get_uuid_with_id(), self._handle_status_update
        )
        coordinator.device.enable_websocket()

        if (entities_names is not None) and (
            capability.get_uuid_with_id() in entities_names
        ):
            self._attr_name = entities_names[capability.get_uuid_with_id()]

    @property
    def should_poll(self) -> bool:
        """No polling needed for a Vemmio entity."""
        return False

    @property
    def device_info(self):
        """Return device information about this entity."""

        # Last 3 bytes of mac address

        LOGGER.debug("[VemmioEntity] Getting device info")
        LOGGER.debug(str(self.coordinator))
        LOGGER.debug(str(self.coordinator.data))

        deviceModel: DeviceModel = self.coordinator.data.model

        macId = deviceModel.info.mac.replace(":", "")[-6:]
        device_name = f"VEMMIO-{deviceModel.info.type}-{macId}".upper()

        LOGGER.debug("Device name: %s", device_name)

        return DeviceInfo(
            connections={(CONNECTION_NETWORK_MAC, deviceModel.info.mac)},
            identifiers={(DOMAIN, deviceModel.info.mac)},
            name=device_name,
            manufacturer="Vemmio",
            model=deviceModel.info.type,
            sw_version=deviceModel.info.fw,
            hw_version=deviceModel.info.revision,
            configuration_url=f"http://{self.coordinator.vemmio.host}",
        )

    @callback
    def _handle_status_update(self) -> None:
        """Handle a status update from the websocket."""
        LOGGER.debug(
            f"[VemmioEntity] {self._capability.get_uuid_with_id()}:  Handling status update."
        )

        self.async_write_ha_state()
