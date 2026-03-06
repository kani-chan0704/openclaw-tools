---
name: memory-maintenance
description: Periodically review and compact OpenClaw workspace MD files to keep them organized, non-redundant, and efficiently sized. Use when: (1) workspace files have grown bloated or repetitive, (2) MEMORY.md contains outdated or stale entries, (3) daily memory logs need review and key facts promoted to long-term memory, (4) HEARTBEAT.md has drifted from actual agent behavior, (5) TOOLS.md or AGENTS.md contains redundant or superseded information, (6) agent is asked to "clean up", "organize", or "tidy" its workspace files. NOT for: deleting files the user created, restructuring the entire workspace, or modifying SOUL.md values without explicit user instruction.
---

# Memory Maintenance

OpenClaw agents accumulate workspace state across sessions. Without periodic curation, MDfiles drift: MEMORY.md grows stale, HEARTBEAT.md becomes aspirational rather than operational, TOOLS.md accumulates dead config. This skill keeps them lean and trustworthy.

## File Roles (Quick Reference)

| File | Purpose | Key question |
|------|---------|--------------|
| `MEMORY.md` | Long-term curated facts | "Still true? Still relevant?" |
| `AGENTS.md` | Behavioral rules & conventions | "Still followed? Duplicated elsewhere?" |
| `SOUL.md` | Identity, tone, values | "Touch only if explicitly asked" |
| `HEARTBEAT.md` | Active task checklist | "Executable today? Not a wish list?" |
| `TOOLS.md` | Env notes, credentials, config | "Still valid? Credentials rotated?" |
| `memory/YYYY-MM-DD.md` | Daily raw logs | "Promote key facts → MEMORY.md, then archive" |

See `references/md-roles.md` for detailed per-file rules and what to keep vs. cut.

## Maintenance Workflow

### 1. Assess before acting

Read each target file. Note:
- **Staleness**: facts that are no longer true (old credentials, closed projects, outdated plans)
- **Redundancy**: same information in multiple files
- **Bloat**: verbose logs where a one-liner summary suffices
- **Drift**: rules in AGENTS.md or tasks in HEARTBEAT.md that don't reflect actual behavior

### 2. Promote daily logs → MEMORY.md

For each recent `memory/YYYY-MM-DD.md` not yet reviewed:
- Extract facts worth remembering long-term (decisions made, lessons learned, preferences revealed, new tools configured)
- Add to appropriate MEMORY.md section with a single clear sentence per fact
- Skip: task logs, error traces, intermediate steps, things already in MEMORY.md

### 3. Compact MEMORY.md

- Merge related facts into single entries where possible
- Remove entries that are superseded, no longer actionable, or time-bounded and expired
- Keep personal context, persistent preferences, configured integrations, and lessons learned
- Target: under 150 lines. If growing past 200, aggressive curation is needed.

### 4. Prune HEARTBEAT.md

HEARTBEAT.md should be a short, executable checklist — not an aspirational doc.
- Remove tasks the agent no longer does in practice
- Collapse verbose check descriptions into terse one-liners
- Verify all referenced channels/IDs/URLs are still active
- Target: under 60 lines

### 5. Audit TOOLS.md

- Flag or remove expired credentials/tokens (check `expiry_date` fields)
- Remove config for tools no longer in use
- Ensure cron job entries match actual `openclaw cron list` output
- One entry per tool — no paragraph-length explanations

### 6. Trim AGENTS.md

- Remove rules that duplicate SOUL.md or HEARTBEAT.md
- Consolidate redundant bullet points
- Keep: conventions specific to this agent's environment that another instance wouldn't know

### 7. Confirm before deleting

Never silently delete content the user may want. When removing more than a few lines from any file:
- Summarize what will be removed and why
- Ask for confirmation if the removal is significant (>10 lines) or irreversible

See `references/cleanup-patterns.md` for common patterns and example transformations.

## Scheduling

Run this skill:
- **Weekly** (during a heartbeat): promote daily logs, quick MEMORY.md pass
- **Monthly**: full audit of all files
- **On demand**: when files feel sluggish or out of date

Track last maintenance in `memory/heartbeat-state.json`:
```json
{
  "lastChecks": {
    "memory_maintenance": 1234567890
  }
}
```
