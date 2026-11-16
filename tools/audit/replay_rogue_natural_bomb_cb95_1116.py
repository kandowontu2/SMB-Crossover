"""Genuine frozen MF then authored1-2 D0 Bomb and actual bomb lifecycle; no writes."""
from functools import lru_cache
from pathlib import Path
from copy import deepcopy
import re
import current_rogue_missile_cb95_1116 as J
import replay_rogue_full11_current_1114 as Retained
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,H,W,N,Frames,PIN=J.R,J.ROM,J.H,J.W,J.N,J.Frames,J.PIN
SOURCE=R/'tools/playthroughs/rogue_natural_bomb_cb95_1116.lua'


def once(s,a,z):assert s.count(a)==1,(a,s.count(a));return s.replace(a,z,1)


@lru_cache(maxsize=1)
def pack(raw):
    b=J.bindings(raw)['bundle'];ref=J.reference(raw);frozen=J.Previous.mf_controller(ref)
    assert frozen.count(J.Previous.PIN)==1
    old=frozen.replace(J.Previous.PIN,PIN,1)
    assert H(old.encode())=='bbe7d0a842ac80de17e2f07345935cc0f9cadfcec3699af87adcd1be6f5b4877'
    cfg=deepcopy(J.Previous.Frozen.bindings(J.Previous.C.inverse(ref)));cfg['sha']=PIN
    source=SOURCE.read_text();sources={};travel=Retained.route('rogue_dawn_11_v9.lua',sources)
    for name in set(re.findall(r"\br\('([^']+)'",source+travel))|{'RdWAction','RdWX','RdWY','RdWHi','RdWAge','RdWFrame','RdSlot','RdBombTerrainPhase'}:cfg['ram'][name]=W.address(b,name)
    for name in('RdControlDispatch','RdBombAllocate','RdBombStepBegin','RdBombStepFinish','RdWxBombTerrain'):
        at=W.location(b,name);cfg['hooks'][name]=dict(PC=W.address(b,name),offset=at-16,bytes=list(raw[at:at+16]))
    text=old;edits=[]
    def edit(a,z):
        nonlocal text
        text=once(text,a,z);edits.append((a,z))
    oldline=old.split('\n',1)[0];newline='local C='+J.Previous.Frozen.lua(cfg)
    edit(oldline,newline)
    edit('local function finish(reason)',"local gear={started=false,phase='travel',events={},states={},terrain={}}\nlocal function finish(reason)")
    edit("reason=='natural-tank-missile-credit-and25workers'and #completed==1", "reason=='natural-Bomb-and-lifecycle25'and gear.complete and #completed==2")
    edit('and collector and credit and born and mature and not reset',
         'and collector and gear.acquisition and gear.acquisition.credit and born and mature and not reset')
    edit('completed_tank_gate=completed[1],stock_phase=stock,','completed_tank_gate=completed[1],completed_missile_gate=completed[2],natural_Bomb=gear,stock_phase=stock,')
    edit('local function afterMain()',source+'\nlocal function afterMain()')
    edit("r('WorldNumber')==0 and r('LevelNumber')==0 and r('NumberofLives')==2", "r('WorldNumber')==0 and(r('LevelNumber')==0 or(gear.started and r('LevelNumber')==1))and r('NumberofLives')==2")
    edit('if a.flag>0 and a.id==46 then','if a.flag>0 and a.id==46 and(not gear.started or(a.private==208 and a.owner==2))then')
    edit("(tank and 216 or 217)","(tank and 216 or(gear.started and 208 or 217))")
    edit("assert(r('RdGear')==0 and not reset,'Original gear and source lifecycle')", "assert(r('RdGear')==(stock=='bomb-credit'and 1 or 0)and not reset,'Original gear and source lifecycle')")
    edit("else finish('natural-tank-missile-credit-and25workers');return end", """elseif stock=='missile-credit'then
    completed[2]={birth=born,mature=mature,collector=collector,credit=credit,terminal=state()}
    gear.started=true;gear.phase='travel';stock='bomb';born=nil;mature=nil;collector=nil;credit=nil
   else
    gear.acquisition={birth=born,mature=mature,collector=collector,credit=credit,terminal=state()}
    gear.phase='morph';stock='bomb-earned';credit=nil
   end""")
    edit('buttons=choose(context(),stock,items)',"if gear.started then buttons=bombDrive()else buttons=choose(context(),stock,items)end")
    edit("assert(updates<3600,'Bounded ordinary tank-to-missile route')", "assert(updates<8500,'Bounded ordinary MF to natural Bomb route')")
    edit("local p={name=n,pc=ret,sp=(sp+2)&255,kind=kind,at=at,A=c['cpu.a']}", """local p={name=n,pc=ret,sp=(sp+2)&255,kind=kind,at=at,A=c['cpu.a']}
 if n=='RdBombAllocate'then p.before=state();p.bombs={};for _,i in ipairs({0xd0,0xe0,0xf0})do p.bombs[i]=r('RdWAction',i)end end
 if n=='RdBombStepBegin'or n=='RdBombStepFinish'then p.weapon_slot=r('RdSlot')end""")
    edit("elseif n=='RdHsCollectActor'then", "elseif n=='RdBombAllocate'or n=='RdBombStepBegin'or n=='RdBombStepFinish'then bombReturned(n,p)\n  elseif n=='RdHsCollectActor'then")
    edit("(stock=='tank'and 8 or 9)","(stock=='tank'and 8 or(stock=='bomb'and 0 or 9))")
    edit("and r('RdMissiles')==5 and r('RdMaxMissiles')==5,'Real missile reward without HP refill'", "and r('RdMissiles')==5 and r('RdMaxMissiles')==5 and r('RdGear')==(stock=='bomb'and 1 or 0),'Real missile/Bomb reward without HP refill'")
    edit("'GameLoop','RdControlStep','RdLifeMovement','HandlePowerUpCollision'", "'GameLoop','RdControlStep','RdControlDispatch','RdLifeMovement','RdBombAllocate','RdBombStepBegin','RdBombStepFinish','HandlePowerUpCollision'")
    edit("(a.private==216 or a.private==217)","(a.private==216 or a.private==217 or a.private==208)")
    edit('local function written(address,value)', """local function written(address,value)
 if gear.started and address==C.ram.RdSfx+3 and(value&1)~=0 and not gear.place_request then gear.place_request={Main=updates,PC=cpu()['cpu.pc'],old=r('RdSfx',3),new=value}end
 if gear.bomb and address==C.ram.RdSfx and(value&16)~=0 and not gear.explode_request then gear.explode_request={Main=updates,PC=cpu()['cpu.pc'],old=r('RdSfx'),new=value}end""")
    edit("for _,name in ipairs({'Square2SoundQueue','RdTanks','PlayerStatus'})do", "for _,name in ipairs({'Square2SoundQueue','RdTanks','PlayerStatus','RdSfx'})do")
    edit("emu.addMemoryCallback(guard(written),emu.callbackType.write,C.ram.RdSfx+4)", "emu.addMemoryCallback(guard(written),emu.callbackType.write,C.ram.RdSfx+4)\nemu.addMemoryCallback(guard(written),emu.callbackType.write,C.ram.RdSfx+3)")
    edit('local age=0',"hook('RdWxBombTerrain',function()if gear.bomb and r('RdSlot')==gear.slot then local p=r('RdBombTerrainPhase');gear.terrain[p]=(gear.terrain[p]or 0)+1 end end)\nlocal age=0")
    edit('if frame>=12000 then', 'if frame>=22000 then')
    restored=text
    for a,z in reversed(edits):restored=once(restored,z,a)
    assert restored==old
    # A separate retained route function has fresh Lua control state; game arena is unchanged.
    text=text.replace('local choose=(function()', 'local gearTravel=(function()\nlocal ROSTER_CONFIG={rogue_tile_attributes={'+','.join(map(str,raw[W.location(b,'MTileAttribute'):W.location(b,'MTileAttribute')+256]))+'}}\n'+travel+'\nend)()\nlocal choose=(function()',1)
    LuaRuntime().compile(text)
    assert not any(t in text for t in('emu.write','emu.setState','takeScreenshot','io.open','dofile','saveState','loadState'))
    return text,dict(owning_SHA256=PIN,factory_SHA256=H(Path(__file__).read_bytes()),controller_SHA256=H(text.encode()),
        prefix_MF_Lua_SHA256=H(old.encode()),prefix_all_controls_and_assertions_exact_until_MF_endpoint=True,
        explicit_edits_reverse_to_frozen_MF=True,continuation_source_SHA256=H(SOURCE.read_bytes()),travel_sources=sources,
        authored1_2_cache_source_receipt='e1221d5c93aa2ee44f0dcd0d230aa61c21eaa28a680aa5c36367936c71a63d2d',
        game_changes=0,seeds=0,images=0,outputs=0,native=False)


def controller(raw):return pack(raw)[0]
def metadata(raw):return pack(raw)[1]
