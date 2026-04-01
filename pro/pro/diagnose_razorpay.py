#!/usr/bin/env python
"""
Razorpay Netbanking Diagnostic Script
This script helps diagnose netbanking and payment issues with Razorpay integration.
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

def check_api_keys():
    """Check if API keys are properly configured"""
    print("🔍 Checking API Key Configuration...")
    print(f"Key ID: {settings.RAZORPAY_KEY_ID}")
    print(f"Key Secret: {'*' * len(settings.RAZORPAY_KEY_SECRET) if settings.RAZORPAY_KEY_SECRET else 'NOT SET'}")

    if settings.RAZORPAY_KEY_ID == 'rzp_test_your_actual_key_here':
        print("❌ API Key ID is still placeholder value")
        return False
    if settings.RAZORPAY_KEY_SECRET == 'your_actual_secret_here':
        print("❌ API Key Secret is still placeholder value")
        return False

    print("✅ API keys appear to be configured")
    return True

def test_api_connection():
    """Test basic API connection"""
    print("\n🔍 Testing API Connection...")
    try:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # Test order creation
        test_order = client.order.create({
            'amount': 100,  # ₹1.00
            'currency': 'INR',
            'payment_capture': '1'
        })

        print("✅ API connection successful!")
        print(f"Test Order ID: {test_order.get('id')}")
        print(f"Order Amount: ₹{test_order.get('amount', 0) / 100}")
        print(f"Order Status: {test_order.get('status')}")

        return True, test_order

    except razorpay.errors.BadRequestError as e:
        print(f"❌ API Authentication failed: {str(e)}")
        print("💡 This usually means invalid API keys")
        return False, None
    except Exception as e:
        print(f"❌ API connection failed: {str(e)}")
        return False, None

def test_payment_methods():
    """Test available payment methods"""
    print("\n🔍 Testing Payment Methods...")
    try:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # Get payment methods (this endpoint might not be available in all plans)
        try:
            methods = client.payment.fetch_all()
            print("✅ Payment methods endpoint accessible")
            if methods and 'items' in methods:
                print(f"Recent payments count: {len(methods['items'])}")
        except:
            print("⚠️ Payment methods endpoint not accessible (normal for test accounts)")

        # Test order with different payment methods
        order_data = {
            'amount': 500,  # ₹5.00
            'currency': 'INR',
            'payment_capture': '1',
            'method': 'netbanking'  # Specifically test netbanking
        }

        netbanking_order = client.order.create(order_data)
        print("✅ Netbanking order creation successful!")
        print(f"Netbanking Order ID: {netbanking_order.get('id')}")

        return True

    except Exception as e:
        print(f"❌ Payment methods test failed: {str(e)}")
        return False

def diagnose_netbanking_issues():
    """Diagnose common netbanking issues"""
    print("\n🔍 Diagnosing Netbanking Issues...")

    issues = []

    # Check API keys
    if not check_api_keys():
        issues.append("API keys not configured properly")

    # Test API connection
    api_ok, _ = test_api_connection()
    if not api_ok:
        issues.append("API connection failed")

    # Test payment methods
    if api_ok and not test_payment_methods():
        issues.append("Payment methods configuration issue")

    # Check Razorpay account status
    print("\n🔍 Account Status Check...")
    print("⚠️ Note: For comprehensive account status, check your Razorpay Dashboard")
    print("   - Ensure your account is activated")
    print("   - Check if netbanking is enabled for your account")
    print("   - Verify you're using the correct environment (test/live)")

    if issues:
        print("\n❌ Issues Found:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    else:
        print("\n✅ No obvious issues detected with API configuration")

    return issues

def provide_solutions():
    """Provide solutions for common issues"""
    print("\n🛠️ Solutions for Netbanking Issues:")
    print("=" * 50)

    print("\n1. 🔑 API Keys Issue:")
    print("   - Run: python setup_razorpay.py")
    print("   - Get keys from: https://dashboard.razorpay.com/app/keys")
    print("   - Use Test keys for development")

    print("\n2. 🔐 Account Activation:")
    print("   - Login to Razorpay Dashboard")
    print("   - Complete account verification")
    print("   - Enable netbanking payments")

    print("\n3. 🌐 Network/Browser Issues:")
    print("   - Clear browser cache")
    print("   - Try different browser")
    print("   - Check internet connection")
    print("   - Disable VPN if using one")

    print("\n4. 💳 Payment Method Issues:")
    print("   - Netbanking may be disabled for test accounts")
    print("   - Some banks may not support test transactions")
    print("   - Try with different banks in live mode")

    print("\n5. 🔧 Code Issues:")
    print("   - Check browser console for JavaScript errors")
    print("   - Verify Razorpay SDK is loading")
    print("   - Check payment_processing.html configuration")

    print("\n📞 For Razorpay Support:")
    print("   - Email: support@razorpay.com")
    print("   - Dashboard: Help section")
    print("   - Documentation: https://docs.razorpay.com/")

def main():
    print("🔧 Razorpay Netbanking Diagnostic Tool")
    print("=" * 50)

    # Run diagnostics
    issues = diagnose_netbanking_issues()

    # Provide solutions
    provide_solutions()

    print("\n" + "=" * 50)
    if issues:
        print("❌ Issues detected. Please resolve them and try again.")
    else:
        print("✅ Configuration appears correct. If netbanking still doesn't work:")
        print("   - Test with a real payment in live mode")
        print("   - Check Razorpay dashboard for transaction logs")
        print("   - Contact Razorpay support if needed")

if __name__ == "__main__":
    main()