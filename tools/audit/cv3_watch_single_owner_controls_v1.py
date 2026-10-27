"""Finite source-only timer/caller/IRQ controls; no emulator launch."""
from pathlib import Path
import hashlib,itertools,json
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location
from current_roster_compact_11_v1 import BASE
from current_link_simon_powerups_prepare_v1 import setup,target
from current_cv3_powerups_prepare_v1 import source_campaign,plans
from verify_native_relocation import NesMPU
import proto_palette_coalesce_controls_v1 as cpuhelper
class TimedMPU(NesMPU):
 cycletime=list(NesMPU.cycletime);cycletime[0xce]=6
cpuhelper.NesMPU=TimedMPU
run=cpuhelper.run
R=Path(__file__).resolve().parents[2];B=R/'build';P=B/'mega_proto_body_palette_9ea.nes';N=B/'cv3_watch_single_owner.nes'
OLD='ab221e81821dd10690ad3a1068d91c9efae6c7406230d9bd7fc4a729fdc433d2';NEW='9a1b68c0a26ea86ff8c4712af66b8de8cd5ed2de13c74db1bfaf15eb9e2ba333'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8',newline='\n')
regs=lambda c:(c.a,c.x,c.y,c.p&207,c.sp)
def fresh(b,identity='grant',mode=1):
 _,char,variant,value=BASE[identity];q=Arena(b,char)
 q.put(PlayerStatus=0,OperMode_Task=3,AreaType=1,CrossoverBehaviorVersion=mode,NumberofLives=2,AreaPointer=194,WorldNumber=0,LevelNumber=0)
 if variant:q.set(variant,value)
 q.invoke('RosterClearState');q.invoke('InventoryInit');q.array('GameTimerDisplay',[3,9,9]);setup(q,char,dict(kind='use',item=0));q.set('SavedJoypadBits',0);q.invoke('GameLoop');return q
def same(qs,cs,allowed=()):
 assert regs(cs[0])==regs(cs[1])and qs[0].m.banks==qs[1].m.banks,('AXYP/banks',regs(cs[0]),regs(cs[1]))
 dif=[(i,qs[0].m[i],qs[1].m[i])for i in range(0x8000)if i not in allowed and qs[0].m[i]!=qs[1].m[i]]
 assert not dif,[(hex(i),a,b)for i,a,b in dif[:12]]
 assert [(a,v)for a,v in qs[0].m.writes if a not in allowed]==[(a,v)for a,v in qs[1].m.writes if a not in allowed]
def main():
 assert sha(P)==OLD and sha(N)==NEW;old,new=scoped_load(P),scoped_load(N);out=B/'cv3_watch_single_owner_controls.json';assert not out.exists()
 whole=[]
 for identity,mode,count in itertools.product(BASE,[0,1],[0,1,2,179,180,255]):
  qs=[fresh(b,identity,mode)for b in [old,new]]
  for q in qs:q.set('AvStopwatch',count)
  cs=[run(q,'GameLoop')[0]for q in qs];cv3=identity in ['grant','sypha','alucard']
  same(qs,cs,{address(old,'AvStopwatch')}if cv3 else())
  values=[q.get('AvStopwatch')for q in qs]
  if cv3:assert values==[max(0,count-2),max(0,count-1)]
  else:assert values[0]==values[1]
  delta=cs[1].processorCycles-cs[0].processorCycles
  assert delta==((-4 if count<=1 else-9)if cv3 else 0),(identity,mode,count,delta)
  whole.append(dict(identity=identity,mode=mode,initial=count,final=values,delta=delta))
 guarded=[]
 for identity,state in itertools.product(['grant','sypha','alucard'],[dict(TimerControl=1),dict(TimerControl=255),dict(GameEngineSubroutine=9),dict(GameEngineSubroutine=10),dict(MmDeathFlag=1)]):
  qs=[fresh(b,identity)for b in [old,new]]
  for q in qs:q.put(AvStopwatch=180,**state)
  cs=[run(q,'Cv3WeaponsGate')[0]for q in qs];same(qs,cs)
  assert cs[0].processorCycles==cs[1].processorCycles and qs[1].get('AvStopwatch')==180
  guarded.append(dict(identity=identity,state=state,cycles=cs[1].processorCycles,all_state_exact=True))
 helper=[]
 for count,freeze,flags in itertools.product([0,1,2,179,180,255],[0,1,5],[0x20,0x21,0x60,0xa2,0xeb]):
  qs=[fresh(b)for b in [old,new]]
  for q in qs:
   q.put(AvStopwatch=count);q.set('Cv3FrozenTimer',freeze,0);q.set('AvFrozen',freeze,0);q.set('Cv3FrozenID',6,0)
   if freeze:target(q,192,184)
  cs=[run(q,'Cv3FreezeTick',flags=flags)[0]for q in qs];same(qs,cs,{address(old,'AvStopwatch')})
  assert qs[1].get('AvStopwatch')==count and qs[0].get('AvStopwatch')==max(0,count-1)
  delta=cs[1].processorCycles-cs[0].processorCycles;assert delta==(-4 if count==0 else-9)
  helper.append(dict(count=count,freeze=freeze,flags=flags,delta=delta))
 earned=source_campaign(new,1,plans(1),watch_expected=180);assert earned['passed']
 watch=next(z for z in earned['cases']if z['name']=='use-watch');writes=watch['watch_writes'];assert writes[0][1]==180
 assert [x[1]for x in writes]==list(range(180,-1,-1))and len({(x[2],x[3])for x in writes[1:]})==1
 assert writes[1][0]==writes[0][0]+1 and writes[-1][0]==writes[0][0]+180
 # Actual Main calls weapons before NPC AI. Birth180 freezes NPCs; the next
 #179 updates stay frozen and update180 decrements1->0 then resumes NPC AI.
 clock=[]
 for identity in ['grant','sypha','alucard','simon']:
  q=fresh(new,identity);target(q,192,184);q.set('Enemy_X_Speed',248,0);q.set('AvStopwatch',180);xy=[q.get('Enemy_X_Position'),q.get('Enemy_Y_Position')];rows=[]
  for tick in range(1,181):
   run(q,'GameLoop');pos=[q.get('Enemy_X_Position'),q.get('Enemy_Y_Position')]
   assert q.get('AvStopwatch')==max(0,180-tick)
   if tick<180:assert pos==xy,(identity,tick,pos,xy)
   else:assert pos!=xy,(identity,'NPC did not resume on zero update')
   if tick in [1,179,180]:rows.append(dict(tick=tick,remaining=q.get('AvStopwatch'),NPC=pos))
  clock.append(dict(identity=identity,subsequent_frozen_AI_updates=179,resume_on_zero_update=180,birth_update_also_frozen=True,phase_rows=rows))
 q=fresh(new);q.put(AvStopwatch=180);target(q,192,184);q.set('Cv3FrozenTimer',5,0);q.set('AvFrozen',5,0);q.set('Cv3FrozenID',6,0)
 image=list(q.m);banks=q.m.banks[:]
 def again():
  t=Arena(new,5);list.__setitem__(t.m,slice(None),image);t.m.banks=banks[:];return t
 q=again();cpu,trace=run(q,'Cv3FreezeTick',record=True);lo=address(new,'Cv3FreezeTick');hi=lo+int(new['syms']['Cv3FreezeTick']['size'],0);keys=sorted({k for k in trace if k[1]==84 and lo<=k[0]<hi})
 def stable(t):return bytes(t.m[:0x1c0]+t.m[0x200:0x2006]+t.m[0x2007:0x8000]),t.m.banks
 wanted=regs(cpu),stable(q);irqs=[]
 for key in keys:
  t=again();c,_=run(t,'Cv3FreezeTick',inject=key);assert(regs(c),stable(t))==wanted,('IRQ',key)
  live=lambda a:not 0x1c0<=a<0x200
  nonirq=[(a,v)for i,(a,v)in enumerate(t.m.writes)if i not in t.m.irq_indices and live(a)]
  assert nonirq==[(a,v)for a,v in q.m.writes if live(a)]
  io=[(a,v)for i,(a,v)in enumerate(t.m.writes)if i in t.m.irq_indices and a>=0x2000];split=t.get('IrqNewScroll');control=t.get('IrqPPUCTRL')
  assert io==[(0x2006,(control&1)<<2),(0x5128,0),(0x2005,32),(0x2005,split),(0x2006,128|(split>>3))]
  irqs.append(dict(pc=key[0],bank=key[1],extra_cycles=c.processorCycles-cpu.processorCycles,native_ordered_IO=io))
 put(out,dict(passed=True,source_CPU_only=True,native_run=False,parent_sha256=OLD,candidate_sha256=NEW,whole_GameLoop_cases=whole,all37_two_modes_6_timer_values=len(whole),guarded_owner_calls=guarded,helper_full_AXYP_RAM_writes_cases=helper,earned_Grant_complete_GameLoops=earned,watch_birth180_then180_decrements=True,NPC_engine_phase=clock,actual_IRQ_cases=irqs,local_CPU_cycle_correction='Copied TimedMPU cycletime table CE=6; stock shared py65 hasCE=3. No shared file/class table modified. Draft raw-model -6 observation corrected to actual opcode timing -9 active/-4 idle.',retained_setup_negatives=['Original Grant complete source campaign remainsFALSE:180->179->178 through two owners,90active updates.','First private link omitted required postlink E-clone producer; retained setup-negative hash before completion.','Initial raw py65 DECabs cycle table predicted -6 versus NMOS -9; isolated table correction only.','Initial source clock assumption put enemy AI before weapons; actual game.s calls weapons first. Final proof asserts native phase, not invented181-update duration.','Unbound source writer cp1252 rejected a Unicode minus; rewritten ASCII before any receipt.'],limits='Source CPU only; no actual NMI/vblank/PPU/DMA/waveform/native campaign or cadence qualification.',bindings={str(p):sha(p)for p in [Path(__file__),P,P.with_suffix('.dbg'),N,N.with_suffix('.dbg'),B/'cv3_watch_single_owner_build.json',R/'tools/audit/current_cv3_powerups_prepare_v1.py',R/'src/remaining_weapons.s',R/'src/object.s',R/'src/game.s']}))
 print(json.dumps(dict(passed=True,output=str(out),sha256=sha(out),whole_cases=len(whole),helper_cases=len(helper),IRQ=len(irqs),source_earned_calls=earned['GameLoop_calls'])))
if __name__=='__main__':main()
