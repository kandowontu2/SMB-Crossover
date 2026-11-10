"""V3 draw-done immutable-record snapshot API proof, no native claim."""
from hashlib import sha256
import json
from unittest.mock import patch

import check_thomas_stdout_controller_source_1110_v2 as V2

C=V2.C
LUA=C.P.W.R/'tools/playthroughs/thomas_earned_powerup_stdout_1110_v3.lua'
V2_PIN='fd52b4d6c9153f62013d746fd94f93d69f2f4d7ec5f55650a4827fbe57144960'
ORIGINAL_RUNTIME=C.runtime


def runtime():
    rt=ORIGINAL_RUNTIME()
    rt.execute('''
emu.memType.nesChrRom=5;host.chr={};local originalRead=emu.read
function emu.read(at,kind)if kind==5 then return host.chr[at]or 0 end;return originalRead(at,kind)end
''')
    return rt


def hardware(rt,bad=False):
    w=rt.globals().host.work;cr=rt.globals().host.chr
    w[0x4800]=167;w[0x4846]=0
    cr[432*1024+1026]=0;cr[432*1024+1068]=0xd0;cr[432*1024]=4
    for i in range(1,5):cr[432*1024+i]=0
    rt.execute('host.exec(0xa375)')
    V2.hardware(rt,bad)


def main():
    assert sha256(V2.LUA.read_bytes()).hexdigest()==V2_PIN
    with patch.object(C,'LUA',LUA),patch.object(C,'runtime',runtime),patch.object(C,'hardware',hardware):
        C.checks()
        rt=runtime();C.startup(rt);hardware(rt)
        # The descriptor/record can change after an accepted draw. DMA must
        # still validate the immutable pose record captured at draw-done.
        w=rt.globals().host.work;w[0x4848]=0x4b;w[0x4849]=0xd0;w[0x504b]=24
        rt.execute('host.write(0x4014,2)');assert rt.globals().host.status is None
        for i in range(64):rt.globals().host.mem[0x201+4*i]=7
        rt.execute('host.write(0x4014,2)');q=C.receipt(rt)
        assert not q['passed'] and q['last_hardware']['body']['expected_cell']['tile']==0
        assert q['last_hardware']['body']['visible_OAM']
    print(json.dumps(dict(passed=True,API_mock_only=True,Mesen_run=False,output_files=0,
        draw_done_original_record_snapshot=True,later_live_descriptor_change_does_not_retag_OAM=True,
        missing_expected_cell_logs_visible_OAM_and_fails=True,v2_preserved=V2_PIN,
        v3_Lua_SHA256=sha256(LUA.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':main()
