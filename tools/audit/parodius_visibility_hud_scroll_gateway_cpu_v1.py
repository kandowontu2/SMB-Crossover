"""Replay gateway ABI with the intentional capture-only zero-scroll pair.

OperMode is title/game flow, not Easy/Hard. Pending HUD publication and native
PPU timing require separate tests. This tool does not qualify adoption.
"""
from pathlib import Path
import argparse
import itertools
import json

from check_nmi_vram_fast_cpu_v1 import Bus, address, run, scoped_load, sha

BASE = '50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--expected-sha256', required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert sha(a.baseline) == BASE
    assert sha(a.candidate) == a.expected_sha256
    a.output.mkdir(parents=True, exist_ok=False)
    bundles = [scoped_load(a.baseline), scoped_load(a.candidate)]
    packets = [[0], [0x20, 0x22, 1, 0xa5, 0],
               [0x20, 0x22, 28] + list(range(28)) + [0x23, 0xc0, 8] + list(range(8))
               + [0x3f, 0x0c, 4, 15, 0, 16, 32, 0x20, 0x7a, 3, 1, 2, 3, 0]]
    rows = []
    for char, oper_mode, variant, capture, freeze, packet in itertools.product(
            range(24), range(2), range(4), range(2), [0, 128], range(3)):
        incoming = [13, 88, 116][packet]
        palette = [(i * 97 + char) & 255 for i in range(32)]
        results = []
        for bundle in bundles:
            m = Bus(bundle)
            m.page(2, incoming)
            m.palette = palette
            state = dict(SelectedCharacter=char, OperMode=oper_mode, VvVariant=variant,
                         PnBombCapturePending=capture, PnBombPaletteReady=0,
                         SmFreezePalettePending=freeze, CurrentBankC=incoming | 128,
                         Mirror_PPUCTRL=0xa0, NmiR0=0, NmiR1=5,
                         X5HudChrUpper=1, InvHudActive=0)
            for name, value in state.items():
                m.put(address(bundle, name), value)
            for i, value in enumerate(packets[packet]):
                m.put(0x0500 + i, value)
            for i, value in enumerate([0x3f, 0x15, 3, 1, 17, 33, 0]):
                m.put(address(bundle, 'SmFreezePalettePacket') + i, value)
            for i in range(32):
                m.put(address(bundle, 'PnBombPaletteShadow') + i, 0x5a)
            m.put(0x2002, 0x80)
            m.put(0x1fe, 0xff)
            m.put(0x1ff, 0x01)
            result = run(bundle, m, address(bundle, 'SamusFreezeUpdateScreen'),
                         0x0200, 0x5a, 3, 0xa5, 0x71)
            assert result['banks'][2] == 116
            assert m[address(bundle, 'CurrentBankC')] == incoming | 128
            expected = char == 18 and oper_mode == 1 and variant != 0 and capture == 1
            assert len(result['reads']) == 32 * int(expected)
            assert m[address(bundle, 'PnBombPaletteReady')] == int(expected)
            assert m[address(bundle, 'SmFreezePalettePending')] == 0
            results.append(result)
        before, after = results
        for key in ('state', 'reads', 'ram', 'banks'):
            assert before[key] == after[key], (char, oper_mode, variant, capture, freeze, packet, key)
        wanted = before['writes']
        if expected:
            at = next(i for i, pair in enumerate(wanted)
                      if pair[0] == address(bundles[0], 'PnBombPaletteShadow') + 31) + 1
            wanted = wanted[:at] + [(0x2005, 0), (0x2005, 0)] + wanted[at:]
        assert after['writes'] == wanted, 'Only intended capture-scroll I/O delta'
        if char != 18 and packet == 0 and freeze == 0:
            assert before['cycles'] + 9 == after['cycles']
        rows.append(dict(char=char, OperMode=oper_mode, variant=variant,
                         capture=capture, freeze=freeze, packet=packet,
                         incoming_C=incoming, before=before['cycles'], after=after['cycles']))
    raw = a.output / 'cases.json'
    raw.write_text(json.dumps(rows, separators=(',', ':')) + '\n')
    proof = dict(passed=True, accepted=False, native_run=False, goal_complete=False,
                 baseline_ROM_sha256=BASE, candidate_ROM_sha256=sha(a.candidate),
                 tool_sha256=sha(Path(__file__)), cases=len(rows),
                 cases_sha256=sha(raw), cycle_delta_min=min(r['after']-r['before'] for r in rows),
                 cycle_delta_max=max(r['after']-r['before'] for r in rows),
                 nonship_empty_no_freeze_extra_cycles=9,
                 equality='Full AXYP/SP, palette reads, nonstack application RAM and banks. '
                          'Ordered nonstack writes exact except two zero-scroll writes '
                          'immediately after the32nd capture shadow store when admitted.',
                 limits='Synthetic24 numeric base IDs/four variants, title/game OperMode0/1; '
                        'these are not96 identities or Easy/Hard tests. No pending HUD packet. '
                        'The no-pending LDA/BMI/JMP pre-guard adds9 cycles even to foreign IDs. '
                        'No native PPU/DMA, publication protocol, cadence or adoption acceptance.')
    (a.output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(proof))


if __name__ == '__main__':
    main()
