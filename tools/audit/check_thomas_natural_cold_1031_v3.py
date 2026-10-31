"""Genuine menu/Start/native parser/Main source cohort. No RAM cache preload."""
from pathlib import Path
import collections,hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_current_ready_cold_controls_v2 as C
from check_tmnt_render_oa import address,location
H=C.H;V=C.A.V
J=R/'build/thomas-natural-host-1031-v6';O=R/'build/thomas-natural-cold-controls-1031-v3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
RAM=['ThMovement','ThGraphics','ThDraw','ThEnsure','ThPostTerrain','ThomasHostCold','ThomasHostFrame','ThomasHostAfterTerrain','ThomasHostWeapons','ThomasHostDamage','ThomasHostPickup','ThomasC2AcceptedFrame','ThStatusName']
ROM=['ThLoad','ThMenuResolve','ThSceneInit','ThColdPrepare','ThColdPortrait','ThColors','ThFresh','ThScene','IcGlobalInit','SunnyGlobalInit','QwBoot','QwSceneInit','ArGenSceneInit','FwSceneInit','BwScene','PlayerBGCollision','PlayerCtrlRoutine','ThPostNativeHot','ThSharedDrawHot','ThMovementIngress','MovePlayerVertically','RyuSourceBodyAfterBGBridge']
def invoke(m,name,**kw):
 points={}
 for n in RAM+ROM:points[(address(m.bundle,n),3 if n in RAM else((location(m.bundle,n)-16)//8192)|128)]=n
 events=[];old=m.rawtags[:];c=H.start(m,name,**kw)
 def watch(mem,c,i):
  if c.pc>=32768:
   tag=mem.rawtags[(c.pc-32768)//8192]
   if(c.pc,tag)in points:events.append([i,points[(c.pc,tag)]])
 c,low=H.finish(m,c,watch);assert c.sp==kw.get('sp',224)and m.rawtags[1]==old[1]and m.rawtags[2]==H.get(m,'CurrentBankC')
 return dict(entry=name,CPU=c.processorCycles,minimumSP=low,regs=[c.a,c.x,c.y,c.p,c.sp],counts=dict(collections.Counter(n for _,n in events)),events=events,X=H.get(m,'Player_X_Position')+256*H.get(m,'Player_PageLoc'),Y=H.get(m,'Player_Y_Position'),Yhi=H.get(m,'Player_Y_HighPos'),state=H.get(m,'Player_State'),health=m.ram[2][0x4a6],pose=m.ram[2][address(m.bundle,'ThPoseCommand')&8191])
def main():
 assert not O.exists();O.mkdir(parents=True);q=dict(passed=False,native=False,no_RAM_cache_preload=True,cohorts=[])
 try:
  stage=json.loads((J/'source-stage.json').read_text())
  for p,h in stage['bindings'].items():assert sha(p)==h,p
  b=H.C.qualified(J/'candidate.nes')
  for player in[0,1]:
   m=C.fresh(b,0);H.put(m,CrossoverMenuIndex=10,FmAlts=64,SelectedCharacter=0,CurrentPlayer=player)
   cohort=dict(player=player,cold=[],setup=[],frames=[]);q['cohorts'].append(cohort)
   for name in['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:
    row=invoke(m,name);cohort['cold'].append(row);assert H.get(m,'SelectedCharacter')==10 and H.get(m,'FmAlts')&68==64
    assert m.ppu_reads==0 and not m.ram_writes,('cold must use immutable ROM only',name)
   assert cohort['cold'][-1]['counts'].get('ThColdPortrait')==1
   H.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0);start=invoke(m,'GameMenuRoutine');cohort['start']=start
   assert H.get(m,'OperMode')==1 and H.get(m,'OperMode_Task')==0 and H.get(m,'FmAlts')==64
   assert start['counts'].get('IcGlobalInit')==1 and start['counts'].get('QwBoot')==1
   invoke(m,'PauseRoutine',a=0)
   for age in range(1000):
    if H.get(m,'OperMode_Task')==3 and H.get(m,'GameEngineSubroutine')==8:break
    H.put(m,SavedJoypad1Bits=0,SavedJoypadBits=0,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
    row=invoke(m,'GameLoop');nmi=C.A.consume(m);cohort['setup'].append(dict(age=age,task=H.get(m,'OperMode_Task'),screen=H.get(m,'ScreenRoutineTask'),engine=H.get(m,'GameEngineSubroutine'),Main=row,NMI=nmi))
   else:raise AssertionError(('actual parser/entrance bound',cohort['setup'][-1]))
   assert m.ppu_reads==16400 and m.ram[2][0x1fe0]==167 and m.ram[3][0x1fe0]==167,('actual forcedblank loader missing',m.ppu_reads)
   assert any(m[address(b,'Block_Buffer_1'):address(b,'Block_Buffer_1')+416]),'Real native parser did not build terrain'
   for age in range(100):
    # Original Thomas: Up=jump, B=punch, A=kick. No engine/HP/terrain writes.
    keys=(1 if age<30 else 0)|(8 if 8<=age<10 else 0)|(64 if 40<=age<46 else 0)
    H.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,Up_Down_Buttons=keys&12,NmiDisable=255)
    row=invoke(m,'GameLoop');nmi=C.A.consume(m)
    cohort['frames'].append(dict(age=age,input=keys,Main=row,NMI=nmi,visible_OAM=sum(m[512+i]<240 for i in range(0,256,4))))
    for n in['ThMovement','ThomasHostFrame','ThomasC2AcceptedFrame','ThPostTerrain','ThDraw','PlayerBGCollision']:
     assert row['counts'].get(n)==1,('sole source/native Main worker',player,age,n,row)
    assert not H.get(m,'MmDeathFlag')and H.get(m,'GameEngineSubroutine')==8,('unexpected death/mode',player,age,row)
   ys=[f['Main']['Y']for f in cohort['frames']]
   assert min(ys)<176 and ys[-1]==176,('original jump/real landing',player,min(ys),ys[-1])
   assert max(f['Main']['X']for f in cohort['frames'])>40
   assert all(f['visible_OAM']>0 for f in cohort['frames'])
   assert any(f['Main']['counts'].get('ThomasHostWeapons')for f in cohort['frames']),'Actual source punch must reach weapon consumer'
   print('Thomas genuine cold/parser/100Main PASS',player,flush=True)
  q.update(passed=True,actual_Main_updates=200,actual_completed_normalNMIs=sum(len(c['setup'])+len(c['frames'])for c in q['cohorts']),limits=['CPU legal native initial-scene/controller-byte fixture; not a native replay/cadence qualification','No full campaign/water/vine/pipe/death/audio admission claim'])
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p):sha(p)for p in[Path(__file__),Path(C.__file__),Path(C.A.__file__),J/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',J/'kernel.bin',J/'state.bin']}
 dump(O/'controls.json',q);print(json.dumps({k:v for k,v in q.items()if k not in['bindings','cohorts','traceback']}));assert q['passed'],q.get('error')
if __name__=='__main__':main()
