"""Network port class."""

from .coordinator import LinkEndpoint


class Port:
    """Represents a network port of the switch."""

    def __init__(self, num: int, link_info: LinkEndpoint) -> None:
        """Initialize the network port."""
        self.num = num
        self.link_info = link_info

    @property
    def enabled(self) -> bool:
        """Return if the port is enabled."""
        return self.link_info.enabled[self.num]

    @property
    def name(self) -> bool:
        """Return the port name."""
        return self.link_info.name[self.num]
