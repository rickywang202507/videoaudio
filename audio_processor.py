
import os
import subprocess
import json

# --- VERY EARLY FFmpeg Discovery ---
# This MUST run before whisper or moviepy imports as they may check environment on load
def find_ffmpeg_early():
    try:
        # Check standard PATH first
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except:
        # Search WinGet and common locations
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        winget_path = os.path.join(local_app_data, "Microsoft", "WinGet", "Packages")
        
        if os.path.exists(winget_path):
            # Prioritize Gyan.FFmpeg which we installed earlier
            for root, dirs, files in os.walk(winget_path):
                if "ffmpeg.exe" in files:
                    bin_dir = os.path.abspath(root)
                    os.environ["PATH"] = bin_dir + os.pathsep + os.environ["PATH"]
                    os.environ["FFMPEG_BINARY"] = os.path.join(bin_dir, "ffmpeg.exe")
                    print(f"--- Global FFmpeg Discovery: Found and configured: {bin_dir} ---")
                    return True
        return False

find_ffmpeg_early()

# Now import libraries that depend on ffmpeg
import whisper
from moviepy import VideoFileClip
from ai_service import AIService

class AudioProcessor:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.reload_config()
        self.whisper_model = None

    def reload_config(self):
        """Reloads configuration from disk."""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.ai = AIService(self.config)

    def _get_whisper(self):
        if self.whisper_model is None:
            print("Loading Whisper model...")
            self.whisper_model = whisper.load_model("base")
        return self.whisper_model

    def ensure_dirs(self):
        dirs = [
            self.config["AUDIO_DIR"], 
            self.config["TXT_DIR"], 
            self.config["WAV_TXT_DIR"]
        ]
        for d in dirs:
            if not os.path.exists(d):
                os.makedirs(d)

    def get_file_path(self, file_name, source_type, ext=".json"):
        """Get path to the JSON/TXT result file."""
        out_dir = self.config["TXT_DIR"] if source_type == "Video" else self.config["WAV_TXT_DIR"]
        return os.path.join(out_dir, f"{file_name}{ext}")

    def set_called_back(self, file_name, source_type, status):
        """Updates the called_back status in the analysis JSON."""
        json_path = self.get_file_path(file_name, source_type, ".json")
        if not os.path.exists(json_path):
            return False
            
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            data["called_back"] = status
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error updating called_back status: {e}")
            return False

    def process_video_to_mp3(self, video_path, force=False):
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        mp3_path = os.path.join(self.config["AUDIO_DIR"], f"{base_name}.mp3")
        
        if os.path.exists(mp3_path) and not force:
            print(f"  [Jump] 音频已存在: {base_name}.mp3")
            return mp3_path

        print(f"  [Extract] 正在提取音频: {base_name}")
        try:
            video = VideoFileClip(video_path)
            if video.audio:
                video.audio.write_audiofile(mp3_path, logger=None)
                video.close()
                return mp3_path
            video.close()
        except Exception as e:
            print(f"Error converting video {video_path}: {e}")
        return None

    def reanalyze(self, base_name, source_type):
        """Forces a re-analysis of an existing transcription."""
        output_dir = self.config["TXT_DIR"] if source_type == "Video" else self.config["WAV_TXT_DIR"]
        txt_path = os.path.join(output_dir, f"{base_name}.txt")
        json_path = os.path.join(output_dir, f"{base_name}.json")

        if not os.path.exists(txt_path):
            return {"error": "Transcription text file not found."}

        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                text = f.read()

            # Skip if text is too short (empty sound or bad transcription)
            if len(text.strip()) < 5:
                print(f"  [AI] Skip analysis: Text too short ({len(text.strip())} chars)")
                analysis = {
                    "summary": "Skipped (Content too short)",
                    "is_urgent": False,
                    "urgency_reason": "Content length < 5 chars",
                    "detected_language": "Unknown",
                    "suggested_reply": ""
                }
            else:
                # AI Analysis
                print(f"  [AI Re-analyze] 正在重新分析: {base_name}")
                analysis = self.ai.analyze_transcription(text)
            
            analysis["text"] = text
            analysis["file_name"] = base_name

            # Save analysis
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(analysis, f, ensure_ascii=False, indent=4)

            return analysis
        except Exception as e:
            print(f"Error reanalyzing {base_name}: {e}")
            return {"error": str(e)}

    def transcribe(self, audio_path, output_dir, force=False, language=None):
        # Handle language string variations
        if isinstance(language, str):
            lang_clean = language.strip().lower()
            if lang_clean in ["auto", "", "null", "none"]:
                language = None
            else:
                language = lang_clean

        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        txt_path = os.path.join(output_dir, f"{base_name}.txt")
        json_path = os.path.join(output_dir, f"{base_name}.json")

        if os.path.exists(txt_path) and os.path.exists(json_path) and not force:
            print(f"  [Jump] 文字已存在: {base_name}.txt")
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        print(f"  [Whisper] 正在转录文字: {base_name} (Language: {language or 'Auto'}) ...")
        
        if not os.path.exists(audio_path):
            print(f"  [Error] 音频文件不存在: {audio_path}")
            return None

        try:
            model = self._get_whisper()
            # Whisper call should now see updated PATH for ffmpeg
            result = model.transcribe(audio_path, verbose=True, language=language)
            text = result["text"]

            # Save raw text
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)

            # Check length - skip AI if too short
            if len(text.strip()) < 5:
                print(f"  [AI] Skip analysis: Text too short ({len(text.strip())} chars)")
                analysis = {
                    "summary": "Skipped (Content too short)",
                    "is_urgent": False,
                    "urgency_reason": "Content length < 5 chars",
                    "detected_language": "Unknown",
                    "suggested_reply": ""
                }
            else:
                # AI Analysis
                print(f"  [AI] 正在分析内容: {base_name}")
                analysis = self.ai.analyze_transcription(text)

            analysis["text"] = text
            analysis["file_name"] = base_name

            # Save analysis
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(analysis, f, ensure_ascii=False, indent=4)

            return analysis
        except Exception as e:
            print(f"Error transcribing {audio_path}: {e}")
            # Try to print path for debugging
            # print(f"DEBUG PATH in process: {os.environ.get('PATH')}")
        return None

    def process_all(self):
        self.ensure_dirs()
        
        print("\n>>> 开始扫描新文件...")
        # 1. Process Videos
        if os.path.exists(self.config["VIDEO_DIR"]):
            video_files = [f for f in os.listdir(self.config["VIDEO_DIR"]) if f.lower().endswith(('.mp4', '.mkv', '.mov', '.mpeg'))]
            if video_files:
                print(f"发现 {len(video_files)} 个视频文件")
                for vf in video_files:
                    v_path = os.path.join(self.config["VIDEO_DIR"], vf)
                    mp3_path = self.process_video_to_mp3(v_path)
                    if mp3_path:
                        self.transcribe(mp3_path, self.config["TXT_DIR"])

        # 2. Process WAVs
        if os.path.exists(self.config["WAV_DIR"]):
            wav_files = [f for f in os.listdir(self.config["WAV_DIR"]) if f.lower().endswith('.wav')]
            if wav_files:
                print(f"发现 {len(wav_files)} 个音频采集文件 (WAV)")
                for wf in wav_files:
                    w_path = os.path.join(self.config["WAV_DIR"], wf)
                    self.transcribe(w_path, self.config["WAV_TXT_DIR"])
        
        print(">>> 扫描处理结束。\n")

    def delete_record(self, file_name, source_type):
        """Deletes all files associated with a record."""
        targets = []
        if source_type == "Video":
            # 视频相关
            targets.append(os.path.join(self.config["VIDEO_DIR"], f"{file_name}.mp4"))
            targets.append(os.path.join(self.config["VIDEO_DIR"], f"{file_name}.mpeg"))
            targets.append(os.path.join(self.config["VIDEO_DIR"], f"{file_name}.mkv"))
            targets.append(os.path.join(self.config["VIDEO_DIR"], f"{file_name}.mov"))
            # 提取的音频
            targets.append(os.path.join(self.config["AUDIO_DIR"], f"{file_name}.mp3"))
            # 结果
            targets.append(os.path.join(self.config["TXT_DIR"], f"{file_name}.txt"))
            targets.append(os.path.join(self.config["TXT_DIR"], f"{file_name}.json"))
        elif source_type == "Phone":
            # 录音原始文件
            targets.append(os.path.join(self.config["WAV_DIR"], f"{file_name}.wav"))
            # 结果
            targets.append(os.path.join(self.config["WAV_TXT_DIR"], f"{file_name}.txt"))
            targets.append(os.path.join(self.config["WAV_TXT_DIR"], f"{file_name}.json"))

        deleted_count = 0
        for t in targets:
            if os.path.exists(t):
                try:
                    os.remove(t)
                    deleted_count += 1
                    print(f"  [Delete] 已删除: {t}")
                except Exception as e:
                    print(f"  [Error] 无法删除 {t}: {e}")
        
        return deleted_count > 0

if __name__ == "__main__":
    processor = AudioProcessor()
    processor.process_all()
