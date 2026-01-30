"""
TextNow 后期接管脚本
等待用户手动登录成功后，再连接浏览器进行自动化
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def connect_to_browser():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║       🔌 TextNow 浏览器接管工具                              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    print("正在连接到已打开的 Chrome (端口 9222)...")
    
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(options=options)
        
        print("\n✅ 连接成功！")
        print(f"当前页面标题: {driver.title}")
        print(f"当前 URL: {driver.current_url}")
        
        # 动态注入反检测（只在连接后注入）
        print("\n💉 正在注入反检测补丁...")
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
        })
        
        if "login" in driver.current_url:
            print("\n⚠️ 警告：您似乎还在登录页面")
            print("请先手动完成登录，直到进入 messaging 界面")
        else:
            print("\n🎉 检测到已登录状态！")
            print("您可以继续让脚本运行自动化任务了。")
            
        return driver
        
    except Exception as e:
        print(f"\n❌ 连接失败: {e}")
        print("请确保您已经运行了 start_clean_chrome.bat")

if __name__ == "__main__":
    driver = connect_to_browser()
    if driver:
        print("\n按 Ctrl+C 退出接管（浏览器不会关闭）")
        while True:
            time.sleep(1)
