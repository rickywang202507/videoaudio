"""
TextNow 不死鸟脚本 (Phoenix Mode)
通过 Monkey Patch 强制禁止浏览器关闭，解决闪退问题
"""

import undetected_chromedriver as uc
import time
import os
import shutil

print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║       🔥 TextNow 不死鸟模式 (Phoenix Mode)                   ║
║                                                              ║
║   此脚本已"废掉"浏览器的关闭功能。                           ║
║   无论发生什么错误，浏览器窗口都将保持打开！                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")

# ==========================================
# 🛑 黑客操作：禁止关闭浏览器
# ==========================================
def fake_quit(self):
    print("\n[🛡️ 拦截] 系统试图关闭浏览器，但被我阻止了！")
    return

def fake_del(self):
    print("\n[🛡️ 拦截] 系统试图清理浏览器，但被我阻止了！")
    return

# 覆盖库的原始方法
uc.Chrome.quit = fake_quit
uc.Chrome.__del__ = fake_del
print("✅ 已注入防关闭补丁")

# ==========================================
# 🧹 清理环境 (防止旧数据冲突)
# ==========================================
def cleanup_environment():
    print("\n[1/3] 清理旧环境...")
    try:
        os.system("taskkill /f /im chrome.exe /t >nul 2>&1")
        print("      - 已清理 Chrome 进程")
    except: pass
    
    # 尝试清理 uc 的缓存目录（解决版本不匹配）
    try:
        appdata = os.getenv('APPDATA')
        uc_dir = os.path.join(appdata, 'undetected_chromedriver')
        if os.path.exists(uc_dir):
            try:
                shutil.rmtree(uc_dir)
                print("      - 已重置驱动缓存")
            except:
                print("      - 缓存清理跳过（文件占用）")
    except: pass

# ==========================================
# 🚀 启动浏览器
# ==========================================
def main():
    cleanup_environment()
    
    print("\n[2/3] 正在启动...")
    print("      (如果卡住，请耐心等待1-2分钟，正在下载补丁)")
    
    try:
        options = uc.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # 使用 subprocess=False 模式
        driver = uc.Chrome(
            options=options,
            headless=False,
            use_subprocess=False,
            version_main=None
        )
        
        print("\n[3/3] ✅ 启动成功！")
        print("      🔗 跳转 TextNow...")
        
        try:
            driver.get("https://www.textnow.com/login")
        except:
            print("⚠️ 无法加载页面，但浏览器应该还活着")
            print("   请手动在地址栏输入: https://www.textnow.com/login")

        print("\n" + "="*60)
        print("  🎉 浏览器已锁定！")
        print("="*60)
        print("\n现在请操作：")
        print("1. 输入账号密码")
        print("2. 长按获取验证码")
        print("3. 【关键】观察窗口是否还在")
        
        print("\n⏳ 脚本将一直运行。关闭此窗口不会影响浏览器。")
        while True:
            time.sleep(10)
            
    except Exception as e:
        print(f"\n❌ 启动过程中发生错误: {e}")
        print("\n⚠️ 但是！由于我们要了'不死鸟'补丁，")
        print("   如果刚才浏览器窗口闪现过，它现在应该还在后台运行！")
        print("   请检查任务栏有没有 Chrome 图标。")
        
        # 即使报错也无限等待
        while True:
            time.sleep(10)

if __name__ == "__main__":
    main()
