from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time

# Set your LinkedIn login credentials
username = "your_email@example.com"
password = "your_password"

# Initialize WebDriver
driver = webdriver.Chrome(executable_path="path_to_chromedriver")  # Replace with your chromedriver path
driver.get("https://www.linkedin.com/login")

# Log in to LinkedIn
driver.find_element(By.ID, "username").send_keys(username)
driver.find_element(By.ID, "password").send_keys(password)
driver.find_element(By.XPATH, "//button[@type='submit']").click()
time.sleep(3)

# Navigate to the "My Network" page
driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")
time.sleep(5)

# Scroll to load all connections
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Extract connection names and profile links
connections = driver.find_elements(By.XPATH, "//a[@class='mn-connection-card__link']")
data = []

for connection in connections:
    name = connection.find_element(By.XPATH, ".//span[@class='mn-connection-card__name']").text
    profile_url = connection.get_attribute("href")
    data.append({"Name": name, "Profile URL": profile_url})

# Save data to CSV
df = pd.DataFrame(data)
df.to_csv("linkedin_connections.csv", index=False)

print("Scraping complete! Connections saved to linkedin_connections.csv")

# Quit the driver
driver.quit()
