"""MAS Tool Definitions — Extensible tool registry for agentic execution.

Provides OpenAI function-calling tool definitions and execution functions.
MAS agent runner sends these as `tools` param, then executes tool_calls locally.

Tool categories:
- NAS: Node Agent System — remote PC exec, doc search
- (future) Commerce: Qoo10/Amazon/Shopee seller APIs
- (future) Analytics: GA4, internal dashboards
"""

import json
import re

import httpx

from . import mas_config as cfg

# --------------------------------------------------------------------------
# NAS Tool definitions (OpenAI function-calling format)
# --------------------------------------------------------------------------

NAS_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "nas_list_nodes",
            "description": "List available compute nodes with their status, OS, IP, CPU and memory usage",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "nas_exec",
            "description": "Execute a shell command on a remote node PC. Returns stdout, stderr, and exit code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "node_id": {"type": "string", "description": "Target node ID (e.g. 'ojunhoui-MacBookPro.local')"},
                    "command": {"type": "string", "description": "Shell command to execute"},
                    "timeout": {"type": "integer", "description": "Timeout in seconds (default 30)", "default": 30},
                },
                "required": ["node_id", "command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "nas_search_docs",
            "description": "Search indexed company documents by keyword. Returns matching docs with previews.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search keyword"},
                    "limit": {"type": "integer", "description": "Max results (default 5)", "default": 5},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "nas_read_doc",
            "description": "Read full content of a document by its ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc_id": {"type": "string", "description": "Document ID (e.g. 'doc-0042')"},
                },
                "required": ["doc_id"],
            },
        },
    },
]

# --------------------------------------------------------------------------
# Worker Local Tools — sent to worker nodes for local execution
# --------------------------------------------------------------------------

WORKER_LOCAL_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "bash_exec",
            "description": "Execute a shell command on this node PC. Returns stdout, stderr, exit code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to execute"},
                    "timeout": {"type": "integer", "description": "Timeout in seconds (default 30)", "default": 30},
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "file_read",
            "description": "Read file contents from this node PC",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to read"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "file_write",
            "description": "Write content to a file on this node PC",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to write"},
                    "content": {"type": "string", "description": "Content to write"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "file_list",
            "description": "List files in a directory on this node PC",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "Directory path", "default": "."},
                    "pattern": {"type": "string", "description": "Glob pattern (default '*')", "default": "*"},
                },
            },
        },
    },
]

# Blocked commands for safety
_BLOCKED_COMMANDS = ["rm -rf", "mkfs", "dd if=", "shutdown", "reboot", "kill -9 1"]


def _get_nas_url() -> str:
    return cfg.get("nas_url", "http://localhost:7730")


def execute_tool(name: str, arguments: dict) -> str:
    """Execute a NAS tool call and return result as string.

    Called by the MAS agent runner when LLM returns tool_calls.
    """
    nas_url = _get_nas_url()
    timeout = cfg.get("nas_timeout", 5.0)

    try:
        if name == "nas_list_nodes":
            resp = httpx.get(f"{nas_url}/nodes", timeout=timeout)
            return resp.text

        elif name == "nas_exec":
            node_id = arguments.get("node_id", "")
            command = arguments.get("command", "")
            exec_timeout = arguments.get("timeout", 30)

            # Safety check
            for blocked in _BLOCKED_COMMANDS:
                if blocked in command:
                    return json.dumps({"error": f"Blocked command pattern: {blocked}"})

            resp = httpx.post(
                f"{nas_url}/nodes/{node_id}/exec",
                json={"command": command, "timeout": exec_timeout},
                timeout=exec_timeout + 10,
            )
            return resp.text

        elif name == "nas_search_docs":
            query = arguments.get("query", "")
            limit = arguments.get("limit", 5)
            resp = httpx.get(
                f"{nas_url}/docs/search",
                params={"q": query, "limit": limit},
                timeout=timeout,
            )
            return resp.text

        elif name == "nas_read_doc":
            doc_id = arguments.get("doc_id", "")
            resp = httpx.get(f"{nas_url}/docs/{doc_id}", timeout=timeout)
            return resp.text

        else:
            return json.dumps({"error": f"Unknown tool: {name}"})

    except httpx.TimeoutException:
        return json.dumps({"error": f"Timeout calling {name}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


# --------------------------------------------------------------------------
# Tool relevance detection
# --------------------------------------------------------------------------

_NAS_RELEVANT_RE = re.compile(
    r"노드|node|서버|server|배포|deploy|인프라|infra|클라우드|cloud|PC|"
    r"원격|remote|실행|exec|파일|file|문서.*검색|doc.*search|NAS",
    re.IGNORECASE,
)

# Future: commerce, analytics, etc.
# _COMMERCE_RELEVANT_RE = re.compile(
#     r"매출|성과|판매|commerce|sales|revenue|큐텐|qoo10|아마존|amazon|쇼피|shopee",
#     re.IGNORECASE,
# )


def get_tools_for_query(query: str, domain: str = "") -> list[dict]:
    """Return relevant tool definitions based on query content.

    Returns empty list if no tools are relevant (agent runs without tools).
    Only provides tools when query keywords explicitly match — avoids over-injection.
    """
    if not cfg.get("agent_tools_enabled", True):
        return []

    tools = []

    # NAS tools: infra/node/server related queries
    if _NAS_RELEVANT_RE.search(query):
        tools.extend(NAS_TOOLS)

    # Future: commerce tools
    # if _COMMERCE_RELEVANT_RE.search(query):
    #     tools.extend(COMMERCE_TOOLS)

    return tools
