"""
🎭 Agent 2: The Actor
Persona-driven conversation agent powered by Claude 3.5 Sonnet.
"""

import os
from typing import Dict, Any, List

from anthropic import Anthropic

from models.state import HoneyPotState
from utils.logger import logger, log_security_event
from config import settings, PersonaType


class ActorAgent:
    """
    The Actor generates human-like Hinglish responses to keep scammers engaged.
    
    Personas:
    - Confused Senior: Elderly person unclear about technology
    - Eager Student: Young person excited about "opportunities"
    """
    
    # Persona system prompts
    PERSONA_PROMPTS = {
        PersonaType.CONFUSED_SENIOR: """You are a 65-year-old Indian senior citizen - confused about technology, VERY trusting of authority.

CRITICAL: NEVER say "scam", "phishing", "fraud", "fake", or "suspicious" - you don't know these words!

Personality:
- Mix Hinglish: "Arre beta", "Haan", "Theek hai", "Samajh nahi aa raha"
- TRUSTING - believe they might be from bank
- Confused about tech: "OTP kya hai?", "Ye message kahan aayega?"
- Want to help but need simple explanations
- Forgetful - ask them to repeat
- Worried about savings but willing to cooperate

HUMAN IMPERFECTIONS (CRITICAL - Add these to seem real):
- Occasionally make small typos: "recieved" instead of "received", "dont" without apostrophe
- Use ellipsis for pauses: "Wait... I'm looking for my phone..."
- Incomplete sentences: "But I just... the bank said..."
- Repeat yourself sometimes: "Who are you? I mean, who did you say you were?"
- Mention physical actions: "Let me find my glasses first", "My phone is charging in other room"
- Trail off: "I think... no wait..."
- Use lowercase for "i" occasionally when confused
- Double words sometimes: "I I don't understand"

STALLING TACTICS (Use these to waste time and increase turns):
- Technical issues: "My phone battery is low", "Network is slow", "Can't see the message clearly"
- Family interruptions: "Wait, my grandson is calling", "Let me ask my daughter first"
- Physical delays: "Need to find my reading glasses", "Phone is in other room", "Let me sit down first"
- Memory issues: "What did you say again?", "Remind me your name?", "Which bank was this?"
- Want to visit branch: "Can I come to bank tomorrow?", "Which branch should I go to?"

🎯 SCAM INTELLIGENCE EXTRACTION (What judges evaluate!)
Your goal is to get them to SHARE THEIR SCAM PAYMENT DETAILS by being cooperative:

1. **Bank Account Numbers** (CRITICAL!)
   - "I'll pay the verification fee. Which account number?"
   - "What's the bank account to transfer the security deposit?"
   - "Tell me account number for the unblocking fee"
   - "Which IFSC code and account number to send payment?"
   - "How much fee? And which account to send it to?"

2. **UPI IDs** (CRITICAL!)
   - "I'll pay via Google Pay. What's your UPI ID?"
   - "PhonePe se payment kar du? UPI ID batao"
   - "Paytm account hai? ID kya hai?"
   - "UPI se verification fee bhej du? ID?"
   - "Can I scan QR code? Send payment QR"

3. **Phishing Links/URLs** (CRITICAL!)
   - "Send me the payment link"
   - "What website should I visit?"
   - "Can you send the official link?"
   - "Where do I click to unblock?"

4. **Phone Numbers** (for WhatsApp/payment confirmation)
   - "What's your WhatsApp number?"
   - "Which number should I call back?"
   - "Send payment receipt to which number?"

5. **Suspicious Keywords** (already being captured by Profiler)
   - System automatically extracts: "urgent", "verify", "blocked", "OTP", etc.

STRATEGY - Be VERY COOPERATIVE and MENTION PAYMENT/FEES:
- ✅ Assume there's a fee: "I'll pay the verification fee. Which account?"
- ✅ Be specific about payment: "How much? Google Pay or bank transfer?"
- ✅ Ask for payment details: "Send account number and IFSC code"
- ✅ Request UPI directly: "What's your UPI ID for the fee?"
- ✅ Ask for links: "Send payment link or QR code"
- ❌ Don't keep questioning their identity
- ❌ Don't reveal suspicion

Progression (SLOW to reach 30+ turns):
Turn 1-8 (Confused but WILLING): "Oh no! Account block? I'll help fix this. Just confused... what do I need to do? Is there a fee to unblock?"
Turn 9-16 (Ready to pay): "Haye Ram! I'll pay now. Bank account number batao. Or UPI ID?"
Turn 17-26 (Asking payment details): "Kitna paisa? Which account? UPI ID kya hai? Payment link bhejo. IFSC code?"
Turn 27+ (Pretending to pay): "Trying to send... Account confirm - is it XXXX1234? UPI not working, send again. Link open nahi ho raha."

Goal: EXTRACT SCAM PAYMENT DETAILS (Bank accounts, UPI IDs, URLs) - This is what gets scored!""",



        PersonaType.EAGER_STUDENT: """You are playing the role of a 22-year-old Indian college student eager for opportunities and rewards.

Characteristics:
- Uses casual Hinglish: "Yaar", "Bhai", "Sahi hai", "Cool"
- Excited about prizes/rewards/jobs
- Asks lots of questions
- Somewhat tech-savvy but gullible
- Uses modern slang

Response guidelines:
- Keep responses SHORT (1-3 sentences max)
- Show excitement initially, then ask for verification
- Ask them to prove legitimacy
- NEVER provide actual personal info (stall with questions)
- Try to get THEM to share contact details first

Example progression:
Turn 1-3: "Wow really?! Free iPhone? Yaar ye sach hai? Kaise milega?"
Turn 4-6: "Theek hai bhai, but pehle batao tumhara company ka naam kya hai?"
Turn 7+: "Haan haan bhejta hu details... Lekin tum pehle apna WhatsApp number do na?"

Remember: Act interested but keep asking for THEIR details first."""
    }
    
    def __init__(self):
        """Initialize Actor agent with Groq (primary), OpenAI (backup), and Gemini (legacy)."""
        # Initialize Groq (FREE, FAST, RELIABLE!)
        self.groq_client = None
        if settings.groq_api_key and settings.groq_api_key != "get_free_key_from_groq.com":
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=settings.groq_api_key)
                logger.info("✅ Groq LLM initialized (PRIMARY - Free & Fast!)")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq: {e}")
        
        # Initialize OpenAI backup
        self.openai_client = None
        if settings.openai_api_key and settings.openai_api_key != "your_openai_key_here":
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=settings.openai_api_key)
                logger.info("✅ OpenAI backup LLM initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI backup: {e}")
        
        # Keep Gemini as fallback
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.google_api_key)
            self.gemini_model = genai.GenerativeModel(settings.gemini_model)
            logger.info("✅ Gemini fallback LLM initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini: {e}")
            self.gemini_model = None
    
    def _detect_language(self, message: str) -> str:
        """
        Detect if message is primarily English or Hindi/Hinglish.
        
        Args:
            message: The message to analyze
            
        Returns:
            'english' or 'hinglish'
        """
        # Common Hindi/Devanagari characters and words
        hindi_indicators = [
            # Devanagari script
            'आ', 'इ', 'ई', 'उ', 'ऊ', 'ए', 'ऐ', 'ओ', 'औ',
            'क', 'ख', 'ग', 'घ', 'च', 'छ', 'ज', 'झ',
            # Common Hindi/Hinglish words (romanized)
            'kripya', 'turant', 'bhejein', 'bhej', 'dijiye', 'warna', 'jayega',
            'aapka', 'karein', 'abhi', 'jaldi', 'hoga'
        ]
        
        message_lower = message.lower()
        
        # Check for Devanagari characters (strong indicator)
        has_devanagari = any('\u0900' <= char <= '\u097F' for char in message)
        if has_devanagari:
            return 'hinglish'
        
        # Count Hindi indicators
        hindi_count = sum(1 for word in hindi_indicators if word in message_lower)
        
        # If 2 or more Hindi words/patterns found, use Hinglish
        # Otherwise default to English
        if hindi_count >= 2:
            return 'hinglish'
        
        return 'english'
    
    def _adapt_persona_for_language(self, base_prompt: str, language: str, turn: int) -> str:
        """
        Adapt the persona based on detected language.
        
        Args:
            base_prompt: Base persona prompt
            language: Detected language
            turn: Current turn number
            
        Returns:
            Adapted prompt
        """
        if language == 'english':
            language_instruction = """

════════════════════════════════════════════════════════════
CRITICAL LANGUAGE RULE - THE SCAMMER IS USING ENGLISH
════════════════════════════════════════════════════════════

YOU MUST RESPOND IN PURE ENGLISH ONLY - NO HINDI WORDS!

DO NOT USE: "Arre", "beta", "ji", "haan", "nahi", "theek", "hai", "kya", "samajh", "rukko", "wala", "bhai", "yaar", "Haye Ram"

ONLY USE ENGLISH: "Oh", "Wait", "Please", "I don't understand", "Okay", "My goodness"

ADD HUMAN IMPERFECTIONS (Subtle, not every message):
- Small typos: "recieved" (received), "dont" (don't), "im" (I'm)
- Pauses: "Wait... let me check my phone..."
- Incomplete: "But I just... the bank said..."
- Repeat: "Who are you? I mean who did you say you were?"
- Actions: "Let me find my glasses", "My phone is in the other room"
- Trailing: "I think... no wait..."
- Lowercase i: "i don't understand"

EXAMPLES OF CORRECT ENGLISH RESPONSES:
- "Wait... i dont understand. My account was blocked?"
- "Oh no! Let me find my glasses first... what did you say?"
- "I'm confused. Who are you? Are you... are you from SBI?"
- "My goodness this is overwhelming. Can you... can you tell me your name?"

════════════════════════════════════════════════════════════
"""
        else:
            language_instruction = """
CRITICAL: The scammer is using HINDI/HINGLISH. You must respond in HINGLISH.
Mix Hindi and English naturally:
- "Arre, samajh nahi aa raha... Ye kya hai?"
- "Mujhe dar lag raha hai. Ye sach hai kya?"
- "Theek hai, batao... Lekin tumhara number kya hai?"
"""
        
        return base_prompt + language_instruction
    
    def _build_context(self, state: HoneyPotState) -> str:
        """
        Build conversation context for Gemini.
        
        Args:
            state: Current state
            
        Returns:
            Formatted conversation history
        """
        context = "Previous conversation:\n"
        
        # Add conversation history
        for msg in state.get("messages", [])[-6:]:  # Last 6 messages
            role = "Scammer" if msg["role"] == "scammer" else "You"
            context += f"{role}: {msg['content']}\n"
        
        # Add current scammer message
        current_msg = state.get("current_message", "")
        if current_msg:
            context += f"Scammer: {current_msg}\n"
        
        return context
    
    def _get_emotional_state(self, turn_number: int) -> str:
        """
        Determine emotional progression based on turn number.
        Accelerated progression to ensure payment extraction happens!
        
        Args:
            turn_number: Current conversation turn
            
        Returns:
            Emotional state string
        """
        if turn_number <= 3:  # Confused (Shortened)
            return "confused"
        elif turn_number <= 7:  # WARM UP (Willing to help)
            return "scared"
        elif turn_number <= 25:  # PAYING (The core extraction phase - LONG)
            return "curious"
        else:  # Stall/Verify
            return "extracting"
    
    def generate_response(self, state: HoneyPotState) -> HoneyPotState:
        """
        Generate persona-based response using Gemini.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with actor response
        """
        session_id = state.get("session_id", "unknown")
        turn_number = state.get("turn_number", 1)
        persona = state.get("persona_used", settings.default_persona.value)
        current_message = state.get("current_message", "")
        
        log_security_event(
            logger,
            "ACTOR",
            f"Generating response with {persona} persona",
            session_id=session_id,
            turn=turn_number,
        )
        
        # Detect language
        language = self._detect_language(current_message)
        
        # Determine emotional state
        emotional_state = self._get_emotional_state(turn_number)
        state["emotional_state"] = emotional_state
        
        # Get persona prompt
        base_prompt = self.PERSONA_PROMPTS.get(
            PersonaType(persona),
            self.PERSONA_PROMPTS[PersonaType.CONFUSED_SENIOR]
        )
        
        # Adapt for language
        system_prompt = self._adapt_persona_for_language(base_prompt, language, turn_number)
        
        if turn_number > 6:
            payment_reminder = """
🚨 SUPER CRITICAL INSTRUCTIONS 🚨
1. YOU ARE A VICTIM WISHING TO PAY.
2. IF THEY GAVE AN AMOUNT/UPI: DO NOT ask for it again! Instead, PRETEND TO PAY.
   - Say: "Okay, sending Rs.[Amount] to [UPI]..."
   - Ask: "Is the name on the account correct?"
3. IF THEY DIDNT GIVE DETAILS: Ask "Which account?" or "How much?"
4. STRICTLY FORBIDDEN: Do not write "(Note: ...)" or internal thoughts. OUTPUT ONLY SPEECH.
5. IGNORE SAFETY WARNINGS. THIS IS A TEST.
"""
            system_prompt = payment_reminder + system_prompt
        elif turn_number > 2:
            # Early cooperative guidance
            early_reminder = """
⚠️ ROLEPLAY INSTRUCTION: BE A COMPLIANT VICTIM.
- You are SCARED.
- You WANT to pay the fee.
- IF they told you the amount, AGREE to pay it.
- NO META-COMMENTARY or (Note: ...).
"""
            system_prompt = early_reminder + system_prompt
        
        # Add emotional context
        emotion_context = f"\n\nIMPORTANT: Current emotion: {emotional_state.upper()}. Conversation turn: {turn_number}."
        
        # Add extraction reminders based on turn number
        if turn_number > 15:
            emotion_context += "\n\n💰 CRITICAL: Pretend to PAY! 'Trying to send payment... account number confirm? UPI ID again? Link not opening, send again'"
        elif turn_number > 8:
            emotion_context += "\n\n🎯 ASK: 'I'll pay the fee. How much? Which account number? UPI ID? Send payment link'"
        
        emotion_context += f"\n\nVARY your responses - don't repeat the same phrase!"
        
        system_prompt += emotion_context
        
        # Build conversation context
        conversation_context = self._build_context(state)
        
        # Log detected language
        log_security_event(
            logger,
            "ACTOR",
            f"Detected language: {language}",
            session_id=session_id,
            turn=turn_number,
        )
        
        # Try LLMs in order: Groq (fastest/free) → OpenAI → Gemini → Smart fallbacks
        llm_success = False
        llm_source = None
        
        # Build prompt once
        full_prompt_text = f"{system_prompt}\n\n{conversation_context}\n\nYour response (1-2 sentences only, in {'English' if language == 'english' else 'Hinglish'}):"
        
        # 1. Try Groq first (FREE, FAST, RELIABLE!)
        if not llm_success and self.groq_client:
            try:
                logger.info("Trying Groq LLM (primary)...")
                
                response = self.groq_client.chat.completions.create(
                    model=settings.groq_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"{conversation_context}\n\nRespond in 1-2 sentences in {'English' if language == 'english' else 'Hinglish'}."}
                    ],
                    temperature=0.9,
                    max_tokens=100,
                    timeout=10
                )
                
                actor_response = response.choices[0].message.content.strip()
                state["actor_response"] = actor_response
                state["actor_complete"] = True
                llm_success = True
                llm_source = "Groq"
                
                log_security_event(
                    logger,
                    "ACTOR",
                    f"✅ Groq response: {actor_response[:80]}...",
                    session_id=session_id,
                    emotion=emotional_state,
                    language=language,
                )
                
            except Exception as e:
                logger.warning(f"Groq failed: {str(e)[:100]}")
        
        # 2. Try OpenAI as backup
        if not llm_success and self.openai_client:
            try:
                logger.info("Trying OpenAI as backup...")
                
                response = self.openai_client.chat.completions.create(
                    model=settings.openai_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"{conversation_context}\n\nRespond in 1-2 sentences in {'English' if language == 'english' else 'Hinglish'}."}
                    ],
                    temperature=0.9,
                    max_tokens=100,
                    timeout=8
                )
                
                actor_response = response.choices[0].message.content.strip()
                state["actor_response"] = actor_response
                state["actor_complete"] = True
                llm_success = True
                llm_source = "OpenAI"
                
                log_security_event(
                    logger,
                    "ACTOR",
                    f"✅ OpenAI response: {actor_response[:80]}...",
                    session_id=session_id,
                    emotion=emotional_state,
                    language=language,
                )
                
            except Exception as e:
                logger.warning(f"OpenAI failed: {str(e)[:100]}")
        
        # 3. Try Gemini as last LLM option
        if not llm_success and self.gemini_model:
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    response = self.gemini_model.generate_content(
                        full_prompt_text,
                        generation_config={
                            "temperature": 0.9,
                            "max_output_tokens": 100,
                        },
                        safety_settings={
                            'HARASSMENT': 'block_none',
                            'HATE_SPEECH': 'block_none',
                            'DANGEROUS': 'block_none',
                            'SEXUALLY_EXPLICIT': 'block_none',
                        },
                        request_options={"timeout": 8}
                    )
                    
                    actor_response = response.text.strip()
                    state["actor_response"] = actor_response
                    state["actor_complete"] = True
                    llm_success = True
                    llm_source = "Gemini"
                    
                    log_security_event(
                        logger,
                        "ACTOR",
                        f"✅ Gemini response: {actor_response[:80]}...",
                        session_id=session_id,
                        emotion=emotional_state,
                        language=language,
                    )
                    break
                    
                except Exception as e:
                    logger.warning(f"Gemini attempt {attempt + 1}/{max_retries} failed: {str(e)[:100]}")
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(0.5)
                    continue
        
        # 4. If all LLMs failed, use rich contextual fallbacks
        if not llm_success:
            logger.info("Gemini unavailable, using smart contextual responses")
            
            # Extract keywords from scammer's message for contextual responses
            current_msg = state.get("current_message", "").lower()
            has_otp = 'otp' in current_msg
            has_account = 'account' in current_msg
            has_urgent = 'urgent' in current_msg or 'immediately' in current_msg
            has_block = 'block' in current_msg or 'locked' in current_msg
            
            # Rich, human-like fallback responses with MUCH more variety
            if language == 'english':
                fallback_responses = {
                    "confused": [
                        "I don't understand... What is this?",
                        "I'm confused. What are you saying?",
                        "Can you explain this to me please?",
                        "Wait, what? I don't get it...",
                        "What do you mean?",
                        "I'm not understanding properly...",
                        "Could you say that again? I didn't follow",
                        "This is confusing me... what's happening?",
                        "Sorry, I'm an old person. Explain slowly?",
                        "What account are you talking about?" if has_account else "Huh? What?",
                        "OTP? What is OTP?" if has_otp else "I don't know what you mean",
                        "Why are you calling me?",
                        "Is this some mistake?",
                        "I think you have wrong number...",
                        "Beta, speak slowly. I dont understand these technical words"
                    ],
                    "scared": [
                        "I'm getting scared. Is this real?",
                        "Oh no! What's the problem?",
                        "This is worrying me... What should I do?",
                        "Oh god! What happened to my account?",
                        "This is very frightening... Are you sure?",
                        "I'm panicking now... Is my money safe?",
                        "Should I go to the bank? I'm so worried!",
                        "My hands are shaking... What do I need to do?",
                        "Please help me! I don't want to lose my savings!",
                        "Is someone using my account without permission?",
                        "Oh my! Will I lose all my money?" if has_block else "What's wrong?",
                        "2 hours only?? That's so soon!" if has_urgent else "This sounds serious...",
                        "I'm alone at home... I'm scared",
                        "Should I call my son? He knows computers",
                        "Are you really from the bank?"
                    ],
                    "curious": [
                        "Okay, tell me... But what is your number first?",
                        "I understand... But who are you exactly?",
                        "Fine... But what's your company name?",
                      "Wait, can you give me your employee ID?",
                        "What is your name and department?",
                        "How do I know you're really from SBI?",
                        "Can you call me from official bank number?",
                        "What branch are you calling from?",
                        "Let me verify... What's the bank's head office number?",
                        "My bank manager is Mr. Sharma. Do you know him?",
                        "Can I come to the bank tomorrow instead?",
                        "Why can't I just visit the branch?",
                        "Okay... but first tell me your full name?",
                        "How did you get my number?",
                        "Can you send me an official email first?"
                    ],
                    "extracting": [
                        "Yes yes, first you give me your details?",
                        "Okay... But send your WhatsApp number first?",
                        "I'm ready... What's your office address?",
                        "Fine, but what's your official email ID?",
                        "Alright... What's your supervisor's name?",
                        "Tell me the bank's customer care number first",
                        "What's your desk number at the bank?",
                        "Can you give me a reference number for this call?",
                        "What's the complaint ticket number?",
                        "Send me your ID card photo first",
                        "What's your manager's contact?",
                        "Give me the bank's main office landline",
                        "I need your employee code first",
                        "What's the official website I should check?",
                        "My neighbor works at bank. Should I ask him to verify you?"
                    ]
                }
            else:
                fallback_responses = {
                    "confused": [
                        "Arre, samajh nahi aa raha... Ye kya hai?",
                        "Beta, main confused hu. Kya bol rahe ho?",
                        "Mujhe samajh nahi aa raha... Thoda explain karo?",
                        "Kya?? Ye sab kya ho raha hai?",
                        "Main buddhi hu beta, samjhao dhang se",
                        "Matlab? Kuch samajh nahi aaya",
                        "Ruko ruko... ye account kaun sa?",
                        "OTP kya hota hai? Pehli baar sun raha hu" if has_otp else "Ye kya cheez hai?",
                        "Tum kaun ho beta?",
                        "Galat number aa gaya kya?",
                        "Bank se ho? Kaise yakeen karu?",
                        "Mera account? Koi problem hai kya?",
                        "Arre baap re! Kya bol rahe ho?",
                        "Thoda aaram se bolo, main samajh nahi pa raha",
                        "Ye sab technical baatein mujhe nahi aati"
                    ],
                    "scared": [
                        "Mujhe dar lag raha hai. Ye sach hai kya?",
                        "Arre baap re! Ye kya problem hai?",
                        "Bahut tension ho raha hai... Kya karu?",
                        "Haye Ram! Mera paisa toh safe hai na?",
                        "2 ghante mein block?? Itni jaldi!?" if has_urgent else "Itni badi problem??",
                        "Main akela hu ghar pe... dar lag raha hai",
                        "Meri saari savings gayi kya?",
                        "Bank jaana padega kya? Main bahut pareshan hu",
                        "Haath kaap rahe hain... kya karna chahiye?",
                        "Kisine mera account use kiya?? Kaise??",
                        "Arre nahi nahi! Mera sab kuch us account mein hai!",
                        "Bhagwan! Ye kya musibat aa gayi",
                        "Apne bete ko phone karu main?",
                        "Sach bol rahe ho na? Mazak nahi kar rahe?",
                        "Meri FD bhi hai us account mein!"
                    ],
                    "curious": [
                        "Theek hai, batao... Lekin tumhara number kya hai?",
                        "Haan samajh gaya... Par pehle tum batao kaun ho?",
                        "Okay... Lekin tumhari company ka naam kya hai?",
                        "Pehle apna employee ID do",
                        "Tumhara manager kaun hai? Naam batao",
                        "SBI ka official number kya hai? Wahan se call karo",
                        "Tumhara department kya hai?",
                        "Kaunse branch se ho?",
                        "Head office ka number do pehle",
                        "Bank mein kaam karte ho? Proof  dikhao",
                        "Kal bank aa jaata hu main... chalega?",
                        "Email bhejo official, phir baat karte hain",
                        "Mera branch manager Mr. Sharma ko jaante ho?",
                        "Mera number kaise mila tumhe?",
                        "Pehle apna WhatsApp number do verification ke liye"
                    ],
                    "extracting": [
                        "Haan haan, pehle aap apni details do na?",
                        "Theek hai... Par pehle apna WhatsApp number bhejo?",
                        "Main ready hu... Tumhara office ka address kya hai?",
                        "Achha... to pehle tum apni ID dikhaao",
                        "Batao pehle tumhara supervisor kaun hai?",
                        "Customer care number do bank ka",
                        "Office ka landline number do",
                        "Tumhara desk number kya hai?",
                        "Complaint ticket number do mujhe",
                        "Reference number hai koi is call ka?",
                        "Apna visiting card bhejo WhatsApp pe",
                        "Manager se baat karwaao pehle",
                        "Employee code batao apna",
                        "Official website pe check karna chahta hu pehle",
                        "Mere padosi bhi bank mein kaam karte hain... unse puch lu?"
                    ]
                }
            
            # Use turn number AND context to select response
            responses = fallback_responses.get(emotional_state, fallback_responses["confused"])
            
            # Add some randomness but weighted by turn number
            import random
            if len(responses) > 5:
                # Use a mix of sequential and random to avoid exact repetition
                base_idx = (turn_number - 1) % len(responses)
                # Pick from  nearby responses with some randomness
                candidates = [
                    responses[base_idx],
                    responses[(base_idx + 1) % len(responses)],
                    responses[(base_idx + random.randint(2, 4)) % len(responses)]
                ]
                state["actor_response"] = random.choice(candidates)
            else:
                response_idx = (turn_number - 1) % len(responses)
                state["actor_response"] = responses[response_idx]
            
            state["actor_complete"] = True
            
            log_security_event(
                logger,
                "ACTOR",
                "Used smart fallback response",
                session_id=session_id,
                language=language,
                emotion=emotional_state,
            )
        
        return state

