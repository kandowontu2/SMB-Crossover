"""Link Laserbot's live held-B cycle, actor, and original CHR cells."""

import argparse
import json

import check_steve_shatterhand_companion_live_1111 as Live
import check_steve_shatterhand_laser_art_1111 as Art
import check_steve_shatterhand_laserbot_1111 as Core


BRIDGE = Live.H.ROOT / 'tools/reference/steve_shatterhand_laserbot_live_1111.s'
ORIGIN, STATE, END = 0xd000, 0xd780, 0xd800
QUALIFIED = '7fcf58df189d70586e46ecc0fcbf7fc219d3c09dba25da383d4e91ccc8fb4973'


def fields(shared):
    sizes = {name: len(addrs) for name, addrs in (Core.SCALARS | Core.ARRAYS).items()
             if name not in shared} | Core.SCRATCH
    sizes.update(SteveLaserDrawTags=8, SteveLaserDrawSlot=1, SteveLaserMeta=9)
    result, at = {'SteveLaserActive': shared['SteveBotDrawPhase']+1}, STATE
    for name, width in sizes.items():
        result[name] = at
        at += width
    assert at <= END, (hex(at), hex(END))
    return result


def proposal(raw):
    import check_steve_shatterhand_late_companion_transport_1111 as Late

    if Live.C.digest(raw) == QUALIFIED:
        from deliver_steve_laserbot_1111 import recover_parent

        raw = recover_parent(raw)
    base, prior = Live.on_nightly(raw)
    staged, linked = Live.on_nightly(raw, laser=True)
    old_cookie, intermediate_cookie = prior['cookie'], linked['cookie']
    assert base.count(old_cookie) == staged.count(intermediate_cookie) == 2
    staged = staged.replace(intermediate_cookie, old_cookie)
    edits, start = [], None
    for at, (before, after) in enumerate(zip(base, staged, strict=True)):
        if before != after:
            if start is None:
                start = at
        elif start is not None:
            edits.append((start, base[start:at], staged[start:at]))
            start = None
    assert start is None
    candidate, info = Late.mount(base, prior, linked['laser_payload'], extra_edits=edits)
    assert Art.apply(candidate, ((at, new, old) for at, old, new in info['late_edits'])) == base
    return candidate, linked | {name: info[name] for name in ('cookie', 'cold', 'late_stage', 'late_edits')}


def exercise(candidate, info):
    m, route, earned = Live.earn_laser(candidate, info)
    linked = info['companion_fields'] | info['laser_fields']

    def value(name, slot=0):
        return Live.resident(m, linked['SteveLaser'+name]+slot)

    def position(x, y):
        return Live.native_position(m, linked, x, y)

    def body(crouched=False):
        x, y = position('SteveBotX', 'SteveBotY')
        facing = Live.resident(m, linked['SteveBotFacing'])
        tile = 0x3d if crouched else 0x39
        assert 8 <= x < 248 and 8 <= y < 240
        expected = {(y-8, tile, 0x41 if facing else 1, x if facing else x-8),
                    (y-8, tile+2, 0x41 if facing else 1, x-8 if facing else x)}
        assert expected <= Live.sprites(m, (tile, tile+2)), (expected, Live.sprites(m, (tile, tile+2)))
        assert tuple(m.chr_latches[4:6]) == Art.HOST_PAGES

    frame = route['frame']
    assert value('Active') == 1
    body()
    contacts = Live.native_contact(m, info, laser=True)
    checked = set()
    cooldown = False
    for tick in range(84):
        frame(64)
        assert value('Active') == 1, tick
        if tick == 0:
            assert value('Charge') == 16
        cooldown |= value('Cooldown') == 64
        checked.update(sprite[1] for sprite in Live.sprites(m, (0x41, 0x7b, 0x7d, 0x7f)))
    assert {0x41, 0x7b, 0x7d} <= checked and cooldown, (checked, cooldown)
    frame(2)
    frame(4)
    body(crouched=True)
    assert Live.resident(m, linked['SteveBotFacing']) == 128
    crouched_pairs = 0
    for _ in range(84):
        frame(4 | 64)
        cells = Live.sprites(m, (0x7f,))
        crouched_pairs += {0x41, 0x81} <= {cell[2] for cell in cells}
    assert crouched_pairs > 0
    return dict(earned=earned, standing_attack_tiles=sorted(checked), held_b_updates=168,
                crouched_left_pairs=crouched_pairs, native_contact_checks=contacts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--first-regression', action='store_true')
    args = parser.parse_args()
    nightly = Live.DONOR.HOST.read_bytes()
    candidate, info = proposal(nightly)
    if args.first_regression:
        model, result = Live.natural(candidate, info)
        result['native_contact_checks'] = Live.native_contact(model, info)
    else:
        result = exercise(candidate, info)
    print(json.dumps(dict(passed=True, candidate=Live.C.digest(candidate), bridge_bytes=len(info['laser_payload']),
                          companion_host_bytes=info['live_bytes'], output_files=0, **result)), flush=True)


if __name__ == '__main__':
    main()
