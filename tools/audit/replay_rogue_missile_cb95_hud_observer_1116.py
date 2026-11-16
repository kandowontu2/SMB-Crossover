"""Passive terminal HUD/queue diagnostic over exact qualified cb95 missile body."""
from functools import lru_cache
from pathlib import Path
import replay_rogue_missile_cb95_1116 as F
from check_ff_stdout_controller_source_1110 import LuaRuntime

J,R,ROM,H,W,N,Frames,PIN=F.J,F.R,F.ROM,F.H,F.W,F.N,F.Frames,F.PIN
BASE_SHA='723f56157c1fa5602ef4a68fc248979109f36bc1adbc48a5468f23af8e0b502a'
RAM=('InvHudAmmo','InvHudName','InvDirty','InvHudActive','VRAM_Buffer1','VRAM_Buffer1_Offset','VRAM_Buffer2',
 'VRAM_Buffer2_Offset','VRAM_Buffer_AddrCtrl','GamePauseStatus','DisableScreenFlag','ReloadCHRBank','RdColorRequest',
 'SmFreezePalettePending','StarInvincibleTimer','GuestPowerupActive','PlayerChangeSizeFlag','AreaParserTaskNum','ScrollThirtyTwo')


def once(s,a,z):assert s.count(a)==1,(a,s.count(a));return s.replace(a,z,1)


@lru_cache(maxsize=1)
def pack(raw):
    assert H(Path(F.__file__).read_bytes())==BASE_SHA
    b=J.bindings(raw)['bundle'];old=F.controller(raw,'missile');edits=[];text=old
    def edit(a,z):
        nonlocal text
        text=once(text,a,z);edits.append((a,z))
    definitions=[]
    for n in RAM:definitions.append('C.ram['+F.Attack.J.Frozen.lua(n)+']='+str(W.address(b,n)))
    for n in('RdUiEarly','RdUiHud'):
        at=W.location(b,n)
        definitions.append('C.hooks['+F.Attack.J.Frozen.lua(n)+']='+F.Attack.J.Frozen.lua(dict(PC=W.address(b,n),offset=at-16,bytes=list(raw[at:at+16]))))
    definitions.append('C.hudEarlyEnd='+str(W.address(b,'RdUiName')))
    start=old.index('\n');edit(old[:start],old[:start]+'\n'+'\n'.join(definitions))
    functions='''local hud={attempts=0,early=0,eligible=0,reasons={},retractions=0,packet_commits=0,ammo_cache_writes=0,witnesses={}}
local function hudValues()
 local v={};for _,n in ipairs({'InvHudAmmo','InvHudName','InvDirty','InvHudActive','VRAM_Buffer1_Offset','VRAM_Buffer2_Offset','VRAM_Buffer_AddrCtrl','GamePauseStatus','DisableScreenFlag','TimerControl','ReloadCHRBank','RdColorRequest','SmFreezePalettePending','StarInvincibleTimer','GuestPowerupActive','PlayerChangeSizeFlag','AreaParserTaskNum','ScrollThirtyTwo'})do v[n]=r(n)end
 v.health_cache={r('InvHudName'),r('InvHudName',1)};v.current_ammo=r('RdMissiles');v.max_ammo=r('RdMaxMissiles');v.raw_health={r('RdHealthLo'),r('RdHealthHi')}
 return v
end
local function hudWitness(name,extra)
 if #hud.witnesses>=4 then return end
 hud.witnesses[#hud.witnesses+1]={name=name,Main=updates,PC=cpu()['cpu.pc'],values=hudValues(),extra=extra}
end
local function hudAttempt()
 if not first or not identity()then return end;hud.attempts=hud.attempts+1
 local blocked=false
 local function reason(n,v)if v~=0 then blocked=true;hud.reasons[n]=(hud.reasons[n]or 0)+1 end end
 reason('OperMode_not1',r('OperMode')==1 and 0 or 1);reason('engine_not8',r('GameEngineSubroutine')==8 and 0 or 1)
 reason('pause',r('GamePauseStatus')&1)
 for _,n in ipairs({'DisableScreenFlag','TimerControl','VRAM_Buffer_AddrCtrl','VRAM_Buffer1_Offset','VRAM_Buffer2_Offset','VRAM_Buffer1','VRAM_Buffer2','ReloadCHRBank','RdColorRequest','SmFreezePalettePending','InvHudActive','StarInvincibleTimer','GuestPowerupActive','PlayerChangeSizeFlag','AreaParserTaskNum'})do reason(n,r(n))end
 reason('ScrollThirtyTwo_ge32',r('ScrollThirtyTwo')>=32 and 1 or 0)
 if not blocked then hud.eligible=hud.eligible+1 end
end
local function hudWrite(address,value)
 if not first or not identity()then return end
 local pc=cpu()['cpu.pc']
 if address==C.ram.VRAM_Buffer1_Offset and value==14 and r('VRAM_Buffer1')==0x20 and r('VRAM_Buffer1',1)==0x23 and r('VRAM_Buffer1',2)==11 and r('VRAM_Buffer1',3)==0x0e and r('VRAM_Buffer1',8)==0x16 and r('VRAM_Buffer1',14)==0 then
  hud.packet_commits=hud.packet_commits+1
  if not hud.first_packet then hud.first_packet=true;local p={};for i=0,14 do p[#p+1]=r('VRAM_Buffer1',i)end;hudWitness('firstHUDpacket14',p)end
 elseif address==C.ram.VRAM_Buffer1_Offset and value==0 and r('VRAM_Buffer1_Offset')==14 and pc>=C.hooks.RdUiEarly.PC and pc<C.hudEarlyEnd then
  hud.retractions=hud.retractions+1
  if not hud.first_retraction then hud.first_retraction=true;hudWitness('firstOwnEarlyRetraction',{old=14,new=0})end
 elseif address==C.ram.InvHudAmmo then
  hud.ammo_cache_writes=hud.ammo_cache_writes+1
  if value==4 and not hud.first_ammo4 then hud.first_ammo4=true;hudWitness('firstAmmoCache4',{old=r('InvHudAmmo'),new=value})end
 end
end
local function hudTerminal()
 hud.terminal=hudValues();hud.terminal.queue={}
 for i=0,14 do hud.terminal.queue[#hud.terminal.queue+1]=r('VRAM_Buffer1',i)end
 assert(emu.memType.nesPpuDebug,'Actual NES PPU debug memory')
 hud.terminal.nametable2023={}
 for at=0x2023,0x202d do hud.terminal.nametable2023[#hud.terminal.nametable2023+1]=emu.read(at,emu.memType.nesPpuDebug)end
 return hud
end
'''
    edit('local function finish(reason)',functions+'\nlocal function finish(reason)')
    edit('pending_scopes=#pending,game_state_writes=false,outputs=0,Mesen_images=0}',
         'pending_scopes=#pending,game_state_writes=false,outputs=0,Mesen_images=0,hud_diagnostic=hudTerminal()}')
    install="""hook('RdUiEarly',function()if first and identity()then hud.early=hud.early+1 end end)
hook('RdUiHud',hudAttempt)
for _,n in ipairs({'VRAM_Buffer1_Offset','InvHudAmmo'})do emu.addMemoryCallback(guard(hudWrite),emu.callbackType.write,C.ram[n])end
"""
    edit('local function context()',install+'\nlocal function context()')
    restored=text
    for a,z in reversed(edits):restored=once(restored,z,a)
    assert restored==old
    LuaRuntime().compile(text)
    lua=LuaRuntime(unpack_returned_tuples=True);registered={0:set(),1:set()};event_counts={0:0,1:0}
    api=lua.table();api.memType=lua.table_from(dict(nesDebug=0,nesWorkRam=1,nesPrgRom=2,nesPpuDebug=3))
    api.callbackType=lua.table_from(dict(exec=0,write=1));api.eventType=lua.table_from(dict(inputPolled=0,endFrame=1))
    def memory(fn,kind,lo,hi=None):registered[kind].update(range(lo,(hi if hi is not None else lo)+1))
    def event(fn,kind):event_counts[kind]+=1
    api.addMemoryCallback=memory;api.addEventCallback=event
    lua.globals().emu=api;lua.globals().CPU_CONTROLLER_OPENING=False;lua.execute(text)
    registration=dict(exec_addresses=len(registered[0]),write_addresses=len(registered[1]),events=event_counts)
    assert registration==dict(exec_addresses=22,write_addresses=14,events={0:1,1:1}),registration
    assert not any(t in text for t in('emu.write','emu.setState','takeScreenshot','io.open','dofile','saveState','loadState'))
    return text,dict(owning_SHA256=PIN,controller_SHA256=H(text.encode()),factory_SHA256=H(Path(__file__).read_bytes()),
        qualified_base_Lua_SHA256=H(old.encode()),exact_functional_restoration=True,diagnostic_only=True,
        executed_top_level_registration_no_game_CPU=registration,
        unchanged_controls_assertions_and_endpoint=True,aggregate_guards_and_maximum4_witnesses=True,
        terminal_PPU_bytes=11,terminal_queue_bytes=15,images=0,output_files=0,native=False)


def controller(raw):return pack(raw)[0]
def metadata(raw):return pack(raw)[1]


if __name__=='__main__':
    import json
    import explore_rogue_natural_bomb_cb95_1116 as Reader
    raw,_=Reader.load_current();print('RESULT '+json.dumps(metadata(raw),separators=(',',':')),flush=True)
