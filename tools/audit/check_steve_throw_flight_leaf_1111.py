"""Exercise flight dispatch on cold-loaded code; AB00 placement is a fixture."""

import json
from itertools import product

import check_steve_throw_controls_live_1111 as Controls

Live, C, H = Controls.Live, Controls.C, Controls.H
SOURCE = H.ROOT / 'tools/reference/steve_shatterhand_throw_flight_live_1111.s'


def link(info):
    fields = info['throw_control_fields'] | info['throw_core_link']['symbols']
    fields.update(SteveThrowFrame=0xc978, PlayerFacingDir=Live.W.address(Live.W.Symbols.bundle(), 'PlayerFacingDir'))
    linked = H.assemble(Live.bindings(fields) + SOURCE.read_text(),
                        {'THROW_FLIGHT': (0xab00, 1024), 'THROW_EMISSION': (0xd777, 9)})
    return linked, fields


def cold(candidate, info):
    m = C.Common.blank(dict(Live.W.Symbols.bundle(), raw=candidate))
    C.Common.scene(m, 16)
    m[0x730b] = 0x40
    cpu = C.ColdVector.entry(m)
    at = info['cold']['symbols']['JaySceneOrRetire']
    m[0x16c], m[0x16d] = at & 255, at >> 8
    C.Vector.finish(m, cpu, Controls.Carrier.T.Weapon.Stock.STOP)
    assert C.Common.headers(m) == (info['cookie'],)*2
    m.raw_page(1, 3)
    m.raw_page(2, 2)
    Live.N.put(m, CurrentBankC=2)
    return m


def main():
    candidate, info = Controls.proposal(Live.DONOR.HOST.read_bytes(), graphics=True)
    linked, fields = link(info)
    seed = cold(candidate, info)
    # Explicit detached injection; this does not claim authenticated AB00
    # ownership or change a ROM. The loader/funding audit is separate.
    for segment, bank, offset in (('THROW_FLIGHT', 3, 0xb00), ('THROW_EMISSION', 2, 0x1777)):
        code = linked['images'][segment]
        seed.ram[bank][offset:offset+len(code)] = code
    counts, trips = 0, []
    for actor, facing, camera in product((1, 3), (0, 0x80), (0, 0x610, 0xcf0)):
        m = C.Vector.clone(seed)
        cpu = Live.N.NesMPU(memory=m)

        def put(name, value, width=1):
            for byte in range(width):
                m[fields[name]+byte] = (value >> (8*byte)) & 255

        def get(name, width=1):
            return sum(m[fields[name]+byte] << (8*byte) for byte in range(width))

        def call(name):
            Controls.Carrier.Late.Transport.Transport.Upgrade.call(cpu, linked['symbols'][name])
            return bool(cpu.p & 1)

        put('SteveUpgradeState', 0)
        put('PlayerFacingDir', 2 if facing else 1)
        put('SteveBotActor', actor)
        put('SteveBotFacing', facing)
        put('SteveThrowSelector', 0x80)
        put('SteveThrowTimer', 3)
        put('SteveThrowSpeed', 0xa0 if facing else 0x60)
        put('ScreenLeft_X_Pos', camera & 255)
        put('ScreenLeft_PageLoc', camera >> 8)
        put('SteveBotX', (camera+120)*16, 2)
        put('SteveBotY', 100*16, 2)
        put('SteveBotPlayerX', (camera+100)*16, 2)
        put('SteveBotPlayerY', 100*16, 2)
        call('SteveThrowTickPrelude')
        assert get('SteveThrowFrame') == 0
        call('SteveThrowOrbit')
        assert get('SteveThrowCameraX', 2) == camera*16
        assert get('SteveBotX', 2) == (camera+120+(-6 if facing else 6))*16, (
            actor, facing, camera, get('SteveBotX', 2), get('SteveThrowTimer'),
            get('SteveThrowSelector'), get('SteveUpgradeState'), get('SteveThrowCameraX', 2))
        assert get('SteveThrowFrame') == 0x80 and call('SteveThrowEmissionGate')
        # A surviving contact receipt makes the source core home. This
        # fixture does not implement or claim native collision/damage.
        put('SteveBotActor', actor | 0x80)
        call('SteveThrowTickPrelude')
        call('SteveThrowOrbit')
        assert get('SteveBotActor') == actor and get('SteveThrowTimer') == 255
        for tick in range(200):
            put('SteveBotClock', tick)
            call('SteveThrowTickPrelude')
            call('SteveThrowOrbit')
            assert call('SteveThrowEmissionGate')
            if not get('SteveThrowSelector') & 128:
                assert get('SteveBotPose', 2) == 0 and get('SteveThrowFrame') == 128
                trips.append(tick+1)
                break
        else:
            raise AssertionError(('no return', actor, facing, camera))
        call('SteveThrowTickPrelude')
        assert get('SteveThrowFrame') == 0 and not call('SteveThrowEmissionGate')
        before = get('SteveBotActor'), get('SteveBotPlayerX', 2), get('SteveBotPlayerY', 2)
        call('SteveThrowReset')
        assert all(m[fields['SteveThrowSelector']+i] == 0 for i in range(16))
        assert (get('SteveBotActor'), get('SteveBotPlayerX', 2), get('SteveBotPlayerY', 2)) == before
        counts += 1
    print(json.dumps(dict(parent_candidate=C.digest(candidate), cases=counts, return_ticks=trips,
                          bytes={key: len(value) for key, value in linked['images'].items()},
                          detached=True, output_files=0)), flush=True)


if __name__ == '__main__':
    main()
