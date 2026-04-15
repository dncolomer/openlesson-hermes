"""Tool handlers for the openLesson Hermes agent plugin.

All handlers use only the Python standard library (urllib.request) so the
plugin has zero external dependencies.

Covers the full openLesson Agentic API v2 surface (33 endpoints):
  - API Keys (4)
  - Learning Plans (8)
  - Sessions (11)
  - Teaching Assistant (2)
  - Analytics (3)
  - Proofs (5)
"""

import json
import os
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "https://www.openlesson.academy"


def _api_request(
    method: str,
    path: str,
    body: dict | None = None,
    query: dict | None = None,
) -> dict:
    """Make an authenticated request to the openLesson v2 API.

    Returns the parsed JSON response body on success, or an error dict on
    HTTP errors.
    """
    api_key = os.environ["OPENLESSON_API_KEY"]
    url = f"{BASE_URL}{path}"
    if query:
        # Drop None values so callers can pass optional params directly
        filtered = {k: v for k, v in query.items() if v is not None}
        if filtered:
            url = f"{url}?{urllib.parse.urlencode(filtered)}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        try:
            return json.loads(error_body)
        except json.JSONDecodeError:
            return {"error": {"code": str(exc.code), "message": error_body}}


def _ok(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False)


def _err(message: str) -> str:
    return json.dumps({"error": {"code": "plugin_error", "message": message}})


# ===================================================================
# API Keys (session auth — included for completeness)
# ===================================================================


def list_keys(args: dict, **kwargs) -> str:
    """List the user's API keys."""
    try:
        result = _api_request("GET", "/api/v2/agent/keys")
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def create_key(args: dict, **kwargs) -> str:
    """Create a new API key."""
    try:
        body: dict = {}
        for key in ("label", "scopes", "expires_in_days"):
            if key in args:
                body[key] = args[key]
        result = _api_request("POST", "/api/v2/agent/keys", body)
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def delete_key(args: dict, **kwargs) -> str:
    """Revoke an API key."""
    try:
        key_id = args["key_id"]
        result = _api_request("DELETE", f"/api/v2/agent/keys/{key_id}")
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def update_key_scopes(args: dict, **kwargs) -> str:
    """Update the scopes on an API key."""
    try:
        key_id = args["key_id"]
        body: dict = {"scopes": args["scopes"]}
        result = _api_request("PATCH", f"/api/v2/agent/keys/{key_id}/scopes", body)
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


# ===================================================================
# Learning Plans
# ===================================================================


def list_plans(args: dict, **kwargs) -> str:
    """List learning plans with optional filters."""
    try:
        query: dict = {}
        for key in ("status", "limit", "offset"):
            if key in args:
                query[key] = args[key]
        result = _api_request("GET", "/api/v2/agent/plans", query=query)
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def create_plan(args: dict, **kwargs) -> str:
    """Create a learning plan from a topic."""
    try:
        body: dict = {"topic": args["topic"]}
        for key in ("duration_days", "difficulty", "user_context"):
            if key in args:
                body[key] = args[key]
        result = _api_request("POST", "/api/v2/agent/plans", body)
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def get_plan(args: dict, **kwargs) -> str:
    """Get plan details with nodes and statistics."""
    try:
        plan_id = args["plan_id"]
        result = _api_request("GET", f"/api/v2/agent/plans/{plan_id}")
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def update_plan(args: dict, **kwargs) -> str:
    """Update plan metadata (title, notes, status)."""
    try:
        plan_id = args["plan_id"]
        body: dict = {}
        for key in ("title", "notes", "status"):
            if key in args:
                body[key] = args[key]
        result = _api_request("PATCH", f"/api/v2/agent/plans/{plan_id}", body)
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def delete_plan(args: dict, **kwargs) -> str:
    """Delete a plan and its nodes, unlinking sessions."""
    try:
        plan_id = args["plan_id"]
        result = _api_request("DELETE", f"/api/v2/agent/plans/{plan_id}")
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def get_plan_nodes(args: dict, **kwargs) -> str:
    """Get plan nodes with edges and graph info."""
    try:
        plan_id = args["plan_id"]
        result = _api_request("GET", f"/api/v2/agent/plans/{plan_id}/nodes")
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def adapt_plan(args: dict, **kwargs) -> str:
    """AI-powered plan adaptation via natural language."""
    try:
        plan_id = args["plan_id"]
        body: dict = {"instruction": args["instruction"]}
        for key in ("preserve_completed", "context"):
            if key in args:
                body[key] = args[key]
        result = _api_request("POST", f"/api/v2/agent/plans/{plan_id}/adapt", body)
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def plan_from_video(args: dict, **kwargs) -> str:
    """Create a learning plan from a YouTube video."""
    try:
        body: dict = {"youtube_url": args["youtube_url"]}
        if "duration_days" in args:
            body["duration_days"] = args["duration_days"]
        result = _api_request("POST", "/api/v2/agent/plans/from-video", body)
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


# ===================================================================
# Sessions
# ===================================================================


def list_sessions(args: dict, **kwargs) -> str:
    """List sessions with optional filters."""
    try:
        query: dict = {}
        for key in ("status", "plan_id", "limit", "offset"):
            if key in args:
                query[key] = args[key]
        result = _api_request("GET", "/api/v2/agent/sessions", query=query)
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def start_session(args: dict, **kwargs) -> str:
    """Start a tutoring session (standalone or linked to a plan)."""
    try:
        body: dict = {"topic": args["topic"]}
        for key in ("plan_id", "plan_node_id", "tutoring_language", "metadata"):
            if key in args:
                body[key] = args[key]
        result = _api_request("POST", "/api/v2/agent/sessions", body)
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def get_session(args: dict, **kwargs) -> str:
    """Get session details, plan, stats, and active probes."""
    try:
        session_id = args["session_id"]
        result = _api_request("GET", f"/api/v2/agent/sessions/{session_id}")
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def analyze(args: dict, **kwargs) -> str:
    """Submit an analysis heartbeat with multimodal inputs."""
    try:
        session_id = args["session_id"]
        inputs: list[dict] = []

        if "text_input" in args:
            inputs.append({"type": "text", "content": args["text_input"]})
        if "audio_base64" in args:
            audio_input: dict = {"type": "audio", "data": args["audio_base64"]}
            if "audio_format" in args:
                audio_input["format"] = args["audio_format"]
            inputs.append(audio_input)
        if "image_base64" in args:
            image_input: dict = {"type": "image", "data": args["image_base64"]}
            if "image_mime_type" in args:
                image_input["mime_type"] = args["image_mime_type"]
            inputs.append(image_input)
        # Support multiple images via the images array param
        if "images" in args:
            for img in args["images"]:
                image_entry: dict = {"type": "image", "data": img["data"]}
                if "mime_type" in img:
                    image_entry["mime_type"] = img["mime_type"]
                if "description" in img:
                    image_entry["description"] = img["description"]
                inputs.append(image_entry)

        body: dict = {}
        if inputs:
            body["inputs"] = inputs
        if "context" in args:
            body["context"] = args["context"]

        result = _api_request(
            "POST", f"/api/v2/agent/sessions/{session_id}/analyze", body
        )
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def pause_session(args: dict, **kwargs) -> str:
    """Pause an active session."""
    try:
        session_id = args["session_id"]
        body: dict = {}
        for key in ("reason", "estimated_resume_minutes"):
            if key in args:
                body[key] = args[key]
        result = _api_request(
            "POST", f"/api/v2/agent/sessions/{session_id}/pause", body
        )
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def resume_session(args: dict, **kwargs) -> str:
    """Resume a paused session."""
    try:
        session_id = args["session_id"]
        body: dict = {}
        if "continuation_context" in args:
            body["continuation_context"] = args["continuation_context"]
        result = _api_request(
            "POST", f"/api/v2/agent/sessions/{session_id}/resume", body
        )
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def restart_session(args: dict, **kwargs) -> str:
    """Restart a session from the beginning."""
    try:
        session_id = args["session_id"]
        body: dict = {}
        for key in ("reason", "preserve_transcript", "new_strategy"):
            if key in args:
                body[key] = args[key]
        result = _api_request(
            "POST", f"/api/v2/agent/sessions/{session_id}/restart", body
        )
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def end_session(args: dict, **kwargs) -> str:
    """End a session and get the summary report."""
    try:
        session_id = args["session_id"]
        body: dict = {}
        for key in ("completion_status", "user_feedback"):
            if key in args:
                body[key] = args[key]
        result = _api_request("POST", f"/api/v2/agent/sessions/{session_id}/end", body)
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def get_session_probes(args: dict, **kwargs) -> str:
    """Get probes for a session."""
    try:
        session_id = args["session_id"]
        query: dict = {}
        if "status" in args:
            query["status"] = args["status"]
        result = _api_request(
            "GET", f"/api/v2/agent/sessions/{session_id}/probes", query=query
        )
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def get_session_plan(args: dict, **kwargs) -> str:
    """Get the session plan with steps."""
    try:
        session_id = args["session_id"]
        result = _api_request("GET", f"/api/v2/agent/sessions/{session_id}/plan")
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def get_session_transcript(args: dict, **kwargs) -> str:
    """Get the session transcript."""
    try:
        session_id = args["session_id"]
        query: dict = {}
        for key in ("format", "since_ms"):
            if key in args:
                query[key] = args[key]
        result = _api_request(
            "GET", f"/api/v2/agent/sessions/{session_id}/transcript", query=query
        )
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


# ===================================================================
# Teaching Assistant
# ===================================================================


def ask_assistant(args: dict, **kwargs) -> str:
    """Ask the teaching assistant a question during a session."""
    try:
        session_id = args["session_id"]
        body: dict = {"question": args["question"]}
        for key in ("context", "conversation_id"):
            if key in args:
                body[key] = args[key]
        result = _api_request("POST", f"/api/v2/agent/sessions/{session_id}/ask", body)
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def get_conversation(args: dict, **kwargs) -> str:
    """Get conversation history with the teaching assistant."""
    try:
        session_id = args["session_id"]
        conversation_id = args["conversation_id"]
        result = _api_request(
            "GET",
            f"/api/v2/agent/sessions/{session_id}/assistant/conversations/{conversation_id}",
        )
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


# ===================================================================
# Analytics
# ===================================================================


def plan_analytics(args: dict, **kwargs) -> str:
    """Get analytics for a specific plan."""
    try:
        plan_id = args["plan_id"]
        result = _api_request("GET", f"/api/v2/agent/analytics/plans/{plan_id}")
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def session_analytics(args: dict, **kwargs) -> str:
    """Get analytics for a specific session."""
    try:
        session_id = args["session_id"]
        result = _api_request("GET", f"/api/v2/agent/analytics/sessions/{session_id}")
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def user_analytics(args: dict, **kwargs) -> str:
    """Retrieve the user's overall learning analytics."""
    try:
        result = _api_request("GET", "/api/v2/agent/analytics/user")
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


# ===================================================================
# Proofs
# ===================================================================


def list_proofs(args: dict, **kwargs) -> str:
    """List cryptographic proofs with optional filters."""
    try:
        query: dict = {}
        for key in ("session_id", "plan_id", "type", "anchored", "limit", "offset"):
            if key in args:
                query[key] = args[key]
        result = _api_request("GET", "/api/v2/agent/proofs", query=query)
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def get_proof(args: dict, **kwargs) -> str:
    """Get proof details including chain and related proofs."""
    try:
        proof_id = args["proof_id"]
        result = _api_request("GET", f"/api/v2/agent/proofs/{proof_id}")
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def verify_proof(args: dict, **kwargs) -> str:
    """Verify a proof by recalculating its fingerprint."""
    try:
        proof_id = args["proof_id"]
        result = _api_request("GET", f"/api/v2/agent/proofs/{proof_id}/verify")
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def anchor_proof(args: dict, **kwargs) -> str:
    """Anchor a proof on Solana."""
    try:
        proof_id = args["proof_id"]
        result = _api_request("POST", f"/api/v2/agent/proofs/{proof_id}/anchor")
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


def get_session_batch(args: dict, **kwargs) -> str:
    """Get the Merkle batch for a completed session."""
    try:
        session_id = args["session_id"]
        result = _api_request("GET", f"/api/v2/agent/proofs/session/{session_id}/batch")
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))
