# openLesson Plugin for Hermes Agent

Hermes agent plugin for the [openLesson](https://www.openlesson.academy) tutoring platform. Full coverage of the Agentic API v2 — 33 tools across learning plans, multimodal sessions, teaching assistant, analytics, cryptographic proofs, and key management.

## Install

```bash
hermes plugins install dncolomer/openlesson-hermes
```

## Configuration

Set your API key as an environment variable:

```bash
export OPENLESSON_API_KEY="sk_..."
```

Get a key from your [openLesson dashboard](https://www.openlesson.academy/dashboard).

## Tools (33)

### API Keys

| Tool | Description |
|------|-------------|
| `openlesson_list_keys` | List API keys |
| `openlesson_create_key` | Create a new API key |
| `openlesson_delete_key` | Revoke an API key |
| `openlesson_update_key_scopes` | Update key permission scopes |

### Learning Plans

| Tool | Description |
|------|-------------|
| `openlesson_list_plans` | List learning plans with optional filters |
| `openlesson_create_plan` | Create a structured plan for a topic |
| `openlesson_get_plan` | Get plan details with nodes and statistics |
| `openlesson_update_plan` | Update plan metadata (title, notes, status) |
| `openlesson_delete_plan` | Delete a plan and its nodes |
| `openlesson_get_plan_nodes` | Get plan nodes with edges and graph info |
| `openlesson_adapt_plan` | AI-powered plan adaptation via natural language |
| `openlesson_plan_from_video` | Generate a plan from a YouTube video |

### Sessions

| Tool | Description |
|------|-------------|
| `openlesson_list_sessions` | List sessions with optional filters |
| `openlesson_start_session` | Start a session (standalone or plan-linked) |
| `openlesson_get_session` | Get session details, plan, stats, and active probes |
| `openlesson_analyze` | Submit text/audio/images for Socratic analysis |
| `openlesson_pause_session` | Pause an active session |
| `openlesson_resume_session` | Resume a paused session |
| `openlesson_restart_session` | Restart a session with a new strategy |
| `openlesson_end_session` | End a session and get the report |
| `openlesson_get_session_probes` | Get session probes (active/archived/all) |
| `openlesson_get_session_plan` | Get the session plan with steps |
| `openlesson_get_session_transcript` | Get session transcript (full/summary/chunks) |

### Teaching Assistant

| Tool | Description |
|------|-------------|
| `openlesson_ask` | Ask the teaching assistant a question |
| `openlesson_get_conversation` | Get conversation history for a thread |

### Analytics

| Tool | Description |
|------|-------------|
| `openlesson_plan_analytics` | Plan analytics — progress, performance, recommendations |
| `openlesson_session_analytics` | Session analytics — probes, gap timeline, transcript stats |
| `openlesson_user_analytics` | User-wide analytics — overview, history, achievements |

### Proofs

| Tool | Description |
|------|-------------|
| `openlesson_list_proofs` | List cryptographic proofs |
| `openlesson_get_proof` | Get proof details and chain linking |
| `openlesson_verify_proof` | Verify a proof's fingerprint integrity |
| `openlesson_anchor_proof` | Anchor a proof on Solana |
| `openlesson_get_session_batch` | Get the Merkle batch for a session |

## Hooks

- **`pre_llm_call`** — Injects active session context into every LLM turn so the model stays aware of the current tutoring session and topic.

## Quick Start

```
> Learn about quantum computing

Agent uses openlesson_create_plan to build a 14-day curriculum,
then openlesson_start_session to begin the first node.

During the session, openlesson_analyze processes the user's responses
and returns gap scores with Socratic follow-up probes.

The pre_llm_call hook keeps session context visible across turns.

When done, openlesson_end_session generates a report and batch proof.
Use openlesson_verify_proof to check integrity.
```

## Key Concepts

- **Gap Score** (0.0–1.0): Below 0.3 = strong understanding, above 0.6 = needs follow-up
- **Probes**: Socratic questions/tasks generated during analysis (question, task, suggestion, checkpoint, feedback)
- **Proofs**: Every mutation generates a SHA-256 fingerprint, anchorable on Solana. Session heartbeats are Merkle-batched.
- **Multimodal**: Analysis accepts audio (webm/mp4/ogg/wav), text, and up to 5 images per request

## Requirements

- Python >= 3.10
- No external dependencies (uses only `urllib.request`)

## License

MIT
