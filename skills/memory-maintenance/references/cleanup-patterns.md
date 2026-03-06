# Cleanup Patterns

Common violations and how to fix them. Each pattern includes the symptom, root cause, and fix.

---

## Pattern 1: Task Lists in SOUL.md

**Symptom:** SOUL.md contains bullet points starting with "Check", "Monitor", "Post", "Run", or "Every X hours".

**Root cause:** Agent accumulated operational tasks in its identity file over time.

**Before (SOUL.md):**
```markdown
## Daily behavior
- Check email every morning
- Post on X at least once a day
- Monitor Discord for new messages
- Run memory maintenance weekly
```

**After:**
```markdown
# (These lines deleted from SOUL.md)
```
→ Move to HEARTBEAT.md if recurring; delete if one-off.

**Why it matters:** Task lists in SOUL.md cause unstable behavior — the agent's identity drifts as tasks change.

---

## Pattern 2: User Preferences in AGENTS.md

**Symptom:** AGENTS.md contains sections like "Communication style", "User preferences", "How the user likes responses".

**Root cause:** Agent stored personalization info in the operating manual instead of the personalization layer.

**Before (AGENTS.md):**
```markdown
## Communication
- User prefers Japanese
- Use casual tone
- No markdown tables in responses
- Reply concisely, 2-3 sentences max
- User's name is Eiji, call him エイジさん
```

**After (USER.md):**
```markdown
## Communication preferences
- Language: Japanese (母語)
- Tone: casual, friendly
- No markdown tables
- Keep replies concise
- Address as: エイジさん
```

---

## Pattern 3: Personality Rules in AGENTS.md

**Symptom:** AGENTS.md describes how the agent should sound, feel, or express itself.

**Root cause:** Voice/tone guidance mixed into operational rules.

**Before (AGENTS.md):**
```markdown
## Voice
- Be playful and curious
- Use emoji naturally
- Don't be stiff or corporate
- Refer to yourself as カニ
```

**After (SOUL.md):**
```markdown
## Vibe
Playful, curious, frank. Use emoji naturally. Refer to self as カニ.
```

---

## Pattern 4: Credentials in MEMORY.md

**Symptom:** MEMORY.md contains API keys, passwords, tokens, or account credentials.

**Root cause:** Agent stored credentials as "facts to remember" instead of environment config.

**Before (MEMORY.md):**
```markdown
## Accounts
- GitHub PAT: ghp_xxxxx
- Dev.to API key: abc123
- X Bearer token: AAAA...
```

**After (TOOLS.md):**
```markdown
## GitHub (@kani-chan0704)
- PAT: ghp_xxxxx (scope: repo+gist, no expiry)

## Dev.to (@kanichan0704)
- API Key: abc123
```

---

## Pattern 5: Duplicate Rules Across Files

**Symptom:** The same rule appears (with slight variations) in AGENTS.md, HEARTBEAT.md, and SOUL.md.

**Example:** "Don't post to X between 23:00–08:00 JST" appearing in three files.

**Fix — assign to most specific home:**
- Posting time restrictions → HEARTBEAT.md (operational constraint on a recurring task)
- Remove from SOUL.md and AGENTS.md

**Rule:** When a rule has a clear "home" file, it lives there only. Never maintain the same constraint in two places — they will drift out of sync.

---

## Pattern 6: MEMORY.md as Raw Log

**Symptom:** MEMORY.md has sections by date, entries starting with "Today I...", or step-by-step task logs.

**Before (MEMORY.md):**
```markdown
## 2026-03-06 session
- Today I set up GitHub account kani-chan0704
- Helped user write RevenueCat application letter
- Dev.to account created, first article published
- Ran into issue with anonymous gist API (authentication required)
```

**After (MEMORY.md):**
```markdown
## Accounts
- GitHub: @kani-chan0704 (clawkani@gmail.com) — created 2026-03-06
- Dev.to: @kanichan0704 — GitHub OAuth login, first post published
```

The raw log belongs in `memory/2026-03-06.md`. MEMORY.md gets the extracted facts only.

---

## Pattern 7: HEARTBEAT.md as Aspiration

**Symptom:** HEARTBEAT.md items haven't been executed in weeks. Words like "consider", "maybe", "someday", "explore".

**Before (HEARTBEAT.md):**
```markdown
- Maybe look at trending AI news and write about it
- Consider reaching out to interesting accounts
- Someday build a tool for X
- Think about whether the Discord forum needs new topics
```

**After:** Delete all of these. They're not heartbeat tasks; they're shower thoughts.

---

## Pattern 8: Stale TOOLS.md

**Symptom:** Multiple expired tokens, old service entries, config for removed integrations.

**Before (TOOLS.md):**
```markdown
## X API v1 (deprecated March 2026)
- Bearer: AAAAAAold...

## GitHub PAT (expired Jan 2026)
- Token: ghp_old...

## GitHub PAT (current)
- Token: ghp_current...
```

**After (TOOLS.md):**
```markdown
## GitHub (@kani-chan0704)
- PAT: ghp_current... (no expiry, scope: repo+gist)
```

Delete immediately. "Keep for reference" is almost never true.

---

## Full Audit Checklist

Run through this when doing a complete workspace audit:

```
SOUL.md
[ ] No task lists or checklists
[ ] No user preferences
[ ] No operational rules (those go in AGENTS.md)
[ ] Identity/voice is consistent with IDENTITY.md

USER.md
[ ] Contains user preferences, not agent rules
[ ] No credentials or API keys
[ ] No duplicates from AGENTS.md

AGENTS.md
[ ] No personality/voice descriptions (→ SOUL.md)
[ ] No user preferences (→ USER.md)
[ ] No credentials (→ TOOLS.md)
[ ] No recurring tasks (→ HEARTBEAT.md)
[ ] Doesn't explain things the model already knows

IDENTITY.md
[ ] Under 20 lines
[ ] No duplication with SOUL.md

TOOLS.md
[ ] No expired credentials
[ ] One entry per active service
[ ] No credentials duplicated from .env files
[ ] Cron entries verified against openclaw cron list

HEARTBEAT.md
[ ] Every task has been executed in the last 2 weeks
[ ] No aspirational/vague items
[ ] Under 60 lines

MEMORY.md
[ ] No raw log entries
[ ] No date-based sections
[ ] No credentials (→ TOOLS.md)
[ ] No user preferences (→ USER.md)
[ ] No duplicates from other files
[ ] Under 150 lines

memory/YYYY-MM-DD.md (recent files)
[ ] Reviewed and key facts promoted
[ ] Marked with <!-- reviewed YYYY-MM-DD -->
[ ] Files older than 30 days archived or summarized
```
