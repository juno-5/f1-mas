"""MAS Slack Dashboard — Socket Mode + Block Kit thread-per-request."""

import threading
import time

from . import mas_config as cfg
from . import mas_state as state

_app = None
_handler = None
_thread_map: dict[str, str] = {}  # request_id → thread_ts
_thread_lock = threading.Lock()

STATUS_EMOJI = {
    "pending": ":hourglass_flowing_sand:",
    "analyzing": ":mag:",
    "assembling": ":busts_in_silhouette:",
    "running": ":gear:",
    "synthesizing": ":crystal_ball:",
    "completed": ":white_check_mark:",
    "failed": ":x:",
    "blocked": ":no_entry:",
}

AGENT_STATUS_EMOJI = {
    "pending": ":white_circle:",
    "running": ":large_blue_circle:",
    "completed": ":green_circle:",
    "failed": ":red_circle:",
}


def _get_channel():
    return cfg.get_nested("slack", "channel_id", "")


def _init_app():
    """Initialize slack_bolt App with Socket Mode."""
    global _app, _handler
    if _app is not None:
        return

    try:
        from slack_bolt import App
        from slack_bolt.adapter.socket_mode import SocketModeHandler
    except ImportError:
        print("[mas-slack] slack_bolt not installed, Slack disabled", flush=True)
        return

    bot_token = cfg.get_nested("slack", "bot_token", "")
    app_token = cfg.get_nested("slack", "app_token", "")

    if not bot_token or not app_token:
        print("[mas-slack] Missing bot_token or app_token", flush=True)
        return

    _app = App(token=bot_token)
    _handler = SocketModeHandler(_app, app_token)

    # Register event listeners
    @_app.event("app_mention")
    def handle_mention(event, say):
        say(
            text=f"{STATUS_EMOJI['pending']} MAS is an internal orchestrator. "
                 f"Use the /request API endpoint to submit tasks.",
            thread_ts=event.get("ts"),
        )

    @_app.action("view_full_output")
    def handle_full_output(ack, body, client):
        ack()
        # Extract agent info from action value
        action_value = body.get("actions", [{}])[0].get("value", "")
        parts = action_value.split(":")
        if len(parts) == 2:
            request_id, agent_idx = parts[0], int(parts[1])
            req = state.get_request(request_id)
            if req and agent_idx < len(req.agents):
                agent = req.agents[agent_idx]
                output = agent.output or "(no output)"
                # Truncate for Slack modal (3000 char limit)
                if len(output) > 2900:
                    output = output[:2900] + "\n\n[... truncated ...]"
                client.views_open(
                    trigger_id=body["trigger_id"],
                    view={
                        "type": "modal",
                        "title": {"type": "plain_text", "text": f"{agent.callsign} Output"},
                        "blocks": [
                            {
                                "type": "section",
                                "text": {"type": "mrkdwn", "text": output},
                            }
                        ],
                    },
                )


def start_slack():
    """Start Slack Socket Mode in a daemon thread."""
    _init_app()
    if _handler is None:
        return

    def _run():
        try:
            _handler.start()
        except Exception as e:
            print(f"[mas-slack] Handler error: {e}", flush=True)

    t = threading.Thread(target=_run, daemon=True)
    t.start()


def _post_message(channel: str, text: str, blocks: list = None, thread_ts: str = None) -> str | None:
    """Post a message and return its ts."""
    if _app is None:
        return None
    try:
        result = _app.client.chat_postMessage(
            channel=channel,
            text=text,
            blocks=blocks,
            thread_ts=thread_ts,
        )
        return result.get("ts")
    except Exception as e:
        print(f"[mas-slack] Post error: {e}", flush=True)
        return None


def _update_message(channel: str, ts: str, text: str, blocks: list = None):
    """Update an existing message."""
    if _app is None:
        return
    try:
        _app.client.chat_update(
            channel=channel, ts=ts, text=text, blocks=blocks,
        )
    except Exception as e:
        print(f"[mas-slack] Update error: {e}", flush=True)


# ── Public notification API ──

def notify_assembly(request_id: str, query: str, personas, analysis: dict):
    """Post parent message + team assembly reply."""
    channel = _get_channel()
    if not channel or _app is None:
        return

    # Parent message: request summary
    parent_blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"{STATUS_EMOJI['pending']} MAS Request"},
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Request:* `{request_id}`\n*Query:* {query[:200]}",
            },
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Domain: `{analysis.get('domains', ['?'])[0]}` | "
                            f"Locale: `{analysis.get('locale', '?')}` | "
                            f"Complexity: `{analysis.get('complexity', '?')}`",
                }
            ],
        },
    ]

    parent_ts = _post_message(channel, f"MAS Request {request_id}", blocks=parent_blocks)
    if parent_ts:
        with _thread_lock:
            _thread_map[request_id] = parent_ts

    # Team assembly reply
    team_lines = []
    for p in personas:
        team_lines.append(f"• *{p.callsign}* ({p.role}) — `{p.id}`")

    assembly_blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f":busts_in_silhouette: *Team Assembly*\n" + "\n".join(team_lines),
            },
        },
    ]

    _post_message(channel, "Team Assembly", blocks=assembly_blocks, thread_ts=parent_ts)


def notify_agent_progress(request_id: str, callsign: str, status: str):
    """Post agent progress update as thread reply."""
    channel = _get_channel()
    if not channel or _app is None:
        return

    with _thread_lock:
        thread_ts = _thread_map.get(request_id)
    if not thread_ts:
        return

    emoji = AGENT_STATUS_EMOJI.get(status, ":white_circle:")
    text = f"{emoji} *{callsign}*: {status}"

    if status == "completed":
        req = state.get_request(request_id)
        if req:
            for i, agent in enumerate(req.agents):
                if agent.callsign == callsign and agent.output:
                    # Show summary + "Full Output" button
                    summary = agent.output[:300]
                    if len(agent.output) > 300:
                        summary += "..."

                    blocks = [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"{emoji} *{callsign}* completed ({agent.duration_ms}ms)\n"
                                        f"```{summary}```",
                            },
                        },
                        {
                            "type": "actions",
                            "elements": [
                                {
                                    "type": "button",
                                    "text": {"type": "plain_text", "text": "Full Output"},
                                    "action_id": "view_full_output",
                                    "value": f"{request_id}:{i}",
                                }
                            ],
                        },
                    ]
                    _post_message(channel, text, blocks=blocks, thread_ts=thread_ts)
                    return

    _post_message(channel, text, thread_ts=thread_ts)


def notify_complete(request_id: str):
    """Post final synthesis and update parent message status."""
    channel = _get_channel()
    if not channel or _app is None:
        return

    with _thread_lock:
        thread_ts = _thread_map.get(request_id)
    if not thread_ts:
        return

    req = state.get_request(request_id)
    if not req:
        return

    # Post synthesis as final reply
    if req.synthesis:
        synth_text = req.synthesis
        if len(synth_text) > 2900:
            synth_text = synth_text[:2900] + "\n\n[... truncated ...]"

        emoji = STATUS_EMOJI.get(req.status, ":question:")
        synth_blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{emoji} *Final Result* ({req.duration_ms}ms)\n\n{synth_text}",
                },
            },
        ]
        _post_message(channel, "Final Result", blocks=synth_blocks, thread_ts=thread_ts)

    elif req.error:
        _post_message(channel, f":x: *Error:* {req.error}", thread_ts=thread_ts)

    # Update parent message status
    status_emoji = STATUS_EMOJI.get(req.status, ":question:")
    status_text = f"{status_emoji} MAS Request `{request_id}` — *{req.status}*"

    parent_blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"{status_emoji} MAS Request — {req.status.upper()}"},
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Request:* `{request_id}`\n*Query:* {req.user_query[:200]}\n"
                        f"*Duration:* {req.duration_ms}ms | *Agents:* {len(req.agents)}",
            },
        },
    ]
    _update_message(channel, thread_ts, status_text, blocks=parent_blocks)

    # Cleanup thread map for completed requests
    with _thread_lock:
        _thread_map.pop(request_id, None)
