from typing import Optional

from fastapi import UploadFile
from fastapi_mail import MessageSchema, MessageType
from pydantic import NameEmail


class MailServiceBuilder:
    """This class represents the mail service"""

    def __init__(self) -> None:
        """Initializer for the mail service builder."""
        self._subject: str = ""
        self._recipients: list[NameEmail] = []
        self._cc: list[NameEmail] = []
        self._attachments: list[UploadFile] = []
        self._template_name: Optional[str] = ""
        self._body: Optional[dict] = {}

    def subject(self, *, subject: str) -> "MailServiceBuilder":
        """Builder method for subject.

        Args:
            subject (str): The subject for the mail.

        Returns:
            MailServiceBuilder: The mail service builder class
        """
        self._subject = subject
        return self

    def recipients(self, *, recipients: list[NameEmail]) -> "MailServiceBuilder":
        """Builder method for recipients.

        Args:
            recipients (list[EmailStr]): The recipients for the mail.

        Returns:
            MailServiceBuilder: The mail service builder class
        """
        self._recipients = recipients
        return self

    def cc(self, *, cc: list[NameEmail]) -> "MailServiceBuilder":
        """Builder method for cc.

        Args:
            cc (str): The cc for the mail.

        Returns:
            MailServiceBuilder: The mail service builder class
        """
        self._cc = cc
        return self

    def attachments(self, *, attachments: list[UploadFile]) -> "MailServiceBuilder":
        """Builder method for attachments.

        Args:
            attachments (list[UploadFile]): The attachments for the mail.

        Returns:
            MailServiceBuilder: The mail service builder class
        """
        self._attachments = attachments
        return self

    def template(self, *, template_name: str) -> "MailServiceBuilder":
        """Builder method for template.

        Args:
            template_name (str): The name of the template.

        Returns:
            MailServiceBuilder: The mail service builder class
        """
        self._template_name = template_name
        return self

    def body(self, *, body: dict) -> "MailServiceBuilder":
        """Builder method for subject.

        Args:
            body (dict): The body for the mail.

        Returns:
            MailServiceBuilder: The mail service builder class
        """
        self._body = body
        return self

    async def send_mail(self) -> None:
        """Builder method for subject."""
        message = MessageSchema(
            subject=self._subject,
            recipients=self._recipients,
            cc=self._cc,
            attachments=self._attachments,  # type: ignore
            subtype=MessageType.html,
            template_body=self._body,
        )
        from app.main import fast_mail

        await fast_mail.send_message(message=message, template_name=self._template_name)
