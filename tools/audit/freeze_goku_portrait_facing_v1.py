"""Freeze the isolated Goku portrait-facing source leaf and negatives."""
from pathlib import Path
import json,zipfile
import prepare_goku_portrait_facing_source_v1 as B
R=B.R;O=R/'build/goku-portrait-facing-source-v3'

def verify(p):
 d=json.loads(p.read_text())
 for name,digest in d.get('bindings',{}).items():assert B.sha(name)==digest,name
 assert d.get('passed',True),p
 return d

def main():
 assert not(O/'handoff.json').exists()
 proof=verify(O/'source-proof.json');checks=verify(O/'portrait-controls.json')
 # Both failed preparations remain separate and unchanged; the output guard
 # rejected the first before any compiler was called. The next compiler
 # rejected only the absolute include syntax, with no old outputs touched.
 negatives=[dict(directory='build/goku-portrait-facing-source-v1',stage='output-preflight',error='Rejected inherited --ld-args --dbgfile outside new private root; no compiler executed.'),dict(directory='build/goku-portrait-facing-source-v2',stage='compile',error='cc65 rejected absolute include path; compile.json retained; no link/native executed.')]
 (O/'negatives.json').write_text(json.dumps(negatives,indent=2)+'\n')
 text='''# Goku cold portrait facing

This genuine source leaf changes only DpAdmissionPortrait's standing record
immediate0→1. The original executable renderer's record0 points left and
record1 points right; source-standing-both.png shows both original pixel
sets. Exact ROM/OAM/pixel hashes are in source-proof.json. Actual source
palette roles are used for the witness; this is not a native RGB capture.

Moving Goku already maps original positive horizontal→right and negative→left.
All32poses×2sourcefacings and all attack/physics bytes remain exact. Actual
cold title/lives portrait calls pass128mode/flag cases, selecting record1.
No movement, controls, damage, projectile direction, menu metadata or resource
lease changes. Thomas and SMB3Bowser pending preview flips belong to root's
separate UI leaf; they have no admitted gameplay host renderer in this cart.

The candidate is an isolated successor of68cbe with exactly1ROMbyte changed,
physicalPRG86 PC$BEF8,0→1. All symbol values stay exact. Root can adopt only
admission.inc's source hunk into the actual Goku component and genuinely
reassemble/link; a whole-ROM overlay is unnecessary. No native or installation.

Two preparation negatives are retained: output guard rejection before a
compiler, then absolute-include compile rejection. V3 uses a relative genuine
include and prevalidated private outputs. Frozen predecessor packets remain
read-only. The new Battletoads/Goku Select request is unrelated and queued.
'''
 (O/'HANDOFF.md').write_text(text,newline='\n')
 tools=[R/'tools/audit'/n for n in ['prepare_goku_portrait_facing_source_v1.py','prepare_goku_portrait_facing_source_v2.py','prepare_goku_portrait_facing_source_v3.py','goku_portrait_facing_controls_v1.py','freeze_goku_portrait_facing_v1.py','private_build_outputs_v1.py']]
 files=[p for p in O.rglob('*')if p.is_file()]+tools
 for q in [R/'build/goku-portrait-facing-source-v1',R/'build/goku-portrait-facing-source-v2']:
  files.extend(p for p in q.rglob('*')if p.is_file())
 source=[p for p in files if p.suffix in ['.s','.inc','.py','.json','.cfg','.md','.patch','.png','.d']]
 with zipfile.ZipFile(O/'source-only.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in source:z.write(p,p.relative_to(R).as_posix())
 files.append(O/'source-only.zip')
 d=dict(status='FROZEN_SOURCE_PORTRAIT_ONLY',candidate=proof['candidate'],parent=proof['parent'],native=False,installed=False,ROM_bytes_changed=1,actual_cold_portrait_cases=128,moving_source_pose_pairs_exact=64,all_public_PCs_and_gameplay_attack_bytes_exact=True,bindings={str(p.resolve()):B.sha(p)for p in files})
 (O/'handoff.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(dict(handoff=B.sha(O/'handoff.json'),bindings=len(d['bindings']),candidate=d['candidate'])))
if __name__=='__main__':main()
