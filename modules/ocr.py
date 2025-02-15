import os
import base64
import requests  # Supports HTTP/HTTPS image fetching
from groq import Groq

def extract_aadhar_number(image_path):
    try:
        # Check if image_path is a URL or a local file path.
        if image_path.startswith(('http://', 'https://')):
            response = requests.get(image_path)
            response.raise_for_status()
            image_bytes = response.content
        else:
            # On Windows, handle long file paths by adding the extended-length prefix if needed.
            if os.name == "nt":
                if not image_path.startswith("\\\\?\\"):
                    image_path = "\\\\?\\" + os.path.abspath(image_path)
            with open(image_path, "rb") as image_file:
                image_bytes = image_file.read()

        # Convert image bytes to base64
        encoded_image = base64.b64encode(image_bytes).decode('utf-8')

        # Initialize Groq client
        client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

        # Prepare prompt for OCR
        prompt = f"""
        This is a base64 encoded image of an Aadhar card: {encoded_image}
        Please extract and return only the 12-digit Aadhar number from this image.
        """

        # Get response from Groq
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.2-11b-vision-preview",
            max_tokens=100
        )

        # Extract Aadhar number from response
        aadhar_text = response.choices[0].message.content
        # Clean and validate the number (should be 12 digits)
        aadhar_number = ''.join(filter(str.isdigit, aadhar_text))
        
        if len(aadhar_number) == 12:
            return aadhar_number
        else:
            return "Invalid Aadhar number detected"

    except Exception as e:
        return f"Error processing image: {str(e)}"