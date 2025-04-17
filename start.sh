#!/bin/bash

# 设置默认环境变量
export LLM_API_KEY=${LLM_API_KEY:-"your_llm_api_key"}
export LLM_BASE_URL=${LLM_BASE_URL:-"your_llm_base_url"}
export LLM_MODEL_NAME=${LLM_MODEL_NAME:-"Qwen2.5-14B-Instruct"}

# MCP服务器配置
export MCP_FILESYSTEM_PATH=${MCP_FILESYSTEM_PATH:-"$HOME/Desktop"}
export MCP_FILESYSTEM_PATH2=${MCP_FILESYSTEM_PATH2:-"$HOME/Documents"}
export MCP_DOC_TOOL_URL=${MCP_DOC_TOOL_URL:-"http://192.168.10.31:8080/sse"}
export MCP_MEMORY_FILE_PATH=${MCP_MEMORY_FILE_PATH:-"$PWD/memory.json"}

echo "启动MCP Playground..."
echo "使用LLM模型: $LLM_MODEL_NAME"
echo "使用API端点: $LLM_BASE_URL"
echo "使用文件系统路径: $MCP_FILESYSTEM_PATH, $MCP_FILESYSTEM_PATH2"

# 运行应用
python app.py 