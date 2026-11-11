"""Prove storage for the earned-upgrade core alongside Jay's machine gun."""

import argparse
from itertools import product
import json
from unittest.mock import patch

import check_jay_silius_machinegun_1111 as Jay
import trace_steve_shatterhand_upgrades_1111 as Upgrade


T, Steve = Jay.T, Jay.Steve
C, H, N = Jay.C, Jay.H, Jay.N
PAGE, MIRROR = 230, 226
ORIGIN, STATE = 0xc100, 0xc1f0
BOOT, BOOT_SIZE = 0xb100, 64
ALIAS, ALIAS_SIZE = 0xa9c0, 64
ALIAS_FIX, ALIAS_FIX_SIZE = 0xa9b8, 8
OLD_NMI = H.ROOT / 'tools/reference/sonic_sms_native_skin_1110.s'
JAY_PIN = 'c8d328a27efbc900216985aeb86600a1f626f8cc76e93a91bb30b2c1f8c2e727'
DESCRIPTOR = bytes((9, 5)) + Steve.DESCRIPTOR[2:11] + bytes((PAGE, 0)) + Steve.DESCRIPTOR[11:]


def skin_alias(raw):
    source = OLD_NMI.read_text().split('.segment "NMI"\n.org $a9c0\n')[1]
    head = 'SonicSkinSelect=$b6cb\n.segment "NMI"\n'
    layout = {'NMI': (ALIAS, ALIAS_SIZE)}
    old = H.assemble(head + source, layout)
    at = C.offset(62, ALIAS)
    assert raw[at:at+ALIAS_SIZE] == old['images']['NMI'].ljust(ALIAS_SIZE, b'\xea')
    edits = (
        ('    plp\n    ora #0\n    rts\nKamikazePage:', '    jmp Return\nKamikazePage:'),
        ('    clc\n    adc #$a8', '    adc #$a7'),  # CMP #$84 set carry.
        ('Return:\n    plp', '    cmp #$e6\n    beq RebindMirror\nReturn:\n    plp'),
    )
    for before, after in edits:
        assert source.count(before) == 1
        source = source.replace(before, after)
    source += '\n.segment "MIRROR"\nRebindMirror:\n    lda #$e2\n    jmp Return\n'
    new = H.assemble(head + source, layout | {'MIRROR': (ALIAS_FIX, ALIAS_FIX_SIZE)})
    return old, new


def allocate(raw, cookie):
    assert T.digest(raw) == JAY_PIN
    assert T.page(raw, PAGE) == T.page(raw, MIRROR)
    physical = T.page

    def verify_mirror(image, page):
        # The census tests the historical page-2 duplicate before it audits
        # reader reachability. Our duplicate is verified separately above.
        return physical(image, 2 if page == PAGE else page)

    with patch.multiple(T, PIN=JAY_PIN, EXTRA_PAGE=PAGE, page=verify_mirror):
        owners = T.carrier_ownership(raw, PAGE)
    old_skin, new_skin = skin_alias(raw)
    symbols = {name: STATE+i for i, name in enumerate(Upgrade.ALIASES)}
    constants = ''.join(f'{name}=${at:04x}\n' for name, at in symbols.items())
    worker = H.assemble(constants + Upgrade.SOURCE.read_text(), {'UPGRADE': (ORIGIN, STATE-ORIGIN)})
    code = worker['images']['UPGRADE']
    transfer = H.assemble(f'''
.segment "COPY"
    ldy #0
CopyUpgrade:
    lda $b000,y
    sta ${ORIGIN:04x},y
    cmp ${ORIGIN:04x},y
    bne BadCopy
    iny
    cpy #{len(code)}
    bne CopyUpgrade
    lda #$40
    sta $03
    jmp $a004
BadCopy:
    clc
    rts
''', {'COPY': (BOOT, BOOT_SIZE)})['images']['COPY']
    # The incumbent copier rewrites B000..B3BE. Zero the staging suffix
    # so its B3BF..B3FF padding matches the original cold image exactly.
    row = (code.ljust(0x100, b'\xea') + transfer).ljust(1024, b'\x00')

    original = T.page(raw, T.PACKET_PAGE)
    assert original[:4] == bytes.fromhex('a9408503')
    packet = b'\x4c' + T.J.u16(BOOT) + b'\xea' + original[4:]
    alias = new_skin['images']['NMI'].ljust(ALIAS_SIZE, b'\xea')
    mirror = new_skin['images']['MIRROR'].ljust(ALIAS_FIX_SIZE, b'\xff')
    next_cookie = cookie[:4] + bytes.fromhex(T.digest(cookie + DESCRIPTOR + packet + row + alias + mirror))[:12]
    old_cold = Steve.cold_program(Steve.DESCRIPTOR, cookie)
    new_cold = Steve.cold_program(DESCRIPTOR, next_cookie)
    assert len(old_cold['images']['COLD65']) == 159 and len(new_cold['images']['COLD65']) == 161
    out = bytearray(raw)

    def edit(at, before, after):
        assert len(before) == len(after) and raw[at:at+len(before)] == before, hex(at)
        out[at:at+len(after)] = after

    edit(C.offset(62, ALIAS), old_skin['images']['NMI'].ljust(ALIAS_SIZE, b'\xea'), alias)
    edit(C.offset(62, ALIAS_FIX), b'\xff'*ALIAS_FIX_SIZE, mirror)
    old_entry, new_entry = (link['symbols']['SonicGraphics'] for link in (old_skin, new_skin))
    edit(C.offset(62, 0xb690), b'\x4c'+T.J.u16(old_entry), b'\x4c'+T.J.u16(new_entry))
    edit(C.offset(65, T.COLD), old_cold['images']['COLD65'].ljust(T.COLD_SIZE, b'\xea'),
         new_cold['images']['COLD65'].ljust(T.COLD_SIZE, b'\xea'))
    edit(C.offset(65, 0xaf01), T.J.u16(old_cold['symbols']['JaySelect']),
         T.J.u16(new_cold['symbols']['JaySelect']))
    edit(C.offset(94, 0xb2ef), cookie, next_cookie)
    edit(C.CHR+1024*T.PACKET_PAGE, original, packet)
    edit(C.CHR+1024*PAGE, T.page(raw, PAGE), row)
    return bytes(out), dict(cookie=next_cookie, code=code, owners=owners, symbols=worker['symbols'], cold=new_cold,
                            old_skin=old_skin, new_skin=new_skin, transfer_bytes=len(transfer))


def alias_parity(raw, candidate, info):
    from py65.devices.mpu6502 import MPU

    def run(image, mode, page, flags):
        mem = [0]*65536
        at = C.offset(62, ALIAS_FIX)
        mem[ALIAS_FIX:ALIAS+ALIAS_SIZE] = image[at:at+ALIAS_SIZE+ALIAS_FIX_SIZE]
        mem[0x147] = page
        cpu = MPU(memory=mem, pc=ALIAS)
        cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = mode, 74, 179, flags, 224
        cpu.stPushWord(0x5aff)
        for _ in range(40):
            if (cpu.pc, cpu.sp) == (0x5b00, 224):
                return cpu.a, cpu.x, cpu.y, cpu.p, mem[0x5130]
            cpu.step()
        raise AssertionError((mode, page, flags, cpu.pc))

    samples = list(product((0x85,), range(256), (0x30, 0x31, 0x71, 0xf1)))
    samples += list(product((m for m in range(256) if m != 0x85), (0, 16, 17, 18, 19, 147, 255), (0x31,)))
    rebound = set()
    for mode, page, flags in samples:
        before, after = (run(image, mode, page, flags) for image in (raw, candidate))
        if mode == 0x85 and before[0] == PAGE:
            assert after == (MIRROR, *before[1:])
            assert T.page(raw, before[0]) == T.page(candidate, after[0])
            rebound.add(page)
        else:
            assert before == after, (mode, page, flags, before, after)
    assert rebound == {0x13, 0x93}
    old_entry, new_entry = (info[key]['symbols']['SonicGraphics'] for key in ('old_skin', 'new_skin'))
    return dict(comparisons=len(samples), rebound=sorted(rebound), graphics_entry=(old_entry, new_entry))


def play_parity(raw, candidate, info, old_cookie):
    from collections import Counter

    report = {}
    pad_sequence = [0]*6 + [64]*12 + [1]*19 + [129]*9 + [2]*15 + [0]*10 + [64]*9
    begin, end = ORIGIN-0xc000, ORIGIN-0xc000+len(info['code'])

    def snapshot(memory):
        app = C.Vector.app(memory)
        ram = list(app[3])
        ram[2] = ram[2][:begin] + ram[2][end:0x1fe0] + ram[2][0x1ff0:]
        ram[3] = ram[3][:0x1fe0] + ram[3][0x1ff0:]
        return (*app[:3], ram, *app[4:], memory.vram, memory.chr_latches)

    for variant, name in enumerate(('Mike', 'Jay', 'Steve')):
        before, old_epoch = Steve.Live.opening(raw, variant)
        after, new_epoch = Steve.Live.opening(candidate, variant)
        assert old_epoch == new_epoch == 167
        if variant:
            assert before.ppu_reads == 16400 and after.ppu_reads == 18450
            assert C.Common.headers(before) == (old_cookie,)*2
            assert C.Common.headers(after) == (info['cookie'],)*2
            assert bytes(before.ram[2][begin:end]) == bytes(end-begin)
            assert bytes(after.ram[2][begin:end]) == info['code']
        else:
            assert before.ppu_reads == after.ppu_reads == 0
            assert bytes(after.ram[2][begin:end]) == bytes(end-begin)
        reads = [before.ppu_reads, after.ppu_reads]
        calls = [Counter(), Counter()]
        for pad in pad_sequence:
            for memory, count in zip((before, after), calls, strict=True):
                memory.controller_pad = pad

                def observe(m, cpu):
                    if (m.rawtags[1], cpu.pc) == (3, Jay.LIVE_ORIGIN):
                        count['JayMachinegun'] += 1
                    if (m.rawtags[2], cpu.pc) == (2, Steve.ORIGIN):
                        count['SteveMotion'] += 1

                C.Game.frame(memory, observe)
            assert snapshot(before) == snapshot(after), (name, pad, Steve.Live.player(after))
        assert calls[0] == calls[1]
        if variant == 1:
            assert calls[1]['JayMachinegun']
        if variant == 2:
            assert calls[1]['SteveMotion']
        report[name] = dict(opening=new_epoch, updates=len(pad_sequence), cold_reads=reads,
                            terminal=Steve.Live.player(after), calls=dict(calls[1]))
    return report


def cold_fail_closed(candidate, info):
    trial = dict(Jay.W.Symbols.bundle(), raw=candidate)
    stop = T.Weapon.Stock.STOP
    target = info['cold']['symbols']['JaySceneOrRetire']
    last = ORIGIN-0xc000+len(info['code'])-1
    faults = ((3, 0x1000), (2, ORIGIN-0xc000), (2, last))

    def call(memory):
        cpu = C.ColdVector.entry(memory)
        memory[0x16c], memory[0x16d] = target & 255, target >> 8
        C.Vector.finish(memory, cpu, stop)
        assert (cpu.a, cpu.x, cpu.y, cpu.p & 0xef) == (83, 71, 109, 0x21)

    def seed():
        m = C.Common.blank(trial)
        C.Common.scene(m, 16)
        m[0x730b] = 32
        return m

    positive = seed()
    call(positive)
    assert positive.ppu_reads == 18450
    assert C.Common.headers(positive) == (info['cookie'],)*2
    call(positive)
    assert positive.ppu_reads == 18450
    for fault in faults:
        m = seed()
        m.corrupt_at = fault
        call(m)
        assert not any(header[0] for header in C.Common.headers(m)), fault
    return dict(warm_reads=0, fault_locations=faults)


def full_routes(candidate, info, machinegun):
    import replay_steve_route_1111 as Route

    jay = Jay.earned_route(candidate, machinegun | {'cookie': info['cookie']})
    m, epoch = Steve.Live.opening(candidate, 2)
    assert epoch == 167 and C.Common.headers(m) == (info['cookie'],)*2
    punch = Steve.S.link(Jay.W.Symbols.bundle())
    first = Route.first_pipe(m, punch)
    steve = Route.continue_route(m, target=3200, max_updates=4000)
    assert (*Steve.Live.mode(m), steve['level']) == (1, 3, 8, 1)
    assert steve['area_type'] == 2 and steve['lives'] == 2 and steve['health'] > 0
    assert set(steve['passed']) == set(Route.PIPES + Route.GAPS)
    assert bytes(m.ram[2][ORIGIN-0xc000:ORIGIN-0xc000+len(info['code'])]) == info['code']
    return dict(Jay=jay, Steve=dict(terminal=(steve['x'], steve['y']), health=steve['health'],
                                   lives=steve['lives'], crossings=steve['passed'], first_pipe=first['pipe1']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--full-routes', action='store_true')
    args = parser.parse_args()
    raw = Upgrade.D.HOST.read_bytes()
    existing = None
    if T.digest(raw) == Upgrade.HOST_PIN:
        jay, existing = Jay.proposal(raw)
        cookie = existing['cookie']
    else:
        jay = raw
        assert T.digest(jay) == JAY_PIN
        at = C.offset(94, 0xb2ef)
        cookie = raw[at:at+16]
    image, info = allocate(jay, cookie)
    aliases = alias_parity(jay, image, info)
    play = play_parity(jay, image, info, cookie)
    negatives = cold_fail_closed(image, info)
    result = dict(passed=True, existing_Jay=JAY_PIN, transport_SHA256=T.digest(image),
                  extra_page=PAGE, mirror=MIRROR, descriptor=DESCRIPTOR.hex(),
                  resident_code_bytes=len(info['code']), transfer_bytes=info['transfer_bytes'],
                  owners=info['owners'], aliases=aliases, real_menu_and_Main=play,
                  cold_negatives=negatives, output_files=0)
    if args.full_routes:
        if existing is None:
            rebuilt, existing = Jay.proposal(Jay.recover_parent(jay))
            assert rebuilt == jay
        result['full_routes'] = full_routes(image, info, existing)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
