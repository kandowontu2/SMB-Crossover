from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[2];O=R/'build/verification/score-anchor-standard-call-al';assert not O.exists();O.mkdir()
names=['src/score_popup.s','src/collision.s','smb1base.cfg']+[f'build/smb-crossover-{m}.nes'for m in ('mmc3','mmc5')]
for n in names:
 p=O/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,p)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(O/'manifest.json').write_text(json.dumps(dict(classification='Unadmitted standard-farcall prototype; replace with the existing selector/flags-preserving rare-call ABI before native testing.',hashes={n:sha(O/n)for n in names},allocation_successor='BFC0..BFFF,64B for score; RyuB700..BFBF2240B; current F endsB9D4 and is unchanged.'),indent=2)+'\n',encoding='utf-8')
