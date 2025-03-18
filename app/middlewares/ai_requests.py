import requests
from configs.envconfig import GEMINI_API_KEY
def update_shift_priorities(employee_data):
    # Extract the necessary data
    constraints_text = employee_data.get("constraints", "")
    availability = employee_data.get("availability", [])
    
    # Build a prompt that describes the situation and asks for updated priorities
    prompt = (
        f"Given the following employee availability data: {availability}\n"
        f"And the employee constraints: '{constraints_text}',\n"
        "update the shift priorities such that the shifts the employee prefers "
        "receive a higher priority on a scale of 1 to 10 (where 10 is highest). "
        "Return the updated availability array in valid JSON format."
    )
    
    # Define the API endpoint and headers
    api_url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}'  # Replace with the correct endpoint
    headers = {
        "Content-Type": "application/json"
    }
    
    # Prepare the payload with the prompt and additional parameters
    payload = {
        "request_type": "generate_text",
        "task": "Update employee shift availability priorities based on constraints and contextual mappings",
        "parameters": {
            "prompt": "You are provided with an employee's shift availability in JSON format, along with"
            " the employee's free-text constraints. Each availability object includes a 'shift' and 'day'"
            " index with an associated 'priority' (on a scale of 1 to 10, where 10 indicates a strong preference). "
            "In addition, you are given the context that maps these indices to human-readable names. For example:"
            "\n\nshift_names: ['morning', 'evening', 'night']\nwork_days: ['Sunday', 'Friday']\n\nThis means that shift 0 is "
            "'morning', shift 1 is 'evening', and so on; similarly, day 0 is 'Sunday' and day 1 is 'Friday'.\n\nGiven the "
            "following input:\n\nAvailability: [\n  {\"shift\": 0, \"day\": 0, \"priority\": 10},\n  {\"shift\": 1, \"day\": "
            "0, \"priority\": 10},\n  {\"shift\": 2, \"day\": 0, \"priority\": 10},\n  {\"shift\": 0, \"day\": 1, \"priority\":"
            " 10},\n  {\"shift\": 1, \"day\": 1, \"priority\": 10}\n]\nConstraints: 'I prefer working morning shifts on Sunday"
            " and dislike evening shifts on Friday.'\n\nAdjust the 'priority' values so that shifts matching the employee's "
            "preferences are given a higher priority (closer to 10) and less preferred shifts are assigned a lower priority "
            "(closer to 1). Return only a valid JSON array containing the updated availability objects in the same format.",
            "max_tokens": 150,
            "temperature": 0.7
        },
        "context": {
            "example_availability": [
            { "shift": 0, "day": 0, "priority": 10 },
            { "shift": 1, "day": 0, "priority": 10 },
            { "shift": 2, "day": 0, "priority": 10 },
            { "shift": 0, "day": 1, "priority": 10 },
            { "shift": 1, "day": 1, "priority": 10 }
            ],
            "example_constraints": "I prefer working morning shifts on Sunday and dislike evening shifts on Friday.",
            "shift_names": ["morning", "evening", "night"],
            "work_days": ["Sunday", "Friday"]
        },
        "response_format": "json"
        }

    
    # Make the POST request to the Gemini API
    response = requests.post(api_url, json=payload, headers=headers)
    
    # Check for a successful response
    if response.status_code == 200:
        result = response.json()
        # Assume the response contains the updated availability under a key (e.g., "result")
        updated_availability = result.get("result")
        return updated_availability
    else:
        raise Exception(f"Error from Gemini API: {response.text}")
