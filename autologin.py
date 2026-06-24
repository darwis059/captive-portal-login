import os
import time
import requests

# Load configuration from Environment Variables (passed by Docker)
PORTAL_URL = os.getenv('PORTAL_URL', 'http://192.168.1.1/login')
USERNAME = os.getenv('PORTAL_USERNAME', 'your_user')
PASSWORD = os.getenv('PORTAL_PASSWORD', 'your_pass')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '60')) # Check every 60 seconds

# The payload structure you found in Step 1
LOGIN_PAYLOAD = {
    'username': USERNAME,
    'password': PASSWORD,
    # Add any other required hidden fields you found, like:
    # 'accept_terms': 'yes'
}

def check_internet():
    """Returns True if internet is working, False if intercepted by portal."""
    try:
        # Check a reliable, external URL. Set timeout low to fail fast.
        response = requests.get('http://clients3.google.com/generate_204', timeout=5)
        # Google's 204 endpoint returns exactly 204 No Content if connected.
        # If a captive portal intercepts it, it will usually return a 200 or 302.
        return response.status_code == 204
    except requests.RequestException:
        return False

def login_to_portal():
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] No internet. Attempting login...")
    try:
        # Use a session so cookies persist if the portal requires a multi-step redirect
        with requests.Session() as session:
            # Step A: (Optional) Get the initial page to grab cookies or CSRF tokens if needed
            # response = session.get(PORTAL_URL)
            
            # Step B: Submit the login payload
            response = session.post(PORTAL_URL, data=LOGIN_PAYLOAD, timeout=10)
            
            if response.status_code in [200, 302]:
                print("Login payload sent successfully.")
            else:
                print(f"Login failed with status: {response.status_code}")
    except Exception as e:
        print(f"Error during login: {e}")

if __name__ == "__main__":
    print("Captive Portal Auto-Login Service Started.")
    while True:
        if not check_internet():
            login_to_portal()
            # Wait a moment to let the network stabilize after login
            time.sleep(10) 
        
        # Wait before checking again
        time.sleep(CHECK_INTERVAL)