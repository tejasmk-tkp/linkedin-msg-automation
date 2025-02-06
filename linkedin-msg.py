import os
import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium_stealth import stealth

# Load CSV with profile URLs and names
csv_file = "Connections.csv"
data = pd.read_csv(csv_file)

# Log file for sent messages
log_file = "MessagesSent.csv"

# Load already messaged profiles to avoid duplicates
if os.path.exists(log_file):
    log_data = pd.read_csv(log_file)
    messaged_profiles = set(log_data["Profile URL"].tolist())
else:
    log_data = pd.DataFrame(columns=["Profile URL", "First Name", "Message Sent Time"])
    messaged_profiles = set()

# Chrome options to connect to existing session
chrome_options = Options()
chrome_options.debugger_address = "localhost:9222"  # Connect to running Chrome
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Apply stealth mode
stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True)

# Open LinkedIn (must be logged in)
driver.get("https://www.linkedin.com")
time.sleep(random.uniform(5, 8))

# Message template
message_template = """Hi {first_name},

I hope you’re doing well! I’m working on a research project focused on urban farming and sustainable food solutions. The idea is to explore how urban spaces can be better utilized to grow food locally and address some of the challenges around food security.

Your insights would be incredibly valuable in shaping this study! The survey takes less than 2 minutes, and your input will directly help in validating the concept.

Here’s the link: https://forms.gle/2Qc6wwCC1tUGESXk8

If you know someone else who might be interested in this, feel free to share it with them too! The more perspectives we gather, the better.

Thanks so much for your time and help—I truly appreciate it!

Best regards,  
Tejas M K"""

# Simulate human typing
def human_typing(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.03, 0.2))  # Random delay between keystrokes

# Process LinkedIn profiles in batches of 20 per hour
message_count = 0
for index, row in data.iterrows():
    profile_url = row['URL']
    first_name = row['First Name']

    # Skip if already messaged
    if profile_url in messaged_profiles:
        print(f"⏭️ Already messaged {first_name}. Skipping.")
        continue

    try:
        driver.get(profile_url)
        time.sleep(random.uniform(3, 6))  # Random delay before interaction
        
        # Scroll randomly
        driver.execute_script(f"window.scrollBy(0, {random.randint(800, 1500)});")
        time.sleep(random.uniform(2, 4))

        # Click the "Message" button
        try:
            message_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'artdeco-button') and contains(., 'Message')]"))
            )
            message_button.click()
        except:
            try:
                more_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'artdeco-dropdown__trigger')]"))
                )
                more_button.click()
                time.sleep(random.uniform(1, 3))

                message_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'artdeco-dropdown__content')]//span[contains(text(), 'Message')]"))
                )
                message_button.click()
            except:
                print(f"❌ Message button not found for {first_name}. Skipping.")
                continue

        # Wait for the message box
        message_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']"))
        )

        # Type and send the message
        message = message_template.format(first_name=first_name)
        human_typing(message_box, message)
        time.sleep(random.uniform(1, 3))

        # Click Send
        try:
            send_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@role='dialog']//button[contains(@aria-label, 'Send') or contains(text(), 'Send')]"))
            )
            driver.execute_script("arguments[0].click();", send_button)
            print(f"✅ Message sent to {first_name}")
        except:
            print(f"⚠️ Send button not found for {first_name}. Trying ENTER key.")
            message_box.send_keys(Keys.CONTROL, Keys.RETURN)

        # Log message
        log_data = log_data.append({
            "Profile URL": profile_url,
            "First Name": first_name,
            "Message Sent Time": time.strftime('%Y-%m-%d %H:%M:%S')
        }, ignore_index=True)

        log_data.to_csv(log_file, index=False)
        messaged_profiles.add(profile_url)

        # Close chat
        try:
            message_box.send_keys(Keys.ESCAPE)
            time.sleep(random.uniform(2, 4))
        except:
            print("❌ Could not close chat. Moving on.")

        # Update message count
        message_count += 1
        print(f"📩 {message_count}/20 messages sent this hour.")

        # Pause after 20 messages
        if message_count >= 20:
            print("⏳ Sent 20 messages. Sleeping for 1 hour...")
            time.sleep(3600)  # Sleep for 1 hour
            message_count = 0  # Reset counter

        # Random sleep to avoid detection
        time.sleep(random.uniform(10, 30))

    except Exception as e:
        print(f"❌ Failed to message {first_name}: {e}")
        continue

# Quit driver
driver.quit()
