"""Checkpoint the native-qualified WIP skin and retain rejected visual evidence."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2];B=R/'build/kamikaze-mario-host-v4'
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def verify(d,seen):
 if isinstance(d,dict):
  if 'path'in d and 'sha256'in d:
   b=bind(d['path']);assert b['sha256']==d['sha256'];seen[b['path']]=b['sha256']
  for k,v in d.items():
   if k in['bindings','actual_dependencies','actual_ASM_dependencies']and isinstance(v,dict):
    for p,h in v.items():
     if isinstance(h,str):assert bind(p)['sha256']==h,p;seen[str(Path(p).resolve())]=h
   verify(v,seen)
 elif isinstance(d,list):
  for v in d:verify(v,seen)
def main():
 target=R/'docs/qa/checkpoints/2026-10-29/kamikaze-mario-native-wip';assert not target.exists()
 assert bind(B/'candidate.nes')['sha256']=='737d71af449b70a73b1d13f228efb6cfa819ea027219f605344861fb0e2b0624'
 seen={};owned=[]
 for n in['build.json','source-closure.json','full-pose-controls-v8.json']:
  p=B/n;d=json.loads(p.read_text());verify(d,seen);owned.append(p)
  if n!='build.json':assert d['passed']
 closure=json.loads((B/'source-closure.json').read_text());assert closure['independent_same_ROM_relink']
 for name,want in[('mmc3','d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),('mmc5','f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:assert bind(B/('ordinary-'+name+'.nes'))['sha256']==want
 runs=[]
 for folder in['kamikaze-mario-native-easy-v3','kamikaze-mario-upgrades-easy-v2']:
  p=R/'build/verification'/folder
  ready=json.loads((p/'ready.json').read_text());verify(ready,seen)
  launch=json.loads((p/'launch.json').read_text());result=json.loads((p/'result.json').read_text());review=json.loads((p/'review.json').read_text())
  assert launch['exit_code']==0 and not launch['changed_inputs']and launch['settings_before']==launch['settings_after']
  assert result['passed']and result['zero_deaths']and result['cheats_off']and result['real_1_2_control_updates']>=25 and review['passed']
  assert result['ROM_sha256']==bind(B/'candidate.nes')['sha256']
  runs.append(dict(result=bind(p/'result.json'),review=bind(p/'review.json'),launch=bind(p/'launch.json')))
  owned += [p/n for n in['ready.json','run.lua','launch.json','result.json','review.json','capture-budget.json','candidate-run.log','selected-whole-frames.png','inputs.csv','trace.csv']]
 p=R/'build/verification/kamikaze-mario-upgrades-easy-v2';owned += [p/'flower-whole-frame.png',p/'flower-frame-review-source.json']
 for x in['src/kamikaze_mario.s','src/kamikaze_mario_render_v2.inc','src/kamikaze_mario_source_art_v2.inc','chr/characters/kamikaze-mario-source-v2.chr',
  'tools/prepare_kamikaze_mario_art_v2.py','tools/prepare_kamikaze_mario_host_v4.py','tools/kamikaze_mario_source_closure_v3.py',
  'tools/audit/kamikaze_mario_full_pose_controls_v8.py','tools/audit/kamikaze_mario_native_prepare_v2.py','tools/audit/kamikaze_mario_native_prepare_v4.py',
  'tools/audit/kamikaze_flower_frame_v1.py','tools/playthroughs/kamikaze_mario_11_v1.lua','tools/playthroughs/kamikaze_mario_upgrades_11_v2.lua','build/kamikaze-mario-art-v2/source-art.json']:
  owned.append(R/x)
 owned += list((B/'overlay').rglob('*.*'))+[B/'kamikaze_chr.s',B/'private_builder.py',Path(__file__)]
 # Byte-bound rejected evidence stays historical. It does not qualify the
 # current ROM. Keep the visual counterexample, not its capture tree.
 for x in['build/kamikaze-mario-art-v1/source-art.json','tools/prepare_kamikaze_mario_art_v1.py','tools/prepare_kamikaze_mario_host_v1.py','chr/characters/kamikaze-mario.chr',
  'build/kamikaze-mario-host-v2/build.json','build/kamikaze-mario-host-v2/source-controls-v5.json','tools/audit/kamikaze_mario_controls_v5.py',
  'build/verification/kamikaze-mario-native-easy-v2/review.json','build/verification/kamikaze-mario-native-easy-v2/selected-whole-frames.png',
  'build/verification/kamikaze-mario-native-easy-v1/candidate-run.log','build/verification/kamikaze-mario-upgrades-easy-v1/candidate-run.log']:
  owned.append(R/x)
 hand=dict(status='Native-qualified WIP Kamikaze skin; broader roster goal remains active',candidate=bind(B/'candidate.nes'),source_closure=bind(B/'source-closure.json'),CPU=bind(B/'full-pose-controls-v8.json'),native_runs=runs,
  verified_unique_source_native_bindings=len(seen),bindings=seen,owned_files=[bind(p)for p in dict.fromkeys(owned)],
  controls='Mario slot Select: Mario -> Luigi -> Kamikaze -> Celeste -> Mario. Native Mario controls, physics, powerups and hitboxes.',
  adaptation='Complete authentic26-frame source art, not same-index tile substitution. Source24px small sprite visually overhangs native small collision by8px; native4-sprite reservation unchanged. Held-swim/throw combinations explicitly map to complete source poses. Native Mario palette remains authoritative.',
  limits='Two Easy controller1-1 clears to25 active1-2 updates; one physically earns Mushroom+Flower. Actual source52 pixel cases and216 complete Main updates both modes/all areas/tiers; finite foreign/resident ABI. No full-roster/all-powerup campaign, Hard native, original Kamikaze engine physics, every-frame visual verdict or FPS equivalence claim. Canonical expanded/default builder remains f56a-source until final shared composition; this WIP is reproduced by the private source overlay recipe.',
  rejected='c2b8615d tile-only artwork disqualified by native visual before distribution. One native recorder1second timeout and one upgrade controller hit remain historical negatives.')
 (B/'handoff.json').write_text(json.dumps(hand,indent=2)+'\n');owned.append(B/'handoff.json')
 target.mkdir(parents=True);members={};archive=target/'frozen-source-packet.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for p in dict.fromkeys(owned):
   assert p.suffix not in['.nes','.dbg','.map','.exe','.dll'];name=p.resolve().relative_to(R).as_posix();data=p.read_bytes();info=zipfile.ZipInfo(name,(2026,10,29,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data);members[name]=hashlib.sha256(data).hexdigest()
 with zipfile.ZipFile(archive)as z:assert {n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()}==members
 review=dict(status=hand['status'],candidate=hand['candidate'],handoff=bind(B/'handoff.json'),archive=bind(archive),archive_members=members,verified_bindings=len(seen),controls=hand['controls'],adaptation=hand['adaptation'],limits=hand['limits'])
 (target/'root-review.json').write_text(json.dumps(review,indent=2)+'\n');print(json.dumps(dict(checkpoint=str(target.relative_to(R)),files=len(members),bindings=len(seen),archive=bind(archive))))
if __name__=='__main__':main()
