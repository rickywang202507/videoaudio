import os
import json

def verify_config():
    config_path = "config.json"
    if not os.path.exists(config_path):
        print(f"❌ Error: {config_path} not found.")
        return False
        
    with open(config_path, 'r') as f:
        config = json.load(f)
        
    paths = [
        config.get("VIDEO_DIR"),
        config.get("AUDIO_DIR"),
        config.get("TXT_DIR"),
        config.get("WAV_DIR"),
        config.get("WAV_TXT_DIR")
    ]
    
    print("Checking paths...")
    for p in paths:
        if not p:
            print("❌ Error: Missing path in config.")
            return False
            
        try:
            if not os.path.exists(p):
                print(f"📁 Creating: {p}")
                os.makedirs(p, exist_ok=True)
            print(f"✅ Success: {p}")
        except Exception as e:
            print(f"❌ Failed to access/create {p}: {e}")
            return False
            
    print("\n🎉 All paths verified and accessible!")
    return True

if __name__ == "__main__":
    verify_config()
