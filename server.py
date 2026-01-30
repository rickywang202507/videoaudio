import os
import json
import sys
import subprocess
import socket
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from audio_processor import AudioProcessor
from typing import List, Optional

app = FastAPI(title="China Eastern Call Processor")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
processor = AudioProcessor(config_path=CONFIG_PATH)
print("--- Server Initialized with FFmpeg robustness fix ---")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Serve static files for UI
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

class ConfigUpdateRequest(BaseModel):
    active_ai: Optional[str] = None
    VIDEO_DIR: Optional[str] = None
    AUDIO_DIR: Optional[str] = None
    TXT_DIR: Optional[str] = None
    WAV_DIR: Optional[str] = None
    WAV_TXT_DIR: Optional[str] = None

@app.get("/api/config")
def get_config():
    """Returns the current configuration."""
    return processor.config

@app.post("/api/config")
def update_config(req: ConfigUpdateRequest):
    """Updates configuration."""
    
    # Update AI Provider if provided
    if req.active_ai:
        if req.active_ai not in processor.config.get("AI_PROVIDERS", {}):
            raise HTTPException(status_code=400, detail="Invalid AI provider")
        processor.config["ACTIVE_AI"] = req.active_ai

    # Update Directories if provided
    if req.VIDEO_DIR: processor.config["VIDEO_DIR"] = req.VIDEO_DIR
    if req.AUDIO_DIR: processor.config["AUDIO_DIR"] = req.AUDIO_DIR
    if req.TXT_DIR: processor.config["TXT_DIR"] = req.TXT_DIR
    if req.WAV_DIR: processor.config["WAV_DIR"] = req.WAV_DIR
    if req.WAV_TXT_DIR: processor.config["WAV_TXT_DIR"] = req.WAV_TXT_DIR
    
    config_path = os.path.join(BASE_DIR, "config.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(processor.config, f, indent=4)
    
    # Re-initialize AI Service in processor if AI changed
    if req.active_ai:
        from ai_service import AIService
        processor.ai = AIService(processor.config)
    
    return {"status": "success", "config": processor.config}

class ReanalyzeRequest(BaseModel):
    file_name: str
    source_type: str

@app.post("/api/reanalyze")
def reanalyze_file(req: ReanalyzeRequest):
    """Manually triggers AI re-analysis for a specific file."""
    try:
        processor.reload_config()
        print(f"Manual re-analysis trigger: {req.file_name}")
        result = processor.reanalyze(req.file_name, req.source_type)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/api/files")
def get_files():
    """Returns a list of all processed files and their analysis."""
    processor.reload_config()
    all_results = []
    
    # Check TXT_DIR (from videos) and WAV_TXT_DIR (from phone recordings)
    dirs_to_check = [
        {"path": processor.config["TXT_DIR"], "type": "Video"},
        {"path": processor.config["WAV_TXT_DIR"], "type": "Phone"}
    ]
    
    for d_info in dirs_to_check:
        d = d_info["path"]
        if os.path.exists(d):
            json_files = [f for f in os.listdir(d) if f.endswith(".json")]
            for jf in json_files:
                try:
                    json_full_path = os.path.join(d, jf)
                    with open(json_full_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        data["source_type"] = d_info["type"]
                        
                        # Determine date from original file
                        base_name = os.path.splitext(jf)[0]
                        source_path = None
                        
                        if d_info["type"] == "Video":
                            video_dir = processor.config["VIDEO_DIR"]
                            # Try common video extensions
                            for ext in ['.mp4', '.mkv', '.mov', '.mpeg', '.MP4', '.MKV', '.MOV', '.MPEG']:
                                v_chk = os.path.join(video_dir, f"{base_name}{ext}")
                                if os.path.exists(v_chk):
                                    source_path = v_chk
                                    break
                        elif d_info["type"] == "Phone":
                            wav_dir = processor.config["WAV_DIR"]
                            w_chk = os.path.join(wav_dir, f"{base_name}.wav")
                            if os.path.exists(w_chk):
                                source_path = w_chk
                        
                        # Get timestamp
                        from datetime import datetime
                        if source_path:
                            ts = os.path.getmtime(source_path)
                        else:
                            ts = os.path.getmtime(json_full_path)
                            
                        data["file_date"] = datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                        data["timestamp"] = ts
                        
                        all_results.append(data)
                except Exception as e:
                    print(f"Error reading {jf}: {e}")
    
    return all_results

class ForceRequest(BaseModel):
    file_name: str
    source_type: str
    language: Optional[str] = None  # Optional: "en", "zh", etc.

class CalledBackRequest(BaseModel):
    file_name: str
    source_type: str
    status: bool

@app.post("/api/convert/mp4-to-mp3")
def force_mp4_to_mp3(req: ForceRequest):
    """Force re-extract MP3 from Video."""
    processor.reload_config()
    if req.source_type != "Video":
        # ... existing logic ...
        raise HTTPException(status_code=400, detail="Only Video source supports MP4->MP3")
    
    # Needs to find original video file extensions
    video_dir = processor.config["VIDEO_DIR"]
    found_video = None
    for ext in ['.mp4', '.mkv', '.mov', '.mpeg', '.MP4', '.MKV', '.MOV', '.MPEG']:
        v_path = os.path.join(video_dir, f"{req.file_name}{ext}")
        if os.path.exists(v_path):
            found_video = v_path
            break
            
    if not found_video:
        raise HTTPException(status_code=404, detail="Original video file not found")
        
    mp3_path = processor.process_video_to_mp3(found_video, force=True)
    if not mp3_path:
        raise HTTPException(status_code=500, detail="Failed to extract MP3")
        
    return {"status": "success", "message": "MP3 extracted"}

@app.post("/api/convert/audio-to-txt")
def force_audio_to_txt(req: ForceRequest):
    """Force re-transcribe Audio to TXT."""
    try:
        processor.reload_config()
        
        if req.source_type == "Video":
            audio_path = os.path.join(processor.config["AUDIO_DIR"], f"{req.file_name}.mp3")
            out_dir = processor.config["TXT_DIR"]
        elif req.source_type == "Phone":
            audio_path = os.path.join(processor.config["WAV_DIR"], f"{req.file_name}.wav")
            out_dir = processor.config["WAV_TXT_DIR"]
        else:
            raise HTTPException(status_code=400, detail="Invalid source type")
            
        if not os.path.exists(audio_path):
            raise HTTPException(status_code=404, detail=f"Audio file not found: {audio_path}")
            
        print(f"Manual transcription trigger: {req.file_name} (Language: {req.language})")
        result = processor.transcribe(audio_path, out_dir, force=True, language=req.language)
        
        if not result:
            raise HTTPException(status_code=500, detail="Transcription failed. Check server console for errors.")
            
        return result
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/api/audio/{source_type}/{file_name}")
def get_audio(source_type: str, file_name: str):
    """Serves the actual audio file."""
    if source_type == "Video":
        path = os.path.join(processor.config["AUDIO_DIR"], f"{file_name}.mp3")
    elif source_type == "Phone":
        path = os.path.join(processor.config["WAV_DIR"], f"{file_name}.wav")
    else:
        raise HTTPException(status_code=400, detail="Invalid source type")

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(path)

@app.delete("/api/files/{source_type}/{file_name}")
def delete_file(source_type: str, file_name: str):
    """Deletes a record and all its associated files."""
    success = processor.delete_record(file_name, source_type)
    if not success:
        # It's possible files are already gone, but we return success to clear UI
        return {"status": "success", "message": "Record cleaned up (files might be already missing)"}
    return {"status": "success", "message": f"Record {file_name} deleted successfully"}

@app.post("/api/called-back")
def update_called_back(req: CalledBackRequest):
    """Updates the called back status for a record."""
    success = processor.set_called_back(req.file_name, req.source_type, req.status)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update status")
    return {"status": "success", "called_back": req.status}

@app.post("/api/process")
async def run_processing():
    """Triggers the background processing of new files."""
    try:
        processor.reload_config()
        processor.process_all()
        return {"status": "success", "message": "Processing completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import socket

def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def launch_chrome():
    if is_port_open(9222):
        print("Chrome debugger already running on 9222.")
        return

    print("Launching Chrome from Server...")
    # Try to find chrome
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
    ]
    
    chrome_exe = "chrome.exe" # Fallback to PATH
    for p in chrome_paths:
        if os.path.exists(p):
            chrome_exe = p
            break
            
    profile_dir = os.path.join(BASE_DIR, "chrome_profile_debug")
    if not os.path.exists(profile_dir):
        os.makedirs(profile_dir)
        
    cmd = [
        chrome_exe,
        "--new-window", 
        "--remote-debugging-port=9222",
        "--disable-blink-features=AutomationControlled",
        "--exclude-switches=enable-automation",
        "--disable-infobars",
        "--start-maximized",
        f"--user-data-dir={profile_dir}"
    ]
    
    try:
        subprocess.Popen(cmd)
        import time
        time.sleep(2) # Wait for launch
    except Exception as e:
        print(f"Failed to launch Chrome: {e}")

    except Exception as e:
        print(f"Failed to launch Chrome: {e}")

# Global reference to the automation process
TEXTNOW_PROCESS = None

@app.post("/api/sync-textnow")
async def sync_textnow(request: Request):
    """Triggers the TextNow automation script. Restarts if already running."""
    # Parse options
    try:
        body = await request.json()
    except:
        body = {}
        
    enable_reply = body.get("enable_reply", True)
    
    global TEXTNOW_PROCESS
    
    # 1. Kill existing process if running
    if TEXTNOW_PROCESS is not None:
        status = TEXTNOW_PROCESS.poll()
        if status is None:
            # It's still running
            print("Stopping existing TextNow process...")
            try:
                TEXTNOW_PROCESS.terminate()
                import time
                time.sleep(1)
                if TEXTNOW_PROCESS.poll() is None:
                    TEXTNOW_PROCESS.kill()
                print("Existing process stopped.")
            except Exception as e:
                print(f"Error stopping process: {e}")
    
    # 2. Ensure Chrome is running
    launch_chrome()
    
    script_path = os.path.join(BASE_DIR, "textnow_automation.py")
    log_path = os.path.join(BASE_DIR, "textnow_automation.log")
    
    try:
        # Run in separate process, HIDDEN (no new console window)
        # CREATE_NO_WINDOW = 0x08000000
        creation_flags = 0x08000000 if sys.platform == 'win32' else 0
        
        # We redirect stdout/stderr to the log file so we can debug if needed
        # (Though the script also logs to the file itself, dual logging might cause contention
        #  but usually appending is safe-ish. Better to let script handle logging or redirect here.)
        # Since script handles logging to 'textnow_automation.log', we might just let it run.
        # However, to be safe against crash output:
        
        
        with open(log_path, "a", encoding="utf-8") as f:
            cmd = [sys.executable, script_path]
            if not enable_reply:
                cmd.append("--no-reply")
                
            TEXTNOW_PROCESS = subprocess.Popen(
                cmd, 
                cwd=BASE_DIR, 
                creationflags=creation_flags,
                stdout=f,
                stderr=f
            )
            
        return {"status": "success", "message": f"TextNow Service (Re)Started. Reply: {enable_reply}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/replied-history")
def get_replied_history():
    """Returns the history of auto-replied numbers."""
    history_path = os.path.join(BASE_DIR, "replied_history.json")
    if not os.path.exists(history_path):
        return []
    
    try:
        with open(history_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading history: {e}")
        return []

@app.get("/")
def read_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    return FileResponse(index_path)

# Path to static folder
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.post("/api/textnow-manual-send")
async def textnow_manual_send(request: Request):
    """Sends a custom message to the currently selected TextNow conversation."""
    try:
        data = await request.json()
        message = data.get("message", "").strip()
        
        if not message:
            return {"success": False, "error": "Message is empty"}
        
        # Create a temporary script to send the message
        script_path = os.path.join(os.path.dirname(__file__), "temp_manual_send.py")
        
        script_content = r'''
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

MESSAGE = """{message}"""

options = webdriver.ChromeOptions()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

try:
    driver = webdriver.Chrome(options=options)
    
    # Find input box
    input_box = None
    try:
        input_box = driver.find_element(By.ID, "message-input")
    except:
        try:
            input_box = driver.find_element(By.TAG_NAME, "textarea")
        except:
            pass
    
    if not input_box:
        print("ERROR: Input box not found")
        exit(1)
    
    # Ensure focus and clear existing content
    input_box.click()
    time.sleep(0.2)
    input_box.send_keys(Keys.CONTROL + "a")
    input_box.send_keys(Keys.BACKSPACE)
    time.sleep(0.2)
    
    # Use Javascript to insert the entire text block at once.
    driver.execute_script("""
        var text = arguments[0];
        var el = arguments[1];
        el.focus();
        if (el.tagName === 'TEXTAREA' || el.tagName === 'INPUT') {
            el.value = text;
            el.dispatchEvent(new Event('input', { bubbles: true }));
        } else {
            document.execCommand('insertText', false, text);
        }
    """, MESSAGE, input_box)
    
    time.sleep(1.0)
    input_box.send_keys(Keys.ENTER)
    print("SUCCESS")
    
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)
'''.replace('{message}', message)
        
        # Write temp script
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # Execute script
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Clean up temp script
        try:
            os.remove(script_path)
        except:
            pass
        
        if "SUCCESS" in result.stdout:
            return {"success": True}
        else:
            error_msg = result.stderr or result.stdout or "Unknown error"
            return {"success": False, "error": error_msg}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    import sys
    import asyncio
    
    # Fix for Windows asyncio loop closing error (AssertionError: assert self._sockets is not None)
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        uvicorn.run(app, host="127.0.0.1", port=8000)
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
