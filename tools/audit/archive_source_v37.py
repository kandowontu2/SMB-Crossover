"""Save the frozen candidate's build inputs and prove a fresh rebuild."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys, zipfile

ROOT=Path(__file__).resolve().parents[2]
CHECKPOINT=ROOT/'build/checkpoints/roster-audit-v37-provisional-c'
ARCHIVE=CHECKPOINT/'source-v37c.zip'
SMOKE=ROOT/'build/checkpoint-tests/source-v37c-rebuild-smoke'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
assert not ARCHIVE.exists() and not SMOKE.exists(),'Do not overwrite immutable receipts'
base=ROOT/'build/checkpoints/roster-audit-v36/source-v36.zip'
assert sha(base)=='1525e14ec43035c87a38c30cca2dccdd0e097dd7d78571f572d9fd006e949f98'
with zipfile.ZipFile(base)as z:
    catalog=set(json.loads(z.read('archived-file-hashes.json')))
catalog.add('src/guest_publish_chr.inc')
assert len(catalog)==400
source_hashes={name:sha(ROOT/name)for name in sorted(catalog)}
with zipfile.ZipFile(ARCHIVE,'x',compression=zipfile.ZIP_DEFLATED)as z:
    for name in sorted(catalog):z.write(ROOT/name,name)
    z.writestr('archived-file-hashes.json',json.dumps(source_hashes,indent=2)+'\n')
SMOKE.mkdir(parents=True)
fresh=SMOKE/'source';fresh.mkdir()
with zipfile.ZipFile(ARCHIVE)as z:z.extractall(fresh)
for name,h in source_hashes.items():assert sha(fresh/name)==h
shutil.copytree(ROOT/'tools/Windows/cc65',fresh/'tools/Windows/cc65')
report={'archive_sha256':sha(ARCHIVE),'source_files':len(source_hashes),'scope':'Fresh extraction with separately supplied compiler and Python/Pillow','cases':[]}
for mapper in('mmc3','mmc5'):
    log=SMOKE/f'build-{mapper}.log'
    with log.open('w')as stream:
        result=subprocess.run([sys.executable,'tools/build.py','--mapper',mapper],cwd=fresh,stdout=stream,stderr=subprocess.STDOUT)
    built=fresh/f'build/smb-crossover-{mapper}.nes'
    entry={'mapper':mapper,'exit':result.returncode,'equal':built.exists() and built.read_bytes()==(CHECKPOINT/built.name).read_bytes(),'sha256':sha(built)if built.exists()else None}
    report['cases'].append(entry)
    (SMOKE/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(entry,flush=True)
    assert result.returncode==0 and entry['equal'],entry
assert source_hashes=={name:sha(ROOT/name)for name in sorted(catalog)},'Source changed while saving/rebuilding frozen candidate'
print('PASS fresh extraction rebuilds both frozen ROMs byte-identically; archive',sha(ARCHIVE))
