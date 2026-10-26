"""Derive a separate startup-only observer without editing the frozen observer."""
from pathlib import Path
import argparse, difflib, hashlib, json

ROOT = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

CORE = '''-- STATIC_RETURN_CORE_START
-- Lua-only slots retain the original dynamic callbacks' first-registration order.
-- Every real emulator callback is registered before emulation begins.
local pending,installed,returnSlotsByPC={},{},{}
local function queueReturnSlot(pc,fn)
 local slots=returnSlotsByPC[pc]
 if not slots then slots={};returnSlotsByPC[pc]=slots end
 slots[#slots+1]=fn
end
local dispatcherInstalled=false
PARODIUS_STATIC_INSTALL_RETURNS=function()
 assert(not dispatcherInstalled,'Static return dispatcher installed exactly once')
 dispatcherInstalled=true
 -- The generated complete run.lua invokes this AFTER the controller harness.
 emu.addMemoryCallback(function(pc)
  local slots=returnSlotsByPC[pc];if not slots then return end
  for i=1,#slots do slots[i]()end
 end,emu.callbackType.exec,0,0xffff)
end
local function onReturn(n,fn)
 local s=emu.getState();local sp=s['cpu.sp'];local pc=(emu.read(256+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+2)%256,emu.memType.nesDebug)+1)%65536;local key=n..':'..pc
 pending[key]={sp=(sp+2)%256,bank=bank(pc),fn=fn}
 if not installed[key]then installed[key]=true;queueReturnSlot(pc,function()local q=pending[key];if q and emu.getState()['cpu.sp']==q.sp and bank(pc)==q.bank then pending[key]=nil;q.fn()end end)end
end
-- STATIC_RETURN_CORE_END'''


def transform(original):
    edits = []
    def replace(old, new, purpose):
        nonlocal original
        assert original.count(old) == 1, purpose
        original = original.replace(old, new)
        edits.append(dict(purpose=purpose, old=old, new=new))
    begin = original.index('local pending,installed={},{}')
    end = original.index('\nfor _,name in ipairs(C.profile_hooks or{})do', begin)
    replace(original[begin:end], CORE, 'Lua-only ordered return slots and final startup dispatcher')
    replace("if not completionHooks[key]then completionHooks[key]=true;emu.addMemoryCallback(function()", "if not completionHooks[key]then completionHooks[key]=true;queueReturnSlot(finishpc,function()", 'DMA completion uses the same ordered Lua-only slots')
    replace("end,emu.callbackType.exec,finishpc)end", "end)end", 'DMA completion no runtime emulator registration')
    begin = original.index('  rasterInstalled=true;emu.addMemoryCallback(function(address)')
    end = original.index('\n end\n if visible and wall>=C.start_frame then', begin)
    old_block = original[begin:end]
    body = old_block.removeprefix('  rasterInstalled=true;emu.addMemoryCallback(function(address)')
    suffix = '\n  end,emu.callbackType.read,0,0x1fff,emu.cpuType.nes,emu.memType.nesPpuMemory)'
    assert body.endswith(suffix)
    body = body.removesuffix(suffix)
    replace(old_block, '  rasterInstalled=true', 'Retain exact endFrame activation epoch without registration')
    raster = '\nemu.addMemoryCallback(function(address)\n   if not rasterInstalled then return end' + body + suffix.replace('\n  end,', '\nend,')
    replace('local rasterInstalled=false\nemu.addEventCallback(function()', 'local rasterInstalled=false' + raster + '\nemu.addEventCallback(function()', 'Register identical raster body at startup behind the original activation gate')
    return original, edits


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--observer-output', type=Path, required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    old=ROOT/'tools/audit/parodius_visibility_observer.lua'
    new,edits=transform(old.read_text(encoding='utf-8'))
    assert not a.observer_output.exists()
    a.observer_output.write_text(new,encoding='utf-8')
    (a.output/'observer.patch').write_text(''.join(difflib.unified_diff(old.read_text(encoding='utf-8').splitlines(True),new.splitlines(True),fromfile=old.name,tofile=a.observer_output.name)),encoding='utf-8')
    (a.output/'edits.json').write_text(json.dumps(edits,indent=2)+'\n',encoding='utf-8')
    for f in [old,a.observer_output,Path(__file__)]:
        (a.output/f.name).write_bytes(f.read_bytes())
    q=dict(passed=True,native_qualified=False,emulated_changes=False,original_sha256=sha(old),observer_sha256=sha(a.observer_output),tool_sha256=sha(Path(__file__)),edits=5,scope='Observation-only transformation. Existing outputs/guards retained; generated dispatcher must be installed last at startup. No native verdict.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(q))

if __name__=='__main__':main()
