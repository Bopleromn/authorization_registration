from pydantic import BaseModel, Field


class UserAdd(BaseModel):
    email: str = Field(max_length=20)
    password: str = Field(max_length=10)
    name: str
    age: int = Field(ge=0)


class User(UserAdd):
    id: int