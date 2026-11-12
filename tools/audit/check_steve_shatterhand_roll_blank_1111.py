"""Qualify Roll's existing blank CHR requests against native blank CHR21."""

from itertools import product
import json
from unittest.mock import patch

import check_steve_shatterhand_throw_carrier_1111 as Carrier

C, H, N, W, T = Carrier.C, Carrier.H, Carrier.N, Carrier.W, Carrier.T
SOURCE = H.ROOT / 'tools/reference/steve_shatterhand_roll_blank_1111.s'
PUBLISH, END, BANK = 0xb03d, 0xb0a9, 79
MIRROR = 21
RETIRED = (304, 306)
PREIMAGE = bytes.fromhex(
    'a9f98da17da9f98d1651a9008d057eac0a5cb96dcca201eaa0008d6a01a975'
    '8d6c01a9a28d6d01a9be205a01ac0a5cb96dcc186902a201eaa0068d6a01'
    'a9758d6c01a9a28d6d01a9be205a01ac0a5cb973cc18b8eaa201eaa0078d'
    '6a01a9758d6c01a9a28d6d01a9be4c5a01'
)


def funding(raw):
    """Provide one preimage-checked edit replacing the old slot-six alias."""
    from audit_mega_giant_chr_candidates_1110_v1 import MAP_BANKS, compiled_readers, prg_at, table

    b = dict(W.Symbols.bundle(), raw=raw)
    labels = {name: W.address(b, name) for name in
              ('RlPublish', 'RlPool', 'RlPoolChrLo', 'RlPoolChrHi', 'SsChrActive', 'X5SetPhysicalChr')}
    assert labels['RlPublish'] == PUBLISH
    assert labels['RlPoolChrLo'] == 0xcc6d and labels['RlPoolChrHi'] == 0xcc73
    lo = W.location(b, 'RlPoolChrLo')
    assert raw[lo:lo+12] == bytes((108, 112, 116, 120, 48, 48, 111, 111, 111, 111, 48, 48))
    for page in (MIRROR, *RETIRED):
        assert T.page(raw, page) == bytes(1024)
    ledger_path = Carrier.Late.Transport.LEDGER
    ledger_bytes = ledger_path.read_bytes()
    assert C.digest(ledger_bytes) == Carrier.Late.Transport.LEDGER_PIN
    ledger = json.loads(ledger_bytes)
    for page in RETIRED:
        assert [name for name, pages in ledger['exact_finite_domains'].items()
                if page in pages] == ['Roll body/effect']
        assert not any(page in row['pages'] for row in ledger['inherited_private_writer_chunks_exact'])
    _, native = table(b, 'ChrPhysicalMap', 256)
    assert MIRROR in native and all(raw[prg_at(i, 0xe36):prg_at(i, 0xe36)+256] == native for i in MAP_BANKS)
    assert not any(set(RETIRED).intersection(row['actual_mmc5_outputs'])
                   for row in compiled_readers(b).values())
    at = C.offset(BANK, PUBLISH)
    assert len(PREIMAGE) == END-PUBLISH and raw[at:at+len(PREIMAGE)] == PREIMAGE
    source = Carrier.Live.bindings(labels) + SOURCE.read_text()
    linked = H.assemble(source, {'ROLL_PUBLISH': (PUBLISH, END-PUBLISH)})
    assert linked['symbols']['RollPublish'] == PUBLISH
    code = linked['images']['ROLL_PUBLISH']
    return (at, PREIMAGE, code.ljust(END-PUBLISH, b'\xea')), linked


def alias(page):
    return MIRROR if page in RETIRED else page


def publishers(before, after):
    bundle = W.Symbols.bundle()
    models = [C.Common.blank(dict(bundle, raw=image)) for image in (before, after)]
    setter = W.address(bundle, 'X5SetPhysicalChr')
    for pool, status in product(range(6), (0x30, 0x31, 0x70, 0x71)):
        results, registers = [], []
        for memory in models:
            N.put(memory, RlPool=pool)
            requests = []

            def observe(m, c):
                if c.pc == setter and m.rawtags[1] == 0xbe:
                    requests.append((c.y, c.a+256*c.x))

            cpu = C.Vector.call(memory, 'RlPublish', p=status, observe=observe)
            results.append(requests)
            registers.append((cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp, memory.rawtags[:]))
        base = (364, 368, 372, 376, 304, 304)[pool]
        last = 367 if pool < 4 else 304
        assert results[0] == [(0, base), (6, base+2), (7, last)]
        assert results[1] == [(slot, alias(page)) for slot, page in results[0]]
        assert registers[0] == registers[1], (pool, status, registers)
        assert all(T.page(before, old) == T.page(after, new) for (_, old), (_, new) in zip(*results, strict=True))
    return 24


def opening(before, after):
    import check_current_roster_stage_ingress_1110 as Active

    row, = [row for row in Active.C.inventory(before)['rows'] if row['name'] == 'ROLL']
    consume = Active.N.consume
    outcomes, draws = [], []
    for image in (before, after):
        frames = []

        def capture(m):
            consume(m)
            if tuple(Active.N.get(m, name) for name in ('OperMode', 'OperMode_Task', 'GameEngineSubroutine')) == (1, 3, 8):
                frames.append((bytes(m[0x200:0x300]), tuple(m.chr_latches)))

        with patch.object(Active.N, 'consume', capture):
            outcomes.append(Active.stage(dict(Active.F.Symbols.bundle(), raw=image), row))
        draws.append(frames)
    assert outcomes[0] == outcomes[1] and len(draws[0]) == 60
    for (old_oam, old_map), (oam, new_map) in zip(*draws, strict=True):
        assert old_oam == oam and new_map == tuple(map(alias, old_map))
        assert all(T.page(before, old) == T.page(after, new) for old, new in zip(old_map, new_map, strict=True))
    return len(draws[0])


def main():
    raw = Carrier.Live.DONOR.HOST.read_bytes()
    (at, old, new), linked = funding(raw)
    fixture = bytearray(raw)
    fixture[at:at+len(old)] = new
    for page in RETIRED:
        start = C.CHR+page*1024
        fixture[start:start+1024] = bytes((i*37+page) & 255 for i in range(1024))
    fixture = bytes(fixture)
    print(json.dumps(dict(parent=C.digest(raw), fixture=C.digest(fixture), offsets=[hex(at), hex(at+len(old))],
                          old_sha256=C.digest(old), code_bytes=len(linked['images']['ROLL_PUBLISH']),
                          compiled_publishers=publishers(raw, fixture), equal_opening_frames=opening(raw, fixture),
                          shared_blank=MIRROR, retired_pages=RETIRED, output_files=0), indent=2), flush=True)


if __name__ == '__main__':
    main()
