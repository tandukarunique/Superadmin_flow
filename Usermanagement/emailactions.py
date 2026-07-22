import os
import random
import re
import string
import time
from time import sleep

import requests
from pydub import AudioSegment
import speech_recognition as sr

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from Loginpage.login import LoginPage 



class Email(LoginPage):
    # ---- where things are on the page ----
    EMAIL_URL = "https://www.guerrillamail.com/inbox"
    INBOX_ID = (By.ID, "inbox-id")
    INBOX_INPUT = (By.CSS_SELECTOR, "span#inbox-id input, input#inbox-id")
    SET_BTN = (By.XPATH, "//button[contains(., 'Set') or contains(., 'Save')]")
    USE_ALIAS_CHECKBOX = (By.ID, "use-alias")
    EMAIL_WIDGET = (By.ID, "email-widget")

    INVITE_BTN = (By.XPATH, "//button[contains(., 'Invite User')]")
    INVITE_EMAIL_INPUT = (By.XPATH, "//input[contains(@placeholder, 'Enter email')]")
    ROLE_DROPDOWN = (By.XPATH, "//button[contains(., 'Select an option')]")
    ROLE_ADMIN = (By.XPATH, "//span[contains(., 'Administrator')]")
    SEND_INVITE_BTN = (By.XPATH, "(//button[contains(., 'Invite User')])[2]")

    FIRST_NAME_INPUT = (By.XPATH, "//input[contains(translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'first') or contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'first')]")
    LAST_NAME_INPUT = (By.XPATH, "//input[contains(translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'last') or contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'last')]")
    PASSWORD_INPUTS = (By.XPATH, "//input[@type='password']")
    CREATE_USER_BTN = (By.XPATH, "//button[contains(., 'Create') or contains(., 'Submit') or contains(., 'Continue') or contains(., 'Accept')]")
    

    RECAPTCHA_ANCHOR_FRAME = (By.XPATH, "//iframe[contains(@src,'recaptcha/api2/anchor')]")

    INVITE_SENDER = "noreply@chatboq.com"
    INVITE_SUBJECT = "Invitation to Join Chatboq SuperAdmin"
    RESET_SUBJECT = "Super Admin Password Reset Request"
    TEST_PASSWORD = "Tha cha 098!"

    def __init__(self, driver):
        self.driver = driver               # main app browser
        self.wait = WebDriverWait(driver, 10)
        self.email_address = None
        self.registered_password = self.TEST_PASSWORD

        self.mail_driver = None            # separate browser for the inbox
        self.mail_wait = None

    # ------------------------------------------------------------------
    # STEP 1: create the temp inbox
    # ------------------------------------------------------------------

    def set_random_email(self):
        """Open a fresh GuerrillaMail inbox with a random name and return the address."""
        self._open_mail_browser()

        name = "abc" + "".join(random.choices(string.ascii_lowercase, k=7))

        self.mail_wait.until(EC.element_to_be_clickable(self.INBOX_ID)).click()
        inbox_input = self.mail_wait.until(EC.element_to_be_clickable(self.INBOX_INPUT))
        inbox_input.send_keys(Keys.CONTROL, "a")
        inbox_input.send_keys(name)

        try:
            self.mail_wait.until(EC.element_to_be_clickable(self.SET_BTN)).click()
        except TimeoutException:
            inbox_input.send_keys(Keys.ENTER)

        sleep(2)
        self.mail_wait.until(EC.element_to_be_clickable(self.USE_ALIAS_CHECKBOX)).click()
        sleep(1)

        self.email_address = self._read_displayed_email(fallback=name)
        print(f"[email] set: {self.email_address}")
        return self.email_address

    def _open_mail_browser(self):
        options = ChromeOptions()
        options.add_argument("--incognito")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        self.mail_driver = webdriver.Chrome(options=options)
        self.mail_wait = WebDriverWait(self.mail_driver, 10)
        self.mail_driver.get(self.EMAIL_URL)
        sleep(3)

    def _read_displayed_email(self, fallback):
        widget = self.mail_wait.until(EC.visibility_of_element_located(self.EMAIL_WIDGET))
        text = widget.text.strip() or self.mail_driver.execute_script(
            "return arguments[0].innerText || arguments[0].value || '';", widget
        )
        match = re.search(r"[\w.+-]+@[\w.-]+\.\w+", text or "")
        return match.group(0) if match else f"{fallback}@guerrillamail.com"

    def quit_mail(self):
        if self.mail_driver:
            self.mail_driver.quit()
            self.mail_driver = None
            self.mail_wait = None

    def invite_user(self):
        if not self.email_address:
            raise RuntimeError("Call set_random_email() before invite_user().")

        self.wait.until(EC.element_to_be_clickable(self.INVITE_BTN)).click()
        sleep(0.5)

        email_input = self.wait.until(EC.element_to_be_clickable(self.INVITE_EMAIL_INPUT))
        self._type(email_input, self.email_address, self.driver)
        print(f"[email] invite pasted: {self.email_address}")

    def select_role(self):
        self.wait.until(EC.element_to_be_clickable(self.ROLE_DROPDOWN)).click()
        sleep(1)
        self.wait.until(EC.element_to_be_clickable(self.ROLE_ADMIN)).click()
        sleep(2)
        self.wait.until(EC.element_to_be_clickable(self.SEND_INVITE_BTN)).click()
        sleep(2)

    def accept_invite(self, timeout_seconds=90):
        if not self._wait_for_invite_email(timeout_seconds):
            raise RuntimeError("Invitation email never arrived.")

        before_tabs = set(self.mail_driver.window_handles)

        link = self._find_invite_link()
        if not link:
            raise RuntimeError("Invitation email opened, but no invite link was found.")

        self.mail_driver.execute_script("window.open(arguments[0], '_blank');", link)
        print(f"[email] opened invite link: {link}")
        self._switch_to_new_tab(before_tabs)

        self._fill_account_form()

    def _wait_for_invite_email(self, timeout_seconds):
        """Poll the inbox until the Chatboq invite email shows up, then open it."""
        print(f"[email] waiting for invite from {self.INVITE_SENDER}...")
        deadline = time.time() + timeout_seconds

        while time.time() < deadline:
            # refresh the inbox if GuerrillaMail's own JS is loaded
            self.mail_driver.execute_script(
                "if (typeof GRML !== 'undefined' && GRML.check_email) { GRML.check_email(); }"
            )
            sleep(2)

            row = self.mail_driver.execute_script(
                """
                const rows = document.querySelectorAll('.mail_row');
                const sender = arguments[0].toLowerCase();
                const subject = arguments[1].toLowerCase();
                for (const row of rows) {
                    const text = row.innerText.toLowerCase();
                    if (text.includes(sender) && text.includes(subject)) return row;
                }
                return null;
                """,
                self.INVITE_SENDER, self.INVITE_SUBJECT,
            )
            if row:
                self.mail_driver.execute_script("arguments[0].click();", row)
                sleep(2)
                return True
            sleep(3)

        return False

    def _find_invite_link(self):
        
        sleep(5)
        return self.mail_driver.execute_script(
            """
            const keywords = ['chatboq', 'invite', 'invitation', 'token'];
            for (const link of document.querySelectorAll('#display_email a[href], .mail_body a[href]')) {
                const href = link.href.toLowerCase();
                const text = link.innerText.toLowerCase();
                if (keywords.some(k => href.includes(k)) || text.includes('accept') || text.includes('join')) {
                    return link.href;
                }
            }
            return null;
            """
        )

    def _switch_to_new_tab(self, tabs_before, timeout=10):
        deadline = time.time() + timeout
        while time.time() < deadline:
            new_tabs = set(self.mail_driver.window_handles) - tabs_before
            if new_tabs:
                self.mail_driver.switch_to.window(next(iter(new_tabs)))
                return
            sleep(0.5)
        self.mail_driver.switch_to.window(self.mail_driver.window_handles[-1])

    def _fill_account_form(self):
        
        self.change_server(driver=self.mail_driver, wait=self.mail_wait)
        sleep(2)
        
        first_name = self._random_name("first")
        last_name = self._random_name("last")
        

        first_input = self.mail_wait.until(EC.element_to_be_clickable(self.FIRST_NAME_INPUT))
        self._type(first_input, first_name, self.mail_driver)

        last_input = self.mail_wait.until(EC.element_to_be_clickable(self.LAST_NAME_INPUT))
        self._type(last_input, last_name, self.mail_driver)

        password_fields = self.mail_wait.until(EC.presence_of_all_elements_located(self.PASSWORD_INPUTS))
        for field in password_fields:
            if field.is_displayed() and field.is_enabled():
                self._type(field, self.TEST_PASSWORD, self.mail_driver)

        if self.mail_driver.find_elements(*self.RECAPTCHA_ANCHOR_FRAME):
            print("[captcha] reCAPTCHA detected, attempting to solve...")
            self.solve_recaptcha(driver=self.mail_driver)
            sleep(2)

    def _wait_for_reset_email(self, timeout_seconds=90):

        print(f"[email] waiting for reset email from {self.INVITE_SENDER}...")
        deadline = time.time() + timeout_seconds

        while time.time() < deadline:
            self.mail_driver.execute_script(
                "if (typeof GRML !== 'undefined' && GRML.check_email) { GRML.check_email(); }"
            )
            sleep(2)

            row = self.mail_driver.execute_script(
                """
                const rows = document.querySelectorAll('.mail_row');
                const sender = arguments[0].toLowerCase();
                const subject = arguments[1].toLowerCase();
                for (const row of rows) {
                    const text = row.innerText.toLowerCase();
                    if (text.includes(sender) && text.includes(subject)) return row;
                }
                return null;
                """,
                self.INVITE_SENDER, self.RESET_SUBJECT,
            )
            if row:
                self.mail_driver.execute_script("arguments[0].click();", row)
                sleep(2)
                return True
            sleep(3)

        return False
                
    def _find_reset_link(self):
           
            sleep(5)
            return self.mail_driver.execute_script(
                """
                const keywords = ['chatboq', 'reset', 'password', 'token'];
                for (const link of document.querySelectorAll('#display_email a[href], .mail_body a[href]')) {
                    const href = link.href.toLowerCase();
                    const text = link.innerText.toLowerCase();
                    if (keywords.some(k => href.includes(k)) || text.includes('reset') || text.includes('password')) {
                        return link.href;
                    }
                }
                return null;
                """
           )
    

    def solve_recaptcha(self, driver=None):
        driver = driver or self.driver

        if not driver.find_elements(*self.RECAPTCHA_ANCHOR_FRAME):
            return True

        print("[captcha] reCAPTCHA detected, attempting to solve...")
        return Recaptcha(driver).solve()

    @staticmethod
    def _type(element, value, driver):
        """Type into a field. If the site's React form ignores send_keys,
        fall back to setting the value directly via JS."""
        element.click()
        element.send_keys(Keys.CONTROL, "a", Keys.DELETE)
        element.send_keys(value)

        if element.get_attribute("value") == value:
            return

        driver.execute_script(
            """
            const el = arguments[0], val = arguments[1];
            const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
            setter.call(el, val);
            el.dispatchEvent(new Event('input', {bubbles: true}));
            el.dispatchEvent(new Event('change', {bubbles: true}));
            """,
            element, value,
        )

    @staticmethod
    def _random_name(prefix):
        return (prefix + "".join(random.choices(string.ascii_lowercase, k=6))).title()


class Recaptcha:
    

    def __init__(self, driver):
        self.driver = driver

    def solve(self):
        """Click the checkbox; if a challenge pops up, solve it by audio."""
        try:
            self._click_checkbox()
            if self._audio_challenge_available():
                return self._solve_with_audio()
            print("[captcha] solved via checkbox only")
            return True
        except Exception as e:
            print(f"[captcha] failed: {e}")
            return False
        finally:
            self.driver.switch_to.default_content()

    def _click_checkbox(self):
        frame = self.driver.find_element(By.XPATH, "//iframe[contains(@src,'recaptcha/api2/anchor')]")
        self.driver.switch_to.frame(frame)
        self.driver.find_element(By.ID, "recaptcha-anchor").click()
        self.driver.switch_to.default_content()
        sleep(2)

    def _audio_challenge_available(self):
        return bool(self.driver.find_elements(By.XPATH, "//iframe[contains(@src,'recaptcha/api2/bframe')]"))

    def _solve_with_audio(self):
        frame = self.driver.find_element(By.XPATH, "//iframe[contains(@src,'recaptcha/api2/bframe')]")
        self.driver.switch_to.frame(frame)

        self.driver.find_element(By.ID, "recaptcha-audio-button").click()
        sleep(2)

        text = self._download_and_transcribe()
        if not text:
            # one retry with a fresh audio clip
            self.driver.find_element(By.ID, "recaptcha-audio-button").click()
            sleep(2)
            text = self._download_and_transcribe()

        if not text:
            return False

        self.driver.find_element(By.ID, "audio-response").send_keys(text)
        sleep(1)
        self.driver.find_element(By.ID, "recaptcha-verify-button").click()
        sleep(3)
        return True

    def _download_and_transcribe(self):
        audio_url = self.driver.find_element(By.ID, "audio-source").get_attribute("src")
        mp3_path, wav_path = "captcha_audio.mp3", "captcha_audio.wav"

        try:
            resp = requests.get(audio_url, timeout=15)
            resp.raise_for_status()
            with open(mp3_path, "wb") as f:
                f.write(resp.content)

            AudioSegment.from_mp3(mp3_path).export(wav_path, format="wav")

            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return re.sub(r"[^0-9a-zA-Z\s]", "", text).strip()

        except Exception as e:
            print(f"[captcha] transcription failed: {e}")
            return None

        finally:
            for path in (mp3_path, wav_path):
                if os.path.exists(path):
                    os.remove(path)