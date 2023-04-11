from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field

from .pydanticobjectid import PydanticObjectId


class CreateUser(BaseModel):
    email: EmailStr
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False
    short_name: str | None = Field(nullable=True)
    full_name: str | None = Field(nullable=True)
    patient_code: str | None = Field(nullable=True)
    site_code: str | None = Field(nullable=True)
    address: Dict[str, Any] | None = Field(nullable=True)
    phone: str | None = Field(nullable=True)
    loops: List[PydanticObjectId] = Field(default=[], nullable=True)
    role: str = Field(nullable=True)
    caregiver: PydanticObjectId | None | str = Field(default=None, nullable=True)
    patients: List[PydanticObjectId] = Field(default=[], nullable=True)
    onboarding_complete: bool = Field(default=False, nullable=True)
    enroller_email: EmailStr | None = Field(nullable=True)
    timezone: str = Field(nullable=False)
    hotspot_id: str | None = Field(nullable=True)
