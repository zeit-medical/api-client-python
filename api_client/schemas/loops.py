from typing import List
from pydantic import BaseModel

from .pydanticobjectid import PydanticObjectId


class CreateLoop(BaseModel):
    name: str | None
    type: str = "pi4"
    status: str = "created"
