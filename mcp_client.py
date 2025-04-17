from typing import List, Callable
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.language_models import BaseChatModel
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
import json
import os
import re


def parse_mcp_config(mcp_config: dict, enabled_mcp_servers: list = None):
    mcp_servers = {}
    for server_name, server in mcp_config.get("mcpServers", {}).items():
        if enabled_mcp_servers is not None and server_name not in enabled_mcp_servers:
            continue
            
        server_type = server.get("type", "sse")
        
        if server_type == "stdio":
            continue
            
        new_server = {**server}
        
        if "type" in new_server:
            new_server["transport"] = new_server["type"]
            del new_server["type"]
        else:
            new_server["transport"] = "sse"
            
        if server.get("env"):
            env = {'PYTHONUNBUFFERED': '1', 'PATH': os.environ.get('PATH', '')}
            env.update(server["env"])
            new_server["env"] = env
        mcp_servers[server_name] = new_server
    return mcp_servers


async def get_mcp_prompts(mcp_config: dict, get_llm: Callable):
    try:
        mcp_servers = parse_mcp_config(mcp_config)
        if len(mcp_servers.keys()) == 0:
            return {}
        llm: BaseChatModel = get_llm()
        async with MultiServerMCPClient(mcp_servers) as client:
            mcp_tool_descriptions = {}
            for mcp_name, server_tools in client.server_name_to_tools.items():
                mcp_tool_descriptions[mcp_name] = {}
                for tool in server_tools:
                    mcp_tool_descriptions[mcp_name][
                        tool.name] = tool.description
            prompt = f"""Based on the tool descriptions of the following MCP services `{json.dumps(mcp_tool_descriptions)}`, generate 2-4 example user queries for each service:

        Please provide 2-4 natural and specific example queries in Chinese that effectively demonstrate the capabilities of each service.
        The response must be in strict JSON format as shown below:
        ```json
        {{
            "mcp_name1": ["中文示例1", "中文示例2"],
            "mcp_name2": ["中文示例1", "中文示例2"]
        }}
        ```
        Return only the JSON object without any additional explanation or text.
        """
            response = await llm.ainvoke(prompt)
            if hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_content = json_match.group(0)
            else:
                json_content = content
            raw_examples = json.loads(json_content)

            for mcp_name in mcp_tool_descriptions.keys():
                if mcp_name not in raw_examples:
                    raw_examples[mcp_name] = [
                        f"请使用 {mcp_name} 服务的功能帮我查询信息或解决问题",
                    ]
            return raw_examples
    except Exception as e:
        return {
            mcp_name: [
                f"请使用 {mcp_name} 服务的功能帮我查询信息或解决问题",
            ]
            for mcp_name in mcp_servers.keys()
        }


def convert_mcp_name(tool_name: str, mcp_names: dict):
    if not tool_name:
        return tool_name
    separators = tool_name.split("__TOOL__")
    if len(separators) >= 2:
        mcp_name_idx, mcp_tool_name = separators[:2]
    else:
        mcp_name_idx = separators[0]
        mcp_tool_name = None
    mcp_name = mcp_names.get(mcp_name_idx)
    if not mcp_tool_name:
        return mcp_name or mcp_name_idx

    if not mcp_name:
        return mcp_tool_name
    return f"[{mcp_name}] {mcp_tool_name}"


async def generate_with_mcp(messages: List[dict], mcp_config: dict,
                            enabled_mcp_servers: list, sys_prompt: str,
                            get_llm: Callable):
    mcp_servers = parse_mcp_config(mcp_config, enabled_mcp_servers)
    async with MultiServerMCPClient(mcp_servers) as client:
        tools = []
        mcp_tools = []
        mcp_names = {}
        for i, server_name_to_tool in enumerate(
                client.server_name_to_tools.items()):
            mcp_name, server_tools = server_name_to_tool
            mcp_names[str(i)] = mcp_name
            for tool in server_tools:
                new_tool = tool.model_copy()
                # tool match ^[a-zA-Z0-9_-]+$
                new_tool.name = f"{i}__TOOL__{tool.name}"
                mcp_tools.append(new_tool)
        tools.extend(mcp_tools)
        llm: BaseChatModel = get_llm()
        prompt = ChatPromptTemplate.from_messages([
            ("system", sys_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ])

        langchain_messages = []
        for msg in messages:
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))

        agent_executor = create_react_agent(llm, tools, prompt=prompt)
        use_tool = False
        async for step in agent_executor.astream(
            {"messages": langchain_messages},
                config={"recursion_limit": 50},
                stream_mode=["values", "messages"],
        ):
            if isinstance(step, tuple):
                if step[0] == "messages":
                    message_chunk = step[1][0]
                    if hasattr(message_chunk, "content"):
                        if isinstance(message_chunk, ToolMessage):
                            use_tool = False
                            yield {
                                "type":
                                "tool",
                                "name":
                                convert_mcp_name(message_chunk.name,
                                                 mcp_names),
                                "content":
                                message_chunk.content
                            }
                        elif hasattr(message_chunk,
                                     'tool_call_chunks') and len(
                                         message_chunk.tool_call_chunks) > 0:
                            for tool_call_chunk in message_chunk.tool_call_chunks:
                                yield {
                                    "type":
                                    "tool_call_chunks",
                                    "name":
                                    convert_mcp_name(tool_call_chunk["name"],
                                                     mcp_names),
                                    "content":
                                    tool_call_chunk["args"],
                                    "next_tool":
                                    bool(use_tool and tool_call_chunk["name"])
                                }
                                if tool_call_chunk["name"]:
                                    use_tool = True
                        elif message_chunk.content:
                            yield {
                                "type": "content",
                                "content": message_chunk.content
                            }
