"""Connect original Steve lift body poses through the native sprite selector."""

import json
import argparse
from collections import Counter
from unittest.mock import patch

import check_steve_shatterhand_pose_carrier_1111 as Carrier
import check_steve_shatterhand_lift_live_1111 as Lift

A, Live, Laser = Carrier.Art.A, Carrier.Live, Carrier.Laser
SOURCE = Live.H.ROOT / 'tools/reference/steve_shatterhand_pose_live_1111.s'


def link(raw, info):
    donor = A.D.DONOR.read_bytes()
    art = A.plan(raw, donor)
    data, offsets = bytearray(), []
    for pose in A.SOURCE_POSES:
        offsets.append(len(data))
        data.extend(art['poses'][pose][0])
    assert len(data) == 186
    labels = dict(PoseIds=0xce00+len(data), PoseOffsets=0xce00+len(data)+10)
    data.extend(p & 255 for p in A.SOURCE_POSES)
    data.extend(offsets)
    assert len(data) == 206
    bundle = Live.W.Symbols.bundle()
    fields = {name: Live.W.address(bundle, name) for name in
              ('OperMode', 'Player_State', 'PlayerFacingDir', 'GameEngineSubroutine', 'SmPosePtr',
               'ObjectMetasprite', 'SmChrBank', 'PlayerChrBank')}
    fields.update(info['lift_fields'] | labels, FmGroups=0x730b, PoseBuffer=0xc8c0,
                  PoseMirror=0xc942, PoseAnchorX=0xc943, PoseAnchorY=0xc944)
    fields.update({name: info['companion_fields'][name] for name in ('SteveBotFacing', 'SteveBotX')})
    fields['SteveLaserActive'] = info['laser_fields']['SteveLaserActive']
    assert info['companion_fields']['SteveBotY'] == fields['SteveBotX']+2
    fields.update({name: info['companion_symbols'][name] for name in
                   ('SetCompanionMeta', 'ProjectToScreen', 'DrawCompanionMeta', 'DrawShot', 'LaserDrawShots')})
    assembled = Live.H.assemble(Live.bindings(fields) + SOURCE.read_text(),
                                {'POSE_GATE': (0xc040, 14), 'POSE_BANK': (0xc38c, 41),
                                 'POSE_WORKER': (0xcecf, 305)})
    assert assembled['symbols']['StevePoseSelect'] == 0xcecf
    gate = assembled['images']['POSE_GATE']
    bank = assembled['images']['POSE_BANK'].ljust(41, b'\xea')
    worker = bytes(data).ljust(207, b'\xea') + assembled['images']['POSE_WORKER']
    at = Live.C.offset
    old_bank = bytes.fromhex('ad0b732960f01dc960f01948e003900aa51ef004a204d002a200684a4a4a1869d4a00060a9c4a00260')
    assert len(old_bank) == 41
    assert raw[at(96, 0xa918):at(96, 0xa918)+2] == b'\x68\x60'
    assert raw[at(97, 0xc040):at(97, 0xc040)+14] == b'\xc1'*14
    assert raw[at(97, 0xc38c):at(97, 0xc38c)+41] == old_bank
    assert raw[at(96, 0xa29a):at(96, 0xa29a)+3] == b'\xbd\x40\xc0'
    edits = ((at(97, 0xc040), b'\xc1'*14, gate),
             (at(97, 0xc38c), old_bank, bank),
             (at(96, 0xa29a), b'\xbd\x40\xc0', b'\xa9\xc1\xea'))
    import check_steve_shatterhand_pose_guard_1111 as Guard
    import check_steve_shatterhand_pose_owner_1111 as Owner
    guard_edits, _ = Guard.link(raw)
    edits = (*edits[1:], *guard_edits, *Owner.plan(raw))
    return worker, edits, assembled


def proposal(raw):
    if Live.C.digest(raw) == '80e6aa3e32574f38b23fa6da6ab3c94bbe7b5ae11b29339b32b11a624fe6f1ed':
        from deliver_steve_lift_art_1111 import recover_parent

        raw = recover_parent(raw)
    original, info = Laser.proposal(raw, lift=True)
    assert original == raw
    worker, edits, linked = link(raw, info)
    draw = linked['symbols']['SteveLiftDraw']
    _, moved_info = Laser.proposal(raw, lift=True, pose_draw=draw)
    worker, edits, linked = link(raw, moved_info)
    assert linked['symbols']['SteveLiftDraw'] == draw
    candidate, result = Carrier.proposal(raw, worker, host_edits=edits,
                                         cookie_prefix=bytes.fromhex('a810200a'), pose_draw=draw)
    return candidate, result | dict(pose_link=linked, pose_worker=worker)


def graphics(candidate, info):
    native_frame = Live.C.Game.frame
    bundle = Live.W.Symbols.bundle()
    renderer = Live.W.address(bundle, 'MetaspriteRenderLoop')
    pose_ptr = Live.W.address(bundle, 'SmPosePtr')
    chr_fields = tuple(Live.W.address(bundle, name) for name in ('SmChrBank', 'PlayerChrBank'))
    lift_state = info['lift_fields']['SteveLiftState']
    draw_shot = info['companion_symbols']['DrawShot']
    stock_table = Live.C.offset(97, 0xc032)
    stock_lows = set(candidate[stock_table:stock_table+14])
    counts = Counter()
    lift_memory = None
    ordinary_body = None
    lift_shot_dispatches = 0

    def frame(m, observe=None):
        expected = set()
        lift_bot_drawn = False

        def visit(memory, cpu):
            nonlocal lift_memory, ordinary_body, lift_bot_drawn, lift_shot_dispatches
            if observe:
                observe(memory, cpu)
            if cpu.pc == draw_shot and memory.rawtags[2] == 2 and lift_bot_drawn:
                lift_shot_dispatches += 1
            if cpu.pc != renderer:
                return
            pointer = memory[3]+256*memory[4]
            is_ordinary = False
            if pointer in (0xc8c0, 0xc8e0):
                assert memory.rawtags[2] == 2, ('body PRG owner', memory.rawtags)
                offset = pointer-0xc000
                record = bytes(memory.ram[2][offset:offset+29])
                field = 'SteveLiftPlayerPose' if pointer == 0xc8c0 else 'SteveLiftBotPose'
                pose = Live.resident(memory, info['lift_fields'][field]) + (0x100 if pointer == 0xc8e0 else 0)
                counts[pose] += 1
                if pointer == 0xc8e0:
                    lift_bot_drawn = True
                elif lift_memory is None and Live.resident(memory, lift_state) == 7:
                    lift_memory = memory
            elif (memory is lift_memory and ordinary_body is None and
                  pointer == memory[pose_ptr]+256*memory[pose_ptr+1] and
                  Live.resident(memory, lift_state) == 0):
                assert pointer >> 8 == 0xc1 and pointer & 0xff in stock_lows, ('stock body pointer', hex(pointer))
                assert memory.rawtags[2] == 0xe1, ('stock body PRG owner', memory.rawtags)
                assert tuple(memory[at] for at in chr_fields) == (220, 220), 'stock body CHR selection'
                offset = Live.C.offset(97, pointer)
                record = bytes(memory[pointer:pointer+17])
                assert record == candidate[offset:offset+17] and record[0] == 16
                is_ordinary = True
            else:
                return
            x = memory[7] + 256*memory[8]
            y = memory[9] + 256*memory[10]
            cells = set()
            for at in range(1, record[0]+1, 4):
                tile, attr, dy, dx = record[at:at+4]
                sx = x + (dx-256 if dx & 128 else dx)
                sy = y + (dy-256 if dy & 128 else dy)
                if 0 <= sx < 256 and 256 <= sy < 496:
                    cells.add((sy & 255, tile, (attr | memory[6]) & 0xf3, sx))
            expected.update(cells)
            if is_ordinary:
                assert cells, 'released Steve body did not enter visible OAM'
                ordinary_body = dict(pointer=f'{pointer:04x}', prg=memory.rawtags[2], oam_cells=len(cells))

        native_frame(m, visit)
        if expected:
            actual = {tuple(m[0x200+i:0x204+i]) for i in range(0, 256, 4)}
            assert expected <= actual, ('missing selected Steve body', expected-actual)
        if m is lift_memory and ordinary_body is not None and m.chr_latches[0] == 220:
            ordinary_body['published_chr'] = 220

    with patch.object(Live.C.Game, 'frame', frame):
        proof = Lift.exercise(candidate, info)
    assert {0x6c, 0xac, 0xb0, 0xb6, 0xb8, 0x15e, 0x160, 0x162, 0x164} <= counts.keys(), counts
    assert ordinary_body is not None and ordinary_body.get('published_chr') == 220, ordinary_body
    assert lift_shot_dispatches > 0, 'first companion projectile renderer was bypassed during lift'
    return dict(movement=proof, body_draws={f'{pose:02x}': count for pose, count in counts.items()},
                ordinary_body_after_release=ordinary_body, lift_shot_dispatches=lift_shot_dispatches)


def projectile_lift(candidate, info):
    """Fire an earned Alpha shot and observe its OAM DMA during lift."""
    from check_jay_silius_stock_draw_dispatch_1111 import DmaBus

    m, earned = Live.natural(candidate, info)
    m.__class__ = DmaBus
    fields = info['companion_fields']
    lift_state = info['lift_fields']['SteveLiftState']
    renderer = Live.W.address(m.bundle, 'MetaspriteRenderLoop')
    start_x, _ = Live.Ingress.Live.player(m)

    def bot(name):
        return Live.resident(m, fields['SteveBot'+name])

    def frame(pad, observe=None):
        m.controller_pad = pad
        m.dma = None
        Live.C.Game.frame(m, observe)
        assert Live.Ingress.Live.mode(m) == Live.Ingress.S.PLAY and Live.N.get(m, 'NumberofLives') == 2
        assert Live.Ingress.Live.player(m)[0] == start_x and bot('Actor') == 1

    for update in range(12):
        frame(4)
        if update >= 2 and bot('Anim') == 0:
            break
    else:
        raise AssertionError('Alpha never re-armed after the first shot')
    assert Live.resident(m, Live.Move.Motion.FIELDS['State']) == 3
    frame(68)  # Down+B fires from crouch.
    assert (bot('ShotType'), bot('ShotTimer'), Live.resident(m, lift_state)) == (0x95, 51, 0)

    state_at_draw = None

    def see_lift_body(memory, cpu):
        nonlocal state_at_draw
        if cpu.pc == renderer and memory.rawtags[2] == 2 and (memory[3], memory[4]) == (0xe0, 0xc8):
            state_at_draw = Live.resident(memory, lift_state)

    pending = None
    dma_tiles = set()
    evidence = []
    for update in range(12):
        state_at_draw = None
        frame(132, see_lift_body)  # Release B and hold Down+A.
        state = Live.resident(m, lift_state)
        assert (state == 4 if update == 0 else 4 <= state <= 7), (update, state)
        assert (bot('ShotType'), bot('ShotTimer')) == (0x95, 50-update), update
        if pending is not None:
            assert m.dma is not None and m.chr_latches[5] == Live.CHR_PAGE
            dma = {tuple(m.dma[at:at+4]) for at in range(0, 256, 4)}
            tile, cells = pending
            assert cells <= dma, ('missing Alpha projectile DMA during lift', cells-dma)
            dma_tiles.add(tile)
        if dma_tiles == {0x77, 0x79}:
            break

        pending = None
        if state_at_draw is None:
            continue
        assert state_at_draw == state
        x, y = Live.native_position(m, fields, 'SteveBotShotX', 'SteveBotShotY')
        if 8 <= x < 248 and 8 <= y < 240:
            tile, palette = (0x77, 1) if bot('DrawPhase') & 1 else (0x79, 2)
            cells = {(y-8, tile, palette, x-8), (y-8, tile, palette | 64, x)}
            actual = Live.sprites(m, (0x77, 0x79))
            assert cells <= actual, ('missing Alpha projectile OAM during lift', cells-actual)
            pending = tile, cells
            evidence.append(dict(update=update+1, state=state, timer=bot('ShotTimer'), cells=sorted(cells)))
    assert dma_tiles == {0x77, 0x79}, evidence
    return dict(earned_pattern=earned['route']['pattern'], projectile_dma_tiles=sorted(dma_tiles), frames=evidence)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--graphics', action='store_true')
    parser.add_argument('--opening-only', action='store_true')
    parser.add_argument('--projectile-lift', action='store_true')
    args = parser.parse_args()
    raw = A.D.HOST.read_bytes()
    candidate, info = proposal(raw)
    print(json.dumps(dict(candidate=Live.C.digest(candidate), worker_bytes=len(info['pose_worker']),
                          outputs=0)), flush=True)
    if args.projectile_lift:
        print(json.dumps(projectile_lift(candidate, info), indent=2), flush=True)
    elif args.graphics:
        print(json.dumps(graphics(candidate, info), indent=2), flush=True)
    else:
        if raw == candidate:
            from deliver_steve_lift_art_1111 import recover_parent

            raw = recover_parent(raw)
        print(json.dumps(Carrier.openings(raw, candidate), indent=2), flush=True)
        if args.opening_only:
            return
        print(json.dumps(Lift.exercise(candidate, info), indent=2), flush=True)


if __name__ == '__main__':
    main()
