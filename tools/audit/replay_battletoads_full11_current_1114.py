"""Current Rash/Zitz ordinary-controller stage discovery; no ROM/file writes."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json

import replay_ryan_full11_current_1114 as Parent

R,ROM,W,N=Parent.R,Parent.ROM,Parent.W,Parent.N
PIN=Parent.PIN
IDENTITIES={'rash':('RASH',0,0),'zitz':('ZITZ',1,32)}


def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new,1)


@lru_cache(maxsize=2)
def normalize(raw):
    assert sha256(raw).hexdigest()==PIN
    return Parent.normalize(raw)


@lru_cache(maxsize=4)
def bindings(raw,key):
    normalize(raw);name,cycle,variant=IDENTITIES[key]
    q=deepcopy(Parent.bindings(raw));b=dict(W.Symbols.bundle(),raw=raw)
    m=W.UI.seed(b,0)
    for pad in(2,4,4):W.UI.key(m,pad)
    for _ in range(cycle):W.UI.key(m,32)
    assert (W.UI.menu_name(m)[0],N.get(m,'SelectedCharacter'),N.get(m,'CrossoverMenuIndex'))==(name,33,23)
    assert N.get(m,'FmGroups')==64+variant
    q.update(key=key,name=name,owner=33,slot=23,variant=variant,cycle=cycle,navigation=[2,4,4]+[32]*cycle)
    for field in('FmGroups','SavedJoypadBits','BtHostReady','BtVariant','BtLife','BtSrc_Objects_Life',
                  'BtSrc_Objects_death_timer','BtSrc_FrameCounter','BtSrc_FrameCounter_Even',
                  'BtSrc_player1_obj_wanted_frame'):
        q['ram'][field]=W.address(b,field)
    pc=W.address(b,'BtCoreStep')
    assert 0xa000<=pc<0xc000
    q['private_hook']=dict(pc=pc,offset=3*8192+(pc&8191),bank=3)
    return q


@lru_cache(maxsize=4)
def controller(raw,key):
    q=bindings(raw,key)
    assert sha256(Parent.Frozen.TEMPLATE.read_bytes()).hexdigest()==Parent.Frozen.ROUTE_PINS[Parent.Frozen.TEMPLATE]
    assert sha256(Parent.BASE.read_bytes()).hexdigest()==Parent.BASE_SHA
    policy=Parent.BASE.read_text();body=Parent.Frozen.TEMPLATE.read_text()
    body=once(body,"local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end",
        "local function r(n,i)local at=assert(C.ram[n],n)+(i or 0);if n:sub(1,2)=='Bt'then return emu.read(3*8192+(at&8191),emu.memType.nesWorkRam)end;return emu.read(at,emu.memType.nesDebug)end")
    body=once(body,"r('SelectedCharacter')==0 and r('MarioVariant')==C.variant",
        "r('SelectedCharacter')==33 and (r('FmGroups')&32)==C.variant")
    body=body.replace("variant=r('MarioVariant')","variant=r('BtVariant')")
    body=once(body,'MarioVariant=C.variant','BtVariant=C.variant')
    body=once(body,"power=r('PlayerStatus'),lives=r('NumberofLives')",
        "power=r('PlayerStatus'),source_HP=r('BtSrc_Objects_Life'),source_death_timer=r('BtSrc_Objects_death_timer'),source_pose=r('BtSrc_player1_obj_wanted_frame'),source_ready=r('BtHostReady'),lives=r('NumberofLives')")
    body=once(body,'local function finish(reason)',
        'local btMoves,btNext,btHeld,btDirty,btMin=0,0,0,false,255\nlocal btInput,btDecide={},nil\nlocal function finish(reason)')
    body=once(body,'full_nonshortcut1_1=not not(flag and castle and entrance),game_state_writes=false',
        'Bt_source_steps=btMoves,Bt_1_2_steps=btNext,minimum_source_HP=btMin,private_state_read="physicalRAM3",full_nonshortcut1_1=not not(flag and castle and entrance),game_state_writes=false')
    body=once(body,"hook('GameLoop',function()", """emu.addMemoryCallback(guard(function()
 local h=C.private_hook;local a=emu.convertAddress(h.pc)
 if not a or a.memType~=emu.memType.nesWorkRam or a.address~=h.offset then return end
 if first and active()and identity()then
  assert(r('BtHostReady')==1 and r('BtVariant')==C.variant,'Actual private RAM3 source identity')
  btMoves=btMoves+1;if r('LevelNumber')==1 then btNext=btNext+1 end
  btHeld=r('SavedJoypadBits');btDirty=true
 end
end),emu.callbackType.exec,C.private_hook.pc)
hook('GameLoop',function()""")
    point=' pendingReturn=nil;updates=updates+1'
    body=once(body,point,point+"""
 if first and active()and identity()then btMin=math.min(btMin,r('BtSrc_Objects_Life'))end
 if not(active()and identity())then btInput={}end
 if btDirty then btDirty=false;if btDecide then btDecide()end end""")
    body=once(body,"and nextUpdates==25 and identity()and r('NumberofLives')==2",
        "and nextUpdates==25 and identity()and r('NumberofLives')==2 and btMoves>0 and btNext>=25 and r('BtSrc_Objects_Life')~=255")
    body=once(body," for i=1,C.cycle do press('select');",
        " press('left');press('down');press('down')\n assert(r('CrossoverMenuIndex')==23 and r('SelectedCharacter')==33,'Actual Battletoads slot')\n for i=1,C.cycle do press('select');")
    body=once(body,'frame=frame,poll=polls,char=0','frame=btMoves,poll=btMoves,char=33')
    body=once(body,'lastA=lastA,grounded=',"lastA=(btHeld&128)~=0,grounded=")
    start=body.index("local stairPhase,stairAge='approach',0")
    end=body.index('emu.addEventCallback(guard(function()\n polls=polls+1',start)
    body=body[:start]+"""btDecide=function()
 if menuDone and active()and identity()and r('LevelNumber')==0 then btInput=choose(context())else btInput={}end
end
"""+body[end:]
    body=once(body,"if menuDone then b=active()and r('LevelNumber')==0 and controls(context())or{}end",'if menuDone then b=btInput end')
    body=once(body,"assert(identity()and r('NumberofLives')==2 and r('AreaType')==1 and r('AreaAddrsLOffset')==5,'Genuine initial1-1')",
        "assert(identity()and r('NumberofLives')==2 and r('AreaType')==1 and r('AreaAddrsLOffset')==5 and r('BtHostReady')==1 and r('BtVariant')==C.variant and r('BtSrc_Objects_Life')==47,'Genuine initial Battletoads constructor')")
    text='local C='+Parent.Frozen.lua(q)+"\nlocal ROSTER_CONFIG={name="+json.dumps(key)+"}\nlocal choose=(function()\n"+policy+'\nend)()\n'+body
    Parent.Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key):
    q=bindings(raw,key)
    return dict(ROM_SHA256=PIN,identity=key,compiled_menu={k:q[k]for k in('name','owner','slot','variant','cycle')},
        controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        physical_private_RAM3_reads=True,normal_controls_only=True,gameplay_seeds=0,outputs=0,Mesen_run=False)
