# TextNow 留言下载 - 最终解决方案

## 问题回顾

1. ❌ **JavaScript XHR方法失败** - 所有留言下载都遇到"Network error"
2. ❌ **CORS限制** - 即使移除 `withCredentials` 仍然失败
3. ✅ **发现UI下载按钮** - 用户发现每个留言右上方有三点菜单，点击后有下载选项

## 最终解决方案：使用UI下载按钮

### 工作流程

1. **找到留言的三点菜单按钮**
   - 尝试多种选择器（aria-label, class, SVG图标）
   - 备用方案：从audio元素向上查找父容器中的按钮

2. **验证是否为留言**
   - 检查附近是否有audio元素
   - 验证audio的src包含 `voicemail-media.textnow.com`

3. **监控下载文件夹**
   - 记录点击前Downloads文件夹中的文件列表
   - 点击菜单按钮 → 点击"Download"选项
   - 等待3秒让下载完成

4. **检测并重命名新文件**
   - 比较下载前后的文件列表
   - 找到新下载的文件
   - 移动并重命名到目标目录：`YYYY-MM-DD_电话号码_序号.wav`

### 代码关键部分

```python
# 1. 记录下载前的文件
from pathlib import Path
browser_download_folder = Path.home() / "Downloads"
before_files = set(browser_download_folder.glob("*"))

# 2. 点击菜单和下载
menu_btn.click()
time.sleep(0.8)
download_option.click()
time.sleep(3)

# 3. 找到新文件并重命名
after_files = set(browser_download_folder.glob("*"))
new_files = after_files - before_files
if new_files:
    new_file = list(new_files)[0]
    import shutil
    shutil.move(str(new_file), final_path)
```

## 优势

✅ **可靠性高** - 使用浏览器原生下载功能，不受CORS限制
✅ **自动重命名** - 自动将下载的文件重命名为规范格式
✅ **错误处理** - 完善的异常处理和日志输出
✅ **跳过已下载** - 自动检测已存在的文件，避免重复下载

## 使用方法

### 运行脚本
```powershell
python textnow_automation.py
```

### 配置
在 `textnow_automation.py` 第 470 行：
```python
# 下载所有留言（包括已读）
bot = TextNowBot(audio_dir, download_all_voicemails=True)

# 只处理未读留言
bot = TextNowBot(audio_dir, download_all_voicemails=False)
```

## 预期日志输出

```
[Mode] Download ALL voicemails (including read ones)
Found 49 conversations in the list. Scanning previews...
  [1] Class: 'uikit-summary-list__cell' | Text: (845) 848-0234 New voicemail Yesterday...
  >> Processing READ voicemail (download_all mode): (845) 848-0234 New v...
  >> Opening conversation: (845) 848-0234 New v... Clicking.
    [Skip SMS] This is a read voicemail, only downloading audio.
    [Info] Found 15 potential menu button(s)
    [Download 1] Attempting to click menu button...
    [Action] Found 'Download' option, clicking...
    [Wait] Waiting for download to complete...
    [Success] Downloaded: voicemail_8458480234.mp3
    [Success] Saved as: 2026-01-16_8458480234_1.wav
```

## 注意事项

1. **浏览器下载文件夹**
   - 默认使用 `C:\Users\<用户名>\Downloads`
   - 确保有足够的磁盘空间

2. **下载等待时间**
   - 当前设置为3秒
   - 如果网络较慢，可能需要增加等待时间

3. **文件名冲突**
   - 如果同一天同一号码有多个留言，使用序号区分
   - 例如：`2026-01-16_8458480234_1.wav`, `2026-01-16_8458480234_2.wav`

## 故障排除

### 问题：找不到菜单按钮
**解决方案**：
1. 运行 `test_voicemail_structure.py` 查看实际的DOM结构
2. 根据输出调整选择器

### 问题：找不到下载选项
**可能原因**：
- 菜单文本可能是其他语言
- 菜单结构可能不同

**解决方案**：
- 在浏览器中手动检查菜单文本
- 更新代码中的 `download_text` 列表

### 问题：下载的文件没有被检测到
**可能原因**：
- 下载时间超过3秒
- 文件下载到了其他位置

**解决方案**：
- 增加等待时间（修改 `time.sleep(3)` 为更大的值）
- 检查浏览器的下载设置

## 下一步优化

1. ✅ 使用UI下载按钮（已完成）
2. ✅ 自动重命名文件（已完成）
3. 🔄 添加下载进度显示
4. 🔄 支持批量下载多个留言
5. 🔄 自动转录下载的留言
