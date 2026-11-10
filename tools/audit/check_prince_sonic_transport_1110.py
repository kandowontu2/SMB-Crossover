"""Qualify the frozen Prince payload on the public Sonic transport in memory."""
import argparse
from collections import Counter
import json
from unittest.mock import patch

import check_prince_logical_support_1110_v8 as Prince
import qualify_prince_logical_support_1110_v8 as Qualify
import stage_sonic_original_1110 as Stage
import stage_sonic_portrait_1110 as Portrait

Q, C, N, I = Prince.Q, Prince.C, Prince.N, Prince.I
PARENT = 'e7a30825f992d9a28c813ee7eb2571e6836b8f75c6579234f7f7a66106a6d896'
SCENE_PARENT = 'd2542ff3c9f78ac26eb7e19d64a7708711bc766515f634b05952bab1be9103f0'
COOKIE = 535471
COMBINED = {
    PARENT: '53b9ea335b92fc05870ad2d3c3838b2f653fc369b0b893cd976e7e4d97c3b924',
    Portrait.PIN: 'f8f91daf9851e76fafaaa55a069b0da5d4eead097d48b3c5fd55435773f6397b',
    SCENE_PARENT: '47a7a6aeabe2cc7db593f431591e52331b834485b3d7638e3f10f95cbf43db4b',
}


def emit(name, result):
    print(name + ' ' + json.dumps(result, separators=(',', ':')), flush=True)


def compose(parent, frozen, *, transport_parent):
    """Allow a downstream parent only when its changes miss the Prince grant."""
    previous, payload, _, layout, _, _, _ = frozen
    assert Q.digest(transport_parent) == PARENT
    assert len(parent) == len(transport_parent) == len(payload['raw']) == 2097168
    spans = [(COOKIE, COOKIE + 16)]
    spans.extend((Q.CHR + page * 1024, Q.CHR + (page + 1) * 1024)
                 for page in layout['carrier_pages'])
    assert len(spans) == 46 and not set(range(321,329)).intersection(layout['carrier_pages'])
    assert 329 in layout['carrier_pages'] and 330 not in layout['carrier_pages']
    allocation = Q.R / 'docs/qa/allocations/sonic-sms-fairy-repack-1110.json'
    alias = json.loads(allocation.read_bytes())['mandatory_atomic_source_change']
    at = alias['file_offset']; expected = bytes.fromhex(alias['new_hex'])
    assert parent[at:at+len(expected)] == previous['raw'][at:at+len(expected)] == expected

    # Every copied byte retains its seventh-owner preimage on the new transport.
    # This catches common, CHR, or downstream scene ownership before overlay.
    public = C.ROM.read_bytes()
    assert Q.digest(public) == C.PIN
    old_transport = Q.Sonic.proposal(public)[0]
    assert Q.digest(old_transport) == layout['parent_SHA256']
    assert all(parent[a:b] == transport_parent[a:b] == old_transport[a:b] for a, b in spans)
    new = bytearray(parent)
    for a, b in spans:
        new[a:b] = payload['raw'][a:b]
    delta = Stage.differences(parent, new)
    scope = {offset for a, b in spans for offset in range(a, b)}
    assert delta.keys() <= scope
    assert not scope.intersection(Stage.differences(transport_parent, parent))
    # Seventh-owner introduction already relocated the Prince cookie from
    # AB9D to AB9F. The eighth-owner and downstream scene deltas are disjoint
    # from this now-stable table entry and all 45 CHR pages.
    assert not scope.intersection(Stage.differences(old_transport, transport_parent))
    assert bytes(new[COOKIE:COOKIE+16]).hex() == layout['Prince_cookie']
    inventory = C.Start.Menu.inventory(parent)
    assert inventory == C.Start.Menu.inventory(bytes(new))
    return bytes(new), dict(layout, in_memory_SHA256=Q.digest(new),
        portable_payload_SHA256=Prince.PIN, transport_parent_SHA256=Q.digest(parent),
        pure_payload_changed_bytes=len(delta), named_menu_entries_preserved=inventory['distinct_named_entries'])


def proposal(*, static_portrait=True, sonic_scene=False):
    raw, program, packet, stage = Stage.reconstruct()
    assert stage['ROM_SHA256'] == PARENT
    frozen = Prince.proposal()
    base = raw
    if static_portrait:
        base, portrait = Portrait.Portrait.proposal(raw)
        assert Q.digest(base) == portrait['ROM_SHA256'] == Portrait.PIN
    if sonic_scene:
        import stage_sonic_original_scene_1110 as Scene
        assert static_portrait
        base, _ = Scene.Palette.proposal(base)
        base, packet, scene = Scene.Scene.proposal(base, packet)
        assert scene['image_SHA256'] == Q.digest(base) == SCENE_PARENT
    image, layout = compose(base, frozen, transport_parent=raw)
    assert layout['in_memory_SHA256'] == COMBINED[layout['transport_parent_SHA256']]
    return C.Start.W.bundle(base), C.Start.W.bundle(image), frozen[2], layout, program, packet, None


def owners(result):
    parent, trial, chunks, layout, program, packet, _ = result
    bus, cold = Stage.Public.A.O, Stage.Public.A.C
    current_program = program['new']
    seeds = {}; counts = Counter()
    cookie = bytes.fromhex(layout['Prince_cookie'])
    for owner in range(37, 44):
        old, new = [bus.blank(bundle) for bundle in (parent, trial)]
        a = cold.cold(old, owner, current_program)
        b = cold.cold(new, owner, current_program)
        if owner != 38:
            cold.parity(old, new, a, b)
            if owner == 43:
                Stage.Public.A.E.owned(new, packet['packet'])
        else:
            assert bus.headers(new) == (cookie,) * 2
            assert bytes(new.ram[3][:len(chunks[0])]) == Q.P.live(chunks[0])
            assert bytes(new.ram[2][0x800:0x800+len(chunks[1])]) == chunks[1]
            assert bytes(old.ram[2][:0x386]) == bytes(new.ram[2][:0x386])
            assert bytes(old.ram[2][0x3b0:0x800]) == bytes(new.ram[2][0x3b0:0x800])
            assert (a['A'], a['X'], a['Y'], a['P']) == (b['A'], b['X'], b['Y'], b['P'])
            assert old.rawtags == new.rawtags
        seeds[owner] = old, new
        counts['cold_owners'] += 1
        warm = Q.Sonic.slim_fork(new)
        assert cold.cold(warm, owner, current_program)['PPU_reads'] == 0
        assert warm.ram == new.ram
        counts['warm_owners'] += 1
        for bank in (2,3):
            for index in range(16):
                m = Q.Sonic.slim_fork(new)
                m.ram[bank][0x1fe0+index] ^= 1
                before = tuple(map(bytes, m.ram)); bus.clear_logs(m)
                assert not cold.invoke(m, bus.AUTH)['P'] & 1
                assert tuple(map(bytes, m.ram)) == before and not m.ram_writes
                counts['header_byte_rejections'] += 1
    for source in seeds:
        for target in seeds:
            a, b = [Q.Sonic.slim_fork(m) for m in seeds[source]]
            left = cold.cold(a, target, current_program)
            right = cold.cold(b, target, current_program)
            assert bus.headers(b) == bus.headers(seeds[target][1])
            if source != 38 and target != 38:
                cold.parity(a, b, left, right)
            else:
                assert a.rawtags == b.rawtags and a.chr_latches == b.chr_latches
                assert bytes(a[3:11]) == bytes(b[3:11])
                old_prince, new_prince = seeds[38]
                assert all(x == y or old_prince.ram[bank][at] != new_prince.ram[bank][at]
                           for bank, (u, v) in enumerate(zip(a.ram, b.ram))
                           for at, (x, y) in enumerate(zip(u, v))), (source, target)
            assert cold.invoke(b, bus.AUTH)['P'] & 1
            counts['ordered_transitions'] += 1
    return dict(counts)


def first_gap(result):
    controls = C.Route.controls
    retained = None

    def observe(env, model, labels, pad):
        nonlocal retained
        retained = env, model, labels
        return controls(env, model, labels, pad)

    with patch.object(C.Route, 'controls', observe):
        trace, cap = Prince.run_trace(result, changed=False)
    route = trace['route']
    assert route['outcome'] == 'first-gap-clear' and route['actual_fourth_cap']
    assert route['HP_debits'] == [dict(tick=312, x=846, before=5, after=4)]
    terminal = route['terminal']
    assert (terminal['epoch'], terminal['x'], terminal['y'], terminal['hp'], terminal['lives']) == (868,1175,176,4,2)
    top, = [event for event in route['events'] if event['event'].endswith(' -> fourth-cap')]
    assert (top['epoch'], top['x'], top['y'], top['support_feet']) == (660,928,112,[True,True])
    logical = [row for row in trace['rows'] if row['kind'] == 'logical']
    assert [row['tick'] for row in logical] == [622,626]
    for row in logical:
        assert (row['previous_sole'],row['previous_high'],row['foot'],row['delta'],row['baseline']) == (147,0,147,5,145)
        assert row['phase_call'] == 4 and row['offset'] == 0
    return dict(image_SHA256=result[3]['in_memory_SHA256'], full_cap=top, first_gap=terminal,
                HP_debits=route['HP_debits'], logical_support=logical), cap, retained


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ('cold', 'readback', 'owners', 'cold-vectors', 'route', 'hot-vectors'):
        parser.add_argument('--'+flag, action='store_true')
    parser.add_argument('--without-static-portrait', action='store_true')
    parser.add_argument('--sonic-scene', action='store_true')
    args = parser.parse_args()
    result = proposal(static_portrait=not args.without_static_portrait, sonic_scene=args.sonic_scene)
    _, trial, chunks, layout, program, _, _ = result
    emit('PRINCE_SONIC_COMPOSITION', {k:layout[k] for k in (
        'in_memory_SHA256','transport_parent_SHA256','portable_payload_SHA256',
        'pure_payload_changed_bytes','named_menu_entries_preserved','Prince_cookie')})
    if args.cold or args.hot_vectors:
        seed, cold = Q.actual_cold(trial, chunks, layout, program)
        emit('PRINCE_SONIC_COLD', cold)
        lifecycle, _, _ = Q.landing_and_lifecycle(trial)
        emit('PRINCE_SONIC_LIFECYCLE', dict(landing=lifecycle['replay']['terminal'],
            contacts=len(lifecycle['contact_cases']), lifecycle=lifecycle['lifecycle']))
    if args.owners:
        emit('PRINCE_SONIC_OWNERS', owners(result))
    if args.readback:
        emit('PRINCE_SONIC_READBACK', Qualify.readback(result))
    if args.cold_vectors:
        emit('PRINCE_SONIC_COLD_VECTORS', Qualify.cold_vectors(result))
    if args.route or args.hot_vectors:
        route, cap, _ = first_gap(result)
        emit('PRINCE_SONIC_ROUTE', route)
        if args.hot_vectors:
            emit('PRINCE_SONIC_HOT_VECTORS', Qualify.vectors(seed, cap))


if __name__ == '__main__':
    main()
