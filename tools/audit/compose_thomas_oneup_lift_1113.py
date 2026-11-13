"""Compose Thomas's eighth native lift and qualify finite placement/ABI/ISR cases."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from unittest.mock import patch

import check_thomas_star_route_1113 as Current
import compose_thomas_flower_lift_1112 as Flower


R, N, W, Cam = Flower.R, Flower.N, Flower.W, Flower.Cam
SOURCE = R/'tools/reference/thomas_oneup_lift_1113.s'
LEFT = 1008
EXISTING = (*Flower.ORIGINAL, Flower.LEFT)
PIN = '65ee94ca9ac6e1b5ad44303d08f76ecbc175a88232c82ef8c32712edf150a643'
OLD_COOKIE = bytes.fromhex('a70a400363ab8235a65b66179dbc3647')


def prior_layout():
    symbols = W.Symbols.bundle()
    names = ('ScreenLeft_X_Pos', 'ScreenLeft_PageLoc', 'R0', 'Enemy_X_Position', 'Enemy_PageLoc')
    fields = {name: W.address(symbols, name) for name in names}
    fields.update(ThomasLiftMark=0xb34a, ThomasLiftNext=0xb353)
    declarations = ''.join(f'{name}=${value:04x}\n' for name, value in fields.items())
    old_spec = {name: (pc, len(body)) for name, (pc, body) in Flower.SPANS.items()}
    original = Flower.Asm.assemble(declarations+Flower.SOURCE.read_text(encoding='ascii'), old_spec)['images']
    return declarations, old_spec, original


def proposal(raw):
    assert sha256(raw).hexdigest() == Current.CURRENT
    Current.authenticate(raw)
    old = raw[Flower.START:Flower.START+6144]
    tail = Cam.TH_KERNEL.read_bytes()[6144:]
    state = Cam.TH_STATE.read_bytes()
    old_cookie = raw[Flower.COOKIE:Flower.COOKIE+16]
    assert old_cookie == OLD_COOKIE == bytes.fromhex('a70a4003')+sha256(old+tail+state).digest()[:12]
    assert raw[Flower.START+6144:Flower.START+8192] == state[4096:6144]
    declarations, old_spec, original = prior_layout()
    specs = dict(old_spec)
    specs['LIFT_TABLE'] = (Flower.TABLE, 24)
    linked = Flower.Asm.assemble(declarations+SOURCE.read_text(encoding='ascii'), specs)['images']
    # Three more table bytes come from the same retired lab query tail.
    # The prior flower source already authenticates its complete 59-byte tail.
    assert old[Flower.TABLE-0xa000+21:Flower.TABLE-0xa000+24] == bytes.fromhex('0320a0')
    for offset in range(len(old)-2):
        if old[offset] in (0x20, 0x4c):
            assert not Flower.TABLE <= int.from_bytes(old[offset+1:offset+3], 'little') < 0xb60d
    kernel, edits = bytearray(old), []
    for name, (pc, width) in specs.items():
        prior = original[name]+(bytes.fromhex('0320a0') if name == 'LIFT_TABLE' else b'')
        body = linked[name]
        offset = pc-0xa000
        assert len(prior) == len(body) == width and old[offset:offset+width] == prior, name
        kernel[offset:offset+width] = body
        edits.append((Flower.START+offset, prior, body))
    cookie = bytes.fromhex('a70a4004')+sha256(bytes(kernel)+tail+state).digest()[:12]
    image = bytearray(raw)
    image[Flower.START:Flower.START+6144] = kernel
    image[Flower.COOKIE:Flower.COOKIE+16] = cookie
    edits.append((Flower.COOKIE, old_cookie, cookie))
    return bytes(image), dict(edits=edits, kernel=bytes(kernel), cookie=cookie,
                             source_SHA256=sha256(SOURCE.read_bytes()).hexdigest())


def inverse(image):
    assert sha256(image).hexdigest() == PIN
    _, specs, original = prior_layout()
    raw = bytearray(image)
    for name, (pc, _) in specs.items():
        prior = original[name]+(bytes.fromhex('0320a0') if name == 'LIFT_TABLE' else b'')
        at = Flower.START+pc-0xa000
        raw[at:at+len(prior)] = prior
    raw[Flower.COOKIE:Flower.COOKIE+16] = OLD_COOKIE
    parent = bytes(raw)
    assert sha256(parent).hexdigest() == Current.CURRENT
    assert proposal(parent)[0] == image
    return parent


def matrix(before, after):
    counts = Counter()
    seeds = Flower.manager(before), Flower.manager(after)
    for index, left in enumerate((*EXISTING, LEFT)):
        for relative, occupied in product((255, 256, 270, 287, 288, 320), (0, 5, 6)):
            results = []
            for which in ((0, 1) if index < 7 else (1,)):
                model = Flower.Cclone(seeds[which])
                model.ram[2][0x838] = (255 if which else 127) ^ (1 << index)
                Cam.fill_actors(model, occupied)
                Cam.geometry(model, left-relative, left-20)
                Cam.call(model, Cam.TH_TICK)
                expected = 256 <= relative <= 287 and occupied < 6
                assert Cam.lift_slots(model) == ({5: (left, 192, 0)} if expected else {})
                assert bool(model.ram[2][0x838] & (1 << index)) == (expected or relative < 256)
                assert N.get(model, 'ObjectOffset') == 4
                results.append((Cam.lift_slots(model), [Flower.Thomas.actor(model, slot) for slot in range(6)]))
                if index == 7 and expected:
                    Cam.platform_carries(model, 5, LEFT)
                    counts['new_native_carry'] += 1
            if len(results) == 2:
                assert results[0] == results[1], (index, relative, occupied)
                counts['existing_placement_pairs'] += 1
            else:
                counts['new_camera_and_pressure_cases'] += 1
    for world, level, area, timer in ((1, 0, 5, 0), (0, 1, 5, 0), (0, 0, 4, 0), (0, 0, 5, 255)):
        model = Flower.manager(after)
        Cam.geometry(model, LEFT-287, LEFT-20)
        N.put(model, WorldNumber=world, LevelNumber=level, AreaAddrsLOffset=area, TimerControl=timer)
        Cam.call(model, Cam.TH_TICK)
        assert not Cam.lift_slots(model) and model.ram[2][0x838] == 0
        counts['other_stage_or_frozen_reject'] += 1
    return dict(counts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--section', choices=('compose', 'cpu', 'all'), default='all')
    args = parser.parse_args()
    raw = Current.ROM.read_bytes()
    image, info = proposal(raw)
    assert inverse(image) == raw
    result = dict(candidate_SHA256=sha256(image).hexdigest(), source_SHA256=info['source_SHA256'],
                  cookie=info['cookie'].hex(), output_files=0)
    if args.section != 'compose':
        _, before = Flower.Thomas.cold(raw, expected=Current.CURRENT,
                                      kernel=raw[Flower.START:Flower.START+6144],
                                      cookie=raw[Flower.COOKIE:Flower.COOKIE+16])
        _, after = Flower.Thomas.cold(image, expected=result['candidate_SHA256'], kernel=info['kernel'], cookie=info['cookie'])
        result['matrix'] = matrix(before, after)
        result['foreign'] = Flower.foreign(before, after)
        with patch.object(Flower, 'LEFT', LEFT):
            result['interrupts'] = Flower.vectors(after)
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
