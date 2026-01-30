"""
TextNow 版本修复工具
自动检测 Chrome 版本并强制匹配驱动
"""

import os
import sys
import undetected_chromedriver as uc
from selenium import webdriver

def get_chrome_version():
    """获取 Chrome 版本"""
    import winreg
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
        version, _ = winreg.QueryValueEx(key, "version")
        return version
    except:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome")
            version, _ = winreg.QueryValueEx(key, "DisplayVersion")
            return version
        except:
            return None

def fix_and_run():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║       🛠️ TextNow 驱动修复工具                                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")

    # 1. 检测 Chrome 版本
    version = get_chrome_version()
    print(f"🔍 检测到的 Chrome 版本: {version or '未知'}")
    
    if not version:
        print("❌ 无法检测到 Chrome 版本。请确保已安装 Google Chrome。")
        return

    # 提取主版本号 (例如 120.0.6099.109 -> 120)
    main_version = int(version.split('.')[0])
    print(f"🎯 主版本号: {main_version}")

    # 2. 尝试启动带版本控制的驱动
    print("\n🚀 正在尝试匹配版本的启动...")
    
    try:
        options = uc.ChromeOptions()
        options.add_argument('--start-maximized')
        
        # 强制指定版本号
        driver = uc.Chrome(
            options=options,
            version_main=main_version,  # 强制匹配主版本
            headless=False,
            use_subprocess=True
        )
        
        print("\n✅ 启动成功！驱动版本匹配正常。")
        driver.get("https://www.textnow.com/login")
        
        print("\n请操作：")
        print("1. 登录")
        print("2. 测试验证码")
        print("\n(保持窗口打开)")
        input()
        
    except Exception as e:
        print(f"\n❌ 指定版本启动失败: {e}")
        print("\n尝试方案 B：完全重新下载驱动...")
        
        # 清理缓存
        import shutil
        appdata = os.getenv('APPDATA')
        uc_dir = os.path.join(appdata, 'undetected_chromedriver')
        if os.path.exists(uc_dir):
            try:
                shutil.rmtree(uc_dir)
                print("🧹 已清除旧驱动缓存")
            except: pass
            
        print("🚀 重新尝试启动（不指定版本，让它重新下载）...")
        try:
            driver = uc.Chrome(options=options, headless=False, use_subprocess=True)
            print("\n✅ 启动成功！")
            driver.get("https://www.textnow.com/login")
            input()
        except Exception as e2:
            print(f"\n❌ 所有尝试都失败了: {e2}")
            print("\n建议：")
            print("1. 手动更新 Chrome 到最新版")
            print("2. 卸载并重新安装 undetected-chromedriver")
            print("   pip uninstall undetected-chromedriver")
            print("   pip install undetected-chromedriver")

if __name__ == "__main__":
    fix_and_run()
