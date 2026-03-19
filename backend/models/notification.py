from pydantic import BaseModel


class NotificationConfig(BaseModel):
    channel: str  # "email", "telegram", "whatsapp"
    is_active: bool = True
    # Email
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""
    to_email: str = ""
    # Telegram
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    # WhatsApp (via Twilio)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""
    whatsapp_to_number: str = ""


class NotificationResponse(BaseModel):
    id: str
    agent_id: str
    channel: str
    config: dict
    is_active: bool
