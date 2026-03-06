# Cleanup Patterns

Common bloat patterns and how to fix them.

---

## Pattern 1: MEMORY.md as a Daily Log

**Symptom:** MEMORY.md entries start with "Today I...", "On March 3rd...", or describe one-off events.

**Before:**
```markdown
## March 3rd session
- Today I helped エイジさん search for Shinkansen tickets to Toyama
- We figured out that かがやき is faster than はくたか
- There was a bug with the browser evaluate tool but we fixed it
```

**After:**
```markdown
## Travel
- 東京→富山の新幹線: かがやき（2h〜2h20）が最速、はくたか（2h30〜）は停車駅多め
```

**Rule:** If it happened once and has no lasting relevance, cut it. If the *fact* learned is lasting, distill it to one line.

---

## Pattern 2: HEARTBEAT.md as a Wish List

**Symptom:** Tasks that sound aspirational but haven't been done in weeks. Words like "consider", "maybe", "someday".

**Before:**
```markdown
## Things to do
- Check email for important messages
- Maybe look at trending AI news and write about it
- Consider reaching out to interesting accounts
- Someday build a tool for X
- Think about whether the Discord forum needs new topics
```

**After:**
```markdown
## Active checks
- **Email**: scan for urgent unread (skip if checked <30min ago)
- **Discord forum**: check for replies; post new topic if 48h silent
```

**Rule:** Only keep tasks the agent *actually executes* on a regular cadence. Delete the rest.

---

## Pattern 3: Duplicated Rules Across Files

**Symptom:** The same rule appears in AGENTS.md, SOUL.md, and HEARTBEAT.md.

**Example:** "Don't post on X between 23:00–08:00" appearing in three places.

**Fix:** Pick the most appropriate home:
- SOUL.md → core values/identity rules
- HEARTBEAT.md → operational timing rules (keep this one here)
- AGENTS.md → behavioral conventions not covered elsewhere

Then remove duplicates from the other two.

---

## Pattern 4: TOOLS.md Credential Graveyard

**Symptom:** Multiple expired tokens, old API keys, credentials for services no longer used.

**Before:**
```markdown
## Old X API (deprecated)
- Bearer: AAAAAold...
- Note: replaced March 2026

## GitHub (kani-chan0704)
- PAT: ghp_xxxxx (expires Apr 2026)
- Old PAT: ghp_yyyyy (expired Jan 2026, keep for reference?)
```

**After:**
```markdown
## GitHub (@kani-chan0704)
- PAT: ghp_xxxxx (no expiry, scope: repo+gist) — GH_TOKEN env var
```

**Rule:** One active credential per service. Delete expired/superseded ones immediately.

---

## Pattern 5: AGENTS.md Explaining the Obvious

**Symptom:** Long paragraphs explaining things the model already knows (how git works, what JSON is, general coding best practices).

**Before:**
```markdown
## How to use the web_fetch tool
When you need to fetch content from the web, use the web_fetch tool. 
This tool takes a URL parameter and returns the content. You should 
use it for static pages. For dynamic pages with JavaScript you may 
need to use the browser tool instead. The browser tool supports...
```

**After (or deleted entirely if it's in TOOLS.md):**
```markdown
## Web access priority: web_fetch → browser(openclaw) → browser(chrome)
```

**Rule:** If the model already knows it, or if TOOLS.md has a clearer version, cut it.

---

## Pattern 6: Stale daily logs never promoted

**Symptom:** `memory/` folder has 30+ daily files, none reviewed, key facts never promoted to MEMORY.md.

**Fix:**
1. Read the last 7 days of daily logs
2. Extract facts worth keeping (1–3 per day on average)
3. Append to MEMORY.md under appropriate sections
4. Mark each daily file as "reviewed" with a note at the top: `<!-- reviewed YYYY-MM-DD -->`
5. Files older than 30 days: summarize if needed, then can be deleted

---

## Maintenance Checklist (Quick Run)

Copy this into a session note when running maintenance:

```
[ ] MEMORY.md: removed stale entries, merged duplicates
[ ] MEMORY.md: promoted facts from last N daily logs
[ ] HEARTBEAT.md: removed non-executed tasks, under 60 lines
[ ] TOOLS.md: removed expired credentials, verified cron entries
[ ] AGENTS.md: removed rules duplicated elsewhere
[ ] daily logs: reviewed and marked, old ones archived
[ ] heartbeat-state.json: updated memory_maintenance timestamp
```
