"""Compact source-only checkpoint for qualified cumulative M3/shared and layout stages."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2]
P=R/'build/m3-cfbt-source-join-v1';S=R/'build/m3-cfbt-gfx-layout-v1';J=S/'joint'
O=R/'docs/qa/checkpoints/2026-10-31/m3-current-cfbt-source-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,q):p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
def check(p):
 q=json.loads(p.read_text(encoding='utf-8'))
 if'passed'in q:assert q['passed'],p
 for n,h in q.get('bindings',{}).items():assert sha(n)==h,(p,n)
 return q
def main():
 assert not O.exists();q=check(S/'source-stage.json');check(P/'qualification.json')
 assert q['passed']and q['changed_ROM_bytes']==0 and q['candidate']=='79634f4581f223293a86d2bae28a0cc8ad05949a24f29695433b806eccf6a4b3'
 plan=R/'build/m3-cfbt-source-join-plan-v2';check(plan/'plan.json')
 files={Path(__file__)}
 names=['plan_m3_cfbt_source_join_1031_v1.py','plan_m3_cfbt_source_join_1031_v2.py','prepare_m3_cfbt_source_join_1031_v1.py','check_m3_cfbt_source_join_1031_v1.py','check_m3_cfbt_pointer_vectors_1031_v1.py','prepare_m3_cfbt_gfx_layout_1031_v1.py']
 files.update(R/'tools/audit'/n for n in names)
 files.update(p for p in plan.iterdir()if p.is_file())
 files.add(R/'build/m3-cfbt-source-join-plan-v1/recipe-negative.json')
 for root in[P,S]:
  files.update(p for p in root.iterdir()if p.is_file()and p.suffix=='.json')
 for n in['entrypoint.s','private.cfg','union.s','src/character_select.s','src/full_roster_menu.s','src/new_roster_dispatch.s','src/smb3_mario_motion.s','src/smb3_mario_render.s','src/smb3_native_controller.inc','src/smb3_mario_art.inc','src/smb3_mario_dispatch.s','src/smb3_mario_world_art.inc','smb3plus_body_host.s','smb3plus_kick_host.s','smb3plus_float_state.inc','smb3plus_float_data.s','smb3plus_menu_name.s','smb3plus-chr.s','toad-smb3plus-body.chr','peach-smb3plus-body.chr','main.dep','union.dep']:
  files.add(P/'joint'/n)
 for n in['private.cfg','src/smb3_mario_art.inc','src/smb3_mario_world_art.inc','smb3plus_float_data.s','main.dep']:
  files.add(J/n)
 predecessors=[R/'build/bt-native-world-source-v2/handoff.json',R/'build/bt-native-world-source-v2/integration-api.json',R/'build/bt-native-world-source-v2/final-link.json',R/'build/bt-current-cf-component-v2/main-build.json',R/'build/cf-bt-shared-transport-v3/union-build.json',R/'docs/qa/checkpoints/2026-10-31/smb3plus-low-table-factor-v1/handoff.json',R/'docs/qa/checkpoints/2026-10-31/contra-force-p1-experimental-resources/native-restore-factor-grant-v1.json']
 files.update(predecessors)
 O.mkdir(parents=True)
 own=dict(source_base=str(J),source_candidate=q['candidate'],native=False,installed=False,readiness_changed=False,canonical_edits=[],actual_Stage1_modified_producers=['five M3 modules','two surgical M3 Select/name hunks in current shared files','five appended M3 helpers','new50page source CHR object/currentCF_CHR_POST binding'],actual_Stage2_modified_producers=['src/smb3_mario_art.inc','src/smb3_mario_world_art.inc','smb3plus_float_data.s','private.cfg'],real_Stage2_main_recipe=str(S/'main-build.json'),real_union_recipe=str(P/'union-build.json'),real_final_recipe=str(S/'final-link.json'),CF67_worker_absent=True,CF67=[0xae97,0xaeda],remaining331_ability_bytes_untouched=True,private_built_files='All compiler/dependency/link/CFG sideoutputs validated within new private roots before execution.',archive_excludes=['NES','objects','executables','large DBG/map','parent37MBarchive'],inherited_source='Final9b b5dd handoff + e54 fea3 factor checkpoint, both immutable and hashbound. Source snapshot and recipe inputs retained, never old wholeunion or oldcfg overlays.')
 put(O/'owned-files.json',own);files.add(O/'owned-files.json')
 (O/'README.txt').write_text('''Qualified cumulative M3 e54 source joins frozen CF/BT9b source. Stage1 genuinely rebuilds current main, true46groupunion and M3 CHR. Full disjoint-source oracle matches; all4671old objectexports and qualifiedM3PCs survive. All parent currentCF/BT/BW/FF/Ar/Quick images/cookies/common contracts exact. Source checks:9072graphics,1344movement,2156originalpixels+112retaineddisabledKuribo,2016wholecontroller,81menus/768status,282current68Main(+0..6CPU),3364+812realvectors.

Stage2 real source prefix/67EA/existingRODATA split is BYTEIDENTICAL to Stage1:79634f4581f223293a86d2bae28a0cc8ad05949a24f29695433b806eccf6a4b3. All91803oldDBGvalues exact; only unconsumedRODATA linkerLOAD/RUN/SIZE metadata changes. All86actualparentobjects had0RODATA/noimports. Main stays256segments. All3 emittingdirectives retargeted. Real legacyM3LOAD/RUN/SIZE C000/C000/13FD = actualprefixE97+67+suffix523 retains audio2.o assertion<=1400.

CF67remains67EA/no worker;331M3abilitybytes untouched. BT/CFremain pending; source names/ready admission/native decisions belong to root. Actual Mesen was never launched, Downloads/canonical/Gitindex untouched. New67worker andFF/P1factor must be a later reviewed source join. Unfinished M3groundpound/customstomp/specialart/kickSFX not claimed. Prior wrongCHRrecipe assumption andca65257 design negative retained in plan/evidence; no frozen input normalized.
''',encoding='utf-8');files.add(O/'README.txt')
 manifest={p.relative_to(R).as_posix():sha(p)for p in sorted(files)};archive=O/'source-and-controls.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for p in sorted(files):z.write(p,p.relative_to(R).as_posix())
 with zipfile.ZipFile(archive)as z:
  assert len(z.namelist())==len(manifest)
  for n,h in manifest.items():assert hashlib.sha256(z.read(n)).hexdigest()==h
 put(O/'source-members.json',manifest)
 bound=files|{archive,O/'source-members.json',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',J/'main.o',J/'union.o'}
 final=dict(status='FROZEN_GENUINE_M3_FINAL_CFBT_SOURCE_AND_BYTE_IDENTICAL_LAYOUT',candidate=q['candidate'],source=True,native=False,installed=False,CF_BT_pending=True,CF67_worker_absent=True,all_parent_contracts_and_current68_M3_preserved=True,Stage1_qualification=sha(P/'qualification.json'),Stage2_proof=sha(S/'source-stage.json'),archive_members=len(manifest),archive_bytes=archive.stat().st_size,bindings={str(p.resolve()):sha(p)for p in sorted(bound)})
 put(O/'handoff.json',final);check(O/'handoff.json');print(json.dumps(dict(handoff=str(O/'handoff.json'),sha256=sha(O/'handoff.json'),members=len(manifest),bindings=len(final['bindings']),bytes=archive.stat().st_size)))
if __name__=='__main__':main()
