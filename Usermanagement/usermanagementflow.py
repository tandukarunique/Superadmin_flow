from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from time import sleep
from selenium.webdriver.common.keys import Keys
from Usermanagement.emailactions import Email
from Loginpage.login import LoginPage 
from selenium.webdriver.common.action_chains import ActionChains



class Userflow(Email, LoginPage):
    USER_MANAGEMENTLINK = ORGPAGE_LINK = (By.XPATH, "//p[contains(., 'User Management')]")
    ALL = (By.XPATH, "//button[contains(., 'All')]")
    ADMINISTRATOR = (By.XPATH, "//button[contains(., 'Administrator')]")
    SUPER_ADMINS = (By.XPATH, "//button[contains(., 'Super Admins')]")
    SUPPORT = (By.XPATH, "//button[contains(., 'Support')]")
    SALES = (By.XPATH, "//button[contains(., 'Sales')]")
    CLEAR_FILTER = (By.XPATH, "//button[contains(., 'Clear Filter')]")
    ACTION_BTN = (By.XPATH, "//*[local-name()='path' and contains(@d, 'M9 15.75C8.175 15.75')]")
    VIEW_PROFILE = (By.XPATH, "//button[contains(., 'View Profile')]")
    LAST_REGISTER_BTN = (By.XPATH, "//button[@type='submit' and normalize-space(text())='Register']")
    LOGIN_EMAIL_INPUT = (By.XPATH, "//input[@type='email' or contains(translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'email') or contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'email')]")
    SEARCH = (By.XPATH, '//input[@role="searchbox" and contains(@class, "h-10") and contains(@class, "w-full")]')
    RESET_PASSWORD = (By.XPATH, "//button[contains(., 'Reset Password')]")
    RESET_BTN = (By.XPATH, "//button[contains(., 'Reset')]")
    NEW_PASSWORD = (By.XPATH, "//input[@placeholder='Enter new password']")
    CONFIRM_NEW_PASSWORD = (By.XPATH, "//input[@placeholder='Confirm password']")
    CHANGE_PASSWORD_BTN = (By.XPATH, "//button[contains(., 'Change Password')]")
    
    
    
    def __init__(self, driver):
        self.driver = driver
        super().__init__(driver)
        self.generated_email = None
        self.wait = WebDriverWait(driver, 10)
        self.click = lambda locator: self.wait.until(EC.element_to_be_clickable(locator)).click()
        self.actions = ActionChains(driver)
   
    
        
    def go_to_user_management(self):
        self.click(self.USER_MANAGEMENTLINK)
        sleep(2)
        
    def prepare_random_email(self):
        self.generated_email = self.set_random_email()
        return self.generated_email
    
    def register_at_last(self):
        driver = self.mail_driver or self.driver
        wait = self.mail_wait or self.wait

        self._solve_captcha_or_wait_manual(driver)
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
        self._solve_captcha_or_wait_manual(driver)
        wait.until(EC.element_to_be_clickable(self.LOGIN_BUTTON)).click()
        sleep(5)
        

        print(f"[login] registered user login submitted: {registered_email}")

    def _solve_captcha_or_wait_manual(self, driver, timeout_seconds=240):
        solved = self.solve_recaptcha(driver=driver)
        if solved and self._captcha_is_solved(driver):
            return True

        print("[captcha] waiting until CAPTCHA is solved. Please solve it manually if needed...")
        WebDriverWait(driver, timeout_seconds).until(lambda _: self._captcha_is_solved(driver))
        print("[captcha] manually solved, continuing...")
        return True

    def _captcha_is_solved(self, driver):
        if not driver.find_elements(*self.RECAPTCHA_ANCHOR_FRAME):
            return True

        try:
            frame = driver.find_element(*self.RECAPTCHA_ANCHOR_FRAME)
            driver.switch_to.frame(frame)
            checkbox = driver.find_element(By.ID, "recaptcha-anchor")
            return checkbox.get_attribute("aria-checked") == "true"
        finally:
            driver.switch_to.default_content()
        
    def close_invite_tabs_and_return(self, admin_window=None):
        if self.mail_driver:
            self.quit_mail()

        if admin_window and admin_window in self.driver.window_handles:
            self.driver.switch_to.window(admin_window)
        elif self.driver.window_handles:
            self.driver.switch_to.window(self.driver.window_handles[0])

        print("[browser] returned to invitation sender window")
        

    def user_filters(self):
        
        self.click(self.ADMINISTRATOR)
        sleep(1.5)
        self.click(self.SUPER_ADMINS)
        sleep(1)
        self.click(self.SUPPORT)
        sleep(1)
        self.click(self.SALES)
        sleep(1)
        self.click(self.ALL)
        sleep(1.5)
        self.click(self.CLEAR_FILTER)
        sleep(1)

    def search(self):
        searchtxt = self.wait.until(EC.element_to_be_clickable(self.SEARCH))
        sleep(0.5)
        searchtxt.send_keys("ab")
        sleep(2)
        searchtxt.send_keys(Keys.CONTROL, 'a')
        searchtxt.send_keys(Keys.DELETE)
        
    def action_btn(self):
        self.click(self.USER_MANAGEMENTLINK)
        sleep(1)
        self.click(self.ACTION_BTN)
        sleep(1)
        
    def view_profile(self):
        self.action_btn()
        sleep(1.5)
        self.click(self.VIEW_PROFILE)
        sleep(2)
        self.actions.send_keys(Keys.ESCAPE).perform()
        sleep(1)
        
    def reset_password(self):
        #reset_email = self.generated_email or self.email_address
        #if not reset_email:
        #    raise RuntimeError("No email found for reset password. Run prepare_random_email() first.")

        searchtxt2 = self.wait.until(EC.element_to_be_clickable(self.SEARCH))
        sleep(0.5)
        #searchtxt2.send_keys(reset_email)
        searchtxt2.send_keys("ab")
        sleep(3)
        self.click(self.ACTION_BTN)
        sleep(1)
        self.click(self.RESET_PASSWORD)
        sleep(1)
        self.click(self.RESET_BTN)
        sleep(1)
        
    def open_mail_for_reset(self):
        self._open_mail_browser() #Opens incognito
        name = "abccvoyydf"
        
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
    
    def open_reset_mail(self):
        if not self._wait_for_reset_email():
            raise RuntimeError("Password reset email never arrived.")

        link = self._find_reset_link()
        if not link:
            raise RuntimeError("Reset email opened, but no reset link was found.")

        before_tabs = set(self.mail_driver.window_handles)
        self.mail_driver.execute_script("window.open(arguments[0], '_blank');", link)
        self._switch_to_new_tab(before_tabs)
        print(f"[email] opened reset link: {link}")
        
    def input_new_password(self):

        driver = self.mail_driver or self.driver
        wait = self.mail_wait or self.wait

        reset_url = driver.current_url

        driver.get(self.URL)
        sleep(2)
        self.change_server(driver=driver, wait=wait)

        driver.get(reset_url)
        sleep(2)

        new_pass = wait.until(EC.element_to_be_clickable(self.NEW_PASSWORD))
        new_pass.send_keys("Tha cha 098!")
        sleep(1)
        confirm_pass = wait.until(EC.element_to_be_clickable(self.CONFIRM_NEW_PASSWORD))
        confirm_pass.send_keys("Tha cha 098!")
        sleep(1)
        wait.until(EC.element_to_be_clickable(self.CHANGE_PASSWORD_BTN)).click()
        
        
    
    
    
   
        
        
        
    
        
        
