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
    assert info['companion_fields']['SteveBotY'] == fields['SteveBotX']+2
    fields.update({name: info['companion_symbols'][name] for name in
                   ('SetCompanionMeta', 'ProjectToScreen', 'DrawCompanionMeta')})
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
    counts = Counter()

    def frame(m, observe=None):
        expected = set()

        def visit(memory, cpu):
            if observe:
                observe(memory, cpu)
            pointer = memory[3]+256*memory[4]
            if cpu.pc != renderer or pointer not in (0xc8c0, 0xc8e0):
                return
            assert memory.rawtags[2] == 2, ('body PRG owner', memory.rawtags)
            offset = pointer-0xc000
            record = bytes(memory.ram[2][offset:offset+29])
            field = 'SteveLiftPlayerPose' if pointer == 0xc8c0 else 'SteveLiftBotPose'
            pose = Live.resident(memory, info['lift_fields'][field]) + (0x100 if pointer == 0xc8e0 else 0)
            counts[pose] += 1
            x = memory[7] + 256*memory[8]
            y = memory[9] + 256*memory[10]
            for at in range(1, record[0]+1, 4):
                tile, attr, dy, dx = record[at:at+4]
                sx = x + (dx-256 if dx & 128 else dx)
                sy = y + (dy-256 if dy & 128 else dy)
                if 0 <= sx < 256 and 256 <= sy < 496:
                    expected.add((sy & 255, tile, (attr | memory[6]) & 0xf3, sx))

        native_frame(m, visit)
        if expected:
            actual = {tuple(m[0x200+i:0x204+i]) for i in range(0, 256, 4)}
            assert expected <= actual, ('missing original lift body', expected-actual)

    with patch.object(Live.C.Game, 'frame', frame):
        proof = Lift.exercise(candidate, info)
    assert {0x6c, 0xac, 0xb0, 0xb6, 0xb8, 0x15e, 0x160, 0x162, 0x164} <= counts.keys(), counts
    return dict(movement=proof, body_draws={f'{pose:02x}': count for pose, count in counts.items()})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--graphics', action='store_true')
    args = parser.parse_args()
    raw = A.D.HOST.read_bytes()
    candidate, info = proposal(raw)
    print(json.dumps(dict(candidate=Live.C.digest(candidate), worker_bytes=len(info['pose_worker']),
                          outputs=0)), flush=True)
    if args.graphics:
        print(json.dumps(graphics(candidate, info), indent=2), flush=True)
    else:
        print(json.dumps(Carrier.openings(raw, candidate), indent=2), flush=True)
        print(json.dumps(Lift.exercise(candidate, info), indent=2), flush=True)


if __name__ == '__main__':
    main()
