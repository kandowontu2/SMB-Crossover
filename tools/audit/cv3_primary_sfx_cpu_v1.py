"""Bounded CPU qualification of the private original Alucard SFX route.

Actual linked projectile admission, source decoder, shared hardware flush,
and mapper writes execute. No Mesen/interrupt/waveform acceptance is implied.
"""
from pathlib import Path
import argparse,csv,hashlib,itertools,json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/audit'))
from check_tmnt_render_oa import load,address
from robots_weapon_cpu_v1 import Arena

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def apu(q):return [(at,v)for at,v in q.m.writes if 0x4000<=at<=0x4017]
def arr(q,name,n=16):return [q.get(name,i)for i in range(n)]

def setup(b,char=5):
 q=Arena(b,char=char)
 q.put(Cv3Variant=3,AvAudioChar=char,GuestAudioCharacter=char,
       GuestNativeEnable=15,GuestCombinedEnable=15)
 music=[0x30,8,0,8,0x30,8,0,8,0,0,0,8,0x30,0,0,8]
 q.array('GuestNativeApu',music);q.array('GuestApuLast',music)
 return q

def snapshot(q):
 return {n:arr(q,n,k)for n,k in [('GuestNativeApu',16),('GuestNativeDirty',16),
    ('AvAudioMusic',16),('AvAudioSfx',16)]}|{n:q.get(n)for n in
    ['AvAudioId','AvAudioMask','AvAudioOldMask','AvAudioRequest','AvAudioPtr',
     'GuestNativeEnable','GuestCombinedEnable','R0','R1']}

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--prepared',type=Path,required=True);p.add_argument('--capture',type=Path,required=True)
 p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 old,new=load(a.prepared/'baseline.nes'),load(a.prepared/'candidate.nes')
 # Existing source effects, channels, pause/unsupported states and C-bank restoration.
 regression=[];peaks=[]
 for effect,bank in itertools.product(range(26),(13,85)):
  qs=[setup(b)for b in (old,new)]
  for q in qs:q.m.page(2,bank);q.set('CurrentBankC',bank|128);q.set('AvAudioRequest',effect)
  for tick in range(40):
   for q in qs:
    q.set('GamePauseStatus',int(tick in (6,7)))
    q.invoke('RemainingAudioBegin')
    q.array('GuestNativeDirty',[0]*16)
   cycles=[];snapshots=[];writes=[]
   for q in qs:
    c,_=q.invoke('SophiaLandAudioTick');cycles.append(c.processorCycles)
    assert q.m.banks[2]==bank and q.get('CurrentBankC')==bank|128
    snapshots.append(snapshot(q));writes.append(apu(q))
   assert snapshots[0]==snapshots[1],(effect,bank,tick,snapshots)
   assert writes[0]==writes[1],(effect,bank,tick,writes)
   delta=cycles[1]-cycles[0];peaks.append(delta)
  regression.append(dict(effect=effect,C_bank=bank,updates=40,passed=True))

 original=[{k:int(v)for k,v in r.items()}for r in csv.DictReader((a.capture/'event-1f-apu.csv').open())]
 q=setup(new);q.set('AvAudioRequest',26);timeline=[]
 for frame in range(30):
  q.invoke('RemainingAudioBegin');q.array('GuestNativeDirty',[0]*16)
  c,_=q.invoke('SophiaLandAudioTick')
  dirty=arr(q,'GuestNativeDirty');image=arr(q,'GuestNativeApu')
  q.invoke('GuestAudioNativeFlush');writes=[(at,v)for at,v in apu(q)if 0x400c<=at<=0x400f]
  if frame<=27:
   want=[(r['address'],r['value'])for r in original if r['frame']==frame]
   assert sorted(writes)==sorted(want),(frame,writes,want)
   assert all(not dirty[i] for i in range(12)),(frame,dirty)
  elif frame==28:
   assert q.get('AvAudioId')==0 and q.get('AvAudioMask')==0
   assert writes==[(0x400c,0x30),(0x400e,0),(0x400f,8)]
  else:assert not writes
  timeline.append(dict(frame=frame,noise_writes=writes,dirty=dirty,cycles=c.processorCycles,
                       noise_image=image[12:16],active=q.get('AvAudioId')))
 (a.output/'alucard-apu-timeline.json').write_text(json.dumps(timeline,indent=2)+'\n')

 # Full projectile gate at its legal fireball release update. Ordinary primary
 # inputs in Grant/Sypha are intentionally still missing DMC effects.
 attacks=[]
 for mode,face,crouch,power in itertools.product((0,1),(1,2),(0,1),(0,1,2)):
  outcomes=[]
  for b in (old,new):
   q=setup(b);q.put(CrossoverBehaviorVersion=mode,PlayerFacingDir=face,
      RgCrouch=crouch,Cv3AttackCrouch=crouch,Cv3AttackKind=1,Cv3AttackAge=8)
   q.set('Cv3Power',power,2);c,_=q.invoke('Cv3WeaponsGate')
   types=arr(q,'Cv3ShotType',4)
   outcomes.append(dict(types=types,request=q.get('AvAudioRequest'),cycles=c.processorCycles,
      shot_x=arr(q,'Cv3ShotX',4),shot_y=arr(q,'Cv3ShotY',4),
      shot_vx=arr(q,'Cv3ShotVXHi',4),shot_vy=arr(q,'Cv3ShotVYHi',4)))
  assert outcomes[0]['request']==0 and outcomes[1]['request']==26
  assert {k:v for k,v in outcomes[0].items()if k not in('request','cycles')}=={
      k:v for k,v in outcomes[1].items()if k not in('request','cycles')}
  attacks.append(dict(mode=mode,face=face,crouch=crouch,power=power,baseline=outcomes[0],candidate=outcomes[1]))

 guards=[]
 for kind,full,pending in itertools.product(range(1,7),(False,True),(0,21,22,26)):
  q=setup(new);q.set('AvAudioRequest',pending)
  if full:q.array('Cv3ShotType',[1]*4)
  q.invoke('Cv3Spawn',a=kind)
  assert q.get('AvAudioRequest')==(26 if kind==6 and not full and pending==0 else pending)
  guards.append(dict(type=kind,full=full,pending=pending,result=q.get('AvAudioRequest')))

 # The mapper bracket is direct register code, never shared farcall SMC.
 bank_rows=[]
 for bank in (0,7,13,28,83,85,126,127):
  q=setup(new);q.m.page(2,bank);q.set('CurrentBankC',bank|128);q.set('AvAudioRequest',26)
  smc=bytes(q.m[0x155:0x176]);q.invoke('SophiaLandAudioTick')
  assert bytes(q.m[0x155:0x176])==smc and q.m.banks[2]==bank and q.get('CurrentBankC')==bank|128
  bw=[(at,v)for at,v in q.m.writes if at in(0x5115,0x5116)]
  assert bw==[(0x5116,0x9c),(0x5116,bank|128)],bw
  bank_rows.append(dict(original_C=bank,mapper_writes=bw,SMC_unchanged=True))

 (a.output/'attacks.json').write_text(json.dumps(attacks,indent=2)+'\n')
 (a.output/'spawn-guards.json').write_text(json.dumps(guards,indent=2)+'\n')
 (a.output/'bank-restore.json').write_text(json.dumps(bank_rows,indent=2)+'\n')
 report=dict(passed=True,accepted=False,baseline_sha256=sha(a.prepared/'baseline.nes'),
    candidate_sha256=sha(a.prepared/'candidate.nes'),source_trace_sha256=sha(a.capture/'event-1f-apu.csv'),
    old_source_overlay_update_regressions=26*2*40,old_effects=26,
    ordinary_update_cycle_delta_min=min(peaks),ordinary_update_cycle_delta_max=max(peaks),
    original_noise_event_updates_exact_as_register_multisets=28,
    original_noise_register_writes=28,silent_source_updates_do_not_retrigger=True,
    real_weapon_release_cases=len(attacks),guard_cases=len(guards),direct_bank_restore_cases=len(bank_rows),
    new_RAM_bytes=0,existing_five_SMC_image_unchanged=True,
    limitations=['Source intra-update write order C,F,E becomes shared native flush C,E,F.',
      'Source event is frame-quantized; no native emulator/APU waveform/IRQ/OAM/CHR visibility acceptance.',
      'Existing mixer overwrites one prior non-DMC effect on a new typed effect; no multi-effect CV3 driver was added.',
      'Grant/Sypha primary DMC plus spells/subweapon/bat/injury source audio still missing.'],
    tool_sha256=sha(__file__))
 (a.output/'proof.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
