# 意韵成音 前端（Vue3 版）

本目录为新建的 Vue3 + Vite + Vue Router 前端。已将原有纯 HTML/JS/CSS 的页面迁移为组件化视图：
- 首页功能（分析、参数设置、生成）见 `src/views/HomeView.vue`
- 登录页 `src/views/LoginView.vue`
- 注册页 `src/views/RegisterView.vue`
- 通用组件：`Loading`、`Notification`、`AudioPlayer`、`StepIndicator`

## 开发启动

1. 安装依赖
```bash
npm install
```
2. 启动本地开发
```bash
npm run dev
```
默认 http://localhost:5173 打开。Vite 已设置代理到后端 `http://127.0.0.1:8000`，前端所有 `/api` 请求将被转发。

## 构建与预览
```bash
npm run build
npm run preview
```

## 后端接口
- 文本分析：POST `/api/analyze/text` (FormData: `text_content`, 可选 `session_id`)
- 图片分析：POST `/api/analyze/image` (FormData: `image`, 可选 `session_id`)
- 提交澄清：POST `/api/clarify` (JSON: `session_id`, `question_id`, `selected_option`)
- 生成音乐：POST `/api/generate/{session_id}` (JSON: 生成参数)
- 登录：POST `/api/login`，注册：POST `/api/register`

## 样式
- 样式来自原 `frontend/styles.css`，已迁移到 `src/assets/styles.css` 并在入口引入。

## 注意
- 若后端端口或地址不同，请修改 `vite.config.ts` 中的代理 `target`。

