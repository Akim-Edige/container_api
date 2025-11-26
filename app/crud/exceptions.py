class ContainerNotFoundError(Exception):
    """Raised when a container does not exist."""


class ZoneNotFoundError(Exception):
    """Raised when a zone does not exist."""


class ZoneOverloadedError(Exception):
    """Raised when the zone capacity would be exceeded."""


class ContainerConflictError(Exception):
    """Raised when container data violates a unique constraint."""


