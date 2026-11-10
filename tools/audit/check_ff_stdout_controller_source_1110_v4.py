"""API-only immediate airborne A release; frozen native-v3 failure retained."""
from hashlib import sha256
import check_ff_stdout_controller_source_1110_v3 as V3

C = V3.C
OLD = C.R / 'tools/playthroughs/ff_full_stage_stdout_1110_v3.lua'
C.LUA = C.R / 'tools/playthroughs/ff_full_stage_stdout_1110_v4.lua'


def airborne_case(continued_desired):
    rt, f = V3.jump_fixture()
    f.pad(129)
    if not continued_desired:
        f.pad(1)
    rt.execute('host.event(1)')
    assert rt.globals().host.pad['a'], 'A pulse must survive until delivered'
    m = rt.globals().host.mem
    m[0xdc], m[0x5c01], m[0x5c00] = 129, 128, 129
    rt.execute('host.exec(0xaacc);host.exec(0xab6d)')
    m[0x1e] = 1
    f.pad(129 if continued_desired else 1)
    rt.execute('host.event(1)')
    assert not rt.globals().host.pad['a'], 'Witnessed airborne must release immediately'
    assert f.active() is None and f.row()['accepted'] and f.row()['airborne']
    assert f.row()['outcome'] == 'source-accepted-airborne-released'
    assert f.row()['returned']['Main'] == f.row()['airborne_Main']
    if continued_desired:
        for _ in range(3):
            f.pad(129)
            rt.execute('host.event(1)')
            assert not rt.globals().host.pad['a'], 'Old hold command must not resurrect A'
        f.pad(1)
        m[0xdc], m[0x5c00], m[0x1e] = 0, 0, 0
        f.pad(129)
        rt.execute('host.event(1)')
        assert rt.globals().host.pad['a'] and f.active(), 'A later fresh request must work'


def main():
    assert sha256(OLD.read_bytes()).hexdigest() == 'c0fe74369c20acfab4fbf6b512aabf3b9234ba0f5b11ee2f8c517e73235eeea5'
    before, after = OLD.read_text(), C.LUA.read_text()
    start, end = "  if phase=='mushroom' then", "  elseif phase=='flower' then"
    assert before.split(start)[1].split(end)[0] == after.split(start)[1].split(end)[0]
    assert "suppressHeldDesiredA=wants;activeJump=nil;return bits&127" in after
    C.runtime = V3.runtime
    C.main()
    airborne_case(False)
    airborne_case(True)
    blocked, b = V3.jump_fixture()
    b.pad(129)
    blocked.globals().host.mem[0x5c01] = 128
    blocked.execute('host.exec(0xab6d)')
    b.advance(4)
    b.pad(1)
    assert b.row()['outcome'] == 'source-accepted-but-no-completed-airborne'
    assert b.active() is None
    print('{"immediate_airborne_release_API_cases":3,"ROM_or_gameplay":false,"outputs_written":0,"passed":true}')


if __name__ == '__main__':
    main()
