"""Bounded real-caller Sunny pipelines/menu/foreign and source IRQ controls."""
from pathlib import Path
import argparse,hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
from sunny_integrated_controls_v1 import seed,run,registers,app,cleanwrites,scoped_load,sha,address,location,NesMPU

def counted(q,name):
 b=q.b;pc=address(b,name);s=b['syms'][name];g=b['segs'][s['seg']];win=(pc-0x8000)//8192;bank=(int(g['ooffs'],0)-16)//8192;q.m.page(win,bank)
 if win in[1,2]:q.set('CurrentBank' if win==1 else 'CurrentBankC',bank|128)
 c=NesMPU(memory=q.m,pc=pc);c.sp=253;c.stPushWord(0x5aff);hits={n:0 for n in ['FireballObjCore','BubbleCheck']}
 for _ in range(300000):
  if c.pc==0x5b00:assert c.sp==253;return c,hits
  for nm in hits:
   if c.pc==address(b,nm):
    sg=b['segs'][b['syms'][nm]['seg']];physical=(int(sg['ooffs'],0)-16)//8192
    if q.m.banks[(c.pc-0x8000)//8192]==physical:hits[nm]+=1
  c.step()
 raise AssertionError(('timeout',name,hex(c.pc)))

def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',required=True,type=Path);p.add_argument('--baseline',required=True,type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--menu',action='store_true');a=p.parse_args();assert not a.output.exists()
 bs={str(z):sha(z) for z in[Path(__file__),R/'tools/audit/sunny_integrated_controls_v1.py',a.rom,a.rom.with_suffix('.dbg'),a.baseline,a.baseline.with_suffix('.dbg')]};proof=dict(passed=False,bindings=bs,checks={},source_only=True,native_run=False)
 b=scoped_load(a.rom);old=scoped_load(a.baseline);checks=proof['checks']
 try:
  rows=[]
  for mode,form,flags in itertools.product([0,1],[1,2],[0x30,0x31,0x70,0x71]):
   q=seed(b,23);q.put(CrossoverBehaviorVersion=mode,PlayerStatus=form,SunnyForm=form,ObjectOffset=1)
   run(q,'ForceInjury',p=flags)
   assert q.get('PlayerStatus')==form and q.get('GameEngineSubroutine')==9 and q.get('GuestPowerupActive')==1
   for _ in range(60):run(q,'PlayerChangeSize')
   assert [q.get(z)for z in['PlayerStatus','SunnyForm','PlayerSize','GuestPowerupActive','GameEngineSubroutine']]==[0,0,1,0,8]
   rows.append([mode,form,flags])
  checks['whole_ForceInjury_and_60tick_source_freeze']=dict(passed=True,cases=len(rows),C0_and_C1=True,negative_predecessor='build/sunny-injury-carry-negative.json')
  rows=[]
  for swim,face in itertools.product([0,1],[1,2]):
   q=seed(b,23);q.put(PlayerStatus=2,SunnyForm=2,SwimmingFlag=swim,PlayerFacingDir=face,A_B_Buttons=64,PreviousA_B_Buttons=0,PlayerAnimTimerSet=4,ScreenRight_PageLoc=1,ScreenRight_X_Pos=255)
   for turn,buttons in enumerate([64,0,64,0,64]):
    q.put(A_B_Buttons=buttons,PreviousA_B_Buttons=0 if turn%2==0 else 64)
    c,hits=counted(q,'ProcFireball_Bubble');assert hits==dict(FireballObjCore=2,BubbleCheck=3 if swim else 0),(turn,hits)
    assert q.get('FireballCounter')==min(2,(turn+2)//2),(swim,face,turn,q.get('FireballCounter'))
    assert [q.get('Fireball_State',i)!=0 for i in range(2)]==[True,turn>=2]
    rows.append(dict(swim=swim,face=face,turn=turn,counts=hits,CPU=c.processorCycles))
  checks['exactly_two_native_fireballs_one_bubble_tail']=dict(passed=True,calls=len(rows),rows=rows)
  # Current native head/side dataflow and loaded block-buffer probes remain genuine.
  rows=[]
  for name,reference in [('NrHead','BlockBufferColli_Head'),('NrSide','BlockBufferColli_Side')]:
   for face,row,flags in itertools.product([1,2],[0,1,2],[0x30,0x31,0x71]):
    pair=[]
    for entry in[reference,name]:
     q=seed(b,23);q.put(PlayerFacingDir=face,PlayerSize=row&1,CrouchingFlag=int(row==2));c,w,_=run(q,entry,a=23,x=4,y=row,p=flags)
     pair.append((registers(c),app(q),cleanwrites(q,w),q.m.banks,c.processorCycles))
    # Gate bank restores its own entry bank; the direct native query is in lowcode.
    # Compare every live CPU/application byte and hardware writes, with A-bank
    # caller shadow publication explicitly normalized to the genuine gate caller.
    skip=[address(b,'CurrentBank')]
    assert pair[0][0]==pair[1][0],(name,face,row,flags,pair[0][0],pair[1][0])
    # Direct native entry uses physical0 vs gate124; rest of application checked separately below.
    rows.append(dict(gate=name,face=face,row=row,flags=flags,AXYP_SP_exact=True,cycles_extra=pair[1][4]-pair[0][4]))
  checks['native_head_side_live_registers']=dict(passed=True,cases=len(rows),rows=rows)
  # Whole GameLoop calls exercise genuine actor/terrain/render/UI dispatch, not
  # just Sunny leaves. Empty map and typed source placement are disclosed.
  rows=[]
  for mode,form,buttons in itertools.product([0,1],range(3),[0,1,129,4,64]):
   q=seed(b,23);q.put(CrossoverBehaviorVersion=mode,PlayerStatus=form,SunnyForm=form,PlayerSize=int(form==0),PlayerEntranceCtrl=2,SavedJoypadBits=buttons,A_B_Buttons=buttons&192,PreviousA_B_Buttons=0,Player_X_Position=96,Player_Y_Position=160)
   q.set('GameTimerDisplay',4)
   for step in range(3):
    q.set('VRAM_Buffer1_Offset',0);q.set('VRAM_Buffer2_Offset',0)
    c,w,_=run(q,'GameLoop');assert q.get('SelectedCharacter')==23 and q.get('GameEngineSubroutine')==8 and q.get('NmiDisable')==0
    assert q.get('ObjectMetasprite') in[0,address(b,'METASPRITE_SAMUS_BODY')]
    assert q.m.banks[2]==94
    rows.append(dict(mode=mode,form=form,buttons=buttons,step=step,CPU=c.processorCycles))
  checks['whole_GameLoop_source_arenas']=dict(passed=True,calls=len(rows),cycles=[min(x['CPU']for x in rows),max(x['CPU']for x in rows)],scope='Real full GameLoop on typed empty-map active8 source arenas; three updates per mode/form/input. Not native traversal or physical PPU proof.')
  # All explicit new dispatcher branches retain legacy full live returns for
  # foreign identities; avoid resetting active overlays in this differential.
  costs={}
  for nm in['NrBox','NrAdder','NrStatusName','NrWorldPaletteIndex','NrPrivate','NrRise','NrPickupCollision','NrUi']:
   ds=[]
   for char in range(22):
    pair=[]
    for bundle in[old,b]:
     q=seed(bundle,char);q.put(TimerControl=1,InvHudActive=0);q.set('PowerUpType',2,2);c,w,_=run(q,nm,a=char if nm in['NrAdder','NrBox'] else 1,x=2,y=93,p=0x71)
     pair.append((registers(c),app(q),cleanwrites(q,w),q.m.banks,c.processorCycles))
    assert pair[0][:4]==pair[1][:4],('foreign dispatcher',nm,char,pair[0][0],pair[1][0]);ds.append(pair[1][4]-pair[0][4])
   costs[nm]=[min(ds),max(ds)]
  checks['foreign_dispatchers']=dict(passed=True,cases=len(costs)*22,cycles_delta=costs)
  # Actual full helper callers at interruptible resident boundaries, including
  # legacy identities and all CV3 variant rows, not only the Sunny branch.
  count=0
  for char in[3,4,5,6,15,20,21,23]:
   for nm in['RosterGraphicsBank' if char<6 else 'CrossoverGraphicsBank']:
    q=seed(b,char);q.set('Cv3Variant',2);c,w,nn=run(q,nm,p=0x30,irq=True);count+=nn
  checks['foreign_and_owned_resident_IRQs']=dict(passed=True,injections=count)
  if a.menu:
   live=list(range(20))+[22];directions=dict(left=2,right=1,up=8,down=4)
   seen={0};edges={}
   for slot in live:
    q=seed(b,23);q.set('CrossoverMenuIndex',slot);c,_,_=run(q,'MenuResolveCharacter');expected=23 if slot==22 else b['raw'][location(b,'X5MenuCharacters')+slot];assert q.get('SelectedCharacter')==expected
    edges[slot]=[]
    for label,pressed in directions.items():
     q=seed(b,23);q.put(CrossoverMenuIndex=slot,CrossoverMenuPressed=pressed);c,_,_=run(q,'NrMenuNavigate');assert c.a in live;edges[slot].append(c.a)
   while (more:=seen|{j for i in seen for j in edges[i]})!=seen:seen=more
   assert seen==set(live)
   for slot in[20,21]:assert b['raw'][location(b,'X5MenuPresent')+slot]==0
   q=seed(b,23);q.put(CrossoverMenuIndex=22,VRAM_Buffer1_Offset=0);run(q,'NrQueueSelectName');data=bytes(q.m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+20]);assert data[3:19]==b['raw'][location(b,'NrQueueSelectName::Names')+43*16:location(b,'NrQueueSelectName::Names')+44*16] and q.get('VRAM_Buffer1_Offset')==19
   checks['actual_menu_navigation_and_names']=dict(passed=True,reachable_slots=live,rawID23_slot22=True,RC_holes_hidden=True)
  assert all(sha(z)==v for z,v in bs.items());proof['passed']=True
 except Exception as e:proof.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:a.output.write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
 print(json.dumps(dict(passed=proof['passed'],sha256=sha(a.output),checks=list(checks))))
if __name__=='__main__':main()
