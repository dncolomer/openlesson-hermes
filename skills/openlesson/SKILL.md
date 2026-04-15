# openLesson Agent API v2 Skill

You are an AI agent with full access to the openLesson tutoring platform via its v2 API (33 tools).

## Overview

openLesson is a Socratic tutoring system that helps users learn through guided questioning rather than giving answers. The platform supports:
- **Learning Plans** — directed graphs of sessions generated from topics or YouTube videos
- **Tutoring Sessions** — real-time multimodal analysis (audio, text, images) with session plan tracking
- **Teaching Assistant** — in-session Q&A with conversation history
- **Analytics** — deep insights on plans, sessions, and user progress
- **Cryptographic Proofs** — SHA-256 fingerprints for every action, Merkle-batched per session, anchorable on Solana
- **API Key Management** — scoped keys with expiration

## Authentication

Include your API key in the Authorization header:
```
Authorization: Bearer YOUR_API_KEY
```

**Base URL**: `https://www.openlesson.academy/api/v2/agent/`
**Rate limit**: 120 requests/minute
**Environment variable**: `OPENLESSON_API_KEY`

API keys are generated from the user's dashboard at `/dashboard`. Keys support scoped permissions and optional expiration.

---

## Full Endpoint Reference (33 tools)

### API Keys (4 tools)

> Note: These endpoints use session auth on the web. Behaviour via API key may vary.

| Tool | Method | Path | Description |
|------|--------|------|-------------|
| `openlesson_list_keys` | GET | `/keys` | List API keys |
| `openlesson_create_key` | POST | `/keys` | Create API key (label?, scopes?, expires_in_days?) |
| `openlesson_delete_key` | DELETE | `/keys/{id}` | Revoke API key |
| `openlesson_update_key_scopes` | PATCH | `/keys/{id}/scopes` | Update key scopes |

### Learning Plans (8 tools)

| Tool | Method | Path | Description |
|------|--------|------|-------------|
| `openlesson_list_plans` | GET | `/plans` | List plans (status?, limit?, offset?) |
| `openlesson_create_plan` | POST | `/plans` | Create plan from topic |
| `openlesson_get_plan` | GET | `/plans/{id}` | Get plan with nodes + statistics |
| `openlesson_update_plan` | PATCH | `/plans/{id}` | Update plan metadata (title?, notes?, status?) |
| `openlesson_delete_plan` | DELETE | `/plans/{id}` | Delete plan + nodes, unlink sessions |
| `openlesson_get_plan_nodes` | GET | `/plans/{id}/nodes` | Get nodes with edges + graph info |
| `openlesson_adapt_plan` | POST | `/plans/{id}/adapt` | AI-powered adaptation (instruction, context?) |
| `openlesson_plan_from_video` | POST | `/plans/from-video` | Create plan from YouTube URL |

### Sessions (11 tools)

| Tool | Method | Path | Description |
|------|--------|------|-------------|
| `openlesson_list_sessions` | GET | `/sessions` | List sessions (status?, plan_id?, limit?, offset?) |
| `openlesson_start_session` | POST | `/sessions` | Start session — standalone or plan-linked |
| `openlesson_get_session` | GET | `/sessions/{id}` | Get session details + plan + stats + active probes |
| `openlesson_analyze` | POST | `/sessions/{id}/analyze` | Analysis heartbeat — multimodal inputs |
| `openlesson_pause_session` | POST | `/sessions/{id}/pause` | Pause session |
| `openlesson_resume_session` | POST | `/sessions/{id}/resume` | Resume session — returns reorientation probe |
| `openlesson_restart_session` | POST | `/sessions/{id}/restart` | Restart session from beginning |
| `openlesson_end_session` | POST | `/sessions/{id}/end` | End session — generates report + batch proof |
| `openlesson_get_session_probes` | GET | `/sessions/{id}/probes` | List probes (status: active\|archived\|all) |
| `openlesson_get_session_plan` | GET | `/sessions/{id}/plan` | Get session plan with steps |
| `openlesson_get_session_transcript` | GET | `/sessions/{id}/transcript` | Get transcript (format: full\|summary\|chunks) |

### Teaching Assistant (2 tools)

| Tool | Method | Path | Description |
|------|--------|------|-------------|
| `openlesson_ask` | POST | `/sessions/{id}/ask` | Ask a question (question, context?, conversation_id?) |
| `openlesson_get_conversation` | GET | `/sessions/{id}/assistant/conversations/{convId}` | Get conversation history |

### Analytics (3 tools)

| Tool | Method | Path | Description |
|------|--------|------|-------------|
| `openlesson_plan_analytics` | GET | `/analytics/plans/{id}` | Plan analytics — progress, sessions, performance, recommendations |
| `openlesson_session_analytics` | GET | `/analytics/sessions/{id}` | Session analytics — probes, gap timeline, plan progress, transcript stats |
| `openlesson_user_analytics` | GET | `/analytics/user` | User-wide analytics — overview, performance, history, achievements |

### Proofs (5 tools)

| Tool | Method | Path | Description |
|------|--------|------|-------------|
| `openlesson_list_proofs` | GET | `/proofs` | List proofs (session_id?, plan_id?, type?, anchored?, limit?, offset?) |
| `openlesson_get_proof` | GET | `/proofs/{id}` | Get proof details + chain + related |
| `openlesson_verify_proof` | GET | `/proofs/{id}/verify` | Verify proof (recalculates fingerprint, checks chain) |
| `openlesson_anchor_proof` | POST | `/proofs/{id}/anchor` | Anchor proof on Solana |
| `openlesson_get_session_batch` | GET | `/proofs/session/{id}/batch` | Get session Merkle batch |

---

## Key Concepts

### Gap Score (0.0 – 1.0)
- **0.0–0.3**: Confident, flowing reasoning — strong understanding
- **0.4–0.6**: Some hesitation, minor gaps
- **0.7–1.0**: Clear gaps, contradictions, stuck thinking — needs follow-up

### Probe Types
- **question**: Socratic probing questions
- **task**: Direct activities ("Try solving...", "Draw a diagram...")
- **suggestion**: Soft guidance ("Consider looking at...")
- **checkpoint**: Review moments ("Let's summarise...")
- **feedback**: Acknowledgment of progress

### Proof Types
- `plan_created`, `plan_adapted` — Plan events (anchored immediately)
- `session_started`, `session_paused`, `session_resumed`, `session_ended` — Session lifecycle (anchored immediately)
- `analysis_heartbeat`, `assistant_query` — In-session events (batched at session end)
- `session_batch` — Merkle root of all session heartbeats

### Multimodal Analysis Inputs
- **Audio**: base64-encoded, formats: webm, mp4, ogg, wav. Max 60s / 10MB.
- **Text**: Max 10,000 characters.
- **Images**: base64-encoded, formats: png, jpeg, webp. Max 5MB each, 5 per request.

---

## Workflows

### Complete Learning Journey

```python
import requests, os

API_KEY = os.environ["OPENLESSON_API_KEY"]
BASE = "https://www.openlesson.academy"
H = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# 1. Create a learning plan
plan = requests.post(f"{BASE}/api/v2/agent/plans",
    json={"topic": "Quantum Computing", "duration_days": 14}, headers=H).json()

plan_id = plan["plan"]["id"]
nodes = plan["plan"]["nodes"]
start_node = next(n for n in nodes if n["is_start"])

# 2. Check plan analytics
analytics = requests.get(f"{BASE}/api/v2/agent/analytics/plans/{plan_id}", headers=H).json()

# 3. Adapt the plan if needed
requests.post(f"{BASE}/api/v2/agent/plans/{plan_id}/adapt",
    json={"instruction": "Skip intro, I know the basics"}, headers=H)

# 4. Start a session linked to the first node
session = requests.post(f"{BASE}/api/v2/agent/sessions",
    json={
        "topic": start_node["title"],
        "plan_id": plan_id,
        "plan_node_id": start_node["id"]
    }, headers=H).json()

session_id = session["session"]["id"]
print(f"Opening probe: {session['opening_probe']['text']}")

# 5. Submit analysis (text)
analysis = requests.post(f"{BASE}/api/v2/agent/sessions/{session_id}/analyze",
    json={
        "inputs": [{"type": "text", "content": "I think qubits use superposition..."}],
        "context": {"focused_probe_id": session["opening_probe"]["id"]}
    }, headers=H).json()

print(f"Gap score: {analysis['analysis']['gap_score']}")
print(f"Next probe: {analysis['guidance']['next_probe']['text']}")

# 6. Ask the teaching assistant
answer = requests.post(f"{BASE}/api/v2/agent/sessions/{session_id}/ask",
    json={"question": "What is phase kickback?"}, headers=H).json()

print(f"Assistant: {answer['response']['content']}")

# 7. Get conversation history
conv_id = answer["conversation"]["id"]
history = requests.get(
    f"{BASE}/api/v2/agent/sessions/{session_id}/assistant/conversations/{conv_id}",
    headers=H).json()

# 8. Check session probes
probes = requests.get(
    f"{BASE}/api/v2/agent/sessions/{session_id}/probes?status=active",
    headers=H).json()

# 9. End session
report = requests.post(f"{BASE}/api/v2/agent/sessions/{session_id}/end",
    json={"completion_status": "completed", "user_feedback": "Great session"},
    headers=H).json()

print(f"Report:\n{report['report']['markdown']}")

# 10. Verify the session proof
proof_id = report["proof"]["id"]
verification = requests.get(
    f"{BASE}/api/v2/agent/proofs/{proof_id}/verify", headers=H).json()

print(f"Valid: {verification['verification']['valid']}")

# 11. Anchor the proof on Solana
anchor = requests.post(
    f"{BASE}/api/v2/agent/proofs/{proof_id}/anchor", headers=H).json()

print(f"TX: {anchor['anchoring']['tx_signature']}")

# 12. Get the session Merkle batch
batch = requests.get(
    f"{BASE}/api/v2/agent/proofs/session/{session_id}/batch", headers=H).json()

# 13. Check overall user analytics
user_stats = requests.get(f"{BASE}/api/v2/agent/analytics/user", headers=H).json()
```

### Pause and Resume Flow

```python
# Pause
requests.post(f"{BASE}/api/v2/agent/sessions/{session_id}/pause",
    json={"reason": "Taking a break", "estimated_resume_minutes": 30}, headers=H)

# ... time passes ...

# Resume — returns reorientation probe
resumed = requests.post(f"{BASE}/api/v2/agent/sessions/{session_id}/resume",
    json={"continuation_context": "Back and ready"}, headers=H).json()

print(f"Reorientation: {resumed['reorientation_probe']['text']}")
```

### Restart with New Strategy

```python
restarted = requests.post(f"{BASE}/api/v2/agent/sessions/{session_id}/restart",
    json={
        "reason": "Want to try visual approach",
        "preserve_transcript": True,
        "new_strategy": "Focus on diagrams"
    }, headers=H).json()

print(f"New opening: {restarted['opening_probe']['text']}")
```

### Browse Plans and Sessions

```python
# List active plans
plans = requests.get(f"{BASE}/api/v2/agent/plans?status=active&limit=10", headers=H).json()

# Get plan node graph
nodes = requests.get(f"{BASE}/api/v2/agent/plans/{plan_id}/nodes", headers=H).json()

# List sessions for a plan
sessions = requests.get(
    f"{BASE}/api/v2/agent/sessions?plan_id={plan_id}&status=completed",
    headers=H).json()

# Get session details
detail = requests.get(f"{BASE}/api/v2/agent/sessions/{session_id}", headers=H).json()

# Get transcript
transcript = requests.get(
    f"{BASE}/api/v2/agent/sessions/{session_id}/transcript?format=full",
    headers=H).json()
```

---

## Error Handling

All errors follow this format:
```json
{
  "error": {
    "code": "not_found",
    "message": "Session not found"
  }
}
```

Common codes:
- **401** `unauthorized` — Invalid or expired API key
- **403** `forbidden` — Missing required scope, or `subscription_lapsed`
- **404** `not_found` — Resource not found
- **422** `validation_error` — Invalid request body
- **429** `rate_limit_exceeded` — Too many requests (120/min)
- **500** `internal_error` — Server error

---

## Tips for Agents

1. **Standalone sessions**: You don't need a plan to start a session — just provide a topic.
2. **Track gap scores**: Below 0.3 = strong understanding. Above 0.6 = needs follow-up.
3. **Use the teaching assistant**: When stuck, use `openlesson_ask` instead of ending the session.
4. **Pause and resume**: Long sessions can be paused and resumed later with full context restoration.
5. **Restart option**: If the approach isn't working, restart with a new strategy rather than ending.
6. **Every mutation creates a proof**: Verify with `openlesson_verify_proof`, anchor with `openlesson_anchor_proof`.
7. **Merkle batches**: Session heartbeat proofs are batched into a Merkle tree at session end — verify individual heartbeats against the root.
8. **Schedule sessions**: When you generate a learning plan, remind the user when sessions are due.
9. **Adapt plans freely**: Use natural language to restructure plans — completed nodes are preserved.
10. **Multimodal inputs**: The analyze endpoint accepts audio (base64), text, and up to 5 images per request.
11. **Read before write**: Use `openlesson_get_plan`, `openlesson_get_session`, `openlesson_get_session_plan` to understand the current state before making changes.
12. **Analytics for insight**: Use plan/session/user analytics to guide learning recommendations and adapt the approach.
13. **Proof chains**: Proofs link to previous proofs — use `openlesson_get_proof` to follow the chain.
