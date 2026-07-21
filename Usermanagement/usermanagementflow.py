from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from time import sleep
from selenium.webdriver.common.keys import Keys
from Usermanagement.emailactions import Email
from Loginpage.login import LoginPage 



class Userflow(Email, LoginPage):
    USER_MANAGEMENTLINK = ORGPAGE_LINK = (By.XPATH, "//p[contains(., 'User Management')]")
    ALL = (By.XPATH, "//button[contains(., 'All')]")
    ADMINISTRATOR = (By.XPATH, "//button[contains(., 'Administrator')]")
    SUPER_ADMINS = (By.XPATH, "//button[contains(., 'Super Admins')]")
    SUPPORT = (By.XPATH, "//button[contains(., 'Support')]")
    SALES = (By.XPATH, "//button[contains(., 'Sales')]")
    CLEAR_FILTER = (By.XPATH, "//button[contains(., 'Clear Filter')]")
    ACTION_BTN = (By.XPATH, "//*local-name='path' and contains(@d, 'M9 15.75C8.175 15.75')")
    VIEW_PROFILE = (By.XPATH, "//button[contains,. 'View Profile']")
    LAST_REGISTER_BTN = (By.XPATH, "//button[@type='submit' and normalize-space(text())='Register']")
    LOGIN_EMAIL_INPUT = (By.XPATH, "//input[@type='email' or contains(translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'email') or contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'email')]")
    
    def __init__(self, driver):
        self.driver = driver
        super().__init__(driver)
        self.wait = WebDriverWait(driver, 10)
        self.click = lambda locator: self.wait.until(EC.element_to_be_clickable(locator)).click()


        
    def go_to_user_management(self):
        self.click(self.USER_MANAGEMENTLINK)
        sleep(2)
        
    def prepare_random_email(self):
        self.generated_email = self.set_random_email()
        return self.generated_email
    
    def register_at_last(self):
        driver = self.mail_driver or self.driver
        wait = self.mail_wait or self.wait

        register_btn = wait.until(EC.element_to_be_clickable(self.LAST_REGISTER_BTN))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", register_btn)
        sleep(0.5)
        register_btn.click()
        print("User registered...")
        
    def login_registered_user(self):
        registered_email = self.generated_email or self.email_address

        if not registered_email:
            raise RuntimeError("No registered email found. Run prepare_random_email() first.")

        driver = self.mail_driver or self.driver
        wait = self.mail_wait or self.wait

        driver.delete_all_cookies()
        driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
        driver.get(self.URL)
        sleep(2)
        self.change_server(driver=driver, wait=wait)

        username_input = wait.until(EC.visibility_of_element_located(self.LOGIN_EMAIL_INPUT))
        password_input = wait.until(EC.visibility_of_element_located(self.PASSWORD_INPUT))

        self._type(username_input, registered_email, driver)
        self._type(password_input, self.registered_password, driver)
        self.solve_recaptcha(driver=driver)
        wait.until(EC.element_to_be_clickable(self.LOGIN_BUTTON)).click()

        print(f"[login] registered user login submitted: {registered_email}")
        

    def user_filters(self):
        
        self.click(self.ADMINISTRATOR)
        sleep(1.5)
        self.click(self.SUPER_ADMINS)
        sleep(1.5)
        self.click(self.SUPPORT)
        sleep(1.5)
        self.click(self.SALES)
        sleep(1.5)
        self.click(self.ALL)
        sleep(1.5)
        self.click(self.CLEAR_FILTER)
        sleep(1)

    def action_btn(self):
        self.click(self.USER_MANAGEMENTLINK)
        sleep(1)
        self.click(self.ACTION_BTN)
        sleep(1)
        
    def view_profile(self):
        self.click(self.VIEW_PROFILE)
        sleep(1)
    
   
        
        
        
    
        
        
