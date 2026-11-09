"""Qualify the Getsu-only native status header on the current renderer."""

import argparse
import json
from pathlib import Path

import check_getsu_loaded_stage_v2_1110 as V


R, S, O, N, SHA = V.R, V.S, V.O, V.N, V.SHA
H = V.H
SOURCE = R / 'tools/reference/getsu_fuma_native_hud_1110.s'
RENDER_SOURCE = R / 'src/screen_render.s'
CHARACTER_SOURCE = R / 'src/characters.s'
SOPHIA_SOURCE = R / 'src/sophia_math.s'
V2 = R / 'build/getsu-loaded-stage-v2-1110/proof.json'
NAME = bytes.fromhex('100e1d1c1e2424')


def apply(raw, output):
    """Apply the same HUD spans to any qualified image with exact preimages."""
    assert '.res 19-(*-UpdateNumber), $ea' in RENDER_SOURCE.read_text()
    assert '.res 32-(*-ProtoPortraitSpan),$ea' in RENDER_SOURCE.read_text()
    assert '.byte $20, $43, $07, "MARIO  "' in RENDER_SOURCE.read_text()
    assert '.proc CrossoverPatchStatusName' in CHARACTER_SOURCE.read_text()
    assert 'Ratio:\n  jmp ::SophiaRatioSelect\n  .res 39,$ea' in SOPHIA_SOURCE.read_text()
    out = bytearray(raw)
    code, labels = O.assemble(output, SOURCE.read_text(), (
        ('G', 0xb829, 16, ('GATE',)),
        ('P', 0xb3dd, 14, ('PACKET',)),
        ('T', 0xac00, 35, ('TEXT',)),
    ))
    assert labels == {'GfStatusGate': 0xb829, 'GfStatusPacket': 0xb3de, 'GfStatusText': 0xac00}, labels
    at = S.FRONT.off(3, 0xb829)
    assert raw[at - 3:at] == bytes.fromhex('4c97be')
    at = S.FRONT.off(3, 0xb3dd)
    assert raw[at - 3:at] == bytes.fromhex('205a01') and raw[at + 14] == 0x60
    at = S.FRONT.off(3, 0xb1dc)
    assert raw[at:at + 18] == bytes.fromhex('8d6a01a9e68d6c01a9b08d6d01a9c14c5a01')
    at = S.FRONT.off(36, 0xabfc)
    assert raw[at - 3:at + 39] == bytes.fromhex('4cb6d4') + b'\xea' * 39
    assert raw[at + 39:at + 43] == bytes.fromhex('a407b924')

    patches = [
        V.change(out, 3, 0xb1dc, bytes.fromhex('8d6a01'), bytes.fromhex('4c29b8')),
        V.change(out, 3, 0xb829, b'\xea' * 16, code[:16]),
        V.change(out, 3, 0xb3dd, b'\xea' * 14, code[16:30]),
        V.change(out, 36, 0xac00, b'\xea' * len(code[30:]), code[30:]),
    ]
    return bytes(out), patches, labels


def compose(output):
    before = O.Page.load_json(V2)
    stock, loaded, _, _, kernel, cookie = V.compose(output)
    assert SHA(loaded['raw']) == before['expected_memory_only_SHA256']
    after, patches, labels = apply(loaded['raw'], output)
    return stock, loaded, dict(loaded, raw=after), patches, labels, kernel, cookie


def native_names(before, after):
    old_seed, new_seed = H.prepare(before), H.prepare(after)
    name_at = S.address(before, 'VRAM_Buffer1') + 11
    assert name_at == 0x04ba
    assert bytes(old_seed.vram[0x2043:0x204a]) == bytes.fromhex('160a1b12182424')
    assert bytes(new_seed.vram[0x2043:0x204a]) == NAME
    count, owned = 0, 0
    for raw in range(43):
        for message in (0, 1, 2, 3, 4):
            for flags in (0x21, 0x60, 0xa1):
                m = N.fork(old_seed)
                N.put(m, SelectedCharacter=raw, CurrentPlayer=0, NumberOfPlayers=0)
                z = S.Preview.rebind(N.fork(m), after)
                O.clear_logs(m)
                O.clear_logs(z)
                a = S.FRONT.F.invoke(m, 'WriteGameText', a=message, p=flags)
                b = S.FRONT.F.invoke(z, 'WriteGameText', a=message, p=flags)
                if raw == 42:
                    expect = NAME if message == 0 else bytes(m[name_at:name_at + 7])
                    assert bytes(z[name_at:name_at + 7]) == expect
                    base = name_at - 11
                    assert bytes(z[base:name_at]) == bytes(m[base:name_at])
                    assert bytes(z[name_at + 7:base + 64]) == bytes(m[name_at + 7:base + 64])
                    owned += 1
                else:
                    assert {k: v for k, v in a.items() if k != 'minimum_SP'} == {
                        k: v for k, v in b.items() if k != 'minimum_SP'}, (raw, message, flags, a, b)
                    assert S.Preview.snapshot(m) == S.Preview.snapshot(z), (raw, message, flags)
                    count += 1
    return dict(actual_foreign_WriteGameText=count, actual_GetSu_WriteGameText=owned, cold_nametable=NAME.hex())


def hot_names(b):
    m = H.prepare(b)
    N.put(m, NmiDisable=255, CurrentPlayer=0, NumberOfPlayers=0)
    count = {'FF': 0, 'IRQ': 0, 'nested': 0}
    minimum = 224
    seen = set()
    deepest = None

    def collect(c):
        nonlocal deepest
        if not c.p & 4 and (deepest is None or c.sp < deepest.sp):
            deepest = H.clone(c)

    def watch(c):
        nonlocal minimum
        bank, pc = H.point(c)
        if not (bank == 164 and 0xac00 <= pc < 0xac23 or
                bank == 131 and (0xb3dd <= pc < 0xb3eb or 0xb829 <= pc < 0xb839) or
                bank == 0 and 0x15a <= pc < 0x17b):
            return
        key = bank, pc, c.sp
        if key in seen:
            return
        seen.add(key)
        for kind in ('FF', 'IRQ'):
            if kind == 'IRQ' and c.p & 4:
                continue
            q = H.clone(c)
            packet = bytes(q.memory[0x04af:0x04ff])
            minimum = min(minimum, H.vector(q, kind, collect if kind == 'FF' else None))
            assert bytes(q.memory[0x04af:0x04ff]) == packet
            count[kind] += 1

    S.FRONT.F.invoke(m, 'WriteGameText', a=0, p=0x21, watch=watch)
    assert deepest is not None
    minimum = min(minimum, H.vector(deepest, 'IRQ'))
    count['nested'] += 1
    assert bytes(m[0x04ba:0x04c1]) == NAME
    return dict(cuts=count, minimum_SP=minimum)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(R / 'build')
    out.mkdir(exist_ok=True)
    stock, before, after, patches, labels, kernel, cookie = compose(out)
    names = native_names(before, after)
    menus = V.L.qualify_menu(stock, after)
    hot = hot_names(after)
    files = (Path(__file__), SOURCE, RENDER_SOURCE, CHARACTER_SOURCE, SOPHIA_SOURCE, V2,
             S.SOURCE, S.R / 'build/getsu-native-stage-1110/proof.json')
    result = dict(passed=True, ROM_written=False, parent_SHA256=SHA(before['raw']),
                  expected_memory_only_SHA256=SHA(after['raw']), patches=patches, labels=labels,
                  names=names, menus=menus, real_vectors=hot, unchanged_kernel_SHA256=SHA(kernel),
                  unchanged_cookie=cookie.hex(), bindings={p.relative_to(R).as_posix(): SHA(p.read_bytes()) for p in files})
    (out / 'proof.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(passed=True, names=names, menus=menus, hot=hot, SHA256=SHA(after['raw']))))


if __name__ == '__main__':
    main()
