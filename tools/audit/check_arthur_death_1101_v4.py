"""Actual HuDeath/Arthur/native timer-worker execution and interrupt cuts."""
import json,itertools
import prepare_arthur_death_1101_v4 as P
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location


def state(c):return(c.pc,c.a,c.x,c.y,c.p,c.sp)


def main():
 b=scoped_load(P.O/'candidate.nes');old=scoped_load(P.P.O/'candidate.nes')
 at=location(b,'ArHostNativeDeath');delta=[i for i,(a,z)in enumerate(zip(b['raw'],old['raw']))if a!=z]
 assert len(delta)==3 and all(at<=i<at+19 for i in delta)
 base=M.fresh(b);M.put(base,SelectedCharacter=32,OperMode=1,GameEngineSubroutine=11,ArHostReady=167,ArDead=1,MmDeathFlag=1,MmDeathAge=0,FamilyMainCommit=1,NmiDisable=255)
 sig=location(b,'ArCacheSignature');base.ram[2][0x1fe0:0x1ff0]=b['raw'][sig:sig+16]
 rows=[];calls=0
 for pit,p in itertools.product([0,1],[0x20,0x31,0x61,0xa1]):
  m=M.fork(base);M.put(m,MmDeathPit=pit,TimerControl=255)
  limit=150 if pit else 168
  for age in range(1,limit+1):
   z=M.invoke(m,'HuDeath',a=85,x=19,y=73,p=p)
   assert M.get(m,'MmDeathAge')==age,(pit,p,age,M.get(m,'MmDeathAge'),z)
   assert M.get(m,'GameEngineSubroutine')==(6 if age==limit else 11)
   assert M.get(m,'TimerControl')==(0 if age==limit else 255)
   assert M.get(m,'ArDead')==1
   assert M.get(m,'CurrentBank')==M.get(base,'CurrentBank') and M.get(m,'CurrentBankC')==M.get(base,'CurrentBankC')
   calls+=1
  rows.append(dict(pit=pit,flags=p,updates=limit,exit_engine=6))
 cuts={};cls=M.NesMPU;step=cls.step
 def record(c):
  if 0xdf7f<=c.pc<0xdf92 and c.memory.rawtags[(c.pc-0x8000)//8192]==191:cuts.setdefault((c.pc,c.sp),(M.fork(c.memory),state(c)))
  return step(c)
 cls.step=record
 try:M.invoke(M.fork(base),'HuDeath')
 finally:cls.step=step
 for kind,(m0,s) in itertools.product(['IRQ','lag-NMI'],cuts.values()):
  m=M.fork(m0);c=cls(memory=m,pc=s[0]);c.pc,c.a,c.x,c.y,c.p,c.sp=s
  before=state(c);smc=bytes(m[0x15a:0x17b]);live=bytes(m[0x101+c.sp:0x200]);maps=m.rawtags[:]
  shadows=[M.get(m,'CurrentBank'),M.get(m,'CurrentBankC')]
  if kind=='IRQ':c.irq()
  else:c.nmi()
  for _ in range(100000):
   if state(c)==before:break
   assert m[c.pc]!=0,(kind,hex(before[0]),'BRK');c.step()
  else:raise AssertionError((kind,hex(before[0]),'ISR bound'))
  assert bytes(m[0x15a:0x17b])==smc and bytes(m[0x101+c.sp:0x200])==live
  assert m.rawtags==maps and [M.get(m,'CurrentBank'),M.get(m,'CurrentBankC')]==shadows and m.ram==m0.ram
 q=dict(passed=True,ROM_sha256=P.sha(P.O/'candidate.nes'),changed_ROM_bytes=3,actual_HuDeath_updates=calls,timed_sequences=rows,interrupt_cuts=len(cuts)*2,unique_leaf_boundaries=len(cuts),scope='Real native guest timer worker through actual HuDeath/Arthur/farcall chain,150pit/168normal threshold and balanced ABI/mapping. CPU fixture seeds death context; separate controller-earned native pit/restart packet has noRAMseeds. Not a native life-restart proof.')
 (P.O/'CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
