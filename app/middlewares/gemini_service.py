import json
import re
from urllib import request
from configs.envconfig import GEMINI_API_KEY
import google.generativeai as genai
from models.manager_settings_model import get_manager_settings


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
    
    return data


days=[
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday"
  ]
shifts= [
    "morning",
    "evening",
    "night"
  ]
manager_settings = get_manager_settings()
genai.configure(api_key=GEMINI_API_KEY)
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
        # "\n\nShift Names:\n" + str(shifts)+
        # "\n\nWork Days:\n" + str(days)
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
