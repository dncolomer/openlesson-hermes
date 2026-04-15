"""openLesson Hermes agent plugin.

Provides 33 tools covering the full openLesson Agentic API v2 surface
and a pre_llm_call hook that injects active session context into every
LLM turn.

Tool categories:
  - API Keys (4): list, create, delete, update scopes
  - Learning Plans (8): list, create, get, update, delete, nodes, adapt, from-video
  - Sessions (11): list, start, get, analyze, pause, resume, restart, end, probes, plan, transcript
  - Teaching Assistant (2): ask, get conversation
  - Analytics (3): plan, session, user
  - Proofs (5): list, get, verify, anchor, session batch
"""

import json
import logging
from pathlib import Path

from . import schemas, tools

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Active session state — shared across tools and hooks
# ---------------------------------------------------------------------------

_active_session: dict = {"session_id": None, "topic": None}


# ---------------------------------------------------------------------------
# Wrapped handlers that track session state
# ---------------------------------------------------------------------------


def _start_session_wrapper(args: dict, **kwargs) -> str:
    """Start a session and track it as the active session."""
    result_json = tools.start_session(args, **kwargs)
    try:
        result = json.loads(result_json)
        if "error" not in result:
            session = result.get("session", {})
            _active_session["session_id"] = session.get("id")
            _active_session["topic"] = args.get("topic")
            logger.info("openLesson session started: %s", _active_session["session_id"])
    except (json.JSONDecodeError, KeyError):
        pass
    return result_json


def _end_session_wrapper(args: dict, **kwargs) -> str:
    """End a session and clear active session tracking."""
    result_json = tools.end_session(args, **kwargs)
    try:
        result = json.loads(result_json)
        if "error" not in result:
            logger.info("openLesson session ended: %s", _active_session["session_id"])
            _active_session["session_id"] = None
            _active_session["topic"] = None
    except (json.JSONDecodeError, KeyError):
        pass
    return result_json


# ---------------------------------------------------------------------------
# Hook: inject active session context before every LLM call
# ---------------------------------------------------------------------------


def _on_pre_llm_call(session_id, user_message, **kwargs):
    """Inject active openLesson session context if one is running."""
    if _active_session["session_id"]:
        return {
            "context": (
                f"[openLesson] Active tutoring session: "
                f"{_active_session['topic']} "
                f"(ID: {_active_session['session_id']})"
            )
        }
    return None


# ---------------------------------------------------------------------------
# Plugin registration entry point
# ---------------------------------------------------------------------------

_TOOL_REGISTRY = [
    # --- API Keys ---
    ("openlesson_list_keys", schemas.LIST_KEYS, tools.list_keys),
    ("openlesson_create_key", schemas.CREATE_KEY, tools.create_key),
    ("openlesson_delete_key", schemas.DELETE_KEY, tools.delete_key),
    (
        "openlesson_update_key_scopes",
        schemas.UPDATE_KEY_SCOPES,
        tools.update_key_scopes,
    ),
    # --- Learning Plans ---
    ("openlesson_list_plans", schemas.LIST_PLANS, tools.list_plans),
    ("openlesson_create_plan", schemas.CREATE_PLAN, tools.create_plan),
    ("openlesson_get_plan", schemas.GET_PLAN, tools.get_plan),
    ("openlesson_update_plan", schemas.UPDATE_PLAN, tools.update_plan),
    ("openlesson_delete_plan", schemas.DELETE_PLAN, tools.delete_plan),
    ("openlesson_get_plan_nodes", schemas.GET_PLAN_NODES, tools.get_plan_nodes),
    ("openlesson_adapt_plan", schemas.ADAPT_PLAN, tools.adapt_plan),
    ("openlesson_plan_from_video", schemas.PLAN_FROM_VIDEO, tools.plan_from_video),
    # --- Sessions (start/end use state-tracking wrappers) ---
    ("openlesson_list_sessions", schemas.LIST_SESSIONS, tools.list_sessions),
    ("openlesson_start_session", schemas.START_SESSION, "_start_session_wrapper"),
    ("openlesson_get_session", schemas.GET_SESSION, tools.get_session),
    ("openlesson_analyze", schemas.ANALYZE, tools.analyze),
    ("openlesson_pause_session", schemas.PAUSE_SESSION, tools.pause_session),
    ("openlesson_resume_session", schemas.RESUME_SESSION, tools.resume_session),
    ("openlesson_restart_session", schemas.RESTART_SESSION, tools.restart_session),
    ("openlesson_end_session", schemas.END_SESSION, "_end_session_wrapper"),
    (
        "openlesson_get_session_probes",
        schemas.GET_SESSION_PROBES,
        tools.get_session_probes,
    ),
    ("openlesson_get_session_plan", schemas.GET_SESSION_PLAN, tools.get_session_plan),
    (
        "openlesson_get_session_transcript",
        schemas.GET_SESSION_TRANSCRIPT,
        tools.get_session_transcript,
    ),
    # --- Teaching Assistant ---
    ("openlesson_ask", schemas.ASK, tools.ask_assistant),
    ("openlesson_get_conversation", schemas.GET_CONVERSATION, tools.get_conversation),
    # --- Analytics ---
    ("openlesson_plan_analytics", schemas.PLAN_ANALYTICS, tools.plan_analytics),
    (
        "openlesson_session_analytics",
        schemas.SESSION_ANALYTICS,
        tools.session_analytics,
    ),
    ("openlesson_user_analytics", schemas.USER_ANALYTICS, tools.user_analytics),
    # --- Proofs ---
    ("openlesson_list_proofs", schemas.LIST_PROOFS, tools.list_proofs),
    ("openlesson_get_proof", schemas.GET_PROOF, tools.get_proof),
    ("openlesson_verify_proof", schemas.VERIFY_PROOF, tools.verify_proof),
    ("openlesson_anchor_proof", schemas.ANCHOR_PROOF, tools.anchor_proof),
    (
        "openlesson_get_session_batch",
        schemas.GET_SESSION_BATCH,
        tools.get_session_batch,
    ),
]


def register(ctx):
    """Wire schemas to handlers and register hooks with Hermes."""

    # Resolve wrapper sentinels to the actual local functions
    _wrappers = {
        "_start_session_wrapper": _start_session_wrapper,
        "_end_session_wrapper": _end_session_wrapper,
    }

    for name, schema, handler in _TOOL_REGISTRY:
        if isinstance(handler, str):
            handler = _wrappers[handler]
        ctx.register_tool(
            name=name,
            toolset="openlesson",
            schema=schema,
            handler=handler,
        )

    # Hook
    ctx.register_hook("pre_llm_call", _on_pre_llm_call)

    # Bundled skill
    skills_dir = Path(__file__).parent / "skills"
    if skills_dir.exists():
        for child in sorted(skills_dir.iterdir()):
            skill_md = child / "SKILL.md"
            if child.is_dir() and skill_md.exists():
                ctx.register_skill(child.name, skill_md)
                logger.info("Registered openLesson skill: %s", child.name)

    logger.info("openLesson plugin registered (%d tools)", len(_TOOL_REGISTRY))
