"""
Mini Agent 框架简单示例

这个示例展示了如何使用 mini_agent 框架创建一个简单的自定义 Agent。
包含自定义工具、配置和运行示例。
"""

import asyncio
from pathlib import Path
from typing import Any

from mini_agent import LLMClient
from mini_agent.agent import Agent
from mini_agent.config import Config
from mini_agent.tools.base import Tool, ToolResult


# ============================================================================
# 1. 创建自定义工具
# ============================================================================

class CalculatorTool(Tool):
    """简单的计算器工具，支持加减乘除"""
    
    @property
    def name(self) -> str:
        return "calculator"
    
    @property
    def description(self) -> str:
        return "执行简单的数学计算。支持加法、减法、乘法、除法。"
    
    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "计算操作：add(加法), subtract(减法), multiply(乘法), divide(除法)"
                },
                "a": {
                    "type": "number",
                    "description": "第一个数字"
                },
                "b": {
                    "type": "number", 
                    "description": "第二个数字"
                }
            },
            "required": ["operation", "a", "b"]
        }
    
    async def execute(self, operation: str, a: float, b: float) -> ToolResult:
        """执行计算"""
        try:
            if operation == "add":
                result = a + b
                operation_name = "加法"
            elif operation == "subtract":
                result = a - b
                operation_name = "减法"
            elif operation == "multiply":
                result = a * b
                operation_name = "乘法"
            elif operation == "divide":
                if b == 0:
                    return ToolResult(
                        success=False,
                        content="",
                        error="除数不能为零"
                    )
                result = a / b
                operation_name = "除法"
            else:
                return ToolResult(
                    success=False,
                    content="",
                    error=f"不支持的操作: {operation}"
                )
            
            return ToolResult(
                success=True,
                content=f"{operation_name}结果: {a} {self._get_operator(operation)} {b} = {result}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=f"计算错误: {str(e)}"
            )
    
    def _get_operator(self, operation: str) -> str:
        """获取操作符符号"""
        operators = {
            "add": "+",
            "subtract": "-", 
            "multiply": "×",
            "divide": "÷"
        }
        return operators.get(operation, "?")


class GreetingTool(Tool):
    """问候工具，根据时间生成问候语"""
    
    @property
    def name(self) -> str:
        return "greeting"
    
    @property
    def description(self) -> str:
        return "根据当前时间生成适当的问候语。"
    
    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "问候的对象名称"
                },
                "language": {
                    "type": "string",
                    "enum": ["zh", "en"],
                    "description": "语言：zh(中文), en(英文)"
                }
            },
            "required": ["name", "language"]
        }
    
    async def execute(self, name: str, language: str = "zh") -> ToolResult:
        """生成问候语"""
        from datetime import datetime
        
        try:
            hour = datetime.now().hour
            
            if language == "zh":
                if 5 <= hour < 12:
                    greeting = "早上好"
                elif 12 <= hour < 14:
                    greeting = "中午好" 
                elif 14 <= hour < 18:
                    greeting = "下午好"
                elif 18 <= hour < 22:
                    greeting = "晚上好"
                else:
                    greeting = "夜深了"
                message = f"{greeting}，{name}！现在是{datetime.now().strftime('%H:%M')}。"
            else:  # english
                if 5 <= hour < 12:
                    greeting = "Good morning"
                elif 12 <= hour < 18:
                    greeting = "Good afternoon"
                else:
                    greeting = "Good evening"
                message = f"{greeting}, {name}! It's {datetime.now().strftime('%H:%M')} now."
            
            return ToolResult(
                success=True,
                content=message
            )
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=f"生成问候语错误: {str(e)}"
            )


# ============================================================================
# 2. 创建简单配置
# ============================================================================

def create_simple_config(api_key: str, api_base: str = "https://api.minimaxi.com") -> Config:
    """创建简单配置"""
    
    config_dict = {
        "api_key": api_key,
        "api_base": api_base,
        "model": "MiniMax-M2.1",
        "provider": "anthropic",
        "retry": {
            "enabled": True,
            "max_retries": 3,
            "initial_delay": 1.0,
            "max_delay": 60.0,
            "exponential_base": 2.0
        },
        "max_steps": 50,
        "workspace_dir": "./workspace",
        "system_prompt_path": "system_prompt.md",
        "tools": {
            "enable_file_tools": False,  # 禁用文件工具，简化示例
            "enable_bash": False,        # 禁用 Bash 工具
            "enable_note": True,         # 启用会话笔记
            "enable_skills": False,      # 禁用 Claude Skills
            "enable_mcp": False,         # 禁用 MCP 工具
            "skills_dir": "./skills",
            "mcp_config_path": "mcp.json"
        }
    }
    
    return Config.from_dict(config_dict)


# ============================================================================
# 3. 创建并运行简单 Agent
# ============================================================================

async def run_simple_agent_example(api_key: str):
    """运行简单 Agent 示例"""
    
    print("=" * 60)
    print("Mini Agent 简单示例")
    print("=" * 60)
    
    # 1. 创建配置
    print("\n1. 创建配置...")
    config = create_simple_config(api_key)
    
    # 2. 创建 LLM 客户端
    print("2. 创建 LLM 客户端...")
    llm_client = LLMClient(
        api_key=config.llm.api_key,
        provider="anthropic",
        api_base=config.llm.api_base,
        model=config.llm.model
    )
    
    # 3. 创建自定义工具
    print("3. 创建自定义工具...")
    tools = [
        CalculatorTool(),
        GreetingTool()
    ]
    
    # 4. 创建系统提示
    system_prompt = """你是一个友好的助手，具有计算和问候功能。

可用工具：
1. calculator - 执行数学计算（加减乘除）
2. greeting - 根据时间生成问候语

请根据用户请求使用适当的工具。如果用户需要计算，使用 calculator 工具。
如果用户需要问候，使用 greeting 工具。

保持友好和 helpful 的态度。"""
    
    # 5. 创建 Agent
    print("4. 创建 Agent...")
    agent = Agent(
        llm_client=llm_client,
        system_prompt=system_prompt,
        tools=tools,
        max_steps=config.agent.max_steps,
        workspace_dir=config.agent.workspace_dir
    )
    
    # 6. 创建测试对话
    print("5. 运行测试对话...")
    print("\n" + "-" * 40)
    
    test_messages = [
        "你好，请向小明问好",
        "计算一下 25 乘以 13 等于多少",
        "用英文向 Alice 问好",
        "123 除以 4 等于多少"
    ]
    
    for message in test_messages:
        print(f"\n用户: {message}")
        print("-" * 30)
        
        agent.add_user_message(message)
        result = await agent.run()
        
        if result:
            print(f"助手: {result}")
    
    print("\n" + "=" * 60)
    print("示例完成！")
    print("=" * 60)


async def run_interactive_agent(api_key: str):
    """运行交互式 Agent"""
    
    print("=" * 60)
    print("Mini Agent 交互式示例")
    print("=" * 60)
    
    # 1. 创建配置
    config = create_simple_config(api_key)
    
    # 2. 创建 LLM 客户端
    llm_client = LLMClient(
        api_key=config.llm.api_key,
        provider="anthropic",
        api_base=config.llm.api_base,
        model=config.llm.model
    )
    
    # 3. 创建工具
    tools = [
        CalculatorTool(),
        GreetingTool()
    ]
    
    # 4. 创建系统提示
    system_prompt = """你是一个友好的助手，具有计算和问候功能。

你可以：
1. 使用 calculator 工具进行数学计算
2. 使用 greeting 工具生成问候语

请根据用户请求使用适当的工具。"""
    
    # 5. 创建 Agent
    agent = Agent(
        llm_client=llm_client,
        system_prompt=system_prompt,
        tools=tools,
        max_steps=config.agent.max_steps,
        workspace_dir=config.agent.workspace_dir
    )
    
    print("\nAgent 已启动！")
    print("可用命令：")
    print("  /help    - 显示帮助")
    print("  /clear   - 清除对话历史")
    print("  /exit    - 退出")
    print("  /tools   - 显示可用工具")
    print("\n你可以尝试：")
    print("  - 向某人问好")
    print("  - 进行数学计算")
    print("  - 询问时间")
    print("\n" + "-" * 40)
    
    while True:
        try:
            user_input = input("\n你: ").strip()
            
            if not user_input:
                continue
            
            # 处理命令
            if user_input.lower() == "/exit":
                print("再见！")
                break
            elif user_input.lower() == "/help":
                print("\n帮助信息：")
                print("  这是一个简单的 Agent 示例，具有计算和问候功能")
                print("  你可以：")
                print("    - 说 '向小明问好'")
                print("    - 说 '计算 15 + 27'")
                print("    - 说 '用英文向 Alice 问好'")
                print("    - 使用 /tools 查看可用工具")
                continue
            elif user_input.lower() == "/tools":
                print("\n可用工具：")
                for tool in tools:
                    print(f"  - {tool.name}: {tool.description}")
                continue
            elif user_input.lower() == "/clear":
                agent.messages = [agent.messages[0]]  # 只保留系统提示
                print("对话历史已清除")
                continue
            
            # 处理用户输入
            print("助手: 思考中...")
            agent.add_user_message(user_input)
            result = await agent.run()
            
            if result:
                print(f"助手: {result}")
            else:
                print("助手: 没有回应")
                
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"错误: {e}")


# ============================================================================
# 4. 主函数
# ============================================================================

def main():
    """主函数"""
    
    print("Mini Agent 框架简单示例")
    print("=" * 60)
    
    # 检查 API Key
    api_key = input("请输入您的 MiniMax API Key (留空使用配置文件): ").strip()
    
    if not api_key:
        # 尝试从配置文件读取
        config_path = Path("mini_agent/config/config.yaml")
        if config_path.exists():
            try:
                config = Config.from_yaml(config_path)
                api_key = config.llm.api_key
                print(f"使用配置文件中的 API Key")
            except:
                print("错误: 无法读取配置文件")
                return
        else:
            print("错误: 未提供 API Key 且配置文件不存在")
            return
    
    # 选择运行模式
    print("\n选择运行模式:")
    print("1. 运行测试示例")
    print("2. 运行交互式对话")
    
    choice = input("请输入选择 (1 或 2): ").strip()
    
    if choice == "1":
        asyncio.run(run_simple_agent_example(api_key))
    elif choice == "2":
        asyncio.run(run_interactive_agent(api_key))
    else:
        print("无效选择")


if __name__ == "__main__":
    main()