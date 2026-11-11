"""Build and trace Steve's live Alpha/Beta item-block pickup in memory."""

import argparse
from itertools import product
import json

import check_steve_shatterhand_upgrade_transport_1111 as Transport
import compose_steve_shatterhand_1111 as S


C, H, N, W = S.C, S.H, S.N, S.W
T, Live = Transport.T, Transport.Steve.Live
PIN = '2d7fb6e63ea55f2d0eb9ef3af4efc467233da013dc70e295952a4adcdd14ecdb'
SOURCE = H.ROOT / 'tools/reference/steve_shatterhand_token_ingress_1111.s'
GATE, ORIGIN = 0xbfed, 0xc200
INGRESS_FIELDS = dict(SteveTokenStamp=0xc3fc, SteveTokenPending=0xc3fd,
                      SteveTokenFlightX=0xc3fe, SteveTokenFlightY=0xc3ff)
NATIVE_FIELDS = ('InvPickup', 'InvPickupOwner', 'JnPickupSlot', 'Enemy_Flag',
                 'Enemy_ID', 'Enemy_State', 'Enemy_X_Position', 'Enemy_PageLoc',
                 'Enemy_Y_Position', 'Enemy_Y_HighPos', 'ScreenLeft_X_Pos',
                 'GamePauseStatus', 'OperMode', 'OperMode_Task', 'GameEngineSubroutine')


def link(bundle, *, lifecycle_tick=None, token_draw=None, token_hud=''):
    native = {name: W.address(bundle, name) for name in NATIVE_FIELDS}
    private = {name: Transport.STATE+i for i, name in enumerate(Transport.Upgrade.ALIASES)}
    definitions = lambda names: ''.join(f'{n}=${at:04x}\n' for n, at in names.items())
    core = H.assemble(definitions(private) + Transport.Upgrade.SOURCE.read_text(),
                      {'UPGRADE': (Transport.ORIGIN, Transport.STATE-Transport.ORIGIN)})
    punch = S.link(bundle, movement_entry=0xdc00)
    ps = punch['symbols']
    names = native | private | INGRESS_FIELDS | S.FIELDS | dict(
        SteveTokenPreview=core['symbols']['SteveTokenPreview'],
        NativeAttack=ps['SteveAttackMain'], NativeOther=ps['OtherSteveCaller'],
        NativeDraw=ps['SteveDraw'], NativeHitEnemy=ps['SteveHitEnemy'])
    source = SOURCE.read_text()
    if lifecycle_tick is not None:
        source = S.changed(source, '    jsr SteveTokenEpoch\n',
                           f'    jsr SteveTokenEpoch\n    jsr ${lifecycle_tick:04x}\n')
    if token_draw is not None or token_hud:
        draw_calls = '' if token_draw is None else f'    jsr ${token_draw:04x}\n'
        if token_hud:
            draw_calls += '    jsr SteveTokenHud\n'
        source = S.changed(source, 'SteveTokenDraw:\n    jmp NativeDraw\n',
                           f'SteveTokenDraw:\n    pha\n{draw_calls}    pla\n    jmp NativeDraw\n')
        source += '\n' + token_hud
    result = H.assemble(definitions(names) + source,
                        {'NATIVE_GATE': (GATE, 19), 'TOKEN_INGRESS': (ORIGIN, 447)})
    return result, punch


def proposal(raw, *, lifecycle=b'', lifecycle_tick=None, token_draw=None, token_hud='',
             extra=b'', extra_edits=(), roll_storage=False):
    assert T.digest(raw) == PIN
    info, punch = link(W.Symbols.bundle(), lifecycle_tick=lifecycle_tick,
                       token_draw=token_draw, token_hud=token_hud)
    symbols, images = info['symbols'], info['images']
    edits = []

    def patch(at, before, after):
        assert len(before) == len(after) and raw[at:at+len(before)] == before, hex(at)
        edits.append((at, before, after))

    def call(name):
        return b'\x20' + S.address_bytes(symbols[name])

    def bank(pc, before, after):
        patch(C.offset(98, pc), before, after)

    bank(0xa681, bytes.fromhex('9d627d'), call('StevePrepareBridge'))
    bank(0xa745, bytes.fromhex('8e185c'), call('SteveCollectBridge'))
    gate = images['NATIVE_GATE']
    bank(GATE, b'\xff'*len(gate), gate)
    combat = punch['images']['COMBAT']
    head, _ = S.LAYOUT['COMBAT']
    origin = C.CHR + 234*1024 + head - 0xbc00
    # This owned CHR row is also the raw3 live Steve COMBAT body.
    before = combat[:11]
    patch(origin, before, b'\x4c'+S.address_bytes(symbols['SteveTokenDispatch'])+b'\xea'*8)
    old_hit = b'\x20'+S.address_bytes(punch['symbols']['SteveHitEnemy'])
    assert combat.count(old_hit) == 1
    patch(origin+combat.index(old_hit), old_hit, call('StevePunchToken'))
    for edit in extra_edits:
        patch(*edit)

    binding = b''.join(at.to_bytes(4, 'little')+after for at, _, after in edits)
    at = C.offset(94, 0xb2ef)
    options = {'extra': extra} if extra else {}
    candidate, resident = Transport.allocate(raw, raw[at:at+16], ingress=images['TOKEN_INGRESS'],
                                             lifecycle=lifecycle, binding=binding,
                                             roll_storage=roll_storage, **options)
    output = bytearray(candidate)
    for at, before, after in edits:
        assert output[at:at+len(before)] == before, hex(at)
        output[at:at+len(after)] = after
    return bytes(output), dict(info, cookie=resident['cookie'], punch=punch, edits=edits,
                               upgrade_page=resident['upgrade_page'],
                               upgrade_descriptor=resident['upgrade_descriptor'])


def authored_reveal(raw, info, *, trace=False):
    m, opens = Live.opening(raw, 2)
    assert opens == 167 and C.Common.headers(m) == (info['cookie'],)*2
    fight = Live.natural_goomba(m, info['punch'])
    assert fight['score'] == 1
    symbols = info['symbols']
    update = 0
    events = []

    def frame(pad):
        nonlocal update
        update += 1
        m.controller_pad = pad

        def observe(q, cpu):
            if q.rawtags[2] != 2:
                return
            for name in ('StevePrepareToken', 'SteveCollectToken', 'SteveTokenPreview'):
                if cpu.pc == symbols[name]:
                    events.append((update, name, Live.player(q)))
            if trace and cpu.pc == symbols['SteveTokenDispatch'] and 0x81 <= cpu.a <= 0x8d:
                print('Token boundary', update, cpu.a, cpu.x, cpu.y, cpu.sp,
                      bytes(q[0x101+cpu.sp:0x116+cpu.sp]).hex(' '), flush=True)

        C.Game.frame(m, observe)
        assert Live.mode(m) == S.PLAY and N.get(m, 'NumberofLives') == 2

    def walk(target):
        for _ in range(170):
            gap = target-Live.player(m)[0]
            if abs(gap) <= 1:
                return
            frame(1 if gap > 0 else 2)
        raise AssertionError(('Token approach', target, Live.player(m)))

    walk(329)
    for _ in range(7):
        frame(0)
    for age in range(62):
        frame(128 if age < 9 else 0)
    stamp = m.ram[2][INGRESS_FIELDS['SteveTokenStamp']-0xc000]
    assert N.get(m, 'InvPickup', 5) == 0x8c and stamp == 1 << 5, (update, events, stamp, N.get(m, 'InvPickup', 5))
    assert N.get(m, 'Enemy_State', 5) == 0x80
    return m, dict(events=events, updates=update, walk=walk, frame=frame)


def collect(m, route, info, *, beta=False):
    walk, frame = route['walk'], route['frame']
    fields = info['symbols']
    pending, pattern = (fields[name]-0xc000 for name in ('SteveTokenPending', 'SteveTokenPattern'))
    hp = tuple(N.get(m, name) for name in ('JnHealth', 'JnMaxHearts', 'JnOwnedTier'))
    walk(302)
    for _ in range(9):
        frame(0)
    launch = Live.player(m)
    switches = []
    previous = 0x8c
    for age in range(75):
        frame((128 if age < 9 else 0) | (64 if beta and 17 <= age < 24 else 0) | 1)
        tag = N.get(m, 'InvPickup', 5)
        if tag and tag != previous:
            switches.append((age, Live.player(m), previous, tag))
        previous = tag
        if m.ram[2][pending]:
            break
    value = 2 if beta else 1
    assert switches == ([(19, (308, 110), 0x8c, 0x8d)] if beta else []), switches
    assert m.ram[2][pending] == value and not m.ram[2][pattern], (Live.player(m), route['events'])
    assert not N.get(m, 'Enemy_Flag', 5) and not N.get(m, 'InvPickup', 5)
    assert tuple(N.get(m, name) for name in ('JnHealth', 'JnMaxHearts', 'JnOwnedTier')) == hp
    for flight in range(80):
        frame(0)
        if m.ram[2][pattern]:
            break
    assert m.ram[2][pattern] == value and not m.ram[2][pending], (flight, Live.player(m))
    return dict(launch=launch, switched=switches, collection=route['events'], pattern=value,
                flight_updates=flight+1, health=hp)


def second_block(raw, info):
    import replay_steve_route_1111 as Route

    m, first = authored_reveal(raw, info)
    first_receipt = collect(m, first, info)
    frame, walk = first['frame'], first['walk']
    arrival = Route.continue_route(m, target=1236, max_updates=2500)
    assert (arrival['x'], arrival['y'], arrival['health']) == (1236, 176, 6)
    walk(1239)
    for _ in range(7):
        frame(0)
    reveal = Live.player(m)
    for age in range(62):
        frame(128 if age < 9 else 0)
    assert (N.get(m, 'Enemy_PageLoc', 5)*256+N.get(m, 'Enemy_X_Position', 5),
            N.get(m, 'Enemy_Y_Position', 5), N.get(m, 'InvPickup', 5)) == (1248, 120, 0x8c)
    walk(1214)
    for _ in range(9):
        frame(0)
    launch = Live.player(m)
    for age in range(72):
        frame((128 if age < 9 else 0) | 1)
        if m.ram[2][0x3fd]:
            break
    contact = Live.player(m)
    assert m.ram[2][0x3fd] == 5
    for _ in range(30):
        frame(0)
    assert m.ram[2][0x1f1] == 5 and not m.ram[2][0x3fd]
    second_receipt = dict(reveal=reveal, launch=launch, collection=contact, pattern=5)
    return m, dict(first=first_receipt, second=second_receipt, frame=frame, walk=walk)


def third_block(raw, info, *, third_beta=False):
    import replay_steve_route_1111 as Route

    m, route = second_block(raw, info)
    frame, walk = route['frame'], route['walk']
    arrival = Route.continue_route(m, target=1695, max_updates=2000)
    assert (arrival['x'], arrival['y'], arrival['health']) == (1695, 176, 6)

    def board(walk_target, release_target):
        walk(walk_target)
        for _ in range(7):
            frame(0)
        launch = Live.player(m)
        for age in range(90):
            x, _ = Live.player(m)
            frame((128 if age < 9 else 0) | (1 if x < release_target else 0))
            if age > 10 and N.get(m, 'Player_State') == 0 and Live.player(m)[1] < 176:
                break
        assert age == 30 and Live.player(m)[1] == 112
        for _ in range(15):
            frame(0)
        return dict(launch=launch, settled=Live.player(m), landing_age=age)

    center = board(1718, 1738)
    assert center['settled'] == (1747, 112)
    for age in range(64):
        frame(128 if age < 9 else 0)
    item = (N.get(m, 'Enemy_PageLoc', 5)*256+N.get(m, 'Enemy_X_Position', 5),
            N.get(m, 'Enemy_Y_Position', 5))
    assert item == (1744, 56) and N.get(m, 'InvPickup', 5) == 0x8c
    side = board(1670, 1692)
    assert side['settled'] == (1702, 112)
    mature_tag = W.address(m.bundle, 'InvPickup')+5
    switches = 0
    for age in range(80):
        tag = m[mature_tag]
        frame((128 if age < 9 else 0) | (64 if third_beta and age == 17 else 0) | 1)
        if tag == 0x8c and m[mature_tag] == 0x8d:
            switches += 1
        if m.ram[2][0x3fd]:
            break
    contact = Live.player(m)
    pattern = 0x25 if third_beta else 0x15
    assert switches == int(third_beta)
    assert age == 27 and contact == (1732, 44) and m.ram[2][0x3fd] == pattern
    for _ in range(30):
        frame(0)
    assert m.ram[2][0x1f1] == pattern and not m.ram[2][0x3fd]
    assert Live.player(m) == (1740, 48) and N.get(m, 'JnHealth') == 6
    route['third'] = dict(center=center, left_support=side, collection_age=age, collection=contact,
                          item=item, terminal=Live.player(m), pattern=pattern, health=6, lives=2)
    return m, route


def donor_flight(info):
    ref = Transport.Upgrade
    D = ref.D
    raw = D.DONOR.read_bytes()
    assert D.sha256(raw).hexdigest() == D.PIN
    symbols = info['symbols']
    pattern, pending, xfield, yfield = (symbols[name] for name in
        ('SteveTokenPattern', 'SteveTokenPending', 'SteveTokenFlightX', 'SteveTokenFlightY'))
    src = info['images']['TOKEN_INGRESS']
    checked = 0
    for x, y, value in product((0, 8, 109, 112, 127, 159, 160, 247),
                               (25, 32, 39, 47, 48, 51, 88, 128, 239), (1, 2)):
        old = D.NesMPU(memory=D.ShatterhandBus(raw))
        ref.banks(old, 2, 3)
        bus = old.memory
        slot = 1
        for address, item in {0x600+slot: 8, 0x610+slot: 255, 0x620+slot: value,
                              0xa0+slot: x*16 & 255, 0xb0+slot: x//16,
                              0xc0+slot: y*16 & 255, 0xd0+slot: y//16}.items():
            bus[address] = item
        host = D.NesMPU(memory=[0]*65536)
        mem = host.memory
        mem[ORIGIN:ORIGIN+len(src)] = src
        for name, mode in (('OperMode', 1), ('OperMode_Task', 3), ('GameEngineSubroutine', 8)):
            mem[symbols[name]] = mode
        mem[pending], mem[xfield], mem[yfield] = value, x, y
        for _ in range(72):
            for address in range(0x50, 0x54):
                bus[address] = 0
            ref.call(old, 0xaa15, x=slot)
            ref.call(host, symbols['SteveTokenEpoch'])
            assert (mem[xfield], mem[yfield]) == (ref.q4(bus, 0xa0+slot, 0xb0+slot),
                ref.q4(bus, 0xc0+slot, 0xd0+slot)), (x, y, value, checked)
            assert mem[pattern] == bus[0x5c4]
            assert bool(mem[pending]) == bool(bus[0x600+slot])
            checked += 1
            if mem[pattern]:
                break
        assert mem[pattern] == value
    return checked


def native_pickup_parity(raw, candidate, info):
    names = ('JnHealth', 'JnMaxHearts', 'JnOwnedTier', 'JnStars', 'JnUiDirty')
    fields = ('Enemy_ID', 'Enemy_State', 'Enemy_Flag', 'PowerUpType', 'InvPickup',
              'InvPickupOwner', 'InvRisePhase')

    def actor(m, kind):
        for name, value in zip(fields, (46, 128, 1, kind, 0, 0, 0), strict=True):
            m[W.address(m.bundle, name)+5] = value

    def state(m):
        return tuple(N.get(m, name) for name in names) + tuple(N.get(m, name, 5) for name in fields)

    def returned(cpu):
        return cpu.a, cpu.x, cpu.y, cpu.p & 0x83

    counters = {}
    for variant, name in ((0, 'Mike'), (1, 'Jay')):
        bases = [Live.opening(image, variant)[0] for image in (raw, candidate)]
        for kind, tier in product(range(4), (1, 2, 3)):
            pair = [C.Vector.clone(m) for m in bases]
            for m in pair:
                actor(m, kind)
                N.put(m, JnOwnedTier=tier)
            for entry in ('JnPreparePickup', 'JnCollectPickup'):
                cpus = [C.Vector.call(m, entry, x=5) for m in pair]
                assert state(pair[0]) == state(pair[1]), (name, kind, tier, entry)
                assert returned(cpus[0]) == returned(cpus[1]), (name, kind, tier, entry)
        counters[name] = 24

    steve = Live.opening(candidate, 2)[0]
    assert C.Common.headers(steve) == (info['cookie'],)*2
    faults = []
    for bank, offset in product((2, 3), (0x1fe0, 0x1fef)):
        m = C.Vector.clone(steve)
        m.ram[bank][offset] ^= 1
        actor(m, 0)
        C.Vector.call(m, 'JnPreparePickup', x=5)
        assert N.get(m, 'InvPickup', 5) == 0x81 and not m.ram[2][0x3fc]
        faults.append((bank, offset))
    return dict(paired_native_calls=counters, blocked_prepare_faults=faults)


def multiple_native_slots(candidate, info):
    m, _ = Live.opening(candidate, 2)
    symbols = info['symbols']
    slots = (4, 5)
    for slot, x in zip(slots, (132, 200), strict=True):
        for name, value in dict(Enemy_ID=46, Enemy_Flag=1, Enemy_State=128, PowerUpType=0,
                                Enemy_X_Position=x, Enemy_PageLoc=0, Enemy_Y_Position=120,
                                Enemy_Y_HighPos=1).items():
            m[W.address(m.bundle, name)+slot] = value
        C.Vector.call(m, 'JnPreparePickup', x=slot)
        assert N.get(m, 'InvPickup', slot) == 0x8c
    assert m.ram[2][0x3fc] == 0x30

    m.raw_page(2, 2)
    N.put(m, CurrentBankC=2)
    for name, value in dict(SteveHitX=142, SteveHitPage=0, SteveHitY=126,
                            SteveHitHigh=1, SteveHitLife=4).items():
        m[S.FIELDS[name]] = value
    cpu = N.NesMPU(memory=m)
    Transport.Upgrade.call(cpu, symbols['StevePunchToken'])
    assert tuple(N.get(m, 'InvPickup', slot) for slot in slots) == (0x8d, 0x8c)
    assert m[S.FIELDS['SteveHitLife']] == 1

    for slot, stamp, flight in ((4, 0x20, 2), (5, 0, 6)):
        cpu = C.Vector.call(m, 'JnCollectPickup', x=slot)
        assert cpu.p & cpu.CARRY and not N.get(m, 'InvPickup', slot)
        assert m.ram[2][0x3fc] == stamp and m.ram[2][0x3fd] == flight
    assert m.ram[2][0x1f1] == 2
    return dict(slots=slots, punch_changed=4, pending_pattern=6, earlier_letter=2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trace', action='store_true')
    parser.add_argument('--all-blocks', action='store_true')
    args = parser.parse_args()
    raw = Transport.source_image(S.Donor.HOST.read_bytes())
    image, info = proposal(raw)
    m, route = authored_reveal(image, info, trace=args.trace)
    alpha = collect(m, route, info)
    m, route = authored_reveal(image, info, trace=args.trace)
    beta = collect(m, route, info, beta=True)
    result = dict(passed=True, candidate=T.digest(image), gate=len(info['images']['NATIVE_GATE']),
                  resident=len(info['images']['TOKEN_INGRESS']), alpha=alpha, beta=beta,
                  donor_flight_steps=donor_flight(info),
                  isolation=native_pickup_parity(raw, image, info),
                  multiple_slots=multiple_native_slots(image, info), output_files=0)
    if args.all_blocks:
        _, route = third_block(image, info)
        result['second_block'], result['third_block'] = route['second'], route['third']
    print(json.dumps(result))


if __name__ == '__main__':
    main()
