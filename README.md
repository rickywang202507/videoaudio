# MU 呼叫处理 AI 增强版 (v2.0-Final)

此工具集成了视频转音频、电话录音转文字、AI 自动分析、紧急事项提醒以及自动回复生成功能。

## 新增功能 (v2.0)

1.  **电话录音处理**: 自动扫描 `PhoneReCO` 目录下的 `.wav` 文件并转录为文字存入 `PhoneTXT`。
2.  **AI 深度分析**: 自动识别通话摘要、检测语种，并判断是否为紧急处理事项。
3.  **智能回复生成**: 根据东航业务模板（购票、退改、特殊服务等）自动生成建议回复内容，支持一键复制。
4.  **现代化 UI 界面**: 基于 FastAPI 构建的 Web 管理后台，提供极致的视觉体验和操作便捷度。

## 目录配置

请在 `config.json` 中配置以下目录（默认为您提供的路径）：
- **视频录像**: `...\Videos\TEXTNOW\Video`
- **电话录音**: `C:\Users\DELL-MUYYZ04\Videos\TEXTNOW\PhoneReCO`
- **文字结果**: `C:\Users\DELL-MUYYZ04\Videos\TEXTNOW\PhoneTXT`

## 配置 AI 密钥

1. 打开 `config.json`。
2. 在 `AI_API_KEY` 处填入您的 OpenAI、Groq 或 Cohere 的 API 密钥。
3. 如果使用非 OpenAI 服务，请同时修改 `AI_BASE_URL`。

## 如何运行

1. **直接运行处理**: 双击 `run_process.bat`。
2. **启动 UI 界面**: 双击 `run_ui.bat`，然后在浏览器访问 `http://localhost:8000`。

## 技术栈

- **后端**: Python, FastAPI, Whisper, OpenAI API
- **前端**: HTML5, Vanilla CSS (Glassmorphism), JavaScript
- **库**: `moviepy`, `openai-whisper`, `openai`

---
*由 Antigravity 助手为您生成。*
