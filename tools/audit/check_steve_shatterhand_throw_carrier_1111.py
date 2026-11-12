"""Qualify a new Steve throw code row alongside the existing pose carrier."""

import argparse
import json
from itertools import product
from unittest.mock import patch

import check_steve_shatterhand_pose_carrier_1111 as Pose
import check_steve_shatterhand_throw_1111 as Throw


Late, Live, Laser = Pose.Late, Pose.Live, Pose.Laser
C, H, N, W, T = Late.C, Late.H, Late.N, Late.W, Late.T
BASE = '235de3ed2487cd3f93c695e1eb2ceec55c172cede3cb6d98c5309afbc7cfbe38'
SOURCE = H.ROOT / 'tools/reference/steve_shatterhand_throw_cold_1111.inc'
PAGE, MIRROR, PUNCH_PAGE = 306, 304, 220
ORIGIN, CAPACITY, DATA, DATA_CAPACITY = 0xd800, 640, 0xcd80, 128
STATE, STATE_CAPACITY = 0xc969, 23
ROLL_PC = 0xb06f
ROLL_OLD = bytes.fromhex('186902a201ea')
ROLL_NEW = bytes.fromhex('c93190026901')
STATE_FIELDS = dict(SteveThrowSelector=0xc969, SteveThrowTimer=0xc96a,
                    SteveThrowSpeed=0xc96b, SteveThrowAux=0xc96c,
                    SteveThrowAim=0xc96d, SteveThrowAnimAux=0xc96e, SteveThrowSound=0xc96f,
                    SteveThrowCameraX=0xc970, SteveThrowCameraY=0xc972,
                    SteveThrowQuadrant=0xc974, SteveThrowContact=0xc975, SteveThrowHealth=0xc976)


def funding(image):
    from audit_mega_giant_chr_candidates_1110_v1 import MAP_BANKS, compiled_readers, prg_at, table

    b = dict(W.Symbols.bundle(), raw=image)
    low = W.location(b, 'RlPoolChrLo')
    assert W.address(b, 'RlPoolChrLo') == 0xcc6d
    assert image[low:low+6] == bytes((108, 112, 116, 120, 48, 48))
    at = C.offset(79, ROLL_PC)
    assert image[at-3:at] == bytes.fromhex('b96dcc')
    assert image[at:at+6] == ROLL_OLD and at == 0x9f07f
    assert T.page(image, PAGE) == T.page(image, MIRROR) == bytes(1024)
    ledger = Late.Transport.LEDGER.read_bytes()
    assert C.digest(ledger) == Late.Transport.LEDGER_PIN
    domains = json.loads(ledger)
    for page in (PAGE, MIRROR):
        assert [name for name, values in domains['exact_finite_domains'].items()
                if page in values] == ['Roll body/effect']
        assert not any(page in row['pages'] for row in domains['inherited_private_writer_chunks_exact'])
    _, native = table(b, 'ChrPhysicalMap', 256)
    assert all(image[prg_at(bank, 0xe36):prg_at(bank, 0xe36)+256] == native for bank in MAP_BANKS)
    assert not any(PAGE in row['actual_mmc5_outputs'] for row in compiled_readers(b).values())
    return at, ROLL_OLD, ROLL_NEW


def mount(image, info, code, data, *, pose=False, extra_edits=()):
    """Bind the D800 prefix, CD80 data, and exact pre-existing DA80 suffix."""
    assert 0 < len(code) <= CAPACITY and 0 < len(data) <= DATA_CAPACITY
    old_source = ('STEVE_POSE_CARRIER=307\n' if pose else '') + Late.SOURCE.read_text()
    anchor = '    lda #$50                       ; CHR336, retired Roll slot 0 mirror\n'
    assert old_source.count(anchor) == 1
    layout = {'STEVE_LATE_COLD': (Late.BOOT, DATA-Late.BOOT)}
    old_boot = H.assemble(old_source, layout)['images']['STEVE_LATE_COLD'].ljust(256, b'\xea')
    new_source = old_source.replace(anchor, SOURCE.read_text() + '\n' + anchor)
    loader = H.assemble(new_source, layout)
    bootstrap = loader['images']['STEVE_LATE_COLD']
    assert len(bootstrap) == (127 if pose else 118)
    new_boot = bootstrap.ljust(DATA-Late.BOOT, b'\xea') + data.ljust(DATA_CAPACITY, b'\xea')
    punch = T.page(image, PUNCH_PAGE)
    carrier = code.ljust(CAPACITY, b'\xea') + punch[CAPACITY:]
    assert len(new_boot) == 256 and len(carrier) == 1024
    allocations = (funding(image),
                   (C.CHR+1024*PAGE, bytes(1024), carrier),
                   (C.CHR+1024*Late.BOOT_PAGE+0x300, old_boot, new_boot), *extra_edits)
    binding = b''.join(at.to_bytes(4, 'little')+len(new).to_bytes(4, 'little')+new
                       for at, _, new in sorted(allocations))
    old_cookie = info['cookie']
    cookie = old_cookie[:4] + bytes.fromhex(C.digest(old_cookie+info['descriptor']+binding))[:12]
    cold = Late.Transport.compact_cold(cookie, extended=True, upgrade=info['upgrade_descriptor'])
    old_resident = info['cold']['images']['COLD65'].ljust(T.COLD_SIZE, b'\xea')
    new_resident = cold['images']['COLD65'].ljust(T.COLD_SIZE, b'\xea')
    assert old_resident.replace(old_cookie, cookie) == new_resident
    edits = sorted((*allocations, (C.offset(65, T.COLD), old_resident, new_resident),
                    (C.offset(94, 0xb2ef), old_cookie, cookie)))
    output = bytearray(image)
    cursor = 16
    for at, old, new in edits:
        assert len(old) == len(new) and cursor <= at and image[at:at+len(old)] == old, hex(at)
        output[at:at+len(old)] = new
        cursor = at+len(old)
    return bytes(output), info | dict(cookie=cookie, cold=cold, throw_loader=loader, throw_stage=carrier,
                                      throw_edits=edits, throw_boot=new_boot, throw_state=dict(STATE_FIELDS))


def detached(donor):
    original, fields = Throw.link(donor)
    anchor = '\nSteveThrowAngles:'
    assert original['source'].count(anchor) == 1
    source = original['source'].replace(anchor, '\n.segment "THROW_DATA"'+anchor)
    linked = H.assemble(source, {'COMPANION': (0xc500, 0x300), 'LIFT': (0xc900, 0x400),
                                 'THROW': (ORIGIN, CAPACITY), 'THROW_DATA': (DATA, DATA_CAPACITY)})
    assert len(linked['images']['THROW']) == 590 and len(linked['images']['THROW_DATA']) == 64
    assert original['images']['THROW'][-64:] == linked['images']['THROW_DATA']
    return linked, fields


def live_link(donor, info):
    """Bind the source throw core to the already-loaded companion/lift code."""
    original, _ = detached(donor)
    fields = info['companion_fields'] | info['lift_fields'] | STATE_FIELDS
    # PlayLiftBot owns this two-byte pose; ordinary orbit has a separate pose.
    fields['SteveBotPose'] = fields['SteveLiftBotPose']
    required = set(Throw.ORIGINAL) | {'SteveThrowQuadrant', 'SteveBotRadius',
                                     'SteveBotVectorX', 'SteveBotVectorY'}
    assert required <= fields.keys(), required-fields.keys()
    symbols = {name: info['companion_symbols'][name] for name in ('PlayLiftBot', 'CompanionVector')}
    angles = original['images']['THROW_DATA']
    source = Live.bindings({name: fields[name] for name in required} | symbols) + Throw.SOURCE.read_text()
    source += '\n.segment "THROW_DATA"\nSteveThrowAngles: .byte ' + ','.join(map(str, angles)) + '\n'
    linked = H.assemble(source, {'THROW': (ORIGIN, CAPACITY), 'THROW_DATA': (DATA, DATA_CAPACITY)})
    # Live clock/input aliases can use zero-page opcodes rather than the
    # detached fixture's absolute RAM addresses.
    assert 0 < len(linked['images']['THROW']) <= CAPACITY and linked['images']['THROW_DATA'] == angles
    return linked, fields


def roll(before, after):
    bundle = W.Symbols.bundle()
    models = [C.Common.blank(dict(bundle, raw=image)) for image in (before, after)]
    setter = W.address(bundle, 'X5SetPhysicalChr')
    slot7 = before[W.location(bundle, 'RlPoolChrHi'):W.location(bundle, 'RlPoolChrHi')+6]
    for pool, flags in product(range(6), (0x30, 0x31, 0x70, 0x71)):
        outputs, registers = [], []
        for m in models:
            N.put(m, RlPool=pool)
            rows = []

            def observe(m, c):
                if c.pc == setter and m.rawtags[1] == 0xbe:
                    rows.append((c.y, c.a+256*c.x))

            c = C.Vector.call(m, 'RlPublish', p=flags, observe=observe)
            outputs.append(rows)
            registers.append((c.a, c.x, c.y, c.p, c.sp))
        base = (364, 368, 372, 376, 304, 304)[pool]
        assert outputs[0] == [(0, base), (6, base+2), (7, slot7[pool]+256)]
        assert outputs[1] == [(slot, MIRROR if page == PAGE else page) for slot, page in outputs[0]]
        assert registers[0] == registers[1]
        assert all(T.page(before, old) == T.page(after, new) for (_, old), (_, new) in zip(*outputs, strict=True))
    return 24


def cold_controls(before, old_info, candidate, info, pose_worker, linked, fields, *, live_bindings=False):
    stop = T.Weapon.Stock.STOP
    cuts = set()

    def seed(image):
        m = C.Common.blank(dict(W.Symbols.bundle(), raw=image))
        C.Common.scene(m, 16)
        m[0x730b] = 0x40
        return m

    def run(m, selected, *, fault=None, nmi=False):
        c = C.ColdVector.entry(m)
        at = selected['cold']['symbols']['JaySceneOrRetire']
        m[0x16c], m[0x16d] = at & 255, at >> 8
        rows = []

        def observe(m, c):
            if m.rawtags[1:3] != [3, 2] or not Late.BOOT <= c.pc < DATA:
                return
            assert c.p & 4 and m.ppuctrl & 4 == 0
            assert all(header != selected['cookie'] for header in C.Common.headers(m))
            if 'throw_loader' in selected:
                labels = selected['throw_loader']['symbols']
                if c.pc == labels['SteveLateRow']:
                    rows.append((c.a, c.x))
                if fault and c.pc == labels['SteveLateVerify'] and m[4] == fault >> 8:
                    m.corrupt_at = (2, fault-0xc000)
            if nmi and c.pc not in cuts:
                cuts.add(c.pc)
                _, branch = C.Vector.clone(m, c)
                C.ColdVector.interrupt(branch, 'FF')

        C.Vector.finish(m, c, stop, observe)
        assert (c.a, c.x, c.y, c.p & 0xef) == (83, 71, 109, 0x21)
        return rows

    old, new = seed(before), seed(candidate)
    run(old, old_info)
    rows = run(new, info, nmi=True)
    expected = ([(0x33, 0xce)] if pose_worker is not None else []) + [(0x32, 0xd8), (0x50, 0xd0), (0x52, 0xd4)]
    assert rows == expected and new.ppu_reads-old.ppu_reads == 2050
    assert C.Common.headers(new) == (info['cookie'],)*2
    assert old.ram[2][0x1800:0x1c00] == T.page(before, PUNCH_PAGE)
    assert new.ram[2][0x1800:0x1c00] == info['throw_stage']
    assert old.ram[2][0x1a80:0x1c00] == new.ram[2][0x1a80:0x1c00]
    assert new.ram[2][0xd00:0xe00] == info['throw_boot']
    assert all(old.ram[2][a:b] == new.ram[2][a:b] for a, b in
               ((0, 0xd00), (0xe00, 0x1800), (0x1a80, 0x1fe0), (0x1ff0, 0x2000)))
    assert old.ram[3][:0x1fe0] == new.ram[3][:0x1fe0] and old.ram[3][0x1ff0:] == new.ram[3][0x1ff0:]
    assert old.chr_latches == new.chr_latches and old.vram == new.vram and old.rawtags == new.rawtags
    state = STATE-0xc000
    assert new.ram[2][state:state+STATE_CAPACITY] == bytes(STATE_CAPACITY)
    new.ram[2][state] = 0x51
    reads = new.ppu_reads
    assert not run(new, info) and new.ppu_reads == reads and new.ram[2][state] == 0x51

    faults = (0xd800, 0xda7f, 0xda80, 0xdbff)
    for fault in faults:
        m = seed(candidate)
        assert run(m, info, fault=fault) == expected[:expected.index((0x32, 0xd8))+1]
        assert m.corrupt_at == (2, fault-0xc000)
        assert not any(header[0] for header in C.Common.headers(m))
    m = seed(candidate)
    m.corrupt_at = (2, DATA-0xc000)
    assert not run(m, info) and not any(header[0] for header in C.Common.headers(m))

    new.raw_page(2, 2)
    N.put(new, CurrentBankC=2)
    for name, value in (('PlayerX', 0x2100), ('PlayerY', 0x1500), ('X', 0x2200), ('Y', 0x1600)):
        at = fields['SteveBot'+name]
        new[at], new[at+1] = value & 255, value >> 8
    cpu = N.NesMPU(memory=new)
    Late.Transport.Transport.Upgrade.call(cpu, linked['symbols']['SteveThrowDirection'])
    assert cpu.a == 8
    direction = cpu.a
    live_launch = None
    if live_bindings:
        new[fields['SteveBotActor']] = 1
        new[fields['SteveBotFacing']] = 0
        new[fields['SteveThrowSelector']] = 0
        new[fields['SteveThrowCameraX']] = 0
        new[fields['SteveThrowCameraX']+1] = 0x21
        Late.Transport.Transport.Upgrade.call(cpu, linked['symbols']['SteveThrowBegin'], a=5)
        assert tuple(new[fields[name]] for name in ('SteveThrowTimer', 'SteveThrowSpeed',
                     'SteveThrowSelector', 'SteveThrowSound')) == (3, 0x60, 0x80, 0x0c)
        Late.Transport.Transport.Upgrade.call(cpu, linked['symbols']['SteveThrowUpdate'])
        assert (new[fields['SteveBotX']], new[fields['SteveBotX']+1]) == (0x60, 0x22)
        assert new[fields['SteveBotPose']+1] != 0, 'Live lift animation decoder must publish the throw pose'
        live_launch = dict(x_q4=0x2260, timer=new[fields['SteveThrowTimer']],
                           pose=new[fields['SteveBotPose']]+256*new[fields['SteveBotPose']+1])
    return dict(loader_bytes=info['throw_loader']['used']['STEVE_LATE_COLD'], extra_cold_reads=2050,
                NMI_cuts=len(cuts), faults=[hex(a) for a in (*faults, DATA)], state_bytes=STATE_CAPACITY,
                exact_punch_tail=384, executed_direction=direction, live_launch=live_launch)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--openings', action='store_true')
    parser.add_argument('--live-pose', action='store_true', help='Qualify on the delivered original lift poses')
    args = parser.parse_args()
    raw, donor = Live.DONOR.HOST.read_bytes(), Live.DONOR.DONOR.read_bytes()
    if args.live_pose:
        import check_steve_shatterhand_pose_live_1111 as LivePose
        import deliver_steve_lift_art_1111 as Delivered

        assert C.digest(raw) == Delivered.PIN
        parent, old_info = LivePose.proposal(raw)
        assert parent == raw
        pose_worker = old_info['pose_worker']
    else:
        if C.digest(raw) != BASE:
            from deliver_steve_lift_art_1111 import recover_parent

            raw = recover_parent(raw)
        assert C.digest(raw) == BASE
        pose_worker = b'\xa9\x39\x60' + bytes((i*29+13) & 255 for i in range(Pose.SIZE-3))
        parent, old_info = Pose.proposal(raw, pose_worker)
    linked, fields = detached(donor)
    with patch.object(Throw, 'ORIGIN', ORIGIN):
        pair = Throw.Pair(donor, linked, fields)
    pair.host.memory[DATA:DATA+64] = linked['images']['THROW_DATA']
    assert Throw.directions(pair) == 529 and Throw.begins(pair) == 12 and Throw.contacts(pair) == 8
    if args.live_pose:
        linked, fields = live_link(donor, old_info)
    candidate, info = mount(parent, old_info, linked['images']['THROW'], linked['images']['THROW_DATA'], pose=True)
    report = dict(base=C.digest(raw), live_pose=args.live_pose, pose_parent=C.digest(parent), fixture=C.digest(candidate),
                  cookie=info['cookie'].hex(), code_bytes=len(linked['images']['THROW']), angle_bytes=64,
                  preimage_D800=C.digest(T.page(raw, PUNCH_PAGE)[:CAPACITY]),
                  preimage_DA80=C.digest(T.page(raw, PUNCH_PAGE)[CAPACITY:]),
                  publisher_cases=roll(parent, candidate), output_files=0)
    report['cold'] = cold_controls(parent, old_info, candidate, info, pose_worker, linked, fields,
                                   live_bindings=args.live_pose)
    if args.openings:
        report['openings'] = Pose.openings(parent, candidate)
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    main()
