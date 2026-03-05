"""
data_manager.py - Data Persistence & Privacy Handler
=====================================================
Handles saving, loading, and anonymizing candidate data.
Uses a local JSON file as a mock database, compliant with
data privacy best practices (GDPR-inspired).

Design Decisions:
    - Each candidate gets a unique anonymized UUID.
    - Email and phone are partially masked before storage.
    - Data is stored in data/candidates.json.
"""

import json
import uuid
import os
import re
from datetime import datetime

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "candidates.json")


# ──────────────────────────────────────────────
# Validation Utilities
# ──────────────────────────────────────────────
def validate_email(email: str) -> bool:
    """
    Validate email format using regex.
    Returns True if the email matches a standard pattern.
    """
    if not email:
        return False
    pattern = r'^[\w\.\-\+]+@[\w\.\-]+\.\w+$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Basic phone number validation.
    Accepts digits, spaces, dashes, parentheses, and optional leading +.
    """
    if not phone:
        return False
    pattern = r'^[\+]?[\d\s\-\(\)]{7,15}$'
    return bool(re.match(pattern, phone.strip()))


def parse_tech_stack(tech_stack_input) -> list:
    """
    Convert a tech stack input (string or list) into a clean list of strings.
    
    Examples:
        "Python, Django, React" -> ["Python", "Django", "React"]
        "Python and Django and React" -> ["Python", "Django", "React"]
        ["Python", "Django"] -> ["Python", "Django"]  (pass-through)
    """
    if isinstance(tech_stack_input, list):
        return [tech.strip() for tech in tech_stack_input if tech.strip()]

    if isinstance(tech_stack_input, str):
        # Replace common separators with comma
        normalized = tech_stack_input.replace(" and ", ",").replace(";", ",").replace("/", ",")
        return [tech.strip() for tech in normalized.split(",") if tech.strip()]

    return []


# ──────────────────────────────────────────────
# Data Anonymization
# ──────────────────────────────────────────────
def mask_email(email: str) -> str:
    """
    Partially mask an email for privacy.
    Example: john.doe@gmail.com -> j*****e@gmail.com
    """
    if not email or "@" not in email:
        return email
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        masked_local = local[0] + "*"
    else:
        masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
    return f"{masked_local}@{domain}"


def mask_phone(phone: str) -> str:
    """
    Partially mask a phone number for privacy.
    Example: +91-9876543210 -> +91-98******10
    """
    if not phone:
        return phone
    digits = re.sub(r'\D', '', phone)
    if len(digits) <= 4:
        return phone
    return digits[:4] + "*" * (len(digits) - 6) + digits[-2:]


# ──────────────────────────────────────────────
# Candidate Data Model
# ──────────────────────────────────────────────
def create_empty_candidate() -> dict:
    """
    Create a fresh candidate data dictionary with all fields initialized to None.
    """
    return {
        "candidate_id": str(uuid.uuid4()),
        "name": None,
        "email": None,
        "phone": None,
        "experience_years": None,
        "position": None,
        "location": None,
        "tech_stack": [],
        "questions": [],
        "answers": [],
        "timestamp": datetime.now().isoformat(),
        "status": "IN_PROGRESS"
    }


def get_missing_fields(candidate: dict) -> list:
    """
    Return a list of field names that are still missing (None or empty).
    """
    required = {
        "name": candidate.get("name"),
        "email": candidate.get("email"),
        "phone": candidate.get("phone"),
        "experience_years": candidate.get("experience_years"),
        "position": candidate.get("position"),
        "location": candidate.get("location"),
        "tech_stack": candidate.get("tech_stack"),
    }
    missing = []
    for field, value in required.items():
        if value is None or value == "" or value == []:
            missing.append(field)
    return missing


def get_collected_info(candidate: dict) -> dict:
    """
    Return a dictionary of only the fields that have been collected.
    """
    collected = {}
    fields = ["name", "email", "phone", "experience_years", "position", "location", "tech_stack"]
    for field in fields:
        value = candidate.get(field)
        if value is not None and value != "" and value != []:
            collected[field] = value
    return collected


# ──────────────────────────────────────────────
# Persistence (Mock Database)
# ──────────────────────────────────────────────
def save_candidate(candidate_data: dict) -> str:
    """
    Save the candidate's data to the local JSON mock database.
    Applies masking to sensitive fields before writing.
    
    Args:
        candidate_data: The full candidate dictionary.
        
    Returns:
        The candidate_id assigned to this record.
    """
    os.makedirs(DB_DIR, exist_ok=True)

    # Create a copy for storage with masked sensitive fields
    safe_data = candidate_data.copy()
    safe_data["status"] = "COMPLETED"
    safe_data["timestamp"] = datetime.now().isoformat()

    # Mask sensitive information for GDPR compliance — replace raw values
    if safe_data.get("email"):
        safe_data["email"] = mask_email(safe_data["email"])
    if safe_data.get("phone"):
        safe_data["phone"] = mask_phone(safe_data["phone"])

    # Load existing database
    db = _load_db()
    db.append(safe_data)

    # Write back
    with open(DB_PATH, 'w') as f:
        json.dump(db, f, indent=4, default=str)

    return safe_data["candidate_id"]


def _load_db() -> list:
    """Load the existing database file, or return an empty list."""
    try:
        with open(DB_PATH, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def get_all_candidates() -> list:
    """Retrieve all saved candidate records."""
    return _load_db()
