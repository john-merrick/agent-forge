import json
import logging
import smtplib
from email.mime.text import MIMEText

import httpx

from backend.database import get_db

logger = logging.getLogger(__name__)


async def send_notifications(agent_id: str, agent_name: str, run_result: dict) -> None:
    """Send agent output to all active notification channels for this agent."""
    db = await get_db()
    rows = await db.execute_fetchall(
        "SELECT * FROM notifications WHERE agent_id = ? AND is_active = 1",
        (agent_id,),
    )
    for row in rows:
        channel = row["channel"]
        config = json.loads(row["config_json"])
        try:
            if channel == "email":
                await _send_email(config, agent_name, run_result)
            elif channel == "telegram":
                await _send_telegram(config, agent_name, run_result)
            elif channel == "whatsapp":
                await _send_whatsapp(config, agent_name, run_result)
            logger.info(f"Notification sent via {channel} for agent {agent_name}")
        except Exception as e:
            logger.error(f"Failed to send {channel} notification for {agent_name}: {e}")


def _format_message(agent_name: str, run_result: dict) -> str:
    status = run_result.get("status", "unknown")
    content = ""
    if run_result.get("output_data"):
        try:
            parsed = json.loads(run_result["output_data"])
            content = parsed.get("content", run_result["output_data"])
        except (json.JSONDecodeError, TypeError):
            content = run_result["output_data"]

    error = run_result.get("error", "")
    tokens = f"{run_result.get('tokens_in', 0)}/{run_result.get('tokens_out', 0)}"
    latency = f"{run_result.get('latency_ms', 0)}ms"

    msg = f"Agent: {agent_name}\nStatus: {status}\nTokens: {tokens} | Latency: {latency}\n"
    if error:
        msg += f"\nError: {error}\n"
    if content:
        # Truncate for SMS-like channels
        if len(content) > 3000:
            content = content[:3000] + "\n... (truncated)"
        msg += f"\n---\n{content}"
    return msg


async def _send_email(config: dict, agent_name: str, run_result: dict) -> None:
    body = _format_message(agent_name, run_result)
    msg = MIMEText(body)
    msg["Subject"] = f"Agent Forge: {agent_name} — {run_result.get('status', 'done')}"
    msg["From"] = config.get("smtp_user", "agentforge@local")
    msg["To"] = config["to_email"]

    with smtplib.SMTP(config.get("smtp_host", "smtp.gmail.com"), config.get("smtp_port", 587)) as server:
        server.starttls()
        if config.get("smtp_user") and config.get("smtp_pass"):
            server.login(config["smtp_user"], config["smtp_pass"])
        server.send_message(msg)


async def _send_telegram(config: dict, agent_name: str, run_result: dict) -> None:
    token = config["telegram_bot_token"]
    chat_id = config["telegram_chat_id"]
    text = _format_message(agent_name, run_result)

    # Telegram has a 4096 char limit
    if len(text) > 4000:
        text = text[:4000] + "\n... (truncated)"

    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
        )


async def _send_whatsapp(config: dict, agent_name: str, run_result: dict) -> None:
    account_sid = config["twilio_account_sid"]
    auth_token = config["twilio_auth_token"]
    from_number = config["twilio_from_number"]
    to_number = config["whatsapp_to_number"]
    text = _format_message(agent_name, run_result)

    # WhatsApp via Twilio has a 1600 char limit
    if len(text) > 1500:
        text = text[:1500] + "\n... (truncated)"

    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(
            f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json",
            auth=(account_sid, auth_token),
            data={
                "From": f"whatsapp:{from_number}",
                "To": f"whatsapp:{to_number}",
                "Body": text,
            },
        )
