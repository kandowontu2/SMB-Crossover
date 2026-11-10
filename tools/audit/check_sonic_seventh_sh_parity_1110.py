"""Verify Sh's live cookie index and carry ABI after seventh-owner factoring."""
from collections import Counter
from hashlib import sha256
import json

import check_sonic_seventh_cold_owner_1110 as S


def main():
    raw = S.C.ROM.read_bytes()
    image, _, _, _, _, _ = S.proposal(raw)
    bundles = [S.C.Current.W.bundle(q) for q in (raw, image)]
    cookie = raw[S.C.off(65, 0xaa78):S.C.off(65, 0xaa78) + 16]
    assert cookie[:3] == bytes((0xa7, 36, 1))
    counts, minimum = Counter(), 255
    for owner in (0, 36, 37, 38, 39, 40, 41, 42, 43):
        for poison in (None, *range(32)):
            for flags in (0x20, 0x21, 0x61, 0xf9):
                pairs = []
                for index, b in enumerate(bundles):
                    m = S.N.fresh(b)
                    m.raw_page(1, 193); m.raw_page(2, 2)
                    S.N.put(m, CurrentBank=193, CurrentBankC=2, SelectedCharacter=owner, ReloadCHRBank=17)
                    for bank in (2, 3):
                        m.ram[bank][0x1fe0:0x1ff0] = cookie
                    if poison is not None:
                        m.ram[2 + poison // 16][0x1fe0 + poison % 16] ^= 1
                    registers, sp = S.Funding.invoke(m, 0xabd4 if index == 0 else 0xabd5, flags)
                    minimum = min(minimum, sp)
                    assert registers[:3] == (83, 71, 109)
                    assert bool(registers[3] & 1) == (owner == 36 and poison is None)
                    # invoke returns with SP242. Only the retired stack below
                    # and including that SP can contain shifted return PCs;
                    # every live byte above it is still compared exactly.
                    pairs.append((registers, bytes(m[:0x100]), bytes(m[0x1f3:0x8000]),
                                  tuple(bytes(bank) for bank in m.ram),
                                  tuple(m.rawtags), tuple(m.chr_latches), bytes(m.vram)))
                assert pairs[0] == pairs[1], (owner, poison, flags)
                counts['actual_Sh_authentication_flags_and_CHR_publication_pairs'] += 1
    print(json.dumps(dict(passed=True, source_only=True, outputs_written=0, ROM_written=False,
                          in_memory_SHA256=sha256(image).hexdigest(), actual_CPU=dict(counts),
                          minimum_SP=minimum, Sh_cookie_index_7_preserved=True), sort_keys=True))


if __name__ == '__main__':
    main()
