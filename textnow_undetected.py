"""
TextNow Automation with Undetected ChromeDriver
使用 undetected-chromedriver 的增强版本

这个版本使用最强的反检测库，可以绕过大多数验证码检测
"""

import undetected_chromedriver as uc
import time
import random
import os
import sys

def create_undetected_browser():
    """创建一个完全不被检测的浏览器实例"""
    
    print("[Undetected] 创建浏览器实例...")
    print("[提示] 首次运行可能需要下载ChromeDriver，请稍候...")
    
    try:
        # 配置选项
        options = uc.ChromeOptions()
        
        # 基础设置
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # 用户代理（看起来像真实用户）
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # 创建驱动（undetected-chromedriver 会自动处理反检测）
        driver = uc.Chrome(
            options=options,
            version_main=None,  # 自动检测Chrome版本
            use_subprocess=False,  # 改为False避免句柄问题
            headless=False  # 必须是可见的浏览器
        )
        
        print("[Undetected] ✅ 浏览器已启动")
        return driver
        
    except Exception as e:
        print(f"[错误] 无法启动浏览器: {e}")
        print("\n可能的原因：")
        print("1. Chrome未安装或版本不兼容")
        print("2. ChromeDriver下载失败")
        print("3. 防火墙阻止")
        print("\n请尝试：")
        print("- 更新Chrome到最新版本")
        print("- 检查网络连接")
        print("- 暂时关闭防火墙")
        raise


def human_like_delay(min_sec=1.0, max_sec=3.0):
    """模拟人类延迟"""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)


def test_textnow_login(driver):
    """测试TextNow登录和验证码"""
    
    print("\n" + "="*70)
    print("  📱 TextNow 验证码测试")
    print("="*70 + "\n")
    
    # 1. 访问TextNow
    print("[步骤 1/5] 访问 TextNow 登录页面...")
    try:
        driver.get("https://www.textnow.com/login")
        print("✅ 页面加载中...")
        human_like_delay(3, 5)
        print("✅ 页面已加载完成")
    except Exception as e:
        print(f"❌ 无法访问TextNow: {e}")
        return False
    
    print("\n" + "-"*70)
    print("  📋 请在浏览器中手动操作")
    print("-"*70)
    print("\n请按以下步骤操作：")
    print("\n  1️⃣  输入您的 TextNow 用户名")
    print("  2️⃣  输入您的密码")
    print("  3️⃣  点击登录按钮")
    print("  4️⃣  🔑 长按获取验证码（这是关键测试！）")
    print("  5️⃣  观察验证码是否正常弹出")
    print("  6️⃣  尝试完成验证")
    
    print("\n" + "-"*70)
    print("  ⏳ 请告诉我结果")
    print("-"*70)
    print("\n请回答以下问题：")
    
    # 询问验证码是否弹出
    print("\n❓ 验证码是否正常弹出？")
    print("   输入 'y' (是) 或 'n' (否): ", end='')
    captcha_appeared = input().strip().lower()
    
    if captcha_appeared == 'y':
        print("\n✅ 太好了！验证码正常弹出")
        
        # 询问是否通过验证
        print("\n❓ 您能否完成验证？")
        print("   输入 'y' (能) 或 'n' (不能): ", end='')
        captcha_passed = input().strip().lower()
        
        if captcha_passed == 'y':
            print("\n🎉 完美！验证码已通过")
            
            # 等待登录完成
            print("\n⏳ 等待登录完成...")
            time.sleep(3)
            
            # 检查URL
            current_url = driver.current_url
            print(f"\n当前URL: {current_url}")
            
            if "messaging" in current_url or "conversations" in current_url:
                print("\n" + "="*70)
                print("  🎊 测试成功！")
                print("="*70)
                print("\n✅ undetected-chromedriver 成功绕过了TextNow的检测！")
                print("✅ 验证码正常工作")
                print("✅ 成功登录")
                return True
            else:
                print("\n⚠️  验证通过但未跳转到messaging页面")
                print("   可能需要额外的操作")
                return False
        else:
            print("\n❌ 验证码无法完成")
            print("\n可能的原因：")
            print("  1. 验证码难度太高")
            print("  2. IP被标记")
            print("  3. 账号被限制")
            print("\n建议：")
            print("  1. 使用住宅代理IP")
            print("  2. 等待24小时后重试")
            print("  3. 尝试不同的网络环境")
            return False
    else:
        print("\n❌ 验证码没有弹出")
        print("\n这说明TextNow仍然检测到了自动化")
        print("\n下一步方案：")
        print("  1. 使用住宅代理IP")
        print("  2. 使用真实设备（非虚拟机）")
        print("  3. 考虑使用API或其他方案")
        return False


def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║       🛡️ TextNow 强制测试版 (No-Quit Mode)                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # 强制清理旧进程
    try:
        os.system("taskkill /f /im chrome.exe /t >nul 2>&1")
    except:
        pass

    driver = None
    try:
        # 创建浏览器
        driver = create_undetected_browser()
        
        # 测试登录
        print("🔗 正在访问 TextNow...")
        driver.get("https://www.textnow.com/login")
        
        print("\n" + "="*70)
        print("  ✅ 浏览器已启动！")
        print("="*70)
        print("\n请操作：")
        print("1. 输入账号密码")
        print("2. 长按验证码")
        print("3. 如果成功，请保持此窗口打开")
        
        print("\n⏳ 脚本将永久挂起，以防浏览器关闭...")
        print("   (关闭此黑框将强制结束)")
        
        while True:
            time.sleep(1000)
            
    except KeyboardInterrupt:
        print("\n用户退出")
        # ⚠️ 关键：强制退出，跳过所有清理代码
        os._exit(0)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        # 即使出错也不退出
        while True: time.sleep(1)

if __name__ == "__main__":
    try:
        # 检查依赖
        import undetected_chromedriver
        main()
    except Exception as e:
        print(e)
        os._exit(1)

