"""Link and test Getsu's menu-only preview on the exact c8 image in memory."""

import argparse
import itertools
import json
from pathlib import Path
import subprocess
import tempfile

import check_getsu_atlas_page_1110 as Page
from check_tmnt_render_oa import address, location
from verify_native_relocation import NesMPU


R, ROM, PIN, SHA = Page.R, Page.ROM, Page.PIN, Page.SHA
SOURCE = R / 'tools/reference/getsu_fuma_menu_preview_1110.s'
ART_SOURCE = Page.SOURCE / 'src/smb3_mario_art.inc'
RUN, PUT, FORK = Page.Front.F.invoke, Page.Front.N.put, Page.Front.N.fork
BANK = 91
STARTS = (0xaf32, 0xafd4, 0xb076)
SEGS = ('GATE', 'DRAW', 'COLORS')
STOP = 0x5b00


def far(target, bank, jsr=False):
    return bytes((0x8d, 0x6a, 1, 0xa9, target & 255, 0x8d, 0x6c, 1, 0xa9, target >> 8,
                  0x8d, 0x6d, 1, 0xa9, bank | 128, 0x20 if jsr else 0x4c, 0x5a, 1))


def assemble(output, portrait, palette):
    def data(name, values):
        return name + ':\n    .byte ' + ','.join(f'${v:02x}' for v in values) + '\n'

    with tempfile.TemporaryDirectory(prefix='asm-', dir=output) as folder:
        temp = Path(folder)
        src, cfg, obj, binary = (temp / ('preview.' + ext) for ext in ('s', 'cfg', 'o', 'bin'))
        source = SOURCE.read_text() + '\n' + data('PortraitOam', portrait) + data('PaletteCommand', palette)
        src.write_text(source)
        cfg.write_text('MEMORY {\n' + ''.join(f'  {seg}: start=${pc:04x},size=81,file=%O,fill=yes,fillval=$ea;\n'
                                             for seg, pc in zip(SEGS, STARTS, strict=True)) +
                       '}\nSEGMENTS {\n' + ''.join(f'  {seg}: load={seg},type=ro;\n' for seg in SEGS) + '}\n')
        cc = R / 'tools/Windows/cc65/bin'
        subprocess.run([cc / 'ca65.exe', src, '-o', obj], check=True)
        subprocess.run([cc / 'ld65.exe', '-C', cfg, obj, '-o', binary], check=True)
        result = binary.read_bytes()
        assert len(result) == 81 * len(SEGS)
        return result


def make_images(b, payload, atlas):
    raw = b['raw']
    result, patches = bytearray(raw), []

    def patch(bank, pc, old, new):
        at = Page.Front.off(bank, pc)
        assert len(old) == len(new) and result[at:at + len(old)] == old
        result[at:at + len(new)] = new
        patches.append(dict(physical_PRG=bank, CPU_half_open=[pc, pc + len(old)], file_offset=at,
                            old_hex=old.hex(), new_hex=new.hex()))

    for index, (pc, form) in enumerate(zip(STARTS, (2, 3, 4), strict=True)):
        name = f'M3Form{form}ChrLo'
        assert address(b, name) == pc + 0x2000 and location(b, name) == Page.Front.off(BANK, pc)
        assert f'{name}:\n .res 81,$ea' in ART_SOURCE.read_text()
        patch(BANK, pc, bytes([0xea]) * 81, payload[81 * index:81 * (index + 1)])
    assert address(b, 'DrawSelectionPreview') == 0xaad5
    patch(66, 0xaad5, far(0xb979, 76, jsr=True), far(STARTS[0], BANK))
    at = Page.CHR + Page.PAGE * 1024
    assert SHA(raw[at:at + 1024]) == 'e2817e9757bbffbfe0cc350f05d694effd065501ea140caa25b450b4ad819fa3'
    result[at:at + 1024] = atlas
    isolated = dict(b, raw=bytes(result))
    # Exercise a real fifth Select edge in a distinct CPU fixture. Do not
    # bundle that proposal with the portrait writes or activate confirmation.
    cycle = Page.Front.off(66, 0xa975)
    expected = bytes.fromhex('ade75f18690129038de75fad09734c14aa')
    assert result[cycle:cycle + 17] == expected
    result[cycle:cycle + 17] = Page.Front.CYCLE
    return isolated, dict(b, raw=bytes(result)), patches


def rebind(m, b):
    m.bundle = b
    for window, mapping in enumerate(m.rawtags):
        m.raw_page(window, mapping)
    return m


def snapshot(m):
    # Stack past the live cursor and transient A-bank map traffic belong to
    # the extra call frame. All application memory including SMC must match.
    return (bytes(m[0:0x180]), bytes(m[0x200:0x800]), bytes(m[0x5c00:0x8000]),
            tuple(bytes(bank) for bank in m.ram), tuple(m.rawtags), tuple(m.ppu_log),
            tuple(m.chr_latches), m.ppuctrl, m.ppu_reads, m.protection,
            [(at, val) for at, val in m.writes if not (0x15a <= at < 0x200 or at in (0x145, 0x5115))])


def compare_foreign(a, b):
    a.writes.clear()
    b.writes.clear()
    registers_a, registers_b = RUN(a, 'DrawSelectionPreview'), RUN(b, 'DrawSelectionPreview')
    assert {k: v for k, v in registers_a.items() if k != 'minimum_SP'} == {
        k: v for k, v in registers_b.items() if k != 'minimum_SP'}, (registers_a, registers_b)
    before, after = snapshot(a), snapshot(b)
    assert before == after, (a[0x7309], a[0x5fe7],
                             [(i, next(((j, x, y) for j, (x, y) in enumerate(zip(old, new)) if x != y),
                                       (len(old), len(new))) if isinstance(old, (bytes, list, tuple)) else (old, new))
                              for i, (old, new) in enumerate(zip(before, after, strict=True)) if old != new])
    return registers_a['minimum_SP'], registers_b['minimum_SP']


def seed(b, slot):
    m = Page.Front.N.fresh(b)
    PUT(m, CrossoverMenuIndex=slot, CmActive=0)
    m[0x5ffe] = 0
    RUN(m, 'MenuResolveCharacter')
    RUN(m, 'QueueSelection')
    return m


def key(m, buttons):
    PUT(m, VRAM_Buffer1_Offset=0, CrossoverMenuButtons=0, SavedJoypad1Bits=buttons, SavedJoypad2Bits=0)
    RUN(m, 'CrossoverMenuInput')


def foreign(b, trial):
    count, minima = 0, [224, 224]
    for slot in range(32):
        m = seed(b, slot)
        seen = set()
        for _ in range(32):
            _, cells = Page.menu_name(m)
            sig = (m[0x6002], tuple(cells), bytes(m[0x5fe0:0x5fff]), m[0x730a])
            if sig in seen:
                break
            seen.add(sig)
            for cursor in (0, 77):
                a = FORK(m)
                PUT(a, VRAM_Buffer1_Offset=cursor)
                z = rebind(FORK(a), trial)
                results = compare_foreign(a, z)
                minima = [min(old, new) for old, new in zip(minima, results, strict=True)]
                count += 1
            key(m, 32)
        else:
            raise AssertionError(('Select bound', slot))
    assert count == 200
    return dict(cases=count, before_minimum_SP=minima[0], after_minimum_SP=minima[1])


def check_positive(b, original, portrait, palette):
    m = seed(b, 5)
    for i in range(1, 5):
        key(m, 32)
        assert (m[0x7309], m[0x5fe7], m[0x6002], m[0x7307]) == (5, i, 5, 2), (i, m[0x5fe7])
    assert bytes(m[0x200:0x214]) == portrait

    seen = 0
    for cursor in (0, 16, 77, 78, 79, 83):
        n = FORK(m)
        PUT(n, VRAM_Buffer1_Offset=cursor)
        n.writes.clear()
        RUN(n, 'DrawSelectionPreview')
        assert bytes(n[0x200:0x214]) == portrait
        assert all(n[0x200 + i * 4] >= 240 for i in range(5, 64))
        assert n[0x06de] == 20
        assert (n[0x147], n[0x73e0], n[0x73ee], n[0x146]) == (222, 131, 1, 1)
        if cursor < 78:
            assert bytes(n[0x4af + cursor:0x4af + cursor + 7]) == palette + b'\0'
            assert n[0x4ae] == cursor + 6
        else:
            assert n[0x4ae] == cursor and not any(0x4af <= at < 0x503 for at, _ in n.writes)
        RUN(n, 'X5PublishChr')
        assert n.chr_latches[0] == Page.PAGE
        seen += 1

    # A real next Select goes back to Simon. Native queue setup clears the
    # direct-mode state and replaces the hardware window before display.
    key(m, 32)
    RUN(m, 'X5PublishChr')
    assert (m[0x7309], m[0x5fe7], m[0x6002]) == (5, 0, 5)
    assert Page.PAGE not in m.chr_latches and not m[0x73e0] & 0x80

    # A stale variant in any of the three other required guard fields must
    # follow the complete foreign path. Test actual Mini + its menu family.
    rejects = 0
    for slot, raw, state, busy in ((0, 41, 2, 255), (5, 41, 2, 255),
                                   (5, 5, 1, 255), (5, 5, 2, 0)):
        a = seed(original, slot)
        PUT(a, SelectedCharacter=raw, Cv3Variant=4, CrossoverMenuState=state, NmiDisable=busy)
        z = rebind(FORK(a), b)
        compare_foreign(a, z)
        rejects += 1
    return dict(actual_Select_edges=5, palette_cursors=seen, off_gate_exact=rejects, raw42_writes=0)


def check_lag_cuts(b, portrait):
    seed_bus = seed(b, 5)
    for _ in range(4):
        key(seed_bus, 32)
    PUT(seed_bus, VRAM_Buffer1_Offset=0, NmiDisable=255, FamilyMainCommit=1)
    seed_bus.chr_latches[0] = 524  # Old hardware stays visible until the following normal publish.
    target = address(b, 'DrawSelectionPreview')
    audio = address(b, 'AudioUpdate')
    cuts, depth = 0, 224

    def cpu(m):
        m.raw_page(1, 194)
        PUT(m, CurrentBank=194)
        c = NesMPU(memory=m, pc=target)
        c.a, c.x, c.y, c.p, c.sp = 85, 7, 91, 0x31, 224
        c.stPushWord(STOP - 1)
        return c

    def step(c):
        assert c.memory[c.pc], ('linked BRK', hex(c.pc), c.memory.rawtags)
        c.step()

    for cut in range(1200):
        m = FORK(seed_bus)
        c = cpu(m)
        for _ in range(cut):
            if c.pc == STOP:
                break
            step(c)
        if c.pc == STOP:
            break
        old = (c.pc, c.a, c.x, c.y, c.p & 0xcf, c.sp)
        maps = tuple(m.rawtags)
        slots = tuple(m.chr_latches)
        m.writes.clear()
        c.nmi()
        for _ in range(1500):
            depth = min(depth, c.sp)
            if c.pc == old[0] and c.sp == old[5]:
                break
            if c.pc == audio:
                c.pc = (c.stPopWord() + 1) & 0xffff  # Same explicit audio child port as prior CHR proof.
            else:
                step(c)
        else:
            raise AssertionError(('lag NMI bound', cut, hex(c.pc)))
        assert (c.pc, c.a, c.x, c.y, c.p & 0xcf, c.sp) == old
        assert tuple(m.chr_latches) == slots and not any(0x5120 <= at <= 0x512b for at, _ in m.writes)
        if tuple(m.rawtags) != maps:
            assert c.pc in (0x166, 0x175) and m.rawtags[1] == c.a == m[0x145]
            assert m.rawtags[0] == maps[0] and tuple(m.rawtags[2:]) == maps[2:]
        for _ in range(1200):
            if c.pc == STOP:
                break
            step(c)
        else:
            raise AssertionError(('preview resume bound', cut, hex(c.pc)))
        assert bytes(m[0x200:0x214]) == portrait and m[0x6de] == 20 and c.sp == 224
        RUN(m, 'X5PublishChr')
        assert m.chr_latches[0] == Page.PAGE
        cuts += 1
    assert cuts > 100 and depth > 0x7a
    return dict(actual_FF_NMI_cuts=cuts, minimum_SP=depth, audio_child='existing explicit return port')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(R / 'build')
    page_proof = output / 'atlas-page.json'
    page = Page.load_json(page_proof)
    art = Page.load_json(Page.ASSET)
    assert page['passed'] and page['page'] == Page.PAGE and page['current_SHA256'] == PIN
    atlas = (Page.ASSET.parent / 'atlas.chr').read_bytes()
    assert SHA(atlas) == page['replacement_atlas_SHA256']
    portrait = bytes.fromhex(art['portrait']['oam_hex'])
    palette = bytes.fromhex('3f1103' + art['palette']['colors'])
    payload = assemble(output, portrait, palette)
    b = Page.bundle()
    trial, cycle_fixture, patches = make_images(b, payload, atlas)
    exact = foreign(b, trial)
    positive = check_positive(cycle_fixture, b, portrait, palette)
    lag = check_lag_cuts(cycle_fixture, portrait)
    (output / 'preview.bin').write_bytes(payload)
    receipt = dict(passed=True, source_proposal_only=True, ROM_written=False, parent_SHA256=PIN,
                   preview_only_memory_SHA256=SHA(trial['raw']), patches=patches,
                   atlas=dict(page=Page.PAGE, SHA256=SHA(atlas)), foreign=exact, positive=positive, lag=lag,
                   scope='Private preview only. No Select or confirmation writes proposed here. Existing names remain unchanged.',
                   bindings={p.relative_to(R).as_posix(): SHA(p.read_bytes()) for p in (
                       Path(__file__), SOURCE, ROM, page_proof, Page.ASSET, ART_SOURCE, output / 'preview.bin')})
    (output / 'preview.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(passed=True, foreign=exact, positive=positive, lag=lag)))


if __name__ == '__main__':
    main()
