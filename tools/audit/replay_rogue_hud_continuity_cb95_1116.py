"""Passive area HUD continuity over exact qualified natural Bomb controls."""
from functools import lru_cache
from pathlib import Path
import json
import replay_rogue_natural_bomb_cb95_1116 as Base
from check_ff_stdout_controller_source_1110 import LuaRuntime

J,R,ROM,H,W,N,Frames,PIN=Base.J,Base.R,Base.ROM,Base.H,Base.W,Base.N,Base.Frames,Base.PIN
PARENT_SHA='5de4679e9d1726a81cfd08afe1d5fd5c953848832443041849fa5945b6fee1ac'
RAM=('InvHudAmmo','InvHudName','InvDirty','InvHudActive','VRAM_Buffer1','VRAM_Buffer1_Offset','VRAM_Buffer2','VRAM_Buffer2_Offset',
 'VRAM_Buffer_AddrCtrl','GamePauseStatus','DisableScreenFlag','ReloadCHRBank','RdColorRequest','SmFreezePalettePending',
 'StarInvincibleTimer','GuestPowerupActive','PlayerChangeSizeFlag','AreaParserTaskNum','ScrollThirtyTwo',
 'Mirror_PPUCTRL','IrqPPUCTRL','HorizontalScroll','VerticalScroll','ScreenLeft_PageLoc','ScreenLeft_X_Pos')


def once(s,a,z):assert s.count(a)==1,(a,s.count(a));return s.replace(a,z,1)


@lru_cache(maxsize=2)
def pack(raw,source=False):
    assert H(Path(Base.__file__).read_bytes())==PARENT_SHA
    old=Base.controller(raw);assert H(old.encode())=='3395fd00a8ffae0e8448850be7b5d299d2f3e67876da6de71625acf1bf15665b'
    b=J.bindings(raw)['bundle'];text=old;edits=[];lua=J.Previous.Frozen.lua
    defs=['C.hudSourceOnly='+('true'if source else'false')]
    for n in RAM:defs.append('C.ram['+lua(n)+']='+str(W.address(b,n)))
    for n in('RdUiEarly','RdUiHud','RdUiStatus','RdHsEnterScene'):
        at=W.location(b,n);defs.append('C.hooks['+lua(n)+']='+lua(dict(PC=W.address(b,n),offset=at-16,bytes=list(raw[at:at+16]))))
    def edit(a,z):
        nonlocal text
        text=once(text,a,z);edits.append((a,z))
    line=old.split('\n',1)[0];edit(line,line+'\n'+'\n'.join(defs))
    observer='''local hud={buckets={},markers={},markerKeys={},writes={}}
local function hudKey()return r('WorldNumber')..':'..r('LevelNumber')..':'..r('AreaPointer')end
local function hudBucket()
 local k=hudKey();if not hud.buckets[k]then hud.buckets[k]={early=0,attempts=0,eligible=0,cache_equal=0,packet_commits=0,dirty_writes=0,cache_writes=0,reasons={}}end
 return hud.buckets[k]
end
local function hudSnapshot(tag)
 local q={tag=tag,Main=updates,player=state(),world=r('WorldNumber'),level=r('LevelNumber'),area=r('AreaPointer'),
  cache={health_low=r('InvHudName'),health_high=r('InvHudName',1),ammo=r('InvHudAmmo'),dirty=r('InvDirty')},queue={}}
 q.mirrors={PPUCTRL=r('Mirror_PPUCTRL'),IrqPPUCTRL=r('IrqPPUCTRL'),horizontal=r('HorizontalScroll'),vertical=r('VerticalScroll'),camera=pos('ScreenLeft_X_Pos','ScreenLeft_PageLoc')}
 for i=0,14 do q.queue[#q.queue+1]=r('VRAM_Buffer1',i)end
 q.queue_offset=r('VRAM_Buffer1_Offset')
 if not C.hudSourceOnly then
  assert(emu.memType.nesPpuDebug,'Actual native PPU debug memory');q.NT2023={};q.NT2423={}
  for i=0,10 do q.NT2023[#q.NT2023+1]=emu.read(0x2023+i,emu.memType.nesPpuDebug);q.NT2423[#q.NT2423+1]=emu.read(0x2423+i,emu.memType.nesPpuDebug)end
 end
 return q
end
local function hudMark(tag)
 local k=tag..':'..hudKey();if hud.markerKeys[k]then return end;hud.markerKeys[k]=true
 assert(#hud.markers<10,'Bounded actual area HUD milestones');hud.markers[#hud.markers+1]=hudSnapshot(tag)
end
local function hudAttempt()
 if not first or not identity()then return end
 local b=hudBucket();b.attempts=b.attempts+1;local blocked=false
 local function reason(n,v)if v~=0 then blocked=true;b.reasons[n]=(b.reasons[n]or 0)+1 end end
 reason('mode_not1',r('OperMode')==1 and 0 or 1);reason('engine_not8',r('GameEngineSubroutine')==8 and 0 or 1);reason('pause',r('GamePauseStatus')&1)
 for _,n in ipairs({'DisableScreenFlag','TimerControl','VRAM_Buffer_AddrCtrl','VRAM_Buffer1_Offset','VRAM_Buffer2_Offset','VRAM_Buffer1','VRAM_Buffer2','ReloadCHRBank','RdColorRequest','SmFreezePalettePending','InvHudActive','StarInvincibleTimer','GuestPowerupActive','PlayerChangeSizeFlag','AreaParserTaskNum'})do reason(n,r(n))end
 reason('ScrollThirtyTwo_ge32',r('ScrollThirtyTwo')>=32 and 1 or 0)
 if not blocked then
  b.eligible=b.eligible+1
  if r('InvDirty')==0 and r('InvHudName',1)==r('RdHealthHi')and r('InvHudName')==(r('RdHealthLo')&240)and r('InvHudAmmo')==r('RdMissiles')then b.cache_equal=b.cache_equal+1 end
 end
 if r('LevelNumber')==0 and r('RdMissiles')==5 and r('InvHudAmmo')==5 and r('InvDirty')==0 then hudMark('earned-MF-cache5')end
end
local function hudAfterMain()
 if not first or not identity()then return end
 if r('LevelNumber')==1 and active()then hudMark('first-active1-2')end
end
local function hudWrite(at,value)
 if not first or not identity()then return end
 local b=hudBucket();local k
 if at==C.ram.InvDirty then b.dirty_writes=b.dirty_writes+1;k='dirty'
 elseif at==C.ram.InvHudAmmo or at==C.ram.InvHudName or at==C.ram.InvHudName+1 then b.cache_writes=b.cache_writes+1;k='cache'
 elseif at==C.ram.VRAM_Buffer1_Offset and value==14 and r('VRAM_Buffer1')==0x20 and r('VRAM_Buffer1',1)==0x23 and r('VRAM_Buffer1',2)==11 and r('VRAM_Buffer1',3)==14 and r('VRAM_Buffer1',8)==22 then b.packet_commits=b.packet_commits+1;k='packet14'end
 if k then local key=hudKey()..':'..k;if not hud.writes[key]then hud.writes[key]={Main=updates,PC=cpu()['cpu.pc'],old=emu.read(at,emu.memType.nesDebug),new=value}end end
end
local function hudTerminal()hud.terminal=hudSnapshot('terminal');hud.source_counter_only=C.hudSourceOnly;return hud end
'''
    edit('local function finish(reason)',observer+'\nlocal function finish(reason)')
    edit('Mesen_images=0}', 'Mesen_images=0,hud_continuity=hudTerminal()}')
    edit('local function context()', """hook('RdUiEarly',function()if first and identity()then local b=hudBucket();b.early=b.early+1 end end)
hook('RdUiHud',hudAttempt)
hook('RdUiStatus',function()if first and identity()and cpu()['cpu.a']==0 then hudMark('native-status0')end end)
hook('RdHsEnterScene',function()if first and identity()then hudMark('before-source-scene')end end)
for _,n in ipairs({'InvDirty','InvHudAmmo','VRAM_Buffer1_Offset'})do emu.addMemoryCallback(guard(hudWrite),emu.callbackType.write,C.ram[n])end
emu.addMemoryCallback(guard(hudWrite),emu.callbackType.write,C.ram.InvHudName,C.ram.InvHudName+1)
local function context()""")
    edit(' if not first then return end\n', ' if not first then return end\n hudAfterMain()\n')
    restored=text
    for a,z in reversed(edits):restored=once(restored,z,a)
    assert restored==old;LuaRuntime().compile(text)
    assert not any(t in text for t in('emu.write','emu.setState','takeScreenshot','io.open','dofile','saveState','loadState'))
    return text,dict(owning_SHA256=PIN,controller_SHA256=H(text.encode()),factory_SHA256=H(Path(__file__).read_bytes()),
        exact_functional_restoration_to3395=True,all_inputs_assertions_and_endpoint_unchanged=True,
        source_counter_only=source,native_PPU_rows=0 if source else 2,native_PPU_bytes_per_milestone=0 if source else 22,
        maximum_area_milestones=10,aggregate_per_area_counters=True,images=0,outputs=0,native=False)


def controller(raw,source=False):return pack(raw,source)[0]
def metadata(raw,source=False):return pack(raw,source)[1]


if __name__=='__main__':
    import inspect_rogue_missile_targets_cb95_1116 as Engine
    from unittest.mock import patch
    raw,provenance=Engine.Reader.load_current()
    def deny(*a,**kw):raise AssertionError('HUD continuity attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        text=controller(raw,source=True);q=Engine.run(raw,6000,text=text)
        result=dict(input=provenance,source_result=q,source_metadata=metadata(raw,True),native_metadata=metadata(raw,False),outputs=0,native=False)
    result['receipt_SHA256']=H(json.dumps(result,sort_keys=True,separators=(',',':')).encode());print('RESULT '+json.dumps(result,separators=(',',':')),flush=True)
