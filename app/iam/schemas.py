from pydantic import BaseModel

# TODO no validation

class UserCreateRequest(BaseModel):
    username: str
    email: str


class UserCreateResponse(BaseModel):
    id: str
    username: str
    email: str
