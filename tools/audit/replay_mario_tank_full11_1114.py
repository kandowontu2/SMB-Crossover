"""Separate strict421 Tank full-stage controller; frozen sibling routes exact."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

import replay_smb1_alts_full11_1114 as Frozen

PIN=Frozen.PIN
ROM=Frozen.ROM
W,N=Frozen.W,Frozen.N
IDENTITIES={'tank':('MARIO THE TANK',7,7)}
FROZEN_SOURCE='e25b9510f2fbdc5ece466033ad02d8ba25abc19cf8359bb15e3bcfe669b3af61'
FROZEN_LUA='294bc876f63bfed77bc0b8fa087036b7b5a01906e99ead2f909e81f20a68ef3c'
LUA_SHA='f6d5fce6e1aae6a0041065265abf903f50529d91ed25c0091473053052d9b132'
normalize=Frozen.normalize


@lru_cache(maxsize=1)
def bindings(raw,key='tank'):
    assert key=='tank'and sha256(raw).hexdigest()==PIN
    assert sha256(Path(Frozen.__file__).read_bytes()).hexdigest()==FROZEN_SOURCE
    q=deepcopy(Frozen.bindings(raw,'toad'))
    m=W.UI.seed(dict(W.Symbols.bundle(),raw=raw),0)
    for _ in range(7):W.UI.key(m,32)
    assert (W.UI.menu_name(m)[0],N.get(m,'SelectedCharacter'),N.get(m,'MarioVariant'))==('MARIO THE TANK',0,7)
    q.update(key='tank',name='MARIO THE TANK',cycle=7,variant=7)
    at=16+28*8192+8112
    cookie=raw[at+55:at+71]
    assert len(cookie)==16 and cookie[:4]==bytes.fromhex('a7f70501')
    image=raw[1048592+501*1024:1048592+503*1024]
    assert len(image)==2048
    q['tank']=dict(cookie=list(cookie),image=list(image),movement_pc=0xb676,
        movement_raw=2*8192+0x1676,movement_bytes=list(image[0x76:0x7e]))
    return q


OBSERVER=r'''
-- Full actual cold Tank ownership, not a preloaded or powered fixture.
local function tankOwner()
 if not first then return end
 local nextArea=r('WorldNumber')==0 and r('LevelNumber')==1 and active()
 if not tankChecked or(nextArea and not tankNextChecked)then
  for i,v in ipairs(C.tank.cookie)do assert(emu.read(2*8192+0x1fe0+i-1,emu.memType.nesWorkRam)==v,'Actual full Tank cookie')end
  for i,v in ipairs(C.tank.image)do assert(emu.read(2*8192+0x1600+i-1,emu.memType.nesWorkRam)==v,'Actual full Tank cold worker')end
  tankChecked=true
  if nextArea then tankNextChecked=true end
 end
 local status=r('PlayerStatus')
 if status~=tankStatus then tankStatus=status;tankPowerPath[#tankPowerPath+1]=state();assert(#tankPowerPath<=8,'Bounded power path')end
end
emu.addMemoryCallback(guard(function()
 local a=emu.convertAddress(C.tank.movement_pc)
 if not a or a.memType~=emu.memType.nesWorkRam or a.address~=C.tank.movement_raw then return end
 if not first then return end
 for i,v in ipairs(C.tank.movement_bytes)do assert(emu.read(C.tank.movement_pc+i-1,emu.memType.nesDebug)==v,'Exact current Tank native movement worker')end
 tankCalls=tankCalls+1
 if r('WorldNumber')==0 and r('LevelNumber')==1 and active()then tankNextCalls=tankNextCalls+1 end
end),emu.callbackType.exec,C.tank.movement_pc)
'''


@lru_cache(maxsize=1)
def controller(raw,key='tank'):
    config=bindings(raw,key);original=Frozen.controller(raw,'toad')
    assert sha256(original.encode()).hexdigest()==FROZEN_LUA
    first,body=original.split('\n',1)
    assert first.startswith('local C=')
    text='local C='+Frozen.lua(config)+'\n'+body
    marker='local function finish(reason)'
    assert text.count(marker)==1
    text=text.replace(marker,'local tankChecked,tankCalls,tankNextChecked,tankNextCalls=false,0,false,0\nlocal tankStatus,tankPowerPath=-1,{}\n'+marker,1)
    marker="hook('GameLoop',function()"
    assert text.count(marker)==1
    text=text.replace(marker,OBSERVER+'\n'+marker,1)
    point=" pendingReturn=nil;updates=updates+1"
    assert text.count(point)==1
    text=text.replace(point,point+'\n tankOwner()',1)
    point="and nextUpdates==25 and identity()and r('NumberofLives')==2"
    assert text.count(point)==1
    text=text.replace(point,point+' and tankChecked and tankNextChecked and tankCalls>0 and tankNextCalls>=25',1)
    point='full_nonshortcut1_1=not not(flag and castle and entrance),game_state_writes=false'
    assert text.count(point)==1
    text=text.replace(point,'Tank_cookie_verified=tankChecked,Tank_next_area_worker_verified=tankNextChecked,Tank_loaded_worker_bytes=2048,Tank_movement_calls=tankCalls,Tank_1_2_movement_calls=tankNextCalls,Tank_status_path=tankPowerPath,'+point,1)
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot'))
    assert sha256(text.encode()).hexdigest()==LUA_SHA
    return text


def metadata(raw,key='tank'):
    q=bindings(raw,key);text=controller(raw,key);parent=normalize(raw).postbg;preserved={}
    banks=(1,12,13,28,31,32,33,35,58,62,66,68,73,78,81,82,86,89,115,124,126,127)
    for bank in banks:
        at=16+bank*8192
        assert raw[at:at+8192]==parent[at:at+8192],('Tank bank changed',bank)
        preserved[str(bank)]=sha256(raw[at:at+8192]).hexdigest()
    a=1048592+501*1024;z=a+2048
    assert raw[a:z]==parent[a:z]
    return dict(ROM_SHA256=PIN,identity='tank',compiled_menu={k:q[k]for k in('name','cycle','variant')},
        controller_SHA256=sha256(text.encode()).hexdigest(),frozen_parent_Lua_SHA256=FROZEN_LUA,
        frozen_factory_source_SHA256=FROZEN_SOURCE,full_Tank_host_loader_menu_dispatch_physics_banks_equal12397=preserved,
        Tank_carrier501_502_SHA256=sha256(raw[a:z]).hexdigest(),Tank_expected_complete_cookie=bytes(q['tank']['cookie']).hex(),
        actual_cold_worker_and_cookie_readonly_assertions=True,current176_fixes_preserved=True,
        intended_native_Mario_movement=True,powered_boots_or_natural_item_success_not_presumed=True,
        frozen_sibling_factories_unchanged=True,normal_controls_only=True,gameplay_seeds=0,outputs=0,Mesen_run=False)


if __name__=='__main__':print(json.dumps(metadata(ROM.read_bytes()),separators=(',',':')),flush=True)
