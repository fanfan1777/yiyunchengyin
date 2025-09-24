# yiyunchengyin
## 意韵成音（AI 音乐生成器）

一个基于多模态 AI 的音乐生成小应用：
- 文本/图片理解：调用 Qwen 多模态接口分析用户文本或图片，提取音乐元素
- 澄清问答：根据分析结果向用户提问以细化需求，生成最终音乐提示词
- 音乐生成：对接 Coze 的对话接口触发音乐插件生成音频，返回下载链接与可选歌词
- 前端演示页：简洁的 Web 界面（纯静态）与后端 API 交互

---

### 目录结构
```text
.
├─ backend/
│  ├─ app/
│  │  ├─ api/                # FastAPI 路由
│  │  ├─ models/             # Pydantic 模型
│  │  ├─ services/           # 业务服务（AI、Coze、会话）
│  │  └─ main.py             # FastAPI 应用入口
│  ├─ requirements.txt       # 后端依赖
│  └─ env.example            # 环境变量示例（复制为 .env 并填写）
├─ frontend/                 # 前端静态文件（index.html / script.js / styles.css）
├─ start_backend.py          # 一键启动后端脚本（自动检查依赖与 .env）
└─ README.md
```

---

### 环境要求
- Python 3.8+
- 可访问外部网络（用于调用 DashScope 与 Coze API）

---

### 快速开始
1) 克隆仓库并进入目录
```bash
# 任选其一（HTTPS / SSH）
# git clone https://github.com/<your>/<repo>.git
# git clone git@github.com:<your>/<repo>.git
cd <repo>
```

2) 创建虚拟环境并安装依赖
```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -r backend/requirements.txt
```

3) 配置环境变量（重要）
- 复制 `backend/env.example` 为 `backend/.env`，并填写实际值
```bash
# Windows
copy backend\env.example backend\.env
# macOS/Linux
# cp backend/env.example backend/.env
```
- 必填项：
  - `DASHSCOPE_API_KEY`：Qwen(DashScope) API Key
  - `COZE_TOKEN`：Coze 访问令牌
  - `COZE_BOT_ID`：Coze 机器人 ID
- 可选项（有默认值）：`HOST`、`PORT`、`DEBUG`、`MAX_FILE_SIZE`

4) 启动后端
```bash
# 方式A：一键脚本（推荐）
python start_backend.py

# 方式B：手动启动
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- 健康检查：`http://127.0.0.1:8000/health`
- API 前缀：`/api`

5) 打开前端
- 直接用浏览器打开 `frontend/index.html`
- 若需本地静态服务：
```bash
# 在仓库根目录启动一个简易静态服务器（任选其一）
python -m http.server 5500
# 或使用任意本地 Web 服务器
```

---

### API 速览（主要端点）
- `POST /api/analyze/text`
  - 表单字段：`text_content`，`session_id`(可选)
- `POST /api/analyze/image`
  - Multipart：`image` 文件，`session_id`(可选)
- `POST /api/clarify`
  - JSON：澄清回答，推进问题收集
- `POST /api/generate/{session_id}`
  - 使用当前会话的最终提示词触发音乐生成
- `GET /api/session/{session_id}`
  - 查询指定会话状态
- `GET /api/sessions`
  - 列出所有会话（调试用途）

示例（分析文本）：
```bash
curl -X POST http://127.0.0.1:8000/api/analyze/text \
  -F "text_content=来一段温柔浪漫，适合夜晚的钢琴曲"
```

---

### 环境变量说明（backend/.env）
- `HOST`：后端监听地址，默认 `127.0.0.1`
- `PORT`：后端端口，默认 `8000`
- `DEBUG`：`True/False`，控制开发热重载与日志，默认 `True`
- `MAX_FILE_SIZE`：上传图片大小上限，默认 `10485760`（10MB）
- `DASHSCOPE_API_KEY`：DashScope API Key（必填）
- `COZE_TOKEN`：Coze 访问令牌（必填）
- `COZE_BOT_ID`：Coze 机器人 ID（必填）

说明：后端运行时会加载 `backend/.env`（`python-dotenv`），`start_backend.py` 也支持从 `backend/env.example` 自动生成 `.env`。

---

### 安全与合规
- 代码已移除硬编码密钥，所有敏感信息仅来自环境变量
- `.gitignore` 已忽略 `.env`；请勿将真实密钥提交到仓库
- 若历史提交中曾包含密钥，请在公开项目前清理历史（如 `git filter-repo`），并在服务端重置令牌
- 生产环境请将 CORS 的 `allow_origins` 收紧为你的实际域名

---

### 部署建议
- 生产启动示例：
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```
- 建议在反向代理（Nginx/ALB）后运行，并开启 HTTPS
- 为外部 API 设置合理的超时与重试策略，监控错误码与限流
- 使用系统服务或进程管理（systemd/supervisor/docker）保证高可用

---

### 开发说明
- 主要依赖：`fastapi`、`uvicorn`、`requests`、`pydantic`、`python-dotenv`、`python-multipart`
- 代码风格：清晰易读，

---

### 反馈与支持
如果你在本项目中遇到问题或希望新增功能，欢迎提 Issue 或 PR。

