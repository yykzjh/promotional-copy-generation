# 推广文案生成 AI Agent

基于 LangGraph 的 AI Agent，支持 Skills 与 MCP。具备上下文增强、图像理解、文案撰写、图像生成等能力。

## 快速开始

```bash
# 安装依赖
uv sync

# 启动服务（需先部署 vLLM 或其他本地 LLM）
uv run promotional-copy
# 或
uv run uvicorn promotional_copy_generation.main:app --reload --host 0.0.0.0 --port 8000
```

## 配置

将 `.env.example` 复制为 `.env` 并配置：

| 变量 | 说明 | 使用方 |
|------|------|--------|
| `LLM_MAIN_BASE_URL` | 文本→文本 API 地址 | copy_writer, safety, context_enhancer（无图）, image_prompt（无图） |
| `LLM_MAIN_MODEL` | 文本→文本模型 | 同上 |
| `LLM_MAIN_MODEL_API_KEY` | 文本→文本 API 密钥 | 同上 |
| `VLM_TEXT_GEN_BASE_URL` | 图像+文本→文本 API 地址 | context_enhancer, image_prompt（有图时） |
| `VLM_TEXT_GEN_MODEL` | 图像+文本→文本模型 | 同上 |
| `VLM_TEXT_GEN_MODEL_API_KEY` | 图像+文本→文本 API 密钥 | 同上 |
| `LLM_IMAGE_GEN_BASE_URL` | 文本→图像 API 地址 | image_generator |
| `LLM_IMAGE_GEN_MODEL` | 文本→图像模型；设置后启用图像生成 | image_generator |
| `LLM_IMAGE_GEN_MODEL_API_KEY` | 图像生成 API 密钥 | image_generator |
| `FORBIDDEN_WORDS_FILE` | 违禁词列表路径 | safety checker |
| `SAFETY_USE_LLM` | 是否使用 LLM 做合规检查（默认 `true`） | safety checker |
| `SAFETY_LLM_MODEL` | 合规检查模型（默认主模型） | safety checker |
| `SKILLS_DIRS` | 额外 Skill 目录，逗号分隔 | skills loader |
| `CONFIG_DIR` | 配置目录（默认 `config`） | stage_contexts, prompts |
| `LOG_LEVEL` | 日志级别（默认 `INFO`） | service |
| `MAX_CONCURRENT_JOBS` | 最大并发任务数（默认 `10`） | service |

## API

- `GET /api/health` - 健康检查
- `POST /api/generate` - 生成推广文案（multipart/form-data）

## 模型部署

大模型部署框架位于 `model_deployment/`，支持 vLLM（LLM）和 diffusers（图像生成）。详细配置见 `model_deployment/README.md`。

### 安装

```bash
uv sync --extra model-deployment
```

### 模型启动示例

先启动模型服务，再启动 Agent。

```bash
# 1. 主模型 (文本→文本, port 8000)
uv run python -m model_deployment.launch_vllm main --port 8000 --tensor-parallel-size 2

# 2. 多模态 VL 模型 (图像+文本→文本, port 8001) - 另开终端
uv run python -m model_deployment.launch_vllm vl --port 8001 --tensor-parallel-size 2

# 3. 图像生成 (文本→图像, port 8002) - 另开终端
uv run python -m model_deployment.diffusers_serve --port 8002
```

或直接使用 vllm 命令：

```bash
vllm serve Qwen/Qwen3-30B-A3B-Instruct-2507-FP8 --host 0.0.0.0 --port 8000
vllm serve Qwen/Qwen3-VL-8B-Instruct-FP8 --host 0.0.0.0 --port 8001
```

## MCP (Model Context Protocol)

项目内置模块化 MCP 框架，用于接入外部工具。在 `config/mcp_servers.yaml` 中配置服务器，在 `config/stage_contexts.yaml` 中通过 `mcp_tools` 映射到各阶段。详见 `docs/05-MCP扩展指南.md`。

## 文档

参见 `docs/` 目录。
