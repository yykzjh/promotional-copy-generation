# Model Deployment

大模型部署框架，支持 vLLM（LLM）和 diffusers（图像生成）两种后端。

## 模型与端口

| 模型 | 用途 | 后端 | 默认端口 | 配置 |
|------|------|------|----------|------|
| Qwen/Qwen3-30B-A3B-Instruct-2507-FP8 | Agent 主模型 (文本→文本) | vLLM | 8000 | config/model_deployment/main.yaml |
| Qwen/Qwen3-VL-8B-Instruct-FP8 | 多模态 (图像+文本→文本) | vLLM | 8001 | config/model_deployment/vl.yaml |
| Qwen/Qwen-Image-2512 | 文本→图像 | diffusers | 8002 | config/model_deployment/image_gen.yaml |

## 安装

```bash
uv sync --extra model-deployment
```

## 启动

### vLLM 模型

```bash
# Agent 主模型 (port 8000，来自配置文件)
uv run python -m model_deployment.launch_vllm main

# 多模态 VL 模型 (port 8001)
uv run python -m model_deployment.launch_vllm vl

# 命令行参数直接传给 vllm，覆盖配置文件默认值
uv run python -m model_deployment.launch_vllm main --port 9000 --host 0.0.0.0
uv run python -m model_deployment.launch_vllm main --tensor-parallel-size 2
uv run python -m model_deployment.launch_vllm vl --gpu-memory-utilization 0.95
```

或直接使用 vllm 命令：

```bash
vllm serve Qwen/Qwen3-30B-A3B-Instruct-2507-FP8 --host 0.0.0.0 --port 8000
vllm serve Qwen/Qwen3-VL-8B-Instruct-FP8 --host 0.0.0.0 --port 8001
```

### diffusers 图像生成

```bash
uv run python -m model_deployment.diffusers_serve

# 命令行参数覆盖配置文件
uv run python -m model_deployment.diffusers_serve --port 8003 --host 0.0.0.0
```

服务暴露 OpenAI 兼容的 `POST /v1/images/generations` 接口。

## 配置

配置文件位于 `config/model_deployment/`：

- `main.yaml` - 主模型 vLLM 参数
- `vl.yaml` - VL 模型 vLLM 参数
- `image_gen.yaml` - 图像生成 diffusers 参数

修改 `host`、`port`、`tensor_parallel_size`、`gpu_memory_utilization` 等以适配环境。`launch_vllm` 会将脚本后的所有参数原样传给 vllm，用于覆盖配置默认值。

## 与 Agent 的 .env 对应

| 部署服务 | .env 变量 |
|----------|-----------|
| main (port 8000) | LLM_MAIN_BASE_URL=http://localhost:8000/v1 |
| vl (port 8001) | VLM_TEXT_GEN_BASE_URL=http://localhost:8001/v1 |
| image_gen (port 8002) | LLM_IMAGE_GEN_BASE_URL=http://localhost:8002/v1 |
