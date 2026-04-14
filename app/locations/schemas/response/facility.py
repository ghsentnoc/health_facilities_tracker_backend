from app.core.schemas.base_read_schema import BaseReadSchema
from app.locations.schemas.request.facility import BaseFacilitySchema


class ReadFacilitySchema(BaseReadSchema, BaseFacilitySchema):
    """Schema for facility responses."""

    region_id: str
    district_id: str
    region_name: str
    district_name: str
    is_approved: bool
    is_licensed: bool
    contact_numbers: list[str] = []
