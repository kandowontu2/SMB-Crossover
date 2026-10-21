"""Save a frozen38 build-input archive and verify both fresh-extraction builds."""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess, sys, zipfile

ROOT = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--checkpoint', type=Path, required=True)
p.add_argument('--tag', required=True)
a = p.parse_args()
checkpoint = a.checkpoint.resolve()
archive = checkpoint/f'source-{a.tag}.zip'
smoke = ROOT/f'build/checkpoint-tests/source-{a.tag}-rebuild-smoke'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert not archive.exists() and not smoke.exists(), 'Do not overwrite immutable archive/receipts'
with zipfile.ZipFile(ROOT/'build/checkpoints/roster-audit-v37/source-v37.zip') as z:
    catalog = set(json.loads(z.read('archived-file-hashes.json')))
catalog.add('src/samus_collision_ram.s')
assert len(catalog) == 401
hashes = {name: sha(ROOT/name) for name in sorted(catalog)}
with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED) as z:
    for name in sorted(catalog):
        z.write(ROOT/name, name)
    z.writestr('archived-file-hashes.json', json.dumps(hashes, indent=2)+'\n')
fresh = smoke/'source'
fresh.mkdir(parents=True)
with zipfile.ZipFile(archive) as z:
    z.extractall(fresh)
assert all(sha(fresh/n) == h for n, h in hashes.items())
shutil.copytree(ROOT/'tools/Windows/cc65', fresh/'tools/Windows/cc65')
report = {'archive_sha256': sha(archive), 'source_files': 401,
          'scope': 'Fresh extraction, separately supplied compiler/Python/Pillow', 'cases': []}
for mapper in ('mmc3', 'mmc5'):
    with (smoke/f'build-{mapper}.log').open('w') as stream:
        result = subprocess.run([sys.executable, 'tools/build.py', '--mapper', mapper], cwd=fresh, stdout=stream, stderr=subprocess.STDOUT)
    built = fresh/f'build/smb-crossover-{mapper}.nes'
    entry = {'mapper': mapper, 'exit': result.returncode,
             'equal': built.exists() and built.read_bytes() == (checkpoint/built.name).read_bytes(),
             'sha256': sha(built) if built.exists() else None}
    report['cases'].append(entry)
    (smoke/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(entry, flush=True)
    assert entry['exit'] == 0 and entry['equal']
assert hashes == {n: sha(ROOT/n) for n in hashes}, 'Build inputs changed during archive smoke'
print('PASS exact fresh38 builds', sha(archive))
