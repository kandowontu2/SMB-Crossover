"""Real source menu/Start/parser/Main, using controller bytes; no native run."""
from pathlib import Path
import collections,hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_current_ready_cold_controls_v2 as C
from check_tmnt_render_oa import address,location
H=C.H
J=R/'build/wwf-hogan-natural-source-v15/joint';O=R/'build/wwf-hogan-natural-controls-v9'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def invoke(m,name,**kw):
 b=m.bundle;hits=[];xwrites=[];last_x=H.get(m,'Player_X_Position');previous=None
 native=['IcGlobalInit','SunnyGlobalInit','QwBoot','QwSceneInit','ArGenSceneInit','FwSceneInit','MoveAllSpritesOffscreen','DrawAllMetasprites','ShellOrBlockDefeat']
 own=['WfScene','WfLoad','WfConstructCold','WfHostCold','WfMovement','WfHostFrame','WfGraphics','WfDrawBody','WfColdPortrait','WfP1LateDispatch','WfP1LateCore','WfEnv_WfCbRingClamp']
 points={}
 for n in native+own:
  pc=address(b,n)
  tag=(2 if pc>=0xc000 else 224)if n in own else((location(b,n)-16)//8192)|128
  points[pc,tag]=n
 def watch(mem,cpu,step):
  nonlocal last_x,previous
  current=H.get(mem,'Player_X_Position')
  if current!=last_x:xwrites.append([previous,last_x,current]);last_x=current
  previous=[cpu.pc,cpu.a,cpu.x,cpu.y,cpu.p,mem.rawtags[:]]
  if cpu.pc>=0x8000:
   raw=mem.rawtags[(cpu.pc-0x8000)//8192]
   if(cpu.pc,raw)in points:hits.append(points[cpu.pc,raw])
 c=H.start(m,name,**kw);c,low=H.finish(m,c,watch)
 assert c.sp==224
 return dict(entry=name,AXYP=[c.a,c.x,c.y,c.p,c.sp],CPU=c.processorCycles,minimum_SP=low,counts=dict(collections.Counter(hits)),hits=hits,X_writes=xwrites)

def main():
 assert not O.exists();O.mkdir();q=dict(passed=False,native=False,installed=False,source_controller_byte_fixture=True,cache_or_Ready_preload=False,steps=[],parser=[],Main=[])
 try:
  b=H.C.qualified(J/'candidate.nes');m=C.fresh(b,0)
  H.put(m,CrossoverMenuIndex=28,FmGroups=0,FmAlts=0)
  for name in ['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:
   z=invoke(m,name);q['steps'].append(z);assert H.get(m,'SelectedCharacter')==29
  assert m.ppu_reads==0 and H.get(m,'CurrentOAMOffset')>0,('cold ROM preview',q['steps'])
  q['selected_OAM']=list(m[512:512+H.get(m,'CurrentOAMOffset')])
  H.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0,CrossoverMenuButtons=0)
  start=invoke(m,'CrossoverMenuInput');q['steps'].append(start)
  assert H.get(m,'CrossoverMenuState')==0 and H.get(m,'FmGroups')&7==0
  q['steps'].append(invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['AXYP'][0],x=start['AXYP'][1],y=start['AXYP'][2],p=start['AXYP'][3]))
  q['steps'].append(invoke(m,'PauseRoutine',a=0))
  for age in range(600):
   if H.get(m,'OperMode_Task')==3 and H.get(m,'GameEngineSubroutine')==8:break
   H.put(m,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
   z=invoke(m,'GameLoop');C.A.consume(m)
   q['parser'].append(dict(age=age,mode=H.get(m,'OperMode'),task=H.get(m,'OperMode_Task'),screen=H.get(m,'ScreenRoutineTask'),engine=H.get(m,'GameEngineSubroutine'),**z))
  else:raise AssertionError(('real parser bound',q['parser'][-5:]))
  assert any(m[address(b,'Block_Buffer_1'):address(b,'Block_Buffer_1')+416])
  assert m.ram[2][address(b,'WfHostReady')-0xc000]==167
  assert m.ppu_reads==49200,('real24KiB once',m.ppu_reads)
  for age in range(180):
   keys=(1 if 70<=age<140 else 0)|(128 if 95<=age<113 else 0)|(64 if 145<=age<149 else 0)
   H.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,Up_Down_Buttons=keys&12,NmiDisable=255)
   z=invoke(m,'GameLoop')
   q['Main'].append(dict(age=age,keys=keys,X=H.get(m,'Player_X_Position')+256*H.get(m,'Player_PageLoc'),Y=H.get(m,'Player_Y_Position')+256*H.get(m,'Player_Y_HighPos'),state=H.get(m,'Player_State'),timer=H.get(m,'TimerControl'),source_action=m.ram[2][0x3c],source_HP=m.ram[2][0x79],source_phase=m.ram[2][0x71],OAM=H.get(m,'CurrentOAMOffset'),**z))
   if 0<age<70:assert q['Main'][-1]['X']==q['Main'][0]['X'],('Idle drift',age,q['Main'][-1])
   assert not H.get(m,'MmDeathFlag'),('natural source unexpected death',age,q['Main'][-1])
   if not H.get(m,'TimerControl'):
    assert z['counts'].get('WfMovement')==1 and z['counts'].get('WfHostFrame')==1,('source movement once',age,z)
    assert z['counts'].get('WfDrawBody')==1,('source Draw once',age,z)
   C.A.consume(m)
  assert max(r['X']for r in q['Main'])-min(r['X']for r in q['Main'])>10
  assert min(r['Y']for r in q['Main'][95:140])<q['Main'][90]['Y']-30
  assert any(r['source_action']==15 for r in q['Main'][145:])
  q.update(passed=True,candidate=sha(J/'candidate.nes'))
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  q['bindings']={str(p.resolve()):sha(p)for p in [Path(__file__),Path(C.__file__),J/'candidate.nes',J/'candidate.dbg',J.parent/'source-stage.json']if p.exists()}
  (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q.get(k)for k in ['passed','candidate','error']}))
if __name__=='__main__':main()
