from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium_recaptcha_solver import RecaptchaSolver  # Import the solver
from utils.session_manager import save_session, load_session, clear_session
from time import sleep


class SuspendedOrgPage():
    URL = "https://uat.chatboq.com"
    SESSION_FILE = "uat_auth.json"
    ORG_NAME = "Test .this one"
    EMAIL = (By.ID, "email")
    PASSWORD = (By.ID, "password")
    LOGIN = (By.XPATH, "//button[contains(., 'Login to Dashboard')]")
    ORGNAME = (By.XPATH, f"//span[normalize-space()='{ORG_NAME}']/ancestor::div[contains(@class,'justify-between')][1]//button[@data-slot='button']")
    CONFIRM_ORG =  (By.XPATH, "//button[@data-slot='button' and .//section[normalize-space(text())='Switch Organization']]")
    NOT_NOW = (By.XPATH, "//button[contains(., 'Not now')]")
    
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        
        self.solver = RecaptchaSolver(driver=driver)
    
    def go_to_chatboq(self):
        self.driver.get(self.URL)
        return self
    
    def auto_login(self) -> bool:
        if load_session(self.driver, site=self.URL, session_file=self.SESSION_FILE):
            print("[uat] ✅ Auto-login successful")
            if "/select-organization" in self.driver.current_url:
                self.select_org()
            return True
        clear_session(self.SESSION_FILE)
        return False

    def save_session(self):
        save_session(
            self.driver,
            session_file=self.SESSION_FILE,
            extra_data={"selected_organization": self.get_selected_org()},
        )
        print("[uat] ✅ Session saved")

    def get_selected_org(self):
        org_id = self.driver.execute_script("""
            const orgCookie = document.cookie
                .split('; ')
                .find((row) => row.startsWith('organization='));
            if (orgCookie) {
                const value = decodeURIComponent(orgCookie.split('=').slice(1).join('='));
                if (value) return value;
            }

            const queryCache = localStorage.getItem('react-query');
            if (!queryCache) return null;

            const parsed = JSON.parse(queryCache);
            const queries = parsed?.clientState?.queries || [];
            const profile = queries.find((query) => query.queryHash === '["user-profile"]');
            return profile?.state?.data?.data?.user?.attributes?.organization_id || null;
        """)
        return {"name": self.ORG_NAME, "id": org_id}

    def select_org(self):
        orgswitch = self.wait.until(EC.element_to_be_clickable(self.ORGNAME))
        self.driver.execute_script("arguments[0].click();", orgswitch)
        sleep(2)

        self.wait.until(EC.element_to_be_clickable(self.CONFIRM_ORG)).click()
        sleep(3)

        try:
            self.wait.until(EC.element_to_be_clickable(self.NOT_NOW)).click()
            sleep(1)
        except Exception:
            pass

        self.save_session()

    def login(self):
        if self.auto_login():
            return True

        self.go_to_chatboq()
        email = self.wait.until(EC.element_to_be_clickable(self.EMAIL))
        email.send_keys("uniquetandukar8645@gmail.com")
        
        password = self.wait.until(EC.element_to_be_clickable(self.PASSWORD))
        password.send_keys("Tha cha 098!")
        sleep(3)
        
        recaptcha_iframe = self.driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]')
        self.solver.click_recaptcha_v2(iframe=recaptcha_iframe)
        self.wait.until(EC.element_to_be_clickable(self.LOGIN)).click()
        self.wait.until(lambda driver: "/login" not in driver.current_url)
        sleep(2)
        self.save_session()
        
        self.select_org()
        return True
        
        
        
        
