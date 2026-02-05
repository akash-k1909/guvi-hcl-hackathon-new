"""FastAPI server and routing."""

from datetime import datetime, timezone
import time
from typing import Any, Dict, Optional

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.agent import build_reply
from app.callback import send_guvi_callback
from app.config import (
    API_KEY,
    AUTH_ENABLED,
    ENABLE_NGROK,
    GEMINI_API_KEY,
    MAX_TURNS_BEFORE_CALLBACK,
    MIN_TURNS_BEFORE_CALLBACK,
    NGROK_PORT,
)
from app.identity import create_identity
from app.intel import extract_intelligence, has_actionable_intel, merge_intelligence
from app.models import InputData
from app.scam import classify_scam_type, scam_confirmed, score_scam_intent

SESSIONS: Dict[str, Dict[str, Any]] = {}

app = FastAPI(title="Agentic Honey-Pot API", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> Dict[str, Any]:
    return {
        "status": "ACTIVE",
        "activeSessions": len(SESSIONS),
        "utcTime": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/")
async def root_chat(
    data: InputData,
    background_tasks: BackgroundTasks,
    x_api_key: Optional[str] = Header(None),
) -> Dict[str, Any]:
    return await chat(data, background_tasks, x_api_key)


@app.post("/chat")
async def chat(
    data: InputData,
    background_tasks: BackgroundTasks,
    x_api_key: Optional[str] = Header(None),
) -> Dict[str, Any]:
    if AUTH_ENABLED and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid API Key")

    session_id = data.session_id
    history = data.conversation_history
    current_text = data.message.text
    language = data.metadata.language

    detected_type = classify_scam_type(current_text)

    if session_id not in SESSIONS:
        SESSIONS[session_id] = {
            "identity": create_identity(detected_type),
            "message_count": 0,
            "scam_score": 0,
            "scam_confirmed": False,
            "callback_sent": False,
            "scam_type": detected_type,
            "history": [],
            "total_intelligence": {
                "bankAccounts": [],
                "upiIds": [],
                "phishingLinks": [],
                "phoneNumbers": [],
                "suspiciousKeywords": [],
            },
        }

    session = SESSIONS[session_id]
    if (
        session["scam_type"] == "general"
        and detected_type != "general"
        and session["message_count"] <= 1
    ):
        session["scam_type"] = detected_type
        session["identity"] = create_identity(detected_type)

    session["message_count"] += 1

    if history:
        effective_history = history
    else:
        effective_history = session["history"]

    extracted = extract_intelligence(current_text)
    session["total_intelligence"] = merge_intelligence(
        session["total_intelligence"], extracted
    )

    score = score_scam_intent(current_text, extracted)
    session["scam_score"] += score
    if scam_confirmed(session["scam_score"]) and not session["scam_confirmed"]:
        session["scam_confirmed"] = True
        print(
            f"[AGENT HANDOFF TRIGGERED] session={session_id} type={session['scam_type']}"
        )

    agent_plan = build_reply(
        effective_history,
        current_text,
        session["identity"],
        language,
        session["scam_type"],
    )
    reply = agent_plan["reply"]
    print(f"[AGENT THOUGHT] session={session_id} thought={agent_plan['thought']}")

    updated_history = list(effective_history)
    updated_history.append(
        {
            "sender": data.message.sender,
            "text": data.message.text,
            "timestamp": data.message.timestamp,
        }
    )
    updated_history.append(
        {
            "sender": "user",
            "text": reply,
            "timestamp": int(time.time() * 1000),
        }
    )
    session["history"] = updated_history

    total_messages_exchanged = len(updated_history)

    should_callback = (
        session["scam_confirmed"]
        and not session["callback_sent"]
        and (
            (
                session["message_count"] >= MIN_TURNS_BEFORE_CALLBACK
                and has_actionable_intel(session["total_intelligence"])
            )
            or session["message_count"] >= MAX_TURNS_BEFORE_CALLBACK
        )
    )

    if should_callback:
        agent_notes = (
            f"Scam confirmed. Persona {session['identity']['name']} from {session['identity']['city']}. "
            f"Score {session['scam_score']}."
        )
        background_tasks.add_task(
            send_guvi_callback,
            session_id,
            total_messages_exchanged,
            session["total_intelligence"],
            agent_notes,
        )
        session["callback_sent"] = True

    return {
        "status": "success",
        "reply": reply,
        "scamDetected": session["scam_confirmed"],
        "totalMessagesExchanged": total_messages_exchanged,
        "extractedIntelligence": session["total_intelligence"],
        "agentIdentity": {
            "name": session["identity"]["name"],
            "city": session["identity"]["city"],
        },
    }


@app.on_event("startup")
async def startup_event() -> None:
    if ENABLE_NGROK:
        try:
            from pyngrok import ngrok

            public_url = ngrok.connect(NGROK_PORT, bind_tls=True)
            print(f"NGROK: {public_url}")
        except Exception:
            print("NGROK: failed to start")

    if not GEMINI_API_KEY:
        print("WARNING: GEMINI_API_KEY is not set; fallback replies enabled.")
