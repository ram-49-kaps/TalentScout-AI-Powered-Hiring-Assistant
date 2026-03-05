"""
app.py - TalentScout Hiring Assistant - Streamlit Frontend
==========================================================
Main entry point for the application. Renders a polished, premium chat interface 
using Streamlit's native chat components with custom CSS styling.

Run with: streamlit run app.py
"""

import streamlit as st
from chatbot_engine import (
    ConversationState,
    generate_greeting,
    process_message,
)
from data_manager import create_empty_candidate

# ──────────────────────────────────────────────
# Page Configuration
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="TalentScout - AI Hiring Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# Premium Custom CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Import Google Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* ── Root Variables ── */
    :root {
        --primary: #6C63FF;
        --primary-light: #8B85FF;
        --primary-dark: #5A52E0;
        --accent: #00D2FF;
        --accent-2: #7A5AF8;
        --success: #10B981;
        --warning: #F59E0B;
        --danger: #EF4444;
        --bg-dark: #0F1117;
        --bg-card: #1A1D2E;
        --bg-card-hover: #222640;
        --text-primary: #F1F5F9;
        --text-secondary: #94A3B8;
        --text-muted: #64748B;
        --border-subtle: rgba(108, 99, 255, 0.15);
        --glow-primary: rgba(108, 99, 255, 0.4);
        --glow-accent: rgba(0, 210, 255, 0.3);
    }
    
    /* ── Global Styles ── */
    .stApp {
        font-family: 'Inter', -apple-system, sans-serif !important;
    }
    
    /* ── Main Container ── */
    .block-container {
        padding-top: 1rem !important;
        max-width: 900px !important;
    }
    
    /* ── Main Header ── */
    .main-header {
        background: linear-gradient(135deg, #6C63FF 0%, #5A52E0 30%, #7A5AF8 60%, #00D2FF 100%);
        padding: 2.5rem 2rem 2rem;
        border-radius: 20px;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 12px 40px rgba(108, 99, 255, 0.35), 0 0 80px rgba(0, 210, 255, 0.08);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 60%);
        animation: shimmer 8s ease-in-out infinite;
    }
    @keyframes shimmer {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        50% { transform: translate(-10%, -10%) rotate(5deg); }
    }
    .main-header h1 {
        color: white;
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -1px;
        position: relative;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    }
    .main-header .subtitle {
        color: rgba(255, 255, 255, 0.8);
        font-size: 1rem;
        margin-top: 0.4rem;
        font-weight: 400;
        letter-spacing: 0.5px;
        position: relative;
    }
    
    /* ── Status Badge ── */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 16px;
        border-radius: 24px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-top: 0.8rem;
        position: relative;
        letter-spacing: 0.3px;
        text-transform: uppercase;
    }
    .status-active {
        background: rgba(16, 185, 129, 0.2);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.15);
    }
    .status-active::before {
        content: '';
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #34D399;
        animation: pulse-dot 2s ease-in-out infinite;
    }
    @keyframes pulse-dot {
        0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.6); }
        50% { opacity: 0.7; box-shadow: 0 0 0 6px rgba(52, 211, 153, 0); }
    }
    .status-ended {
        background: rgba(108, 99, 255, 0.15);
        color: #A5B4FC;
        border: 1px solid rgba(108, 99, 255, 0.3);
    }
    
    /* ── Chat Messages ── */
    [data-testid="stChatMessage"] {
        border-radius: 16px !important;
        padding: 1rem 1.2rem !important;
        margin-bottom: 0.75rem !important;
        border: 1px solid var(--border-subtle) !important;
        backdrop-filter: blur(12px);
        animation: fadeInUp 0.3s ease-out;
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* ── Chat Input ── */
    [data-testid="stChatInput"] {
        border-radius: 16px !important;
    }
    [data-testid="stChatInput"] textarea {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
    }
    
    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        border-right: 1px solid var(--border-subtle) !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }
    
    /* Sidebar Title */
    .sidebar-title {
        font-size: 1.1rem;
        font-weight: 700;
        letter-spacing: -0.3px;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--border-subtle);
    }
    
    /* Sidebar Stage Badge */
    .stage-badge {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 12px 16px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 1.2rem;
        background: linear-gradient(135deg, rgba(108, 99, 255, 0.12), rgba(0, 210, 255, 0.08));
        border: 1px solid rgba(108, 99, 255, 0.2);
        box-shadow: 0 4px 12px rgba(108, 99, 255, 0.08);
    }
    
    /* Sidebar Field Cards */
    .field-card {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 14px;
        border-radius: 10px;
        margin-bottom: 6px;
        font-size: 0.82rem;
        font-weight: 500;
        transition: all 0.2s ease;
        border: 1px solid transparent;
    }
    .field-card:hover {
        transform: translateX(3px);
    }
    .field-collected {
        background: rgba(16, 185, 129, 0.08);
        border-color: rgba(16, 185, 129, 0.2);
        color: #34D399;
    }
    .field-collected .field-icon {
        background: rgba(16, 185, 129, 0.15);
        color: #10B981;
    }
    .field-pending {
        background: rgba(245, 158, 11, 0.06);
        border-color: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        opacity: 0.7;
    }
    .field-pending .field-icon {
        background: rgba(245, 158, 11, 0.1);
        color: #F59E0B;
    }
    .field-icon {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.85rem;
        flex-shrink: 0;
    }
    .field-icon svg {
        width: 16px;
        height: 16px;
        stroke-width: 2;
        fill: none;
        stroke: currentColor;
    }
    .field-label {
        font-weight: 600;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        opacity: 0.7;
    }
    .field-value {
        font-weight: 500;
        font-size: 0.85rem;
        word-break: break-word;
    }
    
    /* ── Progress Bar ── */
    .progress-wrapper {
        margin: 1rem 0;
        padding: 12px 14px;
        border-radius: 12px;
        background: rgba(108, 99, 255, 0.06);
        border: 1px solid rgba(108, 99, 255, 0.12);
    }
    .progress-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .progress-bar-bg {
        width: 100%;
        height: 6px;
        border-radius: 3px;
        background: rgba(255, 255, 255, 0.08);
        overflow: hidden;
    }
    .progress-bar-fill {
        height: 100%;
        border-radius: 3px;
        background: linear-gradient(90deg, #6C63FF, #00D2FF);
        transition: width 0.5s ease;
        box-shadow: 0 0 10px rgba(108, 99, 255, 0.4);
    }
    
    /* ── Completion Card ── */
    .completion-card {
        text-align: center;
        padding: 2.5rem 2rem;
        background: linear-gradient(135deg, rgba(108, 99, 255, 0.08), rgba(0, 210, 255, 0.05));
        border-radius: 20px;
        border: 1px solid rgba(108, 99, 255, 0.2);
        box-shadow: 0 8px 32px rgba(108, 99, 255, 0.1);
        margin: 1rem 0;
    }
    .completion-card .icon {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    .completion-card h3 {
        margin: 0.5rem 0;
        font-weight: 700;
        font-size: 1.3rem;
        letter-spacing: -0.3px;
    }
    .completion-card p {
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin: 0.3rem 0;
    }
    
    /* ── Reset Button ── */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.25s ease !important;
        border: 1px solid rgba(108, 99, 255, 0.3) !important;
        background: linear-gradient(135deg, rgba(108, 99, 255, 0.15), rgba(0, 210, 255, 0.08)) !important;
    }
    .stButton > button:hover {
        border-color: rgba(108, 99, 255, 0.5) !important;
        box-shadow: 0 4px 20px rgba(108, 99, 255, 0.2) !important;
        transform: translateY(-1px) !important;
    }
    
    /* ── Footer ── */
    .footer {
        text-align: center;
        padding: 1.5rem 1rem;
        margin-top: 2rem;
        font-size: 0.78rem;
        color: var(--text-muted);
        border-top: 1px solid var(--border-subtle);
    }
    .footer a {
        color: var(--primary-light);
        text-decoration: none;
    }
    .footer .powered-by {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 20px;
        background: rgba(108, 99, 255, 0.08);
        border: 1px solid rgba(108, 99, 255, 0.12);
        font-size: 0.72rem;
        font-weight: 500;
        margin-top: 0.5rem;
    }
    
    /* ── Hide Streamlit defaults ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Session State Initialization
# ──────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_state" not in st.session_state:
    st.session_state.conversation_state = ConversationState.GREETING

if "candidate_data" not in st.session_state:
    st.session_state.candidate_data = create_empty_candidate()

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "initialized" not in st.session_state:
    st.session_state.initialized = False

if "exit_pending" not in st.session_state:
    st.session_state.exit_pending = False


# ──────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────
is_ended = st.session_state.conversation_state == ConversationState.ENDED
badge_class = "status-ended" if is_ended else "status-active"
badge_text = "Session Complete" if is_ended else "Live Interview"

st.markdown(f"""
<div class="main-header">
    <h1>TalentScout</h1>
    <p class="subtitle">AI-Powered Candidate Screening Assistant</p>
    <span class="status-badge {badge_class}">{badge_text}</span>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Sidebar: Premium Progress Tracker
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">Interview Dashboard</div>', unsafe_allow_html=True)

    # Show current state — clean text labels
    state_labels = {
        ConversationState.GREETING: ("○", "Welcome"),
        ConversationState.INFO_COLLECTION: ("◉", "Collecting Information"),
        ConversationState.TECH_ASSESSMENT: ("◉", "Technical Assessment"),
        ConversationState.SIGN_OFF: ("●", "Session Complete"),
        ConversationState.ENDED: ("●", "Interview Ended"),
    }
    icon, label = state_labels.get(st.session_state.conversation_state, ("○", "Unknown"))
    st.markdown(f'<div class="stage-badge">{icon} <span>{label}</span></div>', unsafe_allow_html=True)

    # Field definitions — clean SVG icons (Feather-style)
    SVG_USER = '<svg viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>'
    SVG_MAIL = '<svg viewBox="0 0 24 24"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>'
    SVG_PHONE = '<svg viewBox="0 0 24 24"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>'
    SVG_BRIEFCASE = '<svg viewBox="0 0 24 24"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>'
    SVG_TARGET = '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>'
    SVG_MAPPIN = '<svg viewBox="0 0 24 24"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>'
    SVG_CODE = '<svg viewBox="0 0 24 24"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>'

    fields = {
        "name": (SVG_USER, "Name"),
        "email": (SVG_MAIL, "Email"),
        "phone": (SVG_PHONE, "Phone"),
        "experience_years": (SVG_BRIEFCASE, "Experience"),
        "position": (SVG_TARGET, "Position"),
        "location": (SVG_MAPPIN, "Location"),
        "tech_stack": (SVG_CODE, "Tech Stack"),
    }

    collected_count = 0
    field_html = ""

    for field_key, (field_icon, field_label) in fields.items():
        value = st.session_state.candidate_data.get(field_key)
        if value and value != []:
            collected_count += 1
            if field_key == "tech_stack" and isinstance(value, list):
                display_val = ", ".join(value)
            else:
                display_val = str(value)
            field_html += f"""
            <div class="field-card field-collected">
                <div class="field-icon">{field_icon}</div>
                <div>
                    <div class="field-label">{field_label}</div>
                    <div class="field-value">{display_val}</div>
                </div>
            </div>"""
        else:
            field_html += f"""
            <div class="field-card field-pending">
                <div class="field-icon">{field_icon}</div>
                <div>
                    <div class="field-label">{field_label}</div>
                    <div class="field-value">Pending...</div>
                </div>
            </div>"""

    st.markdown(field_html, unsafe_allow_html=True)

    # Progress bar
    progress_pct = int((collected_count / len(fields)) * 100)
    st.markdown(f"""
    <div class="progress-wrapper">
        <div class="progress-header">
            <span>Completion</span>
            <span>{collected_count}/{len(fields)} fields</span>
        </div>
        <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width: {progress_pct}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Reset button with spacing
    st.markdown("")
    if st.button("🔄 Start New Interview", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_state = ConversationState.GREETING
        st.session_state.candidate_data = create_empty_candidate()
        st.session_state.conversation_history = []
        st.session_state.initialized = False
        st.session_state.exit_pending = False
        st.rerun()

    # Sidebar footer
    st.markdown("---")
    st.markdown(
        '<p style="font-size: 0.72rem; color: var(--text-muted); text-align: center;">'
        '🔒 All data is encrypted and handled<br>in compliance with GDPR standards.</p>',
        unsafe_allow_html=True
    )


# ──────────────────────────────────────────────
# Generate Initial Greeting
# ──────────────────────────────────────────────
if not st.session_state.initialized:
    with st.spinner("⚡ Initializing your interview session..."):
        greeting = generate_greeting()
        if greeting:
            st.session_state.messages.append({
                "role": "assistant",
                "content": greeting,
            })
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": (
                    "Welcome to TalentScout! I'm your AI Hiring Assistant. "
                    "I'll be conducting a quick screening interview to learn about your "
                    "background and technical skills.\n\nLet's start — could you please tell me your **full name**?"
                ),
            })
        st.session_state.conversation_state = ConversationState.INFO_COLLECTION
        st.session_state.initialized = True


# ──────────────────────────────────────────────
# Display Chat History
# ──────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ──────────────────────────────────────────────
# Chat Input & Processing
# ──────────────────────────────────────────────
if st.session_state.conversation_state != ConversationState.ENDED:
    if user_input := st.chat_input("Type your response here..."):
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Process the message
        with st.spinner("Thinking..."):
            next_state, response, updated_candidate, exit_flag = process_message(
                user_message=user_input,
                current_state=st.session_state.conversation_state,
                candidate_data=st.session_state.candidate_data,
                conversation_history=st.session_state.conversation_history,
                exit_pending=st.session_state.exit_pending,
            )

        # Update state
        st.session_state.conversation_state = next_state
        st.session_state.candidate_data = updated_candidate
        st.session_state.exit_pending = exit_flag

        # Display bot response
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Rerun to update sidebar
        st.rerun()

else:
    # Interview completed card
    st.markdown("""
    <div class="completion-card">
        <div class="icon">🎉</div>
        <h3>Interview Session Complete!</h3>
        <p>Thank you for participating in the screening process.</p>
        <p>Your responses have been securely recorded.</p>
        <p style="margin-top: 1rem; font-size: 0.8rem; opacity: 0.6;">
            Click "Start New Interview" in the sidebar to begin another session.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────
st.markdown("""
<div class="footer">
    <p>Built with by TalentScout</p>
    <span class="powered-by">⚡ Powered by Groq AI &nbsp;•&nbsp; LLaMA 3.3</span>
</div>
""", unsafe_allow_html=True)
