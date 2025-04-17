import os
import json

is_cn_env = os.getenv('MODELSCOPE_ENVIRONMENT') == 'studio'

# 从环境变量获取ModelScope API令牌
api_key = os.getenv('MODELSCOPE_API_KEY')

# 如果环境变量为空，请在这里设置您的ModelScope API令牌
if not api_key:
    api_key = "your_modelscope_token_here"  # 替换为从ModelScope获取的令牌

# 本地部署LLM的配置
llm_api_key = os.getenv('LLM_API_KEY', 'your_llm_api_key')
llm_base_url = os.getenv('LLM_BASE_URL', 'your_llm_base_url')
llm_model_name = os.getenv('LLM_MODEL_NAME', 'Qwen2.5-14B-Instruct')

# MCP服务器配置
mcp_filesystem_path = os.getenv('MCP_FILESYSTEM_PATH', os.path.expanduser('~/Desktop'))
mcp_filesystem_path2 = os.getenv('MCP_FILESYSTEM_PATH2', os.path.expanduser('~/Documents'))
mcp_doc_tool_url = os.getenv('MCP_DOC_TOOL_URL', 'http://192.168.10.31:8080/sse')
mcp_memory_file_path = os.getenv('MCP_MEMORY_FILE_PATH', os.path.join(os.getcwd(), 'memory.json'))

# 构建MCP配置
internal_mcp_config_obj = {
    "mcpServers": {
        "memory": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-memory"],
            "env": {"MEMORY_FILE_PATH": mcp_memory_file_path},
            "type": "stdio"
        },
        "yolo-tool": {
            "type": "sse",
            "url": mcp_doc_tool_url
        },
        "filesystem": {
            "command": "npx",
            "args": [
                "-y",
                "@modelcontextprotocol/server-filesystem",
                mcp_filesystem_path,
                mcp_filesystem_path2
            ],
            "type": "stdio"
        }
    }
}

internal_mcp_config = json.loads(
    os.getenv("INTERNAL_MCP_CONFIG", json.dumps(internal_mcp_config_obj)))
