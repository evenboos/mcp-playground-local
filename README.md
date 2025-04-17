---
# 详细文档见https://modelscope.cn/docs/%E5%88%9B%E7%A9%BA%E9%97%B4%E5%8D%A1%E7%89%87
domain: #领域：cv/nlp/audio/multi-modal/AutoML
# - cv
tags: #自定义标签
  -
datasets: #关联数据集
  evaluation:
  #- iic/ICDAR13_HCTR_Dataset
  test:
  #- iic/MTWI
  train:
  #- iic/SIBR
models: #关联模型
#- iic/ofa_ocr-recognition_general_base_zh

## 启动文件(若SDK为Gradio/Streamlit，默认为app.py, 若为Static HTML, 默认为index.html)
# deployspec:
#   entry_file: app.py
license: Apache License 2.0
---

# MCP Playground for localhost(mcp client、 mcp server and local llm)

MCP Playground是一个实验性项目，用于测试和展示MCP（Model Context Protocol）工具的能力。
Original Link: https://www.modelscope.cn/studios/Coloring/mcp-playground.git

## 功能特点

- 集成本地部署的基于sse的MCP工具
- 支持本地部署的LLM模型
- 用户友好的界面，便于交互和测试

## 配置说明

### 环境变量

可以通过以下环境变量设置应用程序：

```bash
# LLM配置
export LLM_API_KEY="your_llm_api_key"
export LLM_BASE_URL="your_llm_api_base_url"
export LLM_MODEL_NAME="your_model_name"

# MCP服务器配置
export MCP_FILESYSTEM_PATH="path_to_filesystem_directory"
export MCP_FILESYSTEM_PATH2="path_to_another_filesystem_directory"
export MCP_DOC_TOOL_URL="url_to_doc_tool_service"
export MCP_MEMORY_FILE_PATH="path_to_memory_file"
```

## 安装与运行

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 运行应用：

```bash
python app.py
```

## 使用方法

1. 在UI界面中选择"Qwen2.5-14B-Instruct (本地)"模型选项以使用本地部署的LLM
2. 点击输入框左侧的工具图标来选择要使用的MCP工具
3. 根据示例提示进行交互，例如：
   - YOLO-Tool工具: "检测这张图片中有哪些物体"

## MCP工具说明

### YOLO-Tool工具

用于对图像进行分析，包括对象检测、分割和姿态估计等。

