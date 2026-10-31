"""Bowser actual native item/injury/lifecycle and safe palette queue consumers."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import bowser_current64_cold_controls_v1 as N
import bowser_gameplay_component_controls_v2 as T0
from check_tmnt_render_oa import load,address
T=T0.T;H=N.H;J=N.J;O=R/'build/bowser-current64-host-checks-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def boot(b,form):
 m=N.C.fresh(b,0);H.put(m,CrossoverMenuIndex=26,FmAlts=form,SelectedCharacter=0)
 for n in ['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:N.invoke(m,n)
 H.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0);N.invoke(m,'GameMenuRoutine');N.invoke(m,'PauseRoutine',a=0)
 for age in range(1000):
  if H.get(m,'OperMode_Task')==3 and H.get(m,'GameEngineSubroutine')==8:return m
  H.put(m,SavedJoypad1Bits=0,SavedJoypadBits=0,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
  N.invoke(m,'GameLoop');N.C.A.consume(m)
 raise AssertionError('native parser bound')
def route(m,slot,**kw):return T.call(m,'BwServiceVeneers',slot=slot,**kw)
def main():
 O.mkdir(exist_ok=False);q=dict(passed=False,source_CPU=True,native=False,checks={});ck=q['checks']
 try:
  b=load(J/'candidate.nes');seeds={form:boot(b,form)for form in [0,8]}
  rows=[]
  for form,slot,kind,mature in itertools.product([0,8],range(6),[0,1],[0,1]):
   m=T.fork(seeds[form]);H.put(m,ObjectOffset=(slot+1)%6)
   for n,v in [('Enemy_ID',46),('Enemy_Flag',1),('Enemy_State',128 if mature else 0),('PowerUpType',kind)]:m[address(b,n)+slot]=v
   c,lo=route(m,24,x=slot);tier=m.ram[3][0x1e28]
   assert tier==((1 if kind==0 else 2)if mature else 0),(form,slot,kind,mature,tier)
   if mature:
    assert not m[address(b,'Enemy_Flag')+slot]
    assert m[address(b,'FloateyNum_Control')+slot]==6 and H.get(m,'Square2SoundQueue')==32
    assert m.ram[3][0x1e29]==(5 if form else 34)
   else:assert m[address(b,'Enemy_Flag')+slot]==1
   rows.append([form,slot,kind,mature,tier,c.processorCycles,lo])
  ck['actual_6slot_mature_emerging_mushroom_flower_native_erase_score_sound']=rows
  rows=[]
  for form in [0,8]:
   m=T.fork(seeds[form]);hp=m.ram[3][0x1e29]
   H.put(m,InjuryTimer=0);route(m,5);assert m.ram[3][0x1e29]==hp-1 and H.get(m,'InjuryTimer')==90
   route(m,5);assert m.ram[3][0x1e29]==hp-1
   for player,expected in [(1,hp),(0,hp-1)]:
    H.put(m,CurrentPlayer=player,FamilyMainCommit=1,NmiDisable=255,DisableScreenFlag=1,Mirror_PPUMASK=0)
    T.call(m,'BwScene');assert m.ram[3][0x1e29]==expected and not m.ram[3][0x1e80] and not m.ram[3][0x1e8a]
   H.put(m,NumberofLives=1,FamilyMainCommit=1,NmiDisable=255,DisableScreenFlag=1,Mirror_PPUMASK=0);T.call(m,'BwScene')
   assert m.ram[3][0x1e29]==hp
   # Exhaust actual source health through genuine injury callbacks.
   for i in range(hp):H.put(m,InjuryTimer=0);route(m,5)
   assert m.ram[3][0x1e29]==0 and H.get(m,'GameEngineSubroutine')==11
   H.put(m,TimerControl=200,Mirror_PPUMASK=30,DisableScreenFlag=0)
   before=H.get(m,'Player_Y_Position');r=N.invoke(m,'GameLoop')
   assert r['counts'].get('BwMovement',0)==0,('native auto death must retain native movement',form,r)
   rows.append(dict(form=form,source_health=hp,native_death_engine=11,oldY=before,newY=H.get(m,'Player_Y_Position'),MainCPU=r['CPU']))
  ck['real_health_protection_2player_scene_life_death']=rows
  rows=[]
  for task,off in itertools.product([2,3],range(85)):
   m=T.fork(seeds[0]);H.put(m,OperMode_Task=task,VRAM_Buffer1_Offset=off)
   a=address(b,'VRAM_Buffer1');m.writes.clear();old=bytes(m[a:a+100]);c,lo=T.call(m,'BwColors')
   writes=[(x-a,v)for x,v in m.writes if a<=x<a+100]
   assert all(0<=i<84 for i,v in writes),(task,off,writes)
   if off>=74:assert bytes(m[a:a+100])==old and not c.p&1
   else:
    extra=10 if task==3 else 6
    assert H.get(m,'VRAM_Buffer1_Offset')==off+extra and m[a+off+extra]==0 and c.p&1
   rows.append([task,off,H.get(m,'VRAM_Buffer1_Offset'),len(writes),c.processorCycles])
  ck['actual_body_native_backdrop_queue_84B_all_boundary_offsets']=rows
  q['passed']=True
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(N.__file__),J/'candidate.nes',J/'candidate.dbg',J/'bowser.bin']}
 (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=q['passed'],error=q.get('error'),traceback=q.get('traceback'))));assert q['passed']
if __name__=='__main__':main()
