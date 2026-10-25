from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[2];O=R/'build/checkpoints/score-anchor-before-al';assert not O.exists();O.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
af=R/'build/checkpoints/terrain-publication-af/manifest.json';m=json.loads(af.read_text())
for mapper,h in m['ROMs'].items():assert sha(R/'build'/f'smb-crossover-{mapper}.nes')==h
names=['src/collision.s','src/entrypoint.s','smb1base.cfg']+[f'build/smb-crossover-{m}-baseline.nes'for m in ('mmc3','mmc5')]
for n in names:
 p=O/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,p)
report=dict(parent_checkpoint_sha256=sha(af),hashes={n:sha(O/n)for n in names},allocation={'bank':36,'existing_C_graphics':'C000..D5FF; every old byte retained','A_tail':'B600..BFFF; same physical bank, standard A-only farcall','Water_reserved':'B600..B6FF unchanged','Ryu_reserved':'B700..BFDF; private frozen F currently endsB9D4','score_reserved':'BFE0..BFFF,32B; target body27B','reason':'MMC5 OBJECT bank0 has only2free bytes. Use the existing root-approved physical-tail partition instead; shrink the unused far end of the Ryu reservation by32B. No existing frozen Ryu bytes overlap.'},scope='Back up AF source/config and literal baseline ROMs before the score-anchor fix. No runtime change yet.')
(O/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PRE_SCORE_AL',len(names))
