#!/usr/bin/env python3
"""
Daily content generation script for Capybara Party
Run this as a cron job to pre-generate daily content
"""

import os
import sys
import requests
from datetime import datetime

# Add the app directory to Python path
app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_dir)

# Import Flask app functions
from app import get_or_create_daily_content

def main():
    """Generate today's content"""
    try:
        print(f"[{datetime.now()}] Starting daily content generation...")
        
        # This will create new content if it doesn't exist
        content = get_or_create_daily_content()
        
        if content and content.get('image_filename'):
            print(f"✅ Successfully generated daily content:")
            print(f"   Image: {content['image_filename']}")
            print(f"   Quote: {content['quote'][:50]}...")
        else:
            print("⚠️ Content generation completed with fallback content")
            
    except Exception as e:
        print(f"❌ Error generating daily content: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
