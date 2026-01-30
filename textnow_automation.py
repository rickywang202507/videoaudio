import os
import time
import json
import re
import base64
import requests
import random
import string
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuration
def get_randomized_message(templates=None):
    """Generates a unique message to avoid spam filters."""
    
    # 1. Random Greetings
    cn_greetings = ["尊敬的旅客您好", "您好", "尊敬的客户", "旅客您好", "Hello"]
    en_greetings = ["Dear Customer", "Hello", "Hi there", "Greetings", "Dear Traveler"]
    
    g_cn = random.choice(cn_greetings)
    g_en = random.choice(en_greetings)
    
    
    # Defaults if file missing
    raw_cn = "尊敬的旅客您好，很抱歉未能接听您的来电..."
    raw_en = "Sorry we missed your call..."
    
    # Try to load formatted templates from file or argument
    if templates:
        # Sort of a crude way: iterate keys and find "active": true
        # Default to standard_reply if none active found
        selected_key = "standard_reply"
        for key, tmpl in templates.items():
            if tmpl.get("active", False) == True:
                selected_key = key
                break
        
        target = templates.get(selected_key, {})
        raw_cn = target.get("content_cn", raw_cn)
        raw_en = target.get("content_en", raw_en)
    
    # 2. Random Ref ID (3 chars)
    ref_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    timestamp = datetime.now().strftime("%H%M")
    
    msg = f"""{g_cn}，
{raw_cn}

免责声明：本短信为系统自动回复。
[Ref: {ref_id}-{timestamp}]

{g_en},
{raw_en}

[Ref: {ref_id}]"""
    return msg

# Compatibility for existing code
SMS_TEMPLATE = get_randomized_message() # Initial load, but we should call function dynamically

import sys

class Logger(object):
    def __init__(self, filename="textnow_automation.log"):
        self.terminal = sys.stdout
        self.log = open(filename, "a", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = Logger()
sys.stderr = sys.stdout

from ai_service import AIService

class TextNowBot:
    def __init__(self, download_dir, download_all_voicemails=False, enable_reply=True, config=None):
        print(f"--- Session Started at {datetime.now()} ---")
        self.download_dir = download_dir
        self.download_all_voicemails = download_all_voicemails
        self.enable_reply = enable_reply
        
        self.templates = {}
        try:
            with open("templates.json", "r", encoding="utf-8") as f:
                self.templates = json.load(f)
            print("[Templates] Loaded custom templates from templates.json")
        except Exception as e:
            print(f"[Templates] Could not load templates.json: {e}")
        
        self.ai = None
        if config:
            try:
                self.ai = AIService(config)
                print("[AI] AI Service Initialized for message variations.")
            except Exception as e:
                print(f"[AI] Failed to init AI Service: {e}")

        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        
        if download_all_voicemails:
            print("[Mode] Download ALL voicemails (including read ones)")
        else:
            print("[Mode] Only process UNREAD missed calls/voicemails")
            
        self.options = webdriver.ChromeOptions()
        # Connect to existing Chrome instance on port 9222
        # This requires Chrome to be started with: chrome.exe --remote-debugging-port=9222
        self.options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        
        self.driver = None

    def start_browser(self):
        print("Connecting to existing Chrome instance (127.0.0.1:9222)...")
        try:
            self.driver = webdriver.Chrome(options=self.options)
            
            # Configure download behavior dynamically using CDP since we are attaching
            try:
                self.driver.execute_cdp_cmd('Page.setDownloadBehavior', {
                    'behavior': 'allow', 
                    'downloadPath': self.download_dir
                })
                print(f"Download path set to: {self.download_dir}")
            except Exception as e:
                print(f"Warning: Could not set download behavior: {e}")
                
        except Exception as e:
            print("ERROR: Failed to connect to Chrome.")
            print("make sure you have run 'run_chrome_debug.bat' and kept the window open.")
            raise e

    def close(self):
        # When attaching, we usually DON'T want to quit the driver exactly because it closes the window?
        # Actually driver.quit() closes the session and the browser usually. 
        # driver.close() closes the tab.
        # Since the user wants to 'keep' the browser, we should probably NOT call quit.
        # We'll just detach.
        pass

    def create_synthetic_missed_call(self, phone_number, missed_count=1):
        """Creates a text file record for missed calls (no voicemail)."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{date_str}_{phone_number}_missed.txt"
        filepath = os.path.join(self.download_dir, filename)
        
        # We overwrite even if exists to update count
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"Missed Calls: {missed_count}\n")
                f.write(f"Last Missed: {datetime.now().strftime('%H:%M:%S')}")
            print(f"    [Synthetic] Created missed call record: {filename} (Count: {missed_count})")
            
            # If we updated the count, we should force re-processing by deleting the old JSON if it exists
            # This logic assumes the dashboard views the JSON.
            # We don't know the exact path of the JSON easily here (it's in WAV_TXT_DIR usually?), 
            # BUT audio_processor.py handles that. 
            # Ideally we just create the .txt and let audio_processor scan it.
            return True
        except Exception as e:
            print(f"    [Error] Failed to create synthetic record: {e}")
            return False

    def download_voicemails(self, phone_number):
        """Finds and downloads voicemail audio files in the current conversation view.
           Returns: tuple (download_count, missed_call_count)
        """
        print(f"    [Action] Scanning for voicemails from {phone_number}...")
        try:
            # 1. Find all audio elements
            audios = self.driver.find_elements(By.TAG_NAME, "audio")
            download_count = 0
            
            if audios:
                # Use today's date for filename if we can't get it from UI easily
                date_str = datetime.now().strftime("%Y-%m-%d")
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }

                for idx, au in enumerate(audios):
                    try:
                        src = au.get_attribute("src")
                        if not src or "voicemail-media.textnow.com" not in src:
                            # Skip system sounds or other audio
                            continue
                        
                        # Create unique filename
                        filename = f"{date_str}_{phone_number}_{idx+1}.wav"
                        filepath = os.path.join(self.download_dir, filename)
                        
                        if os.path.exists(filepath):
                            # print(f"    [Skip] Voicemail already exists: {filename}")
                            continue
                        
                        print(f"    [Download] Fetching: {filename}...")
                        
                        # Direct download via requests (works because token is in URL)
                        resp = requests.get(src, headers=headers, timeout=15)
                        if resp.status_code == 200:
                            with open(filepath, "wb") as f:
                                f.write(resp.content)
                            print(f"    [Success] Saved voicemail: {filename} ({len(resp.content)} bytes)")
                            download_count += 1
                        else:
                            print(f"    [Error] Download failed for {filename} (Status: {resp.status_code})")
                    except Exception as ex:
                        print(f"    [Error] Problem with specific audio element: {ex}")
            
            # 2. If no audios downloaded, check for "Missed call" text bubbles
            missed_call_count = 0
            if download_count == 0:
                try:
                    # Look for bubbles containing "Missed call"
                    # Count them. We might want to limit to 'recent' ones but counting distinct elements is a good start.
                    missed_els = self.driver.find_elements(By.XPATH, "//div[contains(text(), 'Missed call')]")
                    missed_call_count = len(missed_els)
                    if missed_call_count > 0:
                        print(f"    [Info] No audio found, but found {missed_call_count} 'Missed call' events.")
                except:
                    pass

            return download_count, missed_call_count
            
        except Exception as e:
             print(f"    [Error] download_voicemails failed: {e}")
             return 0, 0
        except Exception as e:
            print(f"    [Error] in download_voicemails: {e}")
            return 0

    def has_replied_recently(self, phone, hours=8):
        """Check if we have replied to this number within the last N hours."""
        try:
            h_file = "replied_history.json"
            if not os.path.exists(h_file):
                return False
                
            with open(h_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
                
            current_time = datetime.now()
            
            for item in history:
                if item.get('phone') == phone:
                    last_reply_str = item.get('time')
                    if last_reply_str:
                        try:
                            last_reply_time = datetime.strptime(last_reply_str, "%Y-%m-%d %H:%M:%S")
                            diff = current_time - last_reply_time
                            if diff.total_seconds() < hours * 3600:
                                return True
                        except:
                            pass
            return False
        except Exception as e:
            print(f"    [Warning] Error checking history: {e}")
            return False

    def log_history(self, phone, status="Replied", note="Auto-reply sent"):
        """Log an action to the history file."""
        try:
            history_file = "replied_history.json"
            history_data = []
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    try:
                        history_data = json.load(f)
                    except: pass
            
            # Prepend new record
            record = {
                "phone": phone,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": status,
                "note": note
            }
            history_data.insert(0, record)
            
            # Keep only last 500 records
            history_data = history_data[:500]
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=4, ensure_ascii=False)
                
        except Exception as log_err:
            print(f"    [Warning] Failed to log history: {log_err}")

    def sync(self):
        # Ensure we are connected
        if self.driver is None:
            try:
                self.start_browser()
            except Exception as e:
                print(f"Connection failed: {e}")
                return

        try:
            # Check if we are already on the right page
            try:
                # If driver is dead, this property access will raise an exception, caught by outer try
                if "textnow.com/messaging" not in self.driver.current_url:
                    print("Navigating to TextNow Messaging...")
                    self.driver.get("https://www.textnow.com/messaging")
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking TextNow (already on page)...")
            except:
                self.driver.get("https://www.textnow.com/messaging")

            # print("Waiting for interface...") 
            # Commented out verbose log
            
            # Wait generically for ANY common element
            found_ui = False
            for attempt in range(5): # Reduced attempts for speed in loop
                try:
                    # Look for list, or header, or "new message" button
                    if self.driver.find_elements(By.XPATH, "//*[contains(@class, 'conversation')]") or \
                       self.driver.find_elements(By.XPATH, "//*[contains(text(), 'New Message')]") or \
                       self.driver.find_elements(By.ID, "recent-header-text"):
                        found_ui = True
                        break
                except:
                    pass
                time.sleep(1)
                
            if found_ui:
                print("Interface detected.")
            else:
                print("Warning: Could not detect standard UI elements. Script will attempt to proceed searching for items anyway.")
            
            time.sleep(3)
            
            # Find items using broad selectors
            # 2024 UI often uses 'conversation-container' or similar
            # Find items using broad selectors
            # The screenshot shows items have class like 'conversation-list-item' or similar container
            # We want to iterate through them and check their PREVIEW text first.
            
            items = self.driver.find_elements(By.XPATH, "//div[contains(@id, 'conversation-list-item')] | //div[contains(@class, 'conversation-list-item')] | //div[contains(@class, 'recent-conversation')]")
            
            # Try distinct selectors first
            # 2025/2026 UI uses 'uikit-summary-list__cell'
            items = self.driver.find_elements(By.XPATH, "//li[contains(@class, 'uikit-summary-list__cell')]")
            
            if not items:
                items = self.driver.find_elements(By.XPATH, "//div[contains(@id, 'conversation-list-item')] | //div[contains(@class, 'conversation-list-item')] | //div[contains(@class, 'recent-conversation')]")
            
            if not items:
                items = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'conversation-item')]")

            if len(items) == 0:
                print("  [DEBUGGING] 0 Items found with standard selectors. Starting Deep DOM Analysis...")
                
                # 1. Check if 'Missed call' exists anywhere
                try:
                    missed_els = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Missed call')]")
                    if missed_els:
                        print(f"  [DEBUG] Found {len(missed_els)} elements with 'Missed call' text.")
                        parent = missed_els[0].find_element(By.XPATH, "./..")
                        grandparent = parent.find_element(By.XPATH, "./..")
                        greatgrandparent = grandparent.find_element(By.XPATH, "./..")
                        
                        print(f"  [DEBUG] Element 0 Tag: {missed_els[0].tag_name}, Class: {missed_els[0].get_attribute('class')}")
                        print(f"  [DEBUG] Parent Tag: {parent.tag_name}, Class: {parent.get_attribute('class')}")
                        print(f"  [DEBUG] Grandparent Tag: {grandparent.tag_name}, Class: {grandparent.get_attribute('class')}")
                        print(f"  [DEBUG] GreatGrandparent Tag: {greatgrandparent.tag_name}, Class: {greatgrandparent.get_attribute('class')}")
                    else:
                        print("  [DEBUG] 'Missed call' text NOT found in DOM. Page might not be loaded or language is different.")
                except Exception as e:
                    print(f"  [DEBUG] Error analyzing DOM: {e}")
                
                # 2. Dump a small part of structure around the first visible text element that looks like a number
                # This is risky but useful.
            
            # Optimization: Only scan the recent 15 items to save time
            # As history grows, we don't need to scan year-old messages every 30 seconds.
            scan_limit = 30
            count_to_scan = min(len(items), scan_limit)
            print(f"Found {len(items)} conversations. Scanning top {count_to_scan} for efficiency...")
            
            count_processed = 0
            
            for i in range(count_to_scan):
                try:
                    # Re-find items to avoid StaleElementReferenceException
                    # MUST match the selector used to find 'items' initially (Step 101)
                    current_items = self.driver.find_elements(By.XPATH, "//li[contains(@class, 'uikit-summary-list__cell')]")
                    
                    if not current_items:
                        # Fallback
                        current_items = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'conversation-item')]")
                    
                    if i >= len(current_items): 
                        print(f"  [Debug] Index {i} out of bounds (found {len(current_items)} items). Stopping.")
                        break
                    
                    item = current_items[i]
                    
                    # 1. READ PREVIEW
                    preview_text = item.text.replace("\n", " ") or "[No Text]"
                    item_class = item.get_attribute("class") or "[No Class]"
                    
                    # Logging every item for debugging
                    print(f"  [{i}] Class: '{item_class}' | Text: {preview_text[:50]}...")

                    # FILTER: Only process "Missed call", "New voicemail", or "Voicemail"
                    # Sometimes the preview says "New voicemail" or just "Voicemail"
                    has_call_or_voicemail = any(keyword in preview_text for keyword in 
                                                ["Missed call", "New voicemail", "Voicemail"])
                    if not has_call_or_voicemail:
                        continue
                        
                    # FILTER: Strict "Unread" / "New" check
                    is_unread_candidate = False
                    
                    # Method 1: Check class on the item itself (sometimes it has 'unread' modifier)
                    if "unread" in item_class.lower():
                        is_unread_candidate = True
                        
                    # Method 2: Look for common "dot" or "badge" elements inside
                    if not is_unread_candidate:
                        try:
                            # We search for ANY child that looks like an unread indicator.
                            indicators = item.find_elements(By.XPATH, ".//*[contains(@class, 'indicator') or contains(@class, 'badge') or contains(@class, 'dot')]")
                            if indicators:
                                print(f"    [Debug] Found indicator: {indicators[0].get_attribute('class')}")
                                is_unread_candidate = True
                        except:
                            pass
                            
                    # Method 3: Check font weight (The most reliable visual check for 'bold' text)
                    if not is_unread_candidate:
                        try:
                            # Check text elements. Usually unread items have bold text (700+)
                            text_els = item.find_elements(By.XPATH, ".//*[string-length(text()) > 0]")
                            for t in text_els:
                                fw = t.value_of_css_property("font-weight")
                                # 700 is bold. browsers might return 'bold', 'bolder', or numeric string
                                if fw in ['bold', 'bolder', '700', '800', '900'] or (fw.isdigit() and int(fw) >= 600):
                                    is_unread_candidate = True
                                    print(f"    [Debug] Found Bold Text (fw={fw}) -> Unread")
                                    break
                        except:
                            pass

                    # If download_all_voicemails is True, process even read items
                    if not is_unread_candidate and not self.download_all_voicemails:
                        print(f"    [Skip] Item does not appear to be UNREAD (No 'unread' class, badge, or bold text).")
                        continue
                    
                    # Mark if this is a read item being processed
                    if not is_unread_candidate:
                        print(f"  >> Processing READ voicemail (download_all mode): {preview_text[:20]}...")

                    # 2. It IS a missed call/voicemail. Click to open details.
                    if is_unread_candidate:
                        print(f"  >> Found UNREAD Missed Call/Voicemail: {preview_text[:20]}... Clicking.")
                    else:
                        print(f"  >> Opening conversation: {preview_text[:20]}... Clicking.")
                    item.click()
                    time.sleep(1.5) # Wait for right panel to load
                    
                    # 3. Get Phone Number (Right Panel Header)
                    try:
                        # Find all candidates, check for visibility
                        header_candidates = self.driver.find_elements(By.XPATH, "//div[@id='contact-header']//h2 | //span[contains(@class, 'name')] | //div[contains(@class, 'header-text')]")
                        phone_number = "Unknown"
                        
                        for cand in header_candidates:
                            try:
                                if cand.is_displayed():
                                    raw_text = cand.text.strip()
                                    # Ensure it looks like a phone number or name
                                    if len(raw_text) > 0:
                                        img_phone = re.sub(r'[^0-9+]', '', raw_text)
                                        if len(img_phone) > 5: # minimal length check
                                            phone_number = img_phone
                                            # print(f"    [Debug] Found visible header: {raw_text} -> {phone_number}")
                                            break
                            except:
                                continue
                                
                        # Fallback if no visible one found (maybe standard find)
                        if phone_number == "Unknown" and header_candidates:
                             phone_number = re.sub(r'[^0-9+]', '', header_candidates[0].text.strip())

                    except:
                        phone_number = "Unknown"

                    # 4. CHECK DUPLICATE REPLY (8 HOURS)
                    if self.has_replied_recently(phone_number, hours=8):
                        print(f"    [Skip] Already replied to {phone_number} in the last 8 hours.")
                        # Still proceed to download VM if needed, but skip sending SMS
                        self.download_voicemails(phone_number)
                        continue
                        
                    if is_unread_candidate or self.download_all_voicemails:
                        try:
                            # Wait for right panel to load content
                            print("    [Debug] Waiting for conversation history to load...")
                            try:
                                WebDriverWait(self.driver, 5).until(
                                    EC.presence_of_element_located((By.ID, "message-input")) 
                                    or EC.presence_of_element_located((By.CSS_SELECTOR, ".message-history"))
                                )
                            except:
                                print("    [Debug] Wait timeout (might be slow connection), continuing...")

                            history_text = ""
                            # Try to find the specific container for the current conversation
                            try:
                                # Strategy A: Look for the main chat area (Added more generic selectors)
                                history_els = self.driver.find_elements(By.CSS_SELECTOR, 
                                    ".message-history, .conversation-list, [role='main'], main"
                                )
                                
                                if history_els:
                                    # Pick the one with the most text if multiple found?
                                    # Usually there is only one visible main container
                                    for h in history_els:
                                        if h.is_displayed():
                                            history_text += h.text + "\n"
                                    
                                    print(f"    [Debug] Found {len(history_els)} history container(s). Total text length: {len(history_text)}")
                                else:
                                    print("    [Debug] No history containers found via CSS selectors.")
                                    
                                    # Strategy B: Find Input box and look up
                                    try:
                                        inp = self.driver.find_element(By.ID, "message-input")
                                        container = inp.find_element(By.XPATH, "./ancestor::div[contains(@class, 'conversation')] | ./ancestor::main")
                                        history_text = container.text
                                        print(f"    [Debug] Found history via Input Box parent. Length: {len(history_text)}")
                                    except:
                                        print("    [Debug] Strategy B failed.")
                            except Exception as el_err:
                                print(f"    [Error] Error finding elements: {el_err}")
                            
                            
                            # Debug: Print a snippet of history text to checking what we are reading
                            clean_hist = history_text.replace('\n', ' ')[:100]
                            # print(f"    [Debug] History snippet: {clean_hist}...")
                            
                            # --- Check for VoiceMails or Missed Calls ---
                            # We check this EARLY so we capture voicemails even if we skip reply later.
                            downloaded, missed_count = self.download_voicemails(phone_number)
                            if downloaded == 0 and missed_count > 0:
                                self.create_synthetic_missed_call(phone_number, missed_count)
                            # --------------------------------------------
                            
                            # More flexible matching
                            has_en_keyword = "missed your call" in history_text or "Missed your call" in history_text
                            has_cn_keyword = "自动回复" in history_text or "China Eastern" in history_text or "china eastern" in history_text
                            
                            already_replied = has_en_keyword or has_cn_keyword
                            
                            if already_replied:
                                print(f"    [Skip SMS] Already replied to {phone_number}.")
                                
                                # --- Auto-Import History ---
                                # If we see it's replied in UI but not in our JSON, add it.
                                try:
                                    h_file = "replied_history.json"
                                    h_data = []
                                    if os.path.exists(h_file):
                                        with open(h_file, 'r', encoding='utf-8') as f:
                                            try: h_data = json.load(f)
                                            except: pass
                                    
                                    # Check if phone exists
                                    if not any(item.get('phone') == phone_number for item in h_data):
                                        print(f"    [History] Importing existing reply for {phone_number}")
                                        h_data.insert(0, {
                                            "phone": phone_number,
                                            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                            "status": "Previously Replied",
                                            "note": "Imported from scan"
                                        })
                                        with open(h_file, 'w', encoding='utf-8') as f:
                                            json.dump(h_data, f, indent=4, ensure_ascii=False)
                                except Exception as e:
                                    print(f"    [Warning] History import failed: {e}")
                                # ---------------------------
                                
                            elif is_unread_candidate:
                                # Only send SMS if it is truly UNREAD and NOT replied yet
                                print(f"    [ACTION] Processing message for {phone_number}...")
                                
                                if not self.enable_reply:
                                    print(f"    [Info] Auto-Reply DISABLED. Marking as skipped in history.")
                                    # Log as skipped so we track that we saw it
                                    self.log_history(phone_number, "Skipped-NoReply", "User disabled auto-reply")
                                        
                                else:
                                    # REPLIES ENABLED - Proceed to send
                                    print(f"    [ACTION] Sending SMS to {phone_number}...")
                                    # Find Input Box
                                    input_box = None
                                    try:
                                        input_box = self.driver.find_element(By.ID, "message-input")
                                    except:
                                        try:
                                            input_box = self.driver.find_element(By.TAG_NAME, "textarea")
                                        except:
                                            pass
                                            
                                    if input_box:
                                        # [Anti-Bot] Human Delay: Think before clicking (2-5s)
                                        time.sleep(random.uniform(2.0, 5.0))

                                        # Ensure focus and clear existing content
                                        input_box.click()
                                        time.sleep(random.uniform(0.5, 1.5))
                                        
                                        input_box.send_keys(Keys.CONTROL + "a")
                                        input_box.send_keys(Keys.BACKSPACE)
                                        time.sleep(0.5)
                                        
                                        # Generate UNIQUE randomized message
                                        base_message = get_randomized_message(self.templates)
                                        dynamic_message = base_message
                                        
                                        # Apply AI Generation if available
                                        ai_reply = None
                                        if self.ai:
                                            # Try to generate context-aware (language-aware) reply first
                                            if history_text and len(history_text) > 10:
                                                print("    [AI] Analyzing history for language-aware reply...")
                                                ai_reply = self.ai.generate_reply_from_history(history_text, template_text=base_message)
                                            
                                            # If history analysis failed or returned None, fallback to Paraphrasing standard template
                                            if not ai_reply:
                                                print("    [AI] generating unique variation of standard template...")
                                                ai_reply = self.ai.paraphrase_content(base_message)
                                        
                                        if ai_reply:
                                            dynamic_message = ai_reply
                                        else:
                                            dynamic_message = base_message
                                        
                                        self.driver.execute_script("""
                                            var text = arguments[0];
                                            var el = arguments[1];
                                            el.focus();
                                            if (el.tagName === 'TEXTAREA' || el.tagName === 'INPUT') {
                                                el.value = text;
                                                el.dispatchEvent(new Event('input', { bubbles: true }));
                                            } else {
                                                document.execCommand('insertText', false, text);
                                            }
                                        """, dynamic_message, input_box)
                                        
                                        # [Anti-Bot] Human Delay: Proofread before sending (3-7s)
                                        time.sleep(random.uniform(3.0, 7.0))
                                        
                                        # Now send the complete message
                                        input_box.send_keys(Keys.ENTER)
                                        count_processed += 1
                                        print("    [Success] SMS Sent.")
                                        
                                        # --- Log to history file ---
                                        self.log_history(phone_number, "Replied", "Auto-reply sent")
                                        # ---------------------------
                                        
                                        time.sleep(2)
                                    else:
                                        print(f"    [Error] Could not find input box.")
                            
                            else:
                                # It's read, not replied (maybe manual conversation), but we do nothing
                                print(f"    [Info] Read message, not auto-replied. Skipping.")

                        except Exception as e:
                            print(f"    [Error] sending SMS: {e}")
                    else:
                        print(f"    [Skip] Read message (skipped).")
                    
                    # 5. Voicemail Download - Re-enabled
                    # Always try to download audio if it's a voicemail/missed call,
                    # even if it's read (if download_all_voicemails is True).
                    # MOVED UP
                    
                except Exception as e:
                    print(f"  [Error] processing item {i}: {e}")
                    continue
            
            print(f"Sync complete. Sent {count_processed} replies.")

        except Exception as e:
            print(f"Global Error: {e}")
            # Reset driver to force reconnection next cycle
            self.driver = None
        finally:
            # print("Sync session complete.")
            pass
            
if __name__ == "__main__":
    # Load config to get path
    config_path = "config.json"
    audio_dir = "C:\\Antigravity\\VideoAudioConvert\\data\\PhoneReCO"
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            cfg = json.load(f)
            # Use WAV_DIR if available as that seems to be the Phone Recording directory
            audio_dir = cfg.get("WAV_DIR", audio_dir)
    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-reply", action="store_true", help="Disable auto-replies (Download only)")
    args = parser.parse_args()
    
    enable_reply = not args.no_reply
    print(f"Starting TextNow Bot. Auto-Reply Enabled: {enable_reply}")

    # Load config to get path
    config_path = "config.json"
    audio_dir = "C:\\Antigravity\\VideoAudioConvert\\data\\PhoneReCO"
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            cfg = json.load(f)
            # Use WAV_DIR if available as that seems to be the Phone Recording directory
            audio_dir = cfg.get("WAV_DIR", audio_dir)
    
    # Initialize bot
    bot = TextNowBot(audio_dir, download_all_voicemails=False, enable_reply=enable_reply, config=cfg)
    
    print("--- 启动 TextNow 自动扫描监控 ---")
    print("按 Ctrl+C 停止程序")
    
    # Run sync loop
    try:
        while True:
            bot.sync()
            
            # Wait 30 seconds
            wait_sec = 30
            # print(f"Waiting {wait_sec} seconds...")
            time.sleep(wait_sec)
            
    except KeyboardInterrupt:
        print("\nStopping Monitor...")
    except Exception as e:
        print(f"\nFatal Error: {e}")
