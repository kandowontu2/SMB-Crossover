"""Bind a sixth authenticated cold row to Steve's private companion window."""

import argparse
import json
from itertools import product
from unittest.mock import patch

import check_steve_shatterhand_token_draw_1111 as Draw


Ingress = Draw.Ingress
Transport, C, H, N, W = Ingress.Transport, Draw.C, Draw.H, Draw.N, Draw.W
T, Steve = Transport.T, Transport.Steve
BASE = 'f61501cc1c173f5437ef3ae5c7b179116deb1c6bbebe118f41e68fced9497cea'
PAGE, ROLL_MIRROR = 379, 367
ORIGIN, CAPACITY, STATE, STATE_SIZE = 0xc500, 0x3c0, 0xc900, 64
EXT_PAGE, EXT_ORIGIN, EXT_CAPACITY, EXT_STATE = 375, 0xca00, 0x400, 0xc940
BOOT, BOOT_SIZE = 0xb7c0, 64
SOURCE = H.ROOT / 'tools/reference/steve_shatterhand_companion_cold_1111.s'
LEDGER = H.ROOT / 'build/mini-mario-owner-1103-v15/carrier-audit-v16.json'
LEDGER_PIN = 'beaef6513ec8471a60d254daacbf30808b6090cf177a378647801c9be98dac01'
OLD_DESC = Transport.DESCRIPTOR


def companion_descriptors(upgrade):
    core = bytes((10, 6)) + upgrade[2:13] + PAGE.to_bytes(2, 'little') + upgrade[13:]
    full = bytes((11, 7)) + core[2:15] + EXT_PAGE.to_bytes(2, 'little') + core[15:]
    return core, full


DESCRIPTOR, EXT_DESCRIPTOR = companion_descriptors(OLD_DESC)


def roll_funding(raw, *, extended=False, roll_storage=False):
    from audit_mega_giant_chr_candidates_1110_v1 import table, MAP_BANKS, prg_at, compiled_readers

    assert T.page(raw, PAGE) == T.page(raw, ROLL_MIRROR)
    assert T.page(raw, PAGE) == T.page(raw, 371) == T.page(raw, 375)
    bundle = dict(W.Symbols.bundle(), raw=raw)
    assert W.address(bundle, 'RlPublish') == 0xb03d
    assert W.address(bundle, 'RlPoolChrLo') == 0xcc6d
    assert W.address(bundle, 'RlPoolChrHi') == 0xcc73
    highs = W.location(bundle, 'RlPoolChrHi')
    lows = W.location(bundle, 'RlPoolChrLo')
    assert raw[lows:lows+6] == bytes((108, 112, 116, 120, 48, 80))
    assert raw[highs:highs+6] == b'\x01'*6
    assert raw[16:C.CHR].count(bytes.fromhex('be73cc')) == 3
    assert all(raw[16:C.CHR].count(bytes((opcode, 0x73, 0xcc))) == 0
               for opcode in (0xad, 0xac, 0xb9, 0xbd))
    prior = LEDGER.read_bytes()
    assert T.digest(prior) == LEDGER_PIN
    ledger = json.loads(prior)
    pages = (PAGE, EXT_PAGE) if extended else (PAGE,)
    if roll_storage:
        pages += (Transport.ROLL_PAGE,)
    for page in pages:
        owners = [name for name, values in ledger['exact_finite_domains'].items() if page in values]
        assert owners == ['Roll body/effect']
        assert not any(page in row['pages'] for row in ledger['inherited_private_writer_chunks_exact'])
    for name in ('RlPoolChrLo', 'RlPoolChrHi'):
        row, = [row for row in ledger['current_table_bindings'] if row['name'] == name]
        at = W.location(bundle, name)
        assert at == row['offset'] and T.digest(raw[at:at+row['bytes']]) == row['SHA256']
    _, native = table(bundle, 'ChrPhysicalMap', 256)
    assert all(raw[prg_at(bank, 0xe36):prg_at(bank, 0xe36)+256] == native for bank in MAP_BANKS)
    assert not any(set(pages).intersection(row['actual_mmc5_outputs']) for row in compiled_readers(bundle).values())

    first = tuple((C.offset(79, at), bytes.fromhex('be73cc'), bytes.fromhex('a201ea'))
                  for at in (0xb052, 0xb072, 0xb092))
    last = (C.offset(79, 0xb08c), bytes.fromhex('b96dcc186903'), bytes.fromhex('b973cc18b8ea'))
    index = (highs, b'\x01'*6,
             bytes((111, 111 if roll_storage else 115, 111 if extended else 119, 111, 51, 83)))
    return first + (last, index)


def compact_cold(cookie, *, extended=False, upgrade=OLD_DESC):
    core, full = companion_descriptors(upgrade)
    source = T.cold_program(core, cookie)['source']
    source = Ingress.S.changed(source, ' and #$60\n cmp #$20\n beq ReturnIdentity\n',
                               ' adc #$1f\n asl a\n asl a\n rts\n')
    if extended:
        edits = ((' ldx #22\nPushDescriptor:', ' ldx #24\nPushDescriptor:'),
                 (' ldx #23\nPullDescriptor:', ' ldx #25\nPullDescriptor:'),
                 (' .byte '+','.join(map(str, core)), ' .byte '+','.join(map(str, full))),
                 (' lda #0\n sta $c033', ' stx $c033'))
        for before, after in edits:
            source = Ingress.S.changed(source, before, after)
    linked = H.assemble(source, {'COLD65': (T.COLD, T.COLD_SIZE)})
    assert linked['used']['COLD65'] == 161
    return linked


def mount(token_image, token_info, companion, *, extension=b'', extra_edits=(), funding_source=None):
    """Mount 960 core bytes and optional 1 KiB plus its 64 state bytes."""
    assert 0 < len(companion) <= CAPACITY
    assert len(extension) <= EXT_CAPACITY
    extended = bool(extension)
    upgrade = token_info['upgrade_descriptor']
    upgrade_page = token_info['upgrade_page']
    roll_storage = upgrade_page == Transport.ROLL_PAGE
    assert roll_storage == (funding_source is not None)
    core, full = companion_descriptors(upgrade)
    descriptor = full if extended else core
    if extended:
        assert Ingress.S.code(token_image, 126, 0x80c2, 7) == bytes.fromhex('8da17d8d165160')
    old_cookie = token_info['cookie']
    old_cold = Steve.cold_program(upgrade, old_cookie)
    old_row = T.page(token_image, upgrade_page)
    continuation = bytes.fromhex('a94085034c04a0')
    assert old_row[0x100:0x160].count(continuation) == 1
    at = old_row.index(continuation, 0x100, 0x160)
    redir = ((b'\xa0\x00' if extended else b'') + b'\x4c' + T.J.u16(BOOT)).ljust(7, b'\xea')
    row = old_row[:at] + redir + old_row[at+len(redir):]
    setup = 'STEVE_SEVENTH_ROW=1\n' if extended else ''
    boot = H.assemble(setup + SOURCE.read_text(), {'COMPANION_COLD': (BOOT, BOOT_SIZE)})
    loader = boot['images']['COMPANION_COLD']
    payload = companion.ljust(CAPACITY, b'\xea') + loader.ljust(BOOT_SIZE, b'\xea')
    assert len(payload) == 1024
    extension = extension.ljust(EXT_CAPACITY, b'\xea') if extended else b''
    roll_edits = roll_funding(token_image if funding_source is None else funding_source,
                              extended=extended, roll_storage=roll_storage)
    edits = roll_edits + tuple(extra_edits)
    binding = b''.join(offset.to_bytes(4, 'little') + new for offset, _, new in edits)
    cookie = old_cookie[:4] + bytes.fromhex(T.digest(old_cookie + descriptor + row + payload + extension + binding))[:12]
    cold = compact_cold(cookie, extended=extended, upgrade=upgrade)
    output = bytearray(token_image)

    def patch(offset, old, new):
        assert len(old) == len(new) and output[offset:offset+len(old)] == old, hex(offset)
        output[offset:offset+len(new)] = new

    patch(C.offset(65, T.COLD), old_cold['images']['COLD65'].ljust(T.COLD_SIZE, b'\xea'),
          cold['images']['COLD65'].ljust(T.COLD_SIZE, b'\xea'))
    patch(C.offset(65, 0xaf01), T.J.u16(old_cold['symbols']['JaySelect']), T.J.u16(cold['symbols']['JaySelect']))
    patch(C.offset(94, 0xb2ef), old_cookie, cookie)
    patch(C.CHR+1024*upgrade_page, old_row, row)
    patch(C.CHR+1024*PAGE, T.page(token_image, ROLL_MIRROR), payload)
    if extended:
        patch(C.CHR+1024*EXT_PAGE, T.page(token_image, ROLL_MIRROR), extension)
    for edit in edits:
        patch(*edit)
    return bytes(output), token_info | dict(cookie=cookie, cold=cold, loader=boot, payload=payload,
                                           companion=companion, roll_edits=roll_edits,
                                           extension=extension, descriptor=descriptor,
                                           state_size=2*STATE_SIZE if extended else STATE_SIZE)


def fixture_payload(*, extended=False):
    # The real companion worker is supplied by its own source owner. This
    # fixture makes every loaded page distinguishable and has one 2A03 probe.
    probe = bytes.fromhex('ee40c9ad40c960' if extended else 'ee00c9ad00c960')
    length = EXT_CAPACITY if extended else CAPACITY
    salt = 151 if extended else 19
    return probe + bytes(((index*73+salt) ^ (index >> 2)) & 255 for index in range(len(probe), length))


def loaded_parity(raw, candidate, info, old_info):
    report = {}
    extended = bool(info['extension'])
    begin = ORIGIN-0xc000
    state, state_end = STATE-0xc000, STATE+info['state_size']-0xc000
    extension, extension_end = EXT_ORIGIN-0xc000, EXT_ORIGIN+EXT_CAPACITY-0xc000
    end = extension_end if extended else state_end

    def loaded(memory):
        assert memory.ram[2][begin:state] == info['payload']
        assert not any(memory.ram[2][state:state_end])
        if extended:
            assert not any(memory.ram[2][state_end:extension])
            assert memory.ram[2][extension:extension_end] == info['extension']

    def app(memory):
        old = C.Vector.app(memory)
        ram = list(old[3])
        ram[2] = ram[2][:begin] + ram[2][end:0x1fe0] + ram[2][0x1ff0:]
        ram[3] = ram[3][:0x1fe0] + ram[3][0x1ff0:]
        return (*old[:3], ram, *old[4:], memory.chr_latches, memory.vram)

    for variant, name in enumerate(('Mike', 'Jay', 'Steve')):
        old, old_epoch = Steve.Live.opening(raw, variant)
        new, epoch = Steve.Live.opening(candidate, variant)
        assert epoch == old_epoch == 167
        reads = (old.ppu_reads, new.ppu_reads)
        if variant:
            assert reads == (18450, 22550 if extended else 20500)
            assert C.Common.headers(old) == (old_info['cookie'],)*2
            assert C.Common.headers(new) == (info['cookie'],)*2
            loaded(new)
            assert not any(old.ram[2][begin:end])
        else:
            assert reads == (0, 0) and not any(new.ram[2][begin:end])
        pads = [0]*6 + [64]*12 + [1]*19 + [129]*9 + [2]*15 + [0]*10 + [64]*9
        for pad in pads:
            for memory in (old, new):
                memory.controller_pad = pad
                C.Game.frame(memory)
            assert app(old) == app(new), (name, pad, Steve.Live.player(new))
            assert not any(old.ram[2][begin:end]), (name, pad)
            if variant:
                loaded(new)
        report[name] = dict(cold_reads=reads, updates=len(pads), terminal=Steve.Live.player(new))
    # Execute the immutable loaded fixture after a genuine menu and header pair.
    new.raw_page(2, 2)
    N.put(new, CurrentBankC=2)
    cpu = N.NesMPU(memory=new)
    Transport.Upgrade.call(cpu, ORIGIN)
    assert cpu.a == new.ram[2][STATE-0xc000] == 1
    if extended:
        Transport.Upgrade.call(cpu, EXT_ORIGIN)
        assert cpu.a == new.ram[2][EXT_STATE-0xc000] == 1
    return report


def roll_parity(before, after, *, extended=False, roll_storage=False):
    pairs = [C.Common.blank(dict(W.Symbols.bundle(), raw=image)) for image in (before, after)]
    setter = W.address(pairs[0].bundle, 'X5SetPhysicalChr')
    bases = (364, 368, 372, 376, 304, 336)
    rebounds = {PAGE, EXT_PAGE} if extended else {PAGE}
    if roll_storage:
        rebounds.add(Transport.ROLL_PAGE)
    verified = 0
    aliases = []
    for pool, incoming in product(range(len(bases)), (0x30, 0x31, 0x70, 0x71)):
        reads, registers = [], []
        for memory in pairs:
            N.put(memory, RlPool=pool)
            requests = []

            def observe(m, cpu):
                if cpu.pc == setter and m.rawtags[1] == 0xbe:
                    requests.append((cpu.y, cpu.a + 256*cpu.x))

            cpu = C.Vector.call(memory, 'RlPublish', p=incoming, observe=observe)
            reads.append(requests)
            registers.append((cpu.x, cpu.y, cpu.p, cpu.sp))
        base = bases[pool]
        assert reads[0] == [(0, base), (6, base+2), (7, base+3)]
        assert reads[1] == [(0, base), (6, base+2), (7, ROLL_MIRROR if base+3 in rebounds else base+3)]
        assert registers[0] == registers[1]
        for (old_slot, old_page), (slot, page) in zip(*reads, strict=True):
            assert old_slot == slot and T.page(before, old_page) == T.page(after, page)
            if old_page != page:
                aliases.append((pool, old_page, page))
        verified += 1
    pools = ((1, Transport.ROLL_PAGE), (2, EXT_PAGE), (3, PAGE))
    assert set(aliases) == {(pool, page, ROLL_MIRROR) for pool, page in pools
                            if page in rebounds}

    import check_current_roster_stage_ingress_1110 as Active

    row, = [row for row in Active.C.inventory(before)['rows'] if row['name'] == 'ROLL']
    consume = Active.N.consume
    applications, rendered = [], []
    for image in (before, after):
        frames = []

        def observe_nmi(memory):
            consume(memory)
            if tuple(Active.N.get(memory, field) for field in ('OperMode', 'OperMode_Task',
                                                               'GameEngineSubroutine')) == (1, 3, 8):
                frames.append((bytes(memory[0x200:0x300]), tuple(memory.chr_latches)))

        with patch.object(Active.N, 'consume', observe_nmi):
            applications.append(Active.stage(dict(Active.F.Symbols.bundle(), raw=image), row))
        rendered.append(frames)
    assert applications[0] == applications[1]
    for (old_oam, old_chr), (oam, chr_map) in zip(*rendered, strict=True):
        assert old_oam == oam
        for old_page, page in zip(old_chr, chr_map, strict=True):
            assert page == (ROLL_MIRROR if old_page in rebounds else old_page)
            assert T.page(before, old_page) == T.page(after, page)
    assert len(rendered[0]) == 60
    return dict(publisher_comparisons=verified, exact_1KB_pairs=3*verified,
                changed_slot7=sorted(set(aliases)), opening=applications[1], opening_OAM_CHR_pairs=len(rendered[0]))


def identity_parity(old_cookie, info):
    from py65.devices.mpu6502 import MPU

    program = (Steve.cold_program(OLD_DESC, old_cookie), info['cold'])
    fixtures = []
    for link in program:
        memory = [0]*65536
        image = link['images']['COLD65']
        memory[T.COLD:T.COLD+len(image)] = image
        fixtures.append((MPU(memory=memory), link['symbols']['JayIdentity']))
    for owner, variant in product(range(256), repeat=2):
        decisions = []
        for cpu, entry in fixtures:
            cpu.memory[0x6002] = owner
            cpu.memory[0x730b] = variant
            Transport.Upgrade.call(cpu, entry)
            decisions.append(bool(cpu.p & cpu.CARRY))
        assert decisions[0] == decisions[1] == (owner == 16 and (variant & 0x60) in (0x20, 0x40))
    return 65536


def cold_controls(candidate, info):
    bundle = dict(W.Symbols.bundle(), raw=candidate)
    stop = T.Weapon.Stock.STOP
    at = info['cold']['symbols']['JaySceneOrRetire']
    cuts = set()
    faults = ((3, 0x1400), (3, 0x17ff), (2, 0x500), (2, 0x8bf),
              (2, 0x8ff), (2, 0x900), (2, 0x93f))
    extended = bool(info['extension'])
    reads = 22550 if extended else 20500
    state_end = 0x900 + info['state_size']
    if extended:
        faults += ((3, 0x1800), (3, 0x1bff), (2, 0xa00), (2, 0xdff), (2, 0x940), (2, 0x97f))

    def call(memory, interrupts=False):
        cpu = C.ColdVector.entry(memory)
        memory[0x16c], memory[0x16d] = at & 255, at >> 8

        def observe(m, c):
            if m.rawtags[1:3] == [3, 2] and BOOT <= c.pc < BOOT+BOOT_SIZE:
                # A staged metadata row can temporarily contain padding in
                # the header address. Neither cookie may authenticate yet.
                assert c.p & 4 and all(header != info['cookie'] for header in C.Common.headers(m))
                if interrupts and c.pc not in cuts:
                    cuts.add(c.pc)
                    _, branch = C.Vector.clone(m, c)
                    C.ColdVector.interrupt(branch, 'FF')

        C.Vector.finish(memory, cpu, stop, observe)
        assert (cpu.a, cpu.x, cpu.y, cpu.p & 0xef) == (83, 71, 109, 0x21)

    def seed():
        m = C.Common.blank(bundle)
        C.Common.scene(m, 16)
        m[0x730b] = 0x40
        return m

    m = seed()
    assert m.ram[2][0x900:state_end] == b'\x9d'*info['state_size']
    call(m, interrupts=True)
    assert cuts and m.ppu_reads == reads and C.Common.headers(m) == (info['cookie'],)*2
    assert m.ram[2][0x500:0x900] == info['payload'] and not any(m.ram[2][0x900:state_end])
    if extended:
        assert m.ram[2][0xa00:0xe00] == info['extension']
    m.ram[2][0x900] = 0xa6
    m.ram[2][state_end-1] = 0x6a
    m.ram[2][0x33] = 0x51
    call(m)
    assert m.ppu_reads == reads and m.ram[2][0x900] == 0xa6
    assert m.ram[2][state_end-1] == 0x6a and not m.ram[2][0x33]
    for fault in faults:
        m = seed()
        m.corrupt_at = fault
        call(m)
        assert not any(header[0] for header in C.Common.headers(m)), fault
    return dict(physical_readback_faults=faults, forced_blank_lag_NMI_cuts=len(cuts),
                warm_reads=0, warm_state_retained=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--full-routes', action='store_true')
    parser.add_argument('--seventh-row', action='store_true')
    args = parser.parse_args()
    raw = Transport.source_image(Draw.S.Donor.HOST.read_bytes())
    assert T.digest(raw) == Ingress.PIN
    token, token_info = Draw.proposal(raw)
    assert T.digest(token) == BASE
    extended = args.seventh_row
    candidate, info = mount(token, token_info, fixture_payload(),
                            extension=fixture_payload(extended=True) if extended else b'')
    parity = loaded_parity(token, candidate, info, token_info)
    roll = roll_parity(token, candidate, extended=extended)
    identity = identity_parity(token_info['cookie'], info)
    cold = cold_controls(candidate, info)
    result = dict(passed=True, candidate=T.digest(candidate), token_parent=BASE,
                  owner='Roll slot7 exact mirror', CHR=PAGE, mirror=ROLL_MIRROR,
                  resident=[ORIGIN, ORIGIN+CAPACITY], state=[STATE, STATE+info['state_size']],
                  cold_stub_bytes=len(info['loader']['images']['COMPANION_COLD']),
                  descriptor=info['descriptor'].hex(), opening=parity, roll=roll,
                  owner_flag_comparisons=identity, cold_controls=cold, output_files=0)
    if extended:
        result['extension'] = [EXT_ORIGIN, EXT_ORIGIN+EXT_CAPACITY]
    if args.full_routes:
        jay = Transport.original_jay_image(raw)
        rebuilt, live = Transport.Jay.proposal(Transport.Jay.recover_parent(jay))
        assert rebuilt == jay
        result['Jay_route'] = Transport.Jay.earned_route(candidate, live | {'cookie': info['cookie']})
        m, route = Ingress.third_block(candidate, info)
        assert m.ram[2][0x500:0x900] == info['payload']
        assert not any(m.ram[2][0x900:0x900+info['state_size']])
        if extended:
            assert m.ram[2][0xa00:0xe00] == info['extension']
        result['Steve_three_blocks'] = route['third']
    print(json.dumps(result))


if __name__ == '__main__':
    main()
