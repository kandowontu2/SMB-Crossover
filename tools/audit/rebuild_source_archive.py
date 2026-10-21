"""Verify an existing immutable source archive by building a fresh extraction."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--checkpoint', type=Path, required=True)
p.add_argument('--archive', type=Path, required=True)
p.add_argument('--tag', required=True)
a = p.parse_args()
assert a.tag and all(c.isalnum() or c in '-_' for c in a.tag)
checkpoint, archive = a.checkpoint.resolve(), a.archive.resolve()
assert checkpoint.is_relative_to(ROOT) and archive.is_relative_to(checkpoint)
out = ROOT / 'build/checkpoint-tests' / f'source-{a.tag}-rebuild-smoke'
fresh = out / 'source'
fresh.mkdir(parents=True, exist_ok=False)
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
with zipfile.ZipFile(archive) as z:
    catalog = json.loads(z.read('archived-file-hashes.json'))
    assert set(z.namelist()) == set(catalog) | {'archived-file-hashes.json'}
    for n, h in catalog.items():
        name = PurePosixPath(n)
        assert not name.is_absolute() and '..' not in name.parts and '\\' not in n
        content = z.read(n)
        assert hashlib.sha256(content).hexdigest() == h
        target = fresh / n
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
assert all(sha(fresh / n) == h for n, h in catalog.items())
shutil.copytree(ROOT / 'tools/Windows/cc65', fresh / 'tools/Windows/cc65')
report = dict(archive_sha256=sha(archive), source_files=len(catalog),
              scope='Fresh extraction; separately supplied compiler/Python/Pillow; no native/runtime test claim', cases=[])
for mapper in ('mmc3', 'mmc5'):
    with (out / f'build-{mapper}.log').open('w') as log:
        result = subprocess.run([sys.executable, 'tools/build.py', '--mapper', mapper], cwd=fresh,
                                stdout=log, stderr=subprocess.STDOUT)
    built = fresh / f'build/smb-crossover-{mapper}.nes'
    item = dict(mapper=mapper, exit=result.returncode,
                equal=built.exists() and built.read_bytes() == (checkpoint / built.name).read_bytes(),
                sha256=sha(built) if built.exists() else None)
    report['cases'].append(item)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(item, flush=True)
    assert item['exit'] == 0 and item['equal']
print('PASS fresh archive rebuild', flush=True)
