"""Compose the proven native loader, Getsu preview, and loaded gameplay leaves."""

import argparse
from collections import Counter
import json
from pathlib import Path

import check_getsu_native_stage_1110 as S
import check_getsu_fuma_host_motion_1110 as Host


R, O, N, SHA = S.R, S.O, S.N, S.SHA
STAGE = R / 'build/getsu-native-stage-1110/proof.json'
RENDER = R / 'build/getsu-host-render-1110'
SIDE = R / 'tools/reference/mini_native_side_single_map_1109_v1.s'
POST = R / 'tools/reference/getsu_fuma_post_enemy_1110.s'
WRAPPER = 0xa7f2
SIDE_OLD = bytes.fromhex('0848ad0260c904f0e0c90bb0dc68284c8b95') + b'\xff' * 12
SIDE_NEW = bytes.fromhex('0848ad0260c904f0e0c92af004c90bb0d868284c8b95') + b'\xff' * 8


def qualify_menu(stock, trial):
    # Existing profiles still run their original generated name and preview
    # records. Only Simon variant3 with simultaneous Select+confirm changes.
    profiles, confirm = 0, 0
    for slot in range(32):
        m = S.Preview.seed(stock, slot)
        seen = set()
        for _ in range(32):
            _, cells = O.Page.menu_name(m)
            sig = (m[0x6002], tuple(cells), bytes(m[0x5fe0:0x5fff]), m[0x730a])
            if sig in seen:
                break
            seen.add(sig)
            a = N.fork(m)
            N.put(a, VRAM_Buffer1_Offset=0)
            z = S.Preview.rebind(N.fork(a), trial)
            O.clear_logs(a)
            O.clear_logs(z)
            r0 = S.Preview.RUN(a, 'QueueSelection')
            r1 = S.Preview.RUN(z, 'QueueSelection')
            assert {k: v for k, v in r0.items() if k != 'minimum_SP'} == {
                k: v for k, v in r1.items() if k != 'minimum_SP'}, (slot, r0, r1)
            assert S.Preview.snapshot(a) == S.Preview.snapshot(z), ('foreign name/preview', slot, sig[:2])
            for key in (16, 128, 48, 160, 176):
                old, new = N.fork(m), S.Preview.rebind(N.fork(m), trial)
                S.Preview.key(old, key)
                S.Preview.key(new, key)
                if slot == 5 and m[0x5fe7] == 3 and key & 32:
                    assert (old[0x6002], old[0x5fe7], new[0x6002], new[0x5fe7]) == (5, 0, 42, 4)
                else:
                    assert all(old[at] == new[at] for at in (0x6002, 0x7307, 0x7309, 0x730a, 0x5fe5, 0x5fe7, 0x5fe8)), (slot, key)
                    confirm += 1
            S.Preview.key(m, 32)
            profiles += 1
        else:
            raise AssertionError(('Select bound', slot))
    assert profiles == 100 and confirm == 497
    return dict(existing_profiles=profiles, foreign_confirmation_cases=confirm, intended_Select_confirm_cases=3)


def compose(output):
    art = O.Page.load_json(S.ART)
    render_path = RENDER / 'render.bin'
    render = O.Page.load_json(RENDER / 'proof.json')
    assert render['passed'] and render['parent_SHA256'] == O.PIN and render['draw_address'] == 0xa4be
    blob = render_path.read_bytes()
    menu, menu_labels = S.assemble(output, art)
    stock, trial, rows, kernel, old_cookie, targets = S.compose(menu, menu_labels, (blob, render['draw_address']))
    raw = bytearray(trial['raw'])

    def patch(bank, pc, old, new):
        at = S.FRONT.off(bank, pc)
        assert len(old) == len(new) and raw[at:at + len(old)] == old
        raw[at:at + len(new)] = new
        rows.append(dict(physical_PRG=bank, CPU_half_open=[pc, pc + len(old)], file_offset=at,
                         old_hex=old.hex(), new_hex=new.hex()))

    # Preserve the actual A33 side prefix and its rare Kamikaze path. Only
    # the ordinary foreign fallback checks an additional source owner.
    assert '.res 94-(*-ForeignSide), $ff' in SIDE.read_text()
    patch(33, 0xbee2, SIDE_OLD, SIDE_NEW)
    post, _ = O.assemble(output, POST.read_text(), (('P', 0xa1f5, 0x42, ('POST',)), ('X', 0xbfe0, 32, ('PROXY',))))
    assert len(post) == 0x42 + 32
    old_post = bytes.fromhex('ad0260c904d0158d6a01a9a78d6c01a9ba8d6d01a9c5205a014c1da2c902f008c905f004c90ad017203fb9f0128d6a01a90d8d6c01a9bf8d6d01a9cf205a014cce8a')
    patch(0, 0xa1f5, old_post, post[:0x42])
    assert raw[S.FRONT.off(81, 0xbf9b):S.FRONT.off(81, 0xbf9b) + 3] == b'\x4c\x5a\x01'
    # BmName now reads B0D0. This exact old tail was retired by Mario Tank.
    assert raw[S.FRONT.off(81, 0xbfc6):S.FRONT.off(81, 0xbfe0)] == bytes.fromhex(
        'ad0a7338e9050a0a0a0a1869d08505a9b069008506a9004c03b8')
    patch(81, 0xbfe0, b'\xea' * 32, post[0x42:])
    code = bytearray(kernel)
    original = O.Page.load_json(S.OWNER / 'proof.json')
    contact = original['kernel_labels']['GfHostSwordContact']
    # Scan native slots 5..0 after the existing native enemy/body loop.
    # Preserve X across the native defeat service.
    worker = bytes.fromhex('a2058a4820') + contact.to_bytes(2, 'little') + bytes.fromhex('68aaca10f61860')
    assert len(worker) == 14 and code[-14:] == b'\xff' * 14
    code[-14:] = worker
    code[12:15] = b'\x4c' + WRAPPER.to_bytes(2, 'little')
    targets[4] = WRAPPER
    atlas = (S.ART.parent / 'atlas.chr').read_bytes()
    cookie = bytes((0xa7, 42, 1)) + bytes.fromhex(SHA(bytes(code) + atlas))[:13]
    patch(65, 0xab81, old_cookie, cookie)
    for i, page in enumerate(original['code_pages']):
        at = page['file_offset']
        assert raw[at:at + 1024] == kernel[i * 1024:(i + 1) * 1024]
        raw[at:at + 1024] = code[i * 1024:(i + 1) * 1024]
    return stock, dict(trial, raw=bytes(raw)), rows, bytes(code), cookie, targets, contact


def native(b, code, cookie, targets, contact):
    m = S.ColdBus(b)
    cpu = O.NesMPU(memory=m, pc=None)
    cpu.reset()
    for _ in range(300000):
        if cpu.pc == S.address(b, 'IdleLoop'):
            break
        assert m[cpu.pc]
        cpu.step()
    else:
        raise AssertionError('No native IdleLoop')
    m.vblank_at_boot = False
    hits = Counter()
    minimum = 224
    table = {(3, targets[0]): 'movement', (3, targets[2]): 'draw', (3, targets[4]): 'weapons',
             (3, contact): 'sword_slot', (3, targets[36]): 'fresh', (161, 0xbee2): 'side_gate',
             (254, 0x958b): 'native_side', (254, S.address(b, 'ShellOrBlockDefeat')): 'native_defeat',
             (132, S.address(b, 'MetaspriteRenderLoop')): 'native_oam'}

    def watch(c):
        nonlocal minimum
        minimum = min(minimum, c.sp)
        if c.pc >= 0x8000:
            name = table.get((m.rawtags[(c.pc - 0x8000) // 8192], c.pc))
            if name:
                hits[name] += 1
                if name in ('movement', 'draw', 'weapons', 'sword_slot', 'fresh'):
                    assert O.headers(m) == (cookie, cookie)

    for i in range(120):
        if m[0x7307] == 2:
            break
        S.frame(m, 16 if i == 40 else 0, watch)
    else:
        raise AssertionError('No native menu')
    for _ in range(5):
        S.frame(m, 0, watch)
        S.frame(m, 1, watch)
    for _ in range(4):
        S.frame(m, 0, watch)
        S.frame(m, 32, watch)
    assert (m[0x7309], m[0x5fe7], m[0x6002]) == (5, 4, 5)
    S.frame(m, 0, watch)
    S.frame(m, 16, watch)
    assert m[0x6002] == 42
    for stage in range(600):
        if tuple(N.get(m, k) for k in ('OperMode', 'OperMode_Task', 'GameEngineSubroutine')) == (1, 3, 8):
            break
        S.frame(m, 0, watch)
    else:
        raise AssertionError('No active stage')
    assert O.headers(m) == (cookie, cookie) and bytes(m.ram[3][:2048]) == code

    for _ in range(5):
        S.frame(m, 0, watch)
    assert hits['draw'] and hits['native_oam'] and m.chr_latches[0] == 990, (hits, m.chr_latches)
    assert bytes(m.vram[0x3f11:0x3f14]) == bytes.fromhex('002005')
    draw_observation = dict(slot0_CHR=m.chr_latches[0], palette=bytes(m.vram[0x3f11:0x3f14]).hex(),
                            oam=bytes(m[0x200:0x214]).hex(), native_object= m[S.address(b, 'ObjectMetasprite')])
    assert draw_observation['native_object'] == 0, draw_observation
    # Check every header byte at the real public slot before any code entry.
    O.clear_logs(m)
    denies = 0
    for bank in (2, 3):
        for i in range(16):
            n = N.fork(m)
            n.ram[bank][0x1fe0 + i] ^= 1
            before = [bytes(row) for row in n.ram]
            for addr in (0xb08c, 0xb092, 0xb098, 0xb0f8):
                assert not O.invoke(n, addr)['P'] & 1 and [bytes(row) for row in n.ram] == before
                denies += 1

    started = None
    for frame in range(380):
        x = S.word_position(m)
        enemy = next((actor for actor in Host.actors(m) if actor['id'] == 6 and not actor['state'] & 32), None)
        pad = 1
        if started is None and enemy and 42 <= enemy['x'] - x <= 49:
            pad |= 0x40
            started = dict(frame=frame, x=x, enemy=enemy)
        S.frame(m, pad, watch)
        assert N.get(m, 'NumberofLives') == 2 and N.get(m, 'GameEngineSubroutine') == 8, (
            frame, x, started, N.get(m, 'NumberofLives'), N.get(m, 'GameEngineSubroutine'),
            dict(hits), list(m.ram[2][:30]), Host.actors(m))
        if started is not None and hits['native_defeat']:
            break
    else:
        raise AssertionError(('No natural sword defeat', started, S.word_position(m), dict(hits), Host.actors(m)))
    assert hits['movement'] and hits['weapons'] and hits['sword_slot'] == 6 * hits['weapons']
    assert hits['side_gate'] and hits['native_side']
    return dict(active_setup_updates=stage, draw=draw_observation, header_denies=denies,
                minimum_SP=minimum, natural_attack=started, native_defeat_frame=frame, calls=dict(hits))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(R / 'build')
    out.mkdir(exist_ok=True)
    stock, trial, rows, code, cookie, targets, contact = compose(out)
    print(json.dumps(dict(memory_only_SHA256=SHA(trial['raw']), cookie=cookie.hex(), targets=targets)), flush=True)
    result = native(trial, code, cookie, targets, contact)
    menus = qualify_menu(stock, trial)
    receipt = dict(passed=True, ROM_written=False, parent_SHA256=O.PIN,
                   expected_memory_only_SHA256=SHA(trial['raw']), kernel_SHA256=SHA(code), cookie=cookie.hex(),
                   patch_PRG=rows, public_vector_rows=targets, native_stage=result, menus=menus,
                   scope='CPU actual title through named menu, authenticated stage, loaded render and natural sword. Final native/ISR service and full route remain separate.',
                   bindings={p.relative_to(R).as_posix(): SHA(p.read_bytes()) for p in
                             (Path(__file__), STAGE, SIDE, POST, RENDER / 'proof.json', RENDER / 'render.bin')})
    (out / 'proof.json').write_text(json.dumps(receipt, indent=2) + '\n')
    (out / 'kernel.bin').write_bytes(code)
    print(json.dumps(dict(passed=True, native_stage=result, menus=menus)))


if __name__ == '__main__':
    main()
