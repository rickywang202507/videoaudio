"""
TextNow 手动发送工具
功能：
1. 向当前选中的对话发送自定义SMS
2. 提供预设模板和自定义编辑功能
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# 预设SMS模板
TEMPLATES = {
    "1": {
        "name": "未接来电标准回复（中英文）",
        "content": """尊敬的旅客，
很抱歉未能接听您的来电，请参考以下信息：
购票：请访问东航官网 www.ceair.com，或联系您的代理人 / 第三方网站。
退改票：
– 如在东航官网购票，请发送邮件至 MUYVR@chinaeastern.ca
– 其他渠道购票，请联系原购票渠道。
中转服务：
https://www.ceair.com/self-service/service-submit/transferService
特殊服务申请：
– 温哥华始发：MUYVR@chinaeastern.ca
– 多伦多始发：MUyyzSales@chinaeastern.ca
改名服务：请致电 011 86 21 2069 5530
其他事项：请发送邮件至 MUyyzSales@chinaeastern.ca or call 011 86 21 2069 5530

免责声明：本短信为系统自动回复，仅供参考，请旅客自行核实相关信息。本号码无法接收回复短信，敬请谅解。

Dear Customer,
Sorry we missed your call. Please refer to the information below.

For ticket purchase, please visit China Eastern official website www.ceair.com, or contact your agent / third-party website.

For refund or change:
– If ticket purchased on China Eastern website, please email MUYVR@chinaeastern.ca

– Otherwise, please contact original purchase channel.

Transfer service:
https://www.ceair.com/self-service/service-submit/transferService

Special service request:
– Vancouver departure: MUYVR@chinaeastern.ca

– Toronto departure: MUyyzSales@chinaeastern.ca

Name change: please call 011 86 21 2069 5530

Other inquiries: please email MUyyzSales@chinaeastern.ca or call 011 86 21 2069 5530

Disclaimer: This is an auto-reply message. Information is for reference only, please verify by yourself. Do not reply to this message, replies cannot be received."""
    },
    "2": {
        "name": "简短回复（仅中文）",
        "content": """尊敬的旅客，
很抱歉未能接听您的来电。
如需帮助，请发送邮件至 MUyyzSales@chinaeastern.ca
或致电 011 86 21 2069 5530

谢谢！"""
    },
    "3": {
        "name": "简短回复（仅英文）",
        "content": """Dear Customer,
Sorry we missed your call.
For assistance, please email MUyyzSales@chinaeastern.ca
or call 011 86 21 2069 5530

Thank you!"""
    }
}

def send_message(driver, message):
    """发送消息到当前对话"""
    try:
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
            print("   请确保已在Chrome中选中一个对话")
            return False
        
        print("\n正在发送消息...")
        
        # 使用SHIFT+ENTER处理换行
        lines = message.split('\n')
        for idx, line in enumerate(lines):
            input_box.send_keys(line)
            if idx < len(lines) - 1:
                input_box.send_keys(Keys.SHIFT, Keys.ENTER)
                time.sleep(0.1)
        
        time.sleep(0.5)
        input_box.send_keys(Keys.ENTER)
        
        print("✅ 消息已发送！")
        return True
        
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        return False

def main():
    print("=" * 60)
    print("TextNow 手动发送工具".center(60))
    print("=" * 60)
    
    # 连接到Chrome
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(options=options)
        print("✓ 已连接到Chrome")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print("\n请确保:")
        print("1. 已运行 run_chrome_debug.bat")
        print("2. Chrome窗口保持打开")
        return
    
    # 检查是否在TextNow页面
    if "textnow.com" not in driver.current_url:
        print("\n⚠ 警告：当前不在TextNow页面")
        print("请在Chrome中打开 https://textnow.com/messaging")
        input("\n准备好后按 ENTER 继续...")
    
    print("\n" + "=" * 60)
    print("请在Chrome中选择要发送消息的对话")
    print("=" * 60)
    input("选好后按 ENTER 继续...")
    
    while True:
        print("\n" + "=" * 60)
        print("选择操作:")
        print("=" * 60)
        print("1. 使用预设模板")
        print("2. 自定义消息")
        print("3. 退出")
        print("=" * 60)
        
        choice = input("\n请选择 (1-3): ").strip()
        
        if choice == "3":
            print("\n再见！")
            break
        
        elif choice == "1":
            # 显示模板列表
            print("\n" + "=" * 60)
            print("可用模板:")
            print("=" * 60)
            for key, template in TEMPLATES.items():
                print(f"{key}. {template['name']}")
            print("=" * 60)
            
            template_choice = input("\n选择模板 (1-3): ").strip()
            
            if template_choice in TEMPLATES:
                template = TEMPLATES[template_choice]
                print(f"\n已选择: {template['name']}")
                print("\n消息预览:")
                print("-" * 60)
                print(template['content'])
                print("-" * 60)
                
                confirm = input("\n确认发送? (y/n): ").strip().lower()
                if confirm == 'y':
                    send_message(driver, template['content'])
                else:
                    print("已取消")
            else:
                print("❌ 无效选择")
        
        elif choice == "2":
            # 自定义消息
            print("\n" + "=" * 60)
            print("输入自定义消息")
            print("=" * 60)
            print("提示：")
            print("- 输入多行文本，每行按ENTER")
            print("- 输入完成后，单独一行输入 END 并按ENTER")
            print("=" * 60)
            
            lines = []
            while True:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)
            
            custom_message = '\n'.join(lines)
            
            if custom_message.strip():
                print("\n消息预览:")
                print("-" * 60)
                print(custom_message)
                print("-" * 60)
                
                confirm = input("\n确认发送? (y/n): ").strip().lower()
                if confirm == 'y':
                    send_message(driver, custom_message)
                else:
                    print("已取消")
            else:
                print("❌ 消息为空")
        
        else:
            print("❌ 无效选择")
        
        print("\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
