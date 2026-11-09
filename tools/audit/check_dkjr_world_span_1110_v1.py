"""Reconstruct DK Jr's signed source window in native world columns."""
from collections import Counter
from itertools import product
from pathlib import Path
import json
import subprocess

import prepare_dkjr_current_route_1110_v1 as R
from check_mini_funded_actor_1108_v3 import run, slim_fork, registers, live_stack

I, N = R.I, R.I.N
OUT = R.R / 'build/dkjr-world-span-1110'
SOURCE = R.R / 'tools/reference/dkjr_world_span_1110_v1.s'
WALL = R.OUT / 'wall-profile.json'
CHR = 1048592
LEFT, RIGHT = 0xd240, 0xd2d5


def link():
    OUT.mkdir(exist_ok=True)
    cfg, obj, binary, labels = (OUT / ('span.' + x) for x in ['cfg', 'o', 'bin', 'lbl'])
    cfg.write_text('MEMORY{L:start=$D240,size=$1E,file=%O;R:start=$D2D5,size=$2B,file=%O;}'
                   'SEGMENTS{LEFT:load=L,type=ro;RIGHT:load=R,type=ro;}\n')
    cc = R.R / 'tools/Windows/cc65/bin'
    subprocess.run([cc / 'ca65.exe', SOURCE, '-o', obj], check=True)
    subprocess.run([cc / 'ld65.exe', '-C', cfg, obj, '-o', binary, '-Ln', labels], check=True)
    obj.unlink()
    sym = {line.split()[2][1:]: int(line.split()[1], 16) for line in labels.read_text().splitlines()}
    first = sym['DkWorldStartPageEnd'] - LEFT
    second = sym['DkWorldEndPageEnd'] - RIGHT
    data = binary.read_bytes()
    assert (sym['DkWorldStartPage'], sym['DkWorldEndPage']) == (LEFT, RIGHT)
    assert first + second == len(data) and first <= 30 and second <= 43
    return data[:first], data[first:]


def proposal(raw, first, second, cookie):
    carrier_manifest = json.loads(R.OAM.DESCRIPTOR.read_text())
    pages = [row['physical_CHR'] for row in carrier_manifest['patches'] if 'physical_CHR' in row]
    assert pages == [817, 833, 847, 856, 867, 881, 882, 883, 959, 960, 961]
    start = lambda page: CHR + page * 1024
    payload = b''.join(raw[start(page):start(page) + 1024] for page in pages)
    assert cookie == bytes([0xa7, 40, 1]) + bytes.fromhex(I.sha(payload))[:13]
    old = bytearray(payload)
    # Both explicit FF allocations surround the immutable 119-byte constructor.
    boot = (I.BASE / 'admission-cold-v11.bin').read_bytes()
    assert len(boot) == 119
    assert old[9*1024 + 576:9*1024 + 768] == b'\xff'*30 + boot + b'\xff'*43
    assert raw[start(960):start(960) + 384] == (I.BASE / 'native-art-960-v38.chr').read_bytes()[:384]
    at = lambda pc: 9*1024 + pc - 0xd000
    old[at(LEFT):at(LEFT) + len(first)] = first
    old[at(RIGHT):at(RIGHT) + len(second)] = second
    for pc, before, after in [(0xb3a0, '8de1c8', '20d5d2'),
                              (0xb3af, 'ad1d076900', '2040d2eaea')]:
        offset = pc - 0xa000
        assert payload[offset:offset + len(bytes.fromhex(before))] == bytes.fromhex(before)
        old[offset:offset + len(bytes.fromhex(after))] = bytes.fromhex(after)
    rows = []
    for i, page in enumerate(pages):
        before, after = payload[i*1024:(i+1)*1024], old[i*1024:(i+1)*1024]
        if before != after:
            rows.append(dict(physical_CHR=page, file_offset=start(page), old_hex=before.hex(), new_hex=after.hex()))
    assert [row['physical_CHR'] for row in rows] == [867, 960]
    changed_cookie = cookie[:3] + bytes.fromhex(I.sha(old))[:13]
    rows.append(dict(physical_PRG=65, file_offset=534485, old_hex=cookie.hex(), new_hex=changed_cookie.hex()))
    after = R.OAM.compose(raw, rows)
    return after, payload, bytes(old), changed_cookie, rows


def make_seed(raw, payload):
    b = I.SYMBOLS.bundle()
    b['raw'] = raw
    m = N.fresh(b)
    m.ram[3][:] = payload[:8192]
    m.ram[2][0x1000:0x1800] = payload[9*1024:]
    m.raw_page(1, 3)
    m.raw_page(2, 2)
    N.put(m, CurrentBank=3, CurrentBankC=2, SelectedCharacter=40, OperMode=1, GameEngineSubroutine=8,
          NmiDisable=255)
    for i, name in enumerate(['Block_Buffer_1', 'Block_Buffer_2']):
        a = I.UI.address(b, name)
        m[a:a+208] = bytes(0x26 if (j+i)%5 == 0 else 0x54 for j in range(208))
    m.ram[2][0x8da] = 1
    return m


def prep(seed, camera, relative, left, right, top, bottom, kind):
    m = slim_fork(seed)
    player = (camera + relative) & 65535
    N.put(m, Player_X_Position=player & 255, Player_PageLoc=player >> 8,
          ScreenLeft_X_Pos=camera & 255, ScreenLeft_PageLoc=camera >> 8)
    m.ram[2][0x3e:0x42] = bytes([left, top, right, bottom])
    c = N.NesMPU(memory=m, pc=0xb2f2)
    c.a, c.x, c.y, c.p, c.sp = kind, 73, 127, 0x61, 224
    c.stPushWord(0x5aff)
    return c


def scan(seed, args, watch=None):
    c = prep(seed, *args)
    cells = []

    def visit(z):
        if z.pc == 0xb3b7 and z.memory.rawtags[1] == 3:
            s = z.memory.ram[2]
            cells.append((s[0x8de] + 256*s[0x8df], s[0x8e2]))
            assert len(cells) <= 9, ('Native source rectangle escaped its bounds', args, cells)
        if watch:
            watch(z)

    run(c, lambda z: z.pc == 0x5b00, visit)
    assert c.sp == 224
    return c, cells


def expected(camera, relative, left, right, top, bottom, kind):
    if left > right:
        if relative >= 128:
            right += 256
        else:
            left -= 256
    if kind == 3:
        top += 1
        bottom += 2
    if top >= 240 or bottom < 32:
        return []
    return [((camera + low) & 65535, y) for y in range(max(32, top) & ~15, (min(239, bottom) & ~15) + 1, 16)
            for low in range(((camera + left) & ~15) - camera, ((camera + right) & ~15) - camera + 1, 16)]


def region(c):
    m = c.memory
    return (registers(c, 0xef), live_stack(c), bytes(m[:0x100]), bytes(m[0x200:0x800]),
            bytes(m[0x15a:0x17b]), tuple(m.rawtags), bytes(m.ram[2][:0x900]))


def geometry(seeds):
    counts = Counter()
    depths = Counter()
    actual = {}
    for page, camera_lo, left, width, kind in product([0, 1, 255], [0, 7, 15, 200, 255],
                                                      [0, 6, 111, 224, 239, 249, 255], [0, 1, 17, 32], range(4)):
        camera = page*256 + camera_lo
        right = (left + width) & 255
        relative_list = [-2, 8, 127, 128, 231, 256, 383] if left > right else [127]
        for relative in relative_list:
            args = camera, relative, left, right, 176, 190, kind
            new, cells = scan(seeds[1], args)
            assert cells == expected(*args), (args, cells, expected(*args))
            depths[len(cells)] += 1
            if left <= right:
                old, old_cells = scan(seeds[0], args)
                assert region(old) == region(new) and old_cells == cells, args
                counts['nonwrapped_full_native_terrain_hook_parity'] += 1
            else:
                counts['wrapped_native_terrain_hook_bounds'] += 1
                if camera == 0 and relative == 231 and left == 239 and right == 0:
                    actual['right_231_camera_0'] = [list(v) for v in cells]
    for name, args in [('native_wall_433_camera_435', (435, -2, 239, 0, 176, 190, 0)),
                       ('camera_end_lock_over_255', (435, 273, 239, 0, 176, 190, 0)),
                       ('native_page_rollover', (65530, 231, 239, 0, 176, 190, 0))]:
        _, cells = scan(seeds[1], args)
        assert cells == expected(*args)
        actual[name] = [list(v) for v in cells]

    # All admitted byte windows, all camera low bytes, and both interpretations
    # of wrapped intervals. Camera high cannot change the rounded span length.
    exhaustive = 0
    for low, left, width in product(range(256), range(256), range(33)):
        right = (left + width) & 255
        for right_side in (False, True) if left > right else (False,):
            end = low + right + (256 if right_side else 0)
            begin = low + left - (256 if left > right and not right_side else 0)
            rounded_start, rounded_end = begin & ~15, end & ~15
            new_start = (rounded_start & 255) + 256*((rounded_end >> 8) - ((rounded_start & 255) > (rounded_end & 255)))
            assert new_start == rounded_start and 0 <= rounded_end - new_start <= 32
            exhaustive += 1
    return dict(cases=dict(counts), observed_columns=dict(depths), exhaustive_rounding=exhaustive, witnesses=actual)


def main():
    raw, _, cookie, _ = R.pinned_inputs()
    bug = json.loads(WALL.read_text())
    assert bug['memory_only_SHA256'] == R.PIN and bug['terminal']['maps'][1:3] == [3, 2]
    assert 'horizontal scan escapes its width bound' in bug['terminal']['error']
    first, second = link()
    after, old, new, successor_cookie, rows = proposal(raw, first, second, cookie)
    seeds = [make_seed(rom, payload) for rom, payload in [(raw, old), (after, new)]]
    scope = geometry(seeds)
    print('Signed geometry', scope, flush=True)
    ingress = I.cpu(after, successor_cookie)
    result = dict(passed=True, ROM_written=False, base_SHA256=R.PIN, memory_only_SHA256=I.sha(after),
                  patches=rows, cookie=successor_cookie.hex(), first_helper_bytes=len(first), second_helper_bytes=len(second),
                  geometry=scope, actual_cold_controls=ingress, vectors_pending=True,
                  bindings={p.relative_to(R.R).as_posix(): I.sha(p.read_bytes()) for p in
                            [Path(__file__), SOURCE, WALL, R.OUT/'rebase.json', R.OAM.DESCRIPTOR,
                             I.BASE/'admission-cold-v11.bin', I.BASE/'native-art-960-v38.chr']})
    (OUT / 'span-proof.json').write_text(json.dumps(result, indent=2) + '\n')
    print('DK Jr signed-span memory-only successor', result['memory_only_SHA256'], flush=True)


if __name__ == '__main__':
    main()
