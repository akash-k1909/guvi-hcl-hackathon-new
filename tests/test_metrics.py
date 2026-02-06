import time

import pytest
from fastapi.testclient import TestClient

import app.server as server
from app.config import API_KEY


@pytest.fixture(autouse=True)
def clear_sessions():
    server.SESSIONS.clear()


@pytest.fixture
def client():
    return TestClient(server.app)


def _payload(session_id, text, history=None):
    if history is None:
        history = []
    return {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": text,
            "timestamp": int(time.time() * 1000),
        },
        "conversationHistory": history,
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN",
        },
    }


def _headers():
    return {"x-api-key": API_KEY}


def test_scam_detection_accuracy(client):
    payload = _payload(
        "s1",
        "Urgent: account blocked. Send to scammer@upi now.",
    )
    response = client.post("/chat", json=payload, headers=_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["scamDetected"] is True


def test_non_scam_message_not_confirmed(client):
    payload = _payload("s2", "Hi, meeting at 5 pm tomorrow?")
    response = client.post("/chat", json=payload, headers=_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["scamDetected"] is False


def test_intelligence_extraction_quality(client):
    text = (
        "Pay to user@paytm or 9876543210. "
        "Visit https://fake-bank.com and use account 123456789012."
    )
    payload = _payload("s3", text)
    response = client.post("/chat", json=payload, headers=_headers())
    assert response.status_code == 200
    body = response.json()
    intel = body["extractedIntelligence"]
    assert "user@paytm" in intel["upiIds"]
    assert "9876543210" in intel["phoneNumbers"]
    assert "https://fake-bank.com" in intel["phishingLinks"]
    assert "123456789012" in intel["bankAccounts"]


def test_conversation_turns_and_duration(client):
    session_id = "s4"
    history = []

    first = _payload(session_id, "Your account is blocked, reply now.", history)
    response = client.post("/chat", json=first, headers=_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["totalMessagesExchanged"] == 2

    history.append(
        {
            "sender": "scammer",
            "text": first["message"]["text"],
            "timestamp": first["message"]["timestamp"],
        }
    )
    history.append(
        {"sender": "user", "text": body["reply"], "timestamp": int(time.time() * 1000)}
    )

    second = _payload(session_id, "Send UPI to unblock: scammer@upi", history)
    response = client.post("/chat", json=second, headers=_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["totalMessagesExchanged"] == len(history) + 2


def test_callback_triggered_after_threshold(client, monkeypatch):
    calls = []

    def _fake_callback(session_id, total_messages, intelligence, agent_notes):
        calls.append(
            {
                "session_id": session_id,
                "total_messages": total_messages,
                "intel": intelligence,
                "notes": agent_notes,
            }
        )

    monkeypatch.setattr(server, "send_guvi_callback", _fake_callback)

    session_id = "s5"
    history = []

    for i in range(3):
        payload = _payload(session_id, f"Pay to scammer@upi now {i}", history)
        response = client.post("/chat", json=payload, headers=_headers())
        assert response.status_code == 200
        body = response.json()
        history.append(
            {
                "sender": "scammer",
                "text": payload["message"]["text"],
                "timestamp": payload["message"]["timestamp"],
            }
        )
        history.append(
            {
                "sender": "user",
                "text": body["reply"],
                "timestamp": int(time.time() * 1000),
            }
        )

    assert len(calls) == 1
    assert calls[0]["session_id"] == session_id


def test_server_stores_history_without_client_history(client):
    session_id = "s6"

    first = _payload(session_id, "Your account will be blocked today.")
    response = client.post("/chat", json=first, headers=_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["totalMessagesExchanged"] == 2

    second = _payload(session_id, "Send UPI to avoid suspension.")
    response = client.post("/chat", json=second, headers=_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["totalMessagesExchanged"] == 4

    assert len(server.SESSIONS[session_id]["history"]) == 4
