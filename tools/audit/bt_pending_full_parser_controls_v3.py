"""Pending barrier then explicit ready-block projection; real BT cold parser."""
from pathlib import Path
import collections,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import battletoads_joint_cold_controls_v1 as B
from prepare_ff_current_component_v2 import qualified
H=B.H;J=R/'build/bt-native-world-source-v2/joint';O=R/'build/bt-pending-full-parser-controls-v3'
B.RAM+=['BtNativeWorldPalette'];B.ROM+=['CfRetire','QueueMegaManFacePalette'];H.O=J

def main():
 O.mkdir(exist_ok=False);q=dict(passed=False,native=False,CF_BT_pending=True,no_cache_cookie_Ready_preload=True,cohorts=[])
 try:
  b=qualified(J/'candidate.nes');cookie=(J/'bt/cookie.bin').read_bytes()
  for player in range(2):
   for variant in range(2):
    m=B.C.fresh(b,0);H.put(m,CurrentPlayer=player,CrossoverMenuIndex=23,FmGroups=variant<<5,SelectedCharacter=0,CrossoverMenuState=2)
    dirty_before=bytes(m.ram[3])
    cold=[B.invoke(m,n)for n in['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']]
    assert H.get(m,'SelectedCharacter')==0 and m.ppu_reads==0 and bytes(m.ram[3])==dirty_before and m.ram[3][0x1fe0:0x1ff0]!=cookie
    pending=B.invoke(m,'FmPending');assert pending['AXYP_SP'][3]&1
    H.put(m,CrossoverMenuButtons=0,SavedJoypad1Bits=16,SavedJoypad2Bits=0);blocked=B.invoke(m,'CrossoverMenuInput')
    assert H.get(m,'CrossoverMenuState')==2 and H.get(m,'OperMode')==0 and m.ppu_reads==0
    # Identical explicit frontend projection scope to frozen CF parser proof:
    # enter the real ready continuation after independently proving it blocked.
    # Never stage guest RAM, cookie, readiness, support or physical state.
    H.put(m,SelectedCharacter=33)
    allow=B.invoke(m,'CrossoverMenuInput::FmStartReady',x=23,a=0,p=0x30)
    assert H.get(m,'FmGroups')==variant<<5 and H.get(m,'CrossoverMenuState')==0
    for n in['IcGlobalInit','QwBoot','CmHostFresh']:assert allow['counts'].get(n)==1,(n,allow['counts'])
    assert allow['counts'].get('BtConstruct',0)==0
    a,x,y,p=allow['AXYP_SP'][:4];cont=B.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=a,x=x,y=y,p=p)
    assert H.get(m,'OperMode')==1 and H.get(m,'OperMode_Task')==0
    B.invoke(m,'PauseRoutine',a=0);setup=[];frames=[];row=dict(player=player,variant=variant,cold_pending_menu=cold,pending=pending,blocked_Start=blocked,explicit_frontend_ready_projection=allow,native_continue=cont,parser=setup,frames=frames);q['cohorts'].append(row)
    loaded=False;first_palette_query=None;loaded_at=None
    for age in range(600):
     if H.get(m,'OperMode_Task')==3 and H.get(m,'GameEngineSubroutine')==8:break
     H.put(m,SavedJoypad1Bits=0,SavedJoypadBits=0,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
     z=B.invoke(m,'GameLoop');normal=B.C.A.consume(m)
     if z['counts'].get('BtLoad') and m.ram[3][0x1fe0:0x1ff0]==cookie:loaded=True;loaded_at=age if loaded_at is None else loaded_at
     if z['counts'].get('BtNativeWorldPalette'):
      assert loaded and m.ram[3][0x1fe0:0x1ff0]==cookie,('native world32 before full load',age,z['counts'])
      first_palette_query=age if first_palette_query is None else first_palette_query
     setup.append(dict(age=age,task=H.get(m,'OperMode_Task'),screen=H.get(m,'ScreenRoutineTask'),engine=H.get(m,'GameEngineSubroutine'),Main=z,NMI=normal))
    else:raise AssertionError(('full native area parser bound',player,variant,setup[-3:]))
    totals=collections.Counter()
    for e in setup:totals.update(e['Main']['counts'])
    assert loaded and loaded_at is not None and totals['BtConstruct']==1 and totals['JnResetDispatch']==1,(player,variant,totals)
    assert m.ppu_reads==16400 and B.T.get(m,'BtHostReady')==1 and B.T.get(m,'BtVariant')==variant<<5
    assert any(m[B.address(b,'Block_Buffer_1'):B.address(b,'Block_Buffer_1')+416])
    row.update(verified_load_parser_tick=loaded_at,first_world32_query_tick=first_palette_query,parser_counts=dict(totals))
    for age in range(32):
     keys=1|(128 if 4<=age<12 else 0)|(64 if 16<=age<24 else 0)
     H.put(m,SavedJoypad1Bits=keys if player==0 else 0,SavedJoypadBits=keys,SavedJoypad2Bits=keys if player==1 else 0,A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,Up_Down_Buttons=0,NmiDisable=255)
     before=B.T.get(m,'BtSrc_FrameCounter');z=B.invoke(m,'GameLoop');actual_native_input=H.get(m,'SavedJoypadBits');assert actual_native_input==keys;normal=B.C.A.consume(m)
     for n in['BtMovement','BtCoreStep','BtPhysicsStep','BtSrc_update_frame_counters','PlayerBGCollision']:assert z['counts'].get(n)==1,(player,variant,age,n,z['counts'])
     assert z['source_clock']==(before+1)&255 and B.T.get(m,'BtSrc_FrameCounter')==z['source_clock']
     assert not H.get(m,'MmDeathFlag') and z['HP']>0 and not z['counts'].get('BtConstruct')
     frames.append(dict(age=age,input=keys,actual_native_input=actual_native_input,Main=z,NMI=normal))
    assert max(e['Main']['X']for e in frames)>min(e['Main']['X']for e in frames)
    print('real BT parser+Main PASS',player,variant,flush=True)
  q.update(passed=True,actual_native_parser_cohorts=4,actual_postparser_Main=128,real_pending_Start_blocks=4,source_only_future_frontend_projection=True,scope='Genuine pending menu/Start barrier observed, then onlySelected33 projected into real native ready continuation. Actual Fresh/native parser/blankload/Ensure/entrance/Main/NMI without guest preload. Not natural-ready menu admission or native emulator evidence.')
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['retained_v2_negative']='P2 is native alternating controller2. V2 supplied held keys only toSavedJoypad1Bits, and genuine native input selection correctly replacedSavedJoypadBits with controller2 zero. V3 supplies the chosen physical player input and requires actual native sampled bits to equal it before NMI.'
 q['retained_v1_negative']='The reused FF native-scene factory intentionally dirties all guest banks with non-source poison. V1 incorrectly demanded zeroRAM3. V2 requires that exact dirty image remain unchanged throughout pending menu, and forbids a valid BT cookie/preload.'
 files=[R/'tools/audit/bt_pending_full_parser_controls_v2.py',R/'build/bt-pending-full-parser-controls-v2/controls.json',Path(B.C.A.__file__),R/'tools/audit/bt_pending_full_parser_controls_v1.py',R/'build/bt-pending-full-parser-controls-v1/controls.json',Path(__file__),Path(B.__file__),Path(B.C.__file__),Path(B.T.__file__),Path(H.__file__),J/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',J/'bt/cache.bin',J/'bt/cookie.bin',R/'tools/audit/cf_preload_name_parser_controls_v1.py',R/'build/cf-preload-name-parser-controls-v1/controls.json']
 q['bindings']={str(p.resolve()):B.sha(p)for p in files};(O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['cohorts','bindings']}),flush=True);assert q['passed'],q.get('error')
if __name__=='__main__':main()
