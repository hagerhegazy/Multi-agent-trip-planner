import sys
from pathlib import Path

from langchain_mcp_adapters.client import MultiServerMCPClient

MCP_DIR = Path(__file__).parent / "MCP"


async def load_excel_tools():
    client = MultiServerMCPClient({
        "excel_server": {
            "command": sys.executable,
            "args": [str(MCP_DIR / "task_server.py")],
            "transport": "stdio",
        }
    })
    return await client.get_tools()