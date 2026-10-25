"""Freeze and independently rebuild the narrow Grant source packet, without adoption."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT / 'build/checkpoints/smb3-shrink-pc'
LIVE = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-grant-grip-pj/candidate-v1')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT.resolve())
    out.mkdir(parents=True, exist_ok=False)
    parent = json.loads((PARENT / 'manifest.json').read_text())
    prep = json.loads((LIVE / 'preparation.json').read_text())
    assert sha(PARENT / 'candidate.nes') == parent['rom_sha256'] == prep['parent_ROM_sha256']
    assert sha(LIVE / 'candidate.nes') == prep['ROM_sha256']
    assert sha(PARENT / 'source.zip') == parent['source_zip_sha256']
    changed = prep['changes']
    assert set(changed) == {'src/cv3.s', 'src/cv3_abilities.s', 'src/cv3_grip.s', 'smb1base-mmc5-expanded.cfg'}
    allowed_notes = {'docs/qa/final-verification-plan-2026-10-23.md',
                     'docs/qa/firebar-empty-mounts-2026-10-24.md', 'workspace-archive.json'}
    assert all(sha(ROOT / n) == h for n, h in parent['source_files'].items() if n not in allowed_notes)
    for n, q in changed.items():
        assert (not (ROOT / n).exists()) if q['before'] is None else sha(ROOT / n) == q['before']
        assert sha(LIVE / 'source' / n) == q['after']
    notes = {'docs/qa/grant-grip-2026-10-24.md', 'docs/qa/current-work-ph-2026-10-24.md'}
    names = set(parent['source_files']) | set(changed) | notes
    for suffix in ('pf', 'pg', 'ph', 'pi', 'pj', 'pk', 'pl', 'pm'):
        names |= {p.relative_to(ROOT).as_posix() for p in (ROOT / 'tools/audit').glob('*_' + suffix + '.*')}
    sources = {n: LIVE / 'source' / n if n in changed else ROOT / n for n in sorted(names)}
    hashes = {n: sha(path) for n, path in sources.items()}
    archive = out / 'source.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, path in sources.items(): z.write(path, name)
    source = out / 'source'
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None and set(z.namelist()) == set(hashes)
        assert all((source / n).resolve().is_relative_to(source.resolve()) for n in z.namelist())
        z.extractall(source)
    assert all(sha(source / n) == h for n, h in hashes.items())
    command = [sys.executable, str(source / 'tools/build_mmc5_expanded.py'), '--workspace', str(source),
               '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe')]
    previous = json.loads((ROOT / 'build/verification/smb3-shrink-pc/proof.json').read_text())
    builds = {}
    for target in ('expanded', 'mmc3', 'mmc5'):
        rom = out / (target + '.nes')
        args = command + ['--output', str(rom)]
        if target != 'expanded': args += ['--flag-off', target]
        run = subprocess.run(args, cwd=source, capture_output=True, text=True)
        (out / (target + '.log')).write_text(run.stdout + run.stderr)
        assert run.returncode == 0, (target, (run.stdout + run.stderr)[-2000:])
        expected = prep['ROM_sha256'] if target == 'expanded' else previous['ordinary_flag_off_hashes'][target]
        assert sha(rom) == expected, target
        builds[target] = sha(rom)
    debug = (LIVE / 'candidate.dbg').read_bytes()
    packed = gzip.compress(debug, mtime=0)
    assert gzip.decompress(packed) == debug
    (out / 'candidate.dbg.gz').write_bytes(packed)
    assert all(sha(source / n) == h for n, h in hashes.items())
    q = dict(passed=True, accepted=False, goal_complete=False, ROM_sha256=prep['ROM_sha256'],
        parent_ROM_sha256=parent['rom_sha256'], source_files=hashes,
        source_zip_sha256=sha(archive), source_only_roundtrip_exact=True,
        builds=builds, debug_gzip_sha256=sha(out / 'candidate.dbg.gz'),
        changes=changed, preparation_sha256=sha(LIVE / 'preparation.json'),
        compiler_sha256=sha(ROOT / 'tools/Windows/cc65/bin/cl65.exe'), driver_sha256=sha(Path(__file__)),
        scope='Independent source-only ZIP extraction/rebuild and both ordinary flag-off hashes. The staged19byteGrant fix is included; live source and public ROMs remain untouched. Native/visual/IRQ qualification and workspace cap must pass before adoption.')
    (out / 'packet.json').write_text(json.dumps(q, indent=2) + '\n')
    print(json.dumps(dict(passed=True, ROM_sha256=q['ROM_sha256'], source_files=len(hashes), builds=builds), indent=2))


if __name__ == '__main__': main()
