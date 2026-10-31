"""Compact mutually hash-consistent source/CPU checkpoint for BT repair."""
from pathlib import Path
import hashlib,json,sys,zipfile
R=Path(__file__).resolve().parents[2]
J=R/'build/bt-lives-body-source-v5/joint';S=J.parent
C=R/'build/bt-lives-body-controls-v2'
O=R/'docs/qa/checkpoints/2026-10-31/bt-lives-body-source-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,q):p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8',newline='\n')
def main():
 assert not O.exists();O.mkdir(parents=True)
 inputs=[S/'source-stage.json',*[C/(n+'-controls.json')for n in['natural','callers','pixels','vectors','foreign','menu']],C/'foreign-main/controls.json']
 bindings={};notes=[]
 for p in inputs:
  d=json.loads(p.read_text());assert d.get('passed',d.get('source')),p
  for n,h in d['bindings'].items():assert sha(n)==h,(p,n);bindings[str(Path(n).resolve())]=h
  bindings[str(p.resolve())]=sha(p)
 assert sha(J/'candidate.nes')=='998728bab4b5737dcca3663568960a6199adf3e7af36ddfeae8b867efe281f7b'
 parent=R/'build/contra-force-p1-coherent-cart-v2/source-stage.json'
 pd=json.loads(parent.read_text())
 for n,h in pd['bindings'].items():assert sha(n)==h,n;bindings[str(Path(n).resolve())]=h
 members=set(inputs+[Path(__file__),R/'tools/audit/prepare_bt_lives_body_1031_v5.py',R/'tools/audit/check_bt_lives_body_1031_v2.py',R/'tools/audit/check_bt_lives_body_menu_1031_v1.py',J/'candidate.cfg'])
 members.update(S.glob('*.json'))
 members.update(p for p in (J/'bt').rglob('*')if p.suffix in['.s','.inc','.bin'])
 # Earlier builder/caller diagnostics stay explicit negatives, never relabeled.
 for v in range(1,5):
  name='prepare_bt_lives_colors_1031_v1.py'if v==1 else f'prepare_bt_lives_body_1031_v{v}.py'
  p=R/'tools/audit'/name
  if p.is_file():members.add(p)
 for p in [R/'build/bt-lives-colors-source-v1/negative.json',R/'build/bt-lives-body-source-v2/negative.json',R/'build/bt-lives-body-source-v3/negative.json',R/'build/bt-lives-body-controls-v1/natural-controls.json',R/'build/bt-lives-body-controls-v1/pixels-controls.json']:
  if p.is_file():members.add(p);notes.append(dict(path=str(p),sha256=sha(p)))
 for p in members:bindings[str(p.resolve())]=sha(p)
 archive=O/'source-and-controls.zip';entries={}
 with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for p in sorted(members):
   assert p.suffix.lower()not in['.nes','.o','.exe']
   name=p.relative_to(R).as_posix();data=p.read_bytes();z.writestr(name,data);entries[name]=dict(sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
 save(O/'archive-members.json',entries)
 owned=[p.relative_to(R).as_posix()for p in sorted(members)if '/bt-lives-'in p.as_posix()or p.name in['freeze_bt_lives_body_1031_v1.py','check_bt_lives_body_1031_v2.py','check_bt_lives_body_menu_1031_v1.py','prepare_bt_lives_body_1031_v5.py']]
 (O/'owned-files.txt').write_text('\n'.join(owned)+'\n',encoding='utf-8',newline='\n')
 (O/'README.md').write_text('''# Battletoads source repair checkpoint

Exact candidate `998728bab4b5737dcca3663568960a6199adf3e7af36ddfeae8b867efe281f7b` is a source-built child of immutable CF P1 composition `fbbc7b89`. No native launch or installation was performed by this lane.

The genuine lives A1/Y30 continuation appends only original BT P0/P1 body shades after the complete native 30-byte text packet. Actual early DrawAll invokes the source graphics preparation once before the original source body renderer. That preparation publishes an own zero descriptor with its genuine C3 bank; the old QwEmpty34 pointer under C45 could misalign the native post-shot reservation. No movement, attacks, terrain, health, original art or palette values changed.

Finite CPU evidence: 2560 true WriteGameText caller pairs preserve native AXYP/SP, four actual menu/Start/native parser cohorts and 160 visible Main updates, all 96 basic source-pose pixel pairs, 410 actual ISR seams, all 86 menu profiles/688 Start-A boundaries, and 282 current foreign Main cases with zero CPU delta. All source-stage/control bindings were rehashed immediately before this archive.

The native f0b7 lives-palette and invisible-player negatives remain root-owned. Earlier local builder diagnostics and the dfa9 wrong-C-bank/old cold-color-fixture negatives are retained. The P2 native LUIGI header overwrite is still an explicit cosmetic limitation here; root approved a separate 21-byte same-span caller guard for the following coherent CF/BT child. No completed campaign, original full moveset, music, or 60Hz claim is made.

Rebuild from `tools/audit/prepare_bt_lives_body_1031_v5.py`; actual guarded final recipe is `build/bt-lives-body-source-v5/final-link.json`, config `joint/candidate.cfg`. Parent object/source closure is bound transitively through the immutable fbbc stage. The ZIP contains source/recipes/generated cache source assets and receipts, no NES, EXE or object files.
''',encoding='utf-8',newline='\n')
 for p in [archive,O/'archive-members.json',O/'owned-files.txt',O/'README.md']:bindings[str(p.resolve())]=sha(p)
 save(O/'handoff.json',dict(passed=True,source=True,native=False,installed=False,candidate=sha(J/'candidate.nes'),parent=pd['candidate'],
   counts=dict(WriteGameText=2560,natural_cohorts=4,visible_Main=160,source_pixel_pairs=96,real_vectors=410,menu_profiles=86,Start_A=688,foreign_Main=282),
   foreign_CPU_delta=[0,0],source_shared_other_bytes_exact=True,CF_pending=True,P2_header_cosmetic_pending=True,
   local_diagnostics=notes,archive_members=len(entries),archive_bytes=archive.stat().st_size,bindings=bindings))
 print(json.dumps(dict(passed=True,handoff=str(O/'handoff.json'),sha256=sha(O/'handoff.json'),bindings=len(bindings),archive_members=len(entries),archive_bytes=archive.stat().st_size)))
if __name__=='__main__':main()
