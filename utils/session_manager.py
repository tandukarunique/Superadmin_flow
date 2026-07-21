import json
import os
import time
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load .env for URL
from dotenv import load_dotenv
load_dotenv()

SITE = os.getenv('URL', 'https://app-admin.chatboq.com')
SESSION_FILE = Path("auth.json")

def save_session(driver, session_file=SESSION_FILE, extra_data=None):
    """Save cookies and localStorage to a file"""
    try:
        session_data = {
            'cookies': driver.get_cookies(),
            'local_storage': driver.execute_script("return window.localStorage;"),
            'session_storage': driver.execute_script("return window.sessionStorage;"),
            'timestamp': time.time(),
            'url': driver.current_url
        }
        if extra_data:
            session_data.update(extra_data)
        
        session_file = Path(session_file)
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)
        
        print(f"[session] ✅ Saved session with {len(session_data['cookies'])} cookies to {session_file}")
        return True
    except Exception as e:
        print(f"[session] ❌ Failed to save session: {e}")
        return False

def load_session(driver, site=SITE, session_file=SESSION_FILE):
    """Load cookies and localStorage from file"""
    session_file = Path(session_file)
    if not session_file.exists():
        print("[session] No saved session found")
        return False
    
    try:
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        # Navigate to domain first
        driver.get(site)
        time.sleep(1)
        
        # Delete existing cookies
        driver.delete_all_cookies()
        
        # Add saved cookies
        cookies = session_data.get('cookies', [])
        for cookie in cookies:
            try:
                # Handle expiration if present
                if 'expiry' in cookie:
                    cookie['expiry'] = int(cookie['expiry'])
                # Handle sameSite attribute
                if 'sameSite' in cookie and cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
                    cookie['sameSite'] = 'Lax'
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"[session] ⚠️ Could not add cookie {cookie.get('name', 'unknown')}: {e}")
        
        # Restore localStorage
        local_storage = session_data.get('local_storage', {})
        for key, value in local_storage.items():
            driver.execute_script("window.localStorage.setItem(arguments[0], arguments[1]);", key, value)
        
        # Restore sessionStorage
        session_storage = session_data.get('session_storage', {})
        for key, value in session_storage.items():
            driver.execute_script("window.sessionStorage.setItem(arguments[0], arguments[1]);", key, value)
        
        print(f"[session] ✅ Loaded {len(cookies)} cookies and storage data")
        
        # Refresh to apply session
        driver.refresh()
        time.sleep(3)
        
        # Check if login was successful
        if "/login" not in driver.current_url:
            print("[session] ✅ Session is valid")
            return True
        else:
            print("[session] ⚠️ Session expired or invalid")
            return False
            
    except json.JSONDecodeError as e:
        print(f"[session] ❌ Invalid session file: {e}")
        return False
    except Exception as e:
        print(f"[session] ❌ Failed to load session: {e}")
        return False

def clear_session(session_file=SESSION_FILE):
    """Delete the saved session file"""
    session_file = Path(session_file)
    if session_file.exists():
        session_file.unlink()
        print("[session] 🗑️ Session cleared")
        return True
    print("[session] No session to clear")
    return False

def get_session_info():
    """Get info about saved session"""
    if not SESSION_FILE.exists():
        return None
    
    try:
        with open(SESSION_FILE, 'r') as f:
            data = json.load(f)
        
        cookies = data.get('cookies', [])
        created_time = data.get('timestamp', 0)
        
        return {
            'file': str(SESSION_FILE),
            'cookie_count': len(cookies),
            'created': time.ctime(created_time) if created_time else 'Unknown',
            'age_hours': round((time.time() - created_time) / 3600, 2) if created_time else 0,
            'url': data.get('url', 'Unknown')
        }
    except Exception as e:
        print(f"Error reading session info: {e}")
        return None

def is_session_valid(driver) -> bool:
    """Check if current session is still valid"""
    try:
        # Try to access a protected page or check for login indicator
        current_url = driver.current_url
        return "/login" not in current_url
    except:
        return False
