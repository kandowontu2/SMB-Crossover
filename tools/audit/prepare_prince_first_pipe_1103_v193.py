"""One source-geometry-derived first-pipe retiming, retaining189 negative.

Only the running-A request upper gap changes120->96. Passive rectangle and
HP-write witnesses capture the state before the original fatal reaction.
No ROM, original physics, collision policy, ability or state writes.
"""
from pathlib import Path
import json,re,sys
import prepare_prince_first_pipe_1103_v189 as B
from observe_chip_committed_write import lua

R=B.R
O=R/'build/prince-first-pipe-1103-v193'
GLOBALS=R/'build/roster-combined-1101-v3/candidate.lbl'
NEGATIVE=R/'build/prince-first-pipe-1103-v189/native/capture/prince-diagnostic.json'
original=B.ORIGINAL_PREPARE

WITNESS=r'''
local function wholeBoxes(tag)
 local q=state();q.tag=tag;q.frame=frame;q.Main=admitted;q.enemy=goomba();q.PC=emu.getState()['cpu.pc']
 local camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')
 q.camera=camera
 local at=L.BoundingBox_UL_XPos
 q.native_player_screen={ram(at),ram(at+1),ram(at+2),ram(at+3)}
 q.native_player_world={ram(at)+camera,ram(at+1),ram(at+2)+camera,ram(at+3)}
 q.native_state=r('Player_State');q.native_DY=r('Player_Y_Speed')
 q.behavior=r('CrossoverBehaviorVersion');q.native_no_stomp=r('GuestBodyNoStomp');q.easy_descending=r('X5FootDescending')
 q.source_width=ps(0x70f);q.source_relative_foot=ps(0x6f1)
 q.source_origin=ps(0x89)+256*ps(0x8a);q.source_pose_delta=ps(0x88)
 q.source_projection_collision_field=ps(0x4c3)
 local slot=ram(L.ObjectOffset);q.native_collision_slot=slot
 if slot>=0 and slot<6 then
  local eb=L.EnemyBoundingBoxCoord+4*slot
  q.native_enemy_screen={ram(eb),ram(eb+1),ram(eb+2),ram(eb+3)}
  q.native_enemy_world={ram(eb)+camera,ram(eb+1),ram(eb+2)+camera,ram(eb+3)}
  q.native_enemy={id=ram(L.Enemy_ID+slot),flag=ram(L.Enemy_Flag+slot),bound_control=ram(L.Enemy_BoundBoxCtrl+slot),x=ram(L.Enemy_X_Position+slot)+256*ram(L.Enemy_PageLoc+slot),y=ram(L.Enemy_Y_Position+slot),state=ram(L.Enemy_State+slot)}
 end
 return q
end
pipeRoute.pose_boxes={};pipeRoute.precontacts={};pipeRoute.HP_bus_writes={}
local lastJumpPose=nil
emu.addMemoryCallback(function(_,value)
 if not sourceActive()then return end
 local at=emu.convertAddress(0xc6cf)
 if not at or at.memType~=emu.memType.nesWorkRam or at.address~=2*8192+0x6cf then return end
 if #pipeRoute.HP_bus_writes<16 then
  local q=wholeBoxes('actual-HP-bus-write');q.write_value=value;q.stamp=stamp()
  pipeRoute.HP_bus_writes[#pipeRoute.HP_bus_writes+1]=q
 end
end,emu.callbackType.write,0xc6cf)
'''


def prepare(output,rom,text,refs,**kwargs):
    assert B.P.sha(rom)==B.PIN
    symbols={n:int(a,16)for a,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',GLOBALS.read_text(),re.M)}
    needed=['ObjectOffset','BoundingBox_UL_XPos','EnemyBoundingBoxCoord',
            'Enemy_BoundBoxCtrl','Player_Y_Speed','CrossoverBehaviorVersion',
            'GuestBodyNoStomp','X5FootDescending']
    aliases={n:symbols[n]for n in needed}
    anchor='-- Controller-only source; Q is supplied by the hash-bound plan preparer.'
    assert text.count(anchor)==1
    text=text.replace(anchor,'Q.mode="Prince-original-first-pipe193"\nfor n,a in pairs('+lua(aliases)+')do L[n]=a end\n'+anchor)
    anchor='local function controls_tick(finish)'
    assert text.count(anchor)==1
    text=text.replace(anchor,WITNESS+'\n'+anchor)
    old='local hp=ps(0x6cf)'
    assert text.count(old)==1
    text=text.replace(old,"if part=='run-jump'and ps(0x617)~=lastJumpPose then\n  lastJumpPose=ps(0x617);require(#pipeRoute.pose_boxes<32,'Bounded original runjump pose rectangles');pipeRoute.pose_boxes[#pipeRoute.pose_boxes+1]=wholeBoxes('runjump-endframe-pose')\n end\n "+old)
    old="elseif name=='PpNativeContact'then contactCalls=contactCalls+1"
    assert text.count(old)==1
    # The hook is installed earlier than the helper declaration. Forward
    # declare the helper before hooks so the closure captures the local.
    text=text.replace('local require\n','local wholeBoxes\nlocal require\n',1)
    text=text.replace('local function wholeBoxes(tag)','wholeBoxes=function(tag)',1)
    text=text.replace(old,old+";if wholeBoxes and #pipeRoute.precontacts<8 then pipeRoute.precontacts[#pipeRoute.precontacts+1]=wholeBoxes('actual-PpNativeContact-before-reaction')end")
    old='state=ram(L.Enemy_State+i)}'
    assert text.count(old)==1
    text=text.replace(old,'state=ram(L.Enemy_State+i),bound_control=ram(L.Enemy_BoundBoxCtrl+i)}')
    assert 'enemy.gap>=60 and enemy.gap<=96'in text and'enemy.gap<=120'not in text
    assert not any(k in text for k in ['emu.write','emu.loadSavestate','emu.reset','emu.loadState'])
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    assert LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
    kwargs['scope']+=' Distinct193 changes only runningA upperrequestgap120→96 (lower60), derivedfromactual189 apex/landing positions. Adds physicalmapped precontact/source/native/enemy wholebox and16HPwrite-PC witnesses; no policy/physics/ROM changes.189negative retained. No promise of injuryavoidance before actual run.'
    return original(output,rom,text,[*refs,Path(__file__),GLOBALS,NEGATIVE],**kwargs)


def main():
    q=json.loads(NEGATIVE.read_text())
    assert not q['passed']and q['ROM_sha256']==B.PIN and q['contact_calls']==1
    assert(q['state']['HP'],q['state']['source_action'],q['state']['source_frame'])==(0,85,43)
    assert q['first_pipe_route']['running_jump']['admission']['world_x']==224
    B.O=O
    old='enemy.gap>=60 and enemy.gap<=120'
    assert B.TICK.count(old)==1
    B.TICK=B.TICK.replace(old,'enemy.gap>=60 and enemy.gap<=96')
    B.ORIGINAL_PREPARE=prepare
    B.main()
    ready=O/'native/ready.json'
    receipt=dict(prepared=True,native_run=False,ROM_SHA256=B.PIN,
        ready=ready.relative_to(R).as_posix(),ready_SHA256=B.P.sha(ready),
        controller_SHA256=B.P.sha(ready.parent/'controller.lua'),
        prior_negative=NEGATIVE.relative_to(R).as_posix(),
        actual189=dict(A_request_X=224,actual_request_gap=110,action4_admission_Main=139,
            native_apex_X=313,native_apex_Y=161,source_apex_foot=193,
            fatal_landing_X=321,Goomba_X=317,Goomba_Y=184,source_pose=43,source_HP=0),
        single_control_change=dict(old_upper_gap=120,new_upper_gap=96,lower_gap=60,
            source_admission_predicate='action1/mode1/pose6..13/A-lock0 unchanged'),
        telemetry='Before-reaction mappedPpNativeContact snapshot,32jump-pose wholeboxes,16mappedHPwritePCs; normal firstpipe/header/body/DMA/lives guards unchanged.',
        source_files_to_commit=[Path(__file__).relative_to(R).as_posix(),Path(B.__file__).relative_to(R).as_posix()],
        command='python '+(O/'native/run.py').relative_to(R).as_posix())
    (O/'prepared193.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))


if __name__=='__main__':main()
