"""Diagnose third-pipe clearance using real source/native code on fixed terrain."""
import json
import prepare_shinobi_draw_reservation_1101_v26 as P
import check_hogan_current_bounded_v1 as M
from check_tmnt_render_oa import address
from link_pit_rygar_sophia_audit_cpu import scoped_load

O=P.R/'build/shinobi-pipe-clearance-1101-v27'


def main():
 O.mkdir(exist_ok=True);b=scoped_load(P.O/'candidate.nes')
 b['segs']['shinobi_rom']={'start':str(0xa800),'ooffs':str(16+65*8192+0x800)}
 for n,a in P.S.labels(P.R/'build/shinobi-scene-1101-v7/resident.lbl').items():
  if n.startswith('Sh')and 0xa800<=a<0xae00:b['syms'][n]={'val':str(a),'seg':'shinobi_rom'}
 seed=M.fresh(b)
 M.put(seed,SelectedCharacter=36,OperMode=1,OperMode_Task=3,FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=160,Player_X_Position=680&255,Player_PageLoc=680>>8,Player_Y_Position=176,Player_Y_HighPos=1,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=2,ScreenRight_X_Pos=255,ScreenRight_PageLoc=2,PlayerFacingDir=1,AreaType=1)
 M.invoke(seed,'ShScene')
 M.put(seed,GameEngineSubroutine=8,GamePauseStatus=0,DisableScreenFlag=0,Mirror_PPUMASK=30,Player_State=0)
 for buffer,page in [('Block_Buffer_1',2),('Block_Buffer_2',3)]:
  at=address(b,buffer)
  for row in range(13):
   for col in range(16):
    world=page*256+col*16
    seed[at+row*16+col]=0x54 if row>=11 else (0x10+(world//16&1)if row==7 else 0x14+(world//16&1))if 736<=world<768 and row>=7 else 0
 cases=[]
 for mode in ['source-only','source-plus-body','PlayerCtrlRoutine']:
  for takeoff in range(684,722,2):
   m=M.fork(seed);jumped=False;apex=176;positions=[];sizes=[];fault=None
   for epoch in range(150):
    x=M.get(m,'Player_X_Position')+256*M.get(m,'Player_PageLoc')
    if not jumped and x>=takeoff:jumped=True;pressed=0
    keys=1|(128 if jumped and pressed<35 else 0)
    if jumped:pressed+=1
    M.put(m,FrameCounter=epoch,SavedJoypadBits=keys,SavedJoypad1Bits=keys,A_B_Buttons=keys&192,Left_Right_Buttons=1,Up_Down_Buttons=0)
    try:
     M.invoke(m,'PlayerCtrlRoutine'if mode=='PlayerCtrlRoutine'else'HuMovement')
     if mode=='source-plus-body':M.invoke(m,'HuBody')
     sizes.append(M.get(m,'PlayerSize'))
    except Exception as exc:fault=repr(exc);break
    x=M.get(m,'Player_X_Position')+256*M.get(m,'Player_PageLoc');y=M.get(m,'Player_Y_Position');apex=min(apex,y)
    if 708<=x<=776 and epoch%2==0:positions.append([epoch,x,y,M.get(m,'Player_State'),M.get(m,'PlayerSize')])
   cases.append(dict(mode=mode,takeoff=takeoff,x=x,y=y,apex=apex,size_values=sorted(set(sizes)),crossed=x>=780,fault=fault,near_pipe=positions))
 by={(c['mode'],c['takeoff']):c for c in cases}
 checks=dict(no_faults=not any(c['fault']for c in cases),original_66px_jump=all(c['apex']==110 for c in cases if c['takeoff']<=716),both_native_failures_reproduced=not by['PlayerCtrlRoutine',688]['crossed']and not by['PlayerCtrlRoutine',704]['crossed'],native_routine_crosses_692=by['PlayerCtrlRoutine',692]['crossed'],body_callback_does_not_prevent_crossing=by['source-plus-body',692]['crossed'],explicit_body_callback_sets_32px=all(c['size_values']==[0]for c in cases if c['mode']=='source-plus-body'),native_routine_final_size_observed=all(c['size_values']==[1]for c in cases if c['mode']=='PlayerCtrlRoutine'))
 q=dict(passed=all(checks.values()),checks=checks,ROM_sha256=P.S.sha(P.O/'candidate.nes'),cases=len(cases),crossings=[{k:c[k]for k in ['mode','takeoff','x','apex']}for c in cases if c['crossed']],rows=cases,scope='Explicit fixed block-buffer geometry: ground surface208, third pipe left736/right768/top144, initial player680/176, camera512. Genuine authenticated cold scene, actual HuMovement, optional HuBody, and complete PlayerCtrlRoutine instructions. No parser/Main/ISR/native-controller or assisted-crossing claim.')
 (O/'clearance-CPU.json').write_text(json.dumps(q,indent=2)+'\n')
 print(json.dumps({k:v for k,v in q.items()if k!='rows'}));assert q['passed']


if __name__=='__main__':main()
