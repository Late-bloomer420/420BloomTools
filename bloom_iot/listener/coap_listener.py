from __future__ import annotations

from typing import Callable

from bloom_iot.listener.base import AbstractSensorListener


class CoAPListener(AbstractSensorListener):
    """CoAP listener — not yet implemented. Install aiocoap and contribute via GitHub."""

    def on_message(self, callback: Callable[[str, str | bytes], None]) -> None:
        raise NotImplementedError(
            "CoAP support is not yet implemented. "
            "See https://github.com/Late-bloomer420/420BloomTools for contribution info."
        )

    def start(self) -> None:
        raise NotImplementedError("CoAP support is not yet implemented.")

    def stop(self) -> None:
        raise NotImplementedError("CoAP support is not yet implemented.")
