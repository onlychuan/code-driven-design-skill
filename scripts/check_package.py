"""Validate the distributable skill and portable plugin without external services."""
from pathlib import Path
import argparse
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

def check(root: Path) -> dict:
    skill = root / 'skills' / 'code-driven-design'
    required = [
        'SKILL.md', 'agents/openai.yaml', 'assets/example-card.json',
        'scripts/render_design.py', 'references/renderer.md',
        'references/brand-context.md', 'references/interaction-preview.md',
        'references/print-production.md', 'references/publishing-delivery.md',
    ]
    errors = [f'Missing {p}' for p in required if not (skill / p).is_file()]
    if errors:
        raise ValueError('\n'.join(errors))
    entry = (skill / 'SKILL.md').read_text(encoding='utf-8')
    match = re.match(r'^---\n(.*?)\n---\n', entry, re.S)
    if not match or 'name: code-driven-design' not in match.group(1) or not re.search(r'^description:\s*\S', match.group(1), re.M):
        raise ValueError('Invalid skill frontmatter')
    for ref in re.findall(r'\]\((references/[^)]+)\)', entry):
        if not (skill / ref).is_file():
            raise ValueError(f'Broken skill reference: {ref}')
    portable = json.loads((root / 'plugin.json').read_text(encoding='utf-8'))
    legacy = json.loads((root / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))
    assert portable['name'] == legacy['name'] == 'code-driven-design-skill'
    assert portable['version'] == legacy['version']
    assert re.fullmatch(r'\d+\.\d+\.\d+', portable['version'])
    assert portable['$schema'] == 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json'
    subtitle = portable['extensions']['com.openai']['interface']['shortDescription']
    assert len(subtitle) <= 30
    catalog = json.loads((root / '.agents/plugins/marketplace.json').read_text(encoding='utf-8'))
    assert catalog['plugins'][0]['source']['path'] == './'
    assert catalog['plugins'][0]['name'] == portable['name']
    for name in ['install.cmd', 'install.ps1', 'install.sh', 'LICENSE', 'README.md']:
        assert (root / name).is_file(), name
    private_state = re.compile(r'(?:[A-Za-z]:[\\/]Users[\\/][^\\/\s]+|/Users/[^/\s]+|appgprj_[a-zA-Z0-9]+|gh[pousr]_[a-zA-Z0-9]{25,}|github_pat_[a-zA-Z0-9_]{25,})')
    checked = 0
    for p in skill.rglob('*'):
        if p.is_symlink():
            raise ValueError(f'Symlinks cannot enter release: {p.relative_to(root)}')
        if not p.is_file() or '__pycache__' in p.parts:
            continue
        if p.suffix in {'.ttf', '.otf', '.ttc', '.woff', '.woff2'}:
            raise ValueError(f'Font redistribution needs explicit provenance: {p.relative_to(root)}')
        text = p.read_text(encoding='utf-8')
        if '[TODO' in text or private_state.search(text):
            raise ValueError(f'Private state or unfinished scaffold: {p.relative_to(root)}')
        checked += 1
    return {'result': 'PASS', 'version': portable['version'], 'skill_files': checked}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        print(json.dumps(check(args.root.resolve())))
    except (ValueError, AssertionError, KeyError, OSError) as e:
        print(f'Package validation failed: {e}', file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
