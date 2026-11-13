#!/usr/bin/env python3
import json
import os
import re
import urllib.request
from datetime import datetime, timezone

EXCLUDED = {
    'olakunlevpn-claude-commands',
}

ACRONYMS = {'php': 'PHP', 'css': 'CSS', 'api': 'API', 'ui': 'UI', 'qa': 'QA', 'js': 'JS', 'v5': 'v5', 'aws': 'AWS'}

PRINCIPLES = [
    {
        "quote": "When different forms of documentation blur together, every single form gets worse. Keep tutorials, how-to guides, reference, and explanation strictly separated.",
        "skill": "Diataxis Framework Skills",
        "url": "https://github.com/olakunlevpn/olakunlevpn-diataxis-framework"
    },
    {
        "quote": "Most broken features do not fail in the backend or the frontend. They die at the seam. Wire contracts turn data mismatches into compile-time errors.",
        "skill": "Seam Contract Skills",
        "url": "https://github.com/olakunlevpn/olakunlevpn-seam-contract"
    },
    {
        "quote": "Most bad fixes come from the same move: see a symptom, change something nearby, and hope. Never touch code until the root cause is proven by reproduction.",
        "skill": "Safe Bug Fix Skills",
        "url": "https://github.com/olakunlevpn/olakunlevpn-safe-bug-fix"
    },
    {
        "quote": "A passing test is meaningless if it cannot fail when the code is broken. Mutate the code to prove your test actually catches the regression.",
        "skill": "Flow Soundness Skills",
        "url": "https://github.com/olakunlevpn/olakunlevpn-flow-soundness"
    },
    {
        "quote": "You cannot verify what you haven't listed. Map user interactions and server links exhaustively before declaring a feature wired.",
        "skill": "Flow Check Skills",
        "url": "https://github.com/olakunlevpn/olakunlevpn-flow-check"
    },
    {
        "quote": "Design the interaction flow, empty states, error branches, and wire contract before either side is built. Don't let client and server drift during construction.",
        "skill": "Interaction Map Skills",
        "url": "https://github.com/olakunlevpn/olakunlevpn-interaction-map"
    },
    {
        "quote": "Predictability under load beats raw speed at zero load. Design systems for their failure modes, not just their happy path.",
        "skill": "Scaling Discipline Skills",
        "url": "https://github.com/olakunlevpn/olakunlevpn-scaling-discipline"
    },
    {
        "quote": "Never let web requests do heavy background work. Offload queueable jobs immediately to keep HTTP response times deterministic.",
        "skill": "Scaling Discipline Skills",
        "url": "https://github.com/olakunlevpn/olakunlevpn-scaling-discipline"
    },
    {
        "quote": "Fail fast and fail visibly. Silent fallbacks mask corruption until it reaches durable storage where it is ten times harder to untangle.",
        "skill": "Scaling Discipline Skills",
        "url": "https://github.com/olakunlevpn/olakunlevpn-scaling-discipline"
    },
    {
        "quote": "The local dev workspace is the single source of truth. The server runs your code, it never authors it. Every permanent change is written locally and shipped through the pipeline.",
        "skill": "Local Source of Truth Skills",
        "url": "https://github.com/olakunlevpn/olakunlevpn-local-source-of-truth"
    },
    {
        "quote": "Identify the framework in use and follow its conventions to the letter. Code that fights its framework creates technical debt from day one.",
        "skill": "Framework First Skills",
        "url": "https://github.com/olakunlevpn/olakunlevpn-framework-first"
    },
    {
        "quote": "Good writing sounds like a thoughtful human with strong opinions. Strip throat-clearing, bold-spam, and bland filler so the prose reads genuine.",
        "skill": "Human Writing Skills",
        "url": "https://github.com/olakunlevpn/olakunlevpn-human-writing"
    },
    {
        "quote": "Gate 'done' on verifiable evidence, not confidence. An unrun command or uninspected link is never reported clean.",
        "skill": "Meta-Verify Skills",
        "url": "https://github.com/olakunlevpn/olakunlevpn-meta-verify"
    },
    {
        "quote": "Only add files you wrote or deliberately modified. A pristine repository contains zero local cache, secrets, or temporary build clutter.",
        "skill": "Clean Project Export Skills",
        "url": "https://github.com/olakunlevpn/olakunlevpn-clean-export-skills"
    },
    {
        "quote": "Keep admin panels maintainable: keep resources thin, forms declarative, and authorization explicit. Never let administrative logic bypass model policy gates.",
        "skill": "Filament PHP v5 Skills",
        "url": "https://github.com/olakunlevpn/olakunlevpn-filament-skills"
    },
    {
        "quote": "Lean controllers, rich domain models, explicit type hints, and strict database transactions. Write code Laravel was built to run.",
        "skill": "Laravel Coding Standards Skills",
        "url": "https://github.com/olakunlevpn/olakunlevpn-laravel-skills"
    },
    {
        "quote": "Deployments should be automated, repeatable, and boring. A manual server tweak is a future outage waiting to happen.",
        "skill": "Laravel Deployment Skills",
        "url": "https://github.com/olakunlevpn/olakunlevpn-deployment-skills"
    },
    {
        "quote": "State flows down, events flow up. Keep components pure and isolate side effects to maintainable hooks.",
        "skill": "React & Next.js Skills",
        "url": "https://github.com/olakunlevpn/olakunlevpn-react-skills"
    },
    {
        "quote": "Build design-first. Fix layout, typography, and spacing contracts before attaching complex state machines.",
        "skill": "Design-First Frontend Skills",
        "url": "https://github.com/olakunlevpn/olakunlevpn-frontend-first-skills"
    },
    {
        "quote": "Verify features from 7 perspectives: contract, state, error, security, performance, accessibility, and resilience.",
        "skill": "Meta-Cognitive Verification Skills",
        "url": "https://github.com/olakunlevpn/olakunlevpn-meta-cognitive-verification"
    }
]

def format_title(name: str) -> str:
    clean = name.replace('olakunlevpn-', '')
    parts = clean.split('-')
    words = [p for p in parts if p.lower() not in ('skill', 'skills')]
    formatted_words = []
    for w in words:
        low = w.lower()
        if low in ACRONYMS:
            formatted_words.append(ACRONYMS[low])
        elif low == 'nextjs':
            formatted_words.append('Next.js')
        else:
            formatted_words.append(w.capitalize())
    return ' '.join(formatted_words) + ' Skills'

def get_headers():
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'olakunlevpn-profile-sync'
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'
    return headers

def fetch_data():
    headers = get_headers()

    # 1. Fetch user profile data
    user_url = 'https://api.github.com/users/olakunlevpn'
    user_req = urllib.request.Request(user_url, headers=headers)
    with urllib.request.urlopen(user_req) as resp:
        user_info = json.loads(resp.read().decode('utf-8'))

    # 2. Fetch all public repos with pagination
    repos = []
    page = 1
    while True:
        url = f'https://api.github.com/users/olakunlevpn/repos?per_page=100&page={page}&type=public'
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            page_repos = json.loads(resp.read().decode('utf-8'))
        if not page_repos:
            break
        repos.extend(page_repos)
        if len(page_repos) < 100:
            break
        page += 1

    return user_info, repos

def generate_metrics_markdown(user_info, repos, skill_repos):
    public_repos = user_info.get('public_repos', len(repos))
    total_stars = sum(r.get('stargazers_count', 0) for r in repos)
    followers = user_info.get('followers', 0)
    skills_count = len(skill_repos)

    return f"> 🛠️ **{skills_count} Agent Skills** &nbsp;•&nbsp; 📦 **{public_repos} Public Repositories** &nbsp;•&nbsp; ⭐ **{total_stars} Stars Across Projects** &nbsp;•&nbsp; 👥 **{followers} Followers**"

def generate_principle_markdown():
    # Rotate deterministically based on day of year
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    idx = day_of_year % len(PRINCIPLES)
    p = PRINCIPLES[idx]
    return f'> *"{p["quote"]}"*\n>\n> — **[{p["skill"]}]({p["url"]})**'

def generate_recent_activity_markdown(repos):
    # Sort repos by updated_at / pushed_at descending
    active_repos = [r for r in repos if not r.get('fork') and r['name'] != 'Olakunlevpn']
    active_repos.sort(key=lambda x: x.get('pushed_at') or x.get('updated_at') or '', reverse=True)

    lines = []
    now = datetime.now(timezone.utc)
    for r in active_repos[:5]:
        name = r['name']
        desc = (r.get('description') or '').strip()
        if not desc:
            if name == 'olakunlevpn.github.io':
                desc = 'Technical blog and engineering notes'
            else:
                desc = 'Open source project'
        if len(desc) > 85:
            desc = desc[:82].rstrip() + '...'
        updated = r.get('pushed_at') or r.get('updated_at') or ''
        try:
            dt = datetime.fromisoformat(updated.replace('Z', '+00:00'))
            diff_days = (now - dt).days
            if diff_days == 0:
                time_str = 'today'
            elif diff_days == 1:
                time_str = 'yesterday'
            else:
                time_str = f'{diff_days}d ago'
        except Exception:
            time_str = 'recently'

        lines.append(f'- 🚀 [{name}]({r["html_url"]}) — {desc} *({time_str})*')

    return '\n'.join(lines)

def generate_skills_markdown(skill_repos):
    lines = [f"  - [{s['title']}]({s['url']})" for s in skill_repos]
    return '\n'.join(lines)

def replace_section(content, start_tag, end_tag, new_body):
    pattern = rf'{re.escape(start_tag)}.*?{re.escape(end_tag)}'
    replacement = f'{start_tag}\n{new_body}\n{end_tag}'
    return re.sub(pattern, replacement, content, flags=re.DOTALL)

def main():
    user_info, repos = fetch_data()

    # Identify skills
    skill_repos = []
    for r in repos:
        if r.get('fork') or r.get('private'):
            continue
        name = r['name']
        if name in EXCLUDED:
            continue
        topics = r.get('topics') or []
        if name.startswith('olakunlevpn-') or 'agent-skills' in topics or 'skills' in topics:
            title = format_title(name)
            skill_repos.append({
                'name': name,
                'title': title,
                'url': r['html_url']
            })
    skill_repos.sort(key=lambda x: x['title'].lower())

    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = content

    # 1. Update Metrics
    if '<!-- METRICS:START -->' in new_content:
        metrics_md = generate_metrics_markdown(user_info, repos, skill_repos)
        new_content = replace_section(new_content, '<!-- METRICS:START -->', '<!-- METRICS:END -->', metrics_md)

    # 2. Update Principle of the Day
    if '<!-- PRINCIPLE-OF-THE-DAY:START -->' in new_content:
        principle_md = generate_principle_markdown()
        new_content = replace_section(new_content, '<!-- PRINCIPLE-OF-THE-DAY:START -->', '<!-- PRINCIPLE-OF-THE-DAY:END -->', principle_md)

    # 3. Update Recent Activity
    if '<!-- RECENT-ACTIVITY:START -->' in new_content:
        activity_md = generate_recent_activity_markdown(repos)
        new_content = replace_section(new_content, '<!-- RECENT-ACTIVITY:START -->', '<!-- RECENT-ACTIVITY:END -->', activity_md)

    # 4. Update Agent Skills
    if '<!-- AGENT-SKILLS:START -->' in new_content:
        skills_md = generate_skills_markdown(skill_repos)
        new_content = replace_section(new_content, '<!-- AGENT-SKILLS:START -->', '  <!-- AGENT-SKILLS:END -->', skills_md)

    if new_content == content:
        print("No changes needed in README.md")
        return False

    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully updated README.md sections (metrics, principle, activity, skills).")
    return True

if __name__ == '__main__':
    main()
