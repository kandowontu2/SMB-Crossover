"""Finite source CPU ownership/lifecycle/IRQ controls for private CV3 life gains."""
from pathlib import Path
import collections,itertools,json,hashlib
from cv3_watch_single_owner_controls_v1 import fresh,run,TimedMPU,BASE
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location
from current_cv3_powerups_prepare_v1 import source_campaign,plans
from current_shared_star_life_prepare_v1 import actor,hooks_for
from current_link_simon_powerups_prepare_v1 import setup,target
R=Path(__file__).resolve().parents[2];B=R/'build';P=B/'cv3_watch_single_owner.nes';N=B/'cv3_life_gain_watch.nes'
OLD='9a1b68c0a26ea86ff8c4712af66b8de8cd5ed2de13c74db1bfaf15eb9e2ba333';NEW='bdf9ca2bfe69ee93ca85f1b5e5319e474d9f01aa641c79a58cd9bd602253c40e'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8',newline='\n')
regs=lambda c:(c.a,c.x,c.y,c.p&207,c.sp)
def clone(b,image,banks):
 q=Arena(b,5);list.__setitem__(q.m,slice(None),image);q.m.banks=banks[:];return q
def live(q,irq=False):
 # Only dead CPU stack residue is omitted. All genuine page1 SMC stays exact.
 keep=set()
 for g in q.b['segs'].values():
  if g['name']=='"SMCCODE"':keep.update(range(int(g['start'],0),int(g['start'],0)+int(g['size'],0)))
 # $2006 is an actual PPUADDR port, not foreground RAM. IRQ's required
 # five ordered hardware stores below prove its intentional MMIO side effect.
 rest=q.m[512:0x2006]+q.m[0x2007:0x8000]if irq else q.m[512:0x8000]
 return bytes(q.m[:256]+[q.m[i]for i in sorted(keep)]+rest),q.m.banks
def bus(q,omit=()):
 return[(a,v)for i,(a,v)in enumerate(q.m.writes)if i not in getattr(q.m,'irq_indices',set())and(not 256<=a<512 or any(g['name']=='"SMCCODE"'and int(g['start'],0)<=a<int(g['start'],0)+int(g['size'],0)for g in q.b['segs'].values()))and a not in omit]
def stats(q,v):return[q.get(n,v-1)for n in ['Cv3Health','Cv3Hearts','Cv3Subweapon','Cv3Power']]
def earned_life(b,v,mode):
 q=fresh(b,['','grant','sypha','alucard'][v],mode);calls=1;owners=[];hooks,_=hooks_for(b);increment=hooks['LifeIncrement'];physical=hooks['PhysicalPickup'];original=TimedMPU.step
 equipment=212 if v==3 else 209
 def main(bits=0):
  nonlocal calls
  q.set('SavedJoypadBits',bits);calls+=1;c,w=q.invoke('GameLoop');assert q.get('MmDeathFlag')==q.get('Cv3HurtAge')==q.get('Cv3Invul')==0
  return w
 # Real source preparation stamps a mature flower; no earned field is seeded.
 setup(q,5,dict(kind='use',item=0));actor(q,46,5,1,5);q.invoke('Cv3PreparePickupGate',x=5)
 assert q.get('InvPickup',5)==equipment and q.get('Cv3PickupVariant',5)==v
 for _ in range(20):
  w=main()
  if q.get('Enemy_Flag',5)==0:break
 else:raise AssertionError('Actual equipment pickup missing')
 before=stats(q,v);assert before==([64,10,0,1]if v==3 else[64,15,1,0])
 lives=q.get('NumberofLives');actor(q,46,5,3,5);gains=[];collisions=[]
 def step(c):
  pc=c.pc;k=q.m.banks[(pc-0x8000)//8192]if pc>=0x8000 else-1
  if pc==increment['pc']and k in increment['banks']:
   gains.append(dict(call=calls,pc=pc,bank=k,before=q.get('NumberofLives'),popup=q.get('FloateyNum_Timer',c.x),slot=c.x));assert c.x==5 and q.get('FloateyNum_Timer',5)==42
  if pc==physical['pc']and k in physical['banks']:collisions.append(dict(call=calls,slot=c.x,type=q.get('PowerUpType',c.x)))
  original(c)
 # Arena.invoke uses shared NesMPU, whose inherited step must observe real calls.
 from verify_native_relocation import NesMPU
 oldstep=NesMPU.step;NesMPU.step=step
 try:
  for _ in range(90):
   main();assert stats(q,v)==before,('Actual earned equipment lost',v,mode,stats(q,v),before)
   if len(gains)==1 and q.get('FloateyNum_Control',5)==0:break
  else:raise AssertionError('Physical1-Up gain/cleanup missing')
 finally:NesMPU.step=oldstep
 assert collisions==[dict(call=collisions[0]['call'],slot=5,type=3)]and len(gains)==1
 assert q.get('NumberofLives')==(lives+1)&255 and q.get('Cv3LastLife')==q.get('NumberofLives')
 # Actually fire the retained subweapon/tier and hit a default-health target.
 setup(q,5,dict(kind='use',item=0));placed=False;allocations=0;defeats=0;start_hearts=q.get('Cv3Hearts',v-1);seen=[]
 from verify_native_relocation import NesMPU
 original=NesMPU.step
 def use_step(c):
  nonlocal defeats
  k=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
  if c.pc==address(b,'ShellOrBlockDefeat')and k==(location(b,'ShellOrBlockDefeat')-16)//8192 and c.x==0:defeats+=1
  original(c)
 NesMPU.step=use_step
 try:
  for age in range(321):
   if not placed:
    for i in range(4):
     if q.get('Cv3ShotType',i)and q.get('Cv3ShotPage',i)==0 and 110<=q.get('Cv3ShotX',i)<=220:
      target(q,q.get('Cv3ShotX',i)-6,min(184,q.get('Cv3ShotY',i)-8));placed=True;break
   w=main((64+(0 if v==3 else 8))if 6<=age<=8 else 0)
   for z in w:
    if address(b,'Cv3ShotType')<=z['address']<address(b,'Cv3ShotType')+4 and z['value']:
     allocations+=1;seen.append(z['value'])
 finally:NesMPU.step=original
 assert placed and defeats>0 and allocations==(2 if v==3 else 1)and set(seen)=={6 if v==3 else 3 if v==2 else 1}
 assert q.get('Cv3Hearts',v-1)==start_hearts-(0 if v==3 else 1)and all(q.get('Cv3ShotType',i)==0 for i in range(4))
 return dict(variant=v,mode=mode,complete_GameLoops=calls,earned_stamp=equipment,earned_fields=before,actual_1Up_increment=gains[0],real_life_collisions=collisions,initial_lives=lives,final_lives=q.get('NumberofLives'),carried_or_tier_retained=True,retained_weapon_allocations=allocations,native_source_defeats=defeats,real_special_cost=0 if v==3 else 1,no_earned_field_or_life_or_outcome_seeds=True)
def main():
 assert sha(P)==OLD and sha(N)==NEW;out=B/'cv3_life_gain_watch_controls.json';assert not out.exists();old,new=scoped_load(P),scoped_load(N)
 samples=[];cycles=collections.defaultdict(collections.Counter);count=0;full=[]
 for v,mode in itertools.product([1,2,3],[0,1]):
  seed=fresh(old,['','grant','sypha','alucard'][v],mode)
  # Boundary controls intentionally stage representative existing save records;
  # earned invariants are proved separately below without resource setup writes.
  for i in range(3):
   for n,z in [('Cv3Health',47+i),('Cv3Hearts',31+i),('Cv3Subweapon',2),('Cv3Power',2)]:seed.set(n,z,i)
  image=list(seed.m);banks=seed.m.banks[:]
  for previous,delta,flags in itertools.product([0,1,2,127,128,254,255],[0,1,2,7,127,-1,-2,-128],[0x20,0x61,0xeb]):
   current=(previous+delta)&255;gain=delta>0;qs=[clone(b,image,banks)for b in[old,new]]
   for q in qs:q.put(NumberofLives=current,Cv3LastLife=previous)
   if gain:qs[0].set('Cv3LastLife',current)
   cs=[run(q,'Cv3Ensure',flags=flags)[0]for q in qs]
   assert regs(cs[0])==regs(cs[1])and live(qs[0])==live(qs[1]),(v,mode,previous,delta,flags,regs(cs[0]),regs(cs[1]))
   assert bus(qs[0],{address(old,'Cv3LastLife')}if gain else())==bus(qs[1],{address(old,'Cv3LastLife')}if gain else())
   assert stats(qs[1],v)==([64,10,0,0]if delta<0 else stats(seed,v))
   kind='gain'if gain else'loss'if delta<0 else'equal';cost=cs[1].processorCycles-cs[0].processorCycles;cycles[kind][cost]+=1
   if not delta:assert cost==0
   if flags==0x20 and v==1 and mode==0:samples.append(dict(previous=previous,current=current,delta=delta,kind=kind,final_life=qs[1].get('Cv3LastLife'),fields=stats(qs[1],v),cycles_vs_equivalent_reference=cost))
   count+=1
  # Gains must still pass through original area/world/variant handling.
  for changed in[dict(AreaPointer=195),dict(WorldNumber=1),dict(AreaPointer=195,WorldNumber=1)]:
   qs=[clone(b,image,banks)for b in[old,new]]
   for q in qs:q.put(NumberofLives=3,Cv3LastLife=2,Cv3AttackAge=9,Cv3JumpActive=1,**changed)
   qs[0].set('Cv3LastLife',3);cs=[run(q,'Cv3Ensure')[0]for q in qs]
   assert regs(cs[0])==regs(cs[1])and live(qs[0])==live(qs[1]);assert bus(qs[0],{address(old,'Cv3LastLife')})==bus(qs[1],{address(old,'Cv3LastLife')})
   assert qs[1].get('Cv3AttackAge')==qs[1].get('Cv3JumpActive')==0 and stats(qs[1],v)==stats(seed,v)
 # All genuine outer identities, two modes and gains/losses/equal. Foreign
 # Cv3Ensure is never admitted; its RAM, CPU registers, SMC and cycles exact.
 for identity,mode,delta in itertools.product(BASE,[0,1],[-1,0,1]):
  qs=[fresh(b,identity,mode)for b in[old,new]];cv3=identity in['grant','sypha','alucard']
  for q in qs:q.put(Cv3LastLife=2,NumberofLives=2+delta)
  if cv3 and delta>0:qs[0].set('Cv3LastLife',3)
  cs=[run(q,'GameLoop')[0]for q in qs]
  assert regs(cs[0])==regs(cs[1])and live(qs[0])==live(qs[1]),('Full GameLoop',identity,mode,delta)
  assert bus(qs[0],{address(old,'Cv3LastLife')}if cv3 and delta>0 else())==bus(qs[1],{address(old,'Cv3LastLife')}if cv3 and delta>0 else())
  d=cs[1].processorCycles-cs[0].processorCycles
  if not cv3 or delta==0:assert d==0
  full.append(dict(identity=identity,mode=mode,delta=delta,cycles=d,all_live_state_SMC_banks_and_registers_exact=True))
 earned=[earned_life(new,v,mode)for v,mode in itertools.product([1,2,3],[0,1])]
 # Actual multiple native INC instructions before Ensure: source-bound cold
 # boundary inputs, not earned native acquisition. Zero life writes by Python.
 multiple=[]
 for v,initial in itertools.product([1,2,3],[0,1,127,250,254,255]):
  q=fresh(new,['','grant','sypha','alucard'][v]);q.put(NumberofLives=initial,Cv3LastLife=initial,CoinTally=99)
  before=stats(q,v);writers=[]
  _,ws=q.invoke('GiveOneCoin');writers.extend(z for z in ws if z['address']==address(new,'NumberofLives'))
  for slot in range(6):
   q.set('FloateyNum_Control',11,slot);q.set('FloateyNum_Timer',43,slot);_,ws=q.invoke('FloateyNumbersCore',x=slot);writers.extend(z for z in ws if z['address']==address(new,'NumberofLives'))
  assert len(writers)==7 and [z['value']for z in writers]==[(initial+i)&255 for i in range(1,8)]
  run(q,'Cv3Ensure');assert stats(q,v)==before and q.get('Cv3LastLife')==(initial+7)&255
  multiple.append(dict(variant=v,initial=initial,final=q.get('NumberofLives'),actual_native_INC_writers=writers,fields_retained=True,scope='Source boundary actor/tally state, seven actual native INCs before Ensure; not a claimed earned acquisition or native same-Main scheduling capture.'))
 # Every actual reached new helper instruction gets a real hardware IRQ/RTI.
 irqs=[]
 for previous,current in[(2,3),(254,0),(2,1),(0,255)]:
  q=fresh(new);q.put(Cv3LastLife=previous,NumberofLives=current);image=list(q.m);banks=q.m.banks[:]
  a=clone(new,image,banks);c,trace=run(a,'Cv3Ensure',record=True);start=address(new,'Cv3LifeChanged');end=start+int(new['syms']['Cv3LifeChanged']['size'],0)
  keys=sorted({k for k in trace if k[1]==82 and start<=k[0]<end})
  for key in keys:
   t=clone(new,image,banks);d,_=run(t,'Cv3Ensure',inject=key)
   assert regs(d)==regs(c)and live(t,irq=True)==live(a,irq=True)and bus(t)==bus(a),('Actual IRQ',previous,current,key)
   io=[(at,value)for i,(at,value)in enumerate(t.m.writes)if i in t.m.irq_indices and at>=0x2000]
   assert io==[(0x2006,(t.get('IrqPPUCTRL')&1)<<2),(0x5128,0),(0x2005,32),(0x2005,t.get('IrqNewScroll')),(0x2006,128|(t.get('IrqNewScroll')>>3))]
   irqs.append(dict(previous=previous,current=current,pc=key[0],bank=82,cycles=d.processorCycles-c.processorCycles))
 # Reexecute the existing complete earned watch campaign on this exact union.
 watch=source_campaign(new,1,plans(1),watch_expected=180);assert watch['passed']
 core=(R/'src/game.s').read_text();assert 'cpx #$06'in core and core.count('jsr FloateyNumbersCore')==1
 put(out,dict(passed=True,source_CPU_only=True,native_run=False,candidate_sha256=NEW,watch_parent_sha256=OLD,full_Ensure_boundary_cases=count,boundary_scope='Representative legal source snapshots; deltas positive1..127 are gains, negative1..128 are losses. Unchanged/saturated equal values never enter the helper. No claim for arbitrary external jumps>=128; actual active native INC writer bound below.',boundary_samples=samples,cycle_histograms={k:dict(v)for k,v in cycles.items()},retained_area_world_cases=18,full_GameLoop_controls=full,actual_earned_source_campaigns=earned,multiple_INC_source_cases=multiple,actual_IRQs=irqs,existing_earned_watch=watch,active_writer_bound='GameCoreRoutine calls PlayerCtrl once (coin contact may grant at most one100-coin life; even all probes are bounded below128), then six EnemiesAndLoopsCore/FloateyNumbersCore slots once each. No active native writer can create128 INCs between Cv3Ensure entries. Actual six popup plus GiveOneCoin source instructions tested, including wrap. Death uses one DEC. New game/termination STA paths are outside active control and variant/area/world reset remains unchanged.',limits='Finite assembled CPU/source controls only. No native rendering/cadence/audio/physical menu or actual earned native1Up proof until ROOT runs prepared profile.',bindings={str(p):sha(p)for p in[Path(__file__),P,P.with_suffix('.dbg'),N,N.with_suffix('.dbg'),B/'cv3_life_gain_watch_build.json',R/'src/cv3_core.s',R/'src/cv3_pickups.s',R/'src/game.s',R/'src/player.s',R/'src/screen_render.s',R/'tools/audit/current_cv3_life_gain_counterexample_v1.py',B/'current_cv3_life_gain_counterexample_v1.json']}))
 print(json.dumps(dict(passed=True,path=str(out),sha256=sha(out),Ensure=count,full_GameLoop=len(full),IRQ=len(irqs),earned_calls=sum(x['complete_GameLoops']for x in earned),watch_calls=watch['GameLoop_calls'])))
if __name__=='__main__':main()
