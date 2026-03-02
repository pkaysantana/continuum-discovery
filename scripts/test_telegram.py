#!/usr/bin/env python3
"""
Quick Telegram Bot Test Script
Tests TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID from .env file
"""

import os
import sys
import requests
import json

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] Loaded .env file successfully")
except ImportError:
    print("[ERROR] python-dotenv not installed")
    print("Install with: pip install python-dotenv")
    sys.exit(1)

def test_telegram_bot():
    """Test Telegram bot configuration"""

    # Get credentials from environment
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

    # Check for both singular and plural chat ID variables
    chat_id = os.getenv('TELEGRAM_CHAT_ID')  # Single chat ID
    chat_ids = os.getenv('TELEGRAM_CHAT_IDS')  # Multiple chat IDs (comma-separated)

    # Use the first available chat ID for testing
    if chat_ids:
        chat_id = chat_ids.split(',')[0].strip()
    elif not chat_id:
        chat_id = None

    print(f"\n[CONFIG] TELEGRAM CONFIGURATION CHECK:")
    print(f"Bot Token: {'[OK] Set' if bot_token else '[ERROR] Missing'}")
    print(f"Chat ID: {'[OK] Set (' + (chat_ids or chat_id or 'None') + ')' if chat_id else '[ERROR] Missing'}")

    if not bot_token:
        print("\n[ERROR] TELEGRAM_BOT_TOKEN not found in .env file")
        print("Add: TELEGRAM_BOT_TOKEN=your_bot_token_here")
        return False

    if not chat_id:
        print("\n[ERROR] No chat ID found in .env file")
        print("Add either:")
        print("  TELEGRAM_CHAT_ID=your_chat_id_here")
        print("  OR")
        print("  TELEGRAM_CHAT_IDS=your_chat_id_here,another_id")
        return False

    # Prepare test message
    test_message = "🌍 SDG 3 Alert Test: Continuum Discovery Swarm is online and EarthWatcherAgent is monitoring."

    # Telegram API URL
    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    # Payload for the request
    payload = {
        'chat_id': chat_id,
        'text': test_message,
        'parse_mode': 'HTML'
    }

    print(f"\n[SEND] SENDING TEST MESSAGE:")
    print(f"API URL: {api_url}")
    print(f"Chat ID: {chat_id}")
    print(f"Message: {test_message}")
    print(f"\n[REQUEST] Making request...")

    try:
        # Send the request
        response = requests.post(api_url, json=payload, timeout=10)

        print(f"\n[STATUS] RESPONSE STATUS: {response.status_code}")

        # Parse JSON response
        response_json = response.json()

        print(f"\n[JSON] JSON RESPONSE:")
        print(json.dumps(response_json, indent=2))

        # Check if successful
        if response.status_code == 200 and response_json.get('ok'):
            print(f"\n[OK] SUCCESS: Message sent successfully!")
            print(f"Message ID: {response_json['result']['message_id']}")
            print(f"Chat: {response_json['result']['chat'].get('title', 'Direct Message')}")
            return True
        else:
            print(f"\n[ERROR] FAILED: {response_json.get('description', 'Unknown error')}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] REQUEST ERROR: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"\n[ERROR] JSON PARSE ERROR: {e}")
        print(f"Raw response: {response.text}")
        return False
    except Exception as e:
        print(f"\n[ERROR] UNEXPECTED ERROR: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TELEGRAM BOT TEST - CONTINUUM DISCOVERY SWARM")
    print("=" * 60)

    success = test_telegram_bot()

    if success:
        print(f"\n[SUCCESS] TELEGRAM INTEGRATION READY!")
        print(f"Your OpenClaw Multi-Agent Swarm can now send FLock SDG 3 alerts!")
    else:
        print(f"\n[WARNING]  TELEGRAM SETUP NEEDS ATTENTION")
        print(f"Fix the issues above before running the full swarm")

    print(f"\nNext step: python main_swarm.py")