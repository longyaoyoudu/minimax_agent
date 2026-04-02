# Mini Agent — 基于 MiniMax M2.1 的轻量级 AI Agent 开发框架

> 最小化却专业的 Agent 开发范式，基于 MiniMax M2.1 模型 / Anthropic 兼容 API / MCP 协议 / Claude Skills

[![Python](https://img.shields.io/badge/Python-3.8+-green)](https://www.python.org/)
[![MiniMax-M2](https://img.shields.io/badge/MiniMax-M2.1-blue)](https://github.com/MiniMax-AI/MiniMax-M2)
[![MCP](https://img.shields.io/badge/MCP-Protocol-orange)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📌 项目概述

Mini Agent 是一个**轻量级 AI Agent 开发框架**，围绕 MiniMax M2.1 模型构建，提供完整可靠的 Agent 执行循环。核心特点：

- **MiniMax M2.1 模型**：支持 interleaved thinking（交错思考），释放 M2 的长程推理能力
- **Anthropic 兼容 API**：无需更换 SDK，直接使用 `Anthropic` SDK 调用 MiniMax M2.1，支持 extended thinking 思考过程
- **MCP 协议集成**：原生支持 Model Context Protocol，可接入知识图谱、Web Search 等外部工具
- **Claude Skills 兼容**：内置 15+ 专业 Skills，覆盖文档生成、设计、测试、开发全流程
- **智能上下文管理**：自动摘要历史消息，支持无限长任务，token 限制可配置
- **持久化记忆**：Session Note Tool 跨会话记录关键信息

---

## 🗂️ 项目结构

```
Mini-Agent/
├── mini_agent/
│   ├── agent.py               # 核心 Agent 类（执行循环、工具调用、上下文摘要）
│   ├── cli.py                 # 命令行入口
│   ├── config.py              # 配置管理（YAML + Pydantic 模型）
│   ├── logger.py              # 详细日志（每次请求/响应/工具执行）
│   ├── retry.py               # 指数退避重试机制
│   │
│   ├── llm/
│   │   ├── base.py            # LLMClient 基类（抽象接口）
│   │   ├── llm_wrapper.py      # 统一入口（自动路由 Anthropic/OpenAI）
│   │   ├── anthropic_client.py # Anthropic 协议客户端（M2.1 兼容）
│   │   └── openai_client.py   # OpenAI 协议客户端
│   │
│   ├── schema/
│   │   └── schema.py          # 数据模型：Message / ToolCall / LLMResponse / TokenUsage
│   │
│   ├── tools/
│   │   ├── base.py            # Tool 基类（ToolResult / to_schema / to_openai_schema）
│   │   ├── file_tools.py       # 文件操作工具（read_file / write_file / edit_file）
│   │   ├── bash_tool.py        # Shell 命令执行工具
│   │   ├── note_tool.py        # Session Note Tool（record_note / recall_notes）
│   │   ├── skill_loader.py     # Claude Skills 加载器
│   │   ├── skill_tool.py       # Skills 动态调用工具
│   │   └── mcp_loader.py       # MCP 工具加载器
│   │
│   ├── skills/                # Claude Skills 集合
│   │   ├── algorithmic-art/    # 算法艺术生成（p5.js + seeded randomness）
│   │   ├── canvas-design/      # Canvas 视觉设计（.png/.pdf）
│   │   ├── artifacts-builder/   # React/Tailwind/shadcn UI 构建
│   │   ├── brand-guidelines/   # Anthropic 品牌样式
│   │   ├── docx/               # Word 文档生成
│   │   ├── pdf/                # PDF 处理
│   │   ├── pptx/               # PPT 生成
│   │   ├── xlsx/               # Excel 处理
│   │   ├── mcp-server/         # MCP Server 开发
│   │   ├── webapp-testing/      # Playwright Web 测试
│   │   ├── skill-creator/       # Skills 开发指南
│   │   └── ...                 # 更多 Skills
│   │
│   ├── config/
│   │   ├── config-example.yaml # 配置模板
│   │   └── system_prompt.md    # 系统提示词模板
│   │
│   └── acp/
│       └── server.py           # ACP (Agent Communication Protocol) 服务器
│
├── docs/
│   ├── DEVELOPMENT_GUIDE.md    # 开发指南
│   └── PRODUCTION_GUIDE.md      # 生产部署指南
│
├── scripts/
│   ├── setup-config.sh        # macOS/Linux 配置初始化脚本
│   └── setup-config.ps1       # Windows 配置初始化脚本
│
└── README.md
```

---

## 🧠 核心架构

### Agent 执行循环

```
用户输入
   ↓
┌──────────────────────────────────────┐
│  while step < max_steps:             │
│    1. 上下文摘要检查                  │
│       （tiktoken cl100k_base 编码）   │
│    2. LLM.generate()                 │
│       （Anthropic extended thinking） │
│    3. 打印 thinking + content         │
│    4. 无 tool_calls？→ 返回答案       │
│    5. 执行工具调用                    │
│       （try/except 异常捕获）         │
│    6. 追加 tool result message       │
│    7. step++                         │
└──────────────────────────────────────┘
   ↓
返回最终答案
```

### 上下文摘要策略

当 token 超出限制（默认 80K）时，自动触发摘要：

```
原结构: system → user1 → assistant1 → tool1 → ... → user2 → assistant2 → ...
摘要后: system → user1 → summary1 → user2 → summary2 → user3 → ...
```

- **保留所有 user 消息**（用户意图）
- **摘要 agent 执行过程**（工具调用 + 返回结果）
- **使用 LLM 生成摘要文本**，确保关键信息不丢失

### 双协议 LLM 客户端

```python
# LLMClient 自动路由
if provider == "anthropic":
    client = AnthropicClient(api_base=".../anthropic", model="MiniMax-M2.1")
elif provider == "openai":
    client = OpenAIClient(api_base=".../v1", model="MiniMax-M2.1")

# 统一接口
response: LLMResponse = await client.generate(messages, tools)
# response.content     # 文本回复
# response.thinking     # extended thinking 内容
# response.tool_calls   # 工具调用列表
# response.usage        # token 使用统计
```

---

## 🚀 快速开始

### 1. 获取 API Key

| 版本 | 平台 | API Base |
|------|------|---------|
| **全球版** | [platform.minimax.io](https://platform.minimax.io) | `https://api.minimax.io` |
| **中国版** | [platform.minimaxi.com](https://platform.minimaxi.com) | `https://api.minimaxi.com` |

### 2. 安装（两种方式）

**🚀 快速开始（推荐新手）**
```bash
# 一键安装
uv tool install git+https://github.com/MiniMax-AI/Mini-Agent.git

# 初始化配置
curl -fsSL https://raw.githubusercontent.com/MiniMax-AI/Mini-Agent/main/scripts/setup-config.sh | bash

# 编辑配置
nano ~/.mini-agent/config/config.yaml
```

```yaml
api_key: "YOUR_API_KEY_HERE"
api_base: "https://api.minimax.io"   # 全球版
# api_base: "https://api.minimaxi.com"  # 中国版
model: "MiniMax-M2.1"
```

```bash
mini-agent                                    # 使用当前目录
mini-agent --workspace /path/to/project      # 指定工作目录
```

**🔧 开发模式（修改代码）**
```bash
git clone https://github.com/MiniMax-AI/Mini-Agent.git
cd Mini-Agent
uv sync
git submodule update --init --recursive
cp mini_agent/config/config-example.yaml mini_agent/config/config.yaml
# 编辑 config.yaml 填入 API Key
uv run python -m mini_agent.cli
# 或安装为可编辑模式
uv tool install -e .
mini-agent
```

---

## 🔧 核心工具集

### 文件操作工具

| 工具 | 功能 |
|------|------|
| `read_file` | 读取文件（支持 offset/limit 分块读取，tiktoken token 截断） |
| `write_file` | 写入文件（自动创建父目录） |
| `edit_file` | 精确字符串替换（old_str 唯一性校验） |

### Bash 工具

| 工具 | 功能 |
|------|------|
| `bash` | 执行 Shell 命令（workspace 目录下） |

### Session Note 工具（持久化记忆）

| 工具 | 功能 |
|------|------|
| `record_note` | 记录关键信息到 `~/.agent_memory.json`，支持分类标签 |
| `recall_notes` | 召回所有历史笔记，支持按分类过滤 |

### Skills 工具

Claude Skills 以 `SKILL.md` 为核心，动态加载到 Agent 工具集中：

```
SKILL.md 规范:
---
name: skill-name
description: 描述（触发条件）
---
# 指令内容
- 指南 1
- 指南 2
```

### MCP 工具

通过 `mcp.json` 配置 MCP Server，自动加载外部工具：

```json
{
  "mcpServers": {
    "knowledge-graph": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-knowledge-graph"]
    }
  }
}
```

---

## 📊 技术亮点

### 1. Extended Thinking 兼容

MiniMax M2.1 支持 Anthropic 风格的 `thinking` 块，Agent 正确解析并展示思考过程：

```python
# AnthropicClient._parse_response()
for block in response.content:
    if block.type == "thinking":
        thinking_content += block.thinking
    elif block.type == "text":
        text_content += block.text
    elif block.type == "tool_use":
        tool_calls.append(...)
```

### 2. Token 精确估算

使用 `tiktoken.get_encoding("cl100k_base")` 精确计算消息历史 token 数，支持：

- 字符串内容编码
- thinking 块编码
- tool_calls 块编码
- API 端报告的 token 数双重校验

### 3. 指数退避重试

```python
@async_retry(RetryConfig(max_retries=3, exponential_base=2.0))
async def _make_api_request(...):
    ...
# delay = 1.0 * 2^attempt，上限 60s
```

### 4. ACP 协议集成

支持 [Agent Communication Protocol](https://github.com/modelcontextprotocol/protocol)，可与 Zed Editor 等代码编辑器深度集成：

```bash
# Zed settings.json
{
  "agent_servers": {
    "mini-agent": {
      "command": "which mini-agent-acp"
    }
  }
}
```

---

## 📋 典型使用场景

### 任务执行（基础工具循环）

```
用户: 帮我创建一个漂亮的个人主页
Agent:
  🧠 Thinking: 用户需要创建一个网页，我需要先...
  🔧 Tool Call: read_file(path=".")
  🔧 Tool Call: write_file(path="index.html", content="<!DOCTYPE html>...")
  🔧 Tool Call: bash(command="open index.html")
  🤖 Assistant: 已为您创建 index.html 并在浏览器中打开
```

### Claude Skill 调用

```
用户: 用 PDF skill 生成一份项目报告
Agent:
  🔧 Tool Call: skill_loader(skill="pdf")
  🔧 Tool Call: write_file(path="report.pdf", content="...")
  🤖 Assistant: 报告已生成
```

### MCP 工具（Web 搜索）

```
用户: 帮我搜索最新的 AI 新闻
Agent:
  🔧 Tool Call: mcp_web_search(query="AI news 2024")
  🤖 Assistant: 以下是最新 AI 新闻摘要...
```

---

## 🛠️ 配置参考

```yaml
# mini_agent/config/config.yaml
api_key: "YOUR_API_KEY_HERE"
api_base: "https://api.minimax.io"
model: "MiniMax-M2.1"
max_steps: 100

retry:
  enabled: true
  max_retries: 3
  exponential_base: 2.0

tools:
  enable_file_tools: true
  enable_bash: true
  enable_note: true
  enable_skills: true
  enable_mcp: true
```

---

## 🙏 致谢

- **MiniMax** — M2.1 模型与 API 平台 [@GitHub](https://github.com/MiniMax-AI)
- **Anthropic** — Claude SDK 与 Skills 生态 [@anthropic](https://anthropic.com)
- **MCP** — Model Context Protocol [@GitHub](https://github.com/modelcontextprotocol)
- **Datawhale** — 学习社群推动 AI 实践

---

## 📝 License

MIT License

