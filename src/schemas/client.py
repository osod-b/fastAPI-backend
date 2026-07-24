from pydantic import BaseModel, Field
from validators.clients import NameValidator, EmailValidator, PhoneNumberValidator, MessageValidator, UUIDVal
from uuid import UUID

class ClientSchema(BaseModel):
    full_name: NameValidator
    email: EmailValidator
    message: MessageValidator
    phone_number: PhoneNumberValidator
    # date_created: str = Field(frozen=True)
    # completed: bool = Field(frozen=True, default=False)
    # date_completed: str = Field(frozen=True)
    
    model_config = {
        "from_attributes": True 
    }

#dict of field:value and for loop goes over them and along makes
# validation of allowed field names: message, name, pnum along with values validation

class EditInput(BaseModel):
    field: str
    value: str
    uuid: UUIDVal

class UpdateInput(BaseModel):
    input: str | UUID