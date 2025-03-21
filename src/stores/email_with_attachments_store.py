from dataclasses import dataclass
from enum import StrEnum
from lib.types import Singleton
from typing import Optional
from lib import event_bus as eb


@dataclass
class EmailState():
    sender_email: Optional[str]
    subject: Optional[str]
    body: Optional[str]
    recipients: list[str]


@dataclass
class AttachmentsState():
    attachments: list[str]


@dataclass
class ValidationState():
    is_valid: bool
    error_messages: list[str]


class ActionEnum(StrEnum):
    SEND = "send"
    SAVE = "save"


class EventNames(StrEnum):
    EDITING_EMAIL_SET = "email_with_attachments_store.editing_email_id#set"
    EMAIL_SET = "email_with_attachments_store.email#set"
    ATTACHMENTS_SET = "email_with_attachments_store.attachments#set"
    VALIDATION_SET = "email_with_attachments_store.validation#set"
    ACTION_SET = "email_with_attachments_store.action#set"

    EDITING_EMAIL_CLEARED = \
        "email_with_attachments_store.editinig_email_id#cleared"
    EMAIL_CLEARED = "email_with_attachments_store.email#cleared"
    ATTACHMENTS_CLEARED = "email_with_attachments_store.attachments#cleared"
    VALIDATION_CLEARED = "email_with_attachments_store.validation#cleared"

    EMAIL_AND_ATTACHMENTS_READY = "email_with_attachments_store#ready"


class EmailWithAttachmentsStore(Singleton):
    # email: Optional[EmailModel]
    # attachments: list[AttachmentModel]
    editing_email_id: Optional[int]
    email_state: Optional[EmailState]
    attachments_state: Optional[AttachmentsState]
    validation_state: ValidationState
    action: ActionEnum
    
    def __init__(self):
        self.editing_email_id = None
        self.email_state = None
        self.attachments_state = None 
        self.validation_state = ValidationState(True, [])
        self.action = ActionEnum.SEND

    def clear_attachments(self):
        self.attachments_state = None
        eb.bus.publish(EventNames.ATTACHMENTS_CLEARED)

    def clear_email(self):
        self.email_state = None
        eb.bus.publish(EventNames.EMAIL_CLEARED)

    def clear_editing_email_id(self):
        self.editing_email_id = None
        eb.bus.publish(EventNames.EDITING_EMAIL_CLEARED)

    def clear_validation(self):
        self.validation_state = ValidationState(True, [])
        eb.bus.publish(EventNames.VALIDATION_CLEARED)

    def clear_store(self):
        self.clear_email()
        self.clear_attachments()
        self.clear_editing_email_id()
        self.clear_validation()

    def set_action(self, action: ActionEnum):
        self.action = action
        eb.bus.publish(EventNames.ACTION_SET, data={
            "action": self.action
        })

    def set_editing_email_id(self, id: int):
        self.editing_email_id = id
        eb.bus.publish(EventNames.EDITING_EMAIL_SET, data={
            "editing_email_id": self.editing_email_id
        })

    def set_attachments(self, attchs: AttachmentsState):
        self.attachments_state = attchs
        eb.bus.publish(EventNames.ATTACHMENTS_SET, data={ 
            "attachments": self.attachments_state 
        })
        self.notify_if_ready()

    def set_email(self, email: EmailState):
        self.email_state = email
        eb.bus.publish(EventNames.EMAIL_SET, data={
            "email": self.email_state
        })
        self.notify_if_ready()

    def set_validation(self, validation: ValidationState):
        self.validation_state = validation
        eb.bus.publish(EventNames.VALIDATION_SET, data={
            "validation": self.validation_state
        })

    def notify_if_ready(self):
        if not self.is_ready():
            return 
         
        eb.bus.publish(EventNames.EMAIL_AND_ATTACHMENTS_READY, data=self.get_content())

    def is_ready(self):
        return self.email_state is not None and self.attachments_state is not None

    def get_content(self):
        return {
            "is_editing_email": self.editing_email_id is not None,
            "editing_email_id": self.editing_email_id,
            "email": self.email_state,
            "attachments": self.attachments_state,
            "validation": self.validation_state,
            "action": self.action,
        }
    
