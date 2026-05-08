<div align="center">

# Quiz Generator Ai MCP

**MCP server for quiz generator ai mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-quiz-generator-ai-mcp)](https://pypi.org/project/meok-quiz-generator-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Quiz Generator Ai MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `generate_quiz` | Generate a quiz from provided content text. |
| `validate_answers` | Validate submitted answers against correct answers and return scoring. |
| `generate_flashcards` | Generate flashcards (front/back pairs) from content for study purposes. |
| `assess_difficulty` | Assess the difficulty level of content for quiz/study purposes. |

## Installation

```bash
pip install meok-quiz-generator-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "quiz-generator-ai": {
      "command": "python",
      "args": ["-m", "meok_quiz_generator_ai_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 4 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
