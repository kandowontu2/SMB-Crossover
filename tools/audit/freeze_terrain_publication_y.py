from pathlib import Path
import shutil,json,hashlib,subprocess
R=Path(__file__).resolve().parents[2];O=R/'build/checkpoints/terrain-publication-o';assert not O.exists();O.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
names=[f'build/smb-crossover-{m}.{e}'for m in ('mmc3','mmc5')for e in ('nes','lbl','dbg','map')]
names+=['src/game.s','src/guest_body_contact.s','src/terrain_catchup.s','tests/terrain-coin-publication.lua','tools/verify.py']
for n in names:
 p=O/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,p)
source={p.relative_to(R).as_posix():sha(p)for p in (R/'src').rglob('*')if p.is_file()}
report=dict(parent_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),scope='Terrain publication repair only. Existing fixed route timings need retiming; this is not a final all-character release.',hashes={n:sha(O/n)for n in names},source_hashes=source,ROMs={m:sha(R/'build'/f'smb-crossover-{m}.nes')for m in ('mmc3','mmc5')},native_regression_sha256=sha(R/'build/verification/terrain-coin-queue-q/summary.json'),build_regression_sha256=sha(R/'build/verification/terrain-repair-build-v/summary.json'),goal_complete=False)
(O/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('FROZEN',O,report['ROMs'])
