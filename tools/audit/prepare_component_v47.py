"""Build/freeze the narrow MMC5 Goomba renderer candidate; not acceptance."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'build/checkpoints/roster-audit-v46'
OUT=ROOT/'build/checkpoints/roster-audit-v47-provisional-a'
packet=ROOT/'build/verification/native-goomba-metadraw45-preparation'
patch=packet/'native-goomba-mmc5.patch'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(patch)=='b0291a84b953463867c588aec689b30c9063811bad46360f7196cd2003fed236'
assert not OUT.exists()and not(ROOT/'src/native_goomba_draw.s').exists()
with zipfile.ZipFile(OLD/'source-v46.zip')as z:previous=json.loads(z.read('archived-file-hashes.json'))
assert len(previous)==401 and {n for n,h in previous.items()if sha(ROOT/n)!=h}=={'README.md'}
OUT.mkdir()
report=dict(status='preparation-running-not-accepted',parent=OLD.name,
    created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),goal_complete=False,
    patch_sha256=sha(patch),roms={},tests_complete=False)
rp=OUT/'candidate.json'
def save():rp.write_text(json.dumps(report,indent=2)+'\n')
save()
subprocess.run(['git','apply','--check',str(patch)],cwd=ROOT,check=True)
subprocess.run(['git','apply',str(patch)],cwd=ROOT,check=True)
assert (ROOT/'src/native_goomba_draw.s').read_text()==(packet/'native_goomba_draw.s').read_text()
for mapper in('mmc3','mmc5'):
    with(OUT/f'build-{mapper}.log').open('w')as f:
        subprocess.run([sys.executable,'tools/build.py','--mapper',mapper],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True)
    for ext in('.nes','.lbl','.dbg','.map','.lst'):
        p=ROOT/f'build/smb-crossover-{mapper}{ext}';shutil.copyfile(p,OUT/p.name)
    rom=OUT/f'smb-crossover-{mapper}.nes'
    a=(OLD/rom.name).read_bytes();b=rom.read_bytes()
    assert a[:16]==b[:16]and a[16+524288:]==b[16+524288:]
    if mapper=='mmc3':assert a==b
    dbg=rom.with_suffix('.dbg').read_text()
    s=re.search(r'seg\s+[^\n]*name="METASPRITE",start=(0x[0-9A-Fa-f]+),size=(0x[0-9A-Fa-f]+),[^\n]*ooffs=(\d+)',dbg)
    assert s and int(s[1],16)==0xa000
    size=int(s[2],16);assert size==(8068 if mapper=='mmc5' else 8182)
    report['roms'][mapper]=dict(sha256=sha(rom),dbg_sha256=sha(rom.with_suffix('.dbg')),
        lbl_sha256=sha(rom.with_suffix('.lbl')),metasprite_bytes=size,metasprite_free=8192-size,
        identical_to_parent=a==b,chr_identical=True)
    save()
files={n:sha(ROOT/n)for n in sorted(set(previous)|{'src/native_goomba_draw.s'})}
assert {n for n in previous if files[n]!=previous[n]}=={'README.md','src/entrypoint.s','src/metasprite_engine.s'}
archive=OUT/'source-v47a.zip'
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
    for n in files:z.writestr(n,(ROOT/n).read_bytes())
    z.writestr('archived-file-hashes.json',json.dumps(files,indent=2)+'\n')
report.update(status='provisional-not-accepted',source_count=len(files),archive_sha256=sha(archive),
    changed_sources={n:files[n]for n in('src/entrypoint.s','src/metasprite_engine.s','src/native_goomba_draw.s')},
    scope='MMC5 immutable walking-Goomba Ptr/interior/header8 unrolled rendering only; shared generic fallback/postpasses unchanged.',
    limits=['Actual compiled ABI/OAM equivalence and native receipts pending.','No measured frame-rate/visibility benefit yet.',
            'Crowd/DMA/PPU, broader regression, source rebuild and wider goal remain pending.'])
save();print(json.dumps(report,indent=2),flush=True)
