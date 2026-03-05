# 🤖 TalentScout — AI-Powered Hiring Assistant

An intelligent chatbot built with **Python** and **Streamlit** that conducts initial candidate screening interviews for a fictional recruitment agency. Powered by **Groq AI (LLaMA 3.3 70B)**, it collects candidate information through natural conversation and generates tailored technical assessment questions.

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Features](#-features)
- [Demo](#-demo)
- [Installation](#-installation)
- [Usage Guide](#-usage-guide)
- [Project Structure](#-project-structure)
- [Technical Details](#-technical-details)
- [Prompt Design](#-prompt-design)
- [Data Handling & Privacy](#-data-handling--privacy)
- [Challenges & Solutions](#-challenges--solutions)

---

## 🎯 Project Overview

**TalentScout** is an AI Hiring Assistant chatbot designed to streamline the initial candidate screening process for a recruitment agency specializing in technology placements. Instead of static application forms, candidates interact with an intelligent conversational agent that:

1. **Gathers essential candidate information** — Name, email, phone, experience, desired position, location, and tech stack through natural dialogue.
2. **Generates tailored technical questions** — Based on the candidate's declared tech stack and experience level, the bot creates 3-5 relevant technical assessment questions.
3. **Handles the full interview lifecycle** — From warm greeting to graceful sign-off, with context-aware follow-ups and fallback handling.

---

## ✨ Features

### Core Features
| Feature | Description |
|---------|-------------|
| **Conversational Data Collection** | Collects 7 candidate fields through natural dialogue, not rigid forms |
| **Dynamic Question Generation** | Generates 3-5 tech questions tailored to the candidate's stack and experience |
| **Context Retention** | Maintains full conversation context across multiple messages |
| **Fallback Mechanism** | Redirects off-topic inputs back to the interview without breaking flow |
| **Exit Handling with Follow-up** | Asks candidates once to complete pending fields before ending |
| **Real-time Progress Tracking** | Sidebar dashboard shows collected fields and completion percentage |
| **Data Privacy (GDPR)** | PII masking (email, phone) before saving to disk |

### Technical Highlights
- **Entity Extraction** — LLM-powered JSON extraction from freeform text
- **State Machine Architecture** — Deterministic 4-state conversation flow
- **Retry with Backoff** — Automatic retry on API rate limits
- **Anonymized Storage** — UUID-based candidate identification
- **Input Validation** — Regex-based email and phone validation

---

## 🖥️ Demo

### Conversation Flow
```
Greeting → Info Collection (7 fields) → Technical Assessment (3-5 Qs) → Sign-off
```

### Sidebar Progress Tracker
The sidebar shows real-time progress with:
- Current interview stage indicator
- Individual field status cards (Pending / Collected)
- Gradient completion bar (0-100%)

---

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- A free Groq API key ([Get one here](https://console.groq.com/keys))

### Step-by-Step Setup

```bash
# 1. Clone the repository
git clone <repository-url>
cd AI_ML_Intern_Assignment

# 2. Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add your Groq API key:
# GROQ_API_KEY=your_api_key_here

# 5. Run the application
streamlit run app.py
```

The app will open at `http://localhost:8501` in your browser.

### Dependencies
```
streamlit>=1.31.0      # Web UI framework
groq>=0.9.0            # Groq API client (LLaMA 3.3)
python-dotenv>=1.0.1   # Environment variable management
```

---

## 📖 Usage Guide

### Starting an Interview
1. Launch the app with `streamlit run app.py`
2. The chatbot will greet you and ask for your name
3. Provide your information naturally — you can give multiple details in one message

### Example Conversation
```
Bot:  Hello! I'm TalentScout's AI Hiring Assistant. I'll be conducting 
      a quick screening interview. Could you tell me your full name?

You:  Hi, I'm Ram Kapadia from Mumbai

Bot:  Great to meet you, Ram! I've noted your location as Mumbai. 
      Could you share your email address?

You:  ram@example.com, phone 9876543210

Bot:  Perfect! What position are you looking for and how many years 
      of experience do you have?

You:  I'm looking for a Full Stack Developer role, 3 years experience

Bot:  Excellent! What technologies and tools are you proficient in?

You:  Python, Django, React, PostgreSQL, Docker

Bot:  I have all the information I need! Here are your technical questions:
      Q1. How would you optimize a slow Django ORM query?
      Q2. Explain React's virtual DOM and reconciliation...
      ...
```

### Exit Commands
Type any of these to end the conversation:
`bye`, `quit`, `exit`, `goodbye`, `stop`, `done`, `leave`, `cancel`

> **Note:** If you have pending fields, the bot will gently ask once if you'd like to complete them before leaving.

### Starting a New Interview
Click the **"🔄 Start New Interview"** button in the sidebar to reset everything.

---

## 📁 Project Structure

```
AI_ML_Intern_Assignment/
├── app.py                  # Streamlit UI — frontend, chat interface, sidebar
├── chatbot_engine.py       # Core logic — state machine, LLM calls, entity extraction
├── prompts.py              # All prompt templates — persona, extraction, questions
├── data_manager.py         # Data handling — validation, masking, persistence
├── requirements.txt        # Python dependencies
├── .env                    # API key (not committed)
├── .env.example            # Template for environment variables
├── .gitignore              # Excludes .env, data/, __pycache__
├── data/
│   └── candidates.json     # Mock database (auto-created, not committed)
└── README.md               # This file
```

### Module Responsibilities

| Module | Purpose |
|--------|---------|
| `app.py` | Streamlit frontend — page layout, custom CSS, session state, chat rendering |
| `chatbot_engine.py` | Conversation state machine, Groq API integration, entity extraction, question generation |
| `prompts.py` | Centralized prompt templates for all LLM interactions |
| `data_manager.py` | Email/phone validation, tech stack parsing, PII masking, JSON persistence |

---

## ⚙️ Technical Details

### Architecture Overview
```
┌──────────────────────────────────────────────────────┐
│                    Streamlit UI (app.py)              │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────┐   │
│  │  Header   │  │  Chat Area   │  │   Sidebar     │   │
│  │(gradient) │  │ (messages)   │  │  (progress)   │   │
│  └──────────┘  └──────┬───────┘  └───────────────┘   │
│                       │                               │
├───────────────────────┼───────────────────────────────┤
│              chatbot_engine.py                        │
│  ┌─────────────────┐  │  ┌──────────────────────┐    │
│  │  State Machine   │◄─┤  │  Entity Extraction   │    │
│  │ (4 states)       │  │  │  (JSON parsing)      │    │
│  └────────┬────────┘  │  └──────────────────────┘    │
│           │           │                               │
│  ┌────────▼────────┐  │  ┌──────────────────────┐    │
│  │ Question Gen     │  │  │  Groq API (LLaMA 3)  │    │
│  │ (3-5 Qs)         │──┤  │  + Retry Logic       │    │
│  └─────────────────┘  │  └──────────────────────┘    │
│                       │                               │
├───────────────────────┼───────────────────────────────┤
│            prompts.py │        data_manager.py        │
│  ┌─────────────────┐  │  ┌──────────────────────┐    │
│  │  9 Prompt        │  │  │  Validation          │    │
│  │  Templates       │  │  │  Masking (GDPR)      │    │
│  │                  │  │  │  JSON Persistence    │    │
│  └─────────────────┘  │  └──────────────────────┘    │
└───────────────────────┴───────────────────────────────┘
```

### Conversation State Machine
```
GREETING ──► INFO_COLLECTION ──► TECH_ASSESSMENT ──► SIGN_OFF ──► ENDED
                │                       │                           ▲
                │      (exit with       │      (exit with           │
                │       follow-up)      │       follow-up)         │
                └───────────────────────┴───────────────────────────┘
```

### LLM Configuration
| Parameter | Value |
|-----------|-------|
| **Provider** | Groq |
| **Model** | `llama-3.3-70b-versatile` |
| **Temperature** | 0.7 (balanced creativity) |
| **Max Tokens** | 1024 |
| **Retry Strategy** | Exponential backoff (3s, 6s, 12s) |

### Why Groq + LLaMA 3.3?
- **Speed**: Groq's custom LPU hardware delivers 500+ tokens/second — near-instant responses
- **Free Tier**: Generous rate limits suitable for development and testing
- **Quality**: LLaMA 3.3 70B matches GPT-4 class performance on structured tasks
- **Privacy**: Open-weight model with transparent data handling

---

## 🎨 Prompt Design

### Design Philosophy
All prompts are centralized in `prompts.py` using a **template-based approach** with clear placeholders. Each prompt is engineered to:
1. Return **structured JSON** where possible (entity extraction, question generation)
2. Include **explicit behavioral rules** to prevent deviation
3. Maintain a **consistent persona** across all interactions

### Prompt Catalog

#### 1. System Persona (`SYSTEM_PROMPT`)
- Defines the bot's identity as "TalentScout Assistant"
- Sets 7 strict behavioral rules (never deviate from purpose, never fabricate info, etc.)
- Lists the 7 fields to collect and the interview flow
- **Key design choice**: Rules are numbered and bolded to increase LLM compliance

#### 2. Entity Extraction (`ENTITY_EXTRACTION_PROMPT`)
- Instructs the LLM to parse freeform text into a structured JSON object
- Includes field-by-field extraction instructions with type hints (string, integer, list)
- **Key design choice**: Explicit "only extract what's mentioned, don't guess" rule prevents hallucination
- **Normalization rules**: e.g., "js" → "JavaScript", "py" → "Python" for tech stack consistency

#### 3. Info Collection (`INFO_COLLECTION_PROMPT`)
- Dynamic prompt injected with currently collected info and missing fields
- Instructs the bot to ask for ONE missing field at a time (natural flow)
- **Key design choice**: Shows what's already collected to prevent redundant questions

#### 4. Technical Questions (`TECH_QUESTION_PROMPT`)
- Generates 3-5 questions based on the candidate's tech stack and experience
- Difficulty scales with experience: 0-2 years (fundamentals), 3-5 (design), 5+ (architecture)
- **Key design choice**: Outputs a JSON array for reliable programmatic parsing
- Questions target DIFFERENT technologies from the stack for breadth

#### 5. Fallback (`FALLBACK_PROMPT`)
- Handles off-topic messages without breaking conversation flow
- Acknowledges the user's input, then redirects to the interview
- **Key design choice**: Never answers unrelated questions — maintains interview integrity

#### 6. Exit Detection (`is_exit_command`)
- Pattern matching against 12 exit keywords (bye, quit, stop, etc.)
- Case-insensitive substring matching for natural language flexibility
- **Key design choice**: First exit attempt with pending fields triggers a gentle follow-up

---

## 🔒 Data Handling & Privacy

### Simulated Storage
- **Mock Database**: Local JSON file (`data/candidates.json`)
- **Auto-created**: The `data/` directory is created on first save
- **Anonymized IDs**: Each candidate gets a UUID v4 identifier
- **Not committed**: `data/candidates.json` is excluded via `.gitignore`

### GDPR-Compliant Privacy Measures

| Measure | Implementation |
|---------|---------------|
| **Email Masking** | `ram@gmail.com` → `r***m@g***l.com` |
| **Phone Masking** | `9876543210` → `9876****10` |
| **UUID Anonymization** | Random `candidate_id` instead of using names |
| **Local-only Storage** | No data transmitted to external servers (except LLM API) |
| **API Key Protection** | `.env` file excluded from version control |
| **In-memory Raw Data** | Raw PII exists only during the active session |

### Saved Data Schema
```json
{
    "candidate_id": "a3f8d1b6-0b3b-4b1a-...",
    "name": "Ram Kapadia",
    "email": "r***m@g***l.com",
    "phone": "9876****10",
    "experience_years": 3,
    "position": "Full Stack Developer",
    "location": "Mumbai",
    "tech_stack": ["Python", "Django", "React"],
    "questions": ["Q1...", "Q2...", "Q3..."],
    "answers": ["A1...", "A2...", "A3..."],
    "timestamp": "2026-03-06T01:15:00",
    "status": "COMPLETED"
}
```

---

## 🧩 Challenges & Solutions

### 1. API Rate Limits (Gemini Free Tier)
- **Challenge**: Google Gemini's free tier had strict per-minute quotas, causing frequent `429 Quota Exceeded` errors.
- **Solution**: Switched to **Groq API** (LLaMA 3.3 70B) which offers generous free-tier limits and 500+ tokens/sec. Also implemented **exponential backoff retry logic** (3 attempts with increasing delays).

### 2. Reliable Entity Extraction from Freeform Text
- **Challenge**: Users provide information in unpredictable formats — "I'm Ram from Mumbai, 3 yrs exp in Python/React" — making structured extraction difficult.
- **Solution**: Crafted a detailed **JSON-output entity extraction prompt** with explicit rules for each field type. Added multiple fallback layers: JSON fence removal, normalization (e.g., "js" → "JavaScript"), and null-value filtering.

### 3. Preventing Conversation Deviation
- **Challenge**: LLMs naturally want to be helpful with any question, including off-topic ones like "What's the weather?"
- **Solution**: Implemented a **strict system prompt** with numbered behavioral rules, plus a dedicated **Fallback Prompt** that explicitly instructs the LLM to redirect off-topic queries. The system prompt also says "NEVER deviate from the hiring purpose."

### 4. Graceful Exit with Context Awareness
- **Challenge**: Users might say "bye" mid-interview with incomplete data, losing valuable information.
- **Solution**: Added a **one-time follow-up mechanism** — when exit is triggered with pending fields, the bot asks once if the candidate wants to complete the remaining info before ending. If they insist, it saves what's available and exits gracefully.

### 5. Maintaining Conversation Context
- **Challenge**: Each LLM call is stateless — the model doesn't inherently remember previous messages.
- **Solution**: Maintained a **conversation history list** that is passed with every API call, giving the LLM full context of the ongoing interview. This enables natural follow-ups and prevents the bot from re-asking already-answered questions.

### 6. Data Privacy Compliance
- **Challenge**: Storing raw PII (email, phone) in plaintext poses privacy risks.
- **Solution**: Implemented **masking functions** that replace raw values with partially redacted versions before saving to disk. Only the masked version is persisted — raw data exists only in the live session memory.

---

## 🛠️ Built With

- **[Streamlit](https://streamlit.io/)** — Web interface and chat components
- **[Groq](https://groq.com/)** — Ultra-fast LLM inference (LLaMA 3.3 70B)
- **[Python](https://python.org/)** — Core application logic
- **[python-dotenv](https://pypi.org/project/python-dotenv/)** — Environment variable management

---

## 📄 License

This project was developed as part of an AI/ML Intern Assignment for TalentScout.

---

*Built with ❤️ by Ram Kapadia | Powered by Groq AI*
