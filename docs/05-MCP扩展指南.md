# MCP 扩展指南

本文档说明如何为 Agent 接入 MCP (Model Context Protocol) Servers，以及框架的模块化设计。

## 模块结构

```
promotional_copy_generation/mcp/
├── __init__.py      # 对外 API
├── client.py        # MCP 客户端封装（懒加载、生命周期）
├── config.py        # 加载 mcp_servers.yaml，支持 ${VAR} 环境变量展开
├── registry.py      # Stage -> 工具名映射（配置驱动）
├── transports.py    # 传输层工厂（stdio/http/sse），可扩展
├── provider.py      # 主入口：get_tools_for_stage(stage)
└── loader.py        # 向后兼容的 facade
```

## 配置

### mcp_servers.yaml

```yaml
servers:
  my_server:
    enabled: true
    transport: stdio   # stdio | http | sse
    command: npx
    args: ["-y", "@some/mcp-server"]
    env:
      API_KEY: ${API_KEY}
    tools_filter: ["tool_a", "tool_b"]  # 可选，不填则暴露全部

# 可选：stage_tools 作为 stage_contexts 中未配置 mcp_tools 时的回退
stage_tools:
  context_enhance: ["tool_a"]
```

### stage_contexts.yaml

```yaml
stages:
  context_enhance:
    prompt_template: "prompts/context_enhance.txt"
    mcp_tools: ["search_similar_copies", "get_trending_topics"]  # 该阶段可用的 MCP 工具
```

## 使用方式

### 1. 按阶段获取工具

```python
from promotional_copy_generation.mcp import get_tools_for_stage

tools = get_tools_for_stage("context_enhance")
# 返回 LangChain 兼容的 BaseTool 列表
```

### 2. 在 Stage Context 中获取

`load_stage_context(stage)` 返回的上下文中包含 `mcp_tools` 字段（当该阶段配置了 `mcp_tools` 时）：

```python
from promotional_copy_generation.context import load_stage_context

ctx = load_stage_context("context_enhance")
tools = ctx.get("mcp_tools", [])
```

### 3. 检查 MCP 是否可用

```python
from promotional_copy_generation.mcp import is_mcp_available

if is_mcp_available():
    tools = get_tools_for_stage("context_enhance")
```

## 扩展传输类型

如需支持自定义传输（如 WebSocket），可注册新的 transport handler：

```python
from promotional_copy_generation.mcp import register_transport

def _add_websocket(client, name, cfg):
    client.add_server(
        name,
        transport="websocket",
        url=cfg.get("url"),
    )

register_transport("websocket", _add_websocket)
```

## 接入新 MCP Server 步骤

1. 在 `config/mcp_servers.yaml` 中添加 server 配置，设置 `enabled: true`
2. 在 `config/stage_contexts.yaml` 中为需要该工具的 stage 添加 `mcp_tools`
3. 若节点需要调用工具，需在节点逻辑中接入 tool-calling（如 ReAct、bind_tools 等）

## 依赖

- `langchain-mcp-adapters>=0.2.0`：连接 MCP Server 并转换为 LangChain Tools
- 未安装时，框架会静默返回空工具列表，不阻塞主流程
