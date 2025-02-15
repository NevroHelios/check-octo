# # modules/scanner.py
# import cv2
# import numpy as np
# import base64
# from groq import Groq
# import logging
# import os
# from pyzbar.pyzbar import decode
# from PIL import Image
# import io

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# class CodeScanner:
#     def __init__(self):
#         self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
#     def _decode_base64(self, base64_string):
#         """Decode base64 string to OpenCV image"""
#         try:
#             # Remove header if present
#             if 'base64,' in base64_string:
#                 base64_string = base64_string.split('base64,')[1]
            
#             img_bytes = base64.b64decode(base64_string)
#             nparr = np.frombuffer(img_bytes, np.uint8)
#             image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#             return image
#         except Exception as e:
#             logger.error(f"Error decoding base64 image: {str(e)}")
#             return None

#     def _preprocess_image(self, image):
#         """Preprocess image for better code detection"""
#         try:
#             # Convert to grayscale
#             gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
#             # Denoise
#             denoised = cv2.fastNlMeansDenoising(gray)
            
#             # Enhance contrast
#             clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
#             enhanced = clahe.apply(denoised)
            
#             # Sharpen
#             kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
#             sharpened = cv2.filter2D(enhanced, -1, kernel)
            
#             return sharpened
#         except Exception as e:
#             logger.error(f"Error in preprocessing: {str(e)}")
#             return None

#     def _local_code_scan(self, image):
#         """Attempt to scan codes using local processing"""
#         try:
#             # Preprocess image
#             processed = self._preprocess_image(image)
#             if processed is None:
#                 return None

#             # Convert to PIL Image for zbar
#             pil_image = Image.fromarray(processed)
            
#             # Scan for codes
#             codes = decode(pil_image)
            
#             if codes:
#                 results = []
#                 for code in codes:
#                     result = {
#                         'type': code.type,
#                         'data': code.data.decode('utf-8'),
#                         'rect': {
#                             'left': code.rect.left,
#                             'top': code.rect.top,
#                             'width': code.rect.width,
#                             'height': code.rect.height
#                         }
#                     }
#                     results.append(result)
#                 return results
            
#             return None
#         except Exception as e:
#             logger.error(f"Error in local code scanning: {str(e)}")
#             return None

#     def _process_with_groq(self, image_content):
#         """Process image using Groq API as fallback"""
#         try:
#             chat_completion = self.groq_client.chat.completions.create(
#                 messages=[
#                     {
#                         "role": "user",
#                         "content": [
#                             {
#                                 "type": "text",
#                                 "text": "Read and return any QR codes or barcodes from this image. Return only the decoded values separated by newlines, no other text."
#                             },
#                             {
#                                 "type": "image_url",
#                                 "image_url": {"url": image_content}
#                             }
#                         ]
#                     }
#                 ],
#                 model="llama-3.2-90b-vision-preview",
#                 temperature=0.0,
#                 max_tokens=100
#             )

#             code_text = chat_completion.choices[0].message.content.strip()
#             if code_text and code_text.lower() != "no codes detected":
#                 return [{'type': 'unknown', 'data': value.strip()} 
#                         for value in code_text.split('\n') if value.strip()]
#             return None
#         except Exception as e:
#             logger.error(f"Error in Groq API processing: {str(e)}")
#             return None

#     def scan_codes(self, image_data):
#         """Main function to scan for QR codes and barcodes"""
#         try:
#             logger.info("Starting code scanning")
            
#             # Handle URL case
#             if image_data.startswith(('http://', 'https://')):
#                 logger.info("Processing URL image")
#                 results = self._process_with_groq(image_data)
#                 return {'codes': results} if results else {'codes': []}

#             # Decode base64 image
#             image = self._decode_base64(image_data)
#             if image is None:
#                 raise ValueError("Invalid image data")

#             # Try local processing first
#             results = self._local_code_scan(image)
            
#             if results:
#                 logger.info("Successfully scanned codes using local processing")
#                 return {'codes': results}

#             # Fallback to Groq API
#             logger.info("Local processing failed, falling back to Groq API")
#             encoded_image = base64.b64encode(cv2.imencode('.png', image)[1]).decode('utf-8')
#             results = self._process_with_groq(f"data:image/png;base64,{encoded_image}")
            
#             return {'codes': results if results else []}

#         except Exception as e:
#             logger.error(f"Error in code scanning: {str(e)}")
#             raise