from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from time import sleep
from selenium.webdriver.common.keys import Keys

from Orgmanagement.Suspendedorg import SuspendedOrgPage


class Orgpage(SuspendedOrgPage):
    ORGPAGE_LINK = (By.XPATH, "//p[contains(., 'Organization Management')]")
    SEARCH = (By.XPATH, "//input[@placeholder='Search organization']")
    ACTION = (By.XPATH, "//*[local-name()='path' and contains(@d, 'M9 15.75C8.175 15.75 7.5 15.075')]//ancestor::button[1]")
    VIEW_ORG_DETAILS = (By.XPATH, "//p[contains(., 'View Organization Details')]")
    FILTER_SEARCH = (By.XPATH,"//input[@placeholder='Search...']")
    AUDIT_LOGS = (By.XPATH, "//p[contains(., 'View Audit Logs')]")
    PAGE_NUMBER = (By.XPATH, "(//li[@data-slot='pagination-item']//button)[last()]")
    PREV = (By.XPATH, "//button[contains(., 'Previous')]")
    NEXT = (By.XPATH, "//button[contains(., 'Next')]")
    SUSPEND = (By.XPATH, "//p[contains(., 'Suspend Organization')]")
    SUSPEND_REASON = (By.XPATH, "//input[@type='text' and @name='reason']")
    PROCEED_BTN = (By.XPATH, "//button[contains(., 'Proceed')]")
    UNSUSPEND = (By.XPATH, "//p[contains(., 'Unsuspend Organization')]")
    UNSUSPEND_REASON = (By.XPATH, "//textarea[@name='reason']")
    CONFIRM_UNSUSPEND = (By.XPATH, "//button[contains(., 'Unsuspend')]")
    CLEAR_FILTER_VALUE = (By.CSS_SELECTOR, 'input[role="searchbox"]')
    FILTER_SUSPEND = (By.XPATH, "//button[contains(., 'Suspended')]")
    ACTIVE = (By.XPATH, "//button[contains(., 'Active')]")
    SUS_HISTORY = (By.XPATH, "//button[contains(., 'View Suspension History')]")
    
    
                               
    def __init__(self, driver):
        self.driver = driver
        super().__init__(driver)
        self.wait = WebDriverWait(driver, 10)
        self.click = lambda locator: self.wait.until(EC.element_to_be_clickable(locator)).click()

    def visible_element(self, locator):
        elements = self.wait.until(EC.presence_of_all_elements_located(locator))
        for element in elements:
            if element.is_displayed() and element.is_enabled():
                return element
        raise NoSuchElementException(f"No visible enabled element found for {locator}")
        
    def got_to_orgpage(self):
        self.wait.until(EC.element_to_be_clickable(self.ORGPAGE_LINK)).click()
        sleep(2)
    
        trial = self.wait.until(EC.element_to_be_clickable(self.SEARCH))
        trial.send_keys("Test .this one")
        sleep(1.5)
        
        self.wait.until(EC.element_to_be_clickable(self.ACTION)).click()
        sleep(1)
        
    def search(self):
        element = self.wait.until(EC.element_to_be_clickable(self.VIEW_ORG_DETAILS))
        element.click()
        #self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        sleep(3)
        
        #To check if filter is working
        filtercheck= self.wait.until(EC.element_to_be_clickable(self.FILTER_SEARCH))
        filtercheck.send_keys("hellosssssss")
        sleep(1.5)
        
    def audit_logs(self):
        self.got_to_orgpage()
        self.click(self.AUDIT_LOGS)
        sleep(2)
        
        self.click(self.PAGE_NUMBER)
        self.click(self.PREV)
        sleep(2)
        self.click(self.NEXT)
        sleep(2)
    
    
    def suspend_org(self):
        self.got_to_orgpage()
        sleep(2)
        self.click(self.SUSPEND)
        sleep(1)
        reason = self.wait.until(EC.element_to_be_clickable(self.SUSPEND_REASON))
        reason.send_keys("Anything.... ")
        sleep(1)
        self.click(self.PROCEED_BTN)

    def unsuspend_org(self):
        self.got_to_orgpage()
        self.click(self.UNSUSPEND)
        unsuspend_reason = self.wait.until(EC.element_to_be_clickable(self.UNSUSPEND_REASON))
        sleep(2)
        unsuspend_reason.send_keys("Anything......")
        sleep(2)
        self.click(self.CONFIRM_UNSUSPEND)
        
    def go_to_suspended_org(self):
        
        self.driver.execute_script("window.open('');")
        sleep(2) 
        
        # Switch to the new tab (last tab)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        
        # Now navigate to the URL in the new tab
        susorg = SuspendedOrgPage(self.driver)
        susorg.go_to_chatboq()
        
    def login_info(self):
        self.login()
        
    def filters(self):
        filter_btn = self.visible_element(self.CLEAR_FILTER_VALUE)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", filter_btn)
        filter_btn.click()
        filter_btn.send_keys(Keys.CONTROL, "a")
        filter_btn.send_keys(Keys.DELETE)
        sleep(2)
        
        #Suspended
        suspend = self.wait.until(EC.element_to_be_clickable(self.FILTER_SUSPEND))
        suspend.click()
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", suspend)
        sleep(2)
        
        #Active
        active = self.wait.until(EC.element_to_be_clickable(self.ACTIVE))
        active.click()
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", active)
        sleep(2)
        
    def sus_history(self):
        self.got_to_orgpage()
        sleep(0.5)
        
        self.click(self.SUS_HISTORY)
        sleep(1)
        
    
        
        
        
    
