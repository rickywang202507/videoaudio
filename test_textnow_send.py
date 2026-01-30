"""
测试脚本：验证TextNow消息发送是否正确处理换行
使用简短的测试消息，避免发送完整的长模板
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# 简短的测试消息（包含换行）
TEST_MESSAGE = """测试消息 Line 1
测试消息 Line 2
测试消息 Line 3
End of test"""

print("=== TextNow 消息发送测试 ===")
print(f"测试消息内容:\n{TEST_MESSAGE}\n")
print("=" * 50)

# 连接到现有Chrome实例
options = webdriver.ChromeOptions()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

try:
    driver = webdriver.Chrome(options=options)
    print("✓ 已连接到Chrome")
    
    # 确保在TextNow页面
    if "textnow.com" not in driver.current_url:
        print("请先在Chrome中打开 TextNow 并登录")
        print("然后手动点击一个对话（测试用）")
        input("准备好后按 ENTER 继续...")
    
    print("\n请在Chrome中:")
    print("1. 点击一个测试对话（可以是你自己的另一个号码）")
    print("2. 确保输入框可见")
    input("准备好后按 ENTER 开始测试...")
    
    # 查找输入框
    input_box = None
    try:
        input_box = driver.find_element(By.ID, "message-input")
    except:
        try:
            input_box = driver.find_element(By.TAG_NAME, "textarea")
        except:
            pass
    
    if not input_box:
        print("❌ 错误：找不到输入框")
        exit(1)
    
    print("✓ 找到输入框")
    print("\n开始发送测试消息...")
    
    # 使用修复后的逻辑发送
    lines = TEST_MESSAGE.split('\n')
    for idx, line in enumerate(lines):
        print(f"  发送行 {idx+1}/{len(lines)}: {line[:20]}...")
        input_box.send_keys(line)
        # 如果不是最后一行，使用 SHIFT+ENTER
        if idx < len(lines) - 1:
            input_box.send_keys(Keys.SHIFT, Keys.ENTER)
            time.sleep(0.3)
    
    print("\n等待1秒后发送...")
    time.sleep(1)
    
    # 最后按ENTER发送
    input_box.send_keys(Keys.ENTER)
    print("✓ 已发送！")
    
    print("\n" + "=" * 50)
    print("请检查TextNow:")
    print("- 应该只发送了 1 条消息")
    print("- 消息应该包含 4 行内容")
    print("- 不应该分成多条消息")
    print("=" * 50)
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n测试完成！")
