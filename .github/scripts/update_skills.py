#!/usr/bin/env python3
import json
import os
import re
import urllib.request

EXCLUDED = {
    'olakunlevpn-claude-commands',
}

TITLE_MAP = {
    'olakunlevpn-artifact-skills': 'Artifact Skills',
    'olakunlevpn-clean-export-skills': 'Clean Project Export Skills',
    'olakunlevpn-laravel-skills': 'Laravel Coding Standards Skills',
    'olakunlevpn-filament-skills': 'Filament PHP v5 Skills',
    'olakunlevpn-git-skills': 'Git Workflow Standards Skills',
    'olakunlevpn-deployment-skills': 'Laravel Deployment Skills',
    'olakunlevpn-react-skills': 'React & Next.js Skills',
    'olakunlevpn-frontend-first-skills': 'Design-First Frontend Skills',
    'olakunlevpn-meta-cognitive-verification': 'Meta-Cognitive Verification Skills',
    'olakunlevpn-root-cause-skills': 'Root-Cause Discipline Skills',
    'olakunlevpn-meta-verify': 'Meta-Verify Skills',
    'olakunlevpn-human-writing': 'Human Writing Skills',
    'olakunlevpn-scaling-discipline': 'Scaling Discipline Skills',
    'olakunlevpn-diataxis-framework': 'Diataxis Framework Skills',
    'olakunlevpn-flow-check': 'Flow Check Skills',
    'olakunlevpn-flow-soundness': 'Flow Soundness Skills',
    'olakunlevpn-interaction-map': 'Interaction Map Skills',
    'olakunlevpn-safe-bug-fix': 'Safe Bug Fix Skills',
    'olakunlevpn-seam-contract': 'Seam Contract Skills',
    'olakunlevpn-framework-first': 'Framework First Skills',
    'olakunlevpn-local-source-of-truth': 'Local Source of Truth Skills',
    'olakunlevpn-blog-publishing': 'Blog Publishing Skills',
}

def format_title(name: str) -> str:
    if name in TITLE_MAP:
        return TITLE_MAP[name]
    clean = name.replace('olakunlevpn-', '')
    words = [w.capitalize() for w in clean.split('-') if w.lower() != 'skills']
    return ' '.join(words) + ' Skills'

def fetch_skills():
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'olakunlevpn-profile-skills-sync'
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'

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

    # Sort alphabetically by title
    skill_repos.sort(key=lambda x: x['title'].lower())
    return skill_repos

def update_readme(skills):
    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.read()

    lines = [f"  - [{s['title']}]({s['url']})" for s in skills]
    skills_block = '\n'.join(lines)
    replacement = f"<!-- AGENT-SKILLS:START -->\n{skills_block}\n  <!-- AGENT-SKILLS:END -->"

    pattern = r'<!-- AGENT-SKILLS:START -->.*?<!-- AGENT-SKILLS:END -->'
    new_content, count = re.subn(pattern, replacement, content, flags=re.DOTALL)

    if count == 0:
        print("Warning: Could not find <!-- AGENT-SKILLS:START --> in README.md")
        return False

    if new_content == content:
        print("No changes needed in README.md")
        return False

    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Updated README.md with {len(skills)} agent skills.")
    return True

if __name__ == '__main__':
    skills = fetch_skills()
    update_readme(skills)
