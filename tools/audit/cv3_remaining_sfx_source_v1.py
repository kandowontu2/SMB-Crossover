"""Pinned original CV3 seven remaining effects: real requests, ordered APU and per-voice priority."""
from pathlib import Path
import argparse,csv,hashlib,itertools,json,shutil
from cv3_primary_sfx_source_v1 import Original,CV3,CV3_SHA,sha,authenticate
from cv3_dmc_complete_cpu_v1 import LaneArena
from check_tmnt_render_oa import load,address
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
EVENTS={0x13:'dagger',0x14:'cross',0x15:'axe',0x24:'flame',0x21:'ice',0x1e:'lightning',0x2f:'bat-enter',0x1f:'existing-fireball-control'}
PARENT='4c70fe485f73fb8d437fae2e79ae8ddad83908dc26d4008f21e0a2abeccee2da'
def voices(o):return dict(pulse=o.m[0x10a],noise=o.m[0x10d])
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False);raw=CV3.read_bytes();assert sha(CV3)==CV3_SHA and sha(a.rom)==PARENT
 ref=ROOT/'build/player-guide-agent/cv3-private/reference/source/code';pinned=D/'cv3-primary-sfx-v1/original-source';assert pinned.exists()
 manifest=json.loads((ref.parent.parent/'source-manifest.json').read_text());assert manifest['revision']=='3272648f2bbf95f6cb11d947feca73b852a99f10';references={};frozen=out/'reference';frozen.mkdir()
 for name in['playerStateProcessing_b1c.s','playerStateProcessing_b1d.s']:
  f=ref/name;expected=next(r['sha256']for r in manifest['files']if r['path']=='code/'+name);assert sha(f)==expected;references[name]=sha(f);shutil.copyfile(f,frozen/name)
 auth=authenticate(raw,ref/'playerStateProcessing_b1d.s',29,[(0xe52,0xe9b),(0xf77,0xf86),(0x107c,0x1081),(0x1390,0x139a),(0x1640,0x1645),(0x16b2,0x16bc),(0x1823,0x182e),(0x64f,0x697),(0x6bb,0x6d3),(0x726,0x737)])
 (out/'authenticated-source-bytes.json').write_text(json.dumps(auth,indent=2)+'\n')
 owners=[]
 for obj,want in[(1,0x13),(2,0x15),(3,0x14),(5,0x24),(6,0x21),(7,0x1e)]:
  o=Original(raw);o.call(0xe227);o.m[0x54e+20]=obj;o.m[0x438]=100;o.m[0x41c]=144
  for update in range(40):
   result=o.call(0xae52,stop=0xe25f)
   if result['final_pc']==0xe25f:break
  else:raise AssertionError(('No actual source request',obj))
  assert o.c.a==want;owners.append(dict(object=obj,entry=0xae52,source_request=want,dispatcher_updates_before_request=update,actual_slot=o.c.x))
 o=Original(raw);o.m[0x54e]=3;o.call(0xa6bb,stop=0xe25f);assert o.c.a==0x2f;owners.append(dict(entry=0xa6bb,source_request=o.c.a,owner='playerState30_alucard enter-bat'))
 o=Original(raw);o.m[0x54e]=3;o.call(0xa726);assert not o.m.trace;owners.append(dict(entry=0xa726,source_request=None,owner='playerState3c_alucard exit-bat; no request'))
 captures=[]
 for event,name in EVENTS.items():
  o=Original(raw);o.call(0xe227);o.m.trace=[];o.m.frame=0;launch=o.call(0xe25f,a=event);initial=voices(o);states=[]
  for frame in range(180):
   o.m.frame=frame;cost=o.call(0xe24e);states.append(dict(frame=frame,voices=voices(o),cycles=cost['cycles']))
  path=out/f'event-{event:02x}-apu.csv'
  with path.open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=['frame','cycle','pc','bank','address','value']);w.writeheader();w.writerows(o.m.trace)
  old=D/f'cv3-primary-sfx-v1/source-cpu-v2/event-{event:02x}-apu.csv';assert sha(path)==sha(old),'Fresh original executable golden differs from prior pinned reference'
  active={v:[r['frame']for r in states if r['voices'][v]]for v in['pulse','noise']};last=max(r['frame']for r in o.m.trace)
  capture=dict(id=event,name=name,launch=launch,initial_voices=initial,trace_sha256=sha(path),writes=len(o.m.trace),last_APU_write_frame=last,source_voice_active_frames=active,registers=sorted({r['address']-0x4000 for r in o.m.trace}),source_active_max_update_cycles=max(r['cycles']for r in states),raw_ordered_stream_bytes=len(o.m.trace)*2+last+2)
  captures.append(capture);(out/f'event-{event:02x}-states.json').write_text(json.dumps(states,indent=2)+'\n')
 priorities=[]
 for old,new,age in itertools.product(EVENTS,EVENTS,(0,1,5,16,32,88)):
  o=Original(raw);o.call(0xe227);o.call(0xe25f,a=old)
  for _ in range(age):o.call(0xe24e)
  before=voices(o);o.call(0xe25f,a=new);after=voices(o);mask=next(r['initial_voices']for r in captures if r['id']==new)
  expected={voice:(new if mask[voice]and new>=before[voice]else before[voice])for voice in before};assert after==expected,(old,new,age,before,after,expected)
  priorities.append(dict(current=old,incoming=new,age=age,before=before,after=after))
 (out/'original-priority.json').write_text(json.dumps(priorities,separators=(',',':'))+'\n')
 b=load(a.rom);target=[]
 for variant,sub,mode in itertools.product((1,2,3),(1,2,3),(0,1)):
  q=LaneArena(b,5);q.put(Cv3Variant=variant,CrossoverBehaviorVersion=mode,AreaMusicQueue=1);q.invoke('AudioUpdate');q.put(AreaMusicQueue=0,Cv3Fresh=0x40,SavedJoypadBits=0x48);q.set('Cv3Hearts',10,variant-1);q.set('Cv3Subweapon',sub,variant-1)
  q.invoke('Cv3WeaponsGate');armed=dict(kind=q.get('Cv3AttackKind'),age=q.get('Cv3AttackAge'),hearts=q.get('Cv3Hearts',variant-1),RgSfx=q.get('RgSfx'),AvAudioRequest=q.get('AvAudioRequest'),DmcPending=q.get('Cv3DmcPending'))
  assert armed['kind']==2;q.put(Cv3AttackAge=14,Cv3Fresh=0,SavedJoypadBits=0);q.invoke('Cv3WeaponsGate')
  record=dict(variant=variant,subweapon=sub,mode=mode,armed=armed,release_attack_age=14,created_types=[q.get('Cv3ShotType',i)for i in range(4)],AvAudioRequest=q.get('AvAudioRequest'),DmcPending=q.get('Cv3DmcPending'),RgSfx=q.get('RgSfx'),stopwatch=q.get('AvStopwatch'))
  assert record['AvAudioRequest']==record['DmcPending']==0;target.append(record)
 bats=[]
 for mode in(0,1):
  q=LaneArena(b,5);q.put(Cv3Variant=3,CrossoverBehaviorVersion=mode,Cv3Fresh=0x80,SavedJoypadBits=4);q.set('Cv3Hearts',10,2);q.invoke('Cv3BatUpdate');assert q.get('Cv3Bat')==1 and q.get('Cv3BatTransform')==36 and q.get('AvAudioRequest')==0 and q.get('RgSfx')==0;bats.append(dict(mode=mode,bat=q.get('Cv3Bat'),transform=q.get('Cv3BatTransform'),AvAudioRequest=0,RgSfx=0))
 (out/'target-actual-owners.json').write_text(json.dumps(dict(projectiles=target,bat_enter=bats),indent=2)+'\n')
 proof=dict(passed=True,source_ROM_sha256=CV3_SHA,target_ROM_sha256=PARENT,reference_revision='3272648f2bbf95f6cb11d947feca73b852a99f10',reference_files=references,authenticated_bytes=sum(len(bytes.fromhex(r['hex']))for r in auth),actual_original_owner_requests=owners,captures=captures,original_per_voice_priority_cases=len(priorities),priority_rule='Each requested pulse/noise voice independently admits incoming source request>=its still-active current source request; equal retriggers. A voice not requested is untouched.',actual_target_subweapon_owner_cases=len(target),actual_target_bat_owner_cases=len(bats),cross_scope='Only base Simon has a cross: existing CV1 SimonCross typed5 source stream; no CV3 companion cross exists. Do not replace that original-family cue.',scope='Original executable CPU, byte-authenticated source, actual target ability payment/release owners. Logical release stage14 is explicit; no native worker, audible waveform, campaign or final new-SFX implementation claim.',tool_sha256=sha(__file__))
 (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');shutil.copyfile(Path(__file__),out/Path(__file__).name);print(json.dumps(dict(passed=True,source_effects=len(captures),target_owner_cases=len(target)+len(bats),priority_cases=len(priorities),source_trace_bytes=sum(r['raw_ordered_stream_bytes']for r in captures),proof_sha256=sha(out/'proof.json'))))
if __name__=='__main__':main()
