import cv2
import numpy as np
import base64
from groq import Groq
import pytesseract
import logging
import os
from PIL import Image
import io
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AadharCardProcessor:
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
    def _decode_base64(self, base64_string):
        """Decode base64 string to OpenCV image"""
        try:
            # Remove header if present
            if 'base64,' in base64_string:
                base64_string = base64_string.split('base64,')[1]
            
            img_bytes = base64.b64decode(base64_string)
            nparr = np.frombuffer(img_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return image
        except Exception as e:
            logger.error(f"Error decoding base64 image: {str(e)}")
            return None

    def _preprocess_image(self, image):
        """Preprocess image for better OCR results"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply bilateral filter
            denoised = cv2.bilateralFilter(gray, 9, 75, 75)
            
            # Apply CLAHE
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(denoised)
            
            # Adaptive thresholding
            threshold = cv2.adaptiveThreshold(
                enhanced, 255, 
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            return threshold
        except Exception as e:
            logger.error(f"Error in preprocessing: {str(e)}")
            return None

    def _validate_aadhar_number(self, number):
        """Validate the extracted Aadhar number"""
        number = re.sub(r'\D', '', number)
        return len(number) == 12

    def _process_with_groq(self, image_content):
        """Process image using Groq API"""
        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract and return only the 12-digit Aadhar number from this image. Return only the number, no other text."
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

            aadhar_text = chat_completion.choices[0].message.content
            aadhar_number = ''.join(filter(str.isdigit, aadhar_text))
            
            if self._validate_aadhar_number(aadhar_number):
                return aadhar_number
            return "Invalid Aadhar number detected"
        except Exception as e:
            logger.error(f"Error in Groq API processing: {str(e)}")
            return None

    def extract_aadhar_number(self, image_data):
        """Main function to extract Aadhar number"""
        try:
            logger.info("Starting Aadhar number extraction")
            
            # Handle URL case
            if image_data.startswith(('http://', 'https://')):
                logger.info("Processing URL image")
                return self._process_with_groq(image_data)

            # Decode base64 image
            image = self._decode_base64(image_data)
            if image is None:
                raise ValueError("Invalid image data")

            # Preprocess image
            preprocessed = self._preprocess_image(image)
            if preprocessed is None:
                raise ValueError("Image preprocessing failed")

            # Try OCR
            text = pytesseract.image_to_string(
                preprocessed, 
                config='--psm 7 -c tessedit_char_whitelist=0123456789'
            )
            
            # Clean and validate number
            aadhar_number = ''.join(filter(str.isdigit, text))
            if self._validate_aadhar_number(aadhar_number):
                logger.info("Successfully extracted Aadhar number using OCR")
                return aadhar_number

            # Fallback to Groq API
            logger.info("OCR failed, falling back to Groq API")
            encoded_image = base64.b64encode(cv2.imencode('.png', image)[1]).decode('utf-8')
            result = self._process_with_groq(f"data:image/png;base64,{encoded_image}")
            
            if result:
                return result
            return "No valid Aadhar number detected"

        except Exception as e:
            logger.error(f"Error in Aadhar number extraction: {str(e)}")
            raise
