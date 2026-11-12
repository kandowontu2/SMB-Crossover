"""Link and compare the detached native Steve throw pose extension."""

import json
from itertools import product

from py65.devices.mpu6502 import MPU

import check_steve_shatterhand_pose_live_1111 as Pose
import check_steve_shatterhand_throw_art_1111 as Art

Live, H, C = Pose.Live, Pose.Live.H, Pose.Live.C
SOURCE = H.ROOT / 'tools/reference/steve_shatterhand_throw_pose_1111.s'
FIELDS = dict(SteveThrowPlayerAction=0xc977, SteveThrowFrame=0xc978,
              ThrowRecoveryAE=0xcdc8, ThrowRecoveryB2=0xcddd)
LAYOUT = {'POSE_GATE': (0xc040, 14), 'POSE_BANK': (0xc38c, 41),
          'POSE_WORKER': (0xcecf, 305), 'THROW_POSE_LOOKUP': (0xc8a5, 27),
          'THROW_POSE_CHR': (0xda71, 15)}
STOP = 0x5000


def link(info, *, chr_origin=0xda71):
    old_link, old_worker = info['pose_link'], info['pose_worker']
    assert len(old_worker) == 499
    source = old_link['source']
    swaps = (
        ('''    lda SteveLiftState
    cmp #4
    bcc StockPose
    cmp #8
    bcs StockPose
    lda GameEngineSubroutine
    cmp #8
    bne StockPose
    lda SteveLiftPlayerPose
    jsr FindPose''',
         '''    lda GameEngineSubroutine
    cmp #8
    bne StockPose
    lda SteveThrowPlayerAction
    bne PlayerPoseReady
    lda SteveLiftState
    cmp #4
    bcc StockPose
    cmp #8
    bcs StockPose
PlayerPoseReady:
    lda SteveLiftPlayerPose
    jsr SteveThrowFindPlayerPose'''),
        ('''    lda #$53
    sta SmChrBank
    sta PlayerChrBank
    pla
    pla
    pla
    ldx #1
    ldy #0
    lda #$53
    sta $016a''',
         '''    jsr SteveThrowPoseChr
    sta SmChrBank
    sta PlayerChrBank
    sta $016a
    pla
    pla
    pla
    ldx #1'''),
        ('SteveLiftDraw:\n    lda SteveLiftState',
         'SteveLiftDraw:\n    bit SteveThrowFrame\n    bmi LiftBotPose\n    lda SteveLiftState'),
        ('    lda SteveLiftBotPose\n    jsr FindPose',
         'LiftBotPose:\n    lda SteveLiftBotPose\n    jsr FindPose'),
        ('    lda SteveLaserActive\n    beq LiftFirstShot',
         'LiftDrawProjectiles:\n    lda SteveLaserActive\n    beq LiftFirstShot'),
        ('NoLiftDraw:\n    clc', 'NoLiftDraw:\n    bit SteveThrowFrame\n    bmi LiftDrawProjectiles\n    clc'),
        ('    lda #<(PoseBuffer+32)', 'SteveDeathBuildPose:\n    lda #<(PoseBuffer+32)'),
    )
    for old, new in swaps:
        assert source.count(old) == 1, old
        source = source.replace(old, new)
    layout = LAYOUT | {'THROW_POSE_CHR': (chr_origin, 0xda80-chr_origin)}
    linked = H.assemble(Live.bindings(FIELDS) + source + '\n' + SOURCE.read_text(), layout)
    assert linked['symbols']['StevePoseSelect'] == old_link['symbols']['StevePoseSelect'] == 0xcecf
    for segment in ('POSE_GATE', 'POSE_BANK'):
        assert linked['images'][segment] == old_link['images'][segment]
    worker = old_worker[:207] + linked['images']['POSE_WORKER']
    assert len(worker) == 511
    assert len(linked['images']['THROW_POSE_LOOKUP']) == 22
    assert len(linked['images']['THROW_POSE_CHR']) == 11
    return worker, linked


def records(art):
    ae, b2 = (art['poses'][pose][0] for pose in Art.EXTRA_POSES)
    assert (len(ae), len(b2)) == (21, 25)
    assert all(0x20 <= tile <= 0x2e and tile % 2 == 0 for row in (ae, b2) for tile in row[1::4])
    return ae+b2


def rom_edits(raw, info, worker, linked):
    """Return the three bounded edits to existing CHR carriers."""
    old_draw = info['pose_link']['symbols']['SteveLiftDraw']
    new_draw = linked['symbols']['SteveLiftDraw']
    draw = info['companion_symbols']['SteveCompanionDraw']
    old_call, new_call = (b'\x20'+at.to_bytes(2, 'little') for at in (old_draw, new_draw))
    host = Live.Transport
    host_at = C.CHR+1024*host.EXT_PAGE+draw-host.EXT_ORIGIN
    native_entry = raw[host_at:host_at+12]
    assert native_entry.count(old_call) == 1, native_entry.hex()
    lookup_at = C.CHR+1024*host.PAGE+0xc8a5-host.ORIGIN
    lookup = linked['images']['THROW_POSE_LOOKUP']
    before = info['pose_worker'].ljust(512, b'\xea')
    edits = ((C.CHR+1024*Art.EXTRA_PAGE, before, worker.ljust(512, b'\xea')),
             (lookup_at, b'\xea'*len(lookup), lookup),
             (host_at+native_entry.index(old_call), old_call, new_call))
    assert all(raw[at:at+len(old)] == old and len(old) == len(new) for at, old, new in edits)
    return edits


def packet(record, x, y):
    parts = []
    for at in range(1, len(record), 4):
        tile, attr, dy, dx = record[at:at+4]
        parts.append((dy+y, dx+x, tile, attr))
    return Art.A.packet(parts)


def concurrent_chr(raw, donor, art):
    """Compare every thrown body cell with either player CHR selection active."""
    compared = 0
    tiles = set()
    for player_page, facing in product((307, 220), (0, 1)):
        latches = {0: player_page, 5: Art.A.EXISTING_PAGE}
        source_page, parts = Art.A.Geometry.parts(donor, 0x15e+facing)
        record = art['poses'][0x15e][facing]
        for (_, _, source_tile, _), at in zip(parts, range(1, len(record), 4), strict=True):
            tile = record[at]
            slot = (tile & 1)*4 + (tile >> 6)
            assert slot == 5, (hex(tile), slot, player_page)
            offset = (tile & 0x3e)*16
            installed = Art.A.T.page(raw, latches[slot])[offset:offset+32]
            assert installed == Art.A.original_cell(donor, source_page, source_tile)
            compared += 1
            tiles.add(tile)
    return dict(player_pages=[307, 220], robot_slot=5, robot_page=Art.A.EXISTING_PAGE,
                robot_tiles=sorted(tiles), donor_cells=compared)


def fixture(info, worker, linked, recovery=b''):
    cpu = MPU()
    m = cpu.memory
    m[0xce00:0xce00+len(worker)] = worker
    for name in ('THROW_POSE_LOOKUP', 'THROW_POSE_CHR'):
        code = linked['images'].get(name, b'')
        at = LAYOUT[name][0]
        m[at:at+len(code)] = code
    at = FIELDS['ThrowRecoveryAE']
    m[at:at+len(recovery)] = recovery
    # Capture the real far-call ABI and the branch to the original native tail.
    m[0x015a] = 0x60
    m[0x80c2] = 0x60
    m[0xa918:0xa91a] = b'\x68\x60'
    for name in ('SetCompanionMeta', 'ProjectToScreen', 'DrawCompanionMeta', 'DrawShot', 'LaserDrawShots'):
        m[info['companion_symbols'][name]] = 0x60
    return cpu


def run(cpu, entry, *, player=False, observe=None):
    cpu.pc, cpu.sp, cpu.x, cpu.p = entry, 0xf0, 3, 0x20
    cpu.stPushWord(STOP-1)
    if player:
        # Active publisher discards the BodyBank caller's return address.
        cpu.stPushWord(STOP-1)
    for _ in range(700):
        if cpu.pc == STOP:
            return
        if observe:
            observe(cpu)
        assert cpu.memory[cpu.pc], hex(cpu.pc)
        cpu.step()
    raise AssertionError((hex(entry), hex(cpu.pc)))


def compare(info, art, worker, linked, recovery):
    old, old_link = info['pose_worker'], info['pose_link']
    bundle = Live.W.Symbols.bundle()
    native = {name: Live.W.address(bundle, name) for name in
              ('PlayerFacingDir', 'GameEngineSubroutine', 'SmPosePtr', 'SmChrBank',
               'PlayerChrBank', 'ObjectMetasprite')}
    fields = native | info['lift_fields'] | FIELDS
    counts = dict(throw_player=0, stock_player=0, throw_robot=0, stock_robot=0)

    def player(rom, labels, action, pose, state, facing, engine):
        cpu = fixture(info, rom, labels, recovery)
        m = cpu.memory
        for name, value in dict(SteveThrowPlayerAction=action, SteveLiftPlayerPose=pose,
                                SteveLiftState=state, PlayerFacingDir=facing,
                                GameEngineSubroutine=engine).items():
            m[fields[name]] = value
        run(cpu, labels['symbols']['StevePoseSelect'], player=True)
        ptr = m[fields['SmPosePtr']]+256*m[fields['SmPosePtr']+1]
        chr_state = tuple(m[fields[name]] for name in ('SmChrBank', 'PlayerChrBank', 'ObjectMetasprite'))
        return (chr_state, tuple(m[at] for at in (0x16a, 0x16c, 0x16d)),
                (cpu.a, cpu.x, cpu.y, cpu.sp), ptr, bytes(m[ptr:ptr+m[ptr]+1]))

    for (action, pose, state), facing in product(((7, 0xb4, 1), (7, 0xb2, 1), (8, 0xac, 3),
                                                  (8, 0xae, 3), (0x80, 0xb2, 2), (0x80, 0xae, 3)),
                                                 (1, 2)):
        low = 0x33 if pose in Art.EXTRA_POSES else 0x53
        expected = packet(art['poses'][pose][facing-1], 8, 16)
        assert player(worker, linked, action, pose, state, facing, 8) == (
            (low, low, 0xe9), (low, 0x75, 0xa2), (0xbe, 1, 0, 0xf0), 0xc8c0, expected)
        counts['throw_player'] += 1

    for state, facing, engine, pose in product((0, 3, 4, 7, 8), (1, 2), (0, 8), (0, 0xac)):
        previous = player(old, old_link, 0, pose, state, facing, engine)
        assert player(worker, linked, 0, pose, state, facing, engine) == previous
        if engine == 0:
            assert player(worker, linked, 0x80, 0xae, state, facing, engine) == previous
        counts['stock_player'] += 1

    symbols = info['companion_symbols']
    body, first, laser = (symbols[name] for name in ('DrawCompanionMeta', 'DrawShot', 'LaserDrawShots'))

    def robot(rom, labels, marker, selector, pose, state, facing, laser_active):
        cpu = fixture(info, rom, labels, recovery)
        m = cpu.memory
        m[FIELDS['SteveThrowFrame']] = marker
        m[0xc969] = selector
        m[fields['SteveLiftBotPose']:fields['SteveLiftBotPose']+2] = (pose, bool(pose))
        m[fields['SteveLiftState']] = state
        m[info['companion_fields']['SteveBotFacing']] = facing*0x80
        m[info['laser_fields']['SteveLaserActive']] = laser_active
        seen = []

        def observe(cpu):
            if cpu.pc in (body, first, laser):
                seen.append(cpu.pc)

        run(cpu, labels['symbols']['SteveLiftDraw'], observe=observe)
        return bool(cpu.p & cpu.CARRY), seen, bytes(m[0xc8e0:0xc8e1+m[0xc8e0]])

    for active, facing in product((0, 1), repeat=2):
        shot = laser if active else first
        assert robot(worker, linked, 0x80, 0x80, 0x5e, 0, facing, active) == (
            True, [body, shot], art['poses'][0x15e][facing])
        for selector in (0x80, 0):
            assert robot(worker, linked, 0x80, selector, 0, 0, facing, active) == (True, [shot], b'\x00')
        counts['throw_robot'] += 3
        for pose, state in product((0, 0x5e), (0, 4, 7, 8)):
            assert robot(worker, linked, 0, 0, pose, state, facing, active) == (
                robot(old, old_link, 0, 0, pose, state, facing, active))
            counts['stock_robot'] += 1
    return counts


def main():
    from deliver_steve_lift_art_1111 import recover_parent

    raw = Live.DONOR.HOST.read_bytes()
    original, info = Pose.proposal(raw)
    assert original == raw
    donor = Live.DONOR.DONOR.read_bytes()
    worker, linked = link(info)
    art = Art.plan(recover_parent(raw), donor, pose_worker=worker)
    recovery = records(art)
    edits = rom_edits(raw, info, worker, linked)
    print(json.dumps(dict(
        parent=C.digest(raw), counts=compare(info, art, worker, linked, recovery),
        concurrent_chr=concurrent_chr(raw, donor, art),
        worker_bytes=len(worker), worker_sha256=C.digest(worker),
        body_draw=[hex(row['symbols']['SteveLiftDraw']) for row in (info['pose_link'], linked)],
        helper_bytes={name: len(linked['images'][name]) for name in ('THROW_POSE_LOOKUP', 'THROW_POSE_CHR')},
        recovery_hex=recovery.hex(),
        edits=[dict(offset=hex(at), length=len(old), preimage=old.hex() if len(old) < 512 else C.digest(old),
                    replacement=new.hex() if len(new) < 512 else C.digest(new)) for at, old, new in edits],
        chr_helper=linked['images']['THROW_POSE_CHR'].hex(), output_files=0,
    ), indent=2), flush=True)


if __name__ == '__main__':
    main()
