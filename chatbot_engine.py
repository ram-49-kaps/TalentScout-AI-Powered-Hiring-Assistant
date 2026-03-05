"""
chatbot_engine.py - Core Chatbot Logic & LLM Orchestration
==========================================================
Handles the conversation state machine, Groq API calls (LLaMA 3),
entity extraction, dynamic question generation, and fallback logic.

Conversation States:
    GREETING -> INFO_COLLECTION -> TECH_ASSESSMENT -> SIGN_OFF

Design Decisions:
    - Uses Groq (llama-3.3-70b-versatile) for ultra-fast, free inference.
    - Entity extraction uses structured JSON prompts for reliable parsing.
    - State transitions are deterministic based on collected data completeness.
    - Conversation history maintained via message list for context continuity.
"""

import json
import os
import time
from groq import Groq
from dotenv import load_dotenv

from prompts import (
    SYSTEM_PROMPT,
    GREETING_PROMPT,
    ENTITY_EXTRACTION_PROMPT,
    INFO_COLLECTION_PROMPT,
    TECH_QUESTION_PROMPT,
    ANSWER_COLLECTION_PROMPT,
    SIGNOFF_PROMPT,
    FALLBACK_PROMPT,
    is_exit_command,
)
from data_manager import (
    get_missing_fields,
    get_collected_info,
    validate_email,
    parse_tech_stack,
    save_candidate,
)

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Model to use (LLaMA 3.3 70B - fast and powerful)
MODEL_NAME = "llama-3.3-70b-versatile"


# ──────────────────────────────────────────────
# Conversation States
# ──────────────────────────────────────────────
class ConversationState:
    """Enum-like class for conversation states."""
    GREETING = "GREETING"
    INFO_COLLECTION = "INFO_COLLECTION"
    TECH_ASSESSMENT = "TECH_ASSESSMENT"
    SIGN_OFF = "SIGN_OFF"
    ENDED = "ENDED"


# ──────────────────────────────────────────────
# LLM Interaction Helpers
# ──────────────────────────────────────────────
def _call_llm(prompt: str, max_retries: int = 3) -> str:
    """
    Send a one-shot prompt to Groq and return the text response.
    Used for utility tasks like entity extraction and question generation.
    Includes automatic retry with backoff for rate limit errors.
    """
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1024,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "rate" in error_str.lower():
                wait_time = (2 ** attempt) * 3  # 3s, 6s, 12s
                print(f"[Rate Limit] Retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                print(f"[LLM Error] {e}")
                return ""
    print("[LLM Error] Max retries exceeded.")
    return ""


def _call_chat(conversation_history: list, message: str, max_retries: int = 3) -> str:
    """
    Send a message with full conversation history to Groq for context continuity.
    The conversation_history is a list of {"role": ..., "content": ...} dicts.
    Includes automatic retry with backoff for rate limit errors.
    """
    # Build messages with system prompt + history + new message
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": message})

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
            )
            reply = response.choices[0].message.content.strip()

            # Add to history for future context
            conversation_history.append({"role": "user", "content": message})
            conversation_history.append({"role": "assistant", "content": reply})

            return reply
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "rate" in error_str.lower():
                wait_time = (2 ** attempt) * 3
                print(f"[Rate Limit] Retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                print(f"[Chat Error] {e}")
                return "I apologize, I encountered a brief issue. Could you please repeat that?"
    return "I'm experiencing high traffic right now. Please try again in a moment."


# ──────────────────────────────────────────────
# Entity Extraction
# ──────────────────────────────────────────────
def extract_entities(user_message: str) -> dict:
    """
    Use the LLM to extract candidate information from a message.
    Returns a dictionary of extracted fields (non-null values only).
    """
    prompt = ENTITY_EXTRACTION_PROMPT.format(user_message=user_message)
    raw_response = _call_llm(prompt)

    try:
        # Clean the response — remove markdown code fences if present
        cleaned = raw_response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        extracted = json.loads(cleaned)

        # Filter out null values
        result = {}
        for key, value in extracted.items():
            if value is not None and value != "" and value != []:
                result[key] = value

        return result

    except (json.JSONDecodeError, Exception) as e:
        print(f"[Extraction Error] Could not parse: {raw_response[:200]}... Error: {e}")
        return {}


# ──────────────────────────────────────────────
# Technical Question Generation
# ──────────────────────────────────────────────
def generate_tech_questions(candidate: dict, num_questions: int = 4) -> list:
    """
    Generate technical interview questions based on the candidate's profile.
    
    Args:
        candidate: The candidate data dictionary.
        num_questions: Number of questions to generate (3-5).
        
    Returns:
        A list of question strings.
    """
    num_questions = max(3, min(5, num_questions))  # Clamp between 3 and 5

    tech_stack_str = ", ".join(candidate.get("tech_stack", []))
    prompt = TECH_QUESTION_PROMPT.format(
        name=candidate.get("name", "Candidate"),
        position=candidate.get("position", "Software Developer"),
        experience_years=candidate.get("experience_years", 0),
        tech_stack=tech_stack_str,
        num_questions=num_questions,
    )

    raw_response = _call_llm(prompt)

    try:
        # Clean markdown fences
        cleaned = raw_response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        questions = json.loads(cleaned)
        if isinstance(questions, list):
            return questions[:5]  # Safety cap at 5
    except (json.JSONDecodeError, Exception) as e:
        print(f"[Question Gen Error] {e}")

    # Fallback: return generic questions
    return [
        f"Can you explain a recent project where you used {tech_stack_str}?",
        f"What are the key advantages of using {candidate.get('tech_stack', ['your preferred technology'])[0]}?",
        "How do you approach debugging a complex issue in production?",
        "Describe your experience with version control and collaborative development.",
    ]


# ──────────────────────────────────────────────
# Core State Machine: Process Message
# ──────────────────────────────────────────────
def generate_greeting() -> str:
    """Generate the initial greeting message."""
    return _call_llm(SYSTEM_PROMPT + "\n\n" + GREETING_PROMPT)


def process_message(
    user_message: str,
    current_state: str,
    candidate_data: dict,
    conversation_history: list,
    exit_pending: bool = False,
) -> tuple:
    """
    Process a user message and return the updated state, bot response, candidate data, 
    and exit_pending flag.
    
    Args:
        user_message: The message from the candidate.
        current_state: The current conversation state.
        candidate_data: The dictionary holding current candidate info.
        conversation_history: List of message dicts for context continuity.
        exit_pending: Whether the user already attempted to exit once.
        
    Returns:
        Tuple of (next_state, bot_response, updated_candidate_data, exit_pending)
    """
    # ── Check for exit commands ──
    if is_exit_command(user_message):
        missing = get_missing_fields(candidate_data)

        # If fields are still missing AND this is the FIRST exit attempt → follow-up
        if missing and not exit_pending:
            missing_labels = ", ".join(missing)
            follow_up = (
                f"I noticed we still have a few details pending: **{missing_labels}**. "
                "It'll only take a minute to complete — this helps us match you with "
                "the best opportunities!\n\n"
                "Would you like to quickly fill in the remaining info? "
                "If not, just say **bye** again and I'll wrap things up."
            )
            return current_state, follow_up, candidate_data, True

        # Second exit attempt OR all fields complete → actually end
        candidate_data["status"] = "ABORTED"
        save_candidate(candidate_data)
        farewell = (
            "Thank you for your time! I understand you'd like to end our conversation. "
            "Your information has been saved. If you'd like to continue the screening "
            "process in the future, feel free to come back. Have a great day! 👋"
        )
        return ConversationState.ENDED, farewell, candidate_data, False

    # ── If user continues after a follow-up attempt, reset exit_pending ──

    # ── STATE: INFO_COLLECTION ──
    if current_state == ConversationState.INFO_COLLECTION:
        state, response, data = _handle_info_collection(user_message, candidate_data, conversation_history)
        return state, response, data, False

    # ── STATE: TECH_ASSESSMENT ──
    elif current_state == ConversationState.TECH_ASSESSMENT:
        state, response, data = _handle_tech_assessment(user_message, candidate_data, conversation_history)
        return state, response, data, False

    # ── STATE: SIGN_OFF ──
    elif current_state == ConversationState.SIGN_OFF:
        candidate_data["status"] = "COMPLETED"
        save_candidate(candidate_data)
        return ConversationState.ENDED, "Thank you again! Good luck! 🌟", candidate_data, False

    # ── Default fallback ──
    return current_state, "I'm not sure how to respond to that. Let's continue with the interview!", candidate_data, False


def _handle_info_collection(user_message: str, candidate: dict, conversation_history: list) -> tuple:
    """Handle the INFO_COLLECTION state — extract entities and ask for missing fields."""

    # Extract entities from user message
    extracted = extract_entities(user_message)

    # Update candidate data with extracted entities
    if extracted.get("name") and not candidate.get("name"):
        candidate["name"] = extracted["name"]

    if extracted.get("email"):
        email = extracted["email"]
        if validate_email(email):
            candidate["email"] = email
        else:
            response = _call_chat(
                conversation_history,
                f"The candidate provided an invalid email: '{email}'. "
                "Politely ask them to provide a valid email address."
            )
            return ConversationState.INFO_COLLECTION, response, candidate

    if extracted.get("phone") and not candidate.get("phone"):
        candidate["phone"] = extracted["phone"]

    if extracted.get("experience_years") is not None and candidate.get("experience_years") is None:
        try:
            candidate["experience_years"] = int(extracted["experience_years"])
        except (ValueError, TypeError):
            candidate["experience_years"] = extracted["experience_years"]

    if extracted.get("position") and not candidate.get("position"):
        candidate["position"] = extracted["position"]

    if extracted.get("location") and not candidate.get("location"):
        candidate["location"] = extracted["location"]

    if extracted.get("tech_stack") and not candidate.get("tech_stack"):
        candidate["tech_stack"] = parse_tech_stack(extracted["tech_stack"])

    # Check what's still missing
    missing = get_missing_fields(candidate)

    if not missing:
        # All info collected! Transition to TECH_ASSESSMENT
        questions = generate_tech_questions(candidate)
        candidate["questions"] = questions

        # Build question presentation
        question_text = "Excellent! I have all the information I need. 🎯\n\n"
        question_text += "Now, let me assess your technical skills based on your tech stack "
        question_text += f"(**{', '.join(candidate['tech_stack'])}**).\n\n"
        question_text += "Here are your technical questions:\n\n"

        for i, q in enumerate(questions, 1):
            question_text += f"**Q{i}.** {q}\n\n"

        question_text += "\nPlease take your time and answer each question. You can answer them all at once or one by one."

        return ConversationState.TECH_ASSESSMENT, question_text, candidate

    else:
        # Ask for the next missing field
        collected = get_collected_info(candidate)
        prompt = INFO_COLLECTION_PROMPT.format(
            collected_info=json.dumps(collected, indent=2) if collected else "Nothing yet",
            missing_fields=", ".join(missing),
            user_message=user_message,
        )
        response = _call_chat(conversation_history, prompt)
        return ConversationState.INFO_COLLECTION, response, candidate


def _handle_tech_assessment(user_message: str, candidate: dict, conversation_history: list) -> tuple:
    """Handle the TECH_ASSESSMENT state — collect answers to technical questions."""

    # Add the answer
    candidate["answers"].append(user_message)

    questions = candidate.get("questions", [])
    answered_count = len(candidate["answers"])
    total_questions = len(questions)

    if answered_count >= total_questions:
        # All questions answered — transition to SIGN_OFF
        signoff_response = _call_llm(SIGNOFF_PROMPT.format(
            name=candidate.get("name", "Candidate")
        ))
        candidate["status"] = "COMPLETED"
        save_candidate(candidate)
        return ConversationState.SIGN_OFF, signoff_response, candidate

    else:
        # Acknowledge and present next question (if answering one by one)
        remaining = total_questions - answered_count
        next_question = questions[answered_count]

        prompt = ANSWER_COLLECTION_PROMPT.format(
            current_question=questions[answered_count - 1],
            user_message=user_message,
            remaining_count=remaining,
        )
        response = _call_chat(conversation_history, prompt)

        # Ensure the next question is visible
        if next_question not in response:
            response += f"\n\n**Q{answered_count + 1}.** {next_question}"

        return ConversationState.TECH_ASSESSMENT, response, candidate
