"""Qualify retirement of the duplicate punch suffix from Steve's CHR306."""

import argparse
from hashlib import sha256
import json

import check_prince_brick_support_1111 as Host
import check_steve_shatterhand_companion_transport_1111 as Transport
import steve_armor_transport_1112 as Entry


SOURCE = Entry.ROOT/'tools/reference/steve_armor_cold_space_1112.s'
BOOT = Entry.CHR+375*1024+0x300
SUFFIX = Entry.CHR+306*1024+0x280
PUNCH = Entry.CHR+220*1024+0x280
SIZE = 384
OLD_BOOT_SHA = '855f5fff08090ff2e0892560bd723fe40b7b3f41deb0c515135e909246ae311a'
OLD_BOOT = bytes.fromhex(
    '20c0a7905da933a2ce202ccd9054a932a2d8202ccd904b204dda9046a950a2d0202ccd903da952a2d44c2ccd'
    '850586068604a00084032064cda204ad07209103c8d0f8e604cad0f3a50685042064cda204ad0720d103d00a'
    'c8d0f6e604cad0f138601860a9018d3051a5058d2351a9008d30512c0220a90c8d0620a9008d0620ad072060eaeaeaea')
UPGRADE = Entry.CHR+371*1024
BRIDGE = Entry.CHR+307*1024


def proposal(raw, cookie, payload, *, scatter=False, extra_edits=()):
    assert len(payload) == SIZE
    old_boot = raw[BOOT:BOOT+136]
    assert old_boot == OLD_BOOT and Entry.digest(old_boot) == OLD_BOOT_SHA
    assert raw[SUFFIX:SUFFIX+SIZE] == raw[PUNCH:PUNCH+SIZE]
    definitions = 'STEVE_COLD_SCATTER=1\n' if scatter else ''
    layout = {'STEVE_ARMOR_COLD': (0xcd00, 136)}
    if scatter:
        layout |= {'STEVE_ARMOR_SCATTER': (0xc3bf, 60), 'STEVE_ARMOR_SCATTER_MAP': (0xc8c0, 32)}
    program = Entry.U.H.assemble(definitions+SOURCE.read_text(), layout)
    new_boot = program['images']['STEVE_ARMOR_COLD']
    assert len(new_boot) == len(old_boot) and program['symbols']['SteveLateRow'] == 0xcd2c
    changes = [(BOOT, old_boot, new_boot), (SUFFIX, raw[PUNCH:PUNCH+SIZE], payload)]
    if scatter:
        body = program['images']['STEVE_ARMOR_SCATTER']
        mapper = program['images']['STEVE_ARMOR_SCATTER_MAP']
        assert len(body) == 60 and len(mapper) == 32
        assert raw[UPGRADE+0x12e:UPGRADE+0x130] == b'\xc0\xbf'
        changes += [(UPGRADE+0x3bf, bytes(60), body),
                    (UPGRADE+0x12f, b'\xbf', b'\xfb'),
                    (BRIDGE+0x3e0, bytes(32), mapper)]
    changes.extend(extra_edits)
    binding = b''.join(at.to_bytes(4, 'little')+after for at, _, after in changes)
    next_cookie = cookie[:4]+sha256(cookie+binding).digest()[:12]
    changes += [(Entry.prg(65, 0xa727), cookie, next_cookie), (Entry.prg(94, 0xb2ef), cookie, next_cookie)]
    output = bytearray(raw)
    prior_end = 16
    for at, before, after in sorted(changes):
        assert at >= prior_end and len(before) == len(after) and raw[at:at+len(before)] == before
        output[at:at+len(after)] = after
        prior_end = at+len(before)
    return bytes(output), next_cookie, program


def reverse(image, parent_cookie, *, scatter=False, extra_edits=()):
    parent = bytearray(image)
    parent[BOOT:BOOT+136] = OLD_BOOT
    parent[SUFFIX:SUFFIX+SIZE] = image[PUNCH:PUNCH+SIZE]
    if scatter:
        parent[UPGRADE+0x3bf:UPGRADE+0x3fb] = bytes(60)
        parent[UPGRADE+0x12f] = 0xbf
        parent[BRIDGE+0x3e0:BRIDGE+0x400] = bytes(32)
    for at, before, _ in extra_edits:
        parent[at:at+len(before)] = before
    for at in (Entry.prg(65, 0xa727), Entry.prg(94, 0xb2ef)):
        parent[at:at+16] = parent_cookie
    payload = image[SUFFIX:SUFFIX+SIZE]
    parent = bytes(parent)
    assert proposal(parent, parent_cookie, payload, scatter=scatter, extra_edits=extra_edits)[0] == image
    return parent


def check(raw, *, scatter=False):
    payload = b'\xa9\x39\x60'+bytes((i*37+113)&255 for i in range(SIZE-3))
    candidate, new_cookie, program = proposal(raw, Entry.OLD_COOKIE, payload, scatter=scatter)
    assert reverse(candidate, Entry.OLD_COOKIE, scatter=scatter) == raw
    labels = program['symbols']
    C = Transport.C
    cuts = set()
    target = Transport.compact_cold(new_cookie, extended=True,
                                    upgrade=Entry.U.descriptor(371))['symbols']['JaySceneOrRetire']

    def seed(cart, variant):
        memory = C.Common.blank(Host.C.Start.W.bundle(cart))
        C.Common.scene(memory, 16)
        memory[0x730b] = variant << 5
        return memory

    def run(m, expected, *, interrupt=False, fault=None):
        cpu = C.ColdVector.entry(m)
        m[0x16c], m[0x16d] = target&255, target>>8

        def observe(memory, current):
            pc = current.pc
            in_scatter = scatter and (0xc3bf <= pc < 0xc3fb or 0xc8c0 <= pc < 0xc8e0)
            if memory.rawtags[1:3] != [3, 2] or not (0xcd00 <= pc < 0xcd88 or in_scatter):
                return
            assert current.p&4 and all(header != expected for header in C.Common.headers(memory))
            during_row = pc == labels['SteveLateCompare'] and memory[4]*256+current.y == fault
            during_scatter = scatter and pc == labels['ArmorScatterRead'] and 0xcd00+current.y == fault
            if fault is not None and (during_row or during_scatter):
                memory.corrupt_at = (2, fault-0xc000)
            key = (current.pc, bool(current.p&1), current.y in (0, 127, 128, 255))
            if interrupt and key not in cuts:
                cuts.add(key)
                _, branch = C.Vector.clone(memory, current)
                C.ColdVector.interrupt(branch, 'FF')

        C.Vector.finish(m, cpu, Transport.T.Weapon.Stock.STOP, observe)
        assert (cpu.a, cpu.x, cpu.y, cpu.p&0xef, cpu.sp) == (83, 71, 109, 0x21, 224)

    rows = {}
    foreign = None
    for variant in (1, 2):
        before, after = seed(raw, variant), seed(candidate, variant)
        run(before, Entry.OLD_COOKIE)
        run(after, new_cookie, interrupt=variant==2)
        assert C.Common.headers(before) == (Entry.OLD_COOKIE,)*2
        assert C.Common.headers(after) == (new_cookie,)*2
        reads = 32032+274*scatter
        assert (before.ppu_reads, after.ppu_reads) == (32800, reads)
        assert before.ram[2][0x1a80:0x1c00] == after.ram[2][0x1a80:0x1c00] == raw[PUNCH:PUNCH+SIZE]
        resident = payload[:136] if scatter else candidate[BOOT:BOOT+136]
        assert bytes(after.ram[2][0xd00:0xd88]) == resident
        expected2 = bytearray(before.ram[2])
        expected3 = bytearray(before.ram[3])
        expected2[0xd00:0xd88] = resident
        if scatter:
            expected2[0x3bf:0x3fb] = program['images']['STEVE_ARMOR_SCATTER']
            expected2[0x8c0:0x8e0] = program['images']['STEVE_ARMOR_SCATTER_MAP']
            expected3[0x13bf:0x13fb] = program['images']['STEVE_ARMOR_SCATTER']
        expected2[0x1fe0:0x1ff0] = new_cookie
        expected3[0x1fe0:0x1ff0] = new_cookie
        assert after.ram[2] == expected2 and after.ram[3] == expected3, tuple(
            [(hex(i), a, b) for i, (a, b) in enumerate(zip(after.ram[bank], expected, strict=True)) if a != b][:64]
            for bank, expected in ((2, expected2), (3, expected3)))
        assert before.chr_latches == after.chr_latches and before.vram == after.vram
        run(after, new_cookie)
        assert after.ppu_reads == reads
        if scatter:
            from check_steve_armor_transport_1112 import call

            after.raw_page(2, 2)
            probe = Transport.N.NesMPU(memory=after)
            call(probe, 0xcd00)
            assert probe.a == 0x39
        if scatter and variant == 2:
            from prince_cold_packet_1111 import COOKIE as PRINCE_COOKIE

            before_foreign = tuple(bytes(after.ram[bank]) for bank in (2, 3))
            after[0x730b] = 0
            prince = C.Common.cold(after, 38)
            prince_cookie = candidate[PRINCE_COOKIE:PRINCE_COOKIE+16]
            assert C.Common.headers(after) == (prince_cookie,)*2 and prince['PPU_reads'] > 0
            assert bytes(after.ram[2][0xd00:0xd88]) != resident
            assert bytes(after.ram[3][0x13bf:0x13fb]) != before_foreign[1][0x13bf:0x13fb]
            C.Common.scene(after, 16)
            after[0x730b] = 0x40
            C.Common.clear_logs(after)
            prior_reads = after.ppu_reads
            run(after, new_cookie)
            assert after.ppu_reads-prior_reads == reads
            assert C.Common.headers(after) == (new_cookie,)*2
            assert bytes(after.ram[2][0xd00:0xd88]) == resident
            assert bytes(after.ram[3][0x13bf:0x13fb]) == before_foreign[1][0x13bf:0x13fb]
            for bank in (2, 3):
                markers = [value for b, at, value in after.ram_writes if b == bank and at == 0x1fe0]
                assert markers.index(0) < markers.index(new_cookie[0])
            foreign = dict(owner=38, ppu_reads=prince['PPU_reads'], return_ppu_reads=reads)
        rows[variant] = dict(old_ppu_reads=32800, new_ppu_reads=reads, warm_extra_reads=0)

    faults = (0xd800, 0xda7f, *((0xcd00, 0xcd87) if scatter else ()))
    for fault in faults:
        memory = seed(candidate, 2)
        run(memory, new_cookie, fault=fault)
        assert memory.corrupt_at == (2, fault-0xc000)
        assert not any(header[0] for header in C.Common.headers(memory))
    return dict(parent=Entry.digest(raw), canary_candidate=Entry.digest(candidate),
                cookie=new_cookie.hex(), loader_bytes=136, duplicate_storage_bytes=SIZE,
                unchanged_punch_bytes=SIZE, forced_blank_lag_NMI_cuts=len(cuts),
                fault_addresses=[hex(at) for at in faults], variants=rows,
                executable_canary_bytes=136 if scatter else 0, foreign_roundtrip=foreign, output_files=0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scatter', action='store_true')
    args = parser.parse_args()
    print(json.dumps(check(Entry.U.Upgrade.D.HOST.read_bytes(), scatter=args.scatter), sort_keys=True), flush=True)
