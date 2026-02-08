"""
🛡️ LangGraph State Machine
Orchestrates the multi-turn honey-pot workflow.

State flow: START -> DETECT -> ENGAGE -> EXTRACT -> CALLBACK
"""

from typing import Dict, Any, Literal
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from models.state import HoneyPotState
from models.schemas import CallbackPayload, ExtractedIntelligence
from agents.profiler import ProfilerAgent
from agents.actor import ActorAgent
from agents.auditor import AuditorAgent
from services.callback import callback_service
from utils.logger import logger, log_security_event
from utils.redis_client import redis_client
from config import settings


class HoneyPotGraph:
    """
    LangGraph-based state machine for the honey-pot workflow.
    """
    
    def __init__(self):
        """Initialize the state graph."""
        self.profiler = ProfilerAgent()
        self.actor = ActorAgent()
        self.auditor = AuditorAgent()
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state machine.
        
        Returns:
            Compiled state graph
        """
        # Create the graph
        workflow = StateGraph(HoneyPotState)
        
        # Add nodes
        workflow.add_node("start", self._start_node)
        workflow.add_node("detect", self._detect_node)
        workflow.add_node("engage", self._engage_node)
        workflow.add_node("extract", self._extract_node)
        workflow.add_node("callback", self._callback_node)
        
        # Set entry point
        workflow.set_entry_point("start")
        
        # Add edges
        workflow.add_edge("start", "detect")
        
        # Conditional routing after detection
        workflow.add_conditional_edges(
            "detect",
            self._should_engage,
            {
                "engage": "engage",
                "end": END,
            }
        )
        
        workflow.add_edge("engage", "extract")
        
        # Conditional routing after extraction
        workflow.add_conditional_edges(
            "extract",
            self._should_callback,
            {
                "callback": "callback",
                "end": END,
            }
        )
        
        workflow.add_edge("callback", END)
        
        # Compile graph
        return workflow.compile()
    
    # ===================================
    # State Machine Nodes
    # ===================================
    
    def _start_node(self, state: HoneyPotState) -> HoneyPotState:
        """
        START node: Initialize or load session state.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        session_id = state["session_id"]
        
        log_security_event(
            logger,
            "SYSTEM",
            "=== NEW REQUEST ===",
            session_id=session_id,
        )
        
        # Try to load existing state from Redis
        existing_state = redis_client.load_state(session_id)
        
        if existing_state:
            # Merge with incoming state
            state.update(existing_state)
            log_security_event(
                logger,
                "SYSTEM",
                f"Continuing session (turn {state.get('turn_number', 0) + 1})",
                session_id=session_id,
            )
        else:
            # New session
            state["start_time"] = datetime.utcnow()
            state["turn_number"] = 0
            state["messages"] = []
            state["persona_used"] = settings.default_persona.value
            state["callback_sent"] = False
            state["callback_attempts"] = 0
            
            # Initialize agent completion flags
            state["profiler_complete"] = False
            state["actor_complete"] = False
            state["auditor_complete"] = False
            
            # Initialize extraction arrays
            state["extracted_upi_ids"] = []
            state["extracted_bank_accounts"] = []
            state["extracted_phone_numbers"] = []
            state["extracted_urls"] = []
            state["extracted_emails"] = []
            state["extracted_keywords"] = []
            state["forensic_ledger"] = []
            state["risk_flags"] = []
            
            log_security_event(
                logger,
                "SYSTEM",
                "New session initialized",
                session_id=session_id,
            )
        
        # Increment turn counter
        state["turn_number"] = state.get("turn_number", 0) + 1
        state["last_update_time"] = datetime.utcnow()
        state["current_phase"] = "START"
        
        # Add scammer message to history
        state["messages"].append({
            "role": "scammer",
            "content": state["current_message"],
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        return state
    
    def _detect_node(self, state: HoneyPotState) -> HoneyPotState:
        """
        DETECT node: Run Profiler agent.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        state["current_phase"] = "DETECT"
        state = self.profiler.analyze(state)
        return state
    
    def _engage_node(self, state: HoneyPotState) -> HoneyPotState:
        """
        ENGAGE node: Run Actor agent.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        state["current_phase"] = "ENGAGE"
        state = self.actor.generate_response(state)
        
        # Add actor response to history
        state["messages"].append({
            "role": "agent",
            "content": state["actor_response"],
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        return state
    
    def _extract_node(self, state: HoneyPotState) -> HoneyPotState:
        """
        EXTRACT node: Run Auditor agent.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        state["current_phase"] = "EXTRACT"
        state = self.auditor.extract_intelligence(state)
        
        # Calculate engagement duration
        start_time = state.get("start_time")
        if start_time:
            # Handle both datetime objects and ISO strings from Redis
            if isinstance(start_time, str):
                from dateutil import parser
                start_time = parser.isoparse(start_time)
                state["start_time"] = start_time
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            state["engagement_duration"] = duration
        
        # Save state to Redis after each turn
        redis_client.save_state(state["session_id"], state)
        
        return state
    
    async def _callback_node(self, state: HoneyPotState) -> HoneyPotState:
        """
        CALLBACK node: Send final intelligence to GUVI.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        from models.schemas import ExtractedIntelligenceCallback
        
        state["current_phase"] = "CALLBACK"
        session_id = state["session_id"]
        
        log_security_event(
            logger,
            "CALLBACK",
            "Preparing final intelligence report",
            session_id=session_id,
        )
        
        # Build callback payload with GUVI format
        intelligence = ExtractedIntelligenceCallback(
            bankAccounts=state.get("extracted_bank_accounts", []),
            upiIds=state.get("extracted_upi_ids", []),
            phishingLinks=state.get("extracted_urls", []),
            phoneNumbers=state.get("extracted_phone_numbers", []),
            suspiciousKeywords=state.get("extracted_keywords", [])
        )
        
        # Generate summary
        summary = self.auditor.generate_summary(state)
        
        payload = CallbackPayload(
            sessionId=session_id,
            scamDetected=state.get("scam_probability", 0.0) >= settings.scam_threshold,
            totalMessagesExchanged=state.get("turn_number", 0),
            extractedIntelligence=intelligence,
            agentNotes=summary
        )
        
        # Send callback
        state["callback_attempts"] = state.get("callback_attempts", 0) + 1
        success, error = await callback_service.send_callback(payload, session_id)
        
        state["callback_sent"] = True
        state["callback_success"] = success
        state["callback_error"] = error
        
        # Save final state
        redis_client.save_state(session_id, state)
        
        return state
    
    # ===================================
    # Conditional Edge Functions
    # ===================================
    
    def _should_engage(self, state: HoneyPotState) -> Literal["engage", "end"]:
        """
        Decide whether to engage with the scammer.
        
        Args:
            state: Current state
            
        Returns:
            Next node to execute
        """
        # ALWAYS engage for testing - we want to see the persona responses!
        # In production, you can add back the threshold check
        should_engage = state.get("should_continue", False)
        scam_probability = state.get("scam_probability", 0.0)
        
        log_security_event(
            logger,
            "SYSTEM",
            f"Scam probability: {scam_probability:.2f} | Threshold: {settings.scam_threshold} | Engaging: {should_engage or scam_probability >= 0.3}",
            session_id=state.get("session_id"),
        )
        
        # Lower threshold for testing (0.3 instead of 0.7)
        # This ensures we engage with most messages to test the persona
        if should_engage or scam_probability >= 0.3:
            return "engage"
        else:
            # Even for low-probability messages, give a curious response
            state["actor_response"] = "I don't understand... What is this about?"
            return "end"
    
    def _should_callback(self, state: HoneyPotState) -> Literal["callback", "end"]:
        """
        Decide whether to send callback or continue conversation.
        
        Args:
            state: Current state
            
        Returns:
            Next node to execute
        """
        turn_number = state.get("turn_number", 0)
        
        # Force callback after max turns
        if turn_number >= settings.max_conversation_turns:
            log_security_event(
                logger,
                "SYSTEM",
                f"Max turns reached ({settings.max_conversation_turns}), forcing callback",
                session_id=state["session_id"],
            )
            return "callback"
        
        # Otherwise continue conversation
        return "end"
    
    # ===================================
    # Public API
    # ===================================
    
    async def process_message(
        self,
        session_id: str,
        sender_id: str,
        message: str,
    ) -> tuple[str, int, bool]:
        """
        Process an incoming message through the state machine.
        
        Args:
            session_id: Session identifier
            sender_id: Sender ID
            message: Message content
            
        Returns:
            (response, turn_number, is_complete) tuple
        """
        # Initialize state
        initial_state: HoneyPotState = {
            "session_id": session_id,
            "sender_id": sender_id,
            "current_message": message,
        }
        
        # Run graph
        # Note: LangGraph's async execution requires awaiting
        final_state = await self.graph.ainvoke(initial_state)
        
        response = final_state.get("actor_response", "Okay.")
        turn_number = final_state.get("turn_number", 1)
        is_complete = final_state.get("callback_sent", False)
        
        return response, turn_number, is_complete


# Global graph instance
honeypot_graph = HoneyPotGraph()
