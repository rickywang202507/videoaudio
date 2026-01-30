
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

def capture_audio_urls():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(options=options)
        print(f"Connected to: {driver.current_url}")
        
        # Look for all audio elements
        audios = driver.find_elements(By.TAG_NAME, "audio")
        print(f"Found {len(audios)} audio elements.")
        
        found_voicemail = False
        for i, au in enumerate(audios):
            src = au.get_attribute("src")
            # The summary said voicemail URLs contain voicemail-media.textnow.com
            if src and "voicemail-media.textnow.com" in src:
                print(f"VM [{i}] URL: {src[:100]}...")
                found_voicemail = True
                
        if not found_voicemail:
            print("No voicemail audio sources found in current view.")
            # Let's check for sources inside the current conversation history
            # Maybe they are not as <audio> but as links or data attributes
            print("Searching for data-src or other attributes...")
            elements = driver.find_elements(By.XPATH, "//*[@src or @data-src]")
            for el in elements:
                src = el.get_attribute("src") or el.get_attribute("data-src")
                if src and "voicemail-media" in src:
                    print(f"Found via attribute: {src[:100]}...")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    capture_audio_urls()
