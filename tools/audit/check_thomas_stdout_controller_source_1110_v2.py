"""V2 consumed-body-pattern API proof; not native gameplay evidence."""
from hashlib import sha256
import json
from unittest.mock import patch

import check_thomas_stdout_controller_source_1110 as C

LUA=C.P.W.R/'tools/playthroughs/thomas_earned_powerup_stdout_1110_v2.lua'
V1='c0beb4856e173d0426001d6babbd593837120fe062fa2fcaeecd29f7d0d586c3'
ORIGINAL_HARDWARE=C.hardware


def hardware(rt,bad=False):
    work=rt.globals().host.work;m=rt.globals().host.mem
    # One real-format source descriptor and its actual translated OAM cell.
    work[0x4848]=0;work[0x4849]=0xd0;work[0x5000]=4
    for i in range(1,5):work[0x5000+i]=0
    m[0x200]=176;m[0x201]=0;m[0x202]=0;m[0x203]=41
    rt.execute('host.write(0x5130,1);host.write(0x5101,3)')
    for i in range(4):rt.execute(f'host.write({0x5120+i},{0 if bad else 178+i})')
    ORIGINAL_HARDWARE(rt,bad)


def main():
    assert sha256(C.LUA.read_bytes()).hexdigest()==V1
    source=LUA.read_text()
    assert 'local banks,body=bodyPatterns(page)' in source
    assert 'physical<434 or physical>=442' in source
    assert 'result.parts[#result.parts+1]=found' in source
    with patch.object(C,'LUA',LUA),patch.object(C,'hardware',hardware):
        C.checks()
        rt=C.runtime();C.startup(rt);hardware(rt)
        # Irrelevant latches4..7 can point at native terrain/shot art. Every
        # matched Thomas OAM pattern here consumes slot0/page434.
        for i in range(4,8):rt.execute(f'host.write({0x5120+i},0)')
        rt.execute('host.write(0x4014,2)')
        assert rt.globals().host.status is None
        # A wrong physical page in the actually consumed slot fails.
        rt.execute('host.write(0x5120,0);host.write(0x4014,2)')
        q=C.receipt(rt);assert not q['passed'],q
        assert q['last_hardware']['body']['parts'][0]['slot']==0
    print(json.dumps(dict(passed=True,API_mock_only=True,Mesen_run=False,output_files=0,
        actual_descriptor_OAM_pattern_mapping=True,unused_latches_not_mistaken_for_body=True,
        consumed_wrong_page_fails=True,v1_preserved=V1,v2_Lua_SHA256=sha256(LUA.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':main()
