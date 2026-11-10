"""Private complete-Main gameplay controls; actual linked CPU, no native."""
from pathlib import Path
import argparse,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import dragon_power_movement_controls_v2 as M
from sunny_integrated_controls_v1 import *
O=R/'build/dragon-power-gameplay-v1';P=R/'build/dragon-power-movement-v1'
def setup(b,ch=24):
 q=M.setup(b,ch);q.put(GameTimerDisplay=4)
 return q
def actor(q,slot=0,kind=6,x=128,y=176):
 q.set('Enemy_ID',kind,slot);q.set('Enemy_Flag',1,slot);q.set('Enemy_State',0,slot)
 q.set('Enemy_X_Position',x,slot);q.set('Enemy_PageLoc',0,slot);q.set('Enemy_Y_Position',y,slot);q.set('Enemy_Y_HighPos',1,slot)
 q.set('EnemyOffscrBitsMasked',0,slot);q.set('Enemy_BoundBoxCtrl',3,slot)
 q.put(ObjectOffset=slot)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert not a.output.exists()
 b=scoped_load(O/'candidate.nes');old=scoped_load(P/'candidate.nes');proof=dict(passed=False,source_CPU_only=True,native_run=False,checks={});ck=proof['checks']
 try:
  for n in old['syms']:
   if n.startswith('Dp') and n in b['syms'] and '::'not in n:assert address(b,n)==address(old,n),('old Goku PC',n,hex(address(old,n)),hex(address(b,n)))
  ck['old_Goku_PC_exact']=True
  rows=[]
  for ch,mode,keys in itertools.product([0,1,2,4,5,6,8,13,15,19,20,21,22,23,25,26,27,28],range(2),[0,129]):
   pair=[]
   for v in[old,b]:
    q=setup(v,ch);q.put(CrossoverBehaviorVersion=mode,SavedJoypadBits=keys)
    c,tr,mn=M.runtrace(q,'GameLoop',p=0x71)
    state=(registers(c),M.fastapp(q),bytes(q.m[0x100:0x17b]),tuple(q.m.banks))
    writes=[(i,x)for i,x in q.m.writes if not 0x100<=i<0x200 and not 0x5114<=i<=0x5117 and i not in smc_at(v)]
    pair.append((state,writes,c.processorCycles,mn))
   assert pair[0][:2]==pair[1][:2],('foreign Main',ch,mode,keys,pair[0][0][0],pair[1][0][0]);rows.append([ch,mode,keys,pair[1][2]-pair[0][2],pair[1][3]])
  ck['foreign_complete_Main']=dict(cases=len(rows),rows=rows,AXYP_SP_fullapplication_live_page1_final_banks_exact=True,remaining_ordered_writes_exact=True)
  rows=[]
  for mode,face in itertools.product(range(2),[1,2]):
   q=setup(b);q.put(CrossoverBehaviorVersion=mode,PlayerFacingDir=face)
   costs=[]
   for age in range(128):
    keys=(1 if face==1 else 2)|(128 if 2<=age<12 else 0)|(64 if 30<=age<32 or 65<=age<67 else 0)
    q.put(SavedJoypadBits=keys,NmiDisable=255,VRAM_Buffer1_Offset=0)
    c,tr,mn=M.runtrace(q,'GameLoop');costs.append(c.processorCycles)
    assert tr.count((86,address(b,'DpSourceFrame')))==1,('one original source tick',mode,face,age)
    assert (126,address(b,'PlayerBGCollision'))not in tr
    assert q.get('DpHungerPeriod')==1 and q.get('DpHP')==100-(age+1)//60
    assert q.get('CurrentBank')&127==q.m.banks[1]and q.get('CurrentBankC')&127==q.m.banks[2]
   rows.append([mode,face,min(costs),max(costs),mn,q.get('DpClock'),q.get('DpHP')])
  ck['complete_Main_source_clock_hunger_render']=dict(updates=512,rows=rows)
  # True controller-earned punches, repeated hits with source cooldown, full
  # actual native actor update/score path. Scene setup only, no hit/outcome seed.
  rows=[]
  for face in[1,2]:
   q=setup(b);q.put(CrossoverBehaviorVersion=1,PlayerFacingDir=face)
   target=128 if face==1 else 64;actor(q,x=target)
   hits=[];last=0;seen=set()
   for age in range(180):
    keys=(1 if face==1 else 2)if age<1 else 0
    if age%18==2:keys|=64
    q.put(SavedJoypadBits=keys,NmiDisable=255,VRAM_Buffer1_Offset=0)
    c,tr,mn=M.runtrace(q,'GameLoop');seen.update(tr)
    hp=q.get('MmEnemyHealthLo',0)
    if hp!=last:hits.append([age,hp,q.get('Enemy_State',0)]);last=hp
    if q.get('Enemy_State',0)&32:break
   rows.append(dict(face=face,hits=hits,defeated=bool(q.get('Enemy_State',0)&32),source_point_reached=(86,address(b,'DpSourceTestPoint'))in seen,native_defeat_reached=(126,address(b,'ShellOrBlockDefeat'))in seen))
  ck['real_Main_punch_scene_observations']=rows
  # Actual collection admission: six real slots, emerging vs mature, stale OO.
  rows=[]
  for slot,mode,kind,mature in itertools.product(range(6),range(2),range(2),[False,True]):
   q=setup(b);run(q,'DpEnsure');actor(q,slot,0x2e,96,176)
   q.set('PowerUpType',kind,slot);q.set('Enemy_State',0x80 if mature else 0,slot);q.put(ObjectOffset=(slot+1)%6)
   before=[q.get(n)for n in['DpHP','DpPole','DpWaves','DpPower']]
   c,tr,mn=M.runtrace(q,'NrPickup',x=slot,p=0x71)
   if mature:
    assert q.get('Enemy_Flag',slot)==0 and (126,address(b,'EraseEnemyObject'))in tr,('erase',slot,kind)
    assert q.get('FloateyNum_Control',slot)==6 and q.get('Square2SoundQueue')==32
    assert q.get('DpPole')==1 if kind==0 else q.get('DpWaves')==3
   else:assert before==[q.get(n)for n in['DpHP','DpPole','DpWaves','DpPower']]and q.get('Enemy_Flag',slot)==1
   rows.append([slot,mode,kind,mature,c.processorCycles,mn])
  ck['real_pickup_consumer_maturity_actual_X']=dict(cases=len(rows),rows=rows)
  proof['passed']=True
 except Exception as e:proof.update(failure=repr(e),traceback=traceback.format_exc())
 proof['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(M.__file__),O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',P/'candidate.nes',R/'build/dragon_power_gameplay_core_v1.inc',R/'build/dragon_power_gameplay_c_v1.inc']}
 a.output.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=proof['passed'],failure=proof.get('failure'),checks=list(ck))));assert proof['passed']
if __name__=='__main__':main()
