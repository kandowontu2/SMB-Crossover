"""Public helper ABI/state, faithful dirty/source semantics and measured new steady cost."""
from pathlib import Path
import argparse,hashlib,itertools,json
from check_tmnt_render_oa import load,address,location
from verify_native_relocation import NesMPU
from cv3_remaining_sfx_complete_cpu_v1 import init,sound,source_voices
from cv3_primary_sfx_source_v1 import Original,CV3
from cv3_dmc_complete_cpu_v1 import regs,apu
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def writable_equal(qs,allow=()):
 keys={at for q in qs for at,v in q.m.writes if not 0x100<=at<0x200 and at<0x8000}-set(allow);bad=[(hex(at),qs[0].m[at],qs[1].m[at])for at in keys if qs[0].m[at]!=qs[1].m[at]];assert not bad,bad[:15];assert qs[0].m.banks==qs[1].m.banks
def state(q,index,dirty,high,active=128):
 q.put(Cv3NoiseIndex=index,Cv3NoiseActive=128,Cv3FxOwned=8,Cv3FxNoiseID=0x21,Cv3FxNoisePtr=250,Cv3FxSourceHigh=high)
 for i,reg in enumerate([12,14,15]):q.set('GuestNativeDirty',(dirty>>i)&1,reg);q.set('GuestNativeApu',[35,6,11][i],reg)
 for i,v in enumerate([37,active,3,8]):q.set('Cv3NoiseApu',v,i)
def invoke(q,name,a=0,x=0,y=0,flags=0x30):
 bank=(location(q.b,name)-16)//8192;pc=address(q.b,name);window=(pc-0x8000)//8192
 if not(window==3 and bank==127 and q.m.banks[3]==125):q.m.page(window,bank)
 if window in[1,2]:q.set('CurrentBank'if window==1 else'CurrentBankC',bank|128)
 q.m.writes=[];c=NesMPU(memory=q.m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,flags,253;c.stPushWord(0x5aff)
 for _ in range(100000):
  if c.pc==0x5b00:assert c.sp==253;return c
  c.step()
 raise AssertionError(('Actual physical helper timeout',name,hex(c.pc),q.m.banks))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old,new=[load(a.prepared/(n+'.nes'))for n in['baseline','candidate']];public=[];hot=[];schedules=[]
 for index,dirty,high,flags,active in itertools.product(range(43),range(8),[0,7],[0x20,0x69],[0,128,255]):
  qs=[init(b,2)for b in[old,new]]
  for q in qs:state(q,index,dirty,high,active)
  cs=[invoke(q,'Cv3FxResidentNoise',a=213,x=71,y=84,flags=flags)for q in qs];assert regs(cs[0])==regs(cs[1]),('Public ABI',index,dirty,high,flags,regs(cs[0]),regs(cs[1]));writable_equal(qs);public.append(dict(index=index,dirty=dirty,sourceHigh=high,P=flags,active=active,old=cs[0].processorCycles,new=cs[1].processorCycles))
 for index,dirty,high,flags,y in itertools.product([0,16,41,42],range(8),[0,7],[0x20,0x69],[0,84]):
  qs=[init(b,2)for b in[old,new]]
  for q in qs:state(q,index,dirty,high);assert q.get('Cv3NoiseActive')==128;q.put(AvAudioRequest=0,Cv3FxPendingNoise=0,Cv3FxPendingPulse=0)
  cs=[invoke(qs[0],'Cv3FxResidentDispatch',a=128,x=71,y=y,flags=flags),invoke(qs[1],'Cv3FxSteadyTry',a=128,x=71,y=y,flags=flags)];assert regs(cs[0])==regs(cs[1]);writable_equal(qs,[address(new,'Cv3FxSavedA')]);assert qs[1].get('Cv3FxSavedA')==y;hot.append(dict(index=index,dirty=dirty,sourceHigh=high,P=flags,Y=y,old=cs[0].processorCycles,new=cs[1].processorCycles,saved=cs[0].processorCycles-cs[1].processorCycles))
 for event,mode in itertools.product([0x13,0x15,0x24,0x21,0x1e,0x1f,0x2f],[0,1]):
  qs=[init(b,2 if event in[0x24,0x21,0x1e]else 3)for b in[old,new]]
  for q in qs:q.put(CrossoverBehaviorVersion=mode);sound(q,event)
  original=Original(CV3.read_bytes());original.call(0xe227);original.call(0xe25f,a=event);frames=[]
  for frame in range(100):
   before=source_voices(original);original.m.trace=[];original.call(0xe24e);cs=[invoke(q,'AudioUpdate')for q in qs];assert apu(qs[0])==apu(qs[1]),('Complete hardware',event,mode,frame);writable_equal(qs,[address(new,'Cv3FxSavedA')])
   for own,regs0 in[(before[0],[0x4000,0x4001,0x4002,0x4003]),(before[1],[0x400c,0x400e,0x400f])]:
    if own:assert[(at,v)for at,v in apu(qs[1])if at in regs0]==sorted((r['address'],r['value'])for r in original.m.trace if r['address']in regs0),(event,mode,frame,'Original raw hardware')
   frames.append(dict(frame=frame,old=cs[0].processorCycles,new=cs[1].processorCycles))
  schedules.append(dict(event=event,mode=mode,frames=frames))
 no_dirty=[r for r in hot if r['dirty']==0 and r['index']not in[42]];budget_pass=min(r['saved']for r in no_dirty)>=35;(a.output/'public.json').write_text(json.dumps(public,indent=2)+'\n');(a.output/'hot.json').write_text(json.dumps(hot,indent=2)+'\n');(a.output/'schedules.json').write_text(json.dumps(schedules,indent=2)+'\n');result=dict(passed=budget_pass,semantic_state_APU_ABI_passed=True,budget_passed=budget_pass,native_executed=False,ROM_sha256=sha(a.prepared/'candidate.nes'),parent_ROM_sha256=sha(a.prepared/'baseline.nes'),public_ABI_state_cases=len(public),hot_state_cases=len(hot),whole_audio_frames=1400,no_dirty_nonfinal_hot_saved_min=min(r['saved']for r in no_dirty),no_dirty_nonfinal_hot_saved_max=max(r['saved']for r in no_dirty),all_original_raw_hardware_and_all_actual_nonstack_writes_equal_except_dead52=True,dead52_new_meaning='SavedY only on successful C28 steady path; generic bank cache retains dominant write before every restore read.',scope='Initial source/CPU proof, not full readiness. Public noise input/output ABI and final RAM equal for every valid0..42 frame,all dirty combinations, raw high0/7,Pvariants. Hot path restores every live register/flag; only dead cache52 differs. Complete100update hardware equality all7events/bothmodes. Full ordered-image/priority/IRQ/ordinary/layout/producer/flagoff/native remain required.',tool_sha256=sha(__file__));(a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
