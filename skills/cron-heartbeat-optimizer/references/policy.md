# Cron vs Heartbeat Policy

*Based on the official OpenClaw documentation: https://docs.openclaw.ai/automation/cron-vs-heartbeat*

---

## What Each Mechanism Is For

### Heartbeat — Periodic Awareness

Heartbeats run in the **main session** at a regular interval (default: 30 min). The agent reads HEARTBEAT.md and handles all listed checks in a single turn.

**Use heartbeat when:**
- Multiple periodic checks can be batched together (inbox + calendar + notifications in one turn)
- The task benefits from main-session context (recent conversation, user state)
- Timing can drift slightly — "approximately every 30 minutes" is fine
- The overhead of an isolated session isn't justified
- You want to reduce API calls by combining checks

**Heartbeat advantages:**
- One turn replaces many small polling tasks
- Smart suppression: if nothing needs attention, replies `HEARTBEAT_OK` — no message delivered
- Context-aware: the agent knows what you've been working on
- Cheaper: one batch call instead of N isolated sessions

---

### Cron — Precise Scheduling

Cron jobs run at exact times and can run in isolated sessions without affecting main context. Jobs persist at `~/.openclaw/cron/jobs.json`.

**Use cron when:**
- Exact timing is required ("9:00 AM sharp every Monday" — not "sometime around 9")
- The task needs isolation from main session history
- The task needs a different model or thinking level
- The task is a one-shot reminder (`--at`, `--delete-after-run`)
- The task would generate noisy output that shouldn't clutter main session
- The task should run even if main session is idle or compacted

**Cron execution modes:**
- `--session main`: enqueues a system event, runs on next heartbeat → use for things that need main context but at a specific time
- `--session isolated`: runs a dedicated `cron:<jobId>` turn → use for standalone tasks

---

## Decision Table (Quick Reference)

| Scenario | Recommended | Reason |
|----------|-------------|--------|
| Check inbox every 30 min | Heartbeat | Batches with other checks |
| Send daily report at 9AM sharp | Cron (isolated) | Exact timing + standalone |
| Monitor calendar for upcoming events | Heartbeat | Contextual awareness |
| Run weekly deep analysis | Cron (isolated, --model) | Standalone, needs better model |
| Remind me in 20 minutes | Cron (--at --delete-after-run) | One-shot precise |
| Background project health check | Heartbeat | Piggybacks on existing cycle |
| Post a scheduled message at exact time | Cron (isolated, --announce) | Exact timing + delivery |
| Check if a process finished | Heartbeat | Contextual, batches naturally |
| Heavy data processing | Cron (isolated, --model) | Doesn't pollute main context |

---

## Anti-Patterns to Flag

### ❌ Exact-timing tasks in HEARTBEAT.md

**Symptom:** HEARTBEAT.md says "Check X at 9AM" or "Send Y on Mondays"

**Problem:** Heartbeat timing drifts. "Around 9" is not "9:00:00".

**Fix:** Move to `openclaw cron add --cron "0 9 * * 1" --session isolated`

---

### ❌ Multiple cron jobs for batchable checks

**Symptom:** Separate cron jobs for email, calendar, weather, notifications — all running every 30 minutes

**Problem:** 4 isolated sessions every 30 minutes = 4x cost, 4x context. All of these run better as one heartbeat.

**Fix:** Move all to HEARTBEAT.md, delete the cron jobs.

---

### ❌ One-shot items that were never removed

**Symptom:** HEARTBEAT.md contains items like "Check on project X" or "Follow up with person Y" that were completed but never removed.

**Problem:** Completed tasks still running in every heartbeat turn — wastes tokens, can confuse the agent.

**Fix:** Delete from HEARTBEAT.md.

---

### ❌ Heavy analysis in heartbeat

**Symptom:** Heartbeat turns take 60+ seconds because one task requires deep analysis or web research.

**Problem:** Blocks the heartbeat cycle, delays other checks, expensive main-session turns.

**Fix:** Move to isolated cron with `--model` override and `--announce` for delivery.

---

### ❌ Duplicate coverage

**Symptom:** The same check appears in both a cron job and HEARTBEAT.md.

**Problem:** Double execution, double cost. Results may conflict.

**Fix:** Decide which mechanism owns the task. Delete the other.

---

### ❌ Dead cron jobs

**Symptom:** Cron jobs for services, projects, or integrations that no longer exist.

**Problem:** Failed runs accumulate, clutter `cron list`, may cause errors.

**Fix:** `openclaw cron delete <job-id>`

---

## The Ideal Setup

**HEARTBEAT.md** (30-minute batched checks):
```markdown
- Scan inbox for urgent emails (skip if checked < 30 min ago)
- Check calendar for events in next 2h
- Check social feeds (X, Discord) for mentions
- Light check-in if idle 8+ hours
```

**Cron jobs** (precise timing, standalone tasks):
```
morning-briefing    0 8 * * *    isolated  → daily summary at 8AM
weekly-review       0 9 * * 1    isolated  → Monday morning analysis
healthcheck         0 3 * * 1    isolated  → weekly security audit
```

Everything that doesn't need exact timing or isolation → heartbeat.
Everything that does → cron.

---

## CLI Reference

```bash
# List current jobs
openclaw cron list
openclaw cron list --json

# Add a recurring isolated job
openclaw cron add \
  --name "task-name" \
  --cron "0 9 * * 1" \
  --tz "Asia/Tokyo" \
  --session isolated \
  --message "Do the task." \
  --announce

# Add a one-shot reminder
openclaw cron add \
  --name "reminder" \
  --at "20m" \
  --session main \
  --system-event "Reminder text here" \
  --wake now \
  --delete-after-run

# Delete a job
openclaw cron delete <job-id>

# View job run history
openclaw cron runs --id <job-id>
```
