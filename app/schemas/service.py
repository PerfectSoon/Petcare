from pydantic import BaseModel, Field
from typing import Optional


class ServiceBase(BaseModel):
    name: str
    base_price: float
    duration_min: int

    class Config:
        from_attributes = True


class VeterinaryServiceCreate(ServiceBase):
    animal_type: str
    emergency_available: bool


class GroomingServiceCreate(ServiceBase):
    tools_required: str
    coat_type: str


class SittingServiceCreate(ServiceBase):
    max_pets: int
    overnight_available: bool


class VeterinaryServiceOut(VeterinaryServiceCreate):
    id: int

    class Config:
        from_attributes = True


class GroomingServiceOut(GroomingServiceCreate):
    id: int

    class Config:
        from_attributes = True


class SittingServiceOut(SittingServiceCreate):
    id: int

    class Config:
        from_attributes = True


class ProviderServiceBase(BaseModel):
    custom_price: Optional[float] = None
    custom_duration: Optional[int] = None


class ProviderServiceOut(BaseModel):
    id: int
    provider_id: int
    service_id: int
    custom_price: Optional[float]
    custom_duration: Optional[int]
    service: ServiceBase
    extra_info: Optional[str] = Field(default=None, max_length=200)

    class Config:
        from_attributes = True


class ProviderServiceUpdate(ProviderServiceBase):
    pass
