---
name: memory-maintenance
description: Review and reorganize OpenClaw workspace files so every piece of information lives in exactly one correct place, with no redundancy. Covers all workspace files: SOUL.md, USER.md, AGENTS.md, IDENTITY.md, TOOLS.md, HEARTBEAT.md, BOOT.md, MEMORY.md, and daily memory logs. Use when: (1) workspace files have grown bloated or contradictory, (2) the same information appears in multiple files, (3) MEMORY.md contains stale entries or raw logs, (4) HEARTBEAT.md has drifted from actual behavior, (5) information feels like it's in the wrong file, (6) agent is asked to "clean up", "reorganize", or "audit" its workspace. NOT for: modifying SOUL.md values without explicit instruction, deleting user-created content without confirmation, or restructuring the entire workspace without user approval.
---

# Memory Maintenance

Every piece of information in an OpenClaw workspace belongs in exactly one file. When files drift — SOUL.md accumulates task lists, AGENTS.md fills with user preferences, MEMORY.md becomes a raw log — the agent becomes inconsistent and expensive to run. This skill fixes that.

## The File Map (One-Line Each)

| File | One job |
|------|---------|
| `SOUL.md` | Who the agent *is*: voice, values, temperament, ethics |
| `USER.md` | Who the *user* is: preferences, style, communication defaults |
| `AGENTS.md` | How the agent *operates*: rules, workflows, boundaries |
| `IDENTITY.md` | Structured identity profile (name, role, avatar, goals) |
| `TOOLS.md` | *Environment* config: credentials, endpoints, tool quirks |
| `HEARTBEAT.md` | *Recurring* tasks the agent actively executes |
| `BOOT.md` | *Startup* ritual (optional; only if hooks are enabled) |
| `BOOTSTRAP.md` | First-run interview script (skip after initial setup) |
| `MEMORY.md` | Long-lived *facts* worth surviving session churn |
| `memory/YYYY-MM-DD.md` | Today's raw working notes |

See `references/md-roles.md` for keep/cut rules per file.

## Where Does This Information Belong?

When you find a piece of information and don't know where it lives, use this decision tree:

```
Is it about the agent's personality, ethics, or voice?
  YES → SOUL.md

Is it about the user's preferences, style, or communication needs?
  YES → USER.md

Is it a structured fact about the agent's identity (name, avatar, role)?
  YES → IDENTITY.md

Is it a behavioral rule, workflow, or operational boundary?
  YES → AGENTS.md

Is it a tool credential, endpoint URL, cron job, or environment quirk?
  YES → TOOLS.md

Is it a task the agent runs on a recurring cadence?
  YES → HEARTBEAT.md

Is it a startup ritual or hook?
  YES → BOOT.md

Is it a durable fact worth remembering across sessions?
  YES → MEMORY.md

Is it a raw note from today's work?
  YES → memory/YYYY-MM-DD.md
```

If a piece of information fits more than one category, it belongs in the *most specific* file and should be removed from all others.

## Maintenance Workflow

### Step 1: Map before moving

Read all files first. Build a mental (or actual) inventory:
- What information is duplicated across files?
- What's in the wrong place (SOUL.md task lists, AGENTS.md user prefs, etc.)?
- What's stale (expired creds, completed projects, outdated rules)?

### Step 2: Fix misplaced information

Common violations (see `references/cleanup-patterns.md` for before/after examples):

- **Task lists in SOUL.md** → Move to HEARTBEAT.md (recurring tasks) or delete (one-offs)
- **User preferences in AGENTS.md** → Move to USER.md
- **Credentials in MEMORY.md** → Move to TOOLS.md
- **Personality/voice rules in AGENTS.md** → Move to SOUL.md
- **Raw log entries in MEMORY.md** → Compress to one-line facts or delete
- **Duplicate rules across files** → Keep in most specific file, remove elsewhere

### Step 3: Compact MEMORY.md

- Extract facts from recent `memory/YYYY-MM-DD.md` files not yet promoted
- One fact, one line — no event logs, no "today I..." entries
- Remove entries that are expired, superseded, or already in another file
- Target: under 150 lines; aggressive curation needed past 200

### Step 4: Prune HEARTBEAT.md

- Only include tasks the agent *actually executes* on a regular cadence
- Remove aspirational items, vague intentions, tasks not run in 2+ weeks
- Target: under 60 lines

### Step 5: Audit TOOLS.md

- Remove expired credentials and rotate notes
- Verify cron entries match `openclaw cron list` output
- One entry per tool — no lengthy explanations (those go in AGENTS.md)

### Step 6: Confirm before removing

When removing more than ~10 lines from any file, summarize and confirm first. Silently deleting content the user values is worse than leaving it.

### Step 7: Update daily log

Record what was changed and why in today's `memory/YYYY-MM-DD.md`.

## Scheduling

| Cadence | Scope |
|---------|-------|
| Weekly (heartbeat) | Promote daily logs → MEMORY.md; quick MEMORY.md pass |
| Monthly | Full audit of all files; fix misplacements |
| On-demand | Whenever files feel wrong or redundant |

Track in `memory/heartbeat-state.json`:
```json
{ "lastChecks": { "memory_maintenance": 1234567890 } }
```
