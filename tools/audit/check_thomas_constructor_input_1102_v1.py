"""Verify actual native platform construction ignores the incoming accumulator."""
import json
from pathlib import Path
import check_hogan_current_bounded_v1 as M
from prepare_selected_native_packet_v1 import R, sha

def main():
    rom = R / 'build/bub-menu-candidate-1102-v2/combined-event.nes'
    out = R / 'build/thomas-constructor-input-1102-v1'
    out.mkdir(exist_ok=True)
    b = M.scoped_load(rom)
    # The combined debug bundle omits some unchanged native RAM aliases.
    # Recover only data symbols from the linked Thomas source bundle.
    old = M.scoped_load(R / 'build/thomas-platform-ground/candidate.nes')
    for name in ['ObjectOffset','Enemy_ID','Enemy_Flag','Enemy_PageLoc','Enemy_X_Position','Enemy_Y_Position','Enemy_Y_HighPos','AreaAddrsLOffset']:
        if name not in b['syms']:
            symbol = old['syms'][name]
            assert int(symbol['val'],0) < 0x800
            b['syms'][name] = symbol
    target = dict(old['syms']['InitEnemyObject'])
    pos = M.location(old, 'InitEnemyObject')
    assert b['raw'][pos:pos+4] == old['raw'][pos:pos+4] == bytes.fromhex('a900951f')
    # Downstream farcall operands legitimately moved in the combined build.
    # Execute those current bytes rather than transplanting the old worker.
    b['segs']['constructor_reference'] = old['segs'][target['seg']]
    target['seg'] = 'constructor_reference'
    b['syms']['InitEnemyObject'] = target
    seed = M.fresh(b)
    cases = 0
    for slot in range(6):
        for flags in [0x30, 0x31, 0x70, 0xf1]:
            baseline = None
            for incoming in [0, 1, 2, 4, 8, 16, 32, 63, 127, 128, 255]:
                m = M.fork(seed)
                M.put(m, ObjectOffset=slot, WorldNumber=0, LevelNumber=0, AreaAddrsLOffset=5)
                for name, value in [('Enemy_ID',37),('Enemy_Flag',1),('Enemy_PageLoc',10),('Enemy_X_Position',0),('Enemy_Y_Position',192),('Enemy_Y_HighPos',1)]:
                    m[M.address(b,name)+slot] = value
                result = M.invoke(m, 'InitEnemyObject', a=incoming, x=slot, y=5, p=flags)
                # Stack contains historical call arguments; live RAM and all
                # banked state, including the shared SMC operands, must agree.
                state = (bytes(m[:256]), bytes(m[512:2048]),
                         tuple(bytes(r) for r in m.ram), tuple(m.rawtags),
                         tuple(result[k] for k in ['A','X','Y','P','minimum_SP']))
                if baseline is None:
                    baseline = state
                assert state == baseline, (slot, flags, incoming)
                cases += 1
    q = dict(passed=True, cases=cases, ROM_sha256=sha(rom),
             scope='Actual native actor25 constructor incoming-A equivalence, six slots and four flag patterns. Does not qualify whole Thomas caller, interrupts, source composition or assisted crossing.',
             producer_sha256=sha(Path(__file__)))
    (out/'receipt.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(q))

if __name__ == '__main__':
    main()
