import os
import time
import requests
import re

# Load credentials from Environment Variables (defaulting username to darwis2)
USERNAME = os.getenv('PORTAL_USERNAME', 'darwis2')
PASSWORD = os.getenv('PORTAL_PASSWORD', 'your_pass')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '60'))

def check_network_state():
    """
    Checks the internet and attempts to extract the captive portal URL using custom regex.
    Returns: (is_connected: bool, portal_url: str or None)
    """
    try:
        response = requests.get('http://www.gstatic.com/generate_204', timeout=5)
        
        if response.status_code == 204:
            return True, None
            
        portal_url = None
        form_url = None
        
        # Check for the specific JavaScript redirect
        if 'window.location' in response.text:
            # Your exact regex: window.location="(.*)fg.*";
            match2 = re.search(r'window\.location="(.*)fg.*";', response.text)
            match = re.search(r'window\.location="(.*)";', response.text)
            if match:
                # Group 1 extracts whatever is captured inside the (.*)
                portal_url = match.group(1)

            if match2:
                form_url = match2.group(1)
                
        return False, portal_url, form_url

    except requests.RequestException as e:
        print(f"Network error during check: {e}")
        return False, None, None

def login_to_portal(portal_url, form_url):
    if not portal_url:
        print("Network down, but no valid portal URL detected via regex.")
        return

    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting login sequence at: {portal_url}")
    
    try:
        with requests.Session() as session:
            
            # --- STEP 1: GET the portal page and extract the magic token ---
            print("Fetching portal page to extract 'magic' token...")
            get_response = session.get(portal_url, timeout=10)
            
            magic_token = ""
            magic_match = re.search(r'name="magic" value="(.*?)"', get_response.text)
            
            if magic_match:
                magic_token = magic_match.group(1)
                print(f"Success! Extracted magic token: {magic_token}")
            else:
                print("Warning: Could not find 'magic' token. Login might fail.")
            
            # --- STEP 2: Construct payload and POST ---
            # Passing this dictionary to 'data' automatically sets Content-Type to 
            # application/x-www-form-urlencoded and safely URL-encodes the 4Tredir URL.
            login_payload = {
                '4Tredir': 'http://www.gstatic.com/generate_204',
                'magic': magic_token,
                'username': USERNAME, 
                'password': PASSWORD
            }
            
            print("Submitting url-encoded POST request...")
            post_response = session.post(form_url, data=login_payload, timeout=10)
            
            if post_response.status_code in [200, 302]:
                print("Payload submitted successfully.")
            else:
                print(f"Login failed with HTTP Status: {post_response.status_code}")

    except Exception as e:
        print(f"Error during login sequence: {e}")

if __name__ == "__main__":
    print("Captive Portal Auto-Login Service Started.")
    while True:
        is_connected, dynamic_portal_url, dynamic_form_url = check_network_state()
        
        if not is_connected:
            login_to_portal(dynamic_portal_url, dynamic_form_url)
            time.sleep(10) # Pause to let the network stabilize
        
        time.sleep(CHECK_INTERVAL)