"""Prove the current DK Jr scroll input and exact signed-terrain repack."""
from itertools import product
from pathlib import Path
import json
import subprocess

import check_dkjr_world_span_1110_v1 as V

R, I, N = V.R, V.I, V.N
OUT = R.R / 'build/dkjr-scroll-publish-1110'
SOURCE = R.R / 'tools/reference/dkjr_scroll_publish_1110_v1.s'
NATIVE = V.OUT / 'native/capture/result.json'
SPAN = V.OUT / 'span-proof.json'
VECTORS = V.OUT / 'span-vectors.json'
WORLD_START, WORLD_END = 0xb345, 0xb3b7


def link():
    OUT.mkdir(exist_ok=True)
    cfg = OUT / 'publish.cfg'
    cfg.write_text('MEMORY{C:start=$D240,size=$1E,file=%O;W:start=$B345,size=$72,file=%O;}'
                   'SEGMENTS{CAMERA:load=C,type=ro;WORLD:load=W,type=ro;}\n')
    cc = R.R / 'tools/Windows/cc65/bin'
    outputs = []
    for name in ['before', 'after']:
        obj, data, labels = (OUT / (name + ext) for ext in ['.o', '.bin', '.lbl'])
        command = [cc/'ca65.exe', SOURCE, '-o', obj]
        if name == 'before':
            command += ['-D', 'ORIGINAL']
        subprocess.run(command, check=True)
        subprocess.run([cc/'ld65.exe', '-C', cfg, obj, '-o', data, '-Ln', labels], check=True)
        obj.unlink()
        sym = {line.split()[2][1:]: int(line.split()[1], 16) for line in labels.read_text().splitlines()}
        blob = data.read_bytes()
        assert len(blob) == 30 + WORLD_END - WORLD_START and sym['DkScrollPublishEnd'] == 0xd25e
        outputs.append((blob[:30], blob[30:], sym['DkWorldRow']))
    return outputs


def build(old_world, new_world, new_helper, old_row, new_row):
    original, _, cookie, _ = R.pinned_inputs()
    span, vectors, native = (json.loads(p.read_text()) for p in [SPAN, VECTORS, NATIVE])
    raw = R.OAM.compose(original, span['patches'])
    pin = I.sha(raw)
    assert span['passed'] and vectors['passed'] and pin == span['memory_only_SHA256'] == vectors['memory_only_SHA256']
    assert native['ROM_sha256'] == pin and native['first_pipe']['scroll']['mismatches'] == 696
    assert native['first_pipe']['scroll']['last']['value'] == 96
    pages = [817, 833, 847, 856, 867, 881, 882, 883, 959, 960, 961]
    physical = lambda page: V.CHR + page * 1024
    payload = b''.join(raw[physical(p):physical(p)+1024] for p in pages)
    old_cookie = cookie[:3] + bytes.fromhex(I.sha(payload))[:13]
    assert old_cookie.hex() == span['cookie']
    after = bytearray(payload)

    def replace(at, before, value):
        assert payload[at:at + len(before)] == before and len(before) == len(value), hex(at)
        after[at:at + len(before)] = value

    replace(WORLD_START - 0xa000, old_world, new_world)
    replace(0xb49a - 0xa000, old_row.to_bytes(2, 'little'), new_row.to_bytes(2, 'little'))
    left = (V.OUT/'span.bin').read_bytes()[:span['first_helper_bytes']]
    replace(9*1024+0x240, left.ljust(30, b'\xff'), new_helper)
    # The actual successful anchor gate sets C and no intermediate op changes it.
    main_at = 10*1024 + (0xd65e - 0xd400)
    assert payload[main_at:main_at+18] == bytes.fromhex('20c1bf9042a5758dfbc8a5bd8dfcc82040d5')
    replace(main_at+15, bytes.fromhex('2040d5'), bytes.fromhex('2040d2'))
    rows = []
    for i, page in enumerate(pages):
        a, b = payload[i*1024:(i+1)*1024], after[i*1024:(i+1)*1024]
        if a != b:
            rows.append(dict(physical_CHR=page, file_offset=physical(page), old_hex=a.hex(), new_hex=b.hex()))
    assert [row['physical_CHR'] for row in rows] == [867, 881, 960, 961]
    new_cookie = old_cookie[:3] + bytes.fromhex(I.sha(after))[:13]
    rows.append(dict(physical_PRG=65, file_offset=534485, old_hex=old_cookie.hex(), new_hex=new_cookie.hex()))
    return raw, R.OAM.compose(raw, rows), payload, bytes(after), new_cookie, rows


def witness(seed):
    count = 0
    for camera, relative, p in product([0, 7, 255, 256, 435, 0xfff0],
                                       [-32768, -257, -128, -2, -1, 0, 1, 79, 80, 127, 128, 231,
                                        254, 255, 256, 273, 512, 32767], [0x21, 0x65, 0xf1]):
        m = seed
        player = (camera + relative) & 65535
        N.put(m, Player_X_Position=player & 255, Player_PageLoc=player >> 8,
              ScreenLeft_X_Pos=camera & 255, ScreenLeft_PageLoc=camera >> 8, Player_Pos_ForScroll=96)
        m.writes.clear()
        c = N.NesMPU(memory=m, pc=0xd240)
        c.a, c.x, c.y, c.p, c.sp = 176, 73, 127, p, 220
        V.run(c, lambda z: z.pc == 0xd540)
        assert (c.x, c.y, c.p & 0xef, c.sp) == (73, 127, p & 0xef, 220)
        assert N.get(m, 'Player_Pos_ForScroll') == max(0, min(255, relative)), (camera, relative, p)
        assert [(a, x) for a, x in m.writes if not 0x100 <= a <= 0x1ff] == [(0x75a, N.get(m, 'Player_Pos_ForScroll'))]
        count += 1
    return count


def main():
    (_, old_world, old_row), (camera, new_world, new_row) = link()
    raw, image, old, new, cookie, patches = build(old_world, new_world, camera, old_row, new_row)
    assert (old_row, new_row) == (0xb3a3, 0xb39d)
    seeds = [V.make_seed(rom, payload) for rom, payload in [(raw, old), (image, new)]]
    assert witness(V.slim_fork(seeds[1])) == 324
    # Exact signed geometry on the actual re-linked terrain entry.
    scope = V.geometry(seeds)
    assert scope['cases']['nonwrapped_full_native_terrain_hook_parity'] == 1200
    ingress = I.cpu(image, cookie)
    pin = I.sha(image)
    output = dict(passed=True, ROM_written=False, base_SHA256=I.sha(raw), memory_only_SHA256=pin,
                  patches=patches, cookie=cookie.hex(), direct_camera_witness_cases=324,
                  signed_geometry=scope, actual_cold_controls=ingress,
                  prior_native_scroll_mismatches=696, continuation_vectors_pending=True,
                  bindings={p.relative_to(R.R).as_posix(): I.sha(p.read_bytes()) for p in
                            [Path(__file__), SOURCE, SPAN, VECTORS, NATIVE, Path(V.__file__)]},
                  scope='Exact DK owner-only 075A publication before original source phase. Native scroll forces, thresholds, actor source and other owner bytes unchanged.')
    (OUT/'camera-proof.json').write_text(json.dumps(output, indent=2) + '\n')
    print('DK Jr scroll CPU', pin, 'patches', len(patches), 'witnesses', 324, flush=True)


if __name__ == '__main__':
    main()
