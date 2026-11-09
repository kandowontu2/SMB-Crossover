"""Compose Getsu's native palette service with the current shared draw build."""

import argparse
import json
from pathlib import Path

import check_getsu_loaded_stage_v2_1110 as V2
from check_mini_funded_actor_1108_v3 import install


R, S, O, N, SHA = V2.R, V2.S, V2.O, V2.N, V2.SHA
PUBLIC = R / 'build/shared-sparse-draw-native-1110/candidate.nes'
PUBLIC_SHA = 'f33c7b19d27309ab4e4771125a74360f978dba08bd807d25bc6307026e568734'
SHARED = R / 'build/native-sparse-world-draw-1110/combo.json'
V2_PROOF = R / 'build/getsu-loaded-stage-v2-1110/proof.json'
RENDER = R / 'build/getsu-host-render-1110-v3'
V2_KERNEL = V2_PROOF.with_name('kernel.bin')
HUD = R / 'build/getsu-native-hud-1110/proof.json'
COLORS = bytes.fromhex('22220f0f0f220f0f')


def compose(output, hud=False):
    stock, stage, _, prior_rows, old_kernel, old_cookie = V2.compose(output)
    before = O.Page.load_json(V2_PROOF)
    assert before['passed'] and SHA(stage['raw']) == before['expected_memory_only_SHA256']
    assert old_kernel == V2_KERNEL.read_bytes() and SHA(old_kernel) == before['kernel_SHA256']
    current = PUBLIC.read_bytes()
    assert SHA(current) == PUBLIC_SHA
    shared = O.Page.load_json(SHARED)
    assert shared['passed'] and shared['parent_SHA256'] == O.PIN and shared['expected_memory_only_SHA256'] == PUBLIC_SHA
    patches = [p for group in shared['groups'].values() for p in group]
    assert install(stock['raw'], patches) == current
    assert not any(a['file_offset'] < b['file_offset'] + len(bytes.fromhex(b['old_hex']))
                   and b['file_offset'] < a['file_offset'] + len(bytes.fromhex(a['old_hex']))
                   for a in prior_rows for b in patches)
    raw = bytearray(install(stage['raw'], patches))

    renderer, renderer_proof = (RENDER / 'render.bin').read_bytes(), O.Page.load_json(RENDER / 'proof.json')
    assert renderer_proof['passed'] and renderer_proof['parent_SHA256'] == O.PIN
    assert renderer_proof['draw_address'] == 0xa4be and len(renderer) == 0x334
    target = renderer_proof['labels']['GfSetColors']
    code = bytearray(old_kernel)
    code[0x4be:0x7f2] = renderer
    assert code[78:81] == bytes.fromhex('1860ea')
    code[78:81] = b'\x4c' + target.to_bytes(2, 'little')
    targets = {int(k): v for k, v in before['public_vector_rows'].items()} | {26: target}
    atlas = (S.ART.parent / 'atlas.chr').read_bytes()
    cookie = bytes((0xa7, 42, 1)) + bytes.fromhex(SHA(code + atlas))[:13]
    rows = prior_rows + [V2.change(raw, 65, 0xab81, old_cookie, cookie)]
    owner = O.Page.load_json(S.OWNER / 'proof.json')
    for i, page in enumerate(owner['code_pages']):
        at = page['file_offset']
        assert raw[at:at + 1024] == old_kernel[i * 1024:(i + 1) * 1024]
        raw[at:at + 1024] = code[i * 1024:(i + 1) * 1024]

    if hud:
        import check_getsu_native_hud_1110 as Hud

        hud_proof = O.Page.load_json(HUD)
        assert hud_proof['passed']
        raw, edits, _ = Hud.apply(bytes(raw), output)
        rows.extend(edits)
    return dict(stock, raw=current), dict(stage, raw=bytes(raw)), rows, bytes(code), cookie, targets


def native_palette(stage, targets, cookie):
    m = V2.H.prepare(stage)
    assert O.headers(m) == (cookie, cookie)
    assert m.vram[0x3f10] == 0x22 and bytes(m.vram[0x3f11:0x3f14]) == bytes.fromhex('002005')
    buf = S.address(stage, 'VRAM_Buffer1')
    visits = 0
    cases = 0
    for area in range(4):
        for ctrl in range(8):
            a = N.fork(m)
            N.put(a, AreaType=area, BackgroundColorCtrl=ctrl, VRAM_Buffer1_Offset=0, VRAM_Buffer_AddrCtrl=0,
                  NmiDisable=255, GuestPowerupActive=0, StarInvincibleTimer=0)

            def watch(cpu):
                nonlocal visits
                if cpu.pc == targets[26] and a.rawtags[1] == 3:
                    assert O.headers(a) == (cookie, cookie)
                    visits += 1

            S.FRONT.F.invoke(a, 'GetPlayerColors', watch=watch)
            assert bytes(a[buf:buf+8]) == bytes((0x3f, 0x10, 4, COLORS[ctrl or area], 0, 32, 5, 0))
            assert N.get(a, 'VRAM_Buffer1_Offset') == 7
            cases += 1
    assert visits == cases
    return dict(authenticated_row26=visits, actual_cold_backdrop=m.vram[0x3f10],
                actual_cold_sprite_palette=list(m.vram[0x3f11:0x3f14]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--hud', action='store_true')
    args = parser.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R / 'build')
    out.mkdir(exist_ok=True)
    stock, stage, rows, code, cookie, targets = compose(out, args.hud)
    print(json.dumps(dict(memory_only_SHA256=SHA(stage['raw']), color_entry=targets[26], cookie=cookie.hex())), flush=True)
    palette = native_palette(stage, targets, cookie)
    foreign = V2.H.existing_post(stock, stage)
    native = V2.L.native(stage, code, cookie, targets,
                         O.Page.load_json(S.OWNER / 'proof.json')['kernel_labels']['GfHostSwordContact'])
    vectors = V2.H.hot(stage, dict(cookie=cookie.hex()))
    refs = [Path(__file__), PUBLIC, SHARED, V2_PROOF, V2_KERNEL, RENDER / 'proof.json', RENDER / 'render.bin']
    if args.hud:
        refs.append(HUD)
    proof = dict(passed=True, ROM_written=False, renderer_installed=True, native_HUD=args.hud,
                 parent_SHA256=PUBLIC_SHA, expected_memory_only_SHA256=SHA(stage['raw']), kernel_SHA256=SHA(code),
                 cookie=cookie.hex(), public_vector_rows=targets, patch_PRG=rows, native_palette=palette,
                 foreign_post_enemy_cases=foreign, native_stage=native, real_hot_vectors=vectors,
                 bindings={p.relative_to(R).as_posix(): SHA(p.read_bytes()) for p in refs})
    (out / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(passed=True, native_palette=palette, native_stage=native)), flush=True)


if __name__ == '__main__':
    main()
