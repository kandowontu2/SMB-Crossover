"""Actual controller-byte title/menu -> native parser -> Bowser Main services."""
from pathlib import Path
import collections,hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_current_ready_cold_controls_v2 as C
from arthur_cache_host_controls_v1 import OverlayMemory
from check_tmnt_render_oa import load,address,location
H=C.H;V=C.A.V
J=R/'build/bowser-functional-host-v7/joint';O=R/'build/bowser-functional-cold-controls-v4';H.O=J
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
RAM=['BwConstruct','BwMovement','BwGraphics','BwWeaponTail','BwCoreFinish','BwSpawnFire','BwAdvanceFire','BwDrawShots','BwInjury','BwPickup','BwUi']
ROM=['BwScene','BwColdPrepare','BwColdDraw','BwColors','BwStatusName','BwMenuResolve','BwLoad','BwCheck','BwBtResolve','BwStartFlags','IcGlobalInit','SunnyGlobalInit','QwBoot','MoveAllSpritesOffscreen','S2InitScreenPrepare','QwSceneInit','ArGenSceneInit','FwSceneInit','PlayerBGCollision','ScrollHandler','DrawMetasprite','PlayerCtrlRoutine','HandleEnemyFBallCol']
def invoke(m,name,**kw):
 points={}
 for n in RAM+ROM:
  points[(address(m.bundle,n),3 if n in RAM else ((location(m.bundle,n)-16)//8192)|128)]=n
 ev=[];old=m.rawtags[:];c=H.start(m,name,**kw)
 def watch(mem,c,i):
  if c.pc>=32768:
   tag=mem.rawtags[(c.pc-32768)//8192]
   if (c.pc,tag)in points:ev.append([i,points[(c.pc,tag)]])
 c,lo=H.finish(m,c,watch);assert c.sp==kw.get('sp',224);assert m.rawtags[1]==old[1];assert m.rawtags[2]==H.get(m,'CurrentBankC')
 return dict(entry=name,CPU=c.processorCycles,minimum_SP=lo,AXYP_SP=[c.a,c.x,c.y,c.p,c.sp],counts=dict(collections.Counter(n for _,n in ev)),events=ev,X=H.get(m,'Player_X_Position')+256*H.get(m,'Player_PageLoc'),Y=H.get(m,'Player_Y_Position'),state=H.get(m,'Player_State'),HP=m.ram[3][0x1e29],source_pose=m.ram[3][0x1e16])
def main():
 O.mkdir(exist_ok=False);q=dict(passed=False,source_CPU=True,native=False,cohorts=[])
 try:
  b=load(J/'candidate.nes')
  for form in [0,8]:
   m=C.fresh(b,0);H.put(m,CrossoverMenuIndex=26,FmAlts=form,SelectedCharacter=0)
   rows=[]
   for name in ['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:
    row=invoke(m,name);rows.append(row);assert H.get(m,'SelectedCharacter')==27
    assert m.ppu_reads==0 and not m.ram_writes,('Cold must use only ROM',name)
   assert rows[-1]['counts'].get('BwColdDraw')==1
   # Real native Start consumes the menu return, including newgame exactlyonce.
   H.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0)
   start=invoke(m,'GameMenuRoutine');rows.append(start)
   assert H.get(m,'OperMode')==1 and H.get(m,'OperMode_Task')==0,start
   assert H.get(m,'FmAlts')==form and start['counts'].get('IcGlobalInit')==1 and start['counts'].get('QwBoot')==1
   invoke(m,'PauseRoutine',a=0)
   setup=[]
   for age in range(1000):
    if H.get(m,'OperMode_Task')==3 and H.get(m,'GameEngineSubroutine')==8:break
    H.put(m,SavedJoypad1Bits=0,SavedJoypadBits=0,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
    r=invoke(m,'GameLoop');normal=C.A.consume(m)
    setup.append(dict(age=age,task=H.get(m,'OperMode_Task'),screen=H.get(m,'ScreenRoutineTask'),engine=H.get(m,'GameEngineSubroutine'),Main=r,NMI=normal))
   else:raise AssertionError(('real native parser bound',form,setup[-1]))
   assert m.ppu_reads==16400 and m.ram[3][0x1e26]==0xb7
   assert m.ram[3][0x1e29]==(5 if form else 34)
   assert any(m[address(b,'Block_Buffer_1'):address(b,'Block_Buffer_1')+416])
   frames=[]
   for age in range(120):
    keys=(1 if age<80 else 2)|(128 if 8<=age<16 else 0)|(64 if age in[2,66] else 0)
    H.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,Up_Down_Buttons=0,NmiDisable=255)
    r=invoke(m,'GameLoop');normal=C.A.consume(m)
    for n in ['BwMovement','BwWeaponTail','PlayerBGCollision']:
     assert r['counts'].get(n)==1,('sole real source/native update',form,age,n,r)
    assert r['HP']>0 and not H.get(m,'MmDeathFlag'),('actual no death in first controlled area',form,age,r)
    frames.append(dict(age=age,input=keys,Main=r,NMI=normal,shots=[m.ram[3][0x1e80],m.ram[3][0x1e8a]]))
   assert max(r['Main']['X']for r in frames)>120
   assert min(r['Main']['Y']for r in frames)<176
   assert any(any(r['shots'])for r in frames),('actual controller breath emits flames',form)
   q['cohorts'].append(dict(form=form,cold=rows,setup=setup,frames=frames))
  q['passed']=True
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(C.__file__),J/'candidate.nes',J/'candidate.dbg',J/'bowser.bin']}
 (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=q['passed'],error=q.get('error'),traceback=q.get('traceback'))));assert q['passed']
if __name__=='__main__':main()
