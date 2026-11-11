"""Link Jay's three-way weapon into the real cold loader on the current ROM."""

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import check_jay_silius_shotgun_1111 as Weapon
import check_jay_silius_stock_carrier_1110 as Carrier
import check_jay_silius_camera_handoff_1111 as Motion


C, H, J, N, W = Weapon.C, Weapon.H, Weapon.J, Weapon.N, Weapon.W
PIN = '852712c9a2afce71c45f9f2c970e1f5c7969c58d878cfa0a250d2bdb7ba93383'
SOURCE = H.ROOT / 'tools/reference/jay_silius_shotgun_transport_1111.s'
CHR_PAGE = 222
MOTION_PAGE = 232
EXTRA_PAGE = 234
PACKET_PAGE = 218
TRANSFER = 0xa7c0
COLD, COLD_SIZE = 0xa696, 162
DESCRIPTOR = bytes((4, 2, 1, 218, 0, CHR_PAGE, 0, 75, 1, 76, 1))
SCROLL_DESCRIPTOR = bytes((5, 3, 1, 218, 0, CHR_PAGE, 0, MOTION_PAGE, 0, 75, 1, 76, 1))
FULL_DESCRIPTOR = bytes((6, 4, 1, 218, 0, CHR_PAGE, 0, MOTION_PAGE, 0, EXTRA_PAGE, 0, 75, 1, 76, 1))
OLD_DESCRIPTOR = bytes.fromhex('030101da004b014c01')
OLD_PACKET_PIN = 'b0f183ee3d9902f53890344400986bcaba7f6050aa49e109d8d140d3fa2f8bce'
OLD_COLD_PIN = 'cb3dc2ad5b6b71fe792eac4158d4057944a0be8784f4d0d72e9b48f484e73878'
OLD_HOT_PIN = 'fe6255c5750c1c799c29a0d1eef9ee4cb3cdf13cb6e845475e936a0f31d38f16'
DUPLICATE_PIN = 'efccdef7770977105d4a8cad48965ebeb8eeda25d27a37e4624795601373e5ba'
ALT_LAYOUT = {'SHOT': (0xb400, 512), 'SUPPORT': (0xb600, 256)}


def digest(data):
    return sha256(data).hexdigest()


def page(raw, index):
    start = C.CHR + index * 1024
    return raw[start:start + 1024]


def carrier_ownership(raw, candidate=CHR_PAGE):
    assert digest(raw) == PIN
    assert candidate in (CHR_PAGE, MOTION_PAGE, EXTRA_PAGE)
    assert page(raw, candidate) == page(raw, 2) and digest(page(raw, candidate)) == DUPLICATE_PIN
    authority = W.Symbols.bundle()
    historic = authority['raw']
    assert digest(historic) == 'd0b445a71d6c539804d7c559fafc2c328ebf97ab4e35e8f3273f94ff8a25d01d'
    normalized = bytearray(raw)

    def art_table(name, size, first, last):
        bank = raw[first:last]
        # Actual LDA abs,X followed by STA SmChrBank.
        store = b'\x8d' + J.u16(W.address(authority, 'SmChrBank'))
        pointers = [int.from_bytes(bank[i+1:i+3], 'little') for i in range(len(bank) - 5)
                    if bank[i] == 0xbd and bank[i+3:i+6] == store]
        pointer, = pointers
        assert 0xce00 <= pointer and pointer + size <= 0xd27f
        at = C.offset(94, pointer)
        old = W.location(authority, name)
        assert raw[at:at+size] == historic[old:old+size]
        normalized[old:old+size] = historic[old:old+size]
        return pointer

    proto = W.location(authority, 'ProtoSetPose')
    sunny = W.location(authority, 'SunnySetPose')
    proto_pointer = art_table('ProtoPoseChrLo', 27, proto, proto + 53)
    sunny_pointer = art_table('SunnyChrLow', 35, sunny, sunny + 150)
    # The compiled setter no longer reads the old Proto high table. Both
    # relocated body readers are checked above; its old high-table site can
    # be restored in the historical table census without touching the ROM.
    high = W.location(authority, 'ProtoPoseChrHi')
    proto_bank = C.offset(66, 0xa000)
    old_high_read = b'\xbd' + J.u16(W.address(authority, 'ProtoPoseChrHi'))
    assert old_high_read not in raw[proto_bank:proto_bank+8192]
    normalized[high:high+27] = historic[high:high+27]
    # These four already allocated upper-1 rows are outside the proposed
    # upper-0 page. The old census expects the pre-allocation Zelda alias.
    assert [page(raw, i) == page(raw, 319 + int(not i & 1)) for i in range(331, 335)] == [False]*4
    for i in range(331, 335):
        at = C.CHR + i * 1024
        normalized[at:at+1024] = page(raw, 319 + int(not i & 1))
    with patch.object(Carrier, 'PAGE', candidate):
        proof = Carrier.current_domains(bytes(normalized))
    assert proof['Sonic_even_pages'] == [candidate]
    return dict(selector_domains=proof['prior_domains'], legacy_tables=proof['current_tables_exact'],
                native_maps=proof['native_map_mirrors'], current_Proto_table=hex(proto_pointer),
                current_Sunny_table=hex(sunny_pointer), candidate_page=candidate)


def cold_program(descriptor, cookie):
    source = J.SOURCE.read_text().split('.segment "PROTO66"', 1)[0]
    edits = (
        (' ldx #6\nPushDescriptor:', f' ldx #{len(descriptor)-1}\nPushDescriptor:'),
        ('SceneReturn:\n', 'SceneReturn:\n' + ' pla\n' * (len(descriptor) - 7)),
        (' .byte 2,0,1,$4b,1,$4c,1', ' .byte ' + ','.join(map(str, descriptor))),
        ('CookieBytes', ','.join(map(str, cookie))),
    )
    for before, after in edits:
        assert source.count(before) == 1, before
        source = source.replace(before, after)
    saving = 0
    if len(descriptor) >= 15:
        old_pulls = 'SceneReturn:\n' + ' pla\n' * len(descriptor)
        new_pulls = f'SceneReturn:\n ldx #{len(descriptor)}\nPullDescriptor:\n pla\n dex\n bne PullDescriptor\n'
        assert source.count(old_pulls) == 1
        source = source.replace(old_pulls, new_pulls)
        saving = len(descriptor) - 6
    program = H.assemble(source, {'COLD65': (COLD, COLD_SIZE)})
    assert program['used']['COLD65'] == 147 + 2 * (len(descriptor) - 7) - saving
    return program


def draw_scope(trial, previous):
    draw = Weapon.Draw
    names = ('FrameCounter', 'OperMode', 'OperMode_Task', 'GamePauseStatus', 'FamilyMainCommit',
             'SwimmingFlag', 'WorldNumber', 'LevelNumber', 'ScreenLeft_PageLoc', 'ScreenLeft_X_Pos',
             'Player_PageLoc')
    fields = {name: W.address(trial, name) for name in names}
    fields.update(OperModeTask=fields.pop('OperMode_Task'), InitBudget=0xb311)
    constants = ''.join(f'{name}=${address:04x}\n' for name, address in fields.items())
    source = draw.SOURCE.read_text().split('.segment "SCOPE"', 1)[1].split('.segment "MUX"', 1)[0]
    source = constants + '.segment "SCOPE"\n' + source
    viewport = ' ora ScreenLeft_PageLoc\n ora ScreenLeft_X_Pos\n ora Player_PageLoc\n'
    assert source.count(viewport) == 1
    size = draw.MUX - draw.SCOPE
    layout = {'SCOPE': (draw.SCOPE, size)}
    old = H.assemble(source, layout)['images']['SCOPE']
    assert old.ljust(size, b'\xea') == previous
    new = H.assemble(source.replace(viewport, ''), layout)['images']['SCOPE']
    assert len(old) - len(new) == 8
    return new.ljust(size, b'\xea')


def proposal(raw, *, movement=None, extra_segments=(), roll=b'', service_hooks=(),
             service_redirects=(), stage_override=None):
    assert digest(raw) == PIN
    assert page(raw, CHR_PAGE) == page(raw, 2) and digest(page(raw, CHR_PAGE)) == DUPLICATE_PIN
    trial = dict(W.Symbols.bundle(), raw=raw)
    _, fields, aliases = Weapon.assemble(trial)
    constants = ''.join(f'{name}=${address:04x}\n' for name, address in aliases.items())
    alternate = H.assemble(constants + Weapon.SOURCE.read_text(), ALT_LAYOUT)
    assert alternate['used'] == {'SHOT': 390, 'SUPPORT': 123}
    assert movement or not (extra_segments or roll or service_hooks or service_redirects or stage_override)
    copy_pages = 11 if extra_segments else 8 if movement else 3
    transfer_defs = f'CopyPages={copy_pages}\n'
    if extra_segments:
        transfer_defs += 'CopyTailBytes=224\n'
    transfer = H.assemble(transfer_defs + SOURCE.read_text(), {'TRANSFER': (TRANSFER, 64)})

    carrier = bytearray(b'\xea' * 1024)
    for section, (address, size) in ALT_LAYOUT.items():
        start = address - 0xb400
        code = alternate['images'][section]
        assert len(code) <= size and start + size <= 768
        carrier[start:start + len(code)] = code
    copy = transfer['images']['TRANSFER']
    assert len(roll) <= TRANSFER-0xa700
    carrier[0x300:0x300+len(roll)] = roll
    carrier[TRANSFER - 0xa400:TRANSFER - 0xa400 + len(copy)] = copy

    packet = bytearray(page(raw, PACKET_PAGE))
    assert digest(packet) == OLD_PACKET_PIN
    symbols = alternate['symbols']
    service = 64
    assert packet[service:service+3] == bytes.fromhex('4c06b0')
    assert packet[service+0x247:service+0x24a] == b'\x20' + J.u16(aliases['StockFlight'])
    assert packet.count(b'\x4c\x00\xd0', 0, service) == 1
    boot_jump = packet.index(b'\x4c\x00\xd0', 0, service)
    packet[boot_jump+1:boot_jump+3] = J.u16(TRANSFER)
    packet[service+1:service+3] = J.u16(symbols['AlternateInput'])
    packet[service+0x248:service+0x24a] = J.u16(symbols['ShotgunFlight'])
    for address, before, target in service_hooks:
        offset = service + address - 0xb000
        assert packet[offset:offset+3] == b'\x20' + J.u16(before)
        packet[offset+1:offset+3] = J.u16(target)
    for address, before, target in service_redirects:
        offset = service + address - 0xb000
        assert len(before) == 3 and packet[offset:offset+3] == before
        packet[offset:offset+3] = b'\x4c' + J.u16(target)

    descriptor = DESCRIPTOR
    movement_row = b''
    extra_row = b''
    if movement:
        draw = Weapon.Draw
        scope = slice(service+draw.SCOPE-0xb000, service+draw.MUX-0xb000)
        packet[scope] = draw_scope(trial, packet[scope])
        motion_symbols = movement['symbols']
        assert motion_symbols['PrivateUpdate'] == 0xb800
        assert page(raw, MOTION_PAGE) == page(raw, 2)
        for at, before, target in ((0xb30e, 0xa785, 'PrivateUpdate'), (0xb151, 0xa834, 'PublishPosition')):
            at = service + at - 0xb000
            assert packet[at:at+3] == b'\x4c' + J.u16(before)
            packet[at+1:at+3] = J.u16(motion_symbols[target])
        movement_row = movement['images']['HANDOFF'].ljust(1024, b'\xea')
        assert len(movement_row) == 1024
        descriptor = SCROLL_DESCRIPTOR
    if extra_segments:
        assert page(raw, EXTRA_PAGE) == page(raw, 2)
        full = bytearray(movement_row + b'\xea'*1024)
        next_free = len(movement['images']['HANDOFF'])
        for address, data in sorted(extra_segments):
            start = address - 0xb800
            end = start + len(data)
            assert next_free <= start < end <= 0x7e0
            full[start:end] = data
            next_free = end
        movement_row, extra_row = bytes(full[:1024]), bytes(full[1024:])
        descriptor = FULL_DESCRIPTOR

    original_stage = page(raw, 331) + page(raw, 332)
    stage = original_stage if stage_override is None else stage_override
    assert len(stage) == 2048
    cookie = bytes((0xa7, 16, 32, 8)) + sha256(stage + descriptor + packet + carrier + movement_row + extra_row).digest()[:12]
    old_cold = cold_program(OLD_DESCRIPTOR, Weapon.COOKIE)
    cold = cold_program(descriptor, cookie)
    at = C.offset(65, COLD)
    old_body = raw[at:at + COLD_SIZE]
    assert digest(old_body) == OLD_COLD_PIN
    assert old_body == old_cold['images']['COLD65'].ljust(COLD_SIZE, b'\xea')
    redirect = C.offset(65, 0xaf00)
    assert raw[redirect:redirect+3] == b'\x4c' + J.u16(old_cold['symbols']['JaySelect'])
    hot_at = C.offset(94, 0xb27f)
    hot = raw[hot_at:hot_at+129]
    assert digest(hot) == OLD_HOT_PIN and hot.count(Weapon.COOKIE) == 1
    cookie_at = hot_at + hot.index(Weapon.COOKIE)

    edits = (
        (at, cold['images']['COLD65'].ljust(COLD_SIZE, b'\xea')),
        (redirect + 1, J.u16(cold['symbols']['JaySelect'])),
        (cookie_at, cookie),
        (C.CHR + PACKET_PAGE * 1024, packet),
        (C.CHR + CHR_PAGE * 1024, carrier),
    )
    if movement:
        edits += ((C.CHR + MOTION_PAGE * 1024, movement_row),)
    if extra_segments:
        edits += ((C.CHR + EXTRA_PAGE * 1024, extra_row),)
    if stage_override is not None:
        edits += ((C.CHR + 331 * 1024, stage),)
    image = bytearray(raw)
    for start, data in edits:
        image[start:start+len(data)] = data
    assert page(image, 216) == page(raw, 216)
    assert page(image, 331) + page(image, 332) == stage
    return bytes(image), dict(cold=cold, transfer=transfer, alternate=alternate,
                              cookie=cookie, carrier=bytes(carrier), fields=fields, aliases=aliases,
                              descriptor=descriptor,
                              transferred=(bytes(carrier) + movement_row + extra_row)[:copy_pages*256+(224 if extra_segments else 0)],
                              edits=[(start, len(data)) for start, data in edits])


def cold_checks(trial, linked):
    points = {i['pc'] for i in linked['transfer']['instructions']}
    cookie = linked['cookie']
    descriptor, transferred = linked['descriptor'], linked['transferred']
    reads = descriptor[0] * 2050
    seen = set()

    def seed():
        m = C.Common.blank(trial)
        C.Common.scene(m, 16)
        m[0x730b] = 32
        return m

    def call(m, interrupts=False):
        descriptors = []
        cpu = C.ColdVector.entry(m)
        at = linked['cold']['symbols']['JaySceneOrRetire']
        m[0x16c], m[0x16d] = at & 255, at >> 8

        def observe(memory, current):
            bank = memory.rawtags[1]
            if bank == 251 and current.pc == 0xaf40:
                pointer = memory[6] + 256 * memory[7]
                assert 0x101 + current.sp <= pointer and pointer + len(descriptor) <= 0x200
                descriptors.append(bytes(memory[pointer:pointer + len(descriptor)]))
            if bank == 3 and current.pc in points:
                assert current.p & 4 and memory.rawtags[2] == 2
                assert not any(header[0] for header in C.Common.headers(memory))
                if interrupts and current.pc not in seen:
                    seen.add(current.pc)
                    _, fork = C.Vector.clone(memory, current)
                    C.ColdVector.interrupt(fork, 'FF')

        C.Vector.finish(m, cpu, Weapon.Stock.STOP, observe)
        assert (cpu.a, cpu.x, cpu.y, cpu.p & 0xef) == (83, 71, 109, 0x21)
        return descriptors

    m = seed()
    assert call(m, interrupts=True) == [descriptor]
    assert m.ppu_reads == reads and C.Common.headers(m) == (cookie,) * 2
    assert bytes(m.ram[3][0x1400:0x1400+len(transferred)]) == transferred
    assert call(m) == [] and m.ppu_reads == reads
    faults = ((3, 0x400), (3, 0x7c0), (3, 0x1400), (3, 0x1400+len(transferred)-1))
    if len(descriptor) >= len(SCROLL_DESCRIPTOR):
        faults += ((3, 0x800), (3, 0x1800))
    if descriptor == FULL_DESCRIPTOR:
        faults += ((3, 0xc00), (3, 0x1c00))
    for address in faults:
        m = seed()
        m.corrupt_at = address
        assert call(m) == [descriptor]
        assert not any(header[0] for header in C.Common.headers(m)), address
    return dict(cold_PPU_reads=reads, warm_PPU_reads=0, copy_faults=len(faults), cold_NMI_cuts=len(seen))


def gameplay(trial, linked, *, directed_weapon):
    m = C.menu(trial, 1, {'images': {}})
    m.__class__ = Weapon.Draw.DmaBus
    m.dma = None
    state = []
    calls = Counter()
    prior_cells = []
    fields = linked['fields']
    symbols = linked['alternate']['symbols']
    for _ in range(650):
        active = tuple(N.get(m, name) for name in ('OperMode', 'OperMode_Task', 'GameEngineSubroutine')) == (1, 3, 8)
        if active and len(state) == 22:
            break
        m.controller_pad = 64 if active and 4 <= len(state) < 20 else 0
        m.dma = None

        def observe(memory, cpu):
            if not active or memory.rawtags[1] != 3:
                return
            if cpu.pc == symbols['AlternateInput']:
                assert C.Common.headers(memory) == (linked['cookie'],) * 2
                if directed_weapon and not calls['input']:
                    # Pause-selection state is supplied only in this directed
                    # fixture. The cartridge loader and call sites are real.
                    for key, value in ((0xb7, 2), (0xb8, 2), (0xb1, 63)):
                        m.ram[2][fields[key] - 0xc000] = value
                calls['input'] += 1
            elif cpu.pc == symbols['SpreadFlight']:
                calls['angled_rounds'] += 1

        C.Game.frame(m, observe)
        if not active:
            continue
        assert N.get(m, 'NumberofLives') == 2
        if prior_cells:
            assert m.dma is not None and sorted(Weapon.Draw.cells(m.dma)) == prior_cells
            assert m.chr_latches[0] == 216
            calls['DMA'] += 1
        rounds = [Weapon.F.slot(m, slot) for slot in Weapon.SLOTS if Weapon.F.slot(m, slot)[9]]
        prior_cells = sorted(bytes((row[7]-8, 40, 0, row[6]-4)) for row in rounds)
        assert sorted(Weapon.Draw.cells(m[0x200:0x300])) == prior_cells
        assert not any(N.get(m, 'JnShotKind', i) for i in range(6))
        state.append((m.ram[2][fields[0xb1]-0xc000], [(row[6], row[7], row[4], row[5]) for row in rounds]))
    assert len(state) == 22 and calls['input'] == 22 and calls['DMA'] > 0
    if directed_weapon:
        assert [ammo for ammo, _ in state] == [63]*4 + [61]*18
        assert state[4][1] == [(57, 191, 80, 0), (56, 189, 72, 230), (56, 192, 72, 26)]
        assert calls['angled_rounds'] > 0
    else:
        assert state[4] == (0, [(56, 191, 64, 0)])
        assert state[5] == (0, [(60, 191, 64, 0)])
        assert calls['angled_rounds'] == 0
    return dict(calls, first_rounds=state[4][1], ammo=state[-1][0], lives=2)


def scrolling_proposal(raw):
    carrier_ownership(raw, MOTION_PAGE)
    seed, trial, _ = Motion.parent(raw=raw, pin=PIN, cookie=Weapon.COOKIE)
    template = bytes(seed.ram[3][0x88d:0x8c0])
    work, fields = Motion.assemble_handoff(trial, template, origin=0xb800, control_tail=True)
    image, linked = proposal(raw, movement=work)
    return image, dict(linked, motion=work, motion_fields=fields)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scroll', action='store_true')
    parser.add_argument('--prepare', type=Path)
    args = parser.parse_args()
    raw = H.ROM.read_bytes()
    print('Current CHR222 ownership', carrier_ownership(raw), flush=True)
    image, linked = scrolling_proposal(raw) if args.scroll else proposal(raw)
    print(json.dumps(dict(transport_SHA256=digest(image), cookie=linked['cookie'].hex(),
                          spans=linked['edits']), sort_keys=True), flush=True)
    trial = dict(W.Symbols.bundle(), raw=image)
    print('Native cold transport', cold_checks(trial, linked), flush=True)
    stock = gameplay(trial, linked, directed_weapon=False)
    spread = gameplay(trial, linked, directed_weapon=True)
    print(json.dumps(dict(passed=True, stock=stock, spread=spread, output_files=0), sort_keys=True), flush=True)
    if args.prepare:
        output = args.prepare.resolve()
        assert output.is_relative_to(H.ROOT / 'build') and output != H.ROOT / 'build'
        output.mkdir(parents=True, exist_ok=True)
        with (output / 'candidate.nes').open('xb') as file:
            file.write(image)
        assert (output / 'candidate.nes').read_bytes() == image


if __name__ == '__main__':
    main()
