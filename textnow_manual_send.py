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
import json
import os
import sys

# Add current dir to path to find ai_service if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_service import AIService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Helper to load config
def load_config():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

# Helper to load templates
def load_templates():
    try:
        with open("templates.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def get_current_chat_history(driver):
    """Scrapes the visible chat history from the current window."""
    print("    [Info] Reading conversation history...")
    history_text = ""
    try:
        # Strategy A: Look for the main chat area
        history_els = driver.find_elements(By.CSS_SELECTOR, 
            ".message-history, .conversation-list, [role='main'], main"
        )
        
        if history_els:
            for h in history_els:
                if h.is_displayed():
                    history_text += h.text + "\n"
        else:
            # Strategy B: Find Input box and look up
            try:
                inp = driver.find_element(By.ID, "message-input")
                container = inp.find_element(By.XPATH, "./ancestor::div[contains(@class, 'conversation')] | ./ancestor::main")
                history_text = container.text
            except:
                pass
                
    except Exception as e:
        print(f"    [Error] Failed to read history: {e}")
        
    return history_text

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
    
    last_ai_reply = None
    
    while True:
        print("\n" + "=" * 60)
        print("选择操作:")
        print("=" * 60)
        print("1. 使用预设模板")
        print("2. 自定义消息")
        print("3. 退出")
        print("4. AI 智能回复 (读取当前对话)")
        print("=" * 60)
        
        choice = input("\n请选择 (1-4): ").strip()
        
        if choice == "3":
            print("\n再见！")
            break
        
        elif choice == "1":
            # Load fresh templates every time
            templates = load_templates()
            if not templates:
                print("❌ 错误：无法加载 templates.json")
                continue

            # Convert to list for selection
            tmpl_list = []
            for k, v in templates.items():
                tmpl_list.append((k, v))
            
            # 显示模板列表
            print("\n" + "=" * 60)
            print("可用模板:")
            print("=" * 60)
            
            for idx, (key, tmpl) in enumerate(tmpl_list):
                active_mark = "[ACTIVE] " if tmpl.get("active", False) else ""
                print(f"{idx+1}. {active_mark}{tmpl.get('name', key)}")
            print("=" * 60)
            
            try:
                sel_idx = int(input(f"\n选择模板 (1-{len(tmpl_list)}): ").strip()) - 1
                if 0 <= sel_idx < len(tmpl_list):
                    selected_key, template = tmpl_list[sel_idx]
                    
                    # Combine CN and EN logic similar to automation
                    raw_cn = template.get("content_cn", "Error")
                    raw_en = template.get("content_en", "Error")
                    
                    full_content = f"中文内容:\n{raw_cn}\n\nEnglish Content:\n{raw_en}"
                    
                    print(f"\n已选择: {template.get('name', selected_key)}")
                    print("\n消息预览:")
                    print("-" * 60)
                    print(full_content)
                    print("-" * 60)
                    
                    # Note: Manual tool doesn't construct full msg with name/refID currently?
                    # Let's just combine them simply for manual sending or ask user?
                    # For simplicity, we send CN then EN joined by newlines.
                    final_msg_to_send = f"{raw_cn}\n\n{raw_en}"
                print("\n消息预览:")
                print("-" * 60)
                print(template['content'])
                print("-" * 60)
                
                    confirm = input("\n确认发送? (y/n): ").strip().lower()
                    if confirm == 'y':
                        send_message(driver, final_msg_to_send)
                    else:
                        print("已取消")
                else:
                    print("❌ 无效选择")
            except:
                print("❌ 输入无效")
        
        elif choice == "2":
            # 自定义消息
            print("\n" + "=" * 60)
            print("输入自定义消息")
            print("=" * 60)
            
            lines = []
            used_cached = False
            
            if last_ai_reply:
                print(f"💡 检测到上次生成的 AI 回复:\n{'-'*20}\n{last_ai_reply}\n{'-'*20}")
                use = input("是否直接使用此回复? (y/n): ").strip().lower()
                if use == 'y':
                    custom_message = last_ai_reply
                    used_cached = True
            
            if not used_cached:
                print("提示：")
                print("- 输入多行文本，每行按ENTER")
                print("- 输入完成后，单独一行输入 END 并按ENTER")
                print("=" * 60)
                
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
        
        elif choice == "4":
            # AI Smart Reply
            print("\n正在初始化 AI...")
            cfg = load_config()
            ai_service = None
            try:
                ai_service = AIService(cfg)
            except Exception as e:
                print(f"❌ AI 初始化失败: {e}")
                continue

            # 1. Get History
            hist = get_current_chat_history(driver)
            if not hist or len(hist) < 5:
                print("⚠ 警告: 未能读取到足够的对话历史，或对话为空。")
                cont = input("是否继续尝试生成? (y/n): ").strip().lower()
                if cont != 'y': continue
            
            # 2. Get Active Template
            templates = load_templates()
            active_tmpl_key = "standard_reply"
            for k, v in templates.items():
                if v.get("active", False):
                    active_tmpl_key = k
                    break
            
            target_tmpl = templates.get(active_tmpl_key, {})
            tmpl_name = target_tmpl.get("name", "Unknown")
            print(f"Drafting reply using template: [{tmpl_name}]...")
            
            # Construct template text for AI
            raw_cn = target_tmpl.get("content_cn", "")
            raw_en = target_tmpl.get("content_en", "")
            base_info = f"{raw_cn}\n\n{raw_en}"
            
            # 3. Generate
            print("🤖 AI 正在思考 (Detecting Language & Drafting)...")
            reply = ai_service.generate_reply_from_history(hist, template_text=base_info)
            
            if not reply:
                print("❌ AI 生成失败 (返回为空)")
                continue
                
            print("\n🤖 AI 建议回复:")
            print("-" * 60)
            print(reply)
            print("-" * 60)
            
            # Save for manual use
            last_ai_reply = reply
            
            action = input("\n[S]发送 / [R]重试 / [C]取消? ").strip().lower()
            if action == 's':
                send_message(driver, reply)
            elif action == 'r':
                print("重试中...")
                # Could loop here, but simple re-select 4 is fine
                pass
            else:
                print("已取消")
        
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
