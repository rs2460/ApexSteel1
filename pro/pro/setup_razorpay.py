#!/usr/bin/env python
"""
Razorpay Setup Script for APEXSTEEL
This script helps you configure Razorpay API keys for your Django application.
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apexsteel.settings')
django.setup()

import razorpay
from django.conf import settings

def test_razorpay_connection(key_id, key_secret):
    """Test Razorpay API connection with provided keys"""
    try:
        client = razorpay.Client(auth=(key_id, key_secret))
        # Test with a minimal order creation
        test_order = client.order.create({
            'amount': 100,  # ₹1.00
            'currency': 'INR',
            'payment_capture': '1'
        })
        return True, test_order.get('id', 'Unknown')
    except razorpay.errors.BadRequestError as e:
        if "Authentication failed" in str(e):
            return False, "Authentication failed - Invalid API keys"
        else:
            return False, f"Bad request: {str(e)}"
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def update_settings_file(key_id, key_secret):
    """Update the Django settings file with new API keys"""
    settings_file = BASE_DIR / 'apexsteel' / 'settings.py'

    # Read current settings
    with open(settings_file, 'r') as f:
        content = f.read()

    # Replace the placeholder keys
    content = content.replace(
        "RAZORPAY_KEY_ID = 'rzp_test_your_actual_key_here'",
        f"RAZORPAY_KEY_ID = '{key_id}'"
    )
    content = content.replace(
        "RAZORPAY_KEY_SECRET = 'your_actual_secret_here'",
        f"RAZORPAY_KEY_SECRET = '{key_secret}'"
    )

    # Write back to file
    with open(settings_file, 'w') as f:
        f.write(content)

    print("✅ API keys updated in settings.py")

def main():
    print("🔧 Razorpay Setup for APEXSTEEL")
    print("=" * 40)

    print("\n📋 SETUP INSTRUCTIONS:")
    print("1. Go to https://dashboard.razorpay.com/")
    print("2. Sign up/Login to your Razorpay account")
    print("3. Go to Settings → API Keys")
    print("4. Generate Test Keys (for development)")
    print("5. Copy the Key ID and Key Secret below")

    print("\n🔑 Enter your Razorpay API Keys:")

    while True:
        key_id = input("API Key ID (rzp_test_...): ").strip()
        if not key_id:
            print("❌ Key ID cannot be empty")
            continue
        if not key_id.startswith('rzp_'):
            print("❌ Invalid Key ID format. Should start with 'rzp_'")
            continue
        break

    while True:
        key_secret = input("API Key Secret: ").strip()
        if not key_secret:
            print("❌ Key Secret cannot be empty")
            continue
        break

    print("\n🔍 Testing API connection...")

    success, message = test_razorpay_connection(key_id, key_secret)

    if success:
        print("✅ API connection successful!")
        print(f"Test order created: {message}")

        # Update settings file
        update_settings_file(key_id, key_secret)

        print("\n🎉 Razorpay setup completed successfully!")
        print("Your website is now connected to Razorpay.")
        print("\n📝 Next steps:")
        print("- Test the payment flow on your website")
        print("- For production, switch to Live keys in Razorpay dashboard")
        print("- Update settings.py with live keys when ready")

    else:
        print(f"❌ API connection failed: {message}")
        print("\n🔧 Troubleshooting:")
        print("- Check if your API keys are correct")
        print("- Ensure you're using Test keys for development")
        print("- Verify your Razorpay account is active")
        print("\nRun this script again with correct keys.")

if __name__ == "__main__":
    main()