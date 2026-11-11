"""Bisect the current Mega Giant Mario cold-start failure without ROM outputs."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import check_current_roster_stage_ingress_1110 as Ingress
import compose_prince_brick_1111 as PrinceBrick
import compose_steve_shatterhand_1111 as Punch
import deliver_prince_exposed_brick_idle_1111 as PrinceIdle
import deliver_steve_move_1111 as Steve


ROW = {'slot': 0, 'cycle': 9, 'name': 'MEGA GIANT MARIO', 'raw': 0}
STAGES = ((Ingress.R / 'build/mega-giant-current-native-1110/candidate.nes'),
          (Ingress.R / 'build/complete-roster-native-1110/candidate.nes'))
LEGACY = bytes.fromhex('020101d0d600d400')
COMPACT = bytes.fromhex('020101d600d400ff')
SCENE_COOKIE = bytes.fromhex('a7000902331ad79e8d280b2d')
FIX_PIN = '5482f0d69d0179e0d4361b14c599199fc88ed9bfb899edb7735fe9fe682ef455'


def digest(data):
    return sha256(data).hexdigest()


def offset(bank, pc):
    return 16 + bank * 8192 + (pc & 8191)


def proposal(raw):
    assert digest(raw) == Steve.PIN
    at = offset(84, 0xbef8)
    mapper = offset(123, 0xb9d6)
    assert raw[mapper:mapper+6] == bytes.fromhex('a5050a186904')
    assert raw[at-12:at+8] == SCENE_COOKIE + LEGACY
    assert raw[offset(84, 0xbed7):offset(84, 0xbed7)+6] == bytes.fromhex('b9e0dfd9ecbe')
    assert raw.count(SCENE_COOKIE + LEGACY) == 1
    result = raw[:at] + COMPACT + raw[at+8:]
    assert sum(a != b for a, b in zip(raw, result, strict=True)) == 5
    assert digest(result) == FIX_PIN
    return result


def recover_parent(candidate):
    at = offset(84, 0xbef8)
    assert digest(candidate) == FIX_PIN and candidate[at:at+8] == COMPACT
    raw = candidate[:at] + LEGACY + candidate[at+8:]
    assert digest(raw) == Steve.PIN
    return raw


def reversible(raw):
    assert digest(raw) == Steve.PIN
    prince_idle = Steve.recover_parent(raw)
    punch = PrinceIdle.recover_parent(prince_idle)
    prince_brick = Punch.recover_parent(punch)
    old, new, _ = PrinceBrick.support_workers()
    jay, _ = PrinceBrick.replace_worker(prince_brick, new, old)
    assert digest(jay) == Punch.PIN
    return (jay, prince_brick, punch, prince_idle, raw)


def opening(raw, row=ROW, *, cold=False):
    b = dict(Ingress.F.Symbols.bundle(), raw=raw)
    original = Ingress.N.NesMPU
    rows, calls, state = [], [], {}

    class Trace(original):
        def step(self):
            pc, m = self.pc, self.memory
            if m.rawtags[1] == 251 and pc in (0xaf40, 0xb9d6):
                pointer = m[6] | m[7] << 8
                descriptor = bytes(m[pointer+i] for i in range(8)).hex()
                if pc == 0xaf40:
                    calls.append(descriptor)
                else:
                    start = 3 if m[pc+5] == 4 else 4
                    at = pointer + start + m[5] * 2
                    rows.append(m[at] + (m[at+1] & 3) * 256)
            result = super().step()
            # Ingress rejects BRK before executing it, so inspect each
            # transfer target immediately after the preceding instruction.
            next_pc = self.pc
            if m.rawtags[1] == 3 and next_pc in (0xa000, 0xa200) and hex(next_pc) not in state:
                state[hex(next_pc)] = {
                    'opcodes': bytes(m[next_pc:next_pc+8]).hex(),
                    'headers': [bytes(m.ram[bank][0x1fe0:0x1ff0]).hex() for bank in (2, 3)],
                    'ppu_reads': m.ppu_reads,
                }
            return result

    with patch.object(Ingress.N, 'NesMPU', Trace if cold else original):
        try:
            result = Ingress.stage(b, row)
        except AssertionError as error:
            result = {'passed': False, 'error': error.args}
    if cold:
        result.update(cold_descriptors=calls, physical_ppu_rows=rows, first_draw=state)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--extra', action='append', type=Path, default=[])
    parser.add_argument('--repair', action='store_true')
    parser.add_argument('--chronology', action='store_true')
    args = parser.parse_args()
    raw = Steve.NIGHTLY.read_bytes()
    installed = raw if digest(raw) == FIX_PIN else None
    if installed is not None:
        raw = recover_parent(installed)
    if args.repair:
        candidate = proposal(raw)
        if installed is not None:
            assert candidate == installed
        assert recover_parent(candidate) == raw
        known_good = STAGES[1].read_bytes()
        for at, n in ((offset(3, 0xb24d), 15), (offset(84, 0xbe00), 256),
                      (1048592 + 212 * 1024, 1024), (1048592 + 214 * 1024, 1024)):
            assert known_good[at:at+n] == raw[at:at+n], hex(at)
        old = opening(known_good, cold=True)
        assert old['passed'] and old['physical_ppu_rows'] == [214, 214, 212, 212], old
        print('Known-good Giant', json.dumps(old, sort_keys=True), flush=True)
        negative = opening(raw, cold=True)
        assert not negative['passed'] and negative['physical_ppu_rows'] == [720, 720, 0, 0], negative
        print('Current negative', json.dumps(negative, sort_keys=True), flush=True)
        fixed = opening(candidate, cold=True)
        assert fixed['passed'] and fixed['physical_ppu_rows'] == old['physical_ppu_rows'], fixed
        assert fixed['first_draw']['0xa200']['opcodes'] == old['first_draw']['0xa200']['opcodes'], fixed
        print(json.dumps(dict(candidate_SHA256=digest(candidate), changed_bytes=5,
                              repair=fixed, output_files=0), sort_keys=True), flush=True)
        foreign = ((0, 0, 'MARIO', 0), (0, 8, 'MINI MARIO', 41),
                   (15, 0, 'MIKE JONES', 16), (15, 1, 'JAY MCCRAY', 16),
                   (15, 2, 'STEVE HERMANN', 16))
        for values in foreign:
            row = dict(zip(('slot', 'cycle', 'name', 'raw'), values, strict=True))
            before, after = opening(raw, row), opening(candidate, row)
            assert before == after and after['passed'], (row, before, after)
            print('Foreign opening', json.dumps(after, sort_keys=True), flush=True)
        return
    if args.chronology:
        import check_sonic_compact_cold_worker_1110 as Compact
        import check_sonic_seventh_cold_owner_1110 as Seventh
        import stage_sonic_original_scene_1110 as Public
        from check_sonic_original_physical_1110 import PIN as SONIC_PIN

        old = STAGES[1].read_bytes()
        compact = Compact.proposal(old, Compact.B.build())[0]
        seventh = Seventh.proposal(old)[0]
        assert digest(seventh) == 'd07012de9762e93ca76cb283ba84e9b8a9a7bd532364fd94ce4ca6101687cb72'
        for label, image in (('compact worker only', compact), ('Sonic seventh cold', seventh)):
            result = opening(image, cold=True)
            assert not result['passed'] and result['physical_ppu_rows'] == [720, 720, 0, 0], result
            print(json.dumps(dict(release=label, ROM_SHA256=digest(image), **result), sort_keys=True), flush=True)
        try:
            previous = Public.Portrait.Original.WWF.reconstruct()[0]
            assert digest(previous) == Public.PARENT
            result = opening(previous, cold=True)
            assert result['passed'] and result['physical_ppu_rows'] == [214, 214, 212, 212], result
            print(json.dumps(dict(release='WWF pickup and palette', ROM_SHA256=digest(previous), **result),
                             sort_keys=True), flush=True)
            public = Public.reconstruct()[0]
        except FileNotFoundError as error:
            print(json.dumps(dict(release='Sonic delivered', source_unavailable=str(error)), sort_keys=True), flush=True)
        else:
            assert digest(public) == SONIC_PIN
            result = opening(public, cold=True)
            assert not result['passed'] and result['physical_ppu_rows'] == [720, 720, 0, 0], result
            print(json.dumps(dict(release='Sonic delivered', ROM_SHA256=digest(public), **result),
                             sort_keys=True), flush=True)
        return
    images = [(path.parent.name, path.read_bytes()) for path in (*STAGES, *args.extra) if path.is_file()]
    images.extend(zip(('Jay movement', 'Prince brick', 'Steve punch', 'Prince idle', 'Steve movement'),
                      reversible(raw), strict=True))
    for label, image in images:
        print(json.dumps(dict(release=label, ROM_SHA256=digest(image), **opening(image)), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
