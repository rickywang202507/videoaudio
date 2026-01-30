# TextNow 自动化脚本说明

## 当前状态 (2026-01-16)

**脚本功能已精简为专注于自动回复 SMS。**

鉴于 TextNow 的安全限制（CORS）和 UI 结构的复杂性，我们决定**移除自动下载留言音频**的功能。现在的脚本更加轻量级且稳定。

### 主要功能

1. **监控未读消息**：
   - 脚本会自动检测**未读的未接来电** (Missed Call) 和**未读的留言** (New Voicemail)。

2. **自动回复 SMS**：
   - 对于每个未读的未接来电/留言，脚本会自动发送一条预设的 SMS 回复。
   - 回复内容在 `textnow_automation.py` 顶部的 `SMS_TEMPLATE` 变量中配置。
   - 脚本具有防止重复发送的机制（检查历史记录）。

3. **手动下载留言**：
   - 用户需自行在 TextNow 网页界面上手动点击留言右侧的三点菜单，选择 **Download** 来保存音频文件。
   - 这避免了脚本下载失败或下载到错误文件的风险。

---

## 如何运行

确保 Chrome 浏览器已以调试模式启动 (端口 9222)，并且已经登录 TextNow。

```powershell
python textnow_automation.py
```

### 配置选项

在 `textnow_automation.py` 的底部：

```python
# download_all_voicemails=False (默认)
# 只处理未读消息。这是推荐的模式。
bot = TextNowBot(audio_dir, download_all_voicemails=False)
```

如果设置为 `True`，脚本会遍历所有留言（包括已读），但这仅仅会打开对话框，不会进行任何下载操作（因为代码已移除），所以建议保持为 `False`。

## 注意事项

- **已读消息**：脚本会跳过已读的消息。如果您想让脚本处理某个旧的未接来电，请在网页上手动将其标记为“未读”。
- **系统提示音**：脚本不再涉及音频识别，因此无需担心系统提示音过滤问题。
