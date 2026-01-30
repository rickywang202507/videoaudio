"""
Enhanced TextNow Automation with Advanced Anti-Detection
使用增强的反检测技术的TextNow自动化脚本

主要改进:
1. 使用 selenium-stealth 库
2. 更真实的人类行为模拟
3. 随机延迟和鼠标移动
4. 更好的浏览器指纹伪装
"""

import os
import sys

# Check if selenium-stealth is installed
try:
    from selenium_stealth import stealth
    STEALTH_AVAILABLE = True
    print("[Stealth] selenium-stealth library detected")
except ImportError:
    STEALTH_AVAILABLE = False
    print("[Warning] selenium-stealth not installed. Run: pip install selenium-stealth")
    print("[Info] Falling back to basic stealth mode")

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
import random

def create_stealth_driver(debug_port=9222, user_data_dir=None):
    """
    创建一个具有高级反检测功能的Chrome驱动
    
    Args:
        debug_port: Chrome调试端口
        user_data_dir: 用户数据目录路径
    
    Returns:
        配置好的WebDriver实例
    """
    
    options = webdriver.ChromeOptions()
    
    # 连接到现有的Chrome实例
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
    
    # 基础反检测选项
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # 创建驱动
    driver = webdriver.Chrome(options=options)
    
    # 应用selenium-stealth（如果可用）
    if STEALTH_AVAILABLE:
        print("[Stealth] Applying selenium-stealth configuration...")
        stealth(driver,
            languages=["en-US", "en", "zh-CN", "zh"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
        print("[Stealth] selenium-stealth applied successfully")
    
    return driver


def human_like_delay(min_sec=1.0, max_sec=3.0):
    """
    模拟人类操作的随机延迟
    
    Args:
        min_sec: 最小延迟秒数
        max_sec: 最大延迟秒数
    """
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)


def human_like_click(driver, element):
    """
    模拟人类点击行为（带鼠标移动）
    
    Args:
        driver: WebDriver实例
        element: 要点击的元素
    """
    try:
        # 先移动到元素附近
        actions = ActionChains(driver)
        
        # 随机偏移
        x_offset = random.randint(-5, 5)
        y_offset = random.randint(-5, 5)
        
        # 移动到元素
        actions.move_to_element_with_offset(element, x_offset, y_offset)
        
        # 短暂停顿（模拟人类瞄准）
        human_like_delay(0.3, 0.8)
        
        # 点击
        actions.click()
        actions.perform()
        
        print("[Human] Performed human-like click")
    except Exception as e:
        print(f"[Warning] Human-like click failed, using standard click: {e}")
        element.click()


def human_like_typing(element, text, min_interval=0.05, max_interval=0.15):
    """
    模拟人类打字行为（逐字符输入，带随机延迟）
    
    Args:
        element: 输入框元素
        text: 要输入的文本
        min_interval: 最小字符间隔（秒）
        max_interval: 最大字符间隔（秒）
    """
    try:
        element.clear()
        human_like_delay(0.2, 0.5)
        
        for char in text:
            element.send_keys(char)
            # 随机延迟，模拟打字速度
            time.sleep(random.uniform(min_interval, max_interval))
            
            # 偶尔停顿（模拟思考）
            if random.random() < 0.1:  # 10%的概率
                time.sleep(random.uniform(0.3, 0.8))
        
        print(f"[Human] Typed {len(text)} characters with human-like timing")
    except Exception as e:
        print(f"[Warning] Human-like typing failed: {e}")
        element.send_keys(text)


def random_scroll(driver, direction="down", distance=None):
    """
    随机滚动页面（模拟人类浏览行为）
    
    Args:
        driver: WebDriver实例
        direction: 滚动方向 ("up" 或 "down")
        distance: 滚动距离（像素），None则随机
    """
    if distance is None:
        distance = random.randint(100, 500)
    
    if direction == "down":
        distance = abs(distance)
    else:
        distance = -abs(distance)
    
    driver.execute_script(f"window.scrollBy(0, {distance});")
    print(f"[Human] Scrolled {direction} by {abs(distance)}px")


def inject_advanced_stealth(driver):
    """
    注入高级反检测JavaScript代码
    
    Args:
        driver: WebDriver实例
    """
    stealth_script = """
    // 高级反检测脚本
    
    // 1. 移除webdriver属性
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
    
    // 2. 伪装Chrome运行时
    window.chrome = {
        runtime: {},
        loadTimes: function() {},
        csi: function() {},
        app: {}
    };
    
    // 3. 伪装权限查询
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
            Promise.resolve({ state: Notification.permission }) :
            originalQuery(parameters)
    );
    
    // 4. 伪装插件
    Object.defineProperty(navigator, 'plugins', {
        get: () => [
            {
                0: {type: "application/x-google-chrome-pdf", suffixes: "pdf"},
                description: "Portable Document Format",
                filename: "internal-pdf-viewer",
                length: 1,
                name: "Chrome PDF Plugin"
            }
        ]
    });
    
    // 5. 伪装语言
    Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en', 'zh-CN', 'zh']
    });
    
    // 6. 隐藏自动化痕迹
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
    
    // 7. 伪装触摸支持
    Object.defineProperty(navigator, 'maxTouchPoints', {
        get: () => 1
    });
    
    console.log('[Stealth] Advanced anti-detection applied');
    """
    
    try:
        # 在每个新页面加载时执行
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': stealth_script
        })
        print("[Stealth] Advanced stealth script injected")
        return True
    except Exception as e:
        print(f"[Warning] Could not inject stealth script: {e}")
        return False


# 使用示例
if __name__ == "__main__":
    print("=== Enhanced Stealth Mode Test ===")
    print()
    print("This script demonstrates advanced anti-detection techniques.")
    print("Make sure Chrome is running with: run_chrome_stealth.bat")
    print()
    
    try:
        # 创建stealth驱动
        driver = create_stealth_driver()
        
        # 注入高级stealth脚本
        inject_advanced_stealth(driver)
        
        # 导航到测试页面
        print("\nNavigating to bot detection test page...")
        driver.get("https://bot.sannysoft.com/")
        
        time.sleep(3)
        
        print("\nCheck the browser window to see detection results.")
        print("Green = Not detected, Red = Detected as bot")
        print("\nPress Enter to close...")
        input()
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have:")
        print("1. Run run_chrome_stealth.bat")
        print("2. Installed selenium-stealth: pip install selenium-stealth")
