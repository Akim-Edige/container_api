from app.models import Container
from app.schemas import ContainerRead


def serialize_container(container: Container) -> dict:
    """Serialize a Container ORM model to dict suitable for responses/events."""
    return ContainerRead.from_orm(container).dict()


