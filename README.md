# 意韵成音 · AI 音乐生成器

让文字与图片蕴含的情感，绽放为可感知的音乐表达。

## 功能亮点
- 多模态输入：支持文字与图片分析
- 智能澄清：问答式完善音乐要素（风格/情绪/乐器等）
- 可控生成：时长、音色、乐器灵活配置
- 结果展示：播放器、歌词（可选）、下载与分享
- 认证系统：注册、登录、路由守卫，登录态本地持久化
- 主题样式：暗黑霓虹 + 浅霓虹变体（默认已启用）

---

## 架构与技术栈
- 前端：Vue 3 + Vite + Vue Router
  - 目录：`frontend-vue/`
  - 开发端口：5173（已配置 dev 代理到后端 8000）
- 后端：FastAPI + SQLAlchemy + passlib(bcrypt)
  - 目录：`backend/`
  - 运行端口：8000
  - 数据库：MySQL
  - 启动脚本：`start_backend.py`

### 目录结构（关键部分）
```
backend/
  app/
    api/
      routes.py           # API 路由（分析、澄清、生成、注册、登录等）
    models/
      db.py               # 数据库引擎/会话，支持 MySQL & SQLite 回退
      models.py           # ORM 模型（User 等）
      schemas.py          # Pydantic 模型
    services/
      ai_service.py       # 输入分析、提示词生成
      coze_music_service.py# 生成音乐的第三方服务封装
      session_manager.py  # 会话与澄清管理
    main.py               # FastAPI app 入口
  requirements.txt
frontend-vue/
  src/
    views/                # HomeView / AuthView / AccountView
    components/           # TopBar / AudioPlayer / Loading / Notification 等
    assets/styles.css     # 全站主题与组件样式（暗黑霓虹 + 浅霓虹）
    router/index.ts       # 路由与守卫（requiresAuth、guestOnly）
    App.vue / main.ts
  vite.config.ts          # 开发代理：/api -> 127.0.0.1:8000
start_backend.py          # 后端一键启动脚本
```

---

## 快速开始

### 前置要求
- Python 3.8+
- Node.js 18+（推荐 LTS）与 npm

> 国内安装 Node 依赖建议切换镜像：
```bash
npm config set registry https://registry.npmmirror.com
```

### 1) 启动后端（FastAPI）
```bash
# 安装依赖
python start_backend.py  # 首次执行会自动 pip install -r backend/requirements.txt

# 或手动：
# cd backend
# pip install -r requirements.txt
# uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

创建/配置环境变量 `backend/.env`（至少二选一）：
```dotenv
# 方案 A：一次性 DATABASE_URL（推荐）
DATABASE_URL=mysql+pymysql://user:password@host:3306/dbname

# 方案 B：单项变量（db.py 会拼接）
MYSQL_USER=root
MYSQL_PASSWORD=xxxx
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DB=dbname

# 可选
DB_FALLBACK_TO_SQLITE=true   # MySQL 不可达时回退到 backend/app.db（默认 true）
SQL_ECHO=false               # 打印 SQL 日志
```
> 首次启动会自动创建所需数据表。若 MySQL 连接失败且启用回退，将使用 `backend/app.db`（SQLite）。

### 2) 启动前端（Vue 3 + Vite）
```bash
cd frontend-vue
npm install
npm run dev  # http://localhost:5173
```
开发模式已配置代理：所有以 `/api` 开头的请求会转发至 `http://127.0.0.1:8000`。

#### 生产构建与预览
```bash
npm run build
npm run preview  # 本地预览 dist，默认端口 5174
```
如需修改接口基地址，请使用环境变量（示例）：
```bash
# 前端 .env 或系统环境中设置
VITE_API_BASE=/api   # 开发建议保持 /api（使用 Vite 代理）
```
生产部署时，请在网关/Nginx 将 `/api` 反向代理到后端服务。

---

## 前端路由与认证
- `/auth`：合并认证页（登录/注册 Tab），未登录访问受保护页面将跳到这里
- `/`：首页三步流程（输入 → 优化设置 → 生成结果），需登录
- `/account`：账户中心（查看当前用户、退出），需登录

登录成功后会将登录态持久化到 `localStorage`。退出将清除并跳回 `/auth`。

---

## 主要 API（简版）
- POST `/api/register`（JSON）
  - `{ username, email, password }` → `{ success, message }`
- POST `/api/login`（JSON）
  - `{ username, password }` → `{ success, message }`
- POST `/api/analyze/text`（FormData）
  - `text_content`、可选 `session_id` → `{ success, session_id, data }`
- POST `/api/analyze/image`（FormData）
  - `image`、可选 `session_id` → `{ success, session_id, data }`
- POST `/api/clarify`（JSON）
  - `{ session_id, question_id, selected_option }` → `{ success, ... }`
- POST `/api/generate/{session_id}`（JSON）
  - 生成参数（描述、时长、人声/乐器等）→ `{ success, data: { music_url, lyrics? } }`

> 返回体统一包含 `{ success, message?, data?, session_id? }`。登录失败和数据库异常均以 `success:false` 提示友好信息。

---

## 主题与样式
- 默认启用「浅霓虹」：在 `App.vue` 挂载时为 `body` 添加 `theme-soft` 类
- 如需切换为更深的霓虹主题，可移除该类或添加主题开关（在 `body.classList` 上切换）
- 全部样式位于 `frontend-vue/src/assets/styles.css`，已抽象变量：
  - `--primary-start / --primary-end / --primary`
  - `--bg-gradient / --card-bg / --border / --text`
  - `--topbar-bg / --topbar-border`


---

