# TextNow 反机器人检测解决方案

## 问题描述

TextNow 加强了对自动化机器人的检测，导致长按获取验证码等操作失败。正常浏览器可以通过，但自动化脚本被拦截。

## 解决方案

本解决方案提供了多层次的反检测措施：

### 1. 增强的Chrome启动配置

**文件**: `run_chrome_stealth.bat`

新的启动脚本包含更多反检测标志：
- `--disable-blink-features=AutomationControlled` - 禁用自动化控制特征
- `--exclude-switches=enable-automation` - 移除自动化开关
- `--disable-web-security` - 禁用Web安全检查
- 使用独立的用户配置文件 `chrome_profile_stealth`

**使用方法**:
```bash
run_chrome_stealth.bat
```

### 2. JavaScript反检测注入

**文件**: `stealth_injector.js`

自动注入的JavaScript代码会：
- 移除 `navigator.webdriver` 属性
- 伪装 Chrome 运行时对象
- 模拟真实的浏览器插件
- 隐藏自动化相关的window属性
- 伪装硬件信息（CPU核心数、内存等）

### 3. Python Selenium增强

**文件**: `textnow_automation.py` (已更新)

增强功能：
- 自动加载并注入 `stealth_injector.js`
- 使用CDP命令修改User-Agent
- 在每个新页面加载时自动应用反检测脚本

### 4. Selenium-Stealth库

**文件**: `stealth_utils.py`

提供高级功能：
- `create_stealth_driver()` - 创建配置好的stealth驱动
- `human_like_click()` - 模拟人类点击（带鼠标移动）
- `human_like_typing()` - 模拟人类打字（逐字符+随机延迟）
- `human_like_delay()` - 随机延迟
- `random_scroll()` - 随机滚动页面

## 使用步骤

### 步骤 1: 安装依赖

```bash
pip install selenium-stealth
```

或者安装所有依赖：

```bash
pip install -r requirements.txt
```

### 步骤 2: 启动Stealth模式Chrome

```bash
run_chrome_stealth.bat
```

**重要**: 
- 在打开的Chrome窗口中手动登录TextNow
- 完成任何验证码或人机验证
- 保持此窗口打开（可以最小化）

### 步骤 3: 运行自动化脚本

```bash
python textnow_automation.py
```

或使用现有的批处理文件：

```bash
run_monitor.bat
```

## 测试反检测效果

运行测试脚本检查是否被检测为机器人：

```bash
python stealth_utils.py
```

这会打开一个机器人检测测试页面：
- **绿色** = 未被检测为机器人 ✅
- **红色** = 被检测为机器人 ❌

## 高级技巧

### 1. 手动完成验证码

如果遇到验证码：
1. 在 `run_chrome_stealth.bat` 打开的窗口中手动完成
2. 自动化脚本会在同一个会话中继续运行
3. 登录状态会保存在 `chrome_profile_stealth` 目录中

### 2. 增加人类行为模拟

在 `textnow_automation.py` 中已经包含：
- 随机延迟（2-5秒思考时间，3-7秒校对时间）
- 逐字符输入（而非一次性粘贴）
- 使用JavaScript注入（更自然）

### 3. 降低操作频率

如果仍然被检测：
- 增加扫描间隔（从30秒改为60秒或更长）
- 减少每次扫描的对话数量
- 添加更多随机延迟

修改 `textnow_automation.py` 第750行：

```python
wait_sec = 60  # 从30改为60秒
```

### 4. 使用代理IP（可选）

如果IP被标记，可以配置代理：

```python
options.add_argument('--proxy-server=http://your-proxy:port')
```

## 常见问题

### Q1: 仍然被检测为机器人怎么办？

**答**: 
1. 确保使用 `run_chrome_stealth.bat` 而不是旧的 `run_chrome_debug.bat`
2. 检查是否安装了 `selenium-stealth`: `pip install selenium-stealth`
3. 在Chrome中手动完成一次完整的登录和操作流程
4. 增加操作间隔时间

### Q2: 验证码无法通过？

**答**: 
1. 在 `run_chrome_stealth.bat` 打开的Chrome窗口中手动完成验证码
2. 不要关闭这个窗口
3. 验证通过后，自动化脚本可以继续使用这个会话

### Q3: 如何知道是否成功绕过检测？

**答**: 
1. 运行 `python stealth_utils.py` 查看检测结果
2. 查看控制台输出中的 `[Stealth]` 标记
3. 检查是否能正常发送消息

### Q4: Chrome配置文件在哪里？

**答**: 
- 新配置: `chrome_profile_stealth/` （推荐使用）
- 旧配置: `chrome_profile_debug/`

可以删除旧配置，使用新的stealth配置。

## 技术原理

### 检测方法

TextNow 和其他网站检测机器人的常见方法：

1. **navigator.webdriver** - Selenium会设置此属性为true
2. **Chrome DevTools Protocol** - 检测CDP特征
3. **缺失的浏览器对象** - 如 `window.chrome`
4. **行为模式** - 过快的操作、完美的定时
5. **浏览器指纹** - 插件、语言、硬件信息异常

### 绕过方法

我们的解决方案针对每种检测方法：

1. **移除webdriver属性** - JavaScript注入
2. **隐藏CDP特征** - Chrome启动参数
3. **伪装浏览器对象** - 注入完整的chrome对象
4. **模拟人类行为** - 随机延迟、鼠标移动、逐字输入
5. **正常化指纹** - 伪装插件、语言、硬件信息

## 文件清单

- ✅ `run_chrome_stealth.bat` - 增强的Chrome启动脚本
- ✅ `stealth_injector.js` - JavaScript反检测代码
- ✅ `stealth_utils.py` - Python工具库（人类行为模拟）
- ✅ `textnow_automation.py` - 更新的主脚本（已集成stealth）
- ✅ `requirements.txt` - 更新的依赖列表

## 更新日志

**2026-01-30**:
- ✅ 创建增强的Chrome启动脚本
- ✅ 添加JavaScript反检测注入
- ✅ 集成selenium-stealth库
- ✅ 添加人类行为模拟工具
- ✅ 更新主自动化脚本

## 下一步

如果上述方法仍然不够，可以考虑：

1. **使用undetected-chromedriver** - 更强大的反检测库
2. **浏览器扩展** - 安装真实的浏览器扩展增加真实性
3. **Canvas指纹伪装** - 修改Canvas渲染指纹
4. **WebGL指纹伪装** - 修改WebGL渲染指纹
5. **音频指纹伪装** - 修改AudioContext指纹

需要这些高级功能请告知！
