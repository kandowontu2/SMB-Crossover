"""Check the sole expanded NMI gateway and its real C116/palette ownership."""
from pathlib import Path
import argparse
import itertools
import json

from check_nmi_vram_fast_cpu_v1 import Bus, address, run, scoped_load, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    old, new = scoped_load(args.baseline), scoped_load(args.candidate)
    assert sha(args.baseline) == '50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'
    assert sha(args.candidate) == 'cf0f53f012a7830c38d4a2212ceed8bc875040b5698345a83d0b7c98213eeed5'
    memories = [Bus(old), Bus(new)]
    packets = [[0], [0x20, 0x22, 1, 0xa5, 0],
               [0x20, 0x22, 28] + list(range(28)) + [0x23, 0xc0, 8] + list(range(8))
               + [0x3f, 0x0c, 4, 15, 0, 16, 32, 0x20, 0x7a, 3, 1, 2, 3, 0]]
    rows = []
    for char, mode, variant, capture, freeze, packet_id in itertools.product(
            range(24), range(2), range(4), range(2), [0, 128], range(3)):
        incoming = [13, 88, 116][packet_id]
        palette = [(i * 97 + char) & 255 for i in range(32)]
        results = []
        for bundle, memory in zip((old, new), memories):
            memory.page(2, incoming)
            memory.palette = palette
            values = dict(SelectedCharacter=char, OperMode=mode, VvVariant=variant,
                PnBombCapturePending=capture, PnBombPaletteReady=0,
                SmFreezePalettePending=freeze, CurrentBankC=incoming | 128,
                Mirror_PPUCTRL=0xa0, NmiR0=0, NmiR1=5)
            for name, value in values.items():
                memory.put(address(bundle, name), value)
            for i, value in enumerate(packets[packet_id]):
                memory.put(0x0500 + i, value)
            for i, value in enumerate([0x3f, 0x15, 3, 1, 17, 33, 0]):
                memory.put(address(bundle, 'SmFreezePalettePacket') + i, value)
            for i in range(32):
                memory.put(address(bundle, 'PnBombPaletteShadow') + i, 0x5a)
            memory.put(0x2002, 0x80)
            memory.put(0x1fe, 0xff)
            memory.put(0x1ff, 0x01)
            result = run(bundle, memory, address(bundle, 'SamusFreezeUpdateScreen'),
                         0x0200, 0x5a, 3, 0xa5, 0x71)
            assert result['banks'][2] == 116
            assert memory[address(bundle, 'CurrentBankC')] == incoming | 128
            expected_capture = char == 18 and mode == 1 and variant != 0 and capture == 1
            assert len(result['reads']) == (32 if expected_capture else 0)
            assert memory[address(bundle, 'PnBombPaletteReady')] == int(expected_capture)
            assert memory[address(bundle, 'SmFreezePalettePending')] == 0
            results.append(result)
        before, after = results
        for key in ('state', 'writes', 'reads', 'ram', 'banks'):
            assert before[key] == after[key], (char, mode, variant, capture, freeze, packet_id, key)
        rows.append(dict(char=char, mode=mode, variant=variant, capture=capture,
            freeze=freeze, packet=packet_id, incoming_C=incoming,
            before=before['cycles'], after=after['cycles']))
    raw = args.output / 'cases.json'
    raw.write_text(json.dumps(rows, separators=(',', ':')) + '\n')
    result = dict(passed=True, native_run=False, baseline_ROM_sha256=sha(args.baseline),
        candidate_ROM_sha256=sha(args.candidate), tool_sha256=sha(__file__), cases=len(rows),
        cases_sha256=sha(raw), capture_cases=sum(r['char'] == 18 and r['mode'] == 1 and
            r['variant'] != 0 and r['capture'] == 1 for r in rows),
        cycle_delta_min=min(r['after'] - r['before'] for r in rows),
        cycle_delta_max=max(r['after'] - r['before'] for r in rows),
        equality='Full linked gateway: AXYP/SP, ordered nonstack writes, actual palette reads, nonstack application RAM and mapper banks.',
        ownership='All calls execute the real gateway from three incoming C banks. It maps116 before either transfer, preserves the incoming CurrentBankC shadow for outer NMI restoration, and performs only guarded32-byte palette capture.',
        limits='Synthetic bounded CPU states across24 numeric base IDs and four variant values; these are not24×4 playable identities or native mode/cadence/PPU acceptance.')
    (args.output / 'proof.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
