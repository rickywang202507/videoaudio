import time
from audio_processor import AudioProcessor

def main():
    start_time = time.time()
    print("--- 启动 MU 语音处理程序 ---")
    
    processor = AudioProcessor()
    processor.process_all()
    
    end_time = time.time()
    print(f"\n所有任务执行完毕，耗时: {end_time - start_time:.2f} 秒")

if __name__ == "__main__":
    main()
