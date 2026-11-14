"""Strict current Mr. Gimmick full-stage input investigation, zero outputs."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json

import replay_ryan_full11_current_1114 as Current
import replay_smb1_alts_full11_1114 as Frozen

R,ROM,W,N,DK=Current.R,Current.ROM,Current.W,Current.N,Current.DK
PIN=DK.CANDIDATE
IDENTITIES={'mr_gimmick':('MR GIMMICK',0,0)}
normalize=Current.normalize

POLICY=r'''
local jumpAge=-1
return function(c)
 local b={right=true}
 local star=c.r('GmRam0091')
 b.b=star==0 or(star>=128 and star<169)
 local function solid(x,y)
  local t=c.block(x,y)
  return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3 and t~=0x5f
 end
 if c.world~=0 or c.level~=0 then return{}end
 if c.grounded and not c.lastA then jumpAge=-1 end
 local e=c.enemy()
 local obstacle=solid(c.x+42,c.y+24)or solid(c.x+42,c.y+18)
 local support=false
 -- The source hero's leading foot is near nativeX+11. Mario's generic
 -- +32 gap lookahead launches this shorter original jump too early.
 for y=math.min(c.y+40,232),232,16 do if solid(c.x+10,y)then support=true;break end end
 local danger=e and e.dx>0 and e.dx<56 and math.abs(e.y-c.y)<56
 if c.grounded and not c.lastA and(obstacle or not support or danger)then b.a=true;jumpAge=0
 elseif not c.grounded and jumpAge>=0 then jumpAge=jumpAge+1;b.a=jumpAge<42 end
 return b
end
'''


def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new,1)


@lru_cache(maxsize=2)
def bindings(raw,key='mr_gimmick'):
    assert key=='mr_gimmick';normalize(raw)
    legacy=DK.Common.inverse(Current.owning82(raw));q=deepcopy(Frozen.bindings(legacy,'peach'))
    b=dict(W.Symbols.bundle(),raw=raw);m=W.UI.seed(b,0);nav=[1,4,4,4]
    for pad in nav:W.UI.key(m,pad)
    name=W.UI.menu_name(m)[0]
    assert name in('MR GIMMICK','MR. GIMMICK'),name
    assert N.get(m,'CrossoverMenuIndex')==25 and N.get(m,'SelectedCharacter')==26
    q.update(sha=sha256(raw).hexdigest(),key=key,name=name,owner=26,slot=25,variant=0,cycle=0,navigation=nav)
    for name in('GmReady','GmLife','GmArea','GmWorld','GmRam002B','GmRam0346','GmClock','GmFresh','GmPrevious',
        'GmRam0090','GmRam0091','GmRam009A','GmRam00A4','GmRam00AE','GmRam00B8',
        'GmRam009B','GmRam00A5','GmRam00AF','GmRam00B9','GmRam00C2','GmRam00C3','GmRam00CC','GmRam00CD',
        'GmRam00D7','GmRam030A','GmRam036E','GmRam036F','GmRam0039','GmRam0351','CurrentCHRBank','PowerUpType'):
        q['ram'][name]=W.address(b,name)
    for name in('GmMovement','GmAfterTerrain','GmRideStar'):
        at=W.location(b,name);q['hooks'][name]=dict(pc=W.address(b,name),offset=at-16,bytes=list(raw[at:at+8]),bank=(at-16)//8192)
    start,end=W.location(b,'GmMovement'),W.location(b,'GmImport')
    call=b'\x20'+W.address(b,'GmRideStar').to_bytes(2,'little')
    found=[i for i in range(start,end-2)if raw[i:i+3]==call]
    assert len(found)==1,found
    at=found[0]+3;pc=W.address(b,'GmMovement')+at-start
    q['hooks']['GmRideStarReturn']=dict(pc=pc,offset=at-16,bytes=list(raw[at:at+8]),bank=(at-16)//8192)
    for name,h in q['hooks'].items():
        at=16+h['offset'];assert raw[at:at+len(h['bytes'])]==bytes(h['bytes']),name
        if'bank'in h:
            at=16+h['bank']*8192;h['bank_SHA256']=sha256(raw[at:at+8192]).hexdigest()
    return q


@lru_cache(maxsize=2)
def controller(raw,key='mr_gimmick'):
    q=bindings(raw,key);legacy=DK.Common.inverse(Current.owning82(raw));original=Frozen.controller(legacy,'peach')
    marker='-- Normal controller inputs and readonly native witnesses. No game-state writes.'
    body=marker+original.split(marker,1)[1]
    body=once(body,"r('SelectedCharacter')==0 and r('MarioVariant')==C.variant","r('SelectedCharacter')==26 and r('GmReady')==71")
    assert body.count("variant=r('MarioVariant')")==2
    body=body.replace("variant=r('MarioVariant')","variant=0")
    body=once(body,'MarioVariant=C.variant','Gimmick_variant=0')
    body=once(body,"power=r('PlayerStatus'),lives=r('NumberofLives')",
        "power=r('PlayerStatus'),source_HP=r('GmRam0346'),source_max=r('GmRam002B'),hero_status=r('GmRam0090'),source_vy=r('GmRam00C2'),source_ground=r('GmRam036E'),star_status=r('GmRam0091'),star_flags=r('GmRam00D7'),star_x=(r('GmRam00AF')+256*r('GmRam00B9'))/16,star_y=(r('GmRam009B')+256*r('GmRam00A5'))/16,lives=r('NumberofLives')")
    body=once(body,'frame=frame,poll=polls,char=0','frame=updates,poll=updates,char=26')
    body=once(body,'lastA=lastA,grounded=',"lastA=(r('GmPrevious')&128)~=0,grounded=")
    body=once(body," for i=1,C.cycle do press('select');", " press('right');press('down');press('down');press('down')\n assert(r('CrossoverMenuIndex')==25 and r('SelectedCharacter')==26,'Actual Mr Gimmick slot')\n for i=1,C.cycle do press('select');")
    # Menu Ready is constructed only at real Start, so check owner prelaunch.
    body=once(body," assert(identity(),'Actual compiled alternate cycle')"," assert(r('SelectedCharacter')==26,'Actual compiled Gimmick owner')")
    body=once(body,'local function finish(reason)','local gmInput,gmDecide={},nil\nlocal gmMoves,gmNext,gmRides,gmBefore,gmFirstRide=0,0,0,nil,nil\nlocal function finish(reason)')
    body=once(body,"hook('GameLoop',function()", """hook('GmMovement',function()
 if first and identity()and active()then gmMoves=gmMoves+1;if r('LevelNumber')==1 then gmNext=gmNext+1 end end
end)
hook('GmRideStar',function()
 if first and identity()and active()then gmBefore={ground=r('GmRam036E'),vy=r('GmRam00C2'),flags=r('GmRam00D7')}else gmBefore=nil end
end)
hook('GmRideStarReturn',function()
 if gmBefore and gmBefore.ground<128 and gmBefore.vy<128 and gmBefore.flags&64~=0 and r('GmRam036E')==128 and r('GmRam00C2')==0 then gmRides=gmRides+1;gmFirstRide=gmFirstRide or state()end
 gmBefore=nil
end)
hook('GameLoop',function()""")
    point=' pendingReturn=nil;updates=updates+1'
    body=once(body,point,point+'\n if gmDecide then gmDecide()end')
    body=once(body,"and nextUpdates==25 and identity()and r('NumberofLives')==2",
        "and nextUpdates==25 and identity()and r('NumberofLives')==2 and gmMoves>0 and gmNext>=25 and r('GmRam0346')>0")
    body=once(body,'full_nonshortcut1_1=not not(flag and castle and entrance),game_state_writes=false',
        'Gm_movement_calls=gmMoves,Gm_1_2_movement_calls=gmNext,genuine_star_supports=gmRides,first_star_support=gmFirstRide,navigation_clock="completed Main snapshots",full_nonshortcut1_1=not not(flag and castle and entrance),game_state_writes=false')
    body=once(body,"assert(identity()and r('NumberofLives')==2 and r('AreaType')==1 and r('AreaAddrsLOffset')==5,'Genuine initial1-1')",
        "assert(identity()and r('NumberofLives')==2 and r('AreaType')==1 and r('AreaAddrsLOffset')==5 and r('GmRam0346')==2 and r('GmRam002B')==2 and r('GmRam0039')==0,'Actual current Gimmick constructor')")
    start=body.index("local stairPhase,stairAge='approach',0")
    end=body.index('emu.addEventCallback(guard(function()\n polls=polls+1',start)
    body=body[:start]+"""local function controls(c)return choose(c)end
gmDecide=function()
 if menuDone and active()and identity()and r('LevelNumber')==0 then gmInput=controls(context())else gmInput={}end
end
"""+body[end:]
    body=once(body,"if menuDone then b=active()and r('LevelNumber')==0 and controls(context())or{}end",'if menuDone then b=gmInput end')
    text='local C='+Frozen.lua(q)+'\nlocal choose=(function()\n'+POLICY+'\nend)()\n'+body
    Frozen.LuaRuntime().compile(text)
    assert not any(v in text for v in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key='mr_gimmick'):
    q=bindings(raw,key)
    return dict(ROM_SHA256=q['sha'],identity=key,compiled_menu={k:q[k]for k in('name','slot','owner','variant','cycle')},
        controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),policy_SHA256=sha256(POLICY.encode()).hexdigest(),
        exact_typed_current_input=True,normal_controls_only=True,genuine_star_support_witness=True,
        full_nonshortcut1_1_then25grounded1_2=True,gameplay_seeds=0,outputs=0,Mesen_run=False)
