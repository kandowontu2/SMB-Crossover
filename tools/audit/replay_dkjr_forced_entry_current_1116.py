"""Strict7c0f binding of root6699 controls plus actual original-work endpoint."""
from hashlib import sha256
import json
from pathlib import Path

import compose_dkjr_forced_entry_current_1116 as C
import replay_dkjr_final_backward_cap_root_1116 as Root
from check_ff_stdout_controller_source_1110 import LuaRuntime

ROOT_SHA='6699cd358364eb1e4491d7f445a781983134423fc32a3e897af25e81ec9b0c93'
H=lambda value:sha256(value).hexdigest()


def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new,1)


def controller(raw,*,source=False):
    assert H(raw)==C.CANDIDATE and H(Path(Root.__file__).read_bytes())==ROOT_SHA
    parent=C.inverse(raw);base=Root.controller(parent,source=source)
    if not source:assert H(base.encode()).startswith('d06fad3c')
    changes=[];text=base
    count=2 if source else 1
    assert text.count(C.PIN)==count
    text=text.replace(C.PIN,C.CANDIDATE)
    old_cookie,parent_cookie=parent[534485:534501].hex(),raw[534485:534501].hex()
    before="cookie=='"+old_cookie+"'";after="cookie=='"+parent_cookie+"'"
    text=once(text,before,after);changes.append((before,after))
    declarations='''local originalWorkPending
local originalWorkCallbacks={}
local originalWorkEntries,originalWorkReturns,originalWorkGrounded=0,0,0
'''
    text=declarations+text
    before='local function finish(ok,why)\n if done then return end\n'
    after=before+''' if ok then assert(originalWorkGrounded>=25 and not originalWorkPending,
  'Twenty-five actual grounded original-source work returns beyond entry guard')end
'''
    text=once(text,before,after);changes.append((before,after))
    before='events=events,'
    after='events=events,original_work_entries=originalWorkEntries,original_work_returns=originalWorkReturns,original_work_grounded_returns=originalWorkGrounded,'
    text=once(text,before,after);changes.append((before,after))
    _,labels=C.Camera.Plan.source_inputs()
    packet=C.Camera.payload(raw);pcs={name:labels[name]for name in('DkjrNativeSourcePhase','DkjrMove','DkjrClock')}
    assert all(0xa000<=pc<0xc000 for pc in pcs.values())
    assert all(packet[pc-0xa000:pc-0xa000+3]==C.Camera.payload(parent)[pc-0xa000:pc-0xa000+3]for pc in pcs.values())
    phase,move,clock=(pcs[name]for name in('DkjrNativeSourcePhase','DkjrMove','DkjrClock'))
    observer=f'''emu.addMemoryCallback(guarded('original1-2 work entry',function()
 if not mapped(0x{phase:x},'nesWorkRam',3*8192+0x{phase-0xa000:x})or
  read(0x764)~=0 or read(0x761)~=1 or read(0x753)~=2 then return end
 assert(ram(2,0x8fe)==2,'Original work only after native entrance ownership')
 assert(not originalWorkPending,'Nested original-source work')
 originalWorkEntries=originalWorkEntries+1
 local c=emu.getState();local sp=c['cpu.sp']
 local pc=(read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1)&65535
 originalWorkPending={{pc=pc,sp=(sp+2)&255,move=false,clock=false}}
 if not originalWorkCallbacks[pc]then
  originalWorkCallbacks[pc]=true
  emu.addMemoryCallback(guarded('original1-2 work return',function()
   local p=originalWorkPending;if not p then return end
   local c=emu.getState();if c['cpu.pc']~=p.pc or c['cpu.sp']~=p.sp then return end
   originalWorkPending=nil;originalWorkReturns=originalWorkReturns+1
   local healthy=p.move and p.clock and active()and read(0x764)==0 and read(0x761)==1 and
    read(0x753)==2 and read(0x75f)==2 and read(0x0f)==8 and x()==40 and
    read(0xbd)==176 and read(0xa4)==1 and read(0x1e)==0 and ram(2,0x8fe)==2 and
    ram(2,0x6b)==1 and ram(2,0x6c)==1 and ram(2,0x210)==191 and ram(2,0x68)==0
   originalWorkGrounded=healthy and originalWorkGrounded+1 or 0
  end),emu.callbackType.exec,pc)
 end
end),emu.callbackType.exec,0x{phase:x})
emu.addMemoryCallback(guarded('original1-2 move proof',function()
 if originalWorkPending and mapped(0x{move:x},'nesWorkRam',3*8192+0x{move-0xa000:x})then originalWorkPending.move=true end
end),emu.callbackType.exec,0x{move:x})
emu.addMemoryCallback(guarded('original1-2 clock proof',function()
 if originalWorkPending and mapped(0x{clock:x},'nesWorkRam',3*8192+0x{clock-0xa000:x})then originalWorkPending.clock=true end
end),emu.callbackType.exec,0x{clock:x})
'''
    before="emu.addMemoryCallback(guarded('main',function()"
    after=observer+before
    text=once(text,before,after);changes.append((before,after))
    restored=text[len(declarations):]
    for before,after in reversed(changes):restored=once(restored,after,before)
    restored=restored.replace(C.CANDIDATE,C.PIN)
    assert restored==base,'Observer removal must recover exact frozen root6699 controls'
    LuaRuntime().compile(text)
    assert not any(item in text for item in('emu.write','emu.setState','io.open','takeScreenshot','loadState','saveState'))
    return text


if __name__=='__main__':
    raw,_=C.current_proposal(C.BT.ROM.read_bytes())
    native,source=controller(raw),controller(raw,source=True)
    print(json.dumps(dict(factory_SHA256=H(Path(__file__).read_bytes()),root_factory_SHA256=ROOT_SHA,
        ROM_SHA256=H(raw),native_Lua_SHA256=H(native.encode()),source_Lua_SHA256=H(source.encode()),
        exact_root_controls_after_metadata_and_observer_removal=True,
        endpoint='25 living grounded original SourcePhase returns with actual Move+Clock, plus inherited25 D65E wrapper return endpoint',
        no_game_writes=True,outputs=0),separators=(',',':')),flush=True)
