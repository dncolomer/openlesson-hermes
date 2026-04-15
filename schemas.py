"""Tool schemas for the openLesson Hermes agent plugin.

Covers all 33 endpoints of the openLesson Agentic API v2:
  - API Keys (4)
  - Learning Plans (8)
  - Sessions (11)
  - Teaching Assistant (2)
  - Analytics (3)
  - Proofs (5)
"""

# ===================================================================
# API Keys
# ===================================================================

LIST_KEYS = {
    "name": "openlesson_list_keys",
    "description": (
        "List the user's openLesson API keys. Returns key metadata including "
        "label, scopes, rate limit, active status, and usage timestamps. "
        "Note: this endpoint uses session auth on the web — behaviour via API "
        "key may vary."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}

CREATE_KEY = {
    "name": "openlesson_create_key",
    "description": (
        "Create a new openLesson API key. The full key is only returned once "
        "at creation — store it securely. Note: this endpoint uses session auth "
        "on the web — behaviour via API key may vary."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "label": {
                "type": "string",
                "description": "Human-readable name for the key (e.g. 'Production Agent').",
            },
            "scopes": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "Permission scopes. Options: 'plans:read', 'plans:write', "
                    "'sessions:read', 'sessions:write', 'analysis:write', "
                    "'assistant:read', 'analytics:read', 'proofs:read', "
                    "'proofs:anchor', '*'. Defaults to ['*']."
                ),
            },
            "expires_in_days": {
                "type": "integer",
                "description": "Days until the key expires. Omit for no expiration.",
                "minimum": 1,
            },
        },
        "required": [],
    },
}

DELETE_KEY = {
    "name": "openlesson_delete_key",
    "description": (
        "Revoke an openLesson API key. The key will immediately stop working. "
        "Note: this endpoint uses session auth on the web — behaviour via API "
        "key may vary."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "key_id": {
                "type": "string",
                "description": "UUID of the API key to revoke.",
            },
        },
        "required": ["key_id"],
    },
}

UPDATE_KEY_SCOPES = {
    "name": "openlesson_update_key_scopes",
    "description": (
        "Update the permission scopes on an existing openLesson API key. "
        "Note: this endpoint uses session auth on the web — behaviour via API "
        "key may vary."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "key_id": {
                "type": "string",
                "description": "UUID of the API key to update.",
            },
            "scopes": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "New permission scopes to set on the key. Options: "
                    "'plans:read', 'plans:write', 'sessions:read', "
                    "'sessions:write', 'analysis:write', 'assistant:read', "
                    "'analytics:read', 'proofs:read', 'proofs:anchor', '*'."
                ),
            },
        },
        "required": ["key_id", "scopes"],
    },
}

# ===================================================================
# Learning Plans
# ===================================================================

LIST_PLANS = {
    "name": "openlesson_list_plans",
    "description": (
        "List the user's learning plans on openLesson. Supports filtering by "
        "status and pagination. Returns plan summaries with progress counts."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "description": "Filter by plan status.",
                "enum": ["active", "completed", "paused"],
            },
            "limit": {
                "type": "integer",
                "description": "Max results to return (default 20, max 100).",
                "minimum": 1,
                "maximum": 100,
            },
            "offset": {
                "type": "integer",
                "description": "Pagination offset.",
                "minimum": 0,
            },
        },
        "required": [],
    },
}

CREATE_PLAN = {
    "name": "openlesson_create_plan",
    "description": (
        "Create a structured learning plan on openLesson. Generates a directed "
        "graph of tutoring sessions for a given topic. Use this when a user "
        "wants to learn something new and needs a structured multi-session "
        "curriculum. Returns the plan with its session nodes, dependencies, "
        "and a cryptographic proof."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "The subject or topic the user wants to learn (e.g. 'Quantum Computing', 'Rust ownership model').",
            },
            "duration_days": {
                "type": "integer",
                "description": "Number of days to spread the plan over. Defaults to 14 if omitted.",
                "minimum": 1,
                "maximum": 365,
            },
            "difficulty": {
                "type": "string",
                "description": "Difficulty level for the plan content.",
                "enum": ["beginner", "intermediate", "advanced"],
            },
            "user_context": {
                "type": "string",
                "description": "Optional background about the learner (e.g. 'I have a CS degree but no ML experience').",
            },
        },
        "required": ["topic"],
    },
}

GET_PLAN = {
    "name": "openlesson_get_plan",
    "description": (
        "Get full details of an openLesson learning plan including all nodes "
        "and statistics (total/completed/in-progress nodes, session counts, "
        "total time)."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "plan_id": {
                "type": "string",
                "description": "UUID of the plan.",
            },
        },
        "required": ["plan_id"],
    },
}

UPDATE_PLAN = {
    "name": "openlesson_update_plan",
    "description": (
        "Update plan metadata on openLesson — title, notes, or status. "
        "Use this to rename a plan, add personal notes, or pause/resume a plan."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "plan_id": {
                "type": "string",
                "description": "UUID of the plan to update.",
            },
            "title": {
                "type": "string",
                "description": "New title for the plan.",
            },
            "notes": {
                "type": "string",
                "description": "Personal notes about the plan.",
            },
            "status": {
                "type": "string",
                "description": "New status for the plan.",
                "enum": ["active", "paused", "completed"],
            },
        },
        "required": ["plan_id"],
    },
}

DELETE_PLAN = {
    "name": "openlesson_delete_plan",
    "description": (
        "Delete an openLesson learning plan and all its nodes. Sessions linked "
        "to the plan are preserved but unlinked."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "plan_id": {
                "type": "string",
                "description": "UUID of the plan to delete.",
            },
        },
        "required": ["plan_id"],
    },
}

GET_PLAN_NODES = {
    "name": "openlesson_get_plan_nodes",
    "description": (
        "Get all nodes for an openLesson learning plan with their edges and "
        "graph layout info. Useful for visualising or navigating the plan's "
        "directed graph of sessions."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "plan_id": {
                "type": "string",
                "description": "UUID of the plan.",
            },
        },
        "required": ["plan_id"],
    },
}

ADAPT_PLAN = {
    "name": "openlesson_adapt_plan",
    "description": (
        "Adapt an existing openLesson learning plan using natural language "
        "instructions. Use this when a user wants to modify, restructure, "
        "skip, or extend parts of their current plan. Completed sessions are "
        "preserved by default. Returns the updated plan graph and a proof."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "plan_id": {
                "type": "string",
                "description": "UUID of the plan to adapt.",
            },
            "instruction": {
                "type": "string",
                "description": "Natural language instruction describing how to change the plan (e.g. 'Skip the intro sessions and add more on neural networks').",
            },
            "preserve_completed": {
                "type": "boolean",
                "description": "Whether to keep completed nodes unchanged. Defaults to true.",
            },
            "context": {
                "type": "object",
                "description": "Additional context for the AI adaptation (e.g. recent_session_feedback, user_current_level).",
            },
        },
        "required": ["plan_id", "instruction"],
    },
}

PLAN_FROM_VIDEO = {
    "name": "openlesson_plan_from_video",
    "description": (
        "Create a learning plan from a YouTube video on openLesson. The "
        "platform extracts the video content and generates a structured "
        "curriculum from it. Use this when a user shares a YouTube link and "
        "wants to learn the material covered in the video."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "youtube_url": {
                "type": "string",
                "description": "Full YouTube URL (e.g. 'https://youtube.com/watch?v=abc123').",
            },
            "duration_days": {
                "type": "integer",
                "description": "Number of days to spread the plan over. Defaults to 14 if omitted.",
                "minimum": 1,
                "maximum": 365,
            },
        },
        "required": ["youtube_url"],
    },
}

# ===================================================================
# Sessions
# ===================================================================

LIST_SESSIONS = {
    "name": "openlesson_list_sessions",
    "description": (
        "List openLesson tutoring sessions with optional filters. Supports "
        "filtering by status and plan, with pagination."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "description": "Filter by session status.",
                "enum": ["active", "paused", "completed", "ended_by_tutor"],
            },
            "plan_id": {
                "type": "string",
                "description": "Filter sessions belonging to a specific plan.",
            },
            "limit": {
                "type": "integer",
                "description": "Max results to return (default 20, max 100).",
                "minimum": 1,
                "maximum": 100,
            },
            "offset": {
                "type": "integer",
                "description": "Pagination offset.",
                "minimum": 0,
            },
        },
        "required": [],
    },
}

START_SESSION = {
    "name": "openlesson_start_session",
    "description": (
        "Start a tutoring session on openLesson. Sessions can be standalone "
        "(just a topic) or linked to a specific node in a learning plan. "
        "Returns the session details, a session plan with goals and strategy, "
        "an opening Socratic probe, and a proof. Use this when the user is "
        "ready to begin learning a topic."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "The topic for this tutoring session.",
            },
            "plan_id": {
                "type": "string",
                "description": "UUID of the learning plan this session belongs to (optional, for plan-linked sessions).",
            },
            "plan_node_id": {
                "type": "string",
                "description": "UUID of the specific plan node this session covers (optional, for plan-linked sessions).",
            },
            "tutoring_language": {
                "type": "string",
                "description": "ISO 639-1 language code for the session (e.g. 'en', 'es', 'fr'). Defaults to 'en'.",
            },
            "metadata": {
                "type": "object",
                "description": "Additional session configuration (e.g. user_timezone, preferred_probe_frequency).",
            },
        },
        "required": ["topic"],
    },
}

GET_SESSION = {
    "name": "openlesson_get_session",
    "description": (
        "Get full details of an openLesson tutoring session including the "
        "session plan, statistics (probe count, gap scores, word count), "
        "and currently active probes."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "description": "UUID of the session.",
            },
        },
        "required": ["session_id"],
    },
}

ANALYZE = {
    "name": "openlesson_analyze",
    "description": (
        "Submit an analysis heartbeat to an active openLesson tutoring "
        "session. Sends the user's response (text, audio, or images) for "
        "real-time Socratic analysis. Returns a gap score, signals, session "
        "plan updates, and the next probe. Use this each time the user "
        "provides input during a session. Gap scores below 0.3 indicate "
        "strong understanding; above 0.6 needs follow-up."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "description": "UUID of the active session.",
            },
            "text_input": {
                "type": "string",
                "description": "The user's text response to the current probe.",
            },
            "audio_base64": {
                "type": "string",
                "description": "Base64-encoded audio data of the user's spoken response.",
            },
            "audio_format": {
                "type": "string",
                "description": "Format of the audio data.",
                "enum": ["webm", "mp4", "ogg", "wav"],
            },
            "image_base64": {
                "type": "string",
                "description": "Base64-encoded image data (single image shorthand).",
            },
            "image_mime_type": {
                "type": "string",
                "description": "MIME type of the single image (e.g. 'image/png', 'image/jpeg').",
            },
            "images": {
                "type": "array",
                "description": "Multiple images to include (up to 5). Each has 'data' (base64), optional 'mime_type' and 'description'.",
                "items": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "string",
                            "description": "Base64-encoded image data.",
                        },
                        "mime_type": {
                            "type": "string",
                            "description": "MIME type (e.g. 'image/png').",
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the image content.",
                        },
                    },
                    "required": ["data"],
                },
                "maxItems": 5,
            },
            "context": {
                "type": "object",
                "description": (
                    "Analysis context — active_probe_ids (string[]), "
                    "focused_probe_id (string), tools_in_use (string[]), "
                    "user_actions_since_last (array of action objects)."
                ),
                "properties": {
                    "active_probe_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "IDs of currently active probes.",
                    },
                    "focused_probe_id": {
                        "type": "string",
                        "description": "ID of the probe the user is currently responding to.",
                    },
                    "tools_in_use": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tools the user is currently using (e.g. 'canvas', 'notebook').",
                    },
                    "user_actions_since_last": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "User actions since last heartbeat (tool, action, timestamp, data).",
                    },
                },
            },
        },
        "required": ["session_id"],
    },
}

PAUSE_SESSION = {
    "name": "openlesson_pause_session",
    "description": (
        "Pause an active openLesson tutoring session. The session state is "
        "preserved and can be resumed later. Use this when the user needs "
        "to take a break."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "description": "UUID of the session to pause.",
            },
            "reason": {
                "type": "string",
                "description": "Optional reason for pausing (e.g. 'Taking a break').",
            },
            "estimated_resume_minutes": {
                "type": "integer",
                "description": "Estimated minutes until resuming.",
                "minimum": 1,
            },
        },
        "required": ["session_id"],
    },
}

RESUME_SESSION = {
    "name": "openlesson_resume_session",
    "description": (
        "Resume a previously paused openLesson tutoring session. Restores "
        "the full session context and returns a reorientation probe to get "
        "the user back on track. Use this when the user wants to continue "
        "a paused session."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "description": "UUID of the session to resume.",
            },
            "continuation_context": {
                "type": "string",
                "description": "Optional context about what the user has done since pausing.",
            },
        },
        "required": ["session_id"],
    },
}

RESTART_SESSION = {
    "name": "openlesson_restart_session",
    "description": (
        "Restart an openLesson tutoring session from the beginning. Clears "
        "progress but preserves the session record. Use this when the user "
        "wants a fresh start with a different approach."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "description": "UUID of the session to restart.",
            },
            "reason": {
                "type": "string",
                "description": "Reason for restarting (e.g. 'Want to try a different approach').",
            },
            "preserve_transcript": {
                "type": "boolean",
                "description": "Whether to preserve the transcript from the previous attempt. Defaults to false.",
            },
            "new_strategy": {
                "type": "string",
                "description": "Suggested new strategy for the restarted session (e.g. 'Focus more on visual diagrams').",
            },
        },
        "required": ["session_id"],
    },
}

END_SESSION = {
    "name": "openlesson_end_session",
    "description": (
        "End an active openLesson tutoring session. Returns a session "
        "summary, generated report, statistics, plan updates (if linked), "
        "and a proof. Use this when the user is done learning or wants to "
        "finish the current session."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "description": "UUID of the session to end.",
            },
            "completion_status": {
                "type": "string",
                "description": "How the session ended.",
                "enum": ["completed", "ended_by_tutor"],
            },
            "user_feedback": {
                "type": "string",
                "description": "Optional feedback from the user about the session (used in report generation).",
            },
        },
        "required": ["session_id"],
    },
}

GET_SESSION_PROBES = {
    "name": "openlesson_get_session_probes",
    "description": (
        "Get probes for an openLesson tutoring session. Probes are the "
        "Socratic questions and tasks generated during analysis. Filter by "
        "status to see active, archived, or all probes."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "description": "UUID of the session.",
            },
            "status": {
                "type": "string",
                "description": "Filter probes by status.",
                "enum": ["active", "archived", "all"],
            },
        },
        "required": ["session_id"],
    },
}

GET_SESSION_PLAN = {
    "name": "openlesson_get_session_plan",
    "description": (
        "Get the session plan for an openLesson tutoring session. The session "
        "plan contains the goal, strategy, and ordered steps that guide the "
        "session flow."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "description": "UUID of the session.",
            },
        },
        "required": ["session_id"],
    },
}

GET_SESSION_TRANSCRIPT = {
    "name": "openlesson_get_session_transcript",
    "description": (
        "Get the transcript for an openLesson tutoring session. Supports "
        "full text, summary, or chunked formats. Use since_ms to get only "
        "new transcript data since a given point."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "description": "UUID of the session.",
            },
            "format": {
                "type": "string",
                "description": "Transcript format to return.",
                "enum": ["full", "summary", "chunks"],
            },
            "since_ms": {
                "type": "integer",
                "description": "Only return transcript after this timestamp (ms since session start).",
                "minimum": 0,
            },
        },
        "required": ["session_id"],
    },
}

# ===================================================================
# Teaching Assistant
# ===================================================================

ASK = {
    "name": "openlesson_ask",
    "description": (
        "Ask the openLesson teaching assistant a question during an active "
        "session. Maintains conversation history for context. Use this when "
        "the user is stuck on a concept or wants clarification without ending "
        "the session. Prefer this over ending and restarting."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "description": "UUID of the active session.",
            },
            "question": {
                "type": "string",
                "description": "The question to ask the teaching assistant.",
            },
            "context": {
                "type": "object",
                "description": (
                    "Additional context — relevant_probe_ids (string[]), "
                    "user_confusion_level (string), what_user_already_tried (string)."
                ),
                "properties": {
                    "relevant_probe_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "IDs of relevant probes for this question.",
                    },
                    "user_confusion_level": {
                        "type": "string",
                        "description": "Level of confusion (e.g. 'low', 'moderate', 'high').",
                    },
                    "what_user_already_tried": {
                        "type": "string",
                        "description": "What the user has already tried or explored.",
                    },
                },
            },
            "conversation_id": {
                "type": "string",
                "description": "UUID of an existing conversation to continue. Omit to start a new conversation thread.",
            },
        },
        "required": ["session_id", "question"],
    },
}

GET_CONVERSATION = {
    "name": "openlesson_get_conversation",
    "description": (
        "Get the conversation history with the openLesson teaching assistant "
        "for a specific conversation thread within a session."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "description": "UUID of the session.",
            },
            "conversation_id": {
                "type": "string",
                "description": "UUID of the conversation thread.",
            },
        },
        "required": ["session_id", "conversation_id"],
    },
}

# ===================================================================
# Analytics
# ===================================================================

PLAN_ANALYTICS = {
    "name": "openlesson_plan_analytics",
    "description": (
        "Get detailed analytics for a specific openLesson learning plan. "
        "Returns progress breakdown, session stats, performance trends with "
        "gap score history, per-node details, and AI recommendations."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "plan_id": {
                "type": "string",
                "description": "UUID of the plan.",
            },
        },
        "required": ["plan_id"],
    },
}

SESSION_ANALYTICS = {
    "name": "openlesson_session_analytics",
    "description": (
        "Get detailed analytics for a specific openLesson tutoring session. "
        "Returns probe breakdown, gap score timeline, session plan progress, "
        "transcript stats, and the generated report."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "description": "UUID of the session.",
            },
        },
        "required": ["session_id"],
    },
}

USER_ANALYTICS = {
    "name": "openlesson_user_analytics",
    "description": (
        "Retrieve the user's overall learning analytics from openLesson. "
        "Returns an overview of total plans, sessions, completion rates, "
        "performance trends, learning history, calibration data, and "
        "achievements."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}

# ===================================================================
# Proofs
# ===================================================================

LIST_PROOFS = {
    "name": "openlesson_list_proofs",
    "description": (
        "List cryptographic proofs from openLesson. Every mutation generates "
        "a SHA-256 fingerprint proof. Filter by session, plan, proof type, "
        "or anchoring status."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "description": "Filter proofs by session UUID.",
            },
            "plan_id": {
                "type": "string",
                "description": "Filter proofs by plan UUID.",
            },
            "type": {
                "type": "string",
                "description": "Filter by proof type.",
                "enum": [
                    "plan_created",
                    "plan_adapted",
                    "session_started",
                    "session_paused",
                    "session_resumed",
                    "session_ended",
                    "analysis_heartbeat",
                    "assistant_query",
                    "session_batch",
                ],
            },
            "anchored": {
                "type": "boolean",
                "description": "Filter by on-chain anchoring status.",
            },
            "limit": {
                "type": "integer",
                "description": "Max results to return (default 50).",
                "minimum": 1,
            },
            "offset": {
                "type": "integer",
                "description": "Pagination offset.",
                "minimum": 0,
            },
        },
        "required": [],
    },
}

GET_PROOF = {
    "name": "openlesson_get_proof",
    "description": (
        "Get full details of a cryptographic proof from openLesson, including "
        "chain linking info, verification status, and related proofs."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "proof_id": {
                "type": "string",
                "description": "UUID of the proof.",
            },
        },
        "required": ["proof_id"],
    },
}

VERIFY_PROOF = {
    "name": "openlesson_verify_proof",
    "description": (
        "Verify an openLesson cryptographic proof by recalculating its "
        "fingerprint and checking on-chain integrity. Returns whether the "
        "stored, calculated, and on-chain fingerprints all match."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "proof_id": {
                "type": "string",
                "description": "UUID of the proof to verify.",
            },
        },
        "required": ["proof_id"],
    },
}

ANCHOR_PROOF = {
    "name": "openlesson_anchor_proof",
    "description": (
        "Anchor an openLesson proof on Solana. Writes the proof's SHA-256 "
        "fingerprint to the blockchain for trustless verification. Returns "
        "the transaction signature and explorer URL."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "proof_id": {
                "type": "string",
                "description": "UUID of the proof to anchor.",
            },
        },
        "required": ["proof_id"],
    },
}

GET_SESSION_BATCH = {
    "name": "openlesson_get_session_batch",
    "description": (
        "Get the Merkle batch for a completed openLesson session. All "
        "heartbeat proofs are aggregated into a Merkle tree at session end, "
        "allowing verification of individual heartbeats against the root."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "session_id": {
                "type": "string",
                "description": "UUID of the completed session.",
            },
        },
        "required": ["session_id"],
    },
}
