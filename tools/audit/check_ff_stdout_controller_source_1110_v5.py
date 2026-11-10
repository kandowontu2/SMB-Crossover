"""API-only stale grounded-decision decline; no movement/state grant."""
from hashlib import sha256
import check_ff_stdout_controller_source_1110_v4 as V4

C = V4.C
OLD = C.R / 'tools/playthroughs/ff_full_stage_stdout_1110_v4.lua'
C.LUA = C.R / 'tools/playthroughs/ff_full_stage_stdout_1110_v5.lua'


def main():
    assert sha256(OLD.read_bytes()).hexdigest() == '42ed1997f6c472ab3bfa12ab2c8c5a5020eb39963af7af8f7d82b67bf5d09f96'
    V4.main()
    for airborne in (1, 2):
        rt, f = V4.V3.jump_fixture()
        f.pad(129)  # Actual decision sees the API mock's grounded state.
        m = rt.globals().host.mem
        m[0x1e], m[0xdc], m[0x5c00], m[0x5c01] = airborne, 129, 129, 0
        rt.execute('host.exec(0xaacc);host.event(1)')
        q = f.row()
        assert q['outcome'] == 'sampled-airborne-declined-not-accepted'
        assert q['declined']['state'] == airborne and q['declined']['saved'] == 129
        assert q['accepted'] is None and f.active() is None
        assert not rt.globals().host.pad['a'], 'Declined A must release through controller only'
        f.pad(1)
        m[0x1e], m[0xdc], m[0x5c00] = 0, 0, 0
        f.pad(129)
        rt.execute('host.event(1)')
        assert f.active() and rt.globals().host.pad['a'], 'Fresh request after landing must work'
    grounded, g = V4.V3.jump_fixture()
    g.pad(129)
    grounded.globals().host.mem[0xdc] = 129
    grounded.execute('host.exec(0xaacc)')
    assert g.active() and g.row()['declined'] is None
    g.advance(17)
    try:
        g.pad(1)
    except Exception as error:
        assert 'not accepted' in str(error)
    else:
        raise AssertionError('Unexplained grounded non-acceptance must still fail')
    print('{"sampled_airborne_decline_API_cases":3,"ROM_or_gameplay":false,"outputs_written":0,"passed":true}')


if __name__ == '__main__':
    main()
