"""Strict421 Doc Louis, actual compiled alternate and normal boxing controls."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

import replay_smb1_alts_full11_1114 as Frozen

PIN,ROM,W,N=Frozen.PIN,Frozen.ROM,Frozen.W,Frozen.N
IDENTITIES={'doc':('DOC LOUIS',1,1)}
normalize=Frozen.normalize
FROZEN_SOURCE='e25b9510f2fbdc5ece466033ad02d8ba25abc19cf8359bb15e3bcfe669b3af61'
FROZEN_LUA='7057409ee03b52b0cd58394164e715521279772884ebae5488a47522b5124744'
R=Frozen.R
POLICY=R/'tools/playthroughs/mac_roster_11_v2.lua'
STAIR=R/'tools/playthroughs/mac_roster_11_v3.lua'
PINS={POLICY:'29f62d0da3c489502c445d11c1c23081ecc89037470e499948ef8d3a51da7b55',
    STAIR:'a656c0a8ef2458fa29cbc97b7362cb90632dd62a8f6ee39764186c8a57d3b8d1'}
LUA_SHA='b2e4db99c6fd25b4c3d9d7813b63239576d8636d1a9d57cedf39ab420e35780a'


def once(text,before,after):
    assert text.count(before)==1,before
    return text.replace(before,after,1)


@lru_cache(maxsize=1)
def bindings(raw,key='doc'):
    assert key=='doc'and sha256(raw).hexdigest()==PIN
    assert sha256(Path(Frozen.__file__).read_bytes()).hexdigest()==FROZEN_SOURCE
    q=deepcopy(Frozen.bindings(raw,'peach'));b=dict(W.Symbols.bundle(),raw=raw)
    m=W.UI.seed(b,0)
    for k in(4,2,2,32):W.UI.key(m,k)
    assert W.UI.menu_name(m)[0]=='DOC LOUIS'and N.get(m,'CrossoverMenuIndex')==14
    assert N.get(m,'SelectedCharacter')==15 and N.get(m,'MacVariant')==1
    q.update(key='doc',name='DOC LOUIS',cycle=1,variant=1,slot=14,owner=15)
    for n in('MacVariant','LmReady','LmPrevious','LmHealth','LmHearts','LmStars','LmAttack','LmSuper',
              'LmHurt','LmInvul','SavedJoypadBits','PowerUpType','ObjectOffset','Enemy_Y_HighPos'):
        q['ram'][n]=W.address(b,n)
    for n in('LmMovementGate','LmWeaponsGate'):
        at=W.location(b,n);q['hooks'][n]=dict(pc=W.address(b,n),offset=at-16,bytes=list(raw[at:at+8]))
    pc,at=W.address(b,'SetCollisionFlag'),W.location(b,'SetCollisionFlag')
    op=b'\x85'+bytes([W.address(b,'Player_State')]);end=raw[at:at+20].index(op)+2
    assert raw[at+end]==0x60
    q['hooks']['helper_support']=dict(pc=pc+end,offset=at+end-16,bytes=list(raw[at+end:at+end+8]))
    q['helper_authored']=dict(stage='1-1',actor=0x28,center_x=3104,left_x=3096,initial_y=64,width=16)
    return q


OWNER=r'''
local function helperActor(slot)
 return {slot=slot,id=r('Enemy_ID',slot),flag=r('Enemy_Flag',slot),native_x=pos('Enemy_X_Position','Enemy_PageLoc',slot),y=r('Enemy_Y_Position',slot),y_high=r('Enemy_Y_HighPos',slot)}
end
local function docOwner()
 if not first or not active()then return end
 assert(r('LmReady')==0x4d and r('LmHealth')>0,'Actual live boxing constructor/health')
 lmMin=math.min(lmMin,r('LmHealth'))
 local a=r('LmAttack')
 if a>0 and(a>lmLastAttack or lmLastAttack==0)then
  lmPunches=lmPunches+1
  if #lmAttacks<8 then lmAttacks[#lmAttacks+1]=state()end
 end
 lmLastAttack=a
 if r('WorldNumber')==0 and r('LevelNumber')==0 and not helperSeen then
  for slot=0,5 do local e=helperActor(slot)
   if e.flag>0 and e.flag<128 and e.id==0x28 and e.native_x>=2950 and e.native_x<3250 then helperSeen={actor=e,player=state()}end
  end
 end
end
hook('LmMovementGate',function()
 if not first or not identity()then return end
 lmMoves=lmMoves+1
 if r('WorldNumber')==0 and r('LevelNumber')==1 and active()then lmNext=lmNext+1 end
end)
hook('LmWeaponsGate',function()if first and active()and identity()then lmWeaponGates=lmWeaponGates+1 end end)
hook('helper_support',function()
 if not first or not identity()or helperSupport or r('WorldNumber')~=0 or r('LevelNumber')~=0 then return end
 local slot=r('ObjectOffset');if slot>5 then return end
 local e=helperActor(slot)
 if e.flag>0 and e.flag<128 and e.id==0x28 and r('Player_State')==0 then helperSupport={actor=e,player=state(),actual_SetCollisionFlag_return=true}end
end)
'''


@lru_cache(maxsize=1)
def controller(raw,key='doc'):
    q=bindings(raw,key);old=Frozen.controller(raw,'peach')
    assert sha256(old.encode()).hexdigest()==FROZEN_LUA
    assert all(sha256(p.read_bytes()).hexdigest()==pin for p,pin in PINS.items())
    marker='-- Normal controller inputs and readonly native witnesses. No game-state writes.'
    _,body=old.split(marker,1);body=marker+body
    policy=STAIR.read_text()
    policy=once(policy,"local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))\n",'')
    policy=once(policy,"local base=assert(dofile(root..'/tools/playthroughs/mac_roster_11_v2.lua'))",'local base=(function()\n'+POLICY.read_text()+'\nend)()')
    body=once(body,"r('SelectedCharacter')==0 and r('MarioVariant')==C.variant","r('SelectedCharacter')==15 and r('MacVariant')==C.variant")
    assert body.count("variant=r('MarioVariant')")==2
    body=body.replace("variant=r('MarioVariant')","variant=r('MacVariant')")
    body=once(body,'MarioVariant=C.variant','MacVariant=C.variant')
    body=once(body,'frame=frame,poll=polls,char=0','frame=updates,poll=updates,char=15')
    body=once(body,'lastA=lastA,grounded=',"lastA=(r('LmPrevious')&128)~=0,grounded=")
    body=once(body,"power=r('PlayerStatus'),lives=r('NumberofLives')","power=r('PlayerStatus'),hp=r('LmHealth'),hearts=r('LmHearts'),stars=r('LmStars'),attack=r('LmAttack'),super=r('LmSuper'),lives=r('NumberofLives')")
    body=once(body," for i=1,C.cycle do press('select');"," press('down');press('left');press('left')\n assert(r('CrossoverMenuIndex')==14 and r('SelectedCharacter')==15 and r('MacVariant')==0,'Actual Little Mac portrait')\n for i=1,C.cycle do press('select');")
    body=once(body,'local function finish(reason)','local docInput,docDecide={},nil\nlocal lmMoves,lmNext,lmWeaponGates,lmPunches,lmLastAttack,lmMin=0,0,0,0,0,255\nlocal lmAttacks,helperSeen,helperSupport={},nil,nil\nlocal function finish(reason)')
    body=once(body,"hook('GameLoop',function()",OWNER+"\nhook('GameLoop',function()")
    point=' pendingReturn=nil;updates=updates+1'
    body=once(body,point,point+'\n docOwner();if docDecide then docDecide()end')
    body=once(body,"and nextUpdates==25 and identity()and r('NumberofLives')==2","and nextUpdates==25 and identity()and r('NumberofLives')==2 and r('LmHealth')>0 and lmMoves>0 and lmNext>=25")
    body=once(body,'full_nonshortcut1_1=not not(flag and castle and entrance),game_state_writes=false','Lm_movement_gates=lmMoves,Lm_1_2_movement_gates=lmNext,Lm_weapon_gates=lmWeaponGates,punch_starts=lmPunches,punch_samples=lmAttacks,minimum_HP=lmMin,existing_helper_authored=C.helper_authored,helper_seen=helperSeen,helper_support=helperSupport,navigation_clock="completed Main snapshots",full_nonshortcut1_1=not not(flag and castle and entrance),game_state_writes=false')
    marker='emu.addEventCallback(guard(function()\n polls=polls+1'
    code="""controls=function(c)return choose(c)end
docDecide=function()
 if menuDone and active()and identity()and r('LevelNumber')==0 then docInput=controls(context())else docInput={}end
end
"""
    body=once(body,marker,code+marker)
    body=once(body,"if menuDone then b=active()and r('LevelNumber')==0 and controls(context())or{}end",'if menuDone then b=docInput end')
    text='local C='+Frozen.lua(q)+'\nlocal choose=(function()\n'+policy+'\nend)()\n'+body
    Frozen.LuaRuntime().compile(text)
    assert not any(v in text for v in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    assert sha256(text.encode()).hexdigest()==LUA_SHA
    return text


def metadata(raw,key='doc'):
    q=bindings(raw,key);text=controller(raw,key);parent=normalize(raw).postbg;preserved={}
    for bank in(1,93,94,95,124,126,127):
        at=16+bank*8192;assert raw[at:at+8192]==parent[at:at+8192]
        preserved[str(bank)]=sha256(raw[at:at+8192]).hexdigest()
    return dict(ROM_SHA256=PIN,identity='doc',compiled_menu={k:q[k]for k in('name','slot','owner','cycle','variant')},
        controller_SHA256=sha256(text.encode()).hexdigest(),frozen_factory_source_SHA256=FROZEN_SOURCE,
        route_source_SHA256={p.name:sha256(p.read_bytes()).hexdigest()for p in PINS},
        current_boxing_profile_art_motion_banks_equal12397=preserved,current176_fixes_preserved=True,
        intended_shared_boxing_health_hearts_stars_punches=True,actual_live_constructor_required=True,
        existing_helper_authored=q['helper_authored'],helper_changes=0,helper_support_must_be_observed_before_claiming_assistance=True,
        navigation_clock='completed Main snapshots; polls apply cached buttons',normal_controls_only=True,
        gameplay_seeds=0,outputs=0,Mesen_run=False)


if __name__=='__main__':print(json.dumps(metadata(ROM.read_bytes()),separators=(',',':')),flush=True)
