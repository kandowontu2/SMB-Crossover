"""Freeze actual final62 source/targeted controls for root native qualification.

No assembler/linker/native process is launched. Inherited build logs copied
inside joint are historical; only this stage's top-level command logs are
the new compilation recipe. Every immutable input is hash bound.
"""
from pathlib import Path
import json,re,zipfile
import prepare_functional_roster_visuals58_v1 as B

R=B.R;O=R/'build/functional-roster-coherent62-v4';J=O/'joint'
C=R/'docs/qa/checkpoints/2026-10-30/functional-roster-coherent62-source'

def resolved(p):
 p=Path(p);return(p if p.is_absolute()else R/p).resolve()

def dep_inputs(p):
 text=B.read(p)
 assert ':\t'in text,('unknown dependency syntax',str(p))
 line=text.split(':\t',1)[1].splitlines()[0]
 rows=[]
 for token in re.split(r'(?<!\\)\s+',line):
  if token:
   q=resolved(token.replace('\\ ',' '));assert q.is_file(),str(q);rows.append(q)
 return rows

def main():
 assert not(O/'handoff.json').exists()and not C.exists()
 controls=[O/'menu-controls-v2.json',R/'build/ff-coherent62-cold-controls-v1/controls.json',R/'build/smb2-final62-cold-controls-v30/controls.json',R/'build/smb2-final62-cold-controls-v30/lives-palette-v2.json']
 for p in controls:
  d=json.loads(B.read(p));assert d['passed'],str(p);B.bound(d)
 roots=[R/'build/functional-roster-visuals58-v1/handoff.json',R/'build/ff-cold-preview-v5/handoff-source-v1.json',R/'build/smb2-current-cold-render-v29/handoff.json',R/'build/smb2-final62-cold-controls-v30/handoff.json']
 for p in roots:B.bound(json.loads(B.read(p)))
 stage=json.loads(B.read(O/'source-stage.json'));B.bound(stage)
 assert stage['candidate']=='408acae2712c1d9bbbe34233f8261fcf27723907d37acf020e3f5314be3b8604'
 assert json.loads(B.read(controls[0]))['ready_counts']==[58,62]
 # Exact real final-link inputs plus current producer dependency closure.
 deps=set();commands=[]
 for p in sorted(O.glob('*-build.json'))+sorted(O.glob('*-link.json')):
  d=json.loads(B.read(p));assert d['returncode']==0,(str(p),d)
  commands.append(p);c=d['command']
  for flag in ['--create-full-dep','--create-dep']:
   if flag in c:
    q=resolved(c[c.index(flag)+1]);deps.add(q);deps.update(dep_inputs(q))
  if c[-1].endswith('.s'):deps.add(resolved(c[-1]))
  for x in c:
   if x.endswith('.o'):
    q=resolved(x);assert q.is_file(),str(q);deps.add(q)
    for ext in ['.dep','.d']:
     dep=q.with_suffix(ext)
     if dep.is_file():deps.add(dep);deps.update(dep_inputs(dep))
  if '-C'in c:deps.add(resolved(c[c.index('-C')+1]))
 deps.add(J/'dmc-clones.s');deps.add(J/'final127.bin')
 # Preserve actual current generated producer sources even when they are
 # represented by read-only inherited objects in this last targeted link.
 text_suffix={'.s','.inc','.cfg'}
 deps.update(p for p in J.rglob('*')if p.is_file()and p.suffix in text_suffix)
 closure=dict(passed=True,native=False,candidate=stage['candidate'],recipe_logs=[str(p.relative_to(R))for p in commands],inherited_joint_build_logs_are_historical=True,bindings={str(p.resolve()):B.sha(p)for p in sorted(deps)})
 B.write(O/'source-closure.json',json.dumps(closure,indent=2)+'\n')
 tools=[R/'tools/audit'/n for n in ['prepare_functional_roster_coherent62_v1.py','prepare_functional_roster_coherent62_v2.py','prepare_functional_roster_coherent62_v3.py','prepare_functional_roster_coherent62_v4.py','functional_roster_coherent62_menu_v1.py','functional_roster_coherent62_menu_v2.py','freeze_functional_roster_coherent62_v1.py']]
 helper=R/'tools/audit/private_build_outputs_v1.py';tools.append(helper)
 notes='''# Coherent62 source, exact native qualification pending

Actual source-linked ROM408acae2712c1d9bbbe34233f8261fcf27723907d37acf020e3f5314be3b8604
combines frozen visual58 (root410 RCR/Chip, current DK thumb, corrected
gray/pending facings, Quick/Arthur markers, Goku and Gimmick cold portraits)
with genuine final FF334b and SMB2v29 owned producers. No binary overlay,
new lease, native run, Downloads install or canonical source edit occurred.

Actual80 menu profiles and160 Start/A boundaries pass:62ready/18pending;
all58 previous ready profiles remain ready. The four FF classes are newly
ready, and FF/SMB2 names use full16-character marker-free SELECT labels.
Arthur remains menu31/raw32; Quick remains menu9/alternate2/raw9/bit20.
The future Arthur/Goku/Battletoads remap is NOT included.

Actual current-cart FF tests pass four cold bodies/OAM/physicalCHR/P0,
four real black-backdrop lives, native new-game/loader/parser/entrance,
and128 Main TOTAL (32/class) with movement/weapons/early draw once.
Actual current SMB2 tests pass8 class/rules cold/parser cohorts, selected
and lives5-part source bodies/full names,8 real Main/NMI pairs per cohort,
and8 lives normal-NMI body-P0/black checks. SMB2 P1 eye-role/native palette
is logged as pending, not claimed proven. Native all8 review is next.

Cold chain: FwMuxMenuResolve -> FF retirement -> S2MenuResolve ->
QwMenuResolve -> ArGenResolve -> FmResolve. Screen: S2InitScreenPrepare ->
QwSceneInit -> ArGenSceneInit -> FwSceneInit -> native Move exactly once.
Service19 remains native JnResetDispatch -> S2MainScene, distinct from
screen InitScreen. The inherited A79 typed islands, public PCs and current
family5FFF/NMI protocol are preserved. Quick/Arthur WRAM payloads remain
exact, final FF version9 payload/cookie matches frozen334b. Final127 is
genuinely rebound into119/120 sample clones and125 mirror regenerated.

Historical failures are retained: v1 basename object replacement confused
Quick and FF stream.o; v2 incorrectly assumed all DMC inputs werefinal127
instead of also original SMB2 samples; menuv1 incorrectly expected WWF
indices18..21 for FF (actual5..8). Correct successors alter only those
fixture/preparation assumptions. Prior empty S2 cold and FF wrong sprite
read-view negatives remain in their immutable predecessor packets.

Top-level *-build.json/layout-link.json/final-link.json are authoritative
actual commands for this stage. Commands copied inside joint are history.
All output/dependency/CFG destinations passed private_build_outputs_v1
before compilation. Source closure binds exact real final-link objects,
producer dependencies and source paths. Archive contains source/evidence,
not ROM images, objects, DBG/LBL or large generated asset binaries.

Lag is disclosed, not an unlock veto under the user's current instruction.
No60Hz/all1-1/all-powerups/music/full completion claim is made. Existing
Quick/Arthur native functional smoke remains ancestral, final8-family
native visual/controller review still requires root's single-run grants.
'''
 B.write(O/'HANDOFF.md',notes)
 files=set(deps)|set(commands)|set(roots)|set(controls)|set(tools)
 files.update(p for p in O.glob('*')if p.is_file())
 for folder in ['ff-coherent62-cold-controls-v1','smb2-final62-cold-controls-v30']:
  files.update(p for p in(R/'build'/folder).glob('*')if p.is_file())
 # Retain preparation negatives without binding or copying old whole ROMs.
 for version in [1,2,3]:
  folder=R/f'build/functional-roster-coherent62-v{version}'
  files.update(p for p in folder.glob('*.json')if p.is_file())
 archive=O/'source-only.zip';archived=[]
 with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in sorted(files):
   if p.suffix in ['.py','.s','.inc','.cfg','.json','.md','.patch','.diff','.d','.dep']and p.is_relative_to(R):
    rel=p.relative_to(R).as_posix();z.write(p,rel);archived.append(rel)
 files.add(archive)
 for name in ['candidate.nes','candidate.dbg','candidate.lbl','candidate.map','ram3.bin','code.bin','data.bin','ff-cookie.bin','ff-stream.bin','final127.bin']:files.add(J/name)
 d=dict(status='FROZEN_SOURCE_READY62_EXACT_NATIVE_PENDING',candidate=stage['candidate'],source=True,native=False,installed=False,publication_allowed=False,ready=62,pending=18,profiles=80,all_previous58_preserved=True,FF_actual_Main_updates_TOTAL=128,SMB2_cold_class_rules_cohorts=8,SMB2_Main_NMI_pairs=64,SMB2_eye_P1_native_review_pending=True,performance_not_qualified=True,no_new_resource_leases=True,source_archive_members=len(archived),bindings={str(p.resolve()):B.sha(p)for p in sorted(files)})
 B.write(O/'handoff.json',json.dumps(d,indent=2)+'\n')
 C.mkdir(parents=True)
 for p in [O/'HANDOFF.md',O/'source-stage.json',O/'menu-controls-v2.json',O/'source.patch',O/'source-closure.json']:
  B.write(C/p.name,B.read(p))
 receipt=dict(status=d['status'],candidate=d['candidate'],ready=62,pending=18,profiles=80,native=False,installed=False,handoff=dict(path=str(O/'handoff.json'),sha256=B.sha(O/'handoff.json')),bindings={str(p.resolve()):B.sha(p)for p in sorted(C.iterdir())if p.is_file()})
 B.write(C/'receipt.json',json.dumps(receipt,indent=2)+'\n')
 owned=[p.relative_to(R).as_posix()for p in tools if p!=helper]+[p.relative_to(R).as_posix()for p in sorted(C.iterdir())if p.is_file()]
 B.write(O/'owned-files.txt','\n'.join(owned)+'\n')
 print(json.dumps(dict(candidate=d['candidate'],handoff_sha256=B.sha(O/'handoff.json'),bindings=len(d['bindings']),source_members=len(archived),source_archive_bytes=archive.stat().st_size,receipt_sha256=B.sha(C/'receipt.json'),status=d['status'])))

if __name__=='__main__':main()
