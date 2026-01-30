
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

def find_selectors():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(options=options)
        print(f"Connected to: {driver.current_url}")
        
        # 1. Find Voicemail items
        vms = driver.find_elements(By.XPATH, "//*[contains(text(), 'Voicemail')]")
        if not vms:
            print("No 'Voicemail' elements found.")
            return

        for vm in vms:
            try:
                # Find the 'More' button near this voicemail
                # Often it's a child of the same parent or a sibling
                print(f"Checking near voicemail: {vm.text[:20]}...")
                
                # Check for buttons in the same parent bubble
                parent = vm.find_element(By.XPATH, "./ancestor::div[contains(@class, 'message') or contains(@class, 'bubble')]")
                more_btn = parent.find_element(By.XPATH, ".//button[contains(@class, 'more') or contains(@class, 'menu')]")
                
                print(f"Found 'More' button: {more_btn.get_attribute('class')}")
                
                # Hover to reveal if necessary, then click
                ActionChains(driver).move_to_element(more_btn).perform()
                more_btn.click()
                time.sleep(1)
                
                # Now look for "Download" in the whole page (as it might be in a portal)
                download_links = driver.find_elements(By.XPATH, "//*[contains(text(), 'Download')]")
                if download_links:
                    for dl in download_links:
                        if dl.is_displayed():
                            print(f"FOUND DOWNLOAD BUTTON! Tag: {dl.tag_name}, Class: {dl.get_attribute('class')}")
                            # Get a unique selector
                            # Try to find common attributes
                            print(f"HTML snippet: {dl.get_attribute('outerHTML')}")
                            return
                else:
                    print("Download button not found after clicking More.")
            except Exception as e:
                # print(f"Error checking VM: {e}")
                continue

    except Exception as e:
        print(f"Global Error: {e}")

if __name__ == "__main__":
    find_selectors()
