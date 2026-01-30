"""
TextNow 兼容性解决方案
不再依赖 undetected-chromedriver (因为不支持 Chrome v144)
改用 Selenium + Stealth + 增强型反检测参数
"""

import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager
import os

def create_stealth_browser():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║       🚑 Chrome v144 兼容性模式                              ║
║                                                              ║
║   由于您的 Chrome 版本过高，我们切换回 Selenium+Stealth      ║
║   但添加了更强的反检测参数来模拟 undetected 效果             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")

    options = Options()
    
    # === 增强型反检测参数 ===
    options.add_argument("start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--exclude-switches=enable-automation")
    options.add_argument("--disable-infobars")
    
    # 模拟真实用户
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    
    # 禁用可能暴露的API
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    
    print("🚀 正在下载兼容驱动...")
    # 使用 webdriver-manager 自动处理驱动
    service = Service(ChromeDriverManager().install())
    
    print("🚀 启动浏览器...")
    driver = webdriver.Chrome(service=service, options=options)
    
    # === 注入 Stealth JS ===
    print("💉 注入反检测脚本...")
    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    
    # 额外的 JS 注入确保万无一失
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })
    
    return driver

def main():
    try:
        driver = create_stealth_browser()
        
        print("\n✅ 浏览器启动成功（兼容模式）")
        print("🔗 访问 TextNow...")
        
        driver.get("https://www.textnow.com/login")
        
        print("\n" + "="*70)
        print("  ✅ 准备就绪")
        print("="*70)
        print("请测试：")
        print("1. 登录")
        print("2. 验证码")
        print("\n(此窗口将保持打开)")
        
        while True:
            time.sleep(1)
            
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        input("按 Enter 退出...")

if __name__ == "__main__":
    main()
