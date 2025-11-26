from fastapi import Request

from app.events import ContainerEventManager


def get_event_manager(request: Request) -> ContainerEventManager:
    """Return the shared container event manager instance."""
    manager = getattr(request.app.state, "event_manager", None)
    if manager is None:
        manager = ContainerEventManager()
        request.app.state.event_manager = manager
    return manager


