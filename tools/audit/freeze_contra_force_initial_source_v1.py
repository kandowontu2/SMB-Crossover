"""Freeze bounded authentic-source milestones before CF host integration."""
from pathlib import Path
import hashlib,json,sys,zipfile
R=Path(__file__).resolve().parents[2]
O=R/'build/contra-force-initial-source-qualified-v1'
D=R/'docs/qa/checkpoints/2026-10-30/contra-force-initial-source'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):
 assert not p.exists(),p
 p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
def verify(h):
 for p,v in h.get('bindings',{}).items():assert sha(p)==v,p
def main():
 assert not O.exists()and not D.exists();O.mkdir();D.mkdir(parents=True)
 fetch=R/'build/contra-force-source-v1/source-fetch.json';f=json.loads(fetch.read_text())
 repro=R/'build/contra-force-reproduction-v2/proof.json';r=json.loads(repro.read_text());assert r['passed'];verify(r)
 probe=R/'build/contra-force-engine-probe-v5/controls.json';p=json.loads(probe.read_text());assert p['passed'];verify(p)
 assert sha(probe)=='c562172ed783cfc4a7242fafc6d35ce7fe7781a848785a613a9d39d21862c9b6'
 parent=R/'build/coherent62-lives-fixes-v1/handoff.json';h=json.loads(parent.read_text());verify(h)
 assert h['candidate']=='dfdb194ac73438ae8deb05b5fc93f241b1109d45a84b3ad333d0e632008d7fc7'
 for e in f['entries']:assert sha(e['path'])==e['sha256']
 tools=[R/'tools/audit'/n for n in ['prepare_contra_force_source_v1.py','reproduce_contra_force_source_v1.py','reproduce_contra_force_source_v2.py',*[f'contra_force_engine_probe_v{v}.py'for v in range(1,6)],'freeze_contra_force_initial_source_v1.py']]
 negatives=dict(source_reproduction_v1='Annotation guard falsely matched exported labels containing0x; stopped before compiler. v2 checks complete annotated address syntax, exact fullPRG reproduction passes.',probe_v1='Source-bank hardwarepair was changed without original source ram_prg_banks_pair36; original animation script restoredpair0 and returned into data. v2 seeds genuinepair2 before source calls.',probe_v2='Wrong projectile inventory0782[2..9] missed genuine player shots0682[10..17]. Native shotcount1 was real; v3 checks actual source0682 slots.',probe_v4='Tool-lineage binding exporter confused original reproduction directory P with wrapper-tool P; PermissionError after CPU execution. v5 binds actual source files explicitly.',all_prior_artifacts_preserved=True)
 save(O/'retained-negatives.json',negatives)
 api=dict(status='MEASURED_ORIGINAL_SOURCE_API_NOT_RELOCATED_HOST',identity=dict(menu_slot=30,raw=31,variant_byte='FmGroups=$5FE8 bits3..4',names=['Burns','Smith','Iron','Beans'],start_gap='Current FmStartFlags clears all FmGroups. Future selected slot30 must preserve18 only; BTslot23 uses20 and requires coordinated composition.'),original_entries=dict(input=dict(bank_pair=[4,5],address='A2E7'),movement_pose_weapon_spawn=dict(bank_pair=[4,5],address='A538'),clear_source_delta=dict(fixed_address='F640'),position_integration=dict(bank_pair=[0,1],address='BCE0'),source_animation_parser=dict(bank=4,address='9762',nested_script24_data_bank=6,source_shadow='0036')),source_motion=dict(horizontal_8_8=[312,304,288,319],tapA_updates=1,tap_apex_pixels=[4,4,4,4],heldA_updates=20,observed_held_apex_pixels=[55,50,45,53],not_maximum_hold_or_64px_pipe_proof=True),actual_source_weapon_kinds_by_class_gear=[[1,2,14],[1,12,4],[1,3,5],[1,13,7]],contact_scope='Only explicit flat-floor/air07D2 arena inputs. No native SMB collision/platform/pipe/flagpole callback installed or proven.',unimplemented=['Relocatable source core and conservative state projection','Authentic full-body/effect decoder and per-pose hardware page pack','SMB terrain/head/feet/side/pipe/platform/flagpole/progression adapters','Lifecycle constructor/retire/two-player save/load and shared selected31 routes','Actual menu readiness and native cold/controller qualification'],resources=dict(granted=False,PRG_RAM_CHR_reserved_by_this_packet=False,avoid_current_Benj_CHR='901..<915',avoid_current_BT_CHR='915..<927',possible_temporal_RAM1_C2_requires_explicit_owner_review=True),authentic_art=dict(existing_frozen_menu_manifest=str(R/'build/contra-force-body-art-v6/manifest.json'),no_new_art_or_palette_approximation=True,palette_candidate='Original P0[37,12,0F] plus lossless red16 source-mask parts via stable nativeP2index1; actual per-pose OAM/priority budget still unmeasured, not adopted.'))
 save(O/'api-and-host-gaps.json',api)
 files=set(tools)|{fetch,repro,probe,parent,O/'retained-negatives.json',O/'api-and-host-gaps.json'}
 files|={Path(e['path'])for e in f['entries']}|{Path(k)for k in r['bindings']}|{Path(k)for k in p['bindings']}
 files|={R/'build/contra-force-source-v1/tree.json',R/'build/contra-force-reproduction-v2/commands.json',R/'tools/audit/private_build_outputs_v1.py',R/'build/contra-force-body-art-v6/manifest.json'}
 for n in ['contra-force-engine-probe-v1/controls.json','contra-force-engine-probe-v2/controls.json','contra-force-engine-probe-v3/controls.json','contra-force-engine-probe-v4/preparation-negative.json']:
  files.add(R/'build'/n)
 own_handoff=dict(status='FROZEN_GENUINE_ORIGINAL_CF_SOURCE_AND_INITIAL_PLAYER_CPU_ONLY',source_commit=f['commit'],repository=f['repository'],source_tree=f['source_tree'],original_ROM_sha256=r['candidate_sha256'],current_shared_parent=h['candidate'],source_reproduction=dict(PRG_bytes=131072,changed_PRG_bytes=0,proof=str(repro)),CPU_scope=dict(walk_updates=96,jump_cohorts=8,A_hold_updates=[1,20],actual_source_weapon_allocation_cases=12,original_native_code_executed=True,world_contacts_explicit_arena=True),native=False,host=False,readiness=False,resource_grant=False,api=str(O/'api-and-host-gaps.json'),bindings={str(v.resolve()):sha(v)for v in sorted(files)})
 save(O/'handoff.json',own_handoff);verify(own_handoff)
 for n,src in [('handoff.json',O/'handoff.json'),('api-and-host-gaps.json',O/'api-and-host-gaps.json'),('retained-negatives.json',O/'retained-negatives.json'),('original-reproduction.json',repro),('player-controls.json',probe),('source-fetch.json',fetch)]:
  (D/n).write_bytes(src.read_bytes())
 # Include source and textual build evidence only; binary paths stay hash-bound.
 allowed={'.py','.asm','.s','.inc','.cfg','.lua','.sh','.bat','.json','.dep','.txt'}
 archive_inputs={v for v in files if v.suffix.lower()in allowed and v!=parent}
 archive_inputs.add(O/'handoff.json')
 archive=D/'source-only.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for v in sorted(archive_inputs):z.write(v,v.relative_to(R).as_posix())
 assert archive.stat().st_size<=4*1024*1024
 with zipfile.ZipFile(archive)as z:
  for v in archive_inputs:assert hashlib.sha256(z.read(v.relative_to(R).as_posix())).hexdigest()==sha(v)
 (D/'README.md').write_text('''Contra Force initial functional-source checkpoint. This is not a playable roster unlock. The genuine donor disassembly is pinned to commit df2c8e55 and all128KiB PRG reassembles exactly to original ba533736. No remote executables were downloaded or used; local guarded ca65/ld65 outputs stayed in a new private reproduction folder. Original header/CHR are preserved in the local reproduction but no NES/object/debug binaries enter this source-only archive.

The CPU arena executes original input, movement/pose/weapon allocation, nested source animation mapper calls and genuine final position integrator. All4 classes retain distinct original speeds. Eight tap/20-update-held jump cohorts and12 source class/gear projectile allocations pass. Contacts are explicit flat-floor/air arena inputs; this is not a native controller, collision, complete projectile update, full game or hosted Main claim. The20-update hold is not a maximum-jump/64px pipe traversal proof. All meaningful preparation/model/export negatives are retained by name and hash.

The installed parent dfdb and its exact source handoff remain unchanged. Current CFslot30/raw31 is still pending; only4 authentic menu bodies are present. Existing Bill/Lance Contra code is a different engine. The next leaf must relocate the genuine4-class core, preserve original poses/colors/weapon identities, implement real SMB world/lifecycle/progression adapters, and coordinate Start-class masks and shared selected31 dispatch. No new PRG/RAM/CHR ownership is claimed. Benj901..<915 and BT915..<927 remain reserved; temporalRAM1/C2 would require explicit joint review. No native process, source candidate, Downloads file or Git index was changed by this exporter.
''',encoding='utf-8',newline='\n')
 owned=[v.relative_to(R).as_posix()for v in tools]+[v.relative_to(R).as_posix()for v in sorted(D.iterdir())]+[(D/'owned-files.txt').relative_to(R).as_posix(),(D/'manifest.json').relative_to(R).as_posix()]
 (D/'owned-files.txt').write_text('\n'.join(owned)+'\n',encoding='utf-8',newline='\n')
 manifest=dict(handoff_sha256=sha(O/'handoff.json'),archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,archive_members={v.relative_to(R).as_posix():sha(v)for v in sorted(archive_inputs)},bindings=len(own_handoff['bindings']),owned_files=(D/'owned-files.txt').relative_to(R).as_posix(),no_git_mutation=True,no_native=True)
 verify(own_handoff);verify(h)
 save(D/'manifest.json',manifest)
 print(json.dumps(dict(handoff=str(O/'handoff.json'),handoff_sha256=sha(O/'handoff.json'),bindings=len(own_handoff['bindings']),manifest=str(D/'manifest.json'),manifest_sha256=sha(D/'manifest.json'),archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,members=len(archive_inputs))),flush=True)
if __name__=='__main__':main()
