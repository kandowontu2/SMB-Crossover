"""Pending gate + explicit real ready-block consumer -> full native CF parser.

The CF pending gate is NOT cleared. An explicitly labelled future-ready-block
entry exercises the actual native remainder; no CF RAM/Ready is preloaded.
"""
from pathlib import Path
import collections,hashlib,json,re,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_current_ready_cold_controls_v2 as C
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
H=C.H;J=R/'build/cf-preload-name-source-v1/joint';O=R/'build/cf-preload-name-parser-controls-v1'
K=R/'build/contra-force-palette-names-kernel-v3';H.O=J
L={n:int(v,16)for v,n in re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',(K/'runtime.lbl').read_text())}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
CF=['CfHostConstruct','CfHostSceneEnsure','CfHostEnsure','CfHostReset','CfHostAreaReset','CfHostMovement','CfHostGraphics','CfHostDraw','CfHostShots','CfA2Router']
NATIVE=['IcGlobalInit','SunnyGlobalInit','QwBoot','CmHostFresh','JnResetDispatch','BwScene','CfSceneRetireForeign','CfRetire','CfLoadIfCold','BwCfSceneLoad','CfLoaderProposal','CfOrBtCheck','S2InitScreenPrepare','QwSceneInit','ArGenSceneInit','FwSceneInit','MoveAllSpritesOffscreen','PlayerBGCollision','ScrollHandler']
def invoke(m,name,**kw):
 points={}
 for n in NATIVE:points[(address(m.bundle,n),(location(m.bundle,n)-16)//8192|128)]=n
 for n in CF:
  pc=L[n];points[(pc,2 if pc>=0xc000 or n.startswith('CfA2')else 3)]=n
 # Native BW-only constructor setup must never execute for selected31.
 points[(address(m.bundle,'BwSceneDone')-15,(location(m.bundle,'BwSceneDone')-16)//8192|128)]='native_BW_ctor_setup'
 guardRTS=address(m.bundle,'CfExternalCookie')-1;auth=False;rw=len(m.ram_writes);events=[];a2=0
 def watch(mem,c,step):
  nonlocal auth,rw,a2
  for bank,at,v in mem.ram_writes[rw:]:
   if bank==2 and at==0x1fe0 and v==0:auth=False
  rw=len(mem.ram_writes)
  raw=mem.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
  if c.pc==guardRTS and raw==0xc5:
   if c.p&1:auth=True
   events.append([step,'ROM_guard_C1'if c.p&1 else'ROM_guard_C0'])
  if raw==2:
   assert auth,('FIRST A2 opcode preceded by genuine ROM auth',name,hex(c.pc))
   a2+=1
  if(c.pc,raw)in points:events.append([step,points[(c.pc,raw)]])
 before=m.ppu_reads;origin=m.rawtags[:];c=H.start(m,name,**kw);c,low=H.finish(m,c,watch)
 assert c.sp==224 and m.rawtags[1]==origin[1]and H.get(m,'CurrentBankC')==m.rawtags[2]
 return dict(entry=name,CPU=c.processorCycles,minimum_SP=low,AXYP=[c.a,c.x,c.y,c.p],counts=dict(collections.Counter(n for _,n in events)),events=events,A2_instructions=a2,PPU_reads=m.ppu_reads-before,X=H.get(m,'Player_X_Position')+256*H.get(m,'Player_PageLoc'),Y=H.get(m,'Player_Y_Position'))
def main():
 O.mkdir(exist_ok=False);q=dict(passed=False,native=False,CF_still_pending=True,no_CF_RAM_preload=True,cohorts=[])
 try:
  b=qualified(J/'candidate.nes')
  for var in range(4):
   m=C.fresh(b,0);H.put(m,CrossoverMenuIndex=30,FmGroups=var<<3,FmAlts=0,CrossoverMenuState=2,SelectedCharacter=0)
   start=[]
   for n in['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:start.append(invoke(m,n))
   assert H.get(m,'SelectedCharacter')==0 and H.get(m,'FmGroups')&24==var<<3
   pending=invoke(m,'FmPending');assert pending['AXYP'][3]&1
   H.put(m,CrossoverMenuButtons=0,SavedJoypad1Bits=16,SavedJoypad2Bits=0);blocked=invoke(m,'CrossoverMenuInput')
   assert H.get(m,'CrossoverMenuState')==2 and H.get(m,'OperMode')==0 and m.ppu_reads==0
   # An explicit real native block is the finite future-admission fixture.
   # It bypasses only the known pending decision, never a constructor/loader.
   H.put(m,SelectedCharacter=31) # Explicit future frontend identity projection only.
   allow=invoke(m,'CrossoverMenuInput::FmStartReady',x=30,a=0,p=0x30)
   assert H.get(m,'FmGroups')==var<<3 and H.get(m,'CrossoverMenuState')==0
   assert allow['counts'].get('IcGlobalInit')==1 and allow['counts'].get('QwBoot')==1
   assert allow['counts'].get('CmHostFresh')==1 and allow['A2_instructions']==0
   cont=invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=allow['AXYP'][0],x=allow['AXYP'][1],y=allow['AXYP'][2],p=allow['AXYP'][3])
   assert H.get(m,'OperMode')==1 and H.get(m,'OperMode_Task')==0
   invoke(m,'PauseRoutine',a=0)
   setup=[];q['cohorts'].append(dict(variant=var,cold_menu=start,pending=pending,blocked_Start=blocked,explicit_future_ready_block=allow,native_continue=cont,parser=setup,frames=[]))
   for age in range(600):
    if H.get(m,'OperMode_Task')==3 and H.get(m,'GameEngineSubroutine')==8:break
    H.put(m,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
    z=invoke(m,'GameLoop');normal=C.A.consume(m);setup.append(dict(age=age,task=H.get(m,'OperMode_Task'),screen=H.get(m,'ScreenRoutineTask'),engine=H.get(m,'GameEngineSubroutine'),Main=z,NMI=normal))
   else:raise AssertionError(('full native parser bound',var,setup[-3:]))
   totals=collections.Counter()
   for row in setup:totals.update(row['Main']['counts'])
   assert totals['CfLoaderProposal']==1 and totals['CfHostConstruct']==1 and totals['CfHostSceneEnsure']==1,(var,totals)
   assert totals['JnResetDispatch']==1 and totals['native_BW_ctor_setup']==0,(var,totals)
   assert m.ppu_reads==24*1025*2 and m.ram[2][0x2e1]==1
   assert any(m[address(b,'Block_Buffer_1'):address(b,'Block_Buffer_1')+416])
   for age in range(32):
    keys=1|(128 if 4<=age<12 else 0)|(64 if 16<=age<24 else 0)
    H.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,Up_Down_Buttons=0,NmiDisable=255)
    z=invoke(m,'GameLoop');normal=C.A.consume(m)
    assert z['counts'].get('CfHostMovement')==1 and z['counts'].get('CfHostDraw')==1,('actual source Main consumers',var,age,z['counts'])
    assert z['counts'].get('CfHostConstruct',0)==0 and not H.get(m,'MmDeathFlag')
    q['cohorts'][-1]['frames'].append(dict(age=age,input=keys,Main=z,NMI=normal))
   frames=q['cohorts'][-1]['frames'];assert max(r['Main']['X']for r in frames)>min(r['Main']['X']for r in frames)
  q.update(passed=True,actual_parser_classes=4,actual_Main_updates=128,real_pending_Start_rejections=4,explicit_future_ready_entry=True,scope='Actual native ready block+ChkContinue/full parser/Main; pending barrier observed first; only frontend identity31 is then explicitly projected and source gate never changed. No natural ready admission/native/colors/name claim.')
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),R/'tools/audit/cf_cold_warm_parser_controls_v2.py',R/'build/cf-cold-warm-parser-controls-v2/controls.json',R/'tools/audit/cf_cold_warm_parser_controls_v1.py',R/'build/cf-cold-warm-parser-controls-v1/controls.json',Path(C.__file__),J/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',J/'cf-stream.bin',J/'cf-cookie.bin',K/'runtime.lbl',R/'build/contra-force-palette-names-qualified-v1/handoff.json']}
 (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['cohorts','bindings']}));assert q['passed']
if __name__=='__main__':main()
