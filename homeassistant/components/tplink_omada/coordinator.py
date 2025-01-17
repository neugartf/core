"""Generic Omada API coordinator."""
from collections.abc import Awaitable, Callable
from datetime import timedelta
import logging
from typing import Generic, TypeVar

import async_timeout
from tplink_omada_client.exceptions import OmadaClientException
from tplink_omada_client.omadaclient import OmadaSiteClient

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

T = TypeVar("T")


class OmadaCoordinator(DataUpdateCoordinator[dict[str, T]], Generic[T]):
    """Coordinator for synchronizing bulk Omada data."""

    def __init__(
        self,
        hass: HomeAssistant,
        omada_client: OmadaSiteClient,
        name: str,
        update_func: Callable[[OmadaSiteClient], Awaitable[dict[str, T]]],
        poll_delay: int = 300,
    ) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"Omada API Data - {name}",
            update_interval=timedelta(seconds=poll_delay),
        )
        self.omada_client = omada_client
        self._update_func = update_func

    async def _async_update_data(self) -> dict[str, T]:
        """Fetch data from API endpoint."""
        try:
            async with async_timeout.timeout(10):
                return await self._update_func(self.omada_client)
        except OmadaClientException as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
