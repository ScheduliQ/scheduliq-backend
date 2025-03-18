from urllib import request
from configs.envconfig import GEMINI_API_KEY
import google.generativeai as genai

def chat():
    # Read the free text from the request body.
    input_text = request.get_data(as_text=True)
    if not input_text:

        return Response("No input text provided", status=400)
    
    try:
        # Call the Gemini model using the google-generativeai library.
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(input_text)
    except Exception as e:
        return Response(f"Error during generation: {str(e)}", status=500)
    
    # Verify that a response was generated.
    if not response or not response.text:
        return Response("No response generated", status=500)
    
    # Return the generated text as plain text.
    return Response(response.text, mimetype='text/plain')
