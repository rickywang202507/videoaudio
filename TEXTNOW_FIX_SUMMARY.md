# TextNow 自动化修复完成总结

## 修复内容

### 1. ✅ 过滤系统提示音
**问题**: 脚本下载了所有 `<audio>` 元素，包括24个系统提示音（拨号音、按键音等）

**解决方案**:
```python
# 只下载真正的留言文件
if "voicemail-media.textnow.com" not in src:
    print(f"    [Skip] System sound (not voicemail): {src[:60]}...")
    continue
```

### 2. ✅ 支持下载所有留言（包括已读）
**问题**: 原代码只处理未读的未接来电，已读的留言不会被下载

**解决方案**:
- 添加 `download_all_voicemails` 参数（默认 True）
- 当设置为 True 时，下载所有留言（包括已读的）

### 3. ✅ 只对未读留言发送SMS
**问题**: 需要避免对已读留言重复发送SMS

**解决方案**:
```python
if is_unread_candidate:
    # 检查是否已回复，如果没有则发送SMS
    ...
else:
    print(f"    [Skip SMS] This is a read voicemail, only downloading audio.")
```

### 4. ✅ 修复CORS错误
**问题**: 添加 `xhr.withCredentials = true` 导致跨域请求失败

**解决方案**:
- 移除 `xhr.withCredentials = true`
- 留言URL本身已包含JWT token，不需要额外的cookies

### 5. ✅ 改进日志输出
- 区分"系统提示音"和"真实留言"
- 区分"未读"和"已读"留言
- 显示下载文件的字节数
- 提供详细的错误信息

## 使用说明

### 运行脚本
```powershell
python textnow_automation.py
```

### 配置选项
在 `textnow_automation.py` 第 470 行：

**下载所有留言（包括已读）**:
```python
bot = TextNowBot(audio_dir, download_all_voicemails=True)  # 当前设置
```

**只处理未读留言**:
```python
bot = TextNowBot(audio_dir, download_all_voicemails=False)
```

## 工作流程

### 对于未读的未接来电/留言：
1. ✅ 检测到未读标记（badge/bold text）
2. ✅ 点击打开对话
3. ✅ 检查是否已发送SMS
4. ✅ 如果没有，发送自动回复SMS
5. ✅ 下载留言音频文件（如果有）

### 对于已读的留言：
1. ✅ 检测到"Voicemail"关键词
2. ✅ 点击打开对话
3. ❌ 跳过SMS发送（避免重复）
4. ✅ 下载留言音频文件（如果有且未下载）

## 文件命名规则

格式：`YYYY-MM-DD_电话号码_序号.wav`

示例：
- `2026-01-16_8458480234_1.wav`
- `2026-01-16_3067375254_1.wav`

## 预期日志输出

```
[Mode] Download ALL voicemails (including read ones)
Found 49 conversations in the list. Scanning previews...
  [1] Class: 'uikit-summary-list__cell' | Text: (845) 848-0234 New voicemail Yesterday...
  >> Processing READ voicemail (download_all mode): (845) 848-0234 New v...
  >> Opening conversation: (845) 848-0234 New v... Clicking.
    [Skip SMS] This is a read voicemail, only downloading audio.
    [Info] Found 25 audio element(s). Filtering for voicemails...
    [Skip] System sound (not voicemail): https://www.textnow.com/messaging/assets/sounds/call_outgoin...
    [Skip] System sound (not voicemail): https://www.textnow.com/messaging/assets/sounds/call_incomin...
    ...（跳过24个系统提示音）
    [Download] Fetching voicemail from: https://voicemail-media.textnow.com/?t=eyJ0eXAiOiJ...
    [Success] Saved voicemail: 2026-01-16_8458480234_1.wav (245678 bytes)
```

## 常见问题

**Q: 为什么有些留言下载失败？**
A: 可能原因：
- 网络问题
- 留言已过期或被删除
- JWT token 过期

**Q: 如何避免重复下载？**
A: 脚本会自动检查文件是否已存在，跳过已下载的留言。

**Q: 为什么已读留言不发送SMS？**
A: 为了避免重复发送。如果需要重新发送，请手动删除对话历史中的SMS。

**Q: 下载的文件在哪里？**
A: 默认路径：`C:\Users\DELL-MUYYZ04\Videos\TEXTNOW\PhoneReCO`
   可在 `config.json` 中的 `WAV_DIR` 字段修改。

## 技术细节

### 留言URL格式
```
https://voicemail-media.textnow.com/?t=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```
- `t` 参数是JWT (JSON Web Token)
- Token包含认证信息和留言ID
- 不需要额外的cookies或credentials

### 下载方法
使用 JavaScript XHR 在浏览器上下文中下载：
```javascript
var xhr = new XMLHttpRequest();
xhr.open('GET', url, true);
xhr.responseType = 'blob';
xhr.onload = function() { ... };
xhr.send();
```

### 未读检测方法
1. 检查元素class中的 'unread' 关键词
2. 查找 badge/indicator 元素
3. 检查文本的 font-weight（bold = 未读）

## 下一步优化建议

1. **添加重试机制**: 对于下载失败的留言，自动重试2-3次
2. **批量下载**: 一次性下载多个留言，提高效率
3. **进度显示**: 显示下载进度（X/Y个留言已下载）
4. **错误汇总**: 在最后显示所有失败的下载列表
5. **自动转录**: 下载后自动调用 audio_processor 进行转录
