"""Trace Shatterhand's cartridge-native pickup and upgrade paths in memory."""

import argparse
from collections import Counter
from itertools import product
import json
import sys

import trace_steve_shatterhand_donor_1111 as D


HOST_PIN = '677aad54c55f829d9e7b2aab9e2b1f4eddebcd3c6e6532eeddd9f2ce4e1a26ab'
STEVE_FIELDS = (0x05c2, 0x05c3, 0x05c4, 0x05c5, 0x05c6, 0x05c7, 0x05c8,
                0x05a2, 0x05ab, 0x060c, 0x065c, 0x06fc)
SOURCE = D.ROOT / 'tools/reference/steve_shatterhand_upgrades_1111.s'
ALIASES = {'SteveTokenSymbol': 0x90, 'SteveTokenPattern': 0x05c4, 'SteveArmorTimer': 0x05c2,
           'SteveTokenCountdown': 0x05c3, 'SteveUpgradeState': 0x05a2,
           'SteveTokenPreviewActor': 0x060d, 'SteveRobotActor': 0x060c, 'SteveRobotArrival': 0x06fc,
           'SteveUpgradeSound': 0xf1, 'SteveArmorWindup': 0x05ab, 'SteveUpgradeFacing': 0x05b2,
           'SteveRobotAngle': 0x061c, 'SteveRobotIndex': 0x065c, 'SteveRobotLife': 0x06ec,
           'SteveUpgradeAnim': 0x05b5, 'SteveUpgradeCombo': 0x05ce}
TOKENS = (0x15, 0x2a, 0x25, 0x29, 0x1a, 0x16, 0x19, 0x26)
ORIGIN = 0x8000


def q4(bus, low, high=None):
    return (bus[low] + 256 * bus[high if high is not None else low + 1]) / 16


def actors(bus):
    return [(slot, bus[0x0600+slot], q4(bus, 0xa0+slot, 0xb0+slot),
             q4(bus, 0xc0+slot, 0xd0+slot), bus[0x0620+slot], bus[0x0650+slot])
            for slot in range(12) if bus[0x0600+slot]]


def exploration(seed, count):
    cpu = D.fork(seed)
    bus = cpu.memory
    near = set()
    changes = []

    def watch(at, value):
        if at in STEVE_FIELDS and bus[at] != value:
            changes.append((bus.frame, f'{at:04x}', value, bus.code_key(cpu.pc),
                            q4(bus, 0x80), q4(bus, 0x82)))

    bus.watch = watch
    best_x = q4(bus, 0x80)
    advanced = 0
    jump_end = 0
    last_punch = -20
    for update in range(count):
        x = q4(bus, 0x80)
        if x > best_x:
            best_x, advanced = x, update
        if update >= jump_end + 12 and update-advanced >= 12 and bus[0x5a2] == 0:
            jump_end = update + 14
            print('Donor jump', update, x, q4(bus, 0x82), flush=True)
        y = q4(bus, 0x82)
        near_target = any(0 < ax-x <= 30 and abs(y-ay) <= 15 and not flags & 128
                          for _, _, ax, ay, _, flags in actors(bus))
        punch = near_target and update-last_punch >= 12
        if punch:
            last_punch = update
        pad = (129 if update < jump_end else 128) | (2 if punch else 0)
        D.frame(cpu, pad)
        x, y = q4(bus, 0x80), q4(bus, 0x82)
        for slot, kind, ax, ay, token, flags in actors(bus):
            row = (slot, kind, int(ax)//16, token, flags)
            if abs(x-ax) <= 64 and row not in near:
                near.add(row)
                print('Actor', update, (x, y), (slot, kind, ax, ay, token, flags), flush=True)
        if changes and update % 40 == 39:
            print('Changes', json.dumps(changes), flush=True)
            changes.clear()
    print('Exploration terminal', bus.frame, (q4(bus, 0x80), q4(bus, 0x82)),
          tuple(bus[at] for at in STEVE_FIELDS), json.dumps(changes), flush=True)


def link():
    sys.path.insert(0, str(D.ROOT / 'tools/reference'))
    from sonic_sms_compact_cold_worker_1110 import assemble

    definitions = ''.join(f'{name} = ${at:04x}\n' for name, at in ALIASES.items())
    program = assemble(definitions + SOURCE.read_text(), {'UPGRADE': (ORIGIN, 512)})
    return program


def worker(program):
    memory = [0] * 65536
    image = program['images']['UPGRADE']
    memory[ORIGIN:ORIGIN+len(image)] = image
    return D.NesMPU(memory=memory)


def banks(cpu, low, high):
    bus = cpu.memory
    bus.bank_select &= ~0x40
    bus.registers = bus.registers[:6] + (low, high)


def call(cpu, entry, a=0, x=0):
    cpu.pc, cpu.a, cpu.x, cpu.sp = entry, a, x, 0xf0
    cpu.stPushWord(D.STOP - 1)
    for _ in range(15_000):
        if (cpu.pc, cpu.sp) == (D.STOP, 0xf0):
            return
        assert cpu.memory[cpu.pc], ('Unexpected BRK', hex(cpu.pc), hex(entry))
        cpu.step()
    raise AssertionError(('Donor leaf did not return', hex(entry), hex(cpu.pc)))


def physical_tokens(seed, program):
    fields = program['symbols']
    token = ALIASES['SteveTokenPattern']
    checks = Counter()
    for slots in product(range(3), repeat=3):
        packed = sum(value << (i * 2) for i, value in enumerate(slots))
        for kind, entry in ((1, 0x82b5), (2, 0x82f3)):
            original = D.fork(seed)
            banks(original, 8, 3)
            bus = original.memory
            q = worker(program)
            slot = 1
            bus[0x600+slot] = 10
            bus[token] = q.memory[token] = packed
            call(original, entry, kind, slot)
            call(q, fields['SteveTokenPreview'], kind)
            if 0 not in slots:
                assert not bus[0x600+slot] and not q.p & q.CARRY
                checks['full_rejections'] += 1
                continue
            index = slots.index(0)
            expected = packed | kind << (2 * index)
            assert q.p & q.CARRY and q.a == expected and q.x == index
            assert bus[0x620+slot] == expected and bus[0x610+slot] == 255 and bus[0x650+slot] & 128
            assert bus[token] == packed and bus[0xf1] == 0x10
            checks['matching_contact_previews'] += 1
            # Directed terminal flight geometry. The real actor worker
            # commits its candidate only after the final HUD-space contact.
            bus[0xb0+slot], bus[0xd0+slot] = bus[0x31]+8, bus[0x33]+2
            banks(original, 2, 3)
            call(original, 0xaa15, x=slot)
            assert bus[token] == expected and not bus[0x600+slot], (slots, kind, bus[token], expected)
            checks['matching_physical_flight_commits'] += 1
    return dict(checks)


def combination_timing(seed, program):
    tokens = program['symbols']['SteveTokenPatterns']
    relative = tokens - ORIGIN
    image = program['images']['UPGRADE']
    assert image[relative:relative+8] == bytes(TOKENS)
    fields = {name: at for name, at in ALIASES.items() if name not in ('SteveTokenSymbol',)}
    timing = Counter()
    for combo, packed in enumerate(TOKENS, 1):
        for existing, face in product((0, combo, (combo % 8) + 1, 0xff), (0, 128)):
            original = D.fork(seed)
            banks(original, 12, 13)
            bus = original.memory
            assert bus.code_key(0x9250) == (12, 0x9250)
            q = worker(program)
            for name, at in fields.items():
                bus[at] = q.memory[at] = {
                    'SteveTokenPattern': packed, 'SteveRobotActor': existing, 'SteveUpgradeFacing': face,
                    'SteveTokenPreviewActor': 3, 'SteveUpgradeAnim': 9, 'SteveUpgradeCombo': 0x6f,
                }.get(name, 0)
            for age in range(1, 130):
                call(original, 0x9250)
                call(q, program['symbols']['SteveTokenTick'])
                assert all(bus[at] == q.memory[at] for at in fields.values()), (
                    combo, existing, face, age, [(name, bus[at], q.memory[at]) for name, at in fields.items()
                                               if bus[at] != q.memory[at]])
                if age == 80:
                    assert bus[0x5c3] == 0x30 and bus[0x5c4] == 0
                    if existing == combo:
                        assert (bus[0x5a2], bus[0x5ab], bus[0xf1]) == (0x0d, 0x7f, 0x1d)
                    else:
                        assert (bus[0x60c], bus[0x65c], bus[0xf1]) == (combo, combo-1, 0x1e)
                timing['paired_token_updates'] += 1
            timing['matching_transform_grants' if existing == combo else 'matching_robot_grants'] += 1
            if existing == combo:
                for age in range(1, 33):
                    call(original, 0x97e1)
                    call(q, program['symbols']['SteveArmorTransformTick'])
                    for name in ('SteveArmorWindup', 'SteveUpgradeState', 'SteveUpgradeAnim',
                                 'SteveUpgradeCombo', 'SteveArmorTimer'):
                        at = fields[name]
                        assert bus[at] == q.memory[at], (combo, existing, face, age, name, bus[at], q.memory[at])
                    timing['paired_transform_updates'] += 1
                assert (bus[0x5a2], bus[0x5c2]) == (0, 0x7f)
    return dict(timing)


def initialized_companion(seed):
    cpu = D.fork(seed)
    bus = cpu.memory
    birth = D.fork(seed)
    banks(birth, 12, 13)
    call(birth, 0x9300, x=0)
    # Transfer the original constructor's actor bytes without changing
    # the actual running player's PC, stack, mapper, or controller phase.
    bus.ram[0x600:0x700] = birth.memory.ram[0x600:0x700]
    assert bus[0x60c] == 1 and bus[0x65c] == 0
    for _ in range(36):
        D.frame(cpu, 0)
    assert bus[0x60c] == 1
    return cpu


def original_armor_lifetime(seed):
    cpu = initialized_companion(seed)
    bus = cpu.memory
    bus[0x5c4] = TOKENS[0]
    events = []
    samples = []
    baseline = bus.frame
    state = (bus[0x5a2], bus[0x5c2])
    armed_at, expired_at = None, None
    for age in range(1, 2600):
        D.frame(cpu, 0)
        updated = (bus[0x5a2], bus[0x5c2])
        if age % 120 == 0:
            samples.append((age, updated[1]))
        if updated[0] != state[0] or bool(updated[1]) != bool(state[1]):
            events.append((bus.frame-baseline, *updated, bus[0x60c]))
        if updated[1] and not state[1]:
            armed_at = age
        if state[1] and not updated[1]:
            expired_at = age
            break
        state = updated
    assert armed_at is not None and expired_at is not None, (events, samples)
    return dict(ready_at=armed_at, expires_at=expired_at,
                rendered_frame_lifetime=expired_at-armed_at, state_changes=events, timer_samples=samples,
                initial_tokens_directed=True)


def companion_controls(seed):
    results = {}
    for label, pads in (('down', [32]*24), ('down_plus_A', [32]*3+[33]*21)):
        cpu = initialized_companion(seed)
        bus = cpu.memory
        states = []
        for age, pad in enumerate(pads, 1):
            D.frame(cpu, pad)
            if not states or states[-1][1] != bus[0x5a2]:
                states.append((age, bus[0x5a2], q4(bus, 0x80), q4(bus, 0x82)))
        results[label] = states
    assert [row[1] for row in results['down']] == [3], results
    assert any(row[1] == 4 for row in results['down_plus_A']), results
    return results


def coin_checks(seed):
    credits = checks = 0
    for amount, entry in ((5, 0x827e), (20, 0x8299)):
        for balance in (0, 19, 235, 251, 255, 256, 1023, 65535):
            cpu = D.fork(seed)
            banks(cpu, 8, 3)
            bus = cpu.memory
            bus[0x5c6], bus[0x5c7] = balance & 255, balance >> 8
            call(cpu, entry, x=1)
            assert bus[0x5c6] + 256*bus[0x5c7] == (balance+amount) & 0xffff
            assert bus[0xf1] == 0x0f and bus[0x651] & 0x80
            credits += 1
    for price in (10, 30, 200):
        for due in (0, 4, 40, 240):
            for remaining in (0, price-1, price, price+1, 256):
                cpu = D.fork(seed)
                banks(cpu, 12, 13)
                bus = cpu.memory
                balance = due + remaining
                bus[0x5c6], bus[0x5c7], bus[0x56] = balance & 255, balance >> 8, due
                call(cpu, 0x9e62, a=price)
                assert bool(cpu.p & cpu.CARRY) == (remaining >= price), (price, due, remaining)
                assert bus[0x5c6] + 256*bus[0x5c7] == balance
                checks += 1
    return dict(original_coin_credits=credits, original_affordability_checks=checks)


def host_pickup():
    import check_steve_shatterhand_live_1111 as Live
    import compose_steve_shatterhand_1111 as S

    raw = D.HOST.read_bytes()
    if D.sha256(raw).hexdigest() != HOST_PIN:
        from check_jay_silius_machinegun_1111 import recover_parent

        raw = recover_parent(raw)
    assert D.sha256(raw).hexdigest() == HOST_PIN
    m, opens = Live.opening(raw, 2)
    punch = S.link(S.W.Symbols.bundle(), movement_entry=0xdc00)
    first = Live.natural_goomba(m, punch)
    assert first['score'] == 1 and opens == 167
    fields = {name: S.W.address(m.bundle, name) for name in ('JnPreparePickup', 'JnCollectPickup',
              'InvPickup', 'InvPickupOwner', 'JnHealth', 'JnMaxHearts', 'JnOwnedTier')}
    events = []
    current = 0

    def stats():
        return tuple(m[fields[name]] for name in ('JnHealth', 'JnMaxHearts', 'JnOwnedTier'))

    def tick(pad):
        nonlocal current
        current += 1
        m.controller_pad = pad

        def visit(memory, cpu):
            if memory.rawtags[1] != 0xe2:
                return
            for name in ('JnPreparePickup', 'JnCollectPickup'):
                if cpu.pc == fields[name]:
                    slot = cpu.x
                    x = 256*S.N.get(m, 'Enemy_PageLoc', slot) + S.N.get(m, 'Enemy_X_Position', slot)
                    events.append((current, name, Live.player(m), x, S.N.get(m, 'Enemy_Y_Position', slot),
                                   m[fields['InvPickup']+slot], m[fields['InvPickupOwner']+slot]))

        S.C.Game.frame(m, visit)
        assert Live.mode(m) == S.PLAY and S.N.get(m, 'NumberofLives') == 2
        assert m[S.FIELDS['SteveArmor']] == 0

    def walk(target):
        for _ in range(170):
            gap = target - Live.player(m)[0]
            if abs(gap) <= 1:
                return
            tick(1 if gap > 0 else 2)
        raise AssertionError(('Native pickup approach', target, Live.player(m), events))

    start = stats()
    walk(329)
    for _ in range(7):
        tick(0)
    for age in range(62):
        tick(128 if age < 9 else 0)
    assert any(event[1] == 'JnPreparePickup' for event in events), (Live.player(m), events)
    attempts = []
    if stats() == start:
        revealed, reveal_step, prefix = S.C.Vector.clone(m), current, list(events)
        for launch in (302, 291, 375, 386, 316):
            m, current, events = S.C.Vector.clone(revealed), reveal_step, list(prefix)
            walk(launch)
            for _ in range(9):
                tick(0)
            origin = Live.player(m)
            facing = 1 if origin[0] < 336 else 2
            apex = origin[1]
            for age in range(75):
                tick((128 if age < 9 else 0) | facing)
                apex = min(apex, Live.player(m)[1])
                if stats() != start:
                    break
            attempts.append((origin, apex, Live.player(m)))
            if stats() != start:
                break
    assert stats() == (8, 4, 1), (Live.player(m), start, stats(), events, attempts)
    assert any(event[1] == 'JnCollectPickup' and event[3] == 336 and event[5:] == (0x81, 16)
               for event in events), events
    return dict(steps=current, before=start, after=stats(), events=events, terminal=Live.player(m), attempts=attempts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--explore', type=int, default=0)
    parser.add_argument('--host', action='store_true')
    parser.add_argument('--donor-armor', action='store_true')
    args = parser.parse_args()
    if args.host:
        print(json.dumps(dict(host_SHA256=HOST_PIN, pickup=host_pickup(), output_files=0), sort_keys=True), flush=True)
        return
    seed = D.boot(D.DONOR.read_bytes())
    print('Exact original boot', D.PIN, D.hardware_anchors(seed), flush=True)
    if args.explore:
        exploration(seed, args.explore)
    else:
        program = link()
        if not args.donor_armor:
            print('Exact original token actor pairs', json.dumps(physical_tokens(seed, program)), flush=True)
            print('Exact original combination and armor pairs', json.dumps(combination_timing(seed, program)), flush=True)
        print('Original armor on ordinary frames', json.dumps(original_armor_lifetime(seed)), flush=True)
        print('Original companion controller', json.dumps(companion_controls(seed)), flush=True)
        print('Original coins and pad prices', json.dumps(coin_checks(seed)), flush=True)
        image = program['images']['UPGRADE']
        print(json.dumps(dict(passed=True, donor_SHA256=D.PIN, code_bytes=len(image),
                              code_SHA256=D.sha256(image).hexdigest(), output_files=0), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
