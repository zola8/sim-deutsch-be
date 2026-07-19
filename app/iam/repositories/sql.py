import json

from ..models import UserModel
from ..schema_user_profile import UserProfile


def to_schema(model: UserModel) -> UserProfile:
    return UserProfile(
        user_id=model.user_id,
        username=model.username,
        email=model.email,
        status=model.status,
        created_at=model.created_at.isoformat() if model.created_at else None,
        roles=json.loads(model.roles) if model.roles else []
    )


# TODO what for?
