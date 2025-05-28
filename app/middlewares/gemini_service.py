import json
import re
from urllib import request
from configs.envconfig import GEMINI_API_KEY
import google.generativeai as genai
from models.manager_settings_model import get_manager_settings
from models.constraints_model import get_all_constraints

# all_constraints = get_all_constraints()
all_constraints = list(get_all_constraints())

manager_settings = get_manager_settings()
genai.configure(api_key=GEMINI_API_KEY)

def build_prompt_data(manager_settings, constraints_docs):
    """
    Builds a summary of data for the prompt based on manager settings and employees' constraints.
    
    Parameters:
        manager_settings (dict): A dictionary of manager settings.
            (Expected keys: shifts_per_day, shift_names, roles_per_shift, max_consecutive_shifts,
             role_importance, work_days, required_shifts)
        constraints_docs (list): A list of constraint documents, each representing an employee.
            Each document should include keys like first_name, last_name, availability, roles, and constraints.
    
    Returns:
        str: A JSON string with a compact summary of the data.
    """
    # List of keys to include from manager settings (excluding uid, _id, shift_colors, last_updated, and min_max_employees_per_shift)
    keys_to_include = [
        "shifts_per_day",
        "shift_names",
        "roles_per_shift",
        "max_consecutive_shifts",
        "role_importance",
        "work_days",
        "required_shifts"
    ]
    summary_manager_settings = {key: manager_settings[key] for key in keys_to_include if key in manager_settings}
    
    # Get mapping lists from manager settings
    work_days = manager_settings.get("work_days", [])
    shift_names = manager_settings.get("shift_names", [])
    
    employees_summary = []
    # Process each constraints document
    for doc in constraints_docs:
        # Create a summary entry for the employee
        employee_entry = {
            "first_name": doc.get("first_name", ""),
            "last_name": doc.get("last_name", ""),
            "roles": doc.get("roles", []),
        }
        
        # Process and transform the availability list:
        avail_list = doc.get("availability", [])
        transformed_avail = []
        for avail in avail_list:
            shift_index = avail.get("shift")
            day_index = avail.get("day")
            # Convert numeric indices to names using the manager settings lists.
            # If index is out of range, fallback to a placeholder.
            shift_name = shift_names[shift_index] if isinstance(shift_index, int) and shift_index < len(shift_names) else f"shift_{shift_index}"
            day_name = work_days[day_index] if isinstance(day_index, int) and day_index < len(work_days) else f"day_{day_index}"
            transformed_avail.append({
                "shift": shift_name,
                "day": day_name,
                "priority": avail.get("priority")
            })
        employee_entry["availability"] = transformed_avail
        employees_summary.append(employee_entry)
    
    # Sort employees by first_name and last_name to maintain a consistent order
    employees_summary.sort(key=lambda x: (x["first_name"], x["last_name"]))
    
    # Create the final summary structure
    final_summary = {
        "manager_settings": summary_manager_settings,
        "employees": employees_summary
    }
    print("Final summary data:", final_summary)
    print("allllll",list(constraints_docs))
    # Dump the summary to a compact JSON string (separators remove unnecessary whitespace)
    return json.dumps(final_summary, ensure_ascii=False, separators=(",", ":"))

def validate_availability_format(data):
    """
    Validates that the availability data is in the correct format.
    
    Parameters:
        data (list): List of availability entries
        
    Returns:
        bool: True if valid, raises ValueError if invalid
        
    Raises:
        ValueError: If the data format is invalid
    """
    if not isinstance(data, list):
        raise ValueError("Data must be a list")
        
    for entry in data:
        if not isinstance(entry, dict):
            raise ValueError("Each entry must be a dictionary")
            
        required_keys = {"shift", "day", "priority"}
        if not all(key in entry for key in required_keys):
            raise ValueError("Each entry must contain 'shift', 'day', and 'priority'")
            
        if not isinstance(entry["shift"], int) or not isinstance(entry["day"], int):
            raise ValueError("'shift' and 'day' must be integers")
            
        if not isinstance(entry["priority"], int) or entry["priority"] < 1 or entry["priority"] > 10:
            raise ValueError("'priority' must be an integer between 1 and 10")
    
    return True

def parse_availability(response_str):
    """
    Extracts JSON data from a string that might contain markdown code fences.
    
    Parameters:
        response_str (str): The response string containing JSON, e.g.:
            "```json\n[{"shift": 0, "day": 0, "priority": 10}, ...]\n```"
            
    Returns:
        list: A list of dictionaries parsed from the JSON content.
    """
    # Remove markdown code fences if they exist
    # This regex removes leading "```json" and trailing "```" (with optional spaces)
    cleaned = re.sub(r"^```json\s*", "", response_str)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    
    # Parse the cleaned JSON string
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {str(e)}")
    
    # Validate the format
    validate_availability_format(data)
    
    return data

def priorityByAI(constraints, availability):
    # Set the model to "gemini-1.5-flash"
    MODEL = "gemini-1.5-flash"
    model = genai.GenerativeModel(MODEL)
    # print("Initialized model:", model)
    
    # Read the base prompt from file.
    prompt_file_path = "app/middlewares/prompts/priority.txt"
    try:
        with open(prompt_file_path, "r", encoding="utf-8") as f:
            base_prompt = f.read()
    except Exception as e:
        raise ValueError(f"Failed to read prompt file: {str(e)}")
    
    # Append the constraints and availability to the base prompt.
    # For availability, we serialize it as JSON to preserve its structure.
    additional_text = (
        "\n\n=== PARAMETERS ===\n"
        "Constraints:\n" + constraints +
        "\n\nAvailability:\n" + str(availability)+
        "\n\nShift Names:\n" + str(manager_settings["shift_names"]) +
        "\n\nWork Days:\n" + str(manager_settings["work_days"])
    )
    
    # Combine the base prompt with the additional parameters.
    input_text = base_prompt + additional_text
    # print("Final prompt sent to model:\n", input_text)
    
    # Generate content using the combined prompt.
    response = model.generate_content(input_text)
    # print("Raw response received:", response)
    
    # Verify that a valid response was generated.
    if not response or not response.text:
        raise ValueError("No response generated by the Gemini API.")
    
    return parse_availability(response.text)

conversation_history = []

def chat_with_manager(manager_message, first_message):
    """
    This function interacts with Gemini as a chatbot and maintains conversation context.
    It reads a base chat prompt, optionally includes system information (for the first message),
    appends the conversation history, and then the manager's new message.
    
    Parameters:
        manager_message (str): The free-text message from the manager.
        first_message (bool): True if this is the first message in the conversation.
    
    Returns:
        str: The chatbot's response.
    """
    global conversation_history

    MODEL = "gemini-1.5-flash"
    model = genai.GenerativeModel(MODEL)
    
    # Read base prompt from file
    chat_prompt_file = "app/middlewares/prompts/chat_bot.txt"
    try:
        with open(chat_prompt_file, "r", encoding="utf-8") as f:
            base_prompt = f.read()
    except Exception as e:
        raise ValueError(f"Failed to read chat prompt file: {str(e)}")
    
    # If it's the first message, reset the conversation history and include system info.
    if first_message:
        conversation_history = []  # Clear previous history
        # Build the prompt with system information from manager settings and all constraints.
        initial_context = base_prompt + "\n\nSystem information: " + build_prompt_data(manager_settings, all_constraints)
        conversation_history.append("System: " + initial_context)
    
    # Append the new manager message to conversation history.
    conversation_history.append("Manager: " + manager_message)
    
    # Build the full conversation context by joining all messages.
    full_context = "\n".join(conversation_history)
    
    # The final prompt sent to Gemini includes the entire conversation history.
    input_text = full_context
    
    response = model.generate_content(input_text)
    if not response or not response.text:
        raise ValueError("No response generated by the Gemini API.")
    
    # Append the chatbot's reply to the conversation history.
    conversation_history.append("Chatbot: " + response.text)
    # print("Conversation history:", conversation_history)
    
    return response.text
