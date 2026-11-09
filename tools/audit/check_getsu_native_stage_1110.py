"""Qualify Getsu's actual menu and cold stage ingress in a memory-only image."""

import argparse
from collections import Counter
import json
from pathlib import Path

import check_getsu_fuma_owner_1110 as O
import check_getsu_menu_preview_1110 as Preview
from check_getsu_owner_vectors_1110 import reconstruct
from check_mega_giant_ppu_mapping_1110_v1 import ColdBus
from check_tmnt_render_oa import address


R, SHA, N = O.R, O.SHA, O.N
SOURCE = R / 'tools/reference/getsu_fuma_menu_stage_1110.s'
PREVIEW = R / 'build/getsu-atlas-ownership-1110/preview.json'
OWNER = R / 'build/getsu-fuma-owner-1110'
ART = O.Page.ASSET
SIDE_PROOF = R / 'build/getsu-fuma-native-side-1110/proof.json'
PIN = O.PIN
FRONT = O.Page.Front
EXPECTED_NAME = 'GETSU FUMA'
SIMON_START = FRONT.START
PUB_SCENE = 0xb013
SHARED_MOVE = 0xb08c


def data(label, values):
    return label + ':\n    .byte ' + ','.join(f'${v:02x}' for v in values) + '\n'


def assemble(output, art):
    menu = SOURCE.read_text()
    reverse = bytes.fromhex('3f1103' + art['palette']['colors'])[::-1]
    menu += '\n.segment "COLORS"\n' + data('PortraitOam', bytes.fromhex(art['portrait']['oam_hex']))
    menu += data('PaletteReverse', reverse)
    for seg, label, size in (('GATE', 'GfMenuPreview', 81), ('DRAW', 'GfMenuDraw', 81),
                             ('NAME', 'GfMenuColors', 81), ('NAME_TAIL', 'GfMenuNameTail', 15)):
        # COLORS and NAME are contiguous in the link. Their combined length
        # is checked from linked labels below, with the .res in the linker.
        if seg != 'NAME':
            menu += f'\n.segment "{seg}"\n.res {size}-(*-{label}),$ea\n'
    menu += '\n.segment "NAME"\n.export GfMenuNameEnd\nGfMenuNameEnd:\n'
    layout = (('P', 0xaf32, 81, ('GATE',)), ('D', 0xafd4, 81, ('DRAW',)),
              ('C', 0xb076, 81, ('COLORS', 'NAME')), ('T', 0xb1fc, 15, ('NAME_TAIL',)))
    blob, labels = O.assemble(output, menu, layout)
    color_extent = labels['GfMenuNameEnd'] - 0xb076
    assert len(blob) == 81 + 81 + color_extent + 15 and color_extent <= 81
    return (blob[:81], blob[81:162], blob[162:162 + color_extent].ljust(81, b'\xea'), blob[-15:]), labels


def compose(menu, labels, renderer=None):
    stock = O.Page.bundle()
    b, old, _, body = reconstruct(OWNER)
    art = O.Page.load_json(ART)
    preview = O.Page.load_json(PREVIEW)
    assert preview['passed'] and preview['parent_SHA256'] == PIN
    assert preview['bindings'][ART.relative_to(R).as_posix()] == SHA(ART.read_bytes())
    assert O.Page.load_json(SIDE_PROOF)['passed']
    raw = bytearray(b['raw'])
    rows = []

    def patch(bank, pc, before, after):
        at = FRONT.off(bank, pc)
        assert len(before) == len(after) and raw[at:at + len(before)] == before, (bank, hex(pc))
        raw[at:at + len(after)] = after
        rows.append(dict(physical_PRG=bank, CPU_half_open=[pc, pc + len(before)], file_offset=at,
                         old_hex=before.hex(), new_hex=after.hex()))

    for pc, data_blob in zip((0xaf32, 0xafd4, 0xb076, 0xb1fc), menu, strict=True):
        patch(91, pc, b'\xea' * len(data_blob), data_blob)
    patch(66, 0xaad5, Preview.far(0xb979, 76, jsr=True), Preview.far(labels['GfMenuPreview'], 91))
    patch(66, 0xacc0, Preview.far(0xb720, 79), Preview.far(labels['GfMenuName'], 91))
    patch(66, 0xa975, bytes.fromhex('ade75f18690129038de75fad09734c14aa'), FRONT.CYCLE)
    patch(29, 0xb97c, bytes.fromhex('4c6fb4') + b'\xea' * 20, SIMON_START)
    patch(65, 0xb01c, b'\x05', b'\x06')  # Existing forced-blank scene gate.
    patch(65, 0xa751, b'\x05', b'\x06')  # Existing full-header public route.

    # This stage-only layout stays compatible with the independent renderer.
    # The route still checks both exact headers before every loaded vector.
    code = bytearray(body)
    addr = old['kernel_labels']
    target_rows = {0: addr['GfHostMove'], 14: 0x958b, 15: addr['GfHostReset'], 36: addr['GfHostReset']}
    if renderer is not None:
        chunk, draw_label = renderer
        start = old['kernel_bytes']
        assert 0xa000 + start <= draw_label < 0xa000 + start + len(chunk) <= 0xa800
        assert code[start:start + len(chunk)] == b'\xff' * len(chunk)
        code[start:start + len(chunk)] = chunk
        target_rows[2] = draw_label
    for index in range(38):
        target = target_rows.get(index)
        i = index * 3
        assert code[i:i + 3] == b'\xff' * 3
        code[i:i + 3] = b'\x18\x60\xea' if target is None else b'\x4c' + target.to_bytes(2, 'little')
    atlas = (ART.parent / 'atlas.chr').read_bytes()
    assert SHA(atlas) == art['outputs']['atlas.chr']
    art_at = O.Page.CHR + 990 * 1024
    assert SHA(raw[art_at:art_at + 1024]) == 'e2817e9757bbffbfe0cc350f05d694effd065501ea140caa25b450b4ad819fa3'
    raw[art_at:art_at + 1024] = atlas
    for i, page in enumerate(old['code_pages']):
        at = page['file_offset']
        assert raw[at:at + 1024] == body[i * 1024:(i + 1) * 1024]
        raw[at:at + 1024] = code[i * 1024:(i + 1) * 1024]
    cookie = bytes((0xa7, 42, 1)) + bytes.fromhex(SHA(bytes(code) + atlas))[:13]
    patch(65, 0xab81, bytes.fromhex(old['cookie']), cookie)
    return stock, dict(b, raw=bytes(raw)), rows, bytes(code), cookie, target_rows


def frame(m, pad, watch):
    N.put(m, SavedJoypadBits=pad, SavedJoypad1Bits=pad, SavedJoypad2Bits=0, NmiDisable=255)
    FRONT.F.invoke(m, 'GameLoop', watch=watch)
    N.consume(m)


def word_position(m):
    return (m[address(m.bundle, 'Player_PageLoc')] << 8) | m[address(m.bundle, 'Player_X_Position')]


def cold_stage(b, code, cookie, targets, confirm):
    m = ColdBus(b)
    c = O.NesMPU(memory=m, pc=None)
    c.reset()
    for _ in range(300000):
        if c.pc == address(b, 'IdleLoop'):
            break
        assert m[c.pc], ('reset BRK', hex(c.pc))
        c.step()
    else:
        raise AssertionError('No native IdleLoop')
    m.vblank_at_boot = False
    hits = Counter()
    sites = {(193, PUB_SCENE): 'scene', (193, O.COLD): 'cold', (193, O.AUTH): 'auth',
             (193, 0xb0f8): 'scene36', (193, SHARED_MOVE): 'move0', (157, 0xb97c): 'start_retire',
             (3, targets[0]): 'loaded_move', (3, targets[36]): 'loaded_reset'}

    def watch(q):
        if q.pc >= 0x8000:
            bank = m.rawtags[(q.pc - 0x8000) // 8192]
            key = sites.get((bank, q.pc))
            if key:
                hits[key] += 1
                if key.startswith('loaded'):
                    assert O.headers(m) == (cookie, cookie)

    for title in range(120):
        if m[0x7307] == 2:
            break
        frame(m, 16 if title == 40 else 0, watch)
    else:
        raise AssertionError('No native menu')
    for i in range(1, 6):
        frame(m, 0, watch)
        frame(m, 1, watch)
        assert m[0x7309] == i, (i, m[0x7309])
    for i in range(1, 5):
        frame(m, 0, watch)
        frame(m, 32, watch)
        assert (m[0x7309], m[0x6002], m[0x5fe7]) == (5, 5, i)
    assert m.chr_latches[0] == 990
    packet = bytes(m.vram[0x2328:0x2338])
    name = ''.join(chr(55 + n) if 10 <= n <= 35 else ' ' if n == 36 else '?' for n in packet)
    assert name.strip() == EXPECTED_NAME and '?' not in name, (name, packet.hex())
    frame(m, 0, watch)
    frame(m, confirm, watch)
    assert m[0x6002] == 42, ('confirmation identity', confirm, m[0x6002], m[0x7307], dict(hits))
    for stage in range(600):
        if tuple(N.get(m, k) for k in ('OperMode', 'OperMode_Task', 'GameEngineSubroutine')) == (1, 3, 8):
            break
        frame(m, 0, watch)
    else:
        raise AssertionError(('No active stage', m[0x6002], N.get(m, 'OperMode_Task'), dict(hits)))
    assert O.headers(m) == (cookie, cookie) and bytes(m.ram[3][:2048]) == code
    assert N.get(m, 'WorldNumber') == N.get(m, 'LevelNumber') == 0
    assert all(hits[k] for k in ('start_retire', 'scene', 'cold', 'auth', 'scene36', 'loaded_reset')), hits
    start = word_position(m)
    for _ in range(28):
        frame(m, 1, watch)
    finish = word_position(m)
    assert hits['move0'] and hits['loaded_move'] and finish > start, (hits, start, finish)
    assert N.get(m, 'NumberofLives') == 2
    return dict(confirm=confirm, menu_name=name, raw=42, title_updates=title, stage_updates=stage,
                native_X=[start, finish], loads=dict(hits), header=O.headers(m)[0].hex())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(R / 'build')
    out.mkdir(exist_ok=True)
    menu, labels = assemble(out, O.Page.load_json(ART))
    base, trial, rows, code, cookie, targets = compose(menu, labels)
    print(json.dumps(dict(menu_labels=labels, cookie=cookie.hex(), targets=targets)), flush=True)
    confirmations = [cold_stage(trial, code, cookie, targets, key) for key in (16, 128)]
    result = dict(passed=True, ROM_written=False, parent_SHA256=PIN,
                  expected_memory_only_SHA256=SHA(trial['raw']), stage_component_only=True,
                  owner_parent_SHA256=SHA((OWNER / 'proof.json').read_bytes()), renderer_installed=False,
                  patch_PRG=rows, kernel_SHA256=SHA(code), cookie=cookie.hex(), public_vector_rows=targets,
                  menu_labels=labels, confirmations=confirmations,
                  limits=['No Mesen, final renderer, service IRQ or nightly admission.'],
                  bindings={p.relative_to(R).as_posix(): SHA(p.read_bytes()) for p in
                            (Path(__file__), SOURCE, PREVIEW, ART, SIDE_PROOF, OWNER / 'proof.json')})
    (out / 'proof.json').write_text(json.dumps(result, indent=2) + '\n')
    (out / 'kernel.bin').write_bytes(code)
    print(json.dumps(dict(passed=True, confirmations=confirmations)))


if __name__ == '__main__':
    main()
