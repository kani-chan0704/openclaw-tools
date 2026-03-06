#!/usr/bin/env python3
"""
cron-heartbeat-optimizer: audit.py

Reads current cron jobs and HEARTBEAT.md, detects policy violations,
and prints a structured report with recommended fixes.

Usage:
  # Auto-discover from OpenClaw defaults
  python audit.py

  # Explicit paths
  python audit.py --heartbeat /path/to/HEARTBEAT.md

  # Pass cron JSON directly (from `openclaw cron list --json`)
  python audit.py --cron-json '{"jobs": [...]}'

Output: human-readable audit report to stdout.
"""

import argparse
import json
import os
import re
import subprocess
import sys

# ---------------------------------------------------------------------------
# Heuristics for classifying HEARTBEAT.md items
# ---------------------------------------------------------------------------

# Patterns that suggest a task belongs in cron, not heartbeat
TIMING_PATTERNS = [
    r'\b(every|each)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
    r'\b(at|@)\s*\d{1,2}(:\d{2})?\s*(am|pm|AM|PM|JST|UTC)?\b',
    r'\b(9am|8am|7am|6am|midnight|noon)\b',
    r'\beveryw?eek(ly)?\b',
    r'\bmonday morning\b',
    r'\bdaily (report|summary|briefing)\b',
    r'\bsharp\b',
    r'\bexactly at\b',
]

# Patterns that suggest a task is completed/stale
STALE_PATTERNS = [
    r'\bfollow[ -]?up\b',
    r'\bcheck on\b',
    r'\breminder:\b',
    r'\b(TODO|DONE|COMPLETED|FIXME)\b',
    r'\bonce[\s\-]?only\b',
    r'\btoday\b',
]

# Patterns for high-cost tasks that shouldn't run every heartbeat
HEAVY_PATTERNS = [
    r'\b(deep|full|comprehensive|detailed)\s+(analysis|review|scan|report)\b',
    r'\bsearch (the )?web\b',
    r'\bscrape\b',
    r'\bprocess all\b',
    r'\bgenerate (a |an )?(full|complete|long)\b',
]

# Common batchable check keywords — if in cron, could be in heartbeat instead
BATCHABLE_KEYWORDS = [
    'inbox', 'email', 'calendar', 'notification', 'mention', 'discord',
    'twitter', 'x.com', 'slack', 'weather', 'news', 'feed', 'check',
]


def load_cron_jobs():
    """Load cron jobs via `openclaw cron list --json` or return empty list."""
    try:
        result = subprocess.run(
            ['openclaw', 'cron', 'list', '--json'],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            # Handle both {"jobs": [...]} and [...] formats
            if isinstance(data, list):
                return data
            return data.get('jobs', [])
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        pass
    return []


def parse_heartbeat(path):
    """Parse HEARTBEAT.md, return list of (line_number, line_text) for task items."""
    tasks = []
    if not path or not os.path.isfile(path):
        return tasks
    with open(path, encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            stripped = line.strip()
            # Task lines: start with -, *, or a checkbox
            if re.match(r'^[-*]\s+', stripped) or re.match(r'^-\s*\[[ xX]\]', stripped):
                tasks.append((i, stripped))
    return tasks


def detect_heartbeat_violations(tasks):
    """Flag heartbeat tasks that should probably be in cron."""
    findings = []
    for lineno, text in tasks:
        lower = text.lower()

        # Exact timing
        for pat in TIMING_PATTERNS:
            if re.search(pat, lower, re.IGNORECASE):
                findings.append({
                    'type': 'TIMING_IN_HEARTBEAT',
                    'severity': 'high',
                    'line': lineno,
                    'text': text,
                    'reason': 'Task appears to need exact timing — heartbeat timing drifts.',
                    'fix': 'Move to cron with an explicit schedule (--cron "0 9 * * 1" etc.)',
                })
                break

        # Heavy analysis
        for pat in HEAVY_PATTERNS:
            if re.search(pat, lower, re.IGNORECASE):
                findings.append({
                    'type': 'HEAVY_TASK_IN_HEARTBEAT',
                    'severity': 'medium',
                    'line': lineno,
                    'text': text,
                    'reason': 'Heavy analysis tasks slow down the heartbeat cycle.',
                    'fix': 'Move to isolated cron with --model override for better performance.',
                })
                break

        # Stale one-offs
        for pat in STALE_PATTERNS:
            if re.search(pat, lower, re.IGNORECASE):
                findings.append({
                    'type': 'POSSIBLE_STALE_TASK',
                    'severity': 'low',
                    'line': lineno,
                    'text': text,
                    'reason': 'Looks like a one-off task that may already be done.',
                    'fix': 'Verify if still active; remove if completed.',
                })
                break

    return findings


def detect_cron_violations(jobs, heartbeat_tasks):
    """Flag cron jobs that should probably be in heartbeat."""
    findings = []
    heartbeat_lower = [t.lower() for _, t in heartbeat_tasks]

    # Find batchable cron jobs (frequent polling that fits in heartbeat)
    batchable_jobs = []
    for job in jobs:
        name = (job.get('name') or job.get('id') or '').lower()
        message = (job.get('message') or job.get('prompt') or '').lower()
        combined = name + ' ' + message
        schedule = job.get('schedule') or job.get('cron') or ''

        # Frequent schedule (every 15-60 min)
        is_frequent = bool(re.search(r'\*/[1-5]?\d\s', str(schedule)))

        if is_frequent:
            for kw in BATCHABLE_KEYWORDS:
                if kw in combined:
                    batchable_jobs.append((job, kw))
                    break

    if len(batchable_jobs) >= 2:
        names = [j.get('name', j.get('id', '?')) for j, _ in batchable_jobs]
        findings.append({
            'type': 'BATCHABLE_CRON_JOBS',
            'severity': 'medium',
            'jobs': names,
            'reason': 'Multiple frequent cron jobs doing periodic checks. These could be merged into a single heartbeat.',
            'fix': 'Move these checks to HEARTBEAT.md, delete the cron jobs.',
        })

    # Detect duplicate coverage (task in both cron and heartbeat)
    for job in jobs:
        name = (job.get('name') or '').lower()
        for hb_text in heartbeat_lower:
            # Simple overlap: 3+ words in common
            name_words = set(re.findall(r'\w+', name))
            hb_words = set(re.findall(r'\w+', hb_text))
            overlap = name_words & hb_words - {'the', 'a', 'an', 'and', 'or', 'for', 'to', 'in', 'of'}
            if len(overlap) >= 3:
                findings.append({
                    'type': 'DUPLICATE_COVERAGE',
                    'severity': 'high',
                    'cron_job': job.get('name', job.get('id')),
                    'heartbeat_text': hb_text[:80],
                    'reason': 'Same task appears in both cron and heartbeat. Double execution.',
                    'fix': 'Pick one mechanism and remove the other.',
                })
                break

    return findings


def format_report(hb_findings, cron_findings, cron_jobs, hb_tasks):
    """Format a human-readable audit report."""
    lines = []
    lines.append('=' * 60)
    lines.append('CRON / HEARTBEAT AUDIT REPORT')
    lines.append('=' * 60)
    lines.append('')
    lines.append('SUMMARY')
    lines.append(f'  Cron jobs:          {len(cron_jobs)}')
    lines.append(f'  Heartbeat tasks:    {len(hb_tasks)}')
    total_findings = len(hb_findings) + len(cron_findings)
    lines.append(f'  Findings:           {total_findings}')
    lines.append('')

    if not hb_findings and not cron_findings:
        lines.append('✅ No violations found. Cron/heartbeat split looks healthy.')
        return '\n'.join(lines)

    if hb_findings:
        lines.append('─' * 60)
        lines.append('HEARTBEAT.md FINDINGS')
        lines.append('─' * 60)
        for f in hb_findings:
            sev = {'high': '🔴', 'medium': '🟡', 'low': '🔵'}.get(f['severity'], '⚪')
            lines.append(f"\n{sev} [{f['type']}] line {f.get('line', '?')}")
            lines.append(f"   Task:   {f.get('text', '')[:80]}")
            lines.append(f"   Reason: {f['reason']}")
            lines.append(f"   Fix:    {f['fix']}")

    if cron_findings:
        lines.append('')
        lines.append('─' * 60)
        lines.append('CRON JOB FINDINGS')
        lines.append('─' * 60)
        for f in cron_findings:
            sev = {'high': '🔴', 'medium': '🟡', 'low': '🔵'}.get(f['severity'], '⚪')
            lines.append(f"\n{sev} [{f['type']}]")
            if 'jobs' in f:
                lines.append(f"   Jobs:   {', '.join(f['jobs'])}")
            if 'cron_job' in f:
                lines.append(f"   Cron:   {f['cron_job']}")
            if 'heartbeat_text' in f:
                lines.append(f"   HB:     {f['heartbeat_text']}")
            lines.append(f"   Reason: {f['reason']}")
            lines.append(f"   Fix:    {f['fix']}")

    lines.append('')
    lines.append('─' * 60)
    lines.append('NEXT STEPS')
    lines.append('─' * 60)
    high = sum(1 for f in hb_findings + cron_findings if f.get('severity') == 'high')
    medium = sum(1 for f in hb_findings + cron_findings if f.get('severity') == 'medium')
    if high > 0:
        lines.append(f'  {high} high-severity finding(s) — address these first.')
    if medium > 0:
        lines.append(f'  {medium} medium-severity finding(s) — review and optimize.')
    lines.append('')
    lines.append('  Apply fixes, then confirm with user before deleting any cron jobs.')
    lines.append('  See references/policy.md for full guidance.')

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Audit cron/heartbeat split')
    parser.add_argument('--heartbeat', default=None,
                        help='Path to HEARTBEAT.md (default: auto-discover)')
    parser.add_argument('--cron-json', default=None,
                        help='Cron jobs as JSON string (default: run openclaw cron list --json)')
    args = parser.parse_args()

    # Load cron jobs
    if args.cron_json:
        try:
            data = json.loads(args.cron_json)
            cron_jobs = data if isinstance(data, list) else data.get('jobs', [])
        except json.JSONDecodeError as e:
            print(f'Error parsing --cron-json: {e}', file=sys.stderr)
            sys.exit(1)
    else:
        cron_jobs = load_cron_jobs()

    # Locate HEARTBEAT.md
    hb_path = args.heartbeat
    if not hb_path:
        # Auto-discover: walk up from cwd
        search = os.getcwd()
        for _ in range(5):
            candidate = os.path.join(search, 'HEARTBEAT.md')
            if os.path.isfile(candidate):
                hb_path = candidate
                break
            search = os.path.dirname(search)

    hb_tasks = parse_heartbeat(hb_path)

    # Run checks
    hb_findings = detect_heartbeat_violations(hb_tasks)
    cron_findings = detect_cron_violations(cron_jobs, hb_tasks)

    print(format_report(hb_findings, cron_findings, cron_jobs, hb_tasks))


if __name__ == '__main__':
    main()
