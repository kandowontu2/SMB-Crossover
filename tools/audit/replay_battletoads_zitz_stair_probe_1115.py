"""Passive exactbc5 Zitz6334 diagnostic; frozen controls are unchanged."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import compose_hot_draw_bt_67e_1115 as C
import replay_hot_draw_bt_67e_1115 as Base
import hot_draw_bt_67e_model_1115 as Model

R,ROM,W,N=C.R,C.ROM,Base.W,Base.N
BASE_SHA='e3c497579769eb2599651f78f8c788da892f3f540794f0a06624defbdf3cdc0a'
FROZEN_LUA='6334b3e385ef93f56d482c834d59c30137d5169a5e832eb8609ed77af0186870'
FIELDS=('BtSrc_Objects_Xpos_L','BtSrc_Objects_Xpos_H','BtSrc_Objects_Ypos_L','BtSrc_Objects_Ypos_H',
    'BtSrc_Objects_Zpos_L','BtSrc_Objects_Zpos_H','BtSrc_Objects_X_sub','BtSrc_Objects_Z_sub',
    'BtSrc_Objects_X_speed','BtSrc_Objects_Z_speed','BtSrc_Objects_Z_spd_sub','BtSrc_Objects_Z_floor',
    'BtSrc_Objects_Flags','BtSrc_Objects_dir','BtSrc_Objects_Life','BtSrc_Objects_death_timer',
    'BtSrc_FrameCounter','BtSrc_FrameCounter_Even','BtSrc_player1_obj_wanted_frame','BtLastXSpeed','BtLastYSpeed')


@lru_cache(maxsize=1)
def bindings(raw):
    assert isinstance(raw,bytes)and C.H(raw)==C.CANDIDATE,'Exact privatebc5 only'
    assert C.H(Path(Base.__file__).read_bytes())==BASE_SHA
    C.inverse(raw);q=deepcopy(Base.bindings(raw,'zitz'));b=Model.symbols(raw)
    for name in FIELDS:q['ram'][name]=W.address(b,name)
    movement=W.address(b,'BtMovement');entry=W.address(b,'BtCoreStep')
    cache=raw[1989648:1989648+8192];call=bytes((0x20,entry&255,entry>>8))
    sites=[pc for pc in range(movement,entry)if cache[pc&8191:(pc&8191)+3]==call]
    assert len(sites)==1,(movement,entry,sites)
    ret=sites[0]+3
    assert cache[ret&8191]==0x20 and int.from_bytes(cache[(ret&8191)+1:(ret&8191)+3],'little')==W.address(b,'BtExportNative')
    def point(pc):return dict(pc=pc,offset=3*8192+(pc&8191),bytes=list(cache[pc&8191:(pc&8191)+8]))
    q['stair_probe']=dict(entry=point(entry),worker_return=point(ret),call_pc=sites[0],
        cache_SHA256=C.H(cache),actor_fields=[n for n in FIELDS if n.startswith('BtSrc_Objects_')or n=='BtSrc_player1_obj_wanted_frame'],
        global_fields=[n for n in FIELDS if not(n.startswith('BtSrc_Objects_')or n=='BtSrc_player1_obj_wanted_frame')],
        x_half_open=[2144,2257],maximum_rows=8,maximum_aggregate_groups=32,frozen_controller_SHA256=FROZEN_LUA)
    return q


OBSERVER=r'''
local stairPending,stairWorker,stairSignature=nil,nil,nil
local function stairCode(h)
 local a=emu.convertAddress(h.pc)
 if not a or a.memType~=emu.memType.nesWorkRam or a.address~=h.offset then return false end
 for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Exact BT stair code')end
 return true
end
local function stairSource(index)
 local out={}
 for _,name in ipairs(C.stair_probe.actor_fields)do out[name]=r(name,index)end
 for _,name in ipairs(C.stair_probe.global_fields)do out[name]=r(name)end
 return out
end
emu.addMemoryCallback(guard(function()
 if not stairCode(C.stair_probe.entry)or not first or not active()or not identity()then return end
 assert(not stairPending,'Previous actual BT worker must return')
 local cpu=emu.getState();local sp=cpu['cpu.sp']
 local ret=emu.read(0x100+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(0x100+((sp+2)&255),emu.memType.nesDebug)+1
 assert(ret==C.stair_probe.worker_return.pc,'Actual BT movement return word')
 stairPending={Main=updates,frame=frame,movement=btMoves,entry_sp=sp,return_pc=ret,return_sp=(sp+2)&255,
  A=cpu['cpu.a'],X=cpu['cpu.x'],Y=cpu['cpu.y'],P=cpu['cpu.ps']or cpu['cpu.p'],SavedJoypadBits=r('SavedJoypadBits'),btHeld=btHeld,
  requested_A=not not btInput.a,last_set_A=lastA,
  native={x=pos('Player_X_Position','Player_PageLoc'),y=r('Player_Y_Position'),state=r('Player_State'),
   vx=r('Player_X_Speed'),vy=r('Player_Y_Speed'),engine=r('GameEngineSubroutine')},before=stairSource(cpu['cpu.x'])}
 stairProbe.worker_entries=stairProbe.worker_entries+1
 if stairPending.A~=stairPending.SavedJoypadBits then
  stairProbe.A_saved_mismatches=stairProbe.A_saved_mismatches+1
  if stairPending.native.x>=2144 and stairPending.native.x<=2256 then
   stairProbe.stair_A_saved_mismatches=stairProbe.stair_A_saved_mismatches+1
   stairProbe.first_stair_A_saved_mismatch=stairProbe.first_stair_A_saved_mismatch or stairPending
  end
 end
end),emu.callbackType.exec,C.stair_probe.entry.pc)
emu.addMemoryCallback(guard(function()
 if not stairPending or not stairCode(C.stair_probe.worker_return)then return end
 local cpu=emu.getState();assert(cpu['cpu.sp']==stairPending.return_sp,'Actual BT worker SP acknowledgment')
 stairPending.after=stairSource(stairPending.X);stairPending.returned_sp=cpu['cpu.sp']
 if stairPending.native.x>=2144 and stairPending.native.x<=2256 then
  local before,after=stairPending.before,stairPending.after
  local key=(stairPending.A&128)..'/'..(stairPending.SavedJoypadBits&128)..'/'..(stairPending.btHeld&128)..'/'..
   tostring(stairPending.requested_A)..'/'..tostring(stairPending.last_set_A)..'/'..(before.BtSrc_FrameCounter_Even&1)..'/'..
   before.BtSrc_Objects_Z_floor..'/'..after.BtSrc_Objects_Z_floor..'/'..tostring(after.BtSrc_Objects_Z_speed==0)
  if stairProbe.groups[key]then stairProbe.groups[key]=stairProbe.groups[key]+1
  elseif stairProbe.group_count<32 then stairProbe.groups[key]=1;stairProbe.group_count=stairProbe.group_count+1
  else stairProbe.group_overflow=stairProbe.group_overflow+1 end
 end
 stairWorker=stairPending;stairPending=nil;stairProbe.worker_returns=stairProbe.worker_returns+1
end),emu.callbackType.exec,C.stair_probe.worker_return.pc)
local oldStairDecide=btDecide
btDecide=function()
 oldStairDecide()
 if not(first and active()and identity()and r('LevelNumber')==0)then return end
 local c=context();if c.x<2144 or c.x>2256 then return end
 local row={Main=updates,frame=frame,movement=btMoves,x=c.x,y=c.y,state=c.state,lastA=c.lastA,
  held=btHeld,SavedJoypadBits=r('SavedJoypadBits'),input={right=not not btInput.right,left=not not btInput.left,a=not not btInput.a,b=not not btInput.b},
  policy=stairPolicySnapshot,worker=stairWorker,front_top=c.block(c.x+42,c.y+8),front_feet=c.block(c.x+42,c.y+24),support={}}
 for y=math.min(c.y+40,232),232,16 do row.support[#row.support+1]={y=y,tile=c.block(c.x+32,y)}end
 local signature=c.x..'/'..c.y..'/'..c.state..'/'..tostring(c.lastA)..'/'..tostring(btInput.a)..'/'..tostring(btInput.b)..'/'..r('BtSrc_FrameCounter_Even')
 if signature==stairSignature then return end;stairSignature=signature;stairProbe.decisions=stairProbe.decisions+1
 if#stairProbe.first<3 then stairProbe.first[#stairProbe.first+1]=row
 else stairProbe.tail[#stairProbe.tail+1]=row;if#stairProbe.tail>4 then table.remove(stairProbe.tail,1)end end
end
'''


@lru_cache(maxsize=1)
def controller(raw):
    original=Base.controller(raw,'zitz');assert C.H(original.encode())==FROZEN_LUA
    text=Base.Frozen.rebound(original,bindings(raw))
    marker='local choose=(function()';assert text.count(marker)==1
    text=text.replace(marker,'local stairPolicySnapshot=nil\nlocal stairProbe={first={},tail={},decisions=0,worker_entries=0,worker_returns=0,A_saved_mismatches=0,stair_A_saved_mismatches=0,groups={},group_count=0,group_overflow=0}\n'+marker,1)
    marker=' if c.x>3120 then b.right=true;b.b=false;if c.grounded and not c.lastA then b.a=true end end\n return b'
    assert text.count(marker)==1
    text=text.replace(marker," if c.x>=2144 and c.x<=2256 then stairPolicySnapshot={phase=phase,jumpAge=jumpAge,still=still,grounded=c.grounded,lastA=c.lastA,obstacle=obstacle,support=support,danger=not not danger}end\n"+marker,1)
    marker="btDecide=function()\n if menuDone and active()and identity()and r('LevelNumber')==0 then btInput=choose(context())else btInput={}end\nend"
    assert text.count(marker)==1;text=text.replace(marker,marker+'\n'+OBSERVER,1)
    marker='checkpoints=checkpoints,menu_events=menuEvents';assert text.count(marker)==1
    text=text.replace(marker,'stair_probe=stairProbe,'+marker,1)
    Base.Original.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw):
    text=controller(raw);q=bindings(raw)
    return dict(ROM_SHA256=C.H(raw),controller_SHA256=C.H(text.encode()),frozen_Zitz6334_SHA256=FROZEN_LUA,
        code_binding=q['stair_probe'],maximum_rows=8,maximum_aggregate_groups=32,ordinary_controls_and_success_endpoint_unchanged=True,
        observer_only=True,outputs=0,Mesen_run=False)
