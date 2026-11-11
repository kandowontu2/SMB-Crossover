"""Prove storage for the earned-upgrade core alongside Jay's machine gun."""

import argparse
from itertools import product
import json
from unittest.mock import patch

import check_jay_silius_machinegun_1111 as Jay
import check_prince_native_flag_1111 as Prince
import trace_steve_shatterhand_upgrades_1111 as Upgrade


T, Steve = Jay.T, Jay.Steve
C, H, N = Jay.C, Jay.H, Jay.N
PAGE, MIRROR = 230, 226
ORIGIN, STATE = 0xc100, 0xc1f0
BOOT = 0xb100
INGRESS, INGRESS_SIZE = 0xc200, 0x1bf
LIFECYCLE, LIFECYCLE_SIZE = 0xc400, 0x80
EXTRA, EXTRA_SIZE = 0xc480, 0x20
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


def transfer_program(regions, *, reuse_y=False):
    asm = ['.segment "COPY"']
    previous_count = 0
    for index, (source, target, data) in enumerate(regions):
        for offset in range(0, len(data), 256):
            count = min(len(data) - offset, 256)
            label = f'Copy{index}_{offset}'
            if not reuse_y or previous_count != 256:
                asm.append('    ldy #0')
            asm += [f'{label}:', f'    lda ${source+offset:04x},y',
                    f'    sta ${target+offset:04x},y', f'    cmp ${target+offset:04x},y',
                    '    bne BadCopy', '    iny']
            if count < 256:
                asm.append(f'    cpy #{count}')
            asm.append(f'    bne {label}')
            previous_count = count
    asm += ['    lda #$40', '    sta $03', '    jmp $a004', 'BadCopy:']
    asm += ['    clc', '    rts']
    return H.assemble('\n'.join(asm) + '\n', {'COPY': (BOOT, 0x80)})['images']['COPY']


def allocate(raw, cookie, *, ingress=b'', lifecycle=b'', extra=b'', binding=b''):
    pin = T.digest(raw)
    assert pin in (JAY_PIN, Prince.CANDIDATE)
    assert T.page(raw, PAGE) == T.page(raw, MIRROR)
    physical = T.page

    def verify_mirror(image, page):
        # The census tests the historical page-2 duplicate before it audits
        # reader reachability. Our duplicate is verified separately above.
        return physical(image, 2 if page == PAGE else page)

    with patch.multiple(T, PIN=pin, EXTRA_PAGE=PAGE, page=verify_mirror):
        owners = T.carrier_ownership(raw, PAGE)
    old_skin, new_skin = skin_alias(raw)
    symbols = {name: STATE+i for i, name in enumerate(Upgrade.ALIASES)}
    constants = ''.join(f'{name}=${at:04x}\n' for name, at in symbols.items())
    worker = H.assemble(constants + Upgrade.SOURCE.read_text(), {'UPGRADE': (ORIGIN, STATE-ORIGIN)})
    code = worker['images']['UPGRADE']
    assert len(ingress) <= INGRESS_SIZE and len(lifecycle) <= LIFECYCLE_SIZE and len(extra) <= EXTRA_SIZE
    regions = ((0xb000, ORIGIN, code), (0xb200, INGRESS, ingress),
               (0xb180, LIFECYCLE, lifecycle), (0xb160, EXTRA, extra))
    transfer = transfer_program(regions, reuse_y=bool(extra))
    if extra:
        assert len(transfer) <= 0x60
    row = bytearray(1024)
    row[:0x100] = code.ljust(0x100, b'\xea')
    row[0x100:0x100+len(transfer)] = transfer
    for address, _, data in regions[1:]:
        offset = address - 0xb000
        row[offset:offset+len(data)] = data
    # The incumbent stage loader can reject a corrupted transfer before our
    # copier runs. It only restores B000–B3BE, so leave the suffix zero.
    assert not any(row[0x3bf:])
    row = bytes(row)

    original = T.page(raw, T.PACKET_PAGE)
    assert original[:4] == bytes.fromhex('a9408503')
    packet = b'\x4c' + T.J.u16(BOOT) + b'\xea' + original[4:]
    alias = new_skin['images']['NMI'].ljust(ALIAS_SIZE, b'\xea')
    mirror = new_skin['images']['MIRROR'].ljust(ALIAS_FIX_SIZE, b'\xff')
    next_cookie = cookie[:4] + bytes.fromhex(T.digest(cookie + DESCRIPTOR + packet + row + alias + mirror + binding))[:12]
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
                            old_skin=old_skin, new_skin=new_skin, transfer_bytes=len(transfer),
                            residents=tuple(sorted((target, data) for _, target, data in regions if data)))


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
    regions = tuple((origin-0xc000, data) for origin, data in info['residents'])
    preserved = []
    previous = 0
    for start, data in regions:
        preserved.append(slice(previous, start))
        previous = start + len(data)
    preserved.extend((slice(previous, 0x1fe0), slice(0x1ff0, None)))

    def snapshot(memory):
        app = C.Vector.app(memory)
        ram = list(app[3])
        ram[2] = b''.join(ram[2][piece] for piece in preserved)
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
        else:
            assert before.ppu_reads == after.ppu_reads == 0
        for start, data in regions:
            assert before.ram[2][start:start+len(data)] == bytes(len(data))
            assert after.ram[2][start:start+len(data)] == (data if variant else bytes(len(data)))
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
            for start, data in regions:
                assert before.ram[2][start:start+len(data)] == bytes(len(data))
                assert after.ram[2][start:start+len(data)] == (data if variant else bytes(len(data)))
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
    faults = [(3, 0x1000)]
    for origin, data in info['residents']:
        first = origin - 0xc000
        faults.extend(((2, first), (2, first + len(data) - 1)))

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
    for origin, data in info['residents']:
        first = origin - 0xc000
        assert positive.ram[2][first:first+len(data)] == data
    assert not any(positive.ram[3][0x13bf:0x1400])
    call(positive)
    assert positive.ppu_reads == 18450
    for fault in faults:
        m = seed()
        m.corrupt_at = fault
        call(m)
        assert not any(header[0] for header in C.Common.headers(m)), fault
        assert not any(m.ram[3][0x13bf:0x1400]), fault
    return dict(warm_reads=0, fault_locations=faults)


def extension_transport(raw, cookie):
    # Distinct nonzero patterns at both boundaries also exercise the full
    # indexed page loop and short last copy before the zero staging suffix.
    ingress = bytes(1 + (i * 17) % 255 for i in range(INGRESS_SIZE))
    lifecycle = bytes(1 + (i * 33) % 255 for i in range(LIFECYCLE_SIZE))
    extra = bytes(1 + (i * 65) % 255 for i in range(EXTRA_SIZE))
    candidate, info = allocate(raw, cookie, ingress=ingress, lifecycle=lifecycle, extra=extra)
    result = cold_fail_closed(candidate, info)
    return dict(regions=[(origin, len(data)) for origin, data in info['residents']],
                transfer_bytes=info['transfer_bytes'], opening=play_parity(raw, candidate, info, cookie), **result)


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


def source_image(raw):
    pin = T.digest(raw)
    if pin == Upgrade.HOST_PIN:
        return Jay.proposal(raw)[0]
    assert pin in (JAY_PIN, Prince.CANDIDATE)
    return raw


def original_jay_image(raw):
    if T.digest(raw) == Prince.CANDIDATE:
        raw = Prince.Source.Signed.recover_parent(Prince.Source.recover_parent(raw))
    assert T.digest(raw) == JAY_PIN
    return raw


def latest_prince_parity(raw, candidate, cookie):
    jay = original_jay_image(raw)
    earlier, _ = allocate(jay, cookie)
    for parent, latest, previous, result in zip(jay, raw, earlier, candidate, strict=True):
        assert not (parent != latest and parent != previous)
        assert result == (latest if parent != latest else previous)
    (before, _), (after, _) = Prince.B.cold(raw), Prince.B.cold(candidate)
    native = Prince.native_flag(after, 3137, 60)
    assert native == Prince.native_flag(before, 3137, 60)
    trace, writes = native
    assert len(writes) == 2 and trace[-1] == ((3161, 176, 3, 3, 23, 1), 5)
    return dict(unchanged_1_1_flag_approach_updates=len(trace), native_events=writes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--full-routes', action='store_true')
    parser.add_argument('--extension', action='store_true')
    args = parser.parse_args()
    raw = source_image(Upgrade.D.HOST.read_bytes())
    at = C.offset(94, 0xb2ef)
    cookie = raw[at:at+16]
    image, info = allocate(raw, cookie)
    aliases = alias_parity(raw, image, info)
    play = play_parity(raw, image, info, cookie)
    negatives = cold_fail_closed(image, info)
    result = dict(passed=True, existing_Jay=JAY_PIN, parent_SHA256=T.digest(raw), transport_SHA256=T.digest(image),
                  extra_page=PAGE, mirror=MIRROR, descriptor=DESCRIPTOR.hex(),
                  resident_code_bytes=len(info['code']), transfer_bytes=info['transfer_bytes'],
                  owners=info['owners'], aliases=aliases, real_menu_and_Main=play,
                  cold_negatives=negatives, output_files=0)
    if T.digest(raw) == Prince.CANDIDATE:
        result['prince'] = latest_prince_parity(raw, image, cookie)
    if args.extension:
        result['extension'] = extension_transport(raw, cookie)
    if args.full_routes:
        jay = original_jay_image(raw)
        rebuilt, existing = Jay.proposal(Jay.recover_parent(jay))
        assert rebuilt == jay
        result['full_routes'] = full_routes(image, info, existing)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
