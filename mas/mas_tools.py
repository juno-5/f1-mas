"""MAS Tool Definitions — Extensible tool registry for agentic execution.

Provides OpenAI function-calling tool definitions and execution functions.
MAS agent runner sends these as `tools` param, then executes tool_calls locally.

Tool categories:
- NAS: Node Agent System — remote PC exec, doc search
- Infra: Service status, health checks, log access
- (future) Commerce: Qoo10/Amazon/Shopee seller APIs
- (future) Analytics: GA4, internal dashboards
"""

import json
import re
import subprocess

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
# Infra Tool definitions — service status, health, logs
# --------------------------------------------------------------------------

_INFRA_SERVICES = ["f1crew-gateway", "mas", "xapi", "token-manager", "model-router", "nas", "f1crew-exporter"]
_HEALTH_ENDPOINTS = {"fas": "http://localhost:7700", "mas": "http://localhost:7720", "xapi": "http://localhost:7750"}

INFRA_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "infra_service_status",
            "description": "Check systemd service status (active/inactive, PID, uptime). If no service specified, checks all f1crew services.",
            "parameters": {
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "Service name (e.g. 'f1crew-gateway', 'mas', 'xapi'). Omit for all.",
                        "enum": _INFRA_SERVICES,
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "infra_health_check",
            "description": "Get JSON health status from FAS (7700), MAS (7720), or xapi (7750). Returns parsed health response.",
            "parameters": {
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "enum": ["fas", "mas", "xapi"],
                        "description": "Service to health-check",
                    },
                },
                "required": ["service"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "infra_fas_status",
            "description": "Get FAS token manager full status (available tokens, costs, mode, storm state, etc.)",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "infra_service_logs",
            "description": "Get recent systemd journal logs for a service. Can filter for errors only.",
            "parameters": {
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "Service name",
                        "enum": _INFRA_SERVICES,
                    },
                    "lines": {"type": "integer", "description": "Number of log lines (default 30)", "default": 30},
                    "errors_only": {"type": "boolean", "description": "Filter for errors/warnings only", "default": False},
                },
                "required": ["service"],
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
    """Execute a tool call and return result as string.

    Called by the MAS agent runner when LLM returns tool_calls.
    Handles NAS tools and Infra tools.
    """
    # --- Infra tools ---
    if name.startswith("infra_"):
        return _execute_infra_tool(name, arguments)

    # --- NAS tools ---
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


def _execute_infra_tool(name: str, arguments: dict) -> str:
    """Execute infrastructure management tools (local systemd + HTTP health)."""
    try:
        if name == "infra_service_status":
            service = arguments.get("service")
            services = [service] if service else _INFRA_SERVICES
            results = {}
            for svc in services:
                try:
                    active = subprocess.run(
                        ["systemctl", "--user", "is-active", svc],
                        capture_output=True, text=True, timeout=5,
                    )
                    show = subprocess.run(
                        ["systemctl", "--user", "show", svc,
                         "--property=ActiveEnterTimestamp,MainPID"],
                        capture_output=True, text=True, timeout=5,
                    )
                    results[svc] = {
                        "status": active.stdout.strip(),
                        "details": show.stdout.strip(),
                    }
                except Exception as e:
                    results[svc] = {"status": "error", "error": str(e)}
            return json.dumps(results)

        elif name == "infra_health_check":
            service = arguments.get("service", "")
            url = _HEALTH_ENDPOINTS.get(service)
            if not url:
                return json.dumps({"error": f"Unknown service: {service}"})
            resp = httpx.get(f"{url}/health", timeout=5.0)
            return resp.text

        elif name == "infra_fas_status":
            resp = httpx.get("http://localhost:7700/status", timeout=5.0)
            return resp.text

        elif name == "infra_service_logs":
            service = arguments.get("service", "f1crew-gateway")
            lines = min(arguments.get("lines", 30), 200)
            errors_only = arguments.get("errors_only", False)

            if service not in _INFRA_SERVICES:
                return json.dumps({"error": f"Unknown service: {service}"})

            cmd = ["journalctl", "--user", "-u", service, "--no-pager", "-n", str(lines)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            output = result.stdout

            if errors_only:
                output = "\n".join(
                    line for line in output.split("\n")
                    if any(kw in line.lower() for kw in ("error", "fail", "crash", "err", "warn"))
                )

            return output or "(no matching logs)"

        else:
            return json.dumps({"error": f"Unknown infra tool: {name}"})

    except httpx.TimeoutException:
        return json.dumps({"error": f"Timeout calling {name}"})
    except subprocess.TimeoutExpired:
        return json.dumps({"error": f"Command timeout for {name}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


# --------------------------------------------------------------------------
# Tool relevance detection
# --------------------------------------------------------------------------

_NAS_RELEVANT_RE = re.compile(
    r"노드.{0,4}(?:목록|상태|확인|조회|리스트)|(?:NAS|원격).{0,4}노드|\bNAS\b|"
    r"\bnode.{0,4}(?:list|status|check)\b|"
    r"클라우드.{0,4}(?:노드|인스턴스)|\bcloud.{0,4}(?:node|instance)\b|"
    r"\bPC\b.{0,4}(?:접속|연결|원격|실행|상태|확인)|"
    r"원격.{0,4}(?:접속|실행|명령)|\bremote.{0,4}(?:exec|connect)\b|"
    r"(?:명령|코드|스크립트|원격).{0,4}실행|실행해|\bexec\b|"
    r"문서.*검색|\bdoc.*search\b|\bnas_|nas 노드",
    re.IGNORECASE,
)

_INFRA_RELEVANT_RE = re.compile(
    r"서버.{0,4}(?:상태|확인|장애|재시작|다운|점검|접속|로그|에러)|"
    r"\bserver.{0,4}(?:status|down|restart|error|log|check)\b|"
    r"서비스.{0,4}(?:상태|확인|장애|재시작|로그|에러)|"
    r"\bservice.{0,4}(?:status|down|restart|health|error)\b|"
    r"(?:서비스|서버|시스템).{0,4}헬스.?체크|헬스.?체크.{0,4}(?:확인|결과|해줘|실행)|"
    r"\b(?:service|server).{0,4}health.?check\b|"
    r"인프라|\binfra\b|"
    r"(?:API\s*)?게이트웨이.{0,4}(?:상태|에러|로그|재시작|장애)|"
    r"토큰.{0,4}(?:관리|풀|사용량|만료|소진|갱신)|\btoken.{0,4}(?:pool|manager|usage)\b|"
    r"\bFAS\b|\bMAS\b|\bxapi\b|"
    r"(?:서비스|서버|시스템).{0,4}로그|로그.{0,4}(?:확인|분석|조회)|"
    r"\b(?:service|server|system).{0,4}log\b|"
    r"에러.{0,4}(?:로그|원인|분석|추적|확인)|(?:서버|서비스|시스템).{0,4}에러|"
    r"\berror.{0,4}(?:log|trace|cause|debug)\b|"
    r"(?:시스템|서버|서비스).{0,4}모니터링|모니터링.{0,4}(?:대시보드|설정|알림)|"
    r"(?:코드|서버|서비스).{0,4}배포|배포해|\bdeploy\b",
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

    # NAS tools: node/PC/remote related queries
    if _NAS_RELEVANT_RE.search(query):
        tools.extend(NAS_TOOLS)

    # Infra tools: service status, health, logs, deployment
    if _INFRA_RELEVANT_RE.search(query):
        tools.extend(INFRA_TOOLS)

    # Future: commerce tools
    # if _COMMERCE_RELEVANT_RE.search(query):
    #     tools.extend(COMMERCE_TOOLS)

    return tools
