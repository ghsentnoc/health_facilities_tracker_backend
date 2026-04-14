from app.core.schemas.base_read_schema import BaseReadSchema
from app.users.schemas.request.user_facility_association import BaseUserFacilityAssociationSchema


class ReadUserFacilityAssociationSchema(BaseReadSchema, BaseUserFacilityAssociationSchema):
    """Schema for reading a user facility association."""

    facility_id: str
    facility_name: str
