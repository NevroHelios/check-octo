import os
import base64
import requests  # Supports HTTP/HTTPS image fetching
from groq import Groq

def extract_aadhar_number(image_data):
    try:
            # Determine if input is base64 or URL
        if image_data.startswith(('http://', 'https://')):
            # Handle URL case
            image_content = image_data
        else:
            # Handle base64 case - assume it's a PNG image
            image_content = f"data:image/png;base64,{image_data}"

        # Initialize Groq client
        client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

        # Get response from Groq using the chat_completion pattern
        chat_completion = client.chat.completions.create(
            messages=[
            {
                "role": "user",
                "content": [
                {
                    "type": "text",
                    "text": "Please extract and return only the 12-digit Aadhar number from this image. If a valid number is detected return that number only. If not return Unknown."
                },
                {
                    "type": "image_url",
                    "image_url": {"url": image_content}
                }
                ]
            }
            ],
            model="llama-3.2-90b-vision-preview",
            temperature=0.0,
            max_tokens=100
        )

        # Extract Aadhar number from response
        aadhar_text = chat_completion.choices[0].message.content
        # Clean and validate the number (should be 12 digits)
        aadhar_number = ''.join(filter(str.isdigit, aadhar_text))
        
        if len(aadhar_number) == 12:
            return aadhar_number
        else:
            return "Invalid Aadhar number detected"

    except Exception as e:
        return f"Error processing image: {str(e)}"