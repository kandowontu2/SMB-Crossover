"""Exercise actual HuMovement on the private cartridge; no donor callbacks stubbed."""
import json
import prepare_shinobi_owning_graft_1101_v1 as S
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
R=S.R;BASE=R/'build/shinobi-route-1101-v8';O=R/'build/shinobi-active-1101-v9'


def main():
 O.mkdir(exist_ok=True);b=scoped_load(BASE/'candidate.nes')
 assert S.sha(BASE/'candidate.nes')=='12db8aa78ac0fb5de9591fdf34a82a1b0c13a94106cf3b430660c1091072deb7'
 b['segs']['shinobi_rom']={'start':str(0xa800),'ooffs':str(16+65*8192+0x800)}
 for n,a in S.labels(R/'build/shinobi-scene-1101-v7/resident.lbl').items():
  if n.startswith('Sh') and 0xa800<=a<0xae00:b['syms'][n]={'val':str(a),'seg':'shinobi_rom'}
 seed=M.fresh(b)
 M.put(seed,SelectedCharacter=36,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=160,Player_X_Position=120,Player_PageLoc=0,Player_Y_Position=192,Player_Y_HighPos=1,PlayerFacingDir=1,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0)
 for buffer in ['Block_Buffer_1','Block_Buffer_2']:
  at=address(b,buffer)
  for row in range(13):
   for x in range(16):seed[at+row*16+x]=0x54 if row>=12 else 0
 M.invoke(seed,'ShScene')
 M.put(seed,GameEngineSubroutine=8,GamePauseStatus=0,DisableScreenFlag=0,Mirror_PPUMASK=30)
 rows=[]
 for name,held,frames in [('idle',0,100),('right',1,80),('left',2,60),('jump',128,100),('running_jump',129,80),('crouch',4,60),('throw',64,80),('crouch_throw',68,80)]:
  m=M.fork(seed);cycles=[];ys=[];states=set();start=M.get(m,'Player_X_Position');error=None;shots=False
  for frame in range(frames):
   keys=held if frame<35 or name in ['right','left'] else 0
   if name=='running_jump':keys=1 if frame<8 else 129 if frame<35 else 1
   M.put(m,FrameCounter=frame,SavedJoypadBits=keys)
   try:z=M.invoke(m,'HuMovement')
   except Exception as exc:error=str(exc);break
   cycles.append(z['CPU']);ys.append(M.get(m,'Player_Y_Position'));states.add(m.ram[2][0x413])
   shots |= any(m.ram[2][0x414:0x418])
  rows.append(dict(case=name,updates=len(cycles),error=error,x_delta=M.get(m,'Player_X_Position')-start,
                   y=M.get(m,'Player_Y_Position'),rise=192-min(ys) if ys else None,states=sorted(states),
                   weapon_slot_active=shots,max_cycles=max(cycles) if cycles else None))
 byname={r['case']:r for r in rows}
 checks=dict(no_faults=all(r['error'] is None for r in rows),right_moves=byname['right']['x_delta']==80,
             left_moves=byname['left']['x_delta']==-60,jump_returns_to_floor=byname['jump']['y']==192,
             original_jump_height=byname['jump']['rise']==66,running_jump_moves=byname['running_jump']['x_delta']>8,
             crouch_state=5 in byname['crouch']['states'],standing_shot=byname['throw']['weapon_slot_active'],
             crouching_shot=byname['crouch_throw']['weapon_slot_active'])
 # Same-frame and paused calls must not advance source simulation twice.
 m=M.fork(seed);M.put(m,FrameCounter=1,SavedJoypadBits=1)
 M.invoke(m,'HuMovement');phase=m.ram[2][0x553];x=M.get(m,'Player_X_Position')
 M.invoke(m,'HuMovement')
 checks['duplicate_update_rejected']=m.ram[2][0x553]==phase and M.get(m,'Player_X_Position')==x
 M.put(m,FrameCounter=2,GamePauseStatus=1);M.invoke(m,'HuMovement')
 checks['pause_preserved']=m.ram[2][0x553]==phase and M.get(m,'Player_X_Position')==x
 q=dict(passed=all(checks.values()),checks=checks,ROM_sha256=S.sha(BASE/'candidate.nes'),rows=rows,
        scope='Actual cartridge HuMovement, flat native block buffers, no enemy fixture and no callback stubs. No Main/scroll/NMI or gameplay proof.')
 (O/'result.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
 assert q['passed'],checks


if __name__=='__main__':main()
