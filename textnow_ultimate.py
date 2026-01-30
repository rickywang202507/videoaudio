"""
TextNow 终极反检测脚本 (Ultimate Stealth)
解决 [WinError 6] 句柄错误，强制保持浏览器开启
"""

import os
import sys
import time
import subprocess
import undetected_chromedriver as uc

def force_kill_chrome():
    """强制关闭所有Chrome进程，防止冲突"""
    print("[1/3] 清理现有Chrome进程...")
    try:
        if sys.platform == 'win32':
            os.system("taskkill /f /im chrome.exe /t >nul 2>&1")
            os.system("taskkill /f /im chromedriver.exe /t >nul 2>&1")
    except:
        pass
    time.sleep(2)

def start_browser():
    print("[2/3] 启动增强型浏览器...")
    print("      (首次运行可能需要下载驱动，请稍候)")
    
    options = uc.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # 关键：避免出现恢复弹窗
    options.add_argument('--disable-session-crashed-bubble')
    
    try:
        # 使用 standard 模式
        driver = uc.Chrome(
            options=options,
            headless=False,
            use_subprocess=True,
            version_main=None # 自动检测版本
        )
        return driver
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        print("尝试备用模式...")
        try:
            # 备用模式：不仅用 use_subprocess=False
            driver = uc.Chrome(
                options=options,
                headless=False,
                use_subprocess=False
            )
            return driver
        except Exception as e2:
            print(f"❌ 备用模式也失败: {e2}")
            raise

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║       🛡️ TextNow 终极反检测 (无需关闭窗口)                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # 1. 清理环境
    force_kill_chrome()
    
    # 2. 启动浏览器
    try:
        driver = start_browser()
        print("\n[3/3] ✅ 浏览器启动成功！")
        
        # 3. 访问页面
        print("      🔗 正在跳转到 TextNow...")
        driver.get("https://www.textnow.com/login")
        
        print("\n" + "="*60)
        print("  🎉 准备就绪！")
        print("="*60)
        print("\n请在这个浏览器窗口中操作：")
        print("1. 输入账号密码")
        print("2. 长按获取验证码")
        print("3. 如果通过验证，请保持此窗口打开")
        
        # 4. 保持运行
        print("\n⏳ 脚本将挂起以保持浏览器开启...")
        print("   (如需退出，请直接关闭CMD窗口)")
        
        while True:
            time.sleep(1000)
            
    except KeyboardInterrupt:
        print("\n用户退出")
        # 使用 os._exit(0) 强制退出，不调用 cleanup
        # 这可以防止 [WinError 6] 错误
        os._exit(0)
        
    except Exception as e:
        print(f"\n❌ 严重错误: {e}")
        import traceback
        traceback.print_exc()
        print("\n⚠️ 即使报错，我们也会尝试保持窗口不关闭...")
        print("按 Ctrl+C 强制结束")
        try:
            while True: time.sleep(1)
        except:
            os._exit(1)

if __name__ == "__main__":
    try:
        main()
    except:
        os._exit(1)
