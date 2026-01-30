
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

MESSAGE = """尊敬的旅客，
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

options = webdriver.ChromeOptions()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

try:
    driver = webdriver.Chrome(options=options)
    
    # Find input box
    input_box = None
    try:
        input_box = driver.find_element(By.ID, "message-input")
    except:
        try:
            input_box = driver.find_element(By.TAG_NAME, "textarea")
        except:
            pass
    
    if not input_box:
        print("ERROR: Input box not found")
        exit(1)
    
    # Send message with SHIFT+ENTER for line breaks
    lines = MESSAGE.split('\n')
    for idx, line in enumerate(lines):
        input_box.send_keys(line)
        if idx < len(lines) - 1:
            input_box.send_keys(Keys.SHIFT, Keys.ENTER)
            time.sleep(0.1)
    
    time.sleep(0.5)
    input_box.send_keys(Keys.ENTER)
    print("SUCCESS")
    
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)
