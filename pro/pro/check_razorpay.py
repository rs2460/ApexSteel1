#!/usr/bin/env python
import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apexsteel.settings')
django.setup()

from django.conf import settings

print("🔍 Razorpay Netbanking Status Check")
print("=" * 40)
print(f"API Key ID: {settings.RAZORPAY_KEY_ID}")
print(f"API Key Secret: {'Configured' if settings.RAZORPAY_KEY_SECRET != 'your_actual_secret_here' else 'NOT CONFIGURED'}")
print()

if settings.RAZORPAY_KEY_ID == 'rzp_test_your_actual_key_here':
    print("❌ PROBLEM FOUND: API keys are placeholder values")
    print("This is why netbanking is not working!")
    print()
    print("✅ SOLUTION:")
    print("1. Go to https://dashboard.razorpay.com/")
    print("2. Sign up/Login to your account")
    print("3. Go to Settings → API Keys")
    print("4. Generate Test Keys")
    print("5. Run: python setup_razorpay.py")
    print("6. Enter your real API keys")
else:
    print("✅ API keys appear configured")
    print("If netbanking still doesn't work:")
    print("- Check if your Razorpay account is fully activated")
    print("- Try with live keys instead of test keys")
    print("- Some banks may not support test transactions")