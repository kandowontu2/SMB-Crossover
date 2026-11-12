"""Prove a post-decoder, authenticated 2 KiB Steve companion carrier in memory."""

import argparse
from collections import Counter
from itertools import product
import json
from unittest.mock import patch

import check_steve_shatterhand_companion_live_1111 as Live


Transport, C, H, N, W = Live.Transport, Live.C, Live.H, Live.N, Live.W
T = Transport.T
SOURCE = H.ROOT / 'tools/reference/steve_shatterhand_late_companion_cold_1111.s'
INSTALLED = 'c4568faf4f472d4d6c3915c9b4258d5c04d6dcbb562b3e5602a5d580bb3046a2'
BASE = '484d159fee570e6646252a24b3d01d6a9ddd17c70af2172d536f510dc34d0eb9'
ORIGIN, CAPACITY = 0xd000, 0x780
STATE, STATE_SIZE = 0xd780, 0x80
BOOT, BOOT_SIZE = 0xcd00, 0x100
BOOT_PAGE, CONTINUATION_PAGE = 375, 218
PAGES = (336, 338)
ROLL_ALIASES = {336: 304, 338: 306}
ROW_SIZE = 1024
PADS = [0]*6 + [64]*12 + [1]*19 + [129]*9 + [2]*15 + [0]*10 + [64]*9


def installed_base():
    installed = Live.DONOR.HOST.read_bytes()
    assert C.digest(installed) == INSTALLED
    image, info = Live.on_nightly(installed)
    assert C.digest(image) == BASE
    return installed, image, info


def funding(image):
    from audit_mega_giant_chr_candidates_1110_v1 import MAP_BANKS, compiled_readers, prg_at, table

    bundle = dict(W.Symbols.bundle(), raw=image)
    lo = W.location(bundle, 'RlPoolChrLo')
    hi = W.location(bundle, 'RlPoolChrHi')
    assert W.address(bundle, 'RlPoolChrLo') == 0xcc6d
    assert image[lo:lo+6] == bytes((108, 112, 116, 120, 48, 80))
    assert image[hi:hi+6] == bytes((111, 111, 111, 111, 51, 83))
    prg = image[16:C.CHR]
    assert [prg.count(bytes((op, 0x6d, 0xcc))) for op in (0xbd, 0xb9, 0xad, 0xbe, 0xac)] == [1, 2, 0, 0, 0]
    _, legacy = table(bundle, 'ChrPhysicalMap', 256)
    assert all(image[prg_at(bank, 0xe36):prg_at(bank, 0xe36)+256] == legacy for bank in MAP_BANKS)
    assert not any(set(PAGES).intersection(row['actual_mmc5_outputs'])
                   for row in compiled_readers(bundle).values())
    original = Transport.LEDGER.read_bytes()
    assert C.digest(original) == Transport.LEDGER_PIN
    ledger = json.loads(original)
    for old, new in ROLL_ALIASES.items():
        assert T.page(image, old) == T.page(image, new) == bytes(ROW_SIZE)
        for page in (old, new):
            assert [name for name, pages in ledger['exact_finite_domains'].items()
                    if page in pages] == ['Roll body/effect']
            assert not any(page in row['pages'] for row in ledger['inherited_private_writer_chunks_exact'])
    return lo+5, b'\x50', b'\x30'


def mount(image, info, code, *, extra_edits=(), pose_carrier=None, cookie_prefix=None):
    """Link raw2 D000–D77F and clear D780–D7FF before both cookies commit."""
    assert C.digest(image) == BASE
    assert 0 < len(code) <= CAPACITY
    assert info['live_bytes'] <= BOOT - Transport.EXT_ORIGIN
    old_cookie = info['cookie']
    assert pose_carrier is None or pose_carrier == 307
    definitions = '' if pose_carrier is None else f'STEVE_POSE_CARRIER={pose_carrier}\n'
    loader = H.assemble(definitions + SOURCE.read_text(), {'STEVE_LATE_COLD': (BOOT, BOOT_SIZE)})
    program = loader['images']['STEVE_LATE_COLD']
    assert loader['symbols']['SteveLateCold'] == BOOT and program[:3] == b'\x20\xc0\xa7'
    continuation = T.page(image, CONTINUATION_PAGE)
    jump = bytes.fromhex('4cc0a7')
    assert continuation.index(jump, 0, 64) == 0x33
    old_worker = T.page(image, T.CHR_PAGE)
    assert old_worker[0x3f1:0x3f4] == bytes.fromhex('4c00d0')
    assert T.page(image, BOOT_PAGE)[0x300:] == b'\xea'*BOOT_SIZE
    staged = code.ljust(CAPACITY, b'\xea') + bytes(STATE_SIZE)
    assert len(staged) == 2*ROW_SIZE
    allocations = (
        funding(image),
        (C.CHR + ROW_SIZE*CONTINUATION_PAGE+0x33, jump, b'\x4c'+BOOT.to_bytes(2, 'little')),
        (C.CHR + ROW_SIZE*BOOT_PAGE+0x300, b'\xea'*BOOT_SIZE, program.ljust(BOOT_SIZE, b'\xea')),
        *((C.CHR+ROW_SIZE*page, bytes(ROW_SIZE), staged[i*ROW_SIZE:(i+1)*ROW_SIZE])
          for i, page in enumerate(PAGES)),
        *extra_edits,
    )
    binding = b''.join(at.to_bytes(4, 'little') + len(new).to_bytes(4, 'little') + new
                       for at, _, new in sorted(allocations))
    assert cookie_prefix is None or len(cookie_prefix) == 4
    prefix = old_cookie[:4] if cookie_prefix is None else cookie_prefix
    cookie = prefix + bytes.fromhex(C.digest(old_cookie + info['descriptor'] + binding + (cookie_prefix or b'')))[:12]
    cold = Transport.compact_cold(cookie, extended=True, upgrade=info['upgrade_descriptor'])
    cold_old = info['cold']['images']['COLD65'].ljust(T.COLD_SIZE, b'\xea')
    cold_new = cold['images']['COLD65'].ljust(T.COLD_SIZE, b'\xea')
    assert cold_old.replace(old_cookie, cookie) == cold_new
    edits = sorted((*allocations, (C.offset(65, T.COLD), cold_old, cold_new),
                    (C.offset(94, 0xb2ef), old_cookie, cookie)))
    candidate = bytearray(image)
    cursor = 16
    for at, old, new in edits:
        assert len(old) == len(new) and cursor <= at and at+len(old) <= len(image)
        assert image[at:at+len(old)] == old, hex(at)
        candidate[at:at+len(new)] = new
        cursor = at+len(old)
    return bytes(candidate), info | dict(cookie=cookie, cold=cold, late_loader=loader,
                                          late_stage=staged, late_code_bytes=len(code), late_edits=edits)


def fixture():
    probe = bytes.fromhex('ee80d7ad80d760')
    other = bytes.fromhex('eeffd7adffd760')
    fill = bytes(((i*73+29) ^ (i >> 2)) & 255 for i in range(CAPACITY))
    return probe+fill[len(probe):ROW_SIZE]+other+fill[ROW_SIZE+len(other):]


def same_loaded(old, new, info):
    assert old.ram[2][:0xd00] == new.ram[2][:0xd00]
    assert old.ram[2][0xe00:0x1000] == new.ram[2][0xe00:0x1000]
    assert old.ram[2][0x1800:0x1fe0] == new.ram[2][0x1800:0x1fe0]
    assert old.ram[2][0x1ff0:] == new.ram[2][0x1ff0:]
    assert old.ram[3][:0x1fe0] == new.ram[3][:0x1fe0]
    assert old.ram[3][0x1ff0:] == new.ram[3][0x1ff0:]
    assert new.ram[2][0x1000:0x1800] == info['late_stage']
    assert old.chr_latches == new.chr_latches and old.vram == new.vram
    assert old.ppuctrl == new.ppuctrl and old.rawtags == new.rawtags


def openings(image, old_info, candidate, info):
    report = {}
    for variant, name in enumerate(('Mike', 'Jay', 'Steve')):
        old, old_epoch = Transport.Steve.Live.opening(image, variant)
        new, epoch = Transport.Steve.Live.opening(candidate, variant)
        assert epoch == old_epoch == 167
        reads = old.ppu_reads, new.ppu_reads
        if variant:
            assert reads == (22550, 26650), reads
            assert C.Common.headers(old) == (old_info['cookie'],)*2
            assert C.Common.headers(new) == (info['cookie'],)*2
            same_loaded(old, new, info)
        else:
            assert reads == (0, 0)
        for pad in PADS:
            for m in (old, new):
                m.controller_pad = pad
                C.Game.frame(m)
            old_app, new_app = C.Vector.app(old), C.Vector.app(new)
            assert (*old_app[:3], old_app[4]) == (*new_app[:3], new_app[4]), (name, pad)
            if variant:
                same_loaded(old, new, info)
            else:
                assert old_app == new_app
        report[name] = dict(cold_reads=reads, equal_updates=len(PADS), terminal=Transport.Steve.Live.player(new))
    new.raw_page(2, 2)
    N.put(new, CurrentBankC=2)
    cpu = N.NesMPU(memory=new)
    for entry, state in ((ORIGIN, STATE), (ORIGIN+ROW_SIZE, STATE+STATE_SIZE-1)):
        Transport.Transport.Upgrade.call(cpu, entry)
        assert cpu.a == new.ram[2][state-0xc000] == 1
    return report


def cold_controls(candidate, info, *, pose_worker=None):
    at = info['cold']['symbols']['JaySceneOrRetire']
    symbols = info['late_loader']['symbols']
    stop = T.Weapon.Stock.STOP
    cuts = set()

    def seed():
        m = C.Common.blank(dict(W.Symbols.bundle(), raw=candidate))
        C.Common.scene(m, 16)
        m[0x730b] = 0x40
        return m

    def call(memory, *, fault=None, nmi=False):
        trace = []
        cpu = C.ColdVector.entry(memory)
        memory[0x16c], memory[0x16d] = at & 255, at >> 8

        def observe(m, c):
            if m.rawtags[1:3] != [3, 2] or not BOOT <= c.pc < BOOT+BOOT_SIZE:
                return
            assert c.p & 4 and m.ppuctrl & 4 == 0
            assert all(header != info['cookie'] for header in C.Common.headers(m))
            if c.pc == symbols['SteveLateRow']:
                trace.append((c.a, c.x))
            if fault and c.pc == symbols['SteveLateVerify'] and m[4] == fault >> 8:
                m.corrupt_at = (2, fault-0xc000)
            if nmi and c.pc not in cuts:
                cuts.add(c.pc)
                _, branch = C.Vector.clone(m, c)
                C.ColdVector.interrupt(branch, 'FF')

        C.Vector.finish(memory, cpu, stop, observe)
        assert (cpu.a, cpu.x, cpu.y, cpu.p & 0xef) == (83, 71, 109, 0x21)
        return trace

    m = seed()
    assert m.ram[2][0x1780:0x1800] == b'\x9d'*STATE_SIZE
    rows = ([(0x33, 0xce)] if pose_worker is not None else []) + [(0x50, 0xd0), (0x52, 0xd4)]
    expected_reads = 26650 + (2050 if pose_worker is not None else 0)
    assert call(m, nmi=True) == rows
    assert len(cuts) >= 32 and m.ppu_reads == expected_reads
    assert C.Common.headers(m) == (info['cookie'],)*2
    assert m.ram[2][0x1000:0x1800] == info['late_stage']
    assert not any(m.ram[2][0x1780:0x1800])
    if pose_worker is not None:
        assert m.ram[2][0xe00:0x1000] == pose_worker.ljust(512, b'\xea')
    m.ram[2][0x1780], m.ram[2][0x17ff] = 0xa6, 0x6a
    assert not call(m) and m.ppu_reads == expected_reads
    assert (m.ram[2][0x1780], m.ram[2][0x17ff]) == (0xa6, 0x6a)

    faults = ((0xce00, 0xcfff) if pose_worker is not None else ()) + (0xd000, 0xd3ff, 0xd400, 0xd77f, 0xd780, 0xd7ff)
    for fault in faults:
        m = seed()
        # D000 also belongs to the temporary upper half of the pose row;
        # its first readback must reject the candidate before later copies.
        expected_rows = next(i+1 for i, (_, high) in enumerate(rows)
                             if high*256 <= fault < high*256+ROW_SIZE)
        assert len(call(m, fault=fault)) == expected_rows
        assert m.corrupt_at == (2, fault-0xc000), hex(fault)
        assert not any(header[0] for header in C.Common.headers(m)), hex(fault)
    m = seed()
    m.corrupt_at = (3, 0x1c00)
    assert not call(m) and not any(header[0] for header in C.Common.headers(m))
    return dict(readback_faults=[hex(at) for at in faults], rejected_upstream_BC00=True,
                forced_blank_lag_NMI_cuts=len(cuts), warm_state_retained=True)


def roll_parity(before, after):
    import check_current_roster_stage_ingress_1110 as Active

    models = [C.Common.blank(dict(W.Symbols.bundle(), raw=image)) for image in (before, after)]
    setter = W.address(models[0].bundle, 'X5SetPhysicalChr')
    bases = (364, 368, 372, 376, 304, 336)
    slot7 = (367, 367, 367, 367, 307, 339)
    for pool, status in product(range(6), (0x30, 0x31, 0x70, 0x71)):
        outputs, registers = [], []
        for m in models:
            N.put(m, RlPool=pool)
            output = []

            def observe(m, cpu):
                if cpu.pc == setter and m.rawtags[1] == 0xbe:
                    output.append((cpu.y, cpu.a + 256*cpu.x))

            cpu = C.Vector.call(m, 'RlPublish', p=status, observe=observe)
            outputs.append(output)
            registers.append((cpu.x, cpu.y, cpu.p, cpu.sp))
        base = bases[pool]
        assert outputs[0] == [(0, base), (6, base+2), (7, slot7[pool])]
        assert outputs[1] == [(slot, ROLL_ALIASES.get(page, page)) for slot, page in outputs[0]]
        assert registers[0] == registers[1]
        for (_, old), (_, new) in zip(*outputs, strict=True):
            assert T.page(before, old) == T.page(after, new)

    row, = [row for row in Active.C.inventory(before)['rows'] if row['name'] == 'ROLL']
    consume = Active.N.consume
    stage, render = [], []
    for image in (before, after):
        frames = []

        def observe_nmi(m):
            consume(m)
            if tuple(Active.N.get(m, f) for f in ('OperMode', 'OperMode_Task', 'GameEngineSubroutine')) == (1, 3, 8):
                frames.append((bytes(m[0x200:0x300]), tuple(m.chr_latches)))

        with patch.object(Active.N, 'consume', observe_nmi):
            stage.append(Active.stage(dict(Active.F.Symbols.bundle(), raw=image), row))
        render.append(frames)
    assert stage[0] == stage[1] and len(render[0]) == 60
    for (old_oam, old_map), (oam, chr_map) in zip(*render, strict=True):
        assert old_oam == oam
        for old_page, page in zip(old_map, chr_map, strict=True):
            assert page == ROLL_ALIASES.get(old_page, old_page)
            assert T.page(before, old_page) == T.page(after, page)
    return dict(publisher_cases=24, compared_1KiB_pages=72, equal_OAM_frames=60, aliases=ROLL_ALIASES)


def gameplay(installed, image, info, *, enforce_retired):
    from deliver_sonic_vol2_forms_1111 import recover_parent

    bus = W.ControllerBus
    get, put = bus.__getitem__, bus.__setitem__
    counts = Counter()
    scene = 'Steve'

    def hot(m):
        return all(m.ram[i][0x1fe0:0x1ff0] == info['cookie'] for i in (2, 3))

    def read(m, at):
        if isinstance(at, int):
            if 0xd000 <= at < 0xd800 and m.rawtags[2] == 2:
                counts[scene, 'D000 hot reads' if hot(m) else 'D000 cold reads'] += 1
            elif 0xbc00 <= at < 0xbfe0 and m.rawtags[1] == 3 and hot(m):
                counts[scene, 'BC00 hot reads'] += 1
        return get(m, at)

    def write(m, at, value):
        if isinstance(at, int) and 0xd000 <= at < 0xd800 and m.rawtags[2] == 2:
            counts[scene, 'D000 hot writes' if hot(m) else 'D000 cold writes'] += 1
        return put(m, at, value)

    with patch.object(bus, '__getitem__', read), patch.object(bus, '__setitem__', write):
        _, steve = Live.natural(image, info)
        scene = 'Jay'
        owner = Transport.Transport
        jay = owner.original_jay_image(recover_parent(installed))
        _, jay_info = owner.Jay.proposal(owner.Jay.recover_parent(jay))
        earned = owner.Jay.earned_route(image, jay_info | dict(cookie=info['cookie']))
    assert steve['uninterrupted_shot_updates'] == 51
    assert earned['native_flag_and_castle'] and earned['dma_cells'] == 5
    if enforce_retired:
        for actor in ('Steve', 'Jay'):
            assert counts[actor, 'D000 hot reads'] == counts[actor, 'D000 hot writes'] == 0
            assert counts[actor, 'D000 cold writes'] and counts[actor, 'BC00 hot reads']
    return {actor: {name: value for (character, name), value in counts.items() if character == actor}
            for actor in ('Steve', 'Jay')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--gameplay', action='store_true', help='include the existing Steve and Jay routes on the fixture')
    mode.add_argument('--parent-footprint', action='store_true', help='trace the same routes on the pinned parent only')
    args = parser.parse_args()
    installed, image, old_info = installed_base()
    if args.parent_footprint:
        print(json.dumps(gameplay(installed, image, old_info, enforce_retired=True), indent=2))
        return
    candidate, info = mount(image, old_info, fixture())
    report = dict(base_SHA256=BASE, fixture_SHA256=C.digest(candidate), cookie=info['cookie'].hex(),
                  loader_bytes=info['late_loader']['used']['STEVE_LATE_COLD'],
                  code_bytes=CAPACITY, state_bytes=STATE_SIZE, rom_written=False)
    report['cold'] = cold_controls(candidate, info)
    report['opening'] = openings(image, old_info, candidate, info)
    report['roll'] = roll_parity(image, candidate)
    if args.gameplay:
        report['fixture_gameplay'] = gameplay(installed, candidate, info, enforce_retired=True)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
