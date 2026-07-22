from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from Loginpage.login import LoginPage  
from Orgmanagement.orgmanagement import Orgpage
from Usermanagement.usermanagementflow import Userflow
from dotenv import load_dotenv
import os
import traceback
from time import sleep

# Load environment variables
load_dotenv()

def create_driver():
    options = Options()
    headless = os.getenv("HEADLESS", "true").lower() in ("1", "true", "yes")

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
    else:
        options.add_argument("--window-size=1100,900")
        options.add_argument("--window-position=20,20")

    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")

    return webdriver.Chrome(options=options)

def main():
    
    driver = create_driver()
    
    try:
        
        login_page = LoginPage(driver)
        
        username = os.getenv('USERNAME')
        password = os.getenv('PASSWORD')
        
        if login_page.login(username, password, auto_fill=True):
            print("✅ Login successful!")
            
            # Navigate to Organization Management
            #orgpage = Orgpage(driver)
            #orgpage.got_to_orgpage()  
            #orgpage.search()
            #orgpage.audit_logs()
            #orgpage.suspend_org()
            #
            #orgpage.go_to_suspended_org()
            #orgpage.login_info()
            #sleep(4)
            #handles = driver.window_handles
            #driver.switch_to.window(handles[0])
            #orgpage.unsuspend_org()
            #orgpage.filters()
            #orgpage.sus_history()
            
            #User management
            user = Userflow(driver)
            #admin_window = driver.current_window_handle
            #driver.execute_script("window.open('');")
            #driver.switch_to.window(driver.window_handles[-1])
            #user.prepare_random_email()
            #driver.switch_to.window(admin_window)
            
            user.go_to_user_management()
            #user.invite_user()
            #user.select_role()
            #user.accept_invite()
            #user.register_at_last()
            #sleep(5)
            #user.login_registered_user()
            #user.close_invite_tabs_and_return(admin_window)
            #user.user_filters()
            #user.action_btn()
            #user.search()
            #user.view_profile()
            user.reset_password()
            user.open_mail_for_reset()
            user.open_reset_mail()
            user.input_new_password()
            
    
        else:
            print("❌ Login failed!")
            
        if os.getenv("HEADLESS", "true").lower() not in ("1", "true", "yes"):
            input("Press Enter to close browser...")
   
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
    finally:
        driver.quit()
        
  

if __name__ == "__main__":
    main()
