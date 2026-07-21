# Loginpage/login.py
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
from utils.session_manager import save_session, load_session, SITE, clear_session, is_session_valid

load_dotenv()

class LoginPage:
    # Locators
    URL = "https://app-admin.chatboq.com/"
    USERNAME_INPUT = (By.CSS_SELECTOR, "input[placeholder='you@example.com']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[placeholder='********']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    SETTINGS_SVG = (By.XPATH, "//*[local-name()='svg' and contains(@class, 'cursor-pointer')]")
    SELECT_SERVER_DROPDOWN = (By.XPATH, "(//button[@role='combobox'])[last()]")
    SERVER_OPTION = (By.XPATH, "//*[@role='option' and normalize-space()='UAT']")
    SETTINGS_SUBMIT = (By.XPATH, "(//button[normalize-space()='Submit'])[last()]")

    def __init__(self, driver, timeout: int = 15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)
        self.username = os.getenv('USERNAME')
        self.password = os.getenv('PASSWORD')

    # ── Navigation ──────────────────────────────────────────────
    def load(self):
        self.driver.get(self.URL)
        time.sleep(2)
        return self

    def goto(self, path: str):
        url = self.URL + path if path.startswith("/") else self.URL + "/" + path
        self.driver.get(url)
        if "/login" in self.driver.current_url:
            raise RuntimeError("❌ Session expired")
        print(f"[login] Navigated to: {self.driver.current_url}")

    # ── Server ──────────────────────────────────────────────────
    def change_server(self, driver=None, wait=None):
        driver = driver or self.driver
        wait = wait or (self.wait if driver == self.driver else WebDriverWait(driver, 10))

        try:
            wait.until(EC.element_to_be_clickable(self.SETTINGS_SVG)).click()
            time.sleep(1)
            wait.until(EC.element_to_be_clickable(self.SELECT_SERVER_DROPDOWN)).click()
            time.sleep(1)
            wait.until(EC.element_to_be_clickable(self.SERVER_OPTION)).click()
            time.sleep(1)
            wait.until(EC.element_to_be_clickable(self.SETTINGS_SUBMIT)).click()
            time.sleep(3)
            print("[login] ✅ Server changed to UAT")
        except Exception as e:
            print(f"[login] ⚠️ Server change failed: {e}")

    # ── Session ──────────────────────────────────────────────────
    def auto_login(self) -> bool:
        if load_session(self.driver) and "/login" not in self.driver.current_url:
            print("[login] ✅ Auto-login successful")
            return True
        clear_session()
        return False

    def save_session(self):
        save_session(self.driver)
        print("[login] ✅ Session saved")

    def clear_session(self):
        clear_session()

    def is_logged_in(self) -> bool:
        return "/login" not in self.driver.current_url

    # ── CAPTCHA Handling ────────────────────────────────────────
    def wait_for_login(self, timeout: int = 120) -> bool:
        #Wait for user to solve CAPTCHA and click login..... 
        print("[login] 🤖 Solve CAPTCHA and click Login (waiting up to 120s)...")
        start = time.time()
        
        while time.time() - start < timeout:
            if "/login" not in self.driver.current_url:
                time.sleep(2)
                self.save_session()
                return True
            time.sleep(2)
        
        print("[login] ❌ Login timeout")
        return False

    # ── Login ────────────────────────────────────────────────────
    def login(self, username: str = None, password: str = None, auto_fill: bool = True) -> bool:
        """Main login: try session first, then manual with CAPTCHA"""
        if self.auto_login():
            return True
        
        # Manual login flow
        username = username or self.username
        password = password or self.password
        
        self.load()
        self.change_server()
        
        # Auto-fill credentials
        if auto_fill and username and password:
            try:
                self.wait.until(EC.visibility_of_element_located(self.USERNAME_INPUT)).send_keys(username)
                self.wait.until(EC.visibility_of_element_located(self.PASSWORD_INPUT)).send_keys(password)
                print("[login] ✓ Credentials auto-filled")
            except Exception as e:
                print(f"[login] ⚠️ Auto-fill failed: {e}")
        
        # Wait for CAPTCHA and login
        return self.wait_for_login()

    def login_with_retry(self, max_retries: int = 2) -> bool:
        for attempt in range(max_retries):
            if attempt > 0:
                self.clear_session()
            if self.login():
                return True
            print(f"[login] ⚠️ Attempt {attempt + 1} failed")
        return False
