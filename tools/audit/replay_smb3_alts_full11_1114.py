"""Strict421 SMB3 Toad/Peach normal-control full-stage observers."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

import replay_smb1_alts_full11_1114 as Frozen

PIN,ROM,W,N=Frozen.PIN,Frozen.ROM,Frozen.W,Frozen.N
IDENTITIES={'toad3':('SMB3 TOAD',2,2),'peach3':('SMB3 PEACH',3,3)}
FROZEN_SOURCE='e25b9510f2fbdc5ece466033ad02d8ba25abc19cf8359bb15e3bcfe669b3af61'
FROZEN_LUA='7057409ee03b52b0cd58394164e715521279772884ebae5488a47522b5124744'
LUA_SHA={'toad3':'c8f59a13d8acfddb8c87799bc223b68ab11b6ab6f53485fe54d02634d6b8b79b',
    'peach3':'bf45e99dc32da8c377588c344f8abd79c8970ad774f314529707dbf1d94594d1'}
normalize=Frozen.normalize
ROUTE_ROOT=Frozen.R/'tools/playthroughs'
CHIP=ROUTE_ROOT/'current_roster_chip_pickup_v2.lua'
STAIR=ROUTE_ROOT/'current_roster_smb3_stair_v2.lua'
POLE=ROUTE_ROOT/'current_roster_smb3_pole_v4.lua'
ROUTE_PINS={CHIP:'b77a6897b302de2955ff32b83b03edff7b886cb340587184d1c21e50553cb34b',
    STAIR:'4fc9eec0882428141db17821b5d276712fd8ee597a95d9dbf3d05e7ea0070367',
    POLE:'19fde5dedbd7252ef3aa87fc380a00363b0322a02e86d1d6e8bb788c6b044579'}


@lru_cache(maxsize=2)
def bindings(raw,key):
    assert key in IDENTITIES and sha256(raw).hexdigest()==PIN
    assert sha256(Path(Frozen.__file__).read_bytes()).hexdigest()==FROZEN_SOURCE
    q=deepcopy(Frozen.bindings(raw,'peach'));b=dict(W.Symbols.bundle(),raw=raw)
    name,cycle,variant=IDENTITIES[key]
    m=W.UI.seed(b,0);W.UI.key(m,4);W.UI.key(m,4)
    assert N.get(m,'CrossoverMenuIndex')==16 and N.get(m,'SelectedCharacter')==17
    for _ in range(cycle):W.UI.key(m,32)
    assert (W.UI.menu_name(m)[0],N.get(m,'SelectedCharacter'),N.get(m,'M3Variant'))==(name,17,variant)
    q.update(key=key,name=name,cycle=cycle,variant=variant,owner=17,slot=16)
    for n in('M3Variant','M3Ready','M3Form','M3Previous','PowerUpType','MbFloatReady','MbFloatExpired','MbFloatAnchor'):
        q['ram'][n]=W.address(b,n)
    for n in('M3Movement','M3Step'):
        pc,at=W.address(b,n),W.location(b,n)
        q['hooks'][n]=dict(pc=pc,offset=at-16,bytes=list(raw[at:at+8]))
    return q


def once(text,before,after):
    assert text.count(before)==1,before
    return text.replace(before,after,1)


def policy():
    assert all(sha256(p.read_bytes()).hexdigest()==v for p,v in ROUTE_PINS.items())
    chip=CHIP.read_text();stair=STAIR.read_text();pole=POLE.read_text()
    root='local root=ROSTER_CONFIG.root\n'
    stair=once(stair,root,'');pole=once(pole,root,'')
    stair=once(stair,"local base=dofile(root..'/tools/playthroughs/current_roster_chip_pickup_v2.lua')",'local base=(function()\n'+chip+'\nend)()')
    return once(pole,"local base=dofile(root..'/tools/playthroughs/current_roster_smb3_stair_v2.lua')",'local base=(function()\n'+stair+'\nend)()')


OBSERVE=r'''
local function m3Owner()
 if not first then return end
 assert(r('M3Ready')==0xb3,'Actual current SMB3 constructor/header')
 local form=r('M3Form')
 if form~=m3LastForm then m3LastForm=form;m3Forms[#m3Forms+1]=state();assert(#m3Forms<=16,'Bounded form path')end
 if C.variant==3 and r('Player_State')~=0 and r('MbFloatReady')==2 then m3Hover=m3Hover+1 end
end
hook('M3Movement',function()
 if not first then return end
 m3Calls=m3Calls+1
 if r('WorldNumber')==0 and r('LevelNumber')==1 and active()then m3Next=m3Next+1 end
end)
hook('M3Step',function()if first then m3Steps=m3Steps+1 end end)
'''


@lru_cache(maxsize=2)
def controller(raw,key):
    config=bindings(raw,key);old=Frozen.controller(raw,'peach')
    assert sha256(old.encode()).hexdigest()==FROZEN_LUA
    marker='-- Normal controller inputs and readonly native witnesses. No game-state writes.'
    _,body=old.split(marker,1);body=marker+body
    body=once(body,"r('SelectedCharacter')==0 and r('MarioVariant')==C.variant","r('SelectedCharacter')==17 and r('M3Variant')==C.variant")
    assert body.count("variant=r('MarioVariant')")==2
    body=body.replace("variant=r('MarioVariant')","variant=r('M3Variant')")
    body=once(body,'MarioVariant=C.variant','M3Variant=C.variant')
    body=once(body,'char=0,variant=C.variant','char=17,variant=C.variant')
    body=once(body," for i=1,C.cycle do press('select');", " press('down');press('down')\n assert(r('CrossoverMenuIndex')==16 and r('SelectedCharacter')==17 and r('M3Variant')==0,'Actual initial SMB3 Mario portrait')\n for i=1,C.cycle do press('select');")
    body=once(body,'local function finish(reason)','local m3Calls,m3Steps,m3Next,m3Hover=0,0,0,0\nlocal m3LastForm,m3Forms=-1,{}\nlocal function finish(reason)')
    body=once(body,"hook('GameLoop',function()",OBSERVE+"\nhook('GameLoop',function()")
    point=' pendingReturn=nil;updates=updates+1'
    body=once(body,point,point+'\n m3Owner()')
    body=once(body,"and nextUpdates==25 and identity()and r('NumberofLives')==2","and nextUpdates==25 and identity()and r('NumberofLives')==2 and m3Calls>0 and m3Steps>0 and m3Next>=25")
    body=once(body,'full_nonshortcut1_1=not not(flag and castle and entrance),game_state_writes=false','M3_movement_calls=m3Calls,M3_native_steps=m3Steps,M3_1_2_movement_calls=m3Next,M3_hover_ready2_air_samples=m3Hover,M3_forms=m3Forms,full_nonshortcut1_1=not not(flag and castle and entrance),game_state_writes=false')
    marker='emu.addEventCallback(guard(function()\n polls=polls+1'
    controls='controls=function(c)return choose(c)end'
    if key=='peach3':
        controls="""controls=function(c)
 local b=choose(c)
 -- Keep Peach's intended held-A hover through the real final stair gap.
 if c.world==0 and c.level==0 and c.x>=2360 and c.x<2544 and not c.grounded then b.a=true end
 return b
end"""
    body=once(body,marker,controls+'\n'+marker)
    text='local C='+Frozen.lua(config)+"\nROSTER_CONFIG={name='smb3'}\nlocal choose=(function()\n"+policy()+'\nend)()\n'+body
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    assert sha256(text.encode()).hexdigest()==LUA_SHA[key]
    return text


def metadata(raw,key):
    config=bindings(raw,key);text=controller(raw,key);parent=normalize(raw).postbg;preserved={}
    for bank in(66,81,90,91,92,124,126,127):
        at=16+bank*8192;assert raw[at:at+8192]==parent[at:at+8192]
        preserved[str(bank)]=sha256(raw[at:at+8192]).hexdigest()
    at=1048592+969*1024;end=1048592+1019*1024
    assert raw[at:end]==parent[at:end]
    return dict(ROM_SHA256=PIN,identity=key,compiled_menu={k:config[k]for k in('name','slot','owner','cycle','variant')},
        controller_SHA256=sha256(text.encode()).hexdigest(),frozen_observer_factory_SHA256=FROZEN_SOURCE,
        current_SMB3_core_float_menu_graphics_banks_equal12397=preserved,
        SMB3plus_CHR969_to1019_SHA256=sha256(raw[at:end]).hexdigest(),
        route_sources={p.name:sha256(p.read_bytes()).hexdigest()for p in(CHIP,STAIR,POLE)},
        genuine_M3_constructor_movement_and_native_steps_required=True,current176_fixes_preserved=True,
        normal_controls_only=True,frozen_sibling_factories_unchanged=True,gameplay_seeds=0,outputs=0,Mesen_run=False)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',choices=IDENTITIES,required=True)
    args=p.parse_args();print(json.dumps(metadata(ROM.read_bytes(),args.identity),separators=(',',':')),flush=True)
