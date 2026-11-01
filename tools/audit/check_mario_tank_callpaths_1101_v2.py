"""Run exact proposed hook operands through native parser/GameLoop call paths."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_mario_tank_host_1101_v2 import O
from audit_mario_tank_callmap_1101_v2 import prepare
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
import check_hogan_current_bounded_v1 as M
sha=lambda b:hashlib.sha256(b).hexdigest()

def main():
 old,b,patches=prepare();code=(O/'host.bin').read_bytes()
 labels={q[2][1:]:int(q[1],16)for line in(O/'host.lbl').read_text().splitlines()if len(q:=line.split())==3}
 seen={v:n for n,v in labels.items()if n in ['MtHostMovement','MtHostContact','MtHostInjury','MtHostBeginPowerup','MtHostGrowthUpdate','MtTerrainHeadProbe','MtTerrainSideProbe','MtTerrainDestroyCell']}
 measured=[]
 def call(m,name,**values):
  M.put(m,**values)
  target=address(b,name);m[address(b,'SafecallA_SMC')+1]=0x55
  m[address(b,'FarcallJmpTarget_SMC')+1]=target&255;m[address(b,'FarcallJmpTarget_SMC')+2]=target>>8
  c=NesMPU(memory=m,pc=address(b,'FarCallCommon'));c.a=128|((location(b,name)-16)//8192);c.x=0;c.y=0;c.p=0x31;c.sp=224;c.stPushWord(0x5aff);low=c.sp;counts={};cuts=[]
  for _ in range(500000):
   if c.pc==0x5b00:break
   if c.pc in seen and m.rawtags[1]==2:
    n=seen[c.pc];counts[n]=counts.get(n,0)+1;cuts.append(dict(name=n,SP=c.sp))
   assert m[c.pc]!=0,(name,hex(c.pc),m.rawtags);c.step();low=min(low,c.sp)
  else:raise AssertionError((name,'bounded',hex(c.pc)))
  assert c.sp==224 and m.rawtags[2]==M.get(m,'CurrentBankC'),(name,c.sp,m.rawtags,M.get(m,'CurrentBankC'))
  result=dict(name=name,CPU=c.processorCycles,minimum_SP=low,owned_entry_counts=counts,owned_entry_SP=cuts)
  measured.append(result);return result
 m=M.fresh(b);m.ram[2][0x1600:0x1600+len(code)]=code
 # Begin through the genuine admitted Mario0 menu. The new Tank variant is
 # deliberately not admitted; its identity is set only after parser entry.
 M.put(m,CrossoverMenuIndex=0)
 for name in ['MenuResolveCharacter','QueueSelection']:call(m,name)
 M.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0,CrossoverMenuButtons=0)
 c=M.invoke(m,'CrossoverMenuInput');M.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=c['A'],x=c['X'],y=c['Y'],p=c['P']);M.invoke(m,'PauseRoutine',a=0)
 for setup in range(600):
  if M.get(m,'OperMode_Task')==3 and M.get(m,'GameEngineSubroutine')==8:break
  call(m,'GameLoop',SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
  M.consume(m)
 else:raise AssertionError('Actual native parser/entrance did not complete')
 assert any(m[address(b,'Block_Buffer_1'):address(b,'Block_Buffer_1')+416])
 native_C_map=m.rawtags[2];assert native_C_map==M.get(m,'CurrentBankC')==140
 # The installed code/complete RAM2 header constructor is absent on purpose.
 # Set the explicit new identity only in this in-memory source arena.
 M.put(m,MarioVariant=7,SelectedCharacter=0,PlayerStatus=2,PlayerSize=0,Player_State=0,Player_X_Position=96,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,Player_X_Speed=0,Player_Y_Speed=0,CrossoverMenuState=0)
 frames=[]
 for age in range(12):
  q=call(m,'GameLoop',SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
  assert q['owned_entry_counts'].get('MtHostMovement')==1,(q,M.get(m,'GameEngineSubroutine'),M.get(m,'TimerControl'),M.get(m,'OperMode'),M.get(m,'OperMode_Task'))
  assert M.get(m,'MarioVariant')==7 and M.get(m,'SelectedCharacter')==0 and M.get(m,'PlayerStatus')==2
  assert m.rawtags[2]==M.get(m,'CurrentBankC')==native_C_map
  M.consume(m);frames.append(q)
 # Genuine head and side probe callers now reach the actual worker. Put one
 # question cell into the native grid at its source-computed head coordinate.
 M.put(m,Player_State=1,Player_X_Position=96,Player_PageLoc=0,Player_Y_Position=83,Player_Y_Speed=255,Player_Y_MoveForce=0,Player_X_Speed=0,PlayerStatus=2,PlayerSize=0,BlockBounceTimer=0,VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0)
 M.invoke(m,'BlockBufferColli_Head',y=0)
 at=M.get(m,'R6')+256*M.get(m,'R7')+M.get(m,'R2');m[at]=0xc1
 q=call(m,'GameLoop',SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
 assert q['owned_entry_counts'].get('MtTerrainHeadProbe')and q['owned_entry_counts'].get('MtTerrainDestroyCell')and m[at]==0 and not M.get(m,'Enemy_Flag',5),q
 actual=[v for q in measured for v in q['owned_entry_SP']];minimum=min(q['minimum_SP']for q in measured)
 result=dict(passed=True,base_ROM_sha256=patches['base_ROM_sha256'],in_memory_patch_spans=len(patches['patches']),patched_ROM_written=False,real_menu_Mario0_start=True,parser_GameLoop_calls=setup,normal_NMI_calls=setup+len(frames),Tank_identity_fixture_only=True,Tank_GameLoop_frames=len(frames)+1,actual_A2_farcall_transport=True,native_C_map_retained=native_C_map,real_native_head_caller_observed=True,minimum_GameLoop_fixture_SP=minimum,minimum_owned_entry_SP=min(x['SP']for x in actual),observed_call_summary={n:sum(q['owned_entry_counts'].get(n,0)for q in measured)for n in seen.values()},
  measured_source_frames=frames+[q],code_bytes=len(code),RAM_fixture_bytes=12,Main_transport_granted=False,installed=False,native_emulator=False,
  scope='Exact10 compiled spans patched only in memory. Real native admitted Mario0 Start/parser, normal NMI, then explicit Tank7 preloaded RAM2 fixture through13GameLoops including a real upward question-cell collision. Real rawbank2 farcalls execute A2B600 with A2A880 context and restore the native A-window; C-window stays ROM12 throughout gameplay. This is a GameLoop stack/depth observation, not the actual outer Main/IRQ/cold-loader proof. No ISR seam/12-byte Main reserve claim follows from SP224 entry.',
  remaining=['Funded complete-header loader and caller C2 transport; same final image binding as current root.','Actual outer Main plus all reached NMI/IRQ mapper/stack seams, including failed/warm/cold admission.','Native menu/lives/world/boots pickup/masked flashing visuals and scene retirement.'],bindings={str(Path(__file__).relative_to(R)):sha(Path(__file__).read_bytes()),'host.bin':sha(code),'compiled-call-map.json':sha((O/'compiled-call-map.json').read_bytes())})
 (O/'native-callpaths-CPU.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k in ['passed','parser_GameLoop_calls','Tank_GameLoop_frames','minimum_GameLoop_fixture_SP','minimum_owned_entry_SP','observed_call_summary']}))

if __name__=='__main__':main()
