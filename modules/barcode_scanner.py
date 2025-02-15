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


class BarcodeScanner:
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    def scan_barcode(self, image_data):
        """Process image to extract barcode"""
        try:
            logger.info("Starting barcode scanning")
            
            if image_data.startswith(('http://', 'https://')):
                image_content = image_data
            else:
                image_content = f"data:image/png;base64,{image_data}"

            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Read and return only the barcode value from this image. Return only the decoded value, no other text."
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

            barcode_value = chat_completion.choices[0].message.content.strip()
            logger.info(f"Barcode scanning complete: {barcode_value}")
            
            return barcode_value if len(barcode_value) >= 4 else "No valid barcode detected"

        except Exception as e:
            logger.error(f"Error in barcode scanning: {str(e)}")
            raise