"""Freeze and reproduce the accepted50b5 game without production writes."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from tmnt_native_storage_driver import ROOT, CURRENT, sha

ARCHIVE = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    assert sha(ROOT / 'build/smb-crossover-mmc5-expanded.nes') == CURRENT
    a.output.mkdir(parents=True, exist_ok=False)
    source = a.output / 'source'
    prior = json.loads((ARCHIVE / 'mike-native-current5ec-v1/frozen-inputs.json').read_text())
    files = {p.relative_to(ROOT).as_posix(): p for top in ['src', 'inc', 'audio']
             for p in (ROOT / top).rglob('*') if p.is_file()}
    files.update({name: ROOT / name for name in prior['shared_assets']})
    for name in ['smb1base-mmc5-expanded.cfg', 'smb1base.cfg', 'build_options.ini',
                 'tools/build_mmc5_expanded.py', 'tools/prepare_cv3_dmc_mirror.py']:
        files[name] = ROOT / name
    hashes = {name: sha(path) for name, path in files.items()}
    for name, path in files.items():
        dest = source / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dest)
    for suffix in ['.nes', '.dbg', '.lbl', '.map']:
        shutil.copyfile(ROOT / ('build/smb-crossover-mmc5-expanded' + suffix), a.output / ('baseline' + suffix))
    cmd = [sys.executable, str(source / 'tools/build_mmc5_expanded.py'),
           '--workspace', str(source), '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'),
           '--output', str(a.output / 'rebuilt-baseline.nes')]
    r = subprocess.run(cmd, cwd=source, capture_output=True, text=True)
    (a.output / 'baseline-build.log').write_text(r.stdout + r.stderr)
    assert r.returncode == 0, (r.stdout + r.stderr)[-3000:]
    assert sha(a.output / 'rebuilt-baseline.nes') == CURRENT
    assert all(sha(ROOT / name) == digest for name, digest in hashes.items())
    assert all(sha(source / name) == digest for name, digest in hashes.items())
    result = dict(passed=True, parent_ROM_sha256=CURRENT, canonical_baseline_exact=True,
                  source_files=hashes, source_file_count=len(hashes),
                  production_writes=False, native_run=False, tool_sha256=sha(Path(__file__)))
    (a.output / 'frozen-source.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['passed', 'parent_ROM_sha256', 'canonical_baseline_exact', 'source_file_count']}))


if __name__ == '__main__':
    main()
