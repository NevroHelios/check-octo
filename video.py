import os
import base64
import cv2
import numpy as np
from groq import Groq
from urllib.request import urlopen
import tempfile
import requests
from PIL import Image
import io
import re

def is_cloudinary_url(url):
    """Check if the URL is a Cloudinary URL."""
    return 'cloudinary.com' in url or 'res.cloudinary.com' in url

def get_video_format(url):
    """Determine video format from URL or headers."""
    # First try to get format from content-type header
    try:
        response = requests.head(url)
        content_type = response.headers.get('content-type', '')
        if 'video' in content_type:
            # Extract format from content-type (e.g., 'video/mp4' -> 'mp4')
            return content_type.split('/')[-1]
    except:
        pass

    # If that fails, try to get it from the URL
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    for ext in video_extensions:
        if url.lower().endswith(ext):
            return ext[1:]  # Remove the dot

    # Default to mp4 if we can't determine the format
    return 'mp4'

def download_video(url):
    """Download video from URL (including Cloudinary) to a temporary file."""
    try:
        # For Cloudinary URLs, we might need to handle special cases
        if is_cloudinary_url(url):
            # Some Cloudinary URLs might need additional parameters
            if '?' not in url:
                url += '?fl_video'
        
        # Get video format
        video_format = get_video_format(url)
        
        # Create temporary file with appropriate extension
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{video_format}')
        
        # Download the video
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise exception for bad status codes
        
        # Write the content to temporary file
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                temp.write(chunk)
        
        temp.close()
        return temp.name
    except Exception as e:
        raise Exception(f"Failed to download video: {str(e)}")

def extract_frames(video_path, max_duration=4):
    """Extract one frame per second from the video."""
    frames = []
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise Exception("Failed to open video file")
    
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    if fps == 0:
        fps = 25  # Default to 25 fps if we can't detect it
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps
    actual_duration = min(duration, max_duration)
    
    for sec in range(int(actual_duration)):
        frame_position = sec * fps
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_position)
        ret, frame = cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame_rgb)
        else:
            break
    
    cap.release()
    return frames

def create_grid_image(frames):
    """Create a 2x2 grid from up to 4 frames."""
    frames = frames[:4]
    if not frames:
        return None
    
    # Convert frames to PIL Images
    pil_frames = [Image.fromarray(frame) for frame in frames]
    
    # Resize all frames to the same size
    size = (300, 300)
    pil_frames = [img.resize(size) for img in pil_frames]
    
    # Create a new blank image
    grid_width = size[0] * 2
    grid_height = size[1] * 2
    grid_image = Image.new('RGB', (grid_width, grid_height))
    
    # Paste frames into grid
    positions = [(0,0), (size[0],0), (0,size[1]), (size[0],size[1])]
    for i, frame in enumerate(pil_frames):
        if i < 4:
            grid_image.paste(frame, positions[i])
    
    return grid_image

def encode_image(image):
    """Convert PIL Image to base64 string."""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def analyze_garbage_disposal(video_url):
    """Analyze video frames for proper garbage disposal."""
    try:
        # Initialize Groq client
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        
        # Download video
        print("Downloading video...")
        video_path = download_video(video_url)
        
        # Extract frames
        print("Extracting frames...")
        frames = extract_frames(video_path)
        
        if not frames:
            raise ValueError("No frames could be extracted from the video")
        
        # Create grid image
        print("Creating grid image...")
        grid_image = create_grid_image(frames)
        
        if grid_image is None:
            raise ValueError("Failed to create grid image")
        
        # Encode grid image
        encoded_image = encode_image(grid_image)
        image_content = f"data:image/jpeg;base64,{encoded_image}"
        
        # Create the chat completion
        print("Analyzing frames...")
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI assistant that analyzes sequences of images to verify proper garbage disposal. Look for evidence of someone properly disposing of garbage in a bin across the frames."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "These are 4 sequential frames from a video. Does it show someone properly disposing garbage in a bin? Describe what you see and provide a YES/NO conclusion with confidence percentage."
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
            max_tokens=200
        )
        
        # Clean up temporary file
        os.unlink(video_path)
        
        return chat_completion.choices[0].message.content
        
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # Example Cloudinary URL
    video_url = "YOUR_CLOUDINARY_VIDEO_URL"
    
    result = analyze_garbage_disposal(video_url)
    print("\nAnalysis Result:")
    print(result)