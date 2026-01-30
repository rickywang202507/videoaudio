# 项目里程碑记录：Chrome v144 兼容性与 Stealth 架构升级
**日期**: 2026-01-30  
**状态**: ✅ 已完成 / 稳定运行

## 1. 核心问题回顾
在 Windows 环境下，系统自动安装的 Chrome 版本更新至 **v144**（Dev/Canary版），导致以下致命问题：
1.  **Driver 不匹配**：`undetected-chromedriver` 和标准 `selenium` 均无法找到匹配 v144 的 ChromeDriver，导致 `SessionNotCreatedException`。
2.  **反检测失效**：高版本 Chrome 的指纹特征变化，使得旧的 Stealth 方案更容易被 TextNow 识别。
3.  **不稳定**：尝试强制使用旧 Driver 连接新浏览器导致频繁崩溃。

## 2. 架构变革方案
为了彻底脱离系统 Chrome 版本的不可控影响，我们实施了 **"Portable Chrome + Attach Mode"**（便携版+接管模式）方案。

### A. 独立环境 (Portable Chrome)
不再依赖用户电脑上安装的 Chrome。
- **版本锁定**: 锁定使用 **Chrome for Testing v121.0.6167.85**。
- **独立 Driver**: 配套下载对应的 ChromeDriver v121。
- **独立配置**: 使用独立的 `User Data` 目录，不污染系统原有 Chrome 配置。

### B. 接管模式 (Attach Mode)
放弃 "脚本启动浏览器" 的传统模式，改为 "人机协同" 模式：
1.  **启动**: 用户（或脚本）先启动浏览器，开启调试端口 `9222`。
2.  **登录**: 用户手动完成复杂的谷歌/TextNow 登录和验证码（只需一次）。
3.  **接管**: 自动化脚本通过 `9222` 端口接管已打开的浏览器，注入自动化指令。

## 3. 关键组件与脚本说明

| 脚本/文件 | 作用说明 |
| :--- | :--- |
| **`download_chrome.py`** | **[新]** 自动从 Google 官方下载 Portable Chrome v121 和 Driver，解压到 `chrome_portable/` 目录。 |
| **`run_portable.bat`** | **[新]** 启动便携版 Chrome 的批处理。参数：`--remote-debugging-port=9222` 和独立用户目录。 |
| **`textnow_automation.py`** | **[核心]** 已升级。初始化时会自动检测是否存在便携版 Driver。如果存在，强制使用 v121 Driver 连接；否则回退到系统 Driver。 |
| **`stealth_injector.js`** | **[新]** 一个 JS 脚本，在连接浏览器后立即注入，用于抹除 `navigator.webdriver` 等机器人特征。 |
| **`config.json`** | **[更新]** 新增 `REPLY_COOLDOWN_HOURS` 参数，允许配置自动回复的去重时间（默认 8 小时）。 |

## 4. 前端 UI 升级 (Web Control Panel)
`index.html` 和 `server.py` 进行了重大重构：
- **Stealth Mode 面板**：点击顶部的 "Stealth Mode" 按钮进入。
- **一键部署**：可以直接在网页上点击 "Install Portable (v121)" 下载浏览器。
- **状态监控**：实时显示 Chrome 是否在运行、Driver 是否就绪。
- **JS 修复**：修复了严重的 HTML/JS 嵌套错误，确保所有按钮（手动发送、AI 回复等）功能正常。

## 5. 操作流程变更
以后的标准操作流程如下：

1.  **启动服务**：运行 `run_ui.bat` (或 `server.py`)。
2.  **打开网页**：浏览器访问 `http://127.0.0.1:8000`。
3.  **启动浏览器**：
    *   点击 **Stealth Mode** -> **🚀 Launch Portable Chrome**。
    *   (如果是第一次，先点 Install Portable)。
4.  **手动登录**：在弹出的 Chrome 窗口中登录 TextNow。
5.  **开始自动化**：回到网页，点击顶部的 **Scan & Process Files** (或 Start Automation)。

## 6. 维护指南
- **如果要修改去重时间**：编辑 `config.json` 里的 `REPLY_COOLDOWN_HOURS`。
- **如果 Chrome 无法启动**：检查 `chrome_portable` 文件夹是否完整，可以删掉后重新运行 download 脚本。
- **如果 TextNow 封号/检测**：
    1.  运行 **Anti-Detection Test** (UI面板里) 检查环境分。
    2.  清除 `chrome_profile_v121` 文件夹（相当于清除缓存）重新登录。

---
*Created by Antigravity Assistant*
