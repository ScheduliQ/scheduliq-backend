import os
import socket
import json
import re
from urllib import request as urllib_request
import requests
from requests.adapters import HTTPAdapter

from configs.envconfig import GEMINI_API_KEY
from models.manager_settings_model import get_manager_settings
from models.constraints_model import get_all_constraints
from google import genai

# --- IPv6Adapter for requests (unchanged) ---
class IPv6Adapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        kwargs.setdefault('socket_options', []).append(
            (socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
        )
        return super().init_poolmanager(*args, **kwargs)

_orig_sess_init = requests.Session.__init__
def _sess_init(self, *args, **kwargs):
    _orig_sess_init(self, *args, **kwargs)
    self.mount("https://", IPv6Adapter())
    self.mount("http://", IPv6Adapter())

requests.Session.__init__ = _sess_init
# ---------------------------------------------------------------

# load constraints and settings
all_constraints = list(get_all_constraints())
manager_settings = get_manager_settings()

# --- Initialize Gen AI SDK client with print-based logging ---
try:
    client = genai.Client(
        vertexai=True,
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION")
    )
    print("✅ Connected to Gemini (Vertex AI) successfully.")
except Exception as e:
    print(f"❌ Failed to initialize Gemini client: {e}")
    raise

def build_prompt_data(manager_settings, constraints_docs):
    """
    Summarize manager settings & employee constraints into a compact JSON payload.
    """
    keys_to_include = [
        "shifts_per_day", "shift_names", "roles_per_shift",
        "max_consecutive_shifts", "role_importance",
        "work_days", "required_shifts"
    ]
    summary_manager_settings = {
        key: manager_settings[key]
        for key in keys_to_include
        if key in manager_settings
    }

    work_days = manager_settings.get("work_days", [])
    shift_names = manager_settings.get("shift_names", [])

    employees_summary = []
    for doc in constraints_docs:
        entry = {
            "first_name": doc.get("first_name", ""),
            "last_name":  doc.get("last_name", ""),
            "roles":      doc.get("roles", []),
        }
        transformed = []
        for avail in doc.get("availability", []):
            si, di = avail.get("shift"), avail.get("day")
            shift_name = (
                shift_names[si]
                if isinstance(si, int) and si < len(shift_names)
                else f"shift_{si}"
            )
            day_name = (
                work_days[di]
                if isinstance(di, int) and di < len(work_days)
                else f"day_{di}"
            )
            transformed.append({
                "shift":    shift_name,
                "day":      day_name,
                "priority": avail.get("priority")
            })
        entry["availability"] = transformed
        employees_summary.append(entry)

    employees_summary.sort(key=lambda x: (x["first_name"], x["last_name"]))

    final = {
        "manager_settings": summary_manager_settings,
        "employees":        employees_summary
    }
    print(f"🔧 Built prompt data: {final}")
    return json.dumps(final, ensure_ascii=False, separators=(",", ":"))

def validate_availability_format(data):
    """
    Ensure availability is a list of dicts with integer shift/day and priority 1–10.
    """
    if not isinstance(data, list):
        raise ValueError("Data must be a list")
    for entry in data:
        if not isinstance(entry, dict):
            raise ValueError("Each entry must be a dictionary")
        for key in ("shift", "day", "priority"):
            if key not in entry:
                raise ValueError(f"Each entry must contain '{key}'")
        if not isinstance(entry["shift"], int) or not isinstance(entry["day"], int):
            raise ValueError("'shift' and 'day' must be integers")
        p = entry["priority"]
        if not isinstance(p, int) or not (1 <= p <= 10):
            raise ValueError("'priority' must be an integer between 1 and 10")
    return True

def parse_availability(response_str):
    """
    Strip ```json fences, parse JSON, and validate format.
    """
    cleaned = re.sub(r"^```json\s*", "", response_str)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")
    validate_availability_format(data)
    return data

def priorityByAI(constraints, availability):
    """
    Call Gemini via Vertex AI to rank/prioritize shifts.
    """
    prompt_path = "app/middlewares/prompts/priority.txt"
    with open(prompt_path, "r", encoding="utf-8") as f:
        base_prompt = f.read()

    full_prompt = (
        base_prompt
        + "\n\n=== PARAMETERS ===\n"
        + "Constraints:\n" + constraints
        + "\n\nAvailability:\n" + json.dumps(availability, ensure_ascii=False)
        + "\n\nShift Names:\n"   + json.dumps(manager_settings["shift_names"], ensure_ascii=False)
        + "\n\nWork Days:\n"     + json.dumps(manager_settings["work_days"], ensure_ascii=False)
    )

    print("➡️ Sending generate_content request to Gemini for priorityByAI")
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=full_prompt
    )
    print("⬅️ Received response from Gemini for priorityByAI")

    if not response or not response.text:
        print("❌ Empty response from Gemini in priorityByAI")
        raise ValueError("No response generated by the Gemini API.")
    return parse_availability(response.text)

conversation_history = []

def chat_with_manager(manager_message, first_message):
    """
    Maintain context and chat with Gemini as a conversational bot.
    """
    chat_prompt_file = "app/middlewares/prompts/chat_bot.txt"
    with open(chat_prompt_file, "r", encoding="utf-8") as f:
        base_prompt = f.read()

    if first_message:
        conversation_history.clear()
        system_info = build_prompt_data(manager_settings, all_constraints)
        conversation_history.append("System: " + base_prompt + "\n\nSystem information: " + system_info)

    conversation_history.append("Manager: " + manager_message)
    full_context = "\n".join(conversation_history)

    print("➡️ Sending generate_content request to Gemini for chat_with_manager")
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=full_context
    )
    print("⬅️ Received response from Gemini for chat_with_manager")

    if not response or not response.text:
        print("❌ Empty response from Gemini in chat_with_manager")
        raise ValueError("No response generated by the Gemini API.")

    reply = response.text
    conversation_history.append("Chatbot: " + reply)
    return reply