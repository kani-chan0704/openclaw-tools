# MD File Roles — Detailed Guide

## MEMORY.md

**Role:** Curated long-term memory. The distilled essence of everything the agent has learned that should survive session restarts.

**Keep:**
- Persistent personal facts about the user (job, preferences, communication style)
- Configured integrations and their status (APIs, calendars, bots)
- Decisions made and the reasoning behind them
- Lessons learned from past mistakes
- Account/tool info that isn't in TOOLS.md

**Cut:**
- Daily event logs (those belong in `memory/YYYY-MM-DD.md`)
- Temporary states ("currently working on X" — unless it spans weeks)
- Duplicates of what's in TOOLS.md or AGENTS.md
- Time-bounded facts that have expired ("event on March 3rd")
- Anything that starts with "Today I..."

**Structure:**
Group by theme (e.g., "About the User", "Configured Tools", "Lessons Learned"). Use short, declarative sentences. One fact per line where possible.

---

## AGENTS.md

**Role:** Behavioral operating manual. Rules, conventions, and workflows specific to this agent's environment that a freshly-started instance would need.

**Keep:**
- Memory write discipline rules ("write it down, don't mental note")
- Safety rules specific to this deployment
- Group chat behavior rules
- Heartbeat scheduling logic
- Anything that would surprise a naive agent instance

**Cut:**
- Things the model already knows (general coding conventions, how to use tools)
- Duplicates of SOUL.md personality rules
- Outdated workflows that have been replaced
- "Nice to have" suggestions that aren't actually followed

---

## SOUL.md

**Role:** Identity, tone, values, and core personality. The "who am I" file.

**Touch only when explicitly instructed by the user.** Never silently modify SOUL.md during maintenance. It defines the agent's fundamental character.

**If SOUL.md grows bloated:** flag it to the user, do not self-edit.

---

## HEARTBEAT.md

**Role:** Active task checklist for periodic background work. Should be short, executable, and reflect what the agent *actually does* — not an aspirational list.

**Keep:**
- Currently active checks (email, calendar, social feeds)
- Posting frequency rules and limits
- Active Discord/forum channels to monitor
- Clear thresholds for "when to notify" vs. "stay quiet"

**Cut:**
- Tasks that haven't been executed in 2+ weeks
- Vague intentions ("check interesting things")
- Duplicates of rules already in AGENTS.md
- Commentary explaining why tasks matter (move to AGENTS.md if truly needed)

**Red flag:** If HEARTBEAT.md is over 80 lines, it has drifted. Prune aggressively.

---

## TOOLS.md

**Role:** Environment-specific config: credentials, API keys, device names, cron jobs, known endpoints.

**Keep:**
- Active credentials with expiry notes
- Tool-specific quirks ("use Meta+V not Ctrl+V for X.com")
- Cron job definitions that match actual scheduled jobs
- Workspace access patterns (priority table, etc.)

**Cut:**
- Expired or rotated credentials
- Tools no longer in use
- Verbose explanations that belong in AGENTS.md
- Duplicate credentials that appear in `.env` files

**Security note:** TOOLS.md may contain sensitive data. Never include it in public outputs.

---

## memory/YYYY-MM-DD.md

**Role:** Daily raw log. Stream-of-consciousness notes from the day's sessions.

**Lifecycle:**
1. Created fresh each day
2. Written to throughout the day (events, decisions, errors, observations)
3. **Reviewed within 1–7 days**: key facts promoted to MEMORY.md
4. **Archived after review**: keep for 30 days, then can be summarized or deleted

**Do NOT promote to MEMORY.md:**
- Step-by-step task logs (just noise)
- Errors that were immediately fixed
- Things already in MEMORY.md

**DO promote:**
- New user preferences discovered
- Decisions with lasting impact
- New tools/APIs configured
- Lessons from mistakes
- Interesting facts about the user's world

---

## memory/heartbeat-state.json

**Role:** Lightweight state tracker for heartbeat checks.

**Keep current:**
- `lastChecks`: timestamps for each periodic check
- `last_tweet_id` / `last_tweet_time_utc`: prevents duplicate posts
- `discord_last_activity`: tracks last seen message ID per channel
- `chiikawa_last_seen_id`: or equivalent content trackers

**Never store:** secrets, full message content, or anything that grows unboundedly.
