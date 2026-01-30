
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

def explore():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(options=options)
        print(f"Connected to: {driver.current_url}")
        
        # Look for voicemail bubbles
        # Often voicemails have a data-testid or a specific class
        print("Searching for elements containing 'Voicemail'...")
        elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Voicemail')]")
        
        for i, el in enumerate(elements[:10]):
            try:
                print(f"[{i}] Tag: {el.tag_name}, Class: {el.get_attribute('class')}, Text: {el.text[:50]}")
                # Print outerHTML of parent to see structure
                parent = el.find_element(By.XPATH, "./..")
                # print(f"    Parent HTML: {parent.get_attribute('outerHTML')[:200]}...")
            except:
                pass

        # Look for buttons or icons near voicemail text
        print("\nSearching for potential menu buttons (three dots, etc.)...")
        menus = driver.find_elements(By.XPATH, "//button[contains(@class, 'more') or contains(@class, 'menu') or contains(@aria-label, 'More')]")
        for i, m in enumerate(menus[:10]):
            print(f"Menu [{i}] Class: {m.get_attribute('class')}, Label: {m.get_attribute('aria-label')}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    explore()
