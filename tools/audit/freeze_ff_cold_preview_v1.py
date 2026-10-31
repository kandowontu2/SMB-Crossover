"""Freeze the genuine FF Only17 draw and actual lives palette successor."""
from pathlib import Path
import difflib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_ff_joint_source_v1 as B
P=R/'build/ff-current-names-v3';O=R/'build/ff-cold-preview-v5';J=O/'joint'
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8',newline='\n')
def main():
 out=O/'handoff-source-v1.json';assert not out.exists()
 files=B.validate(P/'handoff-source-v1.json','75f7baac5f70763aea759780620c48185db938775c36408b2c9efc9175826887')
 assert B.sha(J/'candidate.nes')=='334b291a929e81d12e25e2f067fe047fdd48f0cba9e58cdab2f0156f9ebd946d'
 for name in ['source-proof.json','controls-v2.json']:
  p=O/name;v=json.loads(p.read_text());assert v['passed'];files.add(p)
  for f,h in v.get('bindings',{}).items():assert B.sha(f)==h,f;files.add(Path(f))
 for version in range(1,6):
  stage=R/f'build/ff-cold-preview-v{version}'
  files|={f for f in stage.rglob('*')if f.is_file()}
  files.add(R/f'tools/audit/prepare_ff_cold_preview_v{version}.py')
 for name in ['ff_cold_preview_controls_v1.py','ff_cold_preview_controls_v2.py']:
  files.add(R/'tools/audit'/name)
 files.add(Path(__file__))
 link=json.loads((J/'final-link.json').read_text())['command']
 inputs=[Path(x)for x in link if x.endswith('.o')]
 for p in inputs:assert p.is_file();files.add(p)
 main=R/'build/ff-cold-preview-v2/joint/main-build.json'
 assert main.exists();v=json.loads(main.read_text());assert not v['returncode'];files.add(main)
 assert str(R/'build/ff-cold-preview-v2/joint/entrypoint.s')in v['command']
 assert str(R/'build/ff-cold-preview-v2/joint/main.o')in link
 assert '.export DrawMetasprite' in (R/'build/ff-cold-preview-v2/joint/entrypoint.s').read_text()
 patch=''
 for name in ['loader.s','veneers.s']:
  patch+=''.join(difflib.unified_diff((P/'joint'/name).read_text().splitlines(True),(J/name).read_text().splitlines(True),fromfile='named0369/'+name,tofile='corrected334b/'+name))
 (O/'source.patch').write_text(patch,encoding='utf-8',newline='\n');files.add(O/'source.patch')
 inv=dict(candidate=B.sha(J/'candidate.nes'),predecessor_gameplay_inventory=str(R/'build/ff-current-ready-v2/source-merge-inventory.json'),
  recipe_logs=[str(J/'final-link.json'),str(J/'loader-build.json'),str(R/'build/ff-cold-preview-v3/joint/veneers-build.json'),str(main)],
  recipes_are_evidence_not_replay_safe=True,guard='Rebase ALL compiler/link/dep/DBG/LBL/map/CFG MEMORY outputs beneath a NEW private root; validate with tools/audit/private_build_outputs_v1.py before any build.',
  full_owned_FF_sources=[str(J/n)for n in ['loader.s','veneers.s','ff-palette.s','ff-epoch-rom.inc','ff-epoch-workers.s','ff-palette-lifecycle.s','ff-palette-preflush.s','ff-world-marker.s','ff-cookie.bin','ff-stream.bin','ram3.bin']],
  actual_main_source=str(R/'build/ff-cold-preview-v2/joint/entrypoint.s'),
  main_source_changes=['Preserve current source and add genuine zero-byte .export DrawMetasprite.','MenuResolveCharacter actual operand->FwMuxMenuResolve.','Existing9B Samus NMI gateway operands->C93 preflush, retain full PN HUD/palette/Ar continuation.','Existing11B DrawMetasprite FF flash probe->complete world marker.','FF readiness SEC->CLC for four index21 variants; remove four FF pending stars only.'],
  live_service_rows={'2':'FwHostDrawShots EARLY gameplay, byte-exact predecessor','3':'FwPortrait metadata, unchanged','17':'FwPortraitDraw actual native DrawMetasprite, title AND lives','18':'FwMenuName genuine full16B class label','30':'FwStatusName A0 HUD; actual native lives A1/Y30 late colors'},
  explicit_own_ABI_retirements=['FwGlobalInit','FwMovement','FwPickup','FwStompPolicy','FwCollisionBounds','FwAdder','FwHead'],
  own_fixed_spans=['62:AC47..<AC5E23B menu','62:AC8C..<ACC052B labels','62:AD42..<AD7652B status','62:AD90..<ADC452B =33B portrait draw+19B lives colors'],
  cfg='No new split beyond frozen280ab epoch593B RAM3 holes and owned C93 protocol/marker tail. Retain all current S2/Quick/Ar/Roll/DMC/reader segments; do NOT replace whole current CFG.',
  mandatory_final_rebind='ff-palette-lifecycle.s genuine QwMenuResolve import/tail MUST become S2MenuResolve on final S2 tree; retain S2→Quick→Ar→Fm chain. Existing inner FwSceneInit remains once.',
  payload='RAM3/full8192B stream/full16B version9 cookie unchanged named0369/3754. Original FF CHR756..<788; carrier893..<901 is CODE, never art.',
  preserve_root_later_changes=['RCR409+Chip1','Quick/Ar ready-marker data repair','Celeste exact name','Goku authentic portrait1byte','latest DK/CF/Rogue menu artwork','SMB2/Roll/DMC/reader allocations'])
 save(O/'source-merge-inventory.json',inv);files.add(O/'source-merge-inventory.json')
 negatives=[dict(path=str(R/'build/ff-cold-preview-v2'),cause='Initial prototype changed service2; actual Only draw callback is17; genuine cold OAM remained empty. No native/admission.'),
  dict(path=str(R/'build/ff-cold-preview-v3/controls-v1.json'),cause='Correct row17 showed authentic body but true SRT7 lives native WriteGameText overwrote earlier queued FF colors; source palette assertion failed.'),
  dict(path=str(P/'native/thief-cold-v1'),cause='Old native observer wrongly expected Red for class3; genuine source class>=2 uses Blue. Retained native failure; no source bug inferred.'),
  dict(path=str(P/'native/fighter-cold-v1/class-cold-menu.png'),cause='Old native preview empty; source-caller trace identified metadata-only service17.')]
 (O/'README-source.md').write_text('''Corrected FF four-class UI source; native validation pending.

Actual Only callback17 now publishes original body0 and calls genuine native
DrawMetasprite. Metadata3 and early gameplay DrawShots2 remain unchanged.
All8 class/option cold callers prove original descriptor/OAM/pixels/final
hardware CHR. Actual native lives WriteGameText A1/Y30 now appends a complete
class palette after text overwrites the earlier packet, preserving the genuine
black lives backdrop. All4 real cold loader/parser/entrance/lives/128Main and
80 menu profiles pass strict source controls (58ready/22pending in this base).

The obsolete own Adder/Head gates are explicitly retired, with zero real-object
imports; their52B holds33B draw plus19B lives colors. All live public entries,
header/CHR/payload/cookie remain exact. Previous wrong-row and lives-palette
negatives remain immutable. Earlier native first3 gameplay passes are0369-
scoped; the old Thief observer failure remains, and this334b has NO native run.

Final coherent62 merge must preserve all current root/S2/Quick/Ar fixes and
tail actual S2MenuResolve after FF retirement; source recipes are evidence,
not replay-safe commands. See source-merge-inventory.json for all owned inputs.
''',encoding='utf-8',newline='\n');files.add(O/'README-source.md')
 d=dict(passed=True,status='PRIVATE_FF4_CORRECTED_SELECT_LIVES_SOURCE_NATIVE_PENDING',native=False,admitted=False,installed=False,
  candidate=B.sha(J/'candidate.nes'),parent_named0369=B.sha(P/'joint/candidate.nes'),
  FF_RAM3_sha256=B.sha(J/'ram3.bin'),cookie=list((J/'ff-cookie.bin').read_bytes()),
  checks=dict(actual_cold_Only17=8,true_lives_classes=4,actual_cold_classes_Main128=4,menu_profiles=80,ready_in_own_parent=58),
  retired_own_ABI=inv['explicit_own_ABI_retirements'],retained_negatives=negatives,
  source_merge_inventory=dict(path=str(O/'source-merge-inventory.json'),sha256=B.sha(O/'source-merge-inventory.json')),
  bindings={str(p.resolve()):B.sha(p)for p in sorted(files)})
 save(out,d);print(json.dumps(dict(path=str(out),sha256=B.sha(out),candidate=d['candidate'],bindings=len(files))))
if __name__=='__main__':main()
