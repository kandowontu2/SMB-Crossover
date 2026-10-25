"""Confine PC to the two growth-phase operands with all linked addresses exact."""
from pathlib import Path
import argparse
import hashlib
import json
from check_tmnt_render_oa import load, address, location
from check_tmnt_audio_fallback_oc import qualified


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for n in ('rom', 'baseline', 'output'):
        p.add_argument('--' + n, type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    old, new = load(a.baseline), load(a.rom)
    assert qualified(a.baseline).items() <= qualified(a.rom).items()
    start, stop = location(old, 'M3Graphics'), location(old, 'M3Portrait')
    def word(n):
        v = address(old, n)
        return bytes((v & 255, v >> 8))
    pattern = b'\xad' + word('M3Growth') + b'\x4a\x4a\x29\x01\x8d' + word('M3Scratch')
    region = old['raw'][start:stop]
    assert region.count(pattern) == 1
    position = start + region.index(pattern)
    expected = b'\xad' + word('M3RenderFrame') + b'\x4a\x4a\x29\x08\x8d' + word('M3Scratch')
    assert new['raw'][position:position + len(expected)] == expected
    differences = [i for i, (x, y) in enumerate(zip(old['raw'], new['raw'])) if x != y]
    assert differences == [position + 1, position + 6]
    assert len(old['raw']) == len(new['raw']) and all((i - 16) // 8192 == 90 for i in differences)
    q = dict(passed=True, accepted=False, ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),
             baseline_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(), changed_bytes=differences,
             all_prior_qualified_addresses_exact=True, header_CHR_and_every_other_ROM_byte_exact=True,
             driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             scope='Only the existing M3Graphics growth-phase LDA low-address operand and AND immediate change. Every previous qualified symbol, instruction address/count, RAM allocation, header, CHR and every other PRG byte remain exact. Native branch timing can differ by four cycles on a corrected phase; no claim that complete CPU timestamps stay identical.')
    (a.output / 'proof.json').write_text(json.dumps(q, indent=2) + '\n')
    print(json.dumps(q, indent=2))


if __name__ == '__main__':
    main()
