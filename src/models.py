from enum import Enum, StrEnum
from typing import Literal, Optional, Type
from dataclasses import dataclass


class DatabaseModel():
    # static methods wont be added to __annotations__ of derived classes
    @staticmethod
    def get_field_count(model: Type["DatabaseModel"]):
        return len(model.__annotations__)


class EmailStatus(StrEnum):
    SENT = "sent"
    DRAFT = "draft"
    DELETED = "deleted"
    SENT_DRAFT = "sent_draft"

    @classmethod
    def _missing_(cls, value: object):
        if isinstance(value, str):
            try:
                return cls(value)
            except ValueError:
                pass
        raise ValueError(f"Invalid status: {value}. Must be one of {list(cls)}")


@dataclass
class UserModel(DatabaseModel):
    user_id: int
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    created_at: str


@dataclass
class EmailModel(DatabaseModel):
    email_id: int
    sender_id: int
    subject: str 
    body: str 
    status: EmailStatus
    sent_at: str


@dataclass
class EmailRecipientModel(DatabaseModel):
    email_id: int
    recepient_id: int 


@dataclass
class AttachmentModel(DatabaseModel):
    attachment_id: int
    filename: str
    filepath: str 
    data: bytes 
    create_at: str


@dataclass
class EmailAttachmentModel:
    email_id: int
    attachment_id: int


