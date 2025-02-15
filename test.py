import os
import base64
# import requests
from groq import Groq

# Access the environment variable
api_key = os.environ.get('GROQ_API_KEY')

def is_plastic_garbage(image_data):
    # Initialize Groq client
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

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
        model="llama-3.2-11b-vision-preview",
        temperature=0.0,
        max_tokens=100
    )

    response = chat_completion.choices[0].message.content.lower()
    return "yes" in response.split()[0]

if __name__ == "__main__":
    # Get input from user
    # image_input = input("Enter image path or URL: ").strip()
    # image_input = "image.png"
    # image_input = "https://www.clf.org/wp-content/uploads/2021/09/Detail-trash-can-filled-with-plastic_Shutterstock.jpg"
    image_input = "https://img.stablecog.com/insecure/1536w/aHR0cHM6Ly9iLnN0YWJsZWNvZy5jb20vZGYzMTNkM2QtZTA2MS00ZjcwLWEyMjgtNTU1OGFhODY4OTczLmpwZWc.webp"
    
    try:
        result = is_plastic_garbage(image_input)
        print(f"\nPlastic garbage detected: {'YES' if result else 'NO'}")
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("Please ensure:")
        print("- You have a valid GROQ_API_KEY environment variable")
        print("- The image path is correct or URL is accessible")
        print("- You have an active internet connection")