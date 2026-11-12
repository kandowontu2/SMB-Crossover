"""Check Steve's proposed raw3 flight and contact region on the delivered ROM."""

import argparse
from collections import Counter
import json
from unittest.mock import patch

from py65.devices.mpu6502 import MPU

import check_steve_shatterhand_pose_live_1111 as Pose
import check_steve_shatterhand_throw_carrier_1111 as Carrier

C, Live, T = Carrier.C, Carrier.Live, Carrier.T
ORIGIN, END, SOURCE_PAGE = 0xab00, 0xaf00, 304
DUPLICATE, COPY_END = 0xbb00, 0xbfe0


def preimage(raw):
    return T.page(raw, 232)[0x300:] + T.page(raw, 234)[:0x300]


def cold_duplicate(raw):
    memory, _ = Carrier.Late.Transport.Steve.Live.opening(raw, 2)
    ram3 = bytes(memory.ram[3])
    original = preimage(raw)
    assert len(original) == END-ORIGIN
    assert ram3[ORIGIN-0xa000:END-0xa000] == original
    assert ram3[DUPLICATE-0xa000:DUPLICATE-0xa000+len(original)] == original
    return ram3, bytes(memory.ram[2])


def absolute_operand_candidates(raw):
    """List static hits in retained resident bytes, including unaligned bytes."""
    ram3, ram2 = cold_duplicate(raw)
    chunks = ((0xa000, ram3[:0x8c0]), (0xb000, ram3[0x1000:COPY_END-0xa000]),
              (0xc000, ram2[:0x1fe0]))
    operands = {opcode: (name, mode) for opcode, (name, mode) in enumerate(MPU.disassemble)
                if mode in ('abs', 'abx', 'aby', 'ind')}
    suspects = []
    for base, code in chunks:
        for at in range(len(code)-2):
            if code[at] not in operands:
                continue
            opcode, mode = operands[code[at]]
            target = code[at+1]+256*code[at+2]
            if ORIGIN <= target < END or (mode in ('abx', 'aby') and ORIGIN-255 <= target < ORIGIN):
                suspects.append((hex(base+at), opcode, mode, hex(target), code[max(0, at-2):at+5].hex()))
    return suspects


def static_report(raw):
    rebuilt, info = Pose.proposal(raw)
    assert rebuilt == raw
    symbols = info['companion_symbols']
    tables = ((symbols['LaserTiles'], symbols['LaserTiles']+4),
              (symbols['LiftSequences'], symbols['SteveLiftForget']))
    candidates = absolute_operand_candidates(raw)
    table_hits = []
    overlaps = []
    for pc, _, _, _, context in candidates:
        pc = int(pc, 16)
        if any(start <= pc < end for start, end in tables):
            table_hits.append(hex(pc))
            continue
        data = bytes.fromhex(context)
        start = 0 if pc == 0xd2f4 else 1
        opcode, mode = MPU.disassemble[data[start]]
        assert mode in ('abs', 'abx', 'aby') and opcode in ('STA', 'JMP', 'JSR', 'INC', 'LDA'), (
            hex(pc), context, opcode, mode)
        overlaps.append(hex(pc))
    assert table_hits == ['0xd23e', '0xd625'] and len(overlaps) == 30
    return dict(operand_overlaps=overlaps, table_hits=table_hits)


def jay_context(raw):
    import check_steve_shatterhand_upgrade_transport_1111 as Upgrade
    import deliver_steve_laserbot_1111 as Laser
    import deliver_steve_lift_1111 as Lift
    import deliver_steve_lift_art_1111 as Art

    base = Laser.recover_parent(Lift.recover_parent(Art.recover_parent(raw)))
    jay = Upgrade.original_jay_image(Upgrade.source_image(base))
    rebuilt, info = Upgrade.Jay.proposal(Upgrade.Jay.recover_parent(jay))
    assert rebuilt == jay
    return Upgrade.Jay, info


def warm_routes(raw, which):
    rebuilt, info = Pose.proposal(raw)
    assert rebuilt == raw
    frame = C.Game.frame
    found, updates = Counter(), Counter()
    epoch = None
    expected = preimage(raw)

    def authenticated(memory):
        return C.Common.headers(memory) == (info['cookie'],)*2

    def checked(memory, observe=None):
        bus = type(memory)
        get, put = bus.__getitem__, bus.__setitem__

        def watch(m, at, operation):
            if isinstance(at, int) and ORIGIN <= at < END and m.rawtags[1] == 3 and authenticated(m):
                found[epoch, operation, hex(at)] += 1

        def read(m, at):
            watch(m, at, 'read')
            return get(m, at)

        def write(m, at, value):
            watch(m, at, 'write')
            return put(m, at, value)

        with patch.object(bus, '__getitem__', read), patch.object(bus, '__setitem__', write):
            frame(memory, observe)
        if authenticated(memory):
            assert memory.ram[3][ORIGIN-0xa000:END-0xa000] == expected
            updates[epoch] += 1

    if which == 'jay':
        jay, jay_info = jay_context(raw)
    with patch.object(C.Game, 'frame', checked):
        if which == 'steve':
            epoch = 'Steve earned Alpha lift'
            Pose.graphics(raw, info)
            print(f'{epoch} {updates[epoch]} authenticated updates', flush=True)
            epoch = 'Steve earned Laserbot'
            Carrier.Laser.exercise(raw, info)
        else:
            epoch = 'Jay earned 1-2 machinegun'
            jay.earned_route(raw, jay_info | {'cookie': info['cookie']})
    assert not found, found
    return dict(updates=updates, authenticated_reads_writes=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('check', choices=('static', 'steve', 'jay'))
    args = parser.parse_args()
    raw = Live.DONOR.HOST.read_bytes()
    assert C.digest(raw) == '80e6aa3e32574f38b23fa6da6ab3c94bbe7b5ae11b29339b32b11a624fe6f1ed'
    report = dict(parent=C.digest(raw), region=[hex(ORIGIN), hex(END)],
                  proposed_source_page=SOURCE_PAGE, raw3_preimage_sha256=C.digest(preimage(raw)),
                  output_files=0)
    if args.check == 'static':
        report.update(static_report(raw))
    else:
        report.update(warm_routes(raw, args.check))
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    main()
