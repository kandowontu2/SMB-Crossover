"""Source priority, real owner chain, lifecycle and ordinary lane CPU checks."""
from pathlib import Path
import argparse,hashlib,itertools,json
from robots_weapon_cpu_v1 import Arena
from check_tmnt_render_oa import load,address,location
from verify_native_relocation import NesMPU
class LaneArena(Arena):
 def invoke(self,name,a=0,x=0,y=0,traps=(),flags=0x30):
  sym=self.b['syms'][name];seg=self.b['segs'][sym['seg']];bank=(int(seg['ooffs'],0)-16)//8192;pc=address(self.b,name);window=(pc-0x8000)//8192
  # Preserve the already selected fixed-E mirror. Its resident instructions
  # are exactly the original127 instructions at the same virtual addresses.
  if not(window==3 and bank==127 and self.m.banks[3]==125):self.m.page(window,bank)
  if window in(1,2):self.set('CurrentBank'if window==1 else'CurrentBankC',bank|128)
  self.m.writes=[];c=NesMPU(memory=self.m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,flags,0xfd;c.stPushWord(0x5aff);trapped={address(self.b,n):n for n in traps};seen=[]
  for _ in range(100000):
   if c.pc==0x5b00:assert c.sp==253;return c,seen
   if c.pc in trapped:seen.append(trapped[c.pc]);c.pc=(c.stPopWord()+1)&65535;continue
   c.step()
  raise AssertionError(('CPU timeout',name,hex(c.pc),self.m.banks))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def regs(c):return(c.a,c.x,c.y,c.p&0xcf,c.sp)
def apu(q):return[(at,v)for at,v in q.m.writes if 0x4000<=at<=0x4017]
def diff(qs,allow=()):
 exc=set(range(256,512))|set(allow);changed=[i for i in range(0x8000)if i not in exc and qs[0].m[i]!=qs[1].m[i]]
 assert not changed,[hex(i)for i in changed[:20]]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--source-tail',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 old,new=load(a.prepared/'baseline.nes'),load(a.prepared/'candidate.nes');source=json.loads((a.source/'original-priority.json').read_text());inj=json.loads((a.source/'proof.json').read_text())
 private=[address(new,'RgAudioZp')+i for i in range(32,36)]
 rows=[]
 for rec,enable,bank,x,y in itertools.product(source,(0,3,15,31),(28,88,124),(0,7,255),(0,3,255)):
  q=LaneArena(new,5);q.put(Cv3DmcPriority=rec['current'],Cv3DmcPending=rec['request'],BassDmcActive=3 if rec['current']else 0,GuestCombinedEnable=enable,CurrentBankC=bank|128);q.m.page(2,bank);q.m.page(3,125 if rec['current']else 127);q.m[0x4015]=enable|16
  c,_=q.invoke('Cv3DmcStartGate',a=rec['request'],x=x,y=y)
  # Arena maps the fixed gate E127 on entry; its E125 code is byte-identical.
  assert q.get('Cv3DmcPending')==0 and q.get('Cv3DmcPriority')==rec['new_priority']
  assert(c.a,c.x,c.y,c.sp)==(rec['request'],x,y,253)
  assert q.get('CurrentBankC')==bank|128 and q.m.banks[2]==bank
  hw=apu(q);launch=any(at==0x4015 and v&16 for at,v in hw);assert launch==rec['launched'],rec
  if launch:
   values=dict(hw);sound=rec['request'];digest='c1b646c36508ad4d134078c8184fea7bd632f50127c5f2af6550e89097cbda01'if sound==0x72 else next(s['payload_sha256']for s in inj['source_injury']if s['character']=={0x74:'Grant',0x75:'Sypha',0x76:'Alucard'}[sound]);start=0xc000+values[0x4012]*64;n=values[0x4013]*16+1;payload=bytes(q.m[start:start+n]);assert hashlib.sha256(payload).hexdigest()==digest
   assert values[0x4011]==0 and values[0x4010]=={0x72:15,0x74:14,0x75:15,0x76:13}[sound]and q.m.banks[3]==125 and q.get('BassDmcActive')==3
  else:assert not hw
  rows.append(dict(**rec,enable=enable,prior_C=bank,x=x,y=y,cycles=c.processorCycles))
 (a.output/'source-priority.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')
 owners=[];negative=[]
 for variant,mode,face,pending,kind in itertools.product((1,2,3),(0,1),(1,2),(0,21,26),('primary','injury')):
  qs=[LaneArena(b,5)for b in(old,new)]
  for q in qs:
   q.put(Cv3Variant=variant,CrossoverBehaviorVersion=mode,PlayerFacingDir=face,AvAudioRequest=pending,AreaMusicQueue=1)
   q.invoke('AudioUpdate');q.put(AvAudioRequest=pending,AreaMusicQueue=0,Cv3DmcPending=0)if'Cv3DmcPending'in q.b['syms']else q.put(AvAudioRequest=pending,AreaMusicQueue=0)
   if kind=='primary':q.put(Cv3Fresh=0x40,SavedJoypadBits=0,RgCrouch=0)
   else:q.put(Cv3Invul=0,ObjectOffset=0);q.set('Cv3Health',64,variant-1);q.set('Enemy_ID',0)
  cs=[q.invoke('Cv3WeaponsGate'if kind=='primary'else'Cv3InjuryStartGate')[0]for q in qs]
  desired=0x72 if kind=='primary'and variant<3 else(0x73+variant if kind=='injury'else 0)
  assert qs[1].get('Cv3DmcPending')==desired,(kind,variant,qs[1].get('Cv3DmcPending'))
  assert qs[1].get('AvAudioRequest')==qs[0].get('AvAudioRequest') if kind=='primary' else qs[1].get('AvAudioRequest')==pending
  assert regs(cs[0])==regs(cs[1]),(kind,variant,regs(cs[0]),regs(cs[1]))
  if desired:
   if pending==0:qs[0].invoke('AudioUpdate')
   qs[1].invoke('AudioUpdate');hw=apu(qs[1]);rates=[v for at,v in hw if at==0x4010];assert rates[0]=={0x72:15,0x74:14,0x75:15,0x76:13}[desired],(kind,variant,pending,hw)
   # A preexisting ordinary typed21 is dispatched later by the common mixer
   # and intentionally preempts this source sample through its normal owner.
   assert qs[1].get('BassDmcActive')==(2 if pending==21 else 3),(kind,variant,pending,hw)
   if pending==0 and mode==1 and face==1:
    negative.append(dict(kind=kind,variant=variant,source_request=desired,baseline_APU=apu(qs[0]),candidate_APU=hw,baseline_DMC_owner=qs[0].get('BassDmcActive'),candidate_DMC_owner=qs[1].get('BassDmcActive')))
   if kind=='primary'and pending==0:
    diff(qs,private+[address(new,n)for n in('BassDmcActive','GuestCombinedEnable')]+[0x4010,0x4011,0x4012,0x4013,0x4015,0x5117])
  owners.append(dict(variant=variant,mode=mode,face=face,pending_common=pending,kind=kind,source_request=desired))
 (a.output/'actual-owners.json').write_text(json.dumps(owners,separators=(',',':'))+'\n')
 (a.output/'baseline-negative.json').write_text(json.dumps(negative,indent=2)+'\n')
 # Source queue priority: primary cannot erase a pending injury.
 for pending,variant in itertools.product((0,0x72,0x74,0x75,0x76),(1,2,3)):
  q=LaneArena(new,5);q.put(Cv3DmcPending=pending,Cv3Variant=variant,Cv3AttackKind=1);q.invoke('Cv3DmcPrimaryQueue');assert q.get('Cv3DmcPending')==(pending if pending>=0x74 or variant==3 else 0x72)
 # Source completion and every preemption store retain ordinary A/X/Y/status.
 lifecycle=[]
 for source_id,enable,owner in itertools.product((0x72,0x74,0x75,0x76),(0,3,15,31),(0,1,2,4)):
  q=LaneArena(new,5);q.put(GuestCombinedEnable=enable);q.invoke('Cv3DmcStartGate',a=source_id);assert q.m.banks[3]==125
  c,_=q.invoke('Cv3DmcOwnerWrite',a=owner,x=7,y=253);assert q.get('BassDmcActive')==owner and q.get('Cv3DmcPriority')==0 and q.m.banks[3]==127 and(c.a,c.x,c.y,c.sp)==(owner,7,253,253)
  assert apu(q)==[(0x4015,enable&15)]
  lifecycle.append(dict(source=source_id,enable=enable,next_owner=owner))
 for case in('pause','character','scene','death','subroutine','completion'):
  q=LaneArena(new,5);q.put(Cv3Variant=1,AreaMusicQueue=1);q.invoke('AudioUpdate');q.invoke('Cv3DmcStartGate',a=0x72);q.put(Cv3DmcPending=0x75);q.m[0x4015]=31
  if case=='pause':q.put(GamePauseStatus=1);q.invoke('GuestAudioFinish')
  elif case=='character':q.put(SelectedCharacter=3);q.invoke('GuestAudioBegin')
  elif case=='scene':q.invoke('Cv3NoiseSceneReset')
  elif case=='death':q.put(MmDeathFlag=1);q.invoke('Cv3DmcBeforeCv1',traps=('CvAudioPlay',))
  elif case=='subroutine':q.put(GameEngineSubroutine=11);q.invoke('Cv3DmcBeforeCv1',traps=('CvAudioPlay',))
  else:q.put(Cv3DmcPending=0);q.m[0x4015]=15;q.invoke('GuestDmcStatus')
  assert q.get('Cv3DmcPending')==0 and q.get('Cv3DmcPriority')==0 and q.get('BassDmcActive')==0 and q.m.banks[3]==127,case
 scene_controls=0
 for owner,noise,pending,variant in itertools.product((0,1,2,4),(0,1),(0,21,26),range(4)):
  qs=[LaneArena(b,5)for b in(old,new)]
  for q in qs:q.put(BassDmcActive=owner,Cv3NoiseActive=noise,AvAudioRequest=pending,Cv3Variant=variant,GuestCombinedEnable=31);q.m[0x4015]=31
  cs=[q.invoke('Cv3NoiseSceneReset',a=0x55,x=3,y=7)[0]for q in qs]
  assert apu(qs[0])==apu(qs[1]);diff(qs,private);assert regs(cs[0])==regs(cs[1])and qs[0].m.banks==qs[1].m.banks;scene_controls+=1
 for owner in(0,1,2,4):
  q=LaneArena(new,5);q.put(BassDmcActive=owner,Cv3DmcPending=0x72,MmDeathFlag=1,GuestCombinedEnable=31);q.m[0x4015]=31
  q.invoke('Cv3DmcBeforeCv1',traps=('CvAudioPlay',));assert q.get('BassDmcActive')==owner and q.get('Cv3DmcPriority')==0 and q.get('Cv3DmcPending')==0 and not apu(q)
 for char in(2,3,4,5,9,18,19):
  q=LaneArena(new,char);q.put(GuestAudioCharacter=255)
  for i in range(32,36):q.set('RgAudioZp',255,i)
  q.invoke('GuestAudioBegin');assert q.get('Cv3DmcPending')==0 and q.get('Cv3DmcPriority')==0 and q.m.banks[3]==127
 completion=0;ordinary_status=0
 if a.source_tail:
  tail=json.loads((a.source_tail/'proof.json').read_text())
  for rec,enable,flags,x,y in itertools.product(tail['rows'],(0,3,15,31),(0x20,0x21,0x60,0x61,0xa0,0xa1,0xe0,0xe1),(0,7,255),(0,3,255)):
   q=LaneArena(new,5);q.put(GuestCombinedEnable=31);q.invoke('Cv3DmcStartGate',a=rec['sound']);q.m[0x4015]=15
   # CPU-only explicit held-output state: verify completion makes no4011
   # write, so both the buffered final byte and its DAC are retained.
   q.m[0x4011]=rec['final_DAC'];c,_=q.invoke('GuestDmcStatus',a=enable,x=x,y=y,flags=flags)
   assert q.get('BassDmcActive')==0 and q.get('Cv3DmcPriority')==0 and q.m.banks[3]==127 and q.m[0x4011]==rec['final_DAC']
   assert not any(at==0x4011 for at,v in apu(q))and(c.a,c.x,c.y,c.p&0x45,c.sp)==(enable&15,x,y,flags&0x45,253);completion+=1
 for owner,status,enable,flags in itertools.product((0,1,2,4),(15,31),(0,3,15,31),(0x20,0x21,0x60,0x61,0xa0,0xa1,0xe0,0xe1)):
  qs=[LaneArena(b,5)for b in(old,new)]
  for q in qs:q.put(BassDmcActive=owner,GuestCombinedEnable=enable);q.m[0x4015]=status;q.m[0x4011]=44
  cs=[q.invoke('GuestDmcStatus',a=enable,x=7,y=255,flags=flags)[0]for q in qs];assert apu(qs[0])==apu(qs[1]);diff(qs,private);assert regs(cs[0])==regs(cs[1])and qs[0].m.banks==qs[1].m.banks;ordinary_status+=1
 # Full ordinary AudioUpdate differential. No source pending/priority: every
 # original APU write, existing RAM byte, register and mapper outcome is exact.
 ordinary=0;cost=[]
 for char,variant,effect in itertools.product((3,4,5),range(4),range(27)):
  if char!=5 and variant:continue
  if effect==26 and(char,variant)!=(5,3):continue
  qs=[LaneArena(b,char)for b in(old,new)]
  for q in qs:q.put(Cv3Variant=variant,AreaMusicQueue=1)
  for tick in range(32):
   for q in qs:
    q.put(GamePauseStatus=int(tick in(16,17)),AvAudioRequest=effect if tick==8 else 0)
    if tick==20:q.m[0x4015]=15
   cs=[q.invoke('AudioUpdate')[0]for q in qs];assert apu(qs[0])==apu(qs[1]),(char,variant,effect,tick,apu(qs[0]),apu(qs[1]))
   diff(qs,private);assert regs(cs[0])==regs(cs[1])and qs[0].m.banks==qs[1].m.banks,(char,variant,effect,tick)
   cost.append(cs[1].processorCycles-cs[0].processorCycles);ordinary+=1
 idle_cost=[];active_cost=[]
 for char,variant in[(2,0),(3,0),(4,0),(5,0),(5,1),(5,2),(5,3),(9,0),(15,0),(18,0),(19,0)]:
  qs=[LaneArena(b,char)for b in(old,new)]
  for q in qs:q.put(Cv3Variant=variant,AreaMusicQueue=1);q.invoke('AudioUpdate')
  for tick in range(16):
   cs=[q.invoke('AudioUpdate')[0]for q in qs];idle_cost.append(dict(character=char,variant=variant,tick=tick,delta=cs[1].processorCycles-cs[0].processorCycles))
 for variant in(1,2,3):
  qs=[LaneArena(b,5)for b in(old,new)]
  for q in qs:q.put(Cv3Variant=variant,AreaMusicQueue=1);q.invoke('AudioUpdate');q.put(BassDmcActive=2,GuestCombinedEnable=31,GuestNativeEnable=31);q.m[0x4015]=31
  qs[1].put(BassDmcActive=3,Cv3DmcPriority=5);qs[1].m.page(3,125)
  for tick in range(16):
   cs=[q.invoke('AudioUpdate')[0]for q in qs];assert apu(qs[0])==apu(qs[1]);active_cost.append(dict(variant=variant,tick=tick,delta=cs[1].processorCycles-cs[0].processorCycles))
 (a.output/'idle-active-cost.json').write_text(json.dumps(dict(idle=idle_cost,active=active_cost,scope='Assembled whole AudioUpdate cycles. Active control explicitly holds the DMC hardware-status bit in both versions; no DMA stealing, waveform or native cadence claim.'),indent=2)+'\n')
 result=dict(passed=True,accepted=False,ROM_sha256=sha(a.prepared/'candidate.nes'),baseline_ROM_sha256=sha(a.prepared/'baseline.nes'),source_priority_receipt_sha256=sha(a.source/'original-priority.json'),source_priority_cases=len(rows),actual_primary_injury_owner_cases=len(owners),pending_priority_cases=15,lifecycle_owner_cases=len(lifecycle)+6,ordinary_scene_owner_controls=scene_controls,unrelated_death_owner_controls=4,unused_private_allones_reset_controls=7,source_completion_held_DAC_controls=completion,ordinary_DmcStatus_controls=ordinary_status,ordinary_full_AudioUpdate_cases=ordinary,ordinary_cycle_delta=[min(cost),max(cost)],idle_full_AudioUpdate_delta_by_character={str(char):sorted({r['delta']for r in idle_cost if r['character']==char})for char in{r['character']for r in idle_cost}},source_active_full_AudioUpdate_delta=sorted({r['delta']for r in active_cost}),old_APU_RAM_regs_mapper_exact_except_declared_private_bytes=True,scope='Assembled CPU/source only. No native interrupt, actual DMA playback, audible output, timing or gameplay certification. Future shared TMNT composition remains separate.')
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
