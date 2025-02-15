import os
import base64
# import requests
from groq import Groq

# Access the environment variable
api_key = os.environ.get('GROQ_API_KEY')

def is_plastic_garbage(image_data):
    # Initialize Groq client
    client = Groq(api_key=api_key)

    # Determine if input is base64 or URL
    if image_data.startswith(('http://', 'https://')):
        # Handle URL case
        image_content = image_data
    else:
        # Handle base64 case - assume it's a PNG image
        image_content = f"data:image/png;base64,{image_data}"

    # Rest of the function remains the same
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Is this image showing plastic garbage? Respond only with 'YES' or 'NO' followed by a confidence percentage."
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

    response = chat_completion.choices[0].message.content.lower()
    return "yes" in response.split()[0]

