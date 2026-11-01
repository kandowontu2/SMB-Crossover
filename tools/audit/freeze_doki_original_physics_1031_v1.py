"""Freeze original Doki source research; no game, native or Git mutations."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2]
O=R/'docs/qa/checkpoints/2026-10-31/doki-original-physics-source-v1'
B=R/'build/doki-original-rebuild-1031-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,q):p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf8',newline='\n')
def main():
 assert not O.exists();O.mkdir()
 positives=[R/'build/doki-original-physics-audit-1031-v2/audit.json',R/'build/doki-motion-lift-controls-1031-v1/controls.json',R/'build/doki-carry-geometry-controls-1031-v4/controls.json']
 reproduction=B/'reproduction.json';q=json.loads(reproduction.read_text());assert not q['passed']
 allproof=[reproduction,*positives]
 negatives=[R/'build/doki-original-physics-audit-1031-v1/audit.json',*[R/f'build/doki-carry-geometry-controls-1031-v{i}/controls.json'for i in range(1,4)]]
 bindings={}
 for p in allproof+negatives:
  a=json.loads(p.read_text())
  if p in positives:assert a['passed'],p
  else:assert not a['passed'],p
  for f,h in a.get('bindings',{}).items():assert sha(f)==h,(p,f);bindings[f]=h
 jumps=json.loads(positives[0].read_text());motion=json.loads(positives[1].read_text());carry=json.loads(positives[2].read_text())
 original=(B/'original-files/main_pro.bin').read_bytes();assembled=(B/'assembled/main_pro.bin').read_bytes()
 # These original-byte slices, unlike the whole MAIN file, reproduce exactly.
 spans=[]
 for name,start,end in [('player_normal_action_jump_gravity_physics',0x8441,0x88d1),('carried_actor_world_commit',*carry['Doki_prefix']['CPU'])]:
  old=original[start-0x6000:end-0x6000];assert old==assembled[start-0x6000:end-0x6000]
  spans.append(dict(name=name,CPU=[start,end],disk_offset=1869+start-0x6000,bytes=len(old),sha256=hashlib.sha256(old).hexdigest(),hex=old.hex(),assembled_source_exact=True))
 save(O/'exact-original-slices.json',dict(spans=spans,stats=jumps['stats'],functions=jumps['source_functions'],original_FDS_byte_execution=True))
 save(O/'negative-ledger.json',dict(whole_file_reproduction=dict(path=str(reproduction),sha256=sha(reproduction),exact_files=sum(x['exact']for x in q['assembled_files']),total_files=len(q['assembled_files']),mismatched_files=[x for x in q['assembled_files']if not x['exact']],conclusion='Do not claim complete source reproduction. CPU controls use the actual extracted original FDS, not mismatched assembled MAIN.'),fixture_negatives=[dict(path=str(p),sha256=sha(p),error=json.loads(p.read_text()).get('error'))for p in negatives],corrections=[
  'Jump v1 used a nonexistent lift RAM label; v2 resolves actual timer_actor_held.',
  'Carry v1 looked for a data label in only the code-bank NL; v2 resolves actual label but cannot initialize a slice.',
  'Carry v2 memory wrapper rejected slice initialization; v3 fixes the fixture wrapper.',
  'Carry v3 falsely interpreted NL suffix2 as a16KB bank index. Actual donor bytes at file7B7B/CPU BB6B are in16KB pair1; v4 binds the exact28-byte source table and passes. No donor or installed source was edited.'
 ]))
 scope=dict(passed=True,source=True,source_CPU=True,native=False,ported=False,admitted=False,installed=False,main_or_shared_edits=False,original=q['donor'],source_revision=q['git_commit'],primary_sources=['https://gitlab.com/segaloco/doki','https://github.com/Xkeeper0/smb2'],
  supersedes=dict(path='docs/qa/additional-campaign-and-doki-donors-2026-10-31.json',field='Doki_Doki_Panic.scope',previous='Four original-character skins/identities for the SMB2 family',current='Four original characters with original custom physics/control/render lineage. Mama must not be treated as an unchanged Luigi skin. No B-running by default.'),
  counts=dict(jump_contexts=192,jump_CPU_executions=576,horizontal_contexts=32,horizontal_CPU_executions=96,timed_lift_contexts=4,timed_lift_CPU_executions=12,carry_contexts=48,carry_CPU_executions=144),
  findings=[
   'Imajin/Mario, Lina/Peach, Papa/Toad original23-byte stat records match. Mama differs from Luigi in all6 jump launch entries: D8 D8 CB CB D2 D6 versus D6 D6 C9 C9 D0 D4. Original Mama has same2/1 gravity, not identical launch/arc.',
   'From rest, long-held jump collisionless leaves: Mama51px/81updates versus Luigi56px/85; tap1 Mama26/41 versus Luigi28/43. Lina retains original60-update float (long-held49px/100 total). No Mama Peach-style hover.',
   'Doki original action/clamp lacks USA B-held1.5x speed branch.32 actual horizontal traces cover all4, left/right, B and heavy carry; without B all three engines match. Installed S2 exactly follows USA in all32.',
   'Class-specific original timed lifting is retained: Imajin20,Lina32,Mama20,Papa8 updates in declared leaf timer model; all3 engines match.',
   'Original Doki carry geometry has fixed standing offset-5 and crouch+8; final SMB2U has character-specific big/small offsets.48 actual world-commit prefixes prove installed S2 follows USA, with concrete Doki differences.',
   'Doki normal player handler lacks final SMB2U HP-based small-form transition and Luigi-only airborne leg-animation path. A Doki port needs explicit original branches, not sprites/constants alone.'
  ],limits=['All controls are finite CPU leaf cases with declared setup/timer handling, not original native/controller/room tests.','Complete donor file rebuild remains negative (23/27 files exact); critical1168-byte player slice,69-byte carry prefix,TEMP-PRG and all4 character CHR files reproduce exactly.','No Doki movement, art, menu, resource, mapper or common hook has been installed. SMB-world terrain/camera/pipes/water/lifecycle remain intentional port adaptations to qualify.'])
 save(O/'scope.json',scope)
 (O/'README.md').write_text('''# Original Doki Doki Panic physics audit

This source-only research supersedes the earlier **skins-only** scope. Imajin, Lina, Papa and Mama require the original Doki player/control behavior. Mama is not an unchanged Luigi skin, and Doki does not acquire SMB2U B-running.

The exact local131000-byte FDS donor is pinned in scope.json. The primary disassembly is pinned at1c7327e4. A genuine guarded175-object build reproduces23 of27 extracted files. Four whole-file differences remain explicit; no full reproduction pass is claimed. The actual1168-byte player slice at8441..88D1,69-byte carry prefix atA956..A99B, original TEMP statistics and all four832-byte character CHR files do reproduce. Tests execute the extracted original donor bytes.

192 jump contexts run on original Doki, original SMB2U and actual installed-a441 S2 leaves (576 executions).32 horizontal contexts,4 timed lift contexts and48 carry contexts also run on all three engines. S2 follows final SMB2U in these tested leaves. Mama's six launch constants are two Q4 units less negative, giving51px versus Luigi56px on the long-held from-rest case; Lina keeps60-update float. Doki has no B speed boost. Its carry offsets and always-large presentation differ from final SMB2U.

These are finite collisionless/declared carry CPU cases, not whole-game or native admission. No game/shared source, Mesen, Git index or Download was changed. The full-rebuild mismatch and all four fixture negatives are retained. The source ZIP excludes ROM/FDS/object/executable/debug/binary assets; original donors remain local and hash-bound. Root owns scope reconciliation and any later private resource/port authorization.
''',encoding='utf8',newline='\n')
 tools=[R/'tools/audit'/n for n in ['prepare_doki_original_rebuild_1031_v1.py','doki_original_physics_audit_1031_v1.py','doki_original_physics_audit_1031_v2.py','doki_motion_lift_controls_1031_v1.py',*[f'doki_carry_geometry_controls_1031_v{i}.py'for i in range(1,5)],Path(__file__).name]]
 # Entire primary text-source checkout is small, while proprietary assets stay local.
 source=[p for p in(B/'source').rglob('*')if p.is_file()and(p.suffix.lower()in('.s','.i','.ld','.md','.py','.sh','.mak','.txt')or p.name in('Makefile','LICENSE','COPYING'))]
 files=set(tools+source+allproof+negatives+[B/'build-log.json',O/'README.md',O/'scope.json',O/'negative-ledger.json',O/'exact-original-slices.json'])
 for p in files:assert p.exists()and p.suffix.lower()not in('.nes','.fds','.o','.obj','.exe','.dbg','.bin','.zip'),p
 members={p.relative_to(R).as_posix():sha(p)for p in sorted(files)};save(O/'source-members.json',members)
 with zipfile.ZipFile(O/'source-only.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for p in sorted(files):z.write(p,p.relative_to(R).as_posix())
 with zipfile.ZipFile(O/'source-only.zip')as z:assert all(hashlib.sha256(z.read(n)).hexdigest()==h for n,h in members.items())
 bindings.update({str(p.resolve()):sha(p)for p in files|{O/'source-members.json',O/'source-only.zip'}})
 for p,h in bindings.items():assert sha(p)==h,p
 hand=dict(**scope,archive_members=len(members),archive_bytes=(O/'source-only.zip').stat().st_size,bindings=bindings);save(O/'handoff.json',hand)
 owned=tools+[O/n for n in ['README.md','scope.json','negative-ledger.json','exact-original-slices.json','source-members.json','source-only.zip','handoff.json','owned-files.json']]
 save(O/'owned-files.json',dict(files=[p.relative_to(R).as_posix()for p in sorted(owned)],stage_or_commit=False))
 print(json.dumps(dict(path=str(O/'handoff.json'),sha256=sha(O/'handoff.json'),bindings=len(bindings),members=len(members),bytes=hand['archive_bytes'])),flush=True)
if __name__=='__main__':main()
