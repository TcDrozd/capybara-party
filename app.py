import os
import requests
import json
import base64
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
from PIL import Image
from io import BytesIO
import hashlib
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'capybara-secret')

# Configuration
A1111_API_URL = os.environ.get('A1111_API_URL', '')
OLLAMA_API_URL = os.environ.get('OLLAMA_API_URL', '')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', '')

# Image storage path
IMAGES_DIR = os.path.join('static', 'images', 'daily')
os.makedirs(IMAGES_DIR, exist_ok=True)

def get_daily_filename():
    """Generate filename based on current date"""
    today = datetime.now().strftime('%Y-%m-%d')
    return f"capybara_{today}.png"

def get_daily_json_filename():
    """Generate JSON filename for storing daily data"""
    today = datetime.now().strftime('%Y-%m-%d')
    return f"daily_{today}.json"

def capybara_prompts():
    """Random capybara-themed prompts"""
    prompts = [
        "peaceful capybara sitting by a serene lake at sunset, anime style, detailed, beautiful lighting",
        "cute capybara family relaxing in hot springs, watercolor style, warm colors",
        "zen capybara meditating under cherry blossoms, japanese art style, tranquil atmosphere",
        "capybara wearing a tiny hat sitting in a field of flowers, studio ghibli style",
        "capybara and bird friends having a picnic, wholesome, bright colors, illustration",
        "capybara floating on a lily pad in a peaceful pond, dreamy, soft lighting",
        "capybara reading a book under a tree, cozy atmosphere, golden hour",
        "capybara with a gentle smile surrounded by butterflies, magical realism",
        "capybara astronaut floating in space with stars and planets in the background, whimsical digital art",
        "majestic capybara standing on a mossy rock with waterfalls behind it, fantasy art, glowing atmosphere",
        "tiny capybara sipping tea at a wooden table, cozy cottagecore illustration",
        "capybara riding a bicycle through a sunflower field, pastel colors, cheerful vibes",
        "steampunk capybara with goggles and gears, Victorian aesthetic, intricate details",
        "capybara swimming underwater with koi fish, dreamy watercolor",
        "capybara knight in shining armor, medieval fantasy illustration, heroic pose",
        "capybara lying in a hammock between two palm trees, tropical paradise, soft pastel sunset",
        "capybara in a wizard hat casting spells, glowing runes, magical realism",
        "capybara surfing a big wave, energetic, bright and colorful comic art",
        "capybara chef in a tiny kitchen making pancakes, warm colors, detailed illustration",
        "capybara and penguin friends building a snowman, winter wonderland, playful style",
        "capybara adventurer with backpack exploring ancient ruins, cinematic lighting",
        "capybara DJ mixing records at a party, neon lights, vaporwave aesthetic",
        "capybara napping on a bookshelf surrounded by stacks of books, cozy reading nook",
        "cyberpunk capybara with neon highlights, futuristic city background, glowing reflections",
        "capybara in a meadow full of fireflies at twilight, magical glow, soft colors",
        "capybara and turtle sharing an umbrella in the rain, gentle watercolor style",
        "capybara samurai under a red maple tree, Japanese ink painting",
        "capybara sailing on a paper boat down a quiet river, dreamlike atmosphere"
    ]
    import random
    return random.choice(prompts)

def generate_image():
    """Generate image using AUTOMATIC1111 API"""
    try:
        prompt = capybara_prompts()
        
        payload = {
            "prompt": prompt,
            "negative_prompt": "ugly, blurry, low quality, distorted, bad anatomy",
            "steps": 25,
            "width": 768,
            "height": 768,
            "cfg_scale": 7,
            "sampler_name": "Euler a",
            "seed": -1  # Random seed
        }
        
        response = requests.post(
            f"{A1111_API_URL}/sdapi/v1/txt2img",
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            # Decode base64 image
            image_data = base64.b64decode(result['images'][0])
            
            # Save image
            filename = get_daily_filename()
            filepath = os.path.join(IMAGES_DIR, filename)
            
            with open(filepath, 'wb') as f:
                f.write(image_data)
            
            return filename, prompt
        else:
            print(f"Image generation failed: {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"Error generating image: {e}")
        return None, None

def generate_quote():
    """Generate inspirational quote using Ollama"""
    try:
        prompt = """You are a wise, gentle voice that speaks only in short, zen-like inspirational quotes. 
The quotes should feel like they come from a calm, grounded creature who values peace, stillness, and simple joys. 
Do not add commentary or explanation. 
Output must be only the quote text itself, nothing else.

Examples:
- "The river does not hurry, yet it carries everything forward."
- "In stillness, the heart remembers what it already knows."
- "Joy hides in the smallest shadows of the day."

Now generate one new quote in the same style. Keep it to 1???2 sentences."""
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.8,
                "max_tokens": 100
            }
        }
        
        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            quote = result['response'].strip()
            # Clean up the quote
            if quote.startswith('"') and quote.endswith('"'):
                quote = quote[1:-1]
            return quote
        else:
            print(f"Quote generation failed: {response.status_code}")
            return "Find peace in the simple moments of today."
            
    except Exception as e:
        print(f"Error generating quote: {e}")
        return "Find peace in the simple moments of today."

def get_or_create_daily_content():
    """Get today's content or create new if doesn't exist"""
    json_filename = get_daily_json_filename()
    json_filepath = os.path.join(IMAGES_DIR, json_filename)
    
    # Check if today's content already exists
    if os.path.exists(json_filepath):
        with open(json_filepath, 'r') as f:
            return json.load(f)
    
    # Generate new content
    print("Generating new daily content...")
    image_filename, image_prompt = generate_image()
    quote = generate_quote()
    
    if image_filename:
        content = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "image_filename": image_filename,
            "image_prompt": image_prompt,
            "quote": quote,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save to JSON file
        with open(json_filepath, 'w') as f:
            json.dump(content, f, indent=2)
        
        return content
    else:
        # Fallback content if generation fails
        return {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "image_filename": None,
            "image_prompt": None,
            "quote": "Sometimes the most productive thing you can do is relax.",
            "timestamp": datetime.now().isoformat()
        }

@app.route('/')
def home():
    """Main page"""
    content = get_or_create_daily_content()
    return render_template('index.html', content=content)

@app.route('/api/refresh', methods=['GET', 'POST'])
def refresh():
    """Force refresh today's content"""
    # Delete existing files for today
    json_filename = get_daily_json_filename()
    json_filepath = os.path.join(IMAGES_DIR, json_filename)
    
    image_filename = get_daily_filename()
    image_filepath = os.path.join(IMAGES_DIR, image_filename)
    
    # Remove existing files
    for filepath in [json_filepath, image_filepath]:
        if os.path.exists(filepath):
            os.remove(filepath)
    
    # Generate new content
    content = get_or_create_daily_content()
    return jsonify(content)

@app.route('/api/status')
def status():
    """Check API status"""
    try:
        # Check A1111
        a1111_response = requests.get(f"{A1111_API_URL}/sdapi/v1/progress", timeout=5)
        a1111_status = a1111_response.status_code == 200
    except:
        a1111_status = False
    
    try:
        # Check Ollama
        ollama_response = requests.get(f"{OLLAMA_API_URL}/api/version", timeout=5)
        ollama_status = ollama_response.status_code == 200
    except:
        ollama_status = False
    
    return jsonify({
        "a1111": a1111_status,
        "ollama": ollama_status,
        "flask": True
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5090, debug=False)
