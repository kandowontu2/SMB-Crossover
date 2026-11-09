"""Bind Getsu's corrected native OAM reservation and exact foreign post tail."""

import argparse
import json
from pathlib import Path

import check_getsu_loaded_hot_1110 as H
import check_getsu_loaded_stage_1110 as L


R, S, O, N, SHA = L.R, L.S, L.O, L.N, L.SHA
RENDER = R / 'build/getsu-host-render-1110-v2'
PRIOR = H.LOAD / 'proof.json'
FIREBAR_SOURCE = R / 'src/world_firebars.s'
CALLER_SOURCE = R / 'src/object.s'
OLD_POST = bytes.fromhex('ad0260c904d0158d6a01a9a78d6c01a9ba8d6d01a9c5205a014c1da2c902f008c905f004c90ad017203fb9f0128d6a01a90d8d6c01a9bf8d6d01a9cf205a014cce8a')
OLD_FIREBAR = bytes.fromhex('9848bd1e7ec90cb01d8a0a8db77e0a186db77e0a187d1e7ea8a50999247ea50a996c7efe1e7e68a860')


def change(raw, bank, pc, old, new):
    at = S.FRONT.off(bank, pc)
    assert len(old) == len(new) and raw[at:at + len(old)] == old, (bank, hex(pc))
    raw[at:at + len(new)] = new
    return dict(physical_PRG=bank, CPU_half_open=[pc, pc + len(old)], file_offset=at,
                old_hex=old.hex(), new_hex=new.hex())


def post_source():
    text = L.POST.read_text()
    text = O.one(text, '    Packet $bf0d, $cf', '    sta FarA\n    Packet $bf0d, $cf')
    return O.one(text, '.res $42-(*-GfPostEnemy)', '.res $43-(*-GfPostEnemy)')


def firebar_source(output):
    text = FIREBAR_SOURCE.read_text().split('.proc CacheFirebarPart\n', 1)[1].split('.endproc', 1)[0]
    assert CALLER_SOURCE.read_text().count('jsr CacheFirebarPart') == 1
    text = O.one(text, '  phy\n', '  tya\n  pha\n')
    text = O.one(text, '  ply\n', '  pla\n  tay\n')
    symbols = ('FirebarPartCount=$7e1e\nFirebarPartX=$7e24\nFirebarPartY=$7e6c\n'
               'FirebarTemp=$7eb7\nR6=$09\nR7=$0a\n.segment "CACHE"\n')
    old, _ = O.assemble(output, symbols + text, (('C', 0xa237, 41, ('CACHE',)),))
    assert old == OLD_FIREBAR
    # This native caller uses the six indexed enemy actor slots. Even the
    # widened qualification X=0..63 has clear C after the second ASL.
    text = O.one(text, '  asl\n  clc\n  adc FirebarTemp', '  asl\n  adc FirebarTemp')
    new, _ = O.assemble(output, symbols + text, (('C', 0xa238, 40, ('CACHE',)),))
    assert len(new) + 1 == len(old)
    return new


def compose(output):
    old, prior = H.Trace.image()
    stock = O.Page.bundle()
    raw = bytearray(old['raw'])
    rproof = O.Page.load_json(RENDER / 'proof.json')
    sprite = (RENDER / 'render.bin').read_bytes()
    assert rproof['passed'] and rproof['parent_SHA256'] == O.PIN and rproof['draw_address'] == 0xa4be
    assert len(sprite) == 820
    code = bytearray((H.LOAD / 'kernel.bin').read_bytes())
    assert SHA(code) == prior['kernel_SHA256']
    assert code[0x4be:0x7f2] == (L.RENDER / 'render.bin').read_bytes()
    code[0x4be:0x7f2] = sprite
    atlas = (S.ART.parent / 'atlas.chr').read_bytes()
    cookie = bytes((0xa7, 42, 1)) + bytes.fromhex(SHA(code + atlas))[:13]
    rows = prior['patch_PRG'][:]
    old_post = next(row for row in rows if row['physical_PRG'] == 0 and row['CPU_half_open'][0] == 0xa1f5)
    assert bytes.fromhex(old_post['old_hex']) == OLD_POST
    proxy = next(row for row in rows if row['physical_PRG'] == 81 and row['CPU_half_open'][0] == 0xbfe0)
    post, _ = O.assemble(output, post_source(), (('P', 0xa1f5, 0x43, ('POST',)), ('X', 0xbfe0, 32, ('PROXY',))))
    assert len(post) == 0x43 + 32 and post[0x43:] == bytes.fromhex(proxy['new_hex'])
    new_cache = firebar_source(output)
    at = S.FRONT.off(0, 0xa1f5)
    raw[at:at + len(OLD_POST)] = OLD_POST
    rows.remove(old_post)
    rows.append(change(raw, 0, 0xa1f5, OLD_POST + OLD_FIREBAR, post[:0x43] + new_cache))
    calls = [pc for pc in range(0xa000, 0xbffe) if raw[S.FRONT.off(0, pc):S.FRONT.off(0, pc) + 3] == b'\x20\x37\xa2']
    assert calls == [0xb15d]
    rows.append(change(raw, 0, 0xb15d, b'\x20\x37\xa2', b'\x20\x38\xa2'))
    rows.append(change(raw, 65, 0xab81, bytes.fromhex(prior['cookie']), cookie))
    original = O.Page.load_json(S.OWNER / 'proof.json')
    for i, page in enumerate(original['code_pages']):
        at = page['file_offset']
        raw[at:at + 1024] = code[i * 1024:(i + 1) * 1024]
    return stock, dict(old, raw=bytes(raw)), prior, rows, bytes(code), cookie


def firebar_vectors(stock, trial):
    count = 0
    for x in range(64):
        for part in range(16):
            a = N.fresh(stock)
            a[0x7e1e + x], a[9], a[10] = part, 0x35, 0x46
            z = S.Preview.rebind(N.fork(a), trial)
            # Same native call site, then resume at its TYA.
            for m in (a, z):
                m[0x145] = 128
                m[0x5115] = 128
            c0 = O.NesMPU(memory=a, pc=0xb15d)
            c1 = O.NesMPU(memory=z, pc=0xb15d)
            for c in (c0, c1):
                c.a, c.x, c.y, c.p, c.sp = 91, x, 131, 0xe1, 224
                for _ in range(40):
                    if c.pc == 0xb160:
                        break
                    assert c.memory[c.pc]
                    c.step()
                else:
                    raise AssertionError(('cache did not return', x, part, c.pc))
            assert (c0.a, c0.x, c0.y, c0.p, c0.sp) == (c1.a, c1.x, c1.y, c1.p, c1.sp), (x, part)
            assert S.Preview.snapshot(a) == S.Preview.snapshot(z), (x, part)
            count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(R / 'build')
    out.mkdir(exist_ok=True)
    stock, trial, prior, rows, kernel, cookie = compose(out)
    expected = SHA(trial['raw'])
    targets = {int(k): v for k, v in prior['public_vector_rows'].items()}
    print(json.dumps(dict(memory_only_SHA256=expected, cookie=cookie.hex())), flush=True)
    foreign = H.existing_post(stock, trial)
    firebar = firebar_vectors(stock, trial)
    print(json.dumps(dict(foreign_post=foreign, firebar=firebar)), flush=True)
    menus = L.qualify_menu(stock, trial)
    stage = L.native(trial, kernel, cookie, targets, O.Page.load_json(S.OWNER / 'proof.json')['kernel_labels']['GfHostSwordContact'])
    trace = H.Trace.trace(trial)
    sprites = trace['pre_DMA_visible']
    assert len(sprites) == 5 and trace['chr'][0] == 990
    assert [event['visible'] for event in trace['events'] if event.get('address') == 0x4014] == [sprites]
    vectors = H.hot(trial, dict(cookie=cookie.hex()))
    bindings = (Path(__file__), Path(H.__file__), PRIOR, H.LOAD / 'kernel.bin', FIREBAR_SOURCE,
                CALLER_SOURCE, L.POST, RENDER / 'proof.json', RENDER / 'render.bin')
    result = dict(passed=True, ROM_written=False, renderer_installed=True, parent_SHA256=O.PIN,
                  expected_memory_only_SHA256=expected, kernel_SHA256=SHA(kernel), cookie=cookie.hex(),
                  patch_PRG=rows, public_vector_rows=targets, native_stage=stage, menus=menus,
                  foreign_post_enemy_cases=foreign, firebar_native_caller_cases=firebar, native_DMA=sprites,
                  real_hot_vectors=vectors,
                  scope='Real CPU native cold menu and movement, sword, fixed zero OAM reservation and DMA. Hardware visual replay, backdrop and HUD remain open.',
                  bindings={p.relative_to(R).as_posix(): SHA(p.read_bytes()) for p in bindings})
    (out / 'kernel.bin').write_bytes(kernel)
    (out / 'proof.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(passed=True, native_stage=stage, hot=vectors)))


if __name__ == '__main__':
    main()
