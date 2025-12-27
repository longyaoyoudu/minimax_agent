"""
Mini Agent 最小化示例

这个示例展示了如何使用 mini_agent 框架创建一个最简单的 Agent。
避免复杂的配置，直接使用核心功能。
"""

import asyncio
from typing import Any

from mini_agent import LLMClient
from mini_agent.agent import Agent
from mini_agent.tools.base import Tool, ToolResult


# ============================================================================
# 1. 最简单的自定义工具
# ============================================================================

class SimpleCalculatorTool(Tool):
    """最简单的计算器工具"""
    
    @property
    def name(self) -> str:
        return "calculator"
    
    @property
    def description(self) -> str:
        return "执行加法计算。输入两个数字，返回它们的和。"
    
    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "第一个数字"
                },
                "b": {
                    "type": "number",
                    "description": "第二个数字"
                }
            },
            "required": ["a", "b"]
        }
    
    async def execute(self, a: float, b: float) -> ToolResult:
        """执行加法计算"""
        try:
            result = a + b
            return ToolResult(
                success=True,
                content=f"{a} + {b} = {result}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=f"计算错误: {str(e)}"
            )


class TimeTool(Tool):
    """时间工具"""
    
    @property
    def name(self) -> str:
        return "get_time"
    
    @property
    def description(self) -> str:
        return "获取当前时间。"
    
    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    async def execute(self) -> ToolResult:
        """获取当前时间"""
        from datetime import datetime
        
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return ToolResult(
                success=True,
                content=f"当前时间: {current_time}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                content="",
                error=f"获取时间错误: {str(e)}"
            )


# ============================================================================
# 2. 直接创建 Agent（不使用复杂配置）
# ============================================================================

async def create_simple_agent(api_key: str) -> Agent:
    """创建最简单的 Agent"""
    
    # 1. 创建 LLM 客户端（最简配置）
    llm_client = LLMClient(
        api_key=api_key,
        provider="anthropic",  # 使用 Anthropic 兼容模式
        api_base="https://api.minimaxi.com",  # 国内版
        model="MiniMax-M2.1"
    )
    
    # 2. 创建工具列表
    tools = [
        SimpleCalculatorTool(),
        TimeTool()
    ]
    
    # 3. 创建系统提示
    system_prompt = """你是一个简单的助手，具有计算和报时功能。

你可以：
1. 使用 calculator 工具进行加法计算
2. 使用 get_time 工具获取当前时间

请根据用户请求使用适当的工具。保持回答简洁明了。"""
    
    # 4. 创建并返回 Agent
    agent = Agent(
        llm_client=llm_client,
        system_prompt=system_prompt,
        tools=tools,
        max_steps=20,  # 限制最大步数
        workspace_dir="./demo_workspace"  # 工作空间目录
    )
    
    return agent


# ============================================================================
# 3. 运行示例对话
# ============================================================================

async def run_demo_conversation(agent: Agent):
    """运行演示对话"""
    
    print("\n" + "="*60)
    print("Mini Agent 演示对话")
    print("="*60)
    
    # 测试对话
    test_cases = [
        "你好！",
        "现在几点了？",
        "计算一下 15 加 27 等于多少",
        "123 加 456 等于多少？",
        "再告诉我一次时间"
    ]
    
    for user_message in test_cases:
        print(f"\n[用户] {user_message}")
        print("-" * 40)
        
        # 添加用户消息
        agent.add_user_message(user_message)
        
        # 运行 Agent
        print("[助手] 思考中...")
        response = await agent.run()
        
        if response:
            print(f"[助手] {response}")
        else:
            print("[助手] 没有回应")
    
    print("\n" + "="*60)
    print("演示完成！")
    print("="*60)


# ============================================================================
# 4. 交互式对话
# ============================================================================

async def run_interactive_demo(agent: Agent):
    """运行交互式对话"""
    
    print("\n" + "="*60)
    print("Mini Agent 交互式对话")
    print("="*60)
    
    print("\n欢迎使用 Mini Agent 演示！")
    print("你可以：")
    print("  1. 询问时间（例如：'现在几点了？'）")
    print("  2. 进行加法计算（例如：'计算 15+27'）")
    print("  3. 输入 /help 查看帮助")
    print("  4. 输入 /exit 退出")
    print("\n" + "-"*40)
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\n你: ").strip()
            
            if not user_input:
                continue
            
            # 处理命令
            if user_input.lower() == "/exit":
                print("再见！")
                break
            elif user_input.lower() == "/help":
                print("\n帮助信息：")
                print("  这是一个简单的 Agent 演示")
                print("  可用工具：")
                for tool in agent.tools.values():
                    print(f"    - {tool.name}: {tool.description}")
                print("  命令：")
                print("    /help - 显示帮助")
                print("    /exit - 退出")
                continue
            elif user_input.lower() == "/tools":
                print("\n可用工具：")
                for tool in agent.tools.values():
                    print(f"  - {tool.name}: {tool.description}")
                continue
            
            # 处理用户消息
            print("助手: 思考中...")
            agent.add_user_message(user_input)
            response = await agent.run()
            
            if response:
                print(f"助手: {response}")
            else:
                print("助手: 没有回应")
                
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"错误: {e}")


# ============================================================================
# 5. 主函数
# ============================================================================

def main():
    """主函数"""
    
    print("Mini Agent 最小化示例")
    print("="*60)
    
    # 获取 API Key
    api_key = input("请输入您的 MiniMax API Key: ").strip()
    
    if not api_key:
        print("错误: 必须提供 API Key")
        return
    
    # 创建 Agent
    print("\n创建 Agent...")
    try:
        agent = asyncio.run(create_simple_agent(api_key))
        print(f"Agent 创建成功！")
        print(f"可用工具: {[tool.name for tool in agent.tools.values()]}")
    except Exception as e:
        print(f"创建 Agent 失败: {e}")
        print("请检查 API Key 是否正确")
        return
    
    # 选择运行模式
    print("\n选择运行模式:")
    print("1. 运行演示对话")
    print("2. 运行交互式对话")
    
    choice = input("请输入选择 (1 或 2): ").strip()
    
    if choice == "1":
        asyncio.run(run_demo_conversation(agent))
    elif choice == "2":
        asyncio.run(run_interactive_demo(agent))
    else:
        print("无效选择，运行演示对话")
        asyncio.run(run_demo_conversation(agent))


if __name__ == "__main__":
    main()