"""Apply a pinned Ryu wall proposal and freeze both provisional mapper builds."""
from pathlib import Path
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
    parser.add_argument('--packet', type=Path, required=True)
    parser.add_argument('--expected-freeze-sha256', required=True)
    parser.add_argument('--tag', required=True)
    args = parser.parse_args()
    assert re.fullmatch(r'[a-z0-9-]+', args.tag)
    packet = args.packet.resolve(strict=True)
    assert packet.is_relative_to(ROOT / 'build/verification')
    freeze = packet / 'implementation-freeze.json'
    assert sha(freeze) == args.expected_freeze_sha256
    frozen = json.loads(freeze.read_text())
    for name, record in frozen['files'].items():
        file = (packet / name).resolve(strict=True)
        assert file.is_relative_to(packet)
        expected = record if isinstance(record, str) else record['sha256']
        assert sha(file) == expected, name
    patch = packet / 'ryu-wall49-unapplied.patch'
    assert patch.is_file()
    qualification = json.loads((packet / 'implementation-qualification.json').read_text())
    assert sha(PARENT / 'manifest.json') == 'fd0770c5058acd0522008f341427878495dadcbb7dd8cbf0e3db1eb934684102'
    with zipfile.ZipFile(PARENT / 'source-v48.zip') as archive:
        previous = json.loads(archive.read('archived-file-hashes.json'))
    assert len(previous) == 403
    assert {n for n, digest in previous.items() if sha(ROOT / n) != digest} == {'README.md'}
    for name, digest in qualification['parent_source_files'].items():
        assert sha(ROOT / name) == digest, name
    assert not (ROOT / 'src/ryu_wall.s').exists()
    output = ROOT / 'build/checkpoints' / ('roster-audit-v49-provisional-' + args.tag)
    output.mkdir(exist_ok=False)
    report = dict(status='preparing-not-accepted', goal_complete=False,
                  utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  parent=PARENT.name, packet=str(packet.relative_to(ROOT)),
                  freeze_sha256=sha(freeze), patch_sha256=sha(patch), roms={},
                  script_sha256=sha(Path(__file__)))
    result_path = output / 'candidate.json'

    def save():
        result_path.write_text(json.dumps(report, indent=2) + '\n')

    save()
    subprocess.run(['git', 'apply', '--check', str(patch)], cwd=ROOT, check=True)
    subprocess.run(['git', 'apply', str(patch)], cwd=ROOT, check=True)
    assert (ROOT / 'src/ryu_wall.s').read_bytes() == (packet / 'ryu_wall.s').read_bytes()
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
        assert old[16 + 524288:] == new[16 + 524288:], 'CHR must remain unchanged'
        debug = rom.with_suffix('.dbg').read_text()
        segments = {}
        for line in debug.splitlines():
            if not line.startswith('seg\t'):
                continue
            fields = {k: v.strip('"') for k, v in re.findall(r'(\w+)=("[^"\n]*"|[^,\t]+)', line)}
            if fields['name'] in ('EXPANDED', 'EXPANDED_EX', 'SAMUS', 'SPECIAL_ROSTER', 'SPECIAL_EXTRA', 'SRAM'):
                segments[fields['name']] = dict(start=int(fields['start'], 0), size=int(fields['size'], 0))
        assert all(value['size'] <= 8192 for value in segments.values())
        report['roms'][mapper] = dict(sha256=sha(rom), dbg_sha256=sha(rom.with_suffix('.dbg')),
                                      lbl_sha256=sha(rom.with_suffix('.lbl')), segments=segments,
                                      changed_bytes=sum(a != b for a, b in zip(old, new)), chr_identical=True)
        save()
    files = {name: sha(ROOT / name) for name in sorted(set(previous) | {'src/ryu_wall.s'})}
    changed = {name for name in previous if files[name] != previous[name]}
    expected = set(qualification['parent_source_files']) | {'README.md'}
    assert changed == expected, (changed, expected)
    archive = output / 'source-v49.zip'
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as writer:
        for name in files:
            writer.writestr(name, (ROOT / name).read_bytes())
        writer.writestr('archived-file-hashes.json', json.dumps(files, indent=2) + '\n')
    report.update(status='provisional-not-accepted', source_count=len(files),
                  source_archive_sha256=sha(archive), changed_sources=sorted(changed),
                  tests_complete=False, qualification=qualification,
                  limits=['Frozen seeded component, broad regression, source rebuild, ordinary routes, and audiovisual review remain required.',
                          'Existing v48 acceptance is preserved; no new release or all-character completion claim.'])
    save()
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    main()
