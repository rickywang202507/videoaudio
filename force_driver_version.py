"""
TextNow 强制驱动版本工具
您的 Chrome 版本号 (144) 异常过高，我们需要强制使用一个稳定的驱动版本
"""

import undetected_chromedriver as uc
import os

print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║       🚑 Chrome 版本异常修复 (Force Version)                 ║
║                                                              ║
║   检测到 Chrome v144 (未来版本?)                             ║
║   将强制使用 v120 驱动进行尝试                               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")

def force_stable_driver():
    options = uc.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--no-sandbox')
    
    # 强制将 Chrome 视为版本 120 (目前最稳定的版本之一)
    # 这会欺骗 undetected-chromedriver 去下载 v120 的驱动
    try:
        print("🚀 正在下载并强制使用 v120 驱动...")
        driver = uc.Chrome(
            options=options,
            headless=False,
            use_subprocess=True,
            version_main=120  # 强制使用 v120
        )
        
        print("\n✅ 启动成功！")
        driver.get("https://www.textnow.com/login")
        
        print("\n请测试验证码...")
        while True:
            pass
            
    except Exception as e:
        print(f"\n❌ v120 失败: {e}")
        print("\n尝试 v119...")
        try:
            driver = uc.Chrome(
                options=options,
                headless=False, 
                use_subprocess=True,
                version_main=119
            )
            print("✅ v119 启动成功！")
            driver.get("https://www.textnow.com/login")
            while True: pass
        except Exception as e2:
            print(f"❌ v119 也失败: {e2}")

if __name__ == "__main__":
    force_stable_driver()
