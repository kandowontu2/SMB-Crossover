"""Pure read-only DMC-alias observer over the frozen current Luigi route.

The factory returns Lua only. It never starts Mesen or writes a ROM, Lua,
capture or receipt file. The existing full-stage inputs and endpoint remain
byte-identical after removing this module's observation-only additions.
"""
from hashlib import sha256
import argparse
import json
from pathlib import Path
import re

import bub_native_noops_1113 as Bub
import compose_smb2_foreground_current_1113 as Current
import replay_smb2_variants_stage_1113 as Terrain

PIN = '3684f3d2a418a484befd80fca351d0dc5f9b472f6f067a0a7894994ea343679d'
BASE_SHA = 'a8e2c9a408daf9fb228c822ab85ccabb98eda00769922dfbec2be0337af47cc5'
LUA_SHA = 'b80d9992f21e4b9632de3a9b8abd4352270368f8394285deb226be0968d10e46'
NIGHTLY = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')


def base_controller(raw):
    """Authenticate the complete typed lineage, then rebind only the ROM pin."""
    assert sha256(raw).hexdigest() == PIN == Current.CANDIDATE
    public = Current.inverse(raw)
    assert sha256(public).hexdigest() == Current.PIN
    parent = Bub.combined_reverse(public)
    flag = Current.Flag.proposal(parent)[0]
    mirror = Current.Mirror.all_mirrors_proposal(flag)[0]
    priority = Current.Priority.proposal(mirror)[0]
    assert sha256(priority).hexdigest() == Terrain.FULL_PIN
    foreground = Current.Foreground.proposal(priority)[0]
    assert sha256(foreground).hexdigest() == Current.Foreground.CANDIDATE
    text = Terrain.profile_controller(priority, 1, full=True)
    assert sha256(text.encode()).hexdigest() == Terrain.FULL_SHA[1]
    assert text.count(Terrain.FULL_PIN) == 1
    text = text.replace(Terrain.FULL_PIN, Current.Foreground.CANDIDATE)
    assert text.count(Current.Foreground.CANDIDATE) == 1
    text = text.replace(Current.Foreground.CANDIDATE, PIN)
    assert BASE_SHA is not None and sha256(text.encode()).hexdigest() == BASE_SHA
    return text


def bindings(raw):
    assert sha256(raw).hexdigest() == PIN
    windows = []
    def window(name, bank, pc, data):
        at = bank * 8192 + (pc & 8191)
        assert raw[16+at:16+at+len(data)] == data, (name, bank, hex(pc))
        windows.append(dict(name=name, bank=bank, pc=pc, offset=at, data=data.hex()))
    # Both instructions are actual current source-owned writes, not inferred
    # from a callback's reported next PC. Also bind the original stop writer.
    window('sample_alias_select', 74, 0xbb93, bytes.fromhex('8d1751297f8d7e6f688d1540'))
    window('sample_start', 74, 0xbb9c, bytes.fromhex('8d154048682860'))
    window('sample_stop', 74, 0xbb78, bytes.fromhex('8d154048ad7e6f'))
    old = bytes.fromhex('8d6a01ad02604903d00d20a4ac0848a902203792682860ad6a018d6a01a9878d6c01a9bb8d6d01a9cf4c5a01')
    new = bytes.fromhex('8d6a01ad02604903d00d20a4ac0848a902203792682860ad6a018d6a01a9388d6c01a9b48d6d01a9c24c5a01')
    for bank in (119, 120, 125, 127):
        window('resident_bridge_'+str(bank), bank, 0xe5cc, old if bank < 121 else new)
    window('old_target_inside_name_loop', 79, 0xbb80, bytes.fromhex('b992bb99ba048810f768a8a90060'))
    window('current_hot_target', 66, 0xb438, bytes.fromhex('088d6a01ad0260c922f037c90ad019ad'))
    b = dict(Terrain.W.Symbols.bundle(), raw=raw)
    for name, pc, bank in (('RyuSourceBodyAfterBGBridge', 0xe5cc, 127),
                           ('ThPostNativeHot', 0xb438, 66),
                           ('HuGmStatusName::Copy', 0xbb80, 79),
                           ('S2AudioStatusSTA', 0xbb6e, 74)):
        assert Terrain.W.address(b, name) == pc
        assert (Terrain.W.location(b, name)-16)//8192 == bank
    fields = {name: Terrain.W.address(b, name) for name in
              ('CurrentBank', 'CurrentBankC', 'WorldNumber', 'LevelNumber',
               'GameEngineSubroutine', 'SelectedCharacter')}
    # Actual source-owned private addresses are encoded in the authenticated
    # audio writer above; none is assigned or initialized by this observer.
    fields.update(active_bank=0x6f7e, pending_bank=0x6f7f, enable=0x6f81)
    return dict(windows=windows, fields=fields, event_cap=64, tail_cap=16)


def lua(value):
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, dict):
        return '{'+','.join('['+json.dumps(k)+']='+lua(value[k]) for k in sorted(value))+'}'
    if isinstance(value, list):
        return '{'+','.join(map(lua, value))+'}'
    assert isinstance(value, int)
    return str(value)


DECLARATION = '''local aliasTrace={events={},count=0,dropped=0,tail_count=0,tail_dropped=0,
event_cap=64,tail_cap=16,observed_calls={},changes={},readonly=true,capture_files=0}
'''


OBSERVER = r'''
-- All reads are debugger reads. No APU register read with CPU side effects,
-- state grant, audio cancellation, mirror repair or input override is made.
for _,w in ipairs(aliasWindows)do
 for i=1,#w.data,2 do
  assert(emu.read(w.offset+(i-1)//2,emu.memType.nesPrgRom)==tonumber(w.data:sub(i,i+1),16),
   'Exact current DMC alias/source writer binding')
 end
end
local aliasLastWrite,aliasLastResident,aliasPending={},{},nil
local function aliasLocation(pc)
 local at=emu.convertAddress(pc)
 if not at then return {kind='unmapped',offset=-1,bank=-1}end
 return {kind=tostring(at.memType),offset=at.address,
  bank=at.memType==emu.memType.nesPrgRom and at.address//8192 or -1}
end
local function aliasMapped(pc,bank)
 local at=emu.convertAddress(pc)
 return at and at.memType==emu.memType.nesPrgRom and at.address==bank*8192+(pc&8191)
end
local function aliasHex(pc,n)
 local out={};for i=0,n-1 do out[#out+1]=string.format('%02x',read(pc+i))end
 return table.concat(out)
end
local function aliasSnapshot(kind)
 local c=emu.getState();local q={kind=kind,frame=frames,Main=updates,
  cycle=c['cpu.cycleCount'],pc=c['cpu.pc'],sp=c['cpu.sp'],a=c['cpu.a'],x=c['cpu.x'],y=c['cpu.y'],
  world=read(aliasFields.WorldNumber),level=read(aliasFields.LevelNumber),
  engine=read(aliasFields.GameEngineSubroutine),selected=read(aliasFields.SelectedCharacter),
  status4015=read(0x4015),active_bank=read(aliasFields.active_bank),
  pending_bank=read(aliasFields.pending_bank),enable=read(aliasFields.enable),
  bankA=read(aliasFields.CurrentBank),bankC=read(aliasFields.CurrentBankC),
  mapped_pc=aliasLocation(c['cpu.pc']),resident=aliasLocation(0xe5cc),
  smc_target=read(0x16c)+256*read(0x16d),smc_next_bank=read(0x162),
  tail=aliasHex(0xe5e3,21),apu={}}
 q.tail_target=read(0xe5ea)+256*read(0xe5ef);q.tail_bank=read(0xe5f4)
 q.stack_return=(read(0x100+((q.sp+1)&255))+256*read(0x100+((q.sp+2)&255))+1)&65535
 for _,name in ipairs({'apu.dmc.bytesRemaining','apu.dmc.sampleAddr','apu.dmc.currentAddr',
  'apu.dmc.sampleLength','apu.dmc.enabled','apu.dmc.dmaRunning','apu.dmc.outputLevel','apu.dmc.timer'})do
  if c[name]~=nil then q.apu[name]=c[name]end
 end
 return q
end
local function aliasRecord(q,tail)
 aliasTrace.observed_calls[q.kind]=(aliasTrace.observed_calls[q.kind]or 0)+1
 if tail then
  if aliasTrace.tail_count>=aliasTrace.tail_cap then aliasTrace.tail_dropped=aliasTrace.tail_dropped+1;return end
  aliasTrace.tail_count=aliasTrace.tail_count+1
 end
 if aliasTrace.count>=aliasTrace.event_cap then aliasTrace.dropped=aliasTrace.dropped+1;return end
 aliasTrace.count=aliasTrace.count+1;aliasTrace.events[tostring(aliasTrace.count)]=q
end
local function aliasScene()
 return game and read(aliasFields.WorldNumber)==0 and read(aliasFields.LevelNumber)==1
end
-- Mesen reports the next PC on a write callback. Authorize the writer using
-- its exact preceding opcode and physical PRG mapping, not the next byte.
local function aliasWrite(at,writer,value)
 if not game or not aliasMapped(writer,74)then return end
 local c=emu.getState();if c['cpu.pc']~=writer+3 then return end
 local resident=aliasLocation(0xe5cc).bank
 local key=tostring(writer)..':'..value..':'..resident..':'..read(aliasFields.LevelNumber)..':'..read(aliasFields.GameEngineSubroutine)
 if aliasLastWrite[at]==key then return end
 aliasLastWrite[at]=key
 local q=aliasSnapshot(at==0x5117 and 'sample_alias_write'or'sample_status_write')
 q.address=at;q.value=value;q.writer=writer;q.status_is_debug_pre_or_current_write=true
 aliasRecord(q,false)
end
emu.addMemoryCallback(guard(function(_,value)aliasWrite(0x5117,0xbb93,value)end),emu.callbackType.write,0x5117)
emu.addMemoryCallback(guard(function(_,value)
 aliasWrite(0x4015,0xbb9c,value);aliasWrite(0x4015,0xbb78,value)
end),emu.callbackType.write,0x4015)
for _,point in ipairs({{pc=0xbb96,name='alias_after_select'},{pc=0xbb9f,name='status_after_start'},{pc=0xbb7b,name='status_after_stop'}})do
 emu.addMemoryCallback(guard(function()
  if not game or not aliasMapped(point.pc,74)then return end
  local q=aliasSnapshot(point.name)
  local key=q.resident.bank..':'..q.status4015..':'..q.level..':'..q.engine
  if aliasLastWrite[point.name]==key then return end
  aliasLastWrite[point.name]=key;aliasRecord(q,false)
 end),emu.callbackType.exec,point.pc)
end
emu.addMemoryCallback(guard(function()
 if not aliasScene()then return end
 local q=aliasSnapshot('resident_entry');local b=q.resident.bank
 if b~=119 and b~=120 and b~=125 and b~=127 then return end
 local key=b..':'..q.status4015..':'..q.engine..':'..q.tail_target..':'..q.tail_bank
 aliasTrace.resident_entry_calls=(aliasTrace.resident_entry_calls or 0)+1
 if aliasLastResident[key]then return end
 aliasLastResident[key]=true;aliasPending={target=q.tail_target,bank=q.tail_bank&127}
 aliasRecord(q,true)
end),emu.callbackType.exec,0xe5cc)
for _,point in ipairs({{pc=0xe5f5,name='resident_tail_jump'},{pc=0x15a,name='FarCallCommon'},
 {pc=0x16b,name='FarcallJmpTarget_SMC'},{pc=0xbb87,name='stale_target'},{pc=0xb438,name='canonical_target'}})do
 emu.addMemoryCallback(guard(function()
  if not aliasScene()or not aliasPending then return end
  if point.pc==0xbb87 or point.pc==0xb438 then
   if point.pc~=aliasPending.target or not aliasMapped(point.pc,aliasPending.bank)then return end
  elseif point.pc==0xe5f5 then
   local b=aliasLocation(point.pc).bank;if b~=119 and b~=120 and b~=125 and b~=127 then return end
  elseif read(0x16c)+256*read(0x16d)~=aliasPending.target then return end
  local q=aliasSnapshot(point.name);q.expected_target=aliasPending.target;q.expected_bank=aliasPending.bank
  aliasRecord(q,true)
  if point.pc==0xbb87 or point.pc==0xb438 then aliasPending=nil end
 end),emu.callbackType.exec,point.pc)
end
'''


def controller(raw):
    base = base_controller(raw)
    info = bindings(raw)
    text = Terrain.Frozen.Flag.Root.once(base, 'local function finish(ok,why)',
                                        DECLARATION+'local function finish(ok,why)')
    text = Terrain.Frozen.Flag.Root.once(text, 'controller_only=true,physical_frames=',
                                        'controller_only=true,dmc_alias=aliasTrace,physical_frames=')
    declarations = 'local aliasWindows='+lua(info['windows'])+'\n'
    declarations += 'local aliasFields='+lua(info['fields'])+'\n'
    extra = '\n'+declarations+OBSERVER
    text += extra
    # Exact inversion of the three observer insertions proves the input and
    # ending policy are unchanged, rather than asserting only similar routes.
    stripped = text[:-len(extra)]
    stripped = stripped.replace(DECLARATION, '', 1).replace(
        'controller_only=true,dmc_alias=aliasTrace,physical_frames=',
        'controller_only=true,physical_frames=', 1)
    assert stripped == base
    Terrain.Frozen.Flag.Root.Base.LuaRuntime().compile(text)
    executable = '\n'.join(line.split('--', 1)[0] for line in text.splitlines())
    assert not re.search(r'\bio\s*[.:]|\bemu\s*[.:]\s*(?:write|save|load)|os\s*\.\s*(?:execute|remove|rename)', executable)
    assert all(word not in text for word in ('emu.setState', 'takeScreenshot'))
    assert sha256(text.encode()).hexdigest() == LUA_SHA
    return text


def metadata(raw):
    text = controller(raw)
    return dict(ROM_SHA256=PIN, variant=1, identity=Terrain.NAMES[1],
                base_controller_SHA256=BASE_SHA, controller_SHA256=sha256(text.encode()).hexdigest(),
                original_inputs_and_25_grounded_endpoint_exact=True,
                event_cap=64, native_tail_snapshot_cap=16, debug_APU_reads_only=True,
                runtime_state_writes=0, capture_files=0, emitted_files=0,
                native_Mesen_run=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, default=NIGHTLY)
    args = parser.parse_args()
    print(json.dumps(metadata(args.rom.read_bytes()), separators=(',', ':')), flush=True)
