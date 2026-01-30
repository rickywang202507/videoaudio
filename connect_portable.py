"""
TextNow 便携版连接脚本
强制使用下载的 chromedriver.exe v121 来连接已打开的便携版浏览器
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def connect_to_portable():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║       🔌 TextNow 便携版连接工具                              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # 获取我们下载的 chromedriver 路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    driver_path = os.path.join(base_dir, "chrome_portable", "bin", "chromedriver.exe")
    
    if not os.path.exists(driver_path):
        print(f"❌ 未找到驱动: {driver_path}")
        print("请确保您已经运行了 python download_chrome.py")
        return

    print(f"✅ 使用专用驱动: {driver_path}")
    print("正在连接到 localhost:9222 ...")

    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    # 关键：手动指定 Service 使用我们的驱动
    service = Service(executable_path=driver_path)
    
    try:
        driver = webdriver.Chrome(service=service, options=options)
        
        print("\n🎉 连接成功！")
        print(f"当前页面: {driver.title}")
        print(f"URL: {driver.current_url}")
        
        # 注入反检测防止后续操作露馅
        try:
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            })
            print("💉 已注入反检测补丁")
        except:
            print("⚠️ 反检测补丁注入失败（可能已注入）")

        if "login" in driver.current_url:
            print("\n⚠️  请手动完成登录！")
        else:
            print("\n✅ 检测到已登录状态")
            
        return driver
        
    except Exception as e:
        print(f"\n❌ 连接失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    driver = connect_to_portable()
    if driver:
        print("\n正在保持连接... 按 Ctrl+C 退出")
        while True:
            time.sleep(1)
