"""
Webhook Server — WhatsApp (Twilio) & Instagram (Meta Graph API)
---------------------------------------------------------------
Endpoints:
  POST /webhook/whatsapp   → Twilio WhatsApp webhook
  POST /webhook/instagram  → Meta Graph API webhook (messages)
  GET  /webhook/instagram  → Meta webhook verification challenge
  GET  /health             → Health check
  POST /chat               → Direct REST endpoint (testing / custom integrations)
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
from urllib.parse import urlencode

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Form, Header, HTTPException, Request, Response
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from .agent import chat, clear_session

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")

META_PAGE_ACCESS_TOKEN = os.getenv("META_PAGE_ACCESS_TOKEN", "")
META_VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "clinica_verify_token")
META_APP_SECRET = os.getenv("META_APP_SECRET", "")

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(title="Clínica Saúde Integral — Agente Virtual", version="1.0.0")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok", "service": "Clínica Saúde Integral Bot"}


# ---------------------------------------------------------------------------
# WhatsApp via Twilio
# ---------------------------------------------------------------------------

def send_whatsapp(to: str, body: str):
    """Send a WhatsApp message via Twilio REST API."""
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
    payload = {"From": TWILIO_WHATSAPP_FROM, "To": to, "Body": body}
    with httpx.Client() as client:
        resp = client.post(
            url,
            data=payload,
            auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
            timeout=10,
        )
    if resp.status_code not in (200, 201):
        logger.error("Twilio error %s: %s", resp.status_code, resp.text)
    return resp


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...),
    ProfileName: str = Form(default=""),
):
    """
    Twilio sends form-encoded POST with From (whatsapp:+5511...) and Body (text).
    We use From as the session_id so each phone number has its own conversation.
    """
    session_id = From  # e.g. "whatsapp:+5511999998888"
    logger.info("WhatsApp [%s]: %s", session_id, Body)

    reply = chat(session_id=session_id, user_message=Body, canal="whatsapp")
    logger.info("Reply → [%s]: %s", session_id, reply[:80])

    send_whatsapp(to=From, body=reply)

    # Twilio expects a TwiML response (can be empty for async sending)
    return Response(
        content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        media_type="application/xml",
    )


# ---------------------------------------------------------------------------
# Instagram via Meta Graph API
# ---------------------------------------------------------------------------

def verify_meta_signature(raw_body: bytes, x_hub_signature: str) -> bool:
    """Validate X-Hub-Signature-256 from Meta."""
    if not META_APP_SECRET:
        return True  # skip in dev if secret not configured
    expected = "sha256=" + hmac.new(
        META_APP_SECRET.encode(), raw_body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, x_hub_signature)


def send_instagram_message(recipient_id: str, text: str):
    """Send a message via Instagram Graph API."""
    url = f"https://graph.facebook.com/v19.0/me/messages"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text},
        "messaging_type": "RESPONSE",
    }
    headers = {"Authorization": f"Bearer {META_PAGE_ACCESS_TOKEN}"}
    with httpx.Client() as client:
        resp = client.post(url, json=payload, headers=headers, timeout=10)
    if resp.status_code != 200:
        logger.error("Meta API error %s: %s", resp.status_code, resp.text)
    return resp


@app.get("/webhook/instagram")
async def instagram_verify(
    hub_mode: str | None = None,
    hub_verify_token: str | None = None,
    hub_challenge: str | None = None,
):
    """Meta sends a GET to verify the webhook endpoint during setup."""
    if hub_mode == "subscribe" and hub_verify_token == META_VERIFY_TOKEN:
        logger.info("Instagram webhook verified.")
        return PlainTextResponse(content=hub_challenge or "")
    raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/webhook/instagram")
async def instagram_webhook(
    request: Request,
    x_hub_signature_256: str = Header(default=""),
):
    """
    Meta sends JSON payloads for Instagram DM events.
    Each sender PSID is used as the session_id.
    """
    raw_body = await request.body()

    if x_hub_signature_256 and not verify_meta_signature(raw_body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    logger.debug("Instagram payload: %s", payload)

    for entry in payload.get("entry", []):
        for messaging in entry.get("messaging", []):
            sender_id = messaging.get("sender", {}).get("id")
            message = messaging.get("message", {})
            text = message.get("text", "")

            if not sender_id or not text:
                continue

            logger.info("Instagram [%s]: %s", sender_id, text)
            reply = chat(session_id=f"ig:{sender_id}", user_message=text, canal="instagram")
            logger.info("Reply → [ig:%s]: %s", sender_id, reply[:80])
            send_instagram_message(recipient_id=sender_id, text=reply)

    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Direct REST endpoint — for testing and custom integrations
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    session_id: str
    message: str
    canal: str = "api"


class ChatResponse(BaseModel):
    session_id: str
    reply: str


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(body: ChatRequest):
    """
    Stateful REST endpoint for testing or integrating custom channels.
    Each unique session_id maintains its own conversation history.
    """
    reply = chat(
        session_id=body.session_id,
        user_message=body.message,
        canal=body.canal,
    )
    return ChatResponse(session_id=body.session_id, reply=reply)


@app.delete("/chat/{session_id}")
async def reset_session(session_id: str):
    """Clear conversation history for a session (e.g., after appointment is done)."""
    clear_session(session_id)
    return {"status": "cleared", "session_id": session_id}
