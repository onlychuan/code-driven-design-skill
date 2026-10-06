"""Build a deterministic ZIP with one installable skill/plugin directory."""
from pathlib import Path
import argparse
import hashlib
import json
import zipfile
from check_package import check, ROOT

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = check(ROOT)
    out = args.out.resolve(); out.mkdir(parents=True, exist_ok=True)
    version = result['version']
    archive = out / f'code-driven-design-skill-v{version}.zip'
    include = ['skills', '.codex-plugin', '.agents', 'plugin.json', 'README.md', 'LICENSE', 'install.cmd', 'install.ps1', 'install.sh', 'requirements-print.txt']
    files = []
    for name in include:
        item = ROOT / name
        files.extend([item] if item.is_file() else [p for p in item.rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.pyc')])
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(files):
            if p.is_symlink(): raise ValueError(f'Symlink refused: {p}')
            rel = str(p.relative_to(ROOT)).replace('\\', '/')
            info = zipfile.ZipInfo(f'code-driven-design-skill/{rel}', date_time=(2026,1,1,0,0,0))
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            mode = 0o755 if p.suffix == '.sh' else 0o644
            info.external_attr = mode << 16
            z.writestr(info, p.read_bytes(), compresslevel=9)
        manifest = {str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
        info = zipfile.ZipInfo('code-driven-design-skill/CONTENTS-SHA256.json', date_time=(2026,1,1,0,0,0))
        info.create_system = 3
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        z.writestr(info, json.dumps(manifest, indent=2).encode(), compresslevel=9)
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None: raise ValueError('ZIP failed CRC verification')
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (out / 'SHA256SUMS.txt').write_text(f'{digest}  {archive.name}\n', encoding='ascii')
    print(json.dumps({'archive':str(archive),'sha256':digest,'bytes':archive.stat().st_size,'files':len(files)}))

if __name__ == '__main__': main()
