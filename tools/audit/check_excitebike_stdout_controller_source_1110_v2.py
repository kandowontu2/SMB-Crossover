"""V2 physical bank2 observer API proof; not ROM/Mesen gameplay evidence."""
from hashlib import sha256
import json
from unittest.mock import patch

import check_excitebike_stdout_controller_source_1110 as C

LUA=C.P.W.R/'tools/playthroughs/excitebike_earned_powerup_stdout_1110_v2.lua'
V1_PIN='20fcef1f4bb2a98a384d24cf457a8f0f4a58acad6cf3cbb411935c0cf1955794'
ORIGINAL_RUNTIME=C.runtime


def runtime():
    rt=C.Base.LuaRuntime(unpack_returned_tuples=True);rt.execute(C.Base.MOCK)
    rt.globals().host.env['SMB_STDOUT_ROM_SHA']='a76d7610eed8493806200c52b96065af0369b926c55d033e17841f818756e2e0'
    rt.execute('''
host.work={};host.work_reads=0;host.debug_source_reads=0
function emu.read(at,kind)
 if kind==3 then
  assert(at>=2*8192 and at<3*8192,'Physical work-RAM bank2 read')
  host.work_reads=host.work_reads+1;return host.work[at]or 0
 end
 if kind==4 then return host.ppu[at]or 0 end
 if at>=0xc000 and at<0xc800 then host.debug_source_reads=host.debug_source_reads+1 end
 return host.mem[at]or 0
end
function emu.convertAddress(pc)
 if host.wrongMap then return{address=0,memType=2}end
 if pc==0xb299 then return{address=10*8192+(pc&8191),memType=2}end
 if pc>=0xa000 and pc<0xc000 then return{address=3*8192+(pc&8191),memType=3}end
 return{address=(pc>=0xc000 and 127 or 126)*8192+(pc&8191),memType=2}
end
function host.write(at,v)
 local n=#host.callbacks
 for i=1,n do local q=host.callbacks[i];if q.kind==2 and q.first<=at and at<=q.last then q.fn(at,v)end end
end
-- Precisely reproduce the bad CPU mapping observed on physical v1: native
-- C-window returns PRG C0, while the bike's physical bank2 has recovered.
for _,at in ipairs({0xc090,0xc094,0xc0ac,0xc0b0,0xc098})do host.mem[at]=192 end
host.work[0x4000+0xac]=6
''')
    rt.execute(LUA.read_text());return rt


def main():
    assert sha256(C.LUA.read_bytes()).hexdigest()==V1_PIN
    old=C.LUA.read_text();new=LUA.read_text()
    # Exact derivative contract: only header comments, one read helper and
    # its five source-field operands differ. Input/observer assertions stay.
    transformed=old.replace('-- Controller-only natural Excitebike mushroom regression. No state/file writes.',
        '-- V2 observer: physical work-RAM2 source reads at native Main return.\n-- Frozen v1/20f negative is preserved; no gameplay or controller policy change.\n-- Controller-only natural Excitebike mushroom regression. No state/file writes.')
    transformed=transformed.replace('local function read(at)return emu.read(at,emu.memType.nesDebug)end',
        'local function read(at)return emu.read(at,emu.memType.nesDebug)end\nlocal function source(offset)return emu.read(2*8192+offset,emu.memType.nesWorkRam)end')
    for a,z in [('read(0xc090)+256*read(0xc094)','source(0x90)+256*source(0x94)'),
        ('read(0xc0ac)','source(0xac)'),('read(0xc0b0)','source(0xb0)'),('read(0xc098)','source(0x98)')]:
        transformed=transformed.replace(a,z)
    assert transformed.strip()==new.strip()
    with patch.object(C,'LUA',LUA),patch.object(C,'runtime',runtime):
        C.checks()
        rt=runtime();C.startup(rt);m=rt.globals().host.mem
        # Recover predicate must read real bank2, not the mapped C0/C0
        # poison which previously made speed49344 and crash192 forever.
        m[0x75]=144;m[0x5c]=1;C.main(rt);assert C.bits(rt)==0
        C.main(rt);assert C.bits(rt)==66
        assert rt.globals().host.work_reads>0 and rt.globals().host.debug_source_reads==0
    print(json.dumps(dict(passed=True,API_mock_only=True,Mesen_run=False,outputs_written=0,
        controller_policy_unchanged=True,physical_bank2_poisoned_CPU_window_case=True,
        v1_preserved_SHA256=V1_PIN,v2_Lua_SHA256=sha256(LUA.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':main()
