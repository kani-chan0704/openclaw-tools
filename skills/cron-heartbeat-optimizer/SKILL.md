---
name: cron-heartbeat-optimizer
description: Audit and optimize the split between cron jobs and HEARTBEAT.md tasks. Detects misplaced tasks (e.g., exact-timing tasks in heartbeat, batchable checks as separate cron jobs), redundancies, and violations of the cron-vs-heartbeat policy. Use when: (1) setting up automation for the first time, (2) the agent has accumulated many cron jobs and HEARTBEAT.md tasks over time, (3) scheduled tasks feel slow, expensive, or duplicated, (4) asked to "audit", "optimize", or "clean up" scheduled tasks. Can be registered as a recurring cron job for ongoing hygiene. See references/policy.md for the complete decision policy.
---

# Cron / Heartbeat Optimizer

Cron and heartbeat solve different problems. When tasks end up in the wrong mechanism, the agent becomes slower, more expensive, and harder to reason about. This skill audits both and realigns them.

## Core Decision Rule (run this for every task)

```
Does the task need to run at an EXACT time?
  YES → Cron (isolated or main)

Does the task need isolation from main session history?
  YES → Cron (isolated)

Can this task be batched with other periodic checks?
  YES → Heartbeat (add to HEARTBEAT.md)

Is this a one-shot reminder?
  YES → Cron with --at --delete-after-run

Does it need a different model or thinking level?
  YES → Cron (isolated) with --model

Otherwise:
  → Heartbeat
```

Full policy with examples: `references/policy.md`

## Audit Workflow

### Step 1: Collect current state

```bash
# List all active cron jobs
openclaw cron list

# Read the heartbeat checklist
cat HEARTBEAT.md
```

### Step 2: Run the audit script

```bash
python scripts/audit.py --cron-list "$(openclaw cron list --json)" --heartbeat HEARTBEAT.md
```

The script outputs a structured report: misplacements, redundancies, and recommendations.

### Step 3: Apply fixes

For each finding, apply the recommended fix:

**Move heartbeat task → cron:**
```bash
openclaw cron add \
  --name "<task name>" \
  --cron "<schedule>" \
  --session isolated \
  --message "<task description>" \
  --announce
```
Then remove the task from HEARTBEAT.md.

**Move cron job → heartbeat:**
Add a one-liner to HEARTBEAT.md under the appropriate section.
Then: `openclaw cron delete <job-id>`

**Merge duplicate cron jobs:**
Keep the most specific one, delete the others.

**Remove stale cron jobs:**
```bash
openclaw cron delete <job-id>
```

### Step 4: Confirm before deleting

Summarize planned deletions and get user confirmation before running `openclaw cron delete`.

### Step 5: Schedule this skill as a recurring audit

Register this audit to run automatically (recommended: weekly):

```bash
openclaw cron add \
  --name "cron-heartbeat-audit" \
  --cron "0 3 * * 1" \
  --session isolated \
  --message "Run the cron-heartbeat-optimizer skill. Audit current cron jobs and HEARTBEAT.md. Report findings, suggest fixes, ask for confirmation before making changes." \
  --announce
```

## Common Violations

| Violation | Symptom | Fix |
|-----------|---------|-----|
| Timing-sensitive task in heartbeat | Task needs to run at 9AM exactly but is in HEARTBEAT.md | Move to cron |
| Batchable checks as separate crons | 4 cron jobs all running every 30 min | Merge into heartbeat |
| One-shot reminder in HEARTBEAT.md | "Check X" that was done once, never removed | Delete from HEARTBEAT.md |
| Heavy analysis in heartbeat | Heartbeat turns take >60s due to one big task | Move to isolated cron with --model |
| Duplicate coverage | Same check in both cron and heartbeat | Keep one, delete other |
| Dead cron jobs | Cron job for a service that no longer exists | Delete |

See `references/policy.md` for detailed guidance on each case.
