"""Build the pinned tail-SRAM revision and prove legacy data/code addresses."""
from pathlib import Path
from collections import Counter
import argparse
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT / 'build/checkpoints/roster-audit-v48'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', type=Path, required=True)
    parser.add_argument('--expected-catalog-sha256', required=True)
    parser.add_argument('--tag', required=True)
    args = parser.parse_args()
    assert re.fullmatch(r'[a-z0-9-]+', args.tag)
    catalog_path = args.catalog.resolve(strict=True)
    assert catalog_path.is_relative_to(ROOT / 'build/verification')
    assert sha(catalog_path) == args.expected_catalog_sha256
    catalog = json.loads(catalog_path.read_text(encoding='utf-8'))
    assert sha(PARENT / 'manifest.json') == 'fd0770c5058acd0522008f341427878495dadcbb7dd8cbf0e3db1eb934684102'
    with zipfile.ZipFile(PARENT / 'source-v48.zip') as archive:
        previous = json.loads(archive.read('archived-file-hashes.json'))
    assert set(catalog) == set(previous) | {'src/ryu_wall.s'} and len(catalog) == 404
    assert all(sha(ROOT / name) == digest for name, digest in catalog.items())
    changed = {name for name in previous if catalog[name] != previous[name]}
    assert changed == {'README.md', 'src/expanded.s', 'src/roster.s', 'src/entrypoint.s',
                       'src/remaining_weapons.s', 'src/lsr_injury.s', 'src/samus.s', 'src/samus_collision_ram.s'}
    sys.path.insert(0, str(ROOT / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(ROOT)
    assert used + 90_000_000 < 30_000_000_000
    output = ROOT / 'build/checkpoints' / ('roster-audit-v49-provisional-' + args.tag)
    output.mkdir(exist_ok=False)
    report = dict(status='building-not-accepted', goal_complete=False,
                  utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  parent=PARENT.name, catalog_sha256=sha(catalog_path),
                  catalog=str(catalog_path.relative_to(ROOT)), script_sha256=sha(Path(__file__)),
                  workspace_before_bytes=used, roms={}, tests_complete=False)

    def save():
        (output / 'candidate.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    for mapper in ('mmc3', 'mmc5'):
        with (output / f'build-{mapper}.log').open('w') as log:
            result = subprocess.run([sys.executable, 'tools/build.py', '--mapper', mapper],
                                    cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        report['last_build'] = dict(mapper=mapper, exit=result.returncode)
        save()
        assert result.returncode == 0, ('Build failure retained', mapper)
        for extension in ('.nes', '.lbl', '.dbg', '.map', '.lst'):
            file = ROOT / f'build/smb-crossover-{mapper}{extension}'
            shutil.copyfile(file, output / file.name)
        rom = output / f'smb-crossover-{mapper}.nes'
        old = (PARENT / rom.name).read_bytes()
        new = rom.read_bytes()
        assert len(old) == len(new) and old[:16] == new[:16]
        assert old[16 + 524288:] == new[16 + 524288:]
        segments = {}
        for line in rom.with_suffix('.dbg').read_text(encoding='utf-8').splitlines():
            if line.startswith('seg\t'):
                fields = {k: v.strip('"') for k, v in re.findall(r'(\w+)=("[^"\n]*"|[^,\t]+)', line)}
                if fields['name'] in ('EXPANDED', 'SAMUS', 'SPECIAL_ROSTER', 'SPECIAL_EXTRA', 'SRAM'):
                    size = int(fields['size'], 0)
                    assert size <= 8192
                    segments[fields['name']] = dict(bytes=size, free_bytes=8192-size)
        def ram_labels(path):
            return Counter((m[2], int(m[1], 16)) for m in re.finditer(r'^al ([0-9a-fA-F]+) (\S+)\s*$', path.read_text(encoding='utf-8'), re.M)
                           if 0x6000 <= int(m[1], 16) < 0x8000 and not m[2].startswith('.__'))
        old_ram = ram_labels(PARENT / rom.with_suffix('.lbl').name)
        new_ram = ram_labels(rom.with_suffix('.lbl'))
        assert not old_ram-new_ram, ('A legacy SRAM label moved', old_ram-new_ram)
        def special_labels(path):
            records = []
            for row in path.read_text(encoding='utf-8').splitlines():
                fields = {k: v.strip('"') for k, v in re.findall(r'(\w+)=("[^"\n]*"|[^,\t]+)', row)}
                records.append((row.split('\t', 1)[0], fields))
            ids = {f['id'] for kind, f in records if kind == 'seg' and f.get('name') == 'SPECIAL_MM'}
            return Counter((f['name'], int(f['val'], 0)) for kind, f in records if kind == 'sym' and f.get('seg') in ids and 'val' in f)
        old_special = special_labels(PARENT / rom.with_suffix('.dbg').name)
        new_special = special_labels(rom.with_suffix('.dbg'))
        assert not old_special-new_special, ('A legacy SPECIAL_MM PC moved', old_special-new_special)
        report.setdefault('legacy_layout', {})[mapper] = dict(SRAM_labels=sum(old_ram.values()),
            SPECIAL_MM_labels=sum(old_special.values()), all_legacy_SRAM_addresses_restored=True,
            all_legacy_SPECIAL_MM_PCs_preserved=True)
        report['roms'][mapper] = dict(sha256=sha(rom), dbg_sha256=sha(rom.with_suffix('.dbg')),
                                      lbl_sha256=sha(rom.with_suffix('.lbl')), segments=segments,
                                      chr_identical=True)
        save()
    assert all(sha(ROOT / name) == digest for name, digest in catalog.items()), 'Generated source drift'
    archive_path = output / 'source-v49.zip'
    with zipfile.ZipFile(archive_path, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in catalog:
            archive.writestr(name, (ROOT / name).read_bytes())
        archive.writestr('archived-file-hashes.json', json.dumps(catalog, indent=2) + '\n')
    report.update(status='provisional-not-accepted', source_count=len(catalog),
                  source_archive_sha256=sha(archive_path), workspace_after_bytes=workspace_bytes(ROOT),
                  limits=['New seeded wall component, unchanged broad regression, fresh rebuild, ordinary routes and audiovisual review remain pending.',
                          'Retained attack geometry, grapple extension, source cancel timers/platforms/topJump details remain open.',
                          'No claim of final release, full source parity, or completed roster goal.'])
    save()
    assert report['workspace_after_bytes'] < 30_000_000_000
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    main()
