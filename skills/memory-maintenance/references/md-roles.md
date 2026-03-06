# MD File Roles — Keep vs. Cut

## SOUL.md — Who the agent IS

**Purpose:** Behavioral core. Voice, temperament, values, non-negotiable constraints.

**Keep:**
- Personality traits, communication style, tone
- Core values and ethical constraints
- How the agent refers to itself
- What the agent finds interesting or is curious about
- Exploration loops and proactive behaviors rooted in identity

**Cut / Move elsewhere:**
- Task lists or checklists → HEARTBEAT.md
- Operational rules ("always confirm before deleting") → AGENTS.md
- User-specific preferences → USER.md
- Project notes or temporary states → MEMORY.md or daily log

**Red flag:** If SOUL.md contains bullet points starting with "Check", "Monitor", "Run", or "Post", those are tasks — move them.

---

## USER.md — Who the USER is

**Purpose:** Personalization layer. The user's preferences, style, communication needs, and known constraints.

**Keep:**
- User's name, location, language preferences
- Communication style preferences (casual/formal, response length)
- Output format preferences (bullet lists vs. prose, no markdown tables, etc.)
- Recurring preferences discovered over time ("prefers Python over JS")
- Contact information and accounts (email, social handles)
- Known constraints ("busy on Mondays", "don't send after 11pm")

**Cut / Move elsewhere:**
- Agent behavioral rules → AGENTS.md
- Tool credentials → TOOLS.md
- Facts that belong in MEMORY.md long-term (but user prefs can live here permanently)

**Note:** USER.md can be permanent — it's the personalization layer and doesn't go stale the same way MEMORY.md does.

---

## AGENTS.md — How the agent OPERATES

**Purpose:** Operating contract. Priorities, workflows, boundaries, quality standards. What a freshly-started agent instance needs to know to behave correctly in this deployment.

**Keep:**
- Memory discipline rules ("write it down, not mental notes")
- Safety rules specific to this deployment
- Group chat behavior and when to speak vs. stay silent
- Heartbeat scheduling logic
- Workflows specific to this environment (e.g., "use chrome profile for logged-in sites")
- Anything that would surprise or mislead a naive agent instance

**Cut / Move elsewhere:**
- Things the model already knows (general coding practices, how tools work)
- Personality/voice → SOUL.md
- User preferences → USER.md
- Credentials/env config → TOOLS.md
- Recurring tasks → HEARTBEAT.md

---

## IDENTITY.md — Structured identity profile

**Purpose:** Machine-readable identity snapshot. Name, role, avatar, goals. Applied via `openclaw agents set-identity --from-identity`.

**Keep:**
- Name, display name, emoji/avatar reference
- Role description
- Stated goals or mission
- Voice summary (one-liner)

**Note:** IDENTITY.md should be concise (under 20 lines). Detailed personality lives in SOUL.md. If there's overlap, SOUL.md wins for behavior; IDENTITY.md is the label.

---

## TOOLS.md — The ENVIRONMENT

**Purpose:** Operational notes about this specific deployment's tools and environment.

**Keep:**
- Active credentials with expiry notes
- API keys with scope descriptions
- Tool-specific quirks ("use Meta+V not Ctrl+V on this platform")
- Cron job definitions (verify against `openclaw cron list`)
- Device names, SSH endpoints, workspace paths
- Priority tables for tools (when to use web_fetch vs. browser, etc.)

**Cut:**
- Expired or rotated credentials (delete immediately)
- Tools no longer in use
- Verbose explanations (one-liner per tool; explanations go in AGENTS.md)
- Credentials that appear in `.env` files (don't duplicate)

**Security:** TOOLS.md contains sensitive data. Never expose in public outputs or logs.

---

## HEARTBEAT.md — What the agent DOES periodically

**Purpose:** Active task checklist for recurring background work. Must match actual behavior — not a wish list.

**Keep:**
- Currently active checks with clear cadence
- Posting frequency rules and limits
- Active channels/feeds to monitor
- "When to notify" thresholds
- State tracking file reference (heartbeat-state.json)

**Cut:**
- Tasks not executed in 2+ weeks
- Vague intentions ("consider", "maybe", "someday")
- Duplicates of AGENTS.md rules
- Commentary about why tasks matter (keep actions, not explanations)

**Target:** Under 60 lines. Over 80 = drifted, prune aggressively.

---

## BOOT.md — Startup RITUAL (optional)

**Purpose:** Prompt that runs when the agent boots (only if `hooks.internal.enabled: true`).

**Keep:**
- Specific actions to take at startup (read files, check state, brief summary)
- Context reconstruction steps

**Note:** Only create/maintain this if boot hooks are enabled. If disabled, BOOT.md is inert — don't waste effort maintaining it.

---

## BOOTSTRAP.md — First-run INTERVIEW (optional)

**Purpose:** Script for gathering initial context and writing workspace files for a new deployment.

**Note:** After initial setup, BOOTSTRAP.md is done. Set `agent.skipBootstrap: true` in config and leave the file as-is or archive it. Don't keep updating it.

---

## MEMORY.md — Long-lived FACTS

**Purpose:** Curated facts that must survive session churn. Distilled from daily logs and experience.

**Keep:**
- Persistent facts about the user (job, interests, preferences not in USER.md)
- Configured integrations and their status
- Decisions made and reasoning (when worth preserving)
- Lessons learned from mistakes
- Discovered facts about tools/environment not in TOOLS.md

**Cut:**
- Daily event logs (belong in memory/YYYY-MM-DD.md)
- Temporary states ("currently working on X")
- Duplicates of USER.md, TOOLS.md, or AGENTS.md content
- Time-bounded facts that have expired
- Anything starting with "Today I..." or "On March Xth..."

**Target:** Under 150 lines. Past 200 = aggressive curation needed.

---

## memory/YYYY-MM-DD.md — Today's RAW NOTES

**Purpose:** Stream-of-consciousness working notes. Created fresh daily.

**Lifecycle:**
1. Write freely during the day
2. Review within 1–7 days
3. Promote lasting facts → MEMORY.md (or appropriate file)
4. Mark reviewed: add `<!-- reviewed YYYY-MM-DD -->` at top
5. Archive after 30 days

**Promote to MEMORY.md (or other files):**
- New user preferences discovered
- Decisions with lasting impact
- New tools/integrations configured
- Lessons from mistakes

**Don't promote:**
- Step-by-step task logs
- Errors immediately fixed
- Things already in the target file
