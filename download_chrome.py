"""
自动下载 Google Chrome v121 (Portable) 和匹配的 ChromeDriver
用于解决 v144 版本过高导致无法自动化的问题
"""

import os
import sys
import zipfile
import shutil
import urllib.request
import ssl

# 忽略 SSL 证书验证
ssl._create_default_https_context = ssl._create_unverified_context

# Chrome v121.0.6167.85 (Stable) 下载链接
CHROME_URL = "https://storage.googleapis.com/chrome-for-testing-public/121.0.6167.85/win64/chrome-win64.zip"
DRIVER_URL = "https://storage.googleapis.com/chrome-for-testing-public/121.0.6167.85/win64/chromedriver-win64.zip"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_DIR = os.path.join(BASE_DIR, "chrome_portable")

def download_file(url, dest_path):
    print(f"📥 正在下载: {os.path.basename(url)} ...")
    try:
        urllib.request.urlretrieve(url, dest_path)
        print("✅ 下载完成")
        return True
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return False

def extract_zip(zip_path, extract_to):
    print(f"📦 正在解压: {os.path.basename(zip_path)} ...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print("✅ 解压完成")
        return True
    except Exception as e:
        print(f"❌ 解压失败: {e}")
        return False

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║       ⬇️  Chrome v121 自动下载工具                           ║
║                                                              ║
║   将下载 Google Chrome for Testing v121 (win64)              ║
║   这是一个官方的免安装便携版本                               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")

    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)

    # 1. 下载 Chrome
    chrome_zip = os.path.join(TARGET_DIR, "chrome.zip")
    if download_file(CHROME_URL, chrome_zip):
        extract_zip(chrome_zip, TARGET_DIR)
        
        # 重命名解压后的文件夹更方便调用
        extracted_folder = os.path.join(TARGET_DIR, "chrome-win64")
        final_chrome_dir = os.path.join(TARGET_DIR, "bin")
        if os.path.exists(extracted_folder):
            if os.path.exists(final_chrome_dir):
                shutil.rmtree(final_chrome_dir)
            os.rename(extracted_folder, final_chrome_dir)

    # 2. 下载 ChromeDriver
    driver_zip = os.path.join(TARGET_DIR, "driver.zip")
    if download_file(DRIVER_URL, driver_zip):
        extract_zip(driver_zip, TARGET_DIR)
        
        # 移动 driver 到 bin 目录
        driver_src = os.path.join(TARGET_DIR, "chromedriver-win64", "chromedriver.exe")
        driver_dst = os.path.join(TARGET_DIR, "bin", "chromedriver.exe")
        if os.path.exists(driver_src):
            shutil.move(driver_src, driver_dst)

    # 3. 清理压缩包
    try:
        os.remove(chrome_zip)
        os.remove(driver_zip)
        shutil.rmtree(os.path.join(TARGET_DIR, "chromedriver-win64"))
    except: pass

    # 4. 生成验证脚本
    chrome_exe = os.path.join(TARGET_DIR, "bin", "chrome.exe")
    driver_exe = os.path.join(TARGET_DIR, "bin", "chromedriver.exe")
    
    if os.path.exists(chrome_exe) and os.path.exists(driver_exe):
        print("\n" + "="*60)
        print("🎉 安装成功！")
        print("="*60)
        print(f"Chrome 路径: {chrome_exe}")
        print(f"Driver 路径: {driver_exe}")
        print("\n您可以运行 'run_portable.bat' 来启动这个浏览器")
    else:
        print("\n❌ 安装似乎不完整，请检查错误信息")

if __name__ == "__main__":
    main()
