"""Exact delivered cf7 classic-DK full1-1 ordinary controller, no outputs."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256

import current_dk_gameplay_input_1114 as Input
import replay_smb1_alts_full11_1114 as Base

R,ROM,W,N,PIN=Input.R,Input.ROM,Input.W,Input.N,Input.PIN
IDENTITIES=Input.IDENTITIES
Frozen=Base
POLICY=R/'tools/playthroughs/dk_full11_controls_1114.lua'


def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new,1)


normalize=Input.Frozen.normalize


@lru_cache(maxsize=1)
def bindings(raw,key='donkey_kong'):
    q=deepcopy(Input.bindings(raw,key));q.update(variant=0,cycle=0)
    b=dict(W.Symbols.bundle(),raw=raw)
    for name in('DkReady','DkTier','DkPrevious','A_B_Buttons','SavedJoypadBits'):
        q['ram'][name]=W.address(b,name)
    name='DkMovement';at=W.location(b,name)
    q['hooks'][name]=dict(pc=W.address(b,name),offset=at-16,bytes=list(raw[at:at+8]),bank=(at-16)//8192)
    for h in q['hooks'].values():
        if'bank'in h:
            at=16+h['bank']*8192;h['bank_SHA256']=sha256(raw[at:at+8192]).hexdigest()
    return q


@lru_cache(maxsize=1)
def controller(raw,key='donkey_kong'):
    q=bindings(raw,key)
    assert sha256(Base.TEMPLATE.read_bytes()).hexdigest()==Base.ROUTE_PINS[Base.TEMPLATE]
    body=Base.TEMPLATE.read_text()
    body=once(body,"r('SelectedCharacter')==0 and r('MarioVariant')==C.variant",
        "r('SelectedCharacter')==28 and r('DkReady')==68 and r('DkTier')<=2")
    body=once(body,"lives=r('NumberofLives'),variant=r('MarioVariant'),chr_mode=",
        "lives=r('NumberofLives'),tier=r('DkTier'),chr_mode=")
    body=once(body,'local function finish(reason)',
        'local dkMoves,dkLast,dkNext=0,0,0\nlocal dkInput,dkDecide={},nil\nlocal dkMainMoved=false\nlocal function finish(reason)')
    body=once(body,"and nextUpdates==25 and identity()and r('NumberofLives')==2",
        "and nextUpdates==25 and identity()and r('NumberofLives')==2 and dkMoves>0 and dkNext>=25")
    body=once(body,'full_nonshortcut1_1=not not(flag and castle and entrance),game_state_writes=false',
        'actual_DkMovement_calls=dkMoves,actual_DkMovement_calls_in_1_2=dkNext,navigation_clock="completed Main snapshots after actual DK movement",full_nonshortcut1_1=not not(flag and castle and entrance),game_state_writes=false')
    body=once(body,"hook('GameLoop',function()", """hook('DkMovement',function()
 if active()and identity()then dkMoves=dkMoves+1 end
end)
hook('GameLoop',function()""")
    body=once(body,' pendingReturn=nil;updates=updates+1',""" pendingReturn=nil;updates=updates+1
 dkMainMoved=dkMoves~=dkLast
 if dkMainMoved then
  assert(dkMoves==dkLast+1,'Exactly one DK movement per completed active Main')
  dkLast=dkMoves
  if r('WorldNumber')==0 and r('LevelNumber')==1 and active()then dkNext=dkNext+1 end
  if dkDecide then dkDecide()end
 end""")
    body=once(body,"if r('AreaType')==2 and r('Player_State')==0 and r('Player_Y_HighPos')==1 and r('Player_Y_Position')<224 then",
        "if dkMainMoved and r('AreaType')==2 and r('Player_State')==0 and r('Player_Y_HighPos')==1 and r('Player_Y_Position')==176 and pos('Player_X_Position','Player_PageLoc')==40 then")
    old=" for i=1,C.cycle do press('select');menuEvents[i]={frame=frame,variant=r('MarioVariant'),raw=r('SelectedCharacter')}end"
    body=once(body,old,""" for i=1,3 do press('down')end
 for i=1,3 do press('right')end
 assert(r('CrossoverMenuIndex')==27 and r('SelectedCharacter')==28,'Actual classic DK slot')""")
    # Before Start the active constructor has not yet set DkReady.
    body=once(body,"assert(identity(),'Actual compiled alternate cycle')",
        "assert(r('SelectedCharacter')==28,'Actual compiled classic DK menu identity')")
    body=once(body,'frame=frame,poll=polls,char=0', 'frame=dkMoves,poll=dkMoves,char=28')
    body=once(body,'lastA=lastA,grounded=',"lastA=(r('PreviousA_B_Buttons')&128)~=0,grounded=")
    begin=body.index("local stairPhase,stairAge='approach',0")
    end=body.index('emu.addEventCallback(guard(function()\n polls=polls+1',begin)
    body=body[:begin]+"""local function controls(c)return choose(c)end
dkDecide=function()
 if menuDone and active()and identity()and r('LevelNumber')==0 then dkInput=controls(context())else dkInput={}end
end
"""+body[end:]
    body=once(body,"if menuDone then b=active()and r('LevelNumber')==0 and controls(context())or{}end",
        'if menuDone then b=dkInput end')
    body=once(body," if not first and active()and r('WorldNumber')==0 and r('LevelNumber')==0 then",
        " if pendingReturn then return end\n if not first and active()and r('WorldNumber')==0 and r('LevelNumber')==0 then")
    body=once(body,"assert(identity()and r('NumberofLives')==2 and r('AreaType')==1 and r('AreaAddrsLOffset')==5,'Genuine initial1-1')",
        "assert(identity()and r('NumberofLives')==2 and r('AreaType')==1 and r('AreaAddrsLOffset')==5 and r('DkTier')==0,'Genuine classic DK constructor and initial1-1')")
    text='local C='+Base.lua(q)+'\nlocal choose=(function()\n'+POLICY.read_text()+'\nend)()\n'+body
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key='donkey_kong'):
    q=bindings(raw,key)
    return dict(ROM_SHA256=PIN,identity=key,controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        policy_SHA256=sha256(POLICY.read_bytes()).hexdigest(),typed_input=Input.KIND,
        compiled_menu={k:q[k]for k in('name','slot','owner','cycle')},
        navigation_clock='actual DkMovement entry followed by authenticated Main return; cached buttons at input poll',
        full_nonshortcut1_1_then25_actual_living_grounded1_2=True,normal_controls_only=True,
        gameplay_seeds=0,ROM_changes=0,outputs=0,Mesen_run=False)
