"""Explicit exact82/1daca Ryan full-stage controller; no files or emulator."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

import compose_dk_private_sprite_window7_1114 as DK
import replay_smb1_alts_full11_1114 as Frozen

R,ROM,W,N=Frozen.R,Frozen.ROM,Frozen.W,Frozen.N
PIN=DK.CANDIDATE
IDENTITIES={'ryan':('RYAN',1,1)}
POLICY=R/'tools/playthroughs/river_city_11_v1.lua'
BASE=R/'tools/playthroughs/full_roster_policy_og.lua'
POLICY_SHA='a4c0577fe74cf24d5044c2051e6ef73eb92b2685d97e561d31014d866faffbec'
BASE_SHA='17d3a38d53fe09b930048f081938bf707028f765577207bce41777ea4f5edb7b'


def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new,1)


@lru_cache(maxsize=2)
def owning82(raw):
    pin=sha256(raw).hexdigest()
    if pin==DK.CANDIDATE:return DK.inverse(raw)
    assert pin==DK.PIN,'Expected explicit exact1daca or exact82ec model input'
    assert DK.Common.proposal(DK.Common.inverse(raw))[0]==raw
    return raw


@lru_cache(maxsize=2)
def normalize(raw):return Frozen.normalize(DK.Common.inverse(owning82(raw)))


@lru_cache(maxsize=2)
def bindings(raw,key='ryan'):
    assert key=='ryan';normalized=normalize(raw)
    legacy=DK.Common.inverse(owning82(raw));q=deepcopy(Frozen.bindings(legacy,'peach'))
    b=dict(W.Symbols.bundle(),raw=raw);m=W.UI.seed(b,0)
    navigation=[4,4,1,1,1,1,32]
    for pad in navigation:W.UI.key(m,pad)
    assert W.UI.menu_name(m)[0]=='RYAN'and N.get(m,'CrossoverMenuIndex')==20
    assert N.get(m,'SelectedCharacter')==21 and N.get(m,'RcVariant')==1
    q.update(sha=sha256(raw).hexdigest(),key=key,name='RYAN',owner=21,slot=20,variant=1,cycle=1,navigation=navigation)
    for name in('RcVariant','RcHealth','RcTier','RcMarker','RcLife','RcArea','RcWorld','RcSavedVariant',
        'RcClock','RcHeld','RcPrevious','RcRun','RcPose','RcAttack','RcAttackKind','RcHurt','RcCarrySlot','PowerUpType',
        'Enemy_Y_HighPos','GuestPowerupActive','GuestPowerupAge','X5WideChrActive','CurrentCHRBank','HpActorOwner','PlatformCollisionFlag'):
        q['ram'][name]=W.address(b,name)
    name='PositionPlayerOnHPlat';at=W.location(b,name)
    q['hooks'][name]=dict(pc=W.address(b,name),offset=at-16,bytes=list(raw[at:at+8]),bank=(at-16)//8192)
    for name,h in q['hooks'].items():
        at=16+h['offset'];assert raw[at:at+len(h['bytes'])]==bytes(h['bytes']),name
        if'bank'in h:
            at=16+h['bank']*8192;h['bank_SHA256']=sha256(raw[at:at+8192]).hexdigest()
    return q


@lru_cache(maxsize=2)
def controller(raw,key='ryan'):
    q=bindings(raw,key);legacy=DK.Common.inverse(owning82(raw));original=Frozen.controller(legacy,'peach')
    assert sha256(original.encode()).hexdigest()=='7057409ee03b52b0cd58394164e715521279772884ebae5488a47522b5124744'
    assert sha256(POLICY.read_bytes()).hexdigest()==POLICY_SHA and sha256(BASE.read_bytes()).hexdigest()==BASE_SHA
    prefix="local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))\n"
    policy=once(POLICY.read_text(),prefix,'')
    policy=once(policy,"local travel=assert(dofile(root..'/tools/playthroughs/full_roster_policy_og.lua'))",
        'local travel=(function()\n'+BASE.read_text()+'\nend)()')
    marker='-- Normal controller inputs and readonly native witnesses. No game-state writes.'
    body=marker+original.split(marker,1)[1]
    body=once(body,"r('SelectedCharacter')==0 and r('MarioVariant')==C.variant","r('SelectedCharacter')==21 and r('RcVariant')==C.variant")
    assert body.count("variant=r('MarioVariant')")==2
    body=body.replace("variant=r('MarioVariant')","variant=r('RcVariant')")
    body=once(body,'MarioVariant=C.variant','RcVariant=C.variant')
    body=once(body,"power=r('PlayerStatus'),lives=r('NumberofLives')",
        "power=r('PlayerStatus'),source_HP=r('RcHealth',1),source_tier=r('RcTier',1),source_clock=r('RcClock'),source_pose=r('RcPose'),world_modes={r('X5ChrMode',1),r('X5ChrMode',2),r('X5ChrMode',3)},world_CHR={r('CurrentCHRBank',1),r('CurrentCHRBank',2),r('CurrentCHRBank',3)},lives=r('NumberofLives')")
    body=once(body,'frame=frame,poll=polls,char=0','frame=rcMoves,poll=rcMoves,char=21')
    body=once(body,'lastA=lastA,grounded=',"lastA=(r('RcHeld')&128)~=0,grounded=")
    body=once(body," for i=1,C.cycle do press('select');", " press('down');press('down');press('right');press('right');press('right');press('right')\n assert(r('CrossoverMenuIndex')==20 and r('SelectedCharacter')==21 and r('RcVariant')==0,'Actual Alex slot before Select')\n for i=1,C.cycle do press('select');")
    body=once(body,'local function finish(reason)','local rcInput,rcDecide={},nil\nlocal rcMoves,rcNext,rcMin,rcLast,rcScene=0,0,255,nil,nil\nlocal helperCalls,helperFirst=0,nil\nlocal function finish(reason)')
    body=once(body,"hook('GameLoop',function()", """hook('PositionPlayerOnHPlat',function()
 if not first or not identity()or r('WorldNumber')~=0 or r('LevelNumber')~=0 then return end
 local slot=emu.getState()['cpu.x']
 if slot<6 and r('HpActorOwner',slot)>0 and r('Enemy_Flag',slot)==1 and r('Enemy_ID',slot)==40 then
  helperCalls=helperCalls+1
  helperFirst=helperFirst or{slot=slot,x=pos('Enemy_X_Position','Enemy_PageLoc',slot),y=r('Enemy_Y_Position',slot),player=state(),collision=r('PlatformCollisionFlag',slot)}
 end
end)
hook('GameLoop',function()""")
    point=' pendingReturn=nil;updates=updates+1'
    body=once(body,point,point+"""
 if not(active()and identity())then rcInput={}end
 if first and active()and identity()then
  rcMin=math.min(rcMin,r('RcHealth',1))
  local clock=r('RcClock')
  local scene=r('WorldNumber')..'/'..r('LevelNumber')..'/'..r('AreaType')..'/'..r('AreaAddrsLOffset')
  if rcScene~=scene then rcScene=scene;rcLast=clock end
  if rcLast==nil or clock~=rcLast then
   if rcLast~=nil then assert((clock-rcLast)&255==1,'Actual RCR movement clock advanced once')end
   rcLast=clock;rcMoves=rcMoves+1
   if r('LevelNumber')==1 then rcNext=rcNext+1 end
   if rcDecide then rcDecide()end
  end
 end""")
    body=once(body,"and nextUpdates==25 and identity()and r('NumberofLives')==2",
        "and nextUpdates==25 and identity()and r('NumberofLives')==2 and rcMoves>0 and rcNext>=25 and r('RcHealth',1)>0")
    body=once(body,'full_nonshortcut1_1=not not(flag and castle and entrance),game_state_writes=false',
        'Rc_movement_clock_advances=rcMoves,Rc_1_2_clock_advances=rcNext,minimum_source_HP=rcMin,existing_helper_HPlat_calls=helperCalls,existing_helper_first=helperFirst,existing_helper_authored={stage="1-1",center_x=3104,left_x=3096,initial_top=64,width=16},navigation_clock="completed Main snapshots with actual RcClock advance",full_nonshortcut1_1=not not(flag and castle and entrance),game_state_writes=false')
    body=once(body,"assert(identity()and r('NumberofLives')==2 and r('AreaType')==1 and r('AreaAddrsLOffset')==5,'Genuine initial1-1')",
        "assert(identity()and r('NumberofLives')==2 and r('AreaType')==1 and r('AreaAddrsLOffset')==5 and r('RcMarker')==199 and r('RcHealth',1)==48 and r('RcTier',1)==0,'Genuine current Ryan constructor and initial1-1')")
    start=body.index("local stairPhase,stairAge='approach',0")
    end=body.index('emu.addEventCallback(guard(function()\n polls=polls+1',start)
    body=body[:start]+"""local function controls(c)return choose(c)end
rcDecide=function()
 if menuDone and active()and identity()and r('LevelNumber')==0 then rcInput=controls(context())else rcInput={}end
end
"""+body[end:]
    body=once(body,"if menuDone then b=active()and r('LevelNumber')==0 and controls(context())or{}end",'if menuDone then b=rcInput end')
    text='local C='+Frozen.lua(q)+"\nlocal ROSTER_CONFIG={name='ryan'}\nlocal choose=(function()\n"+policy+'\nend)()\n'+body
    Frozen.LuaRuntime().compile(text)
    assert not any(v in text for v in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key='ryan'):
    q=bindings(raw,key)
    return dict(ROM_SHA256=q['sha'],identity=key,compiled_menu={k:q[k]for k in('name','slot','owner','variant','cycle')},
        controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),policy_SHA256=POLICY_SHA,base_policy_SHA256=BASE_SHA,
        normalization='explicit1daca→portableDKinverse→82→commoninverse→421 normalization'if q['sha']==PIN else'explicit82 model preparation→commoninverse→421 normalization',
        source_HP_and_real_RcClock_required=True,full_nonshortcut1_1_then25grounded1_2=True,
        navigation_clock='completed Main snapshots, gated on actual source RcClock advance',
        normal_controls_only=True,gameplay_seeds=0,outputs=0,Mesen_run=False)


if __name__=='__main__':print(json.dumps(metadata(ROM.read_bytes()),separators=(',',':')),flush=True)
