"""
🛡️ Agentic Honey-Pot API
FastAPI application for the India AI Impact Buildathon.
"""

import time
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, Security, Depends, BackgroundTasks
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import (
    IncomingMessage,
    HoneyPotResponse,
    HealthCheckResponse,
)
from graph import honeypot_graph
from utils.logger import logger, log_security_event
from utils.redis_client import redis_client
from config import settings


# ===================================
# Lifespan Events
# ===================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for startup and shutdown.
    """
    # Startup
    log_security_event(
        logger,
        "SYSTEM",
        "=== AGENTIC HONEY-POT API STARTING ===",
    )
    log_security_event(
        logger,
        "SYSTEM",
        f"Environment: {settings.environment.value}",
        debug=settings.debug,
    )
    log_security_event(
        logger,
        "SYSTEM",
        f"Redis: {settings.redis_host}:{settings.redis_port}",
        connected=redis_client.is_connected(),
    )
    
    yield
    
    # Shutdown
    log_security_event(
        logger,
        "SYSTEM",
        "Shutting down gracefully...",
    )
    redis_client.close()


# ===================================
# FastAPI Application
# ===================================

app = FastAPI(
    title="Agentic Honey-Pot API",
    description="Production-grade scam detection and intelligence extraction system",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware - Allow GUVI hackathon platform
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"  # Allow all origins for hackathon testing
        # In production, you can restrict to:
        # "https://guvi.in",
        # "https://hackathon.guvi.in",
        # "https://*.guvi.in"
    ] if settings.debug else [
        "https://guvi.in",
        "https://hackathon.guvi.in",
        "https://www.guvi.in",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# ===================================
# Security
# ===================================

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Verify API key from request header.
    
    Args:
        api_key: API key from header
        
    Returns:
        API key if valid
        
    Raises:
        HTTPException: If API key is invalid
    """
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Include X-API-Key header.",
        )
    
    if api_key != settings.api_key:
        logger.warning(f"⚠️ Invalid API key attempted: {api_key[:10]}...")
        raise HTTPException(
            status_code=403,
            detail="Invalid API key",
        )
    
    return api_key


# ===================================
# API Endpoints
# ===================================

@app.get("/")
async def root():
    """Root endpoint - GET."""
    return {
        "service": "Agentic Honey-Pot API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "health": "/health",
            "honeypot": "/api/honeypot (POST)",
            "test": "/api/test (GET)"
        }
    }


@app.post("/")
async def root_post(request: IncomingMessage, api_key: str = Depends(verify_api_key)):
    """
    Root endpoint - POST.
    Redirects to honeypot endpoint for GUVI compatibility.
    """
    # Forward to honeypot endpoint
    from fastapi import BackgroundTasks
    background_tasks = BackgroundTasks()
    
    return await honeypot_endpoint(request, background_tasks, api_key)


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status and Redis connectivity
    """
    return HealthCheckResponse(
        status="healthy",
        redis_connected=redis_client.is_connected(),
    )


# OPTIONS handler for CORS preflight
@app.options("/api/honeypot")
async def honeypot_options():
    """Handle CORS preflight requests."""
    return {"message": "OK"}


@app.post("/api/honeypot", response_model=HoneyPotResponse)
async def honeypot_endpoint(
    request: IncomingMessage,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key),
):
    """
    Main honey-pot endpoint for GUVI hackathon (exact format).
    
    Args:
        request: Incoming message from GUVI Mock Scammer API
        background_tasks: FastAPI background tasks
        api_key: Validated API key
        
    Returns:
        Response to send back to scammer
    """
    start_time = time.time()
    
    # Extract session and message
    session_id = request.sessionId
    message_text = request.message.text
    sender = request.message.sender
    
    # Log the raw request for debugging
    logger.info(f"[GUVI] sessionId={session_id}, sender={sender}, msg_len={len(message_text)}")
    
    log_security_event(
        logger,
        "SYSTEM",
        "Incoming GUVI message",
        session_id=session_id,
        sender=sender,
        length=len(message_text),
    )
    
    try:
        # Process message through LangGraph
        response_text, turn_number, is_complete = await honeypot_graph.process_message(
            session_id=session_id,
            sender_id=sender,
            message=message_text,
        )
        
        # Return GUVI format
        response = HoneyPotResponse(
            status="success",
            reply=response_text
        )
        
        engagement_duration = time.time() - start_time
        
        log_security_event(
            logger,
            "SYSTEM",
            "Response generated",
            session_id=session_id,
            turn=turn_number,
            duration_ms=int(engagement_duration * 1000),
            complete=is_complete,
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing GUVI message: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)[:200]}",
        )


@app.get("/api/session/{session_id}")
async def get_session_state(
    session_id: str,
    api_key: str = Depends(verify_api_key),
):
    """
    Retrieve session state (for debugging).
    
    Args:
        session_id: Session identifier
        api_key: Validated API key
        
    Returns:
        Session state from Redis
    """
    state = redis_client.load_state(session_id)
    
    if not state:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found",
        )
    
    return state


@app.delete("/api/session/{session_id}")
async def delete_session(
    session_id: str,
    api_key: str = Depends(verify_api_key),
):
    """
    Delete session state.
    
    Args:
        session_id: Session identifier
        api_key: Validated API key
        
    Returns:
        Deletion confirmation
    """
    success = redis_client.delete_state(session_id)
    
    if success:
        return {"message": f"Session {session_id} deleted"}
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete session",
        )


@app.get("/api/test")
async def test_endpoint():
    """
    Simple test endpoint for GUVI platform verification.
    No authentication required.
    """
    return {
        "status": "ok",
        "message": "Honeypot API is running",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "health": "/health",
            "honeypot": "/api/honeypot (POST)",
            "test": "/api/test (GET)"
        }
    }


@app.post("/api/test-honeypot")
async def test_honeypot_no_auth(request: IncomingMessage):
    """
    Test honeypot endpoint WITHOUT authentication for GUVI debugging.
    Remove this in production!
    """
    logger.info(f"[TEST] Received test request: sessionId={request.sessionId}")
    
    return HoneyPotResponse(
        status="success",
        reply="Test response from honeypot API. Authentication is working!"
    )


# ===================================
# Run Server
# ===================================

if __name__ == "__main__":
    import uvicorn
    
    log_security_event(
        logger,
        "SYSTEM",
        f"Starting server on {settings.api_host}:{settings.server_port}",
    )
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.server_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
