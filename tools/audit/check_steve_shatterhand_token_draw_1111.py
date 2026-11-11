"""Compose Steve's physical token glyphs and verify their native sprite output."""

import argparse
import json

import check_steve_shatterhand_token_art_1111 as Art
import check_steve_shatterhand_token_ingress_1111 as Ingress


S, C, H, N, W = Ingress.S, Ingress.C, Ingress.H, Ingress.N, Ingress.W
SOURCE = H.ROOT / 'tools/reference/steve_shatterhand_token_draw_1111.s'
HUD = H.ROOT / 'tools/reference/steve_shatterhand_token_hud_1111.s'
START, END, NEXT = 0xa9e8, 0xaa05, 0xaa1e
CHR_PAGE, CHR_OFFSET = 710, 0x300
OLD = bytes.fromhex('bd627d297fc901d009a9da8503a9c14c03aaa8b94ec08503b95cc08504')
NATIVE = ('InvPickup', 'Enemy_State', 'Enemy_X_Position', 'Enemy_PageLoc', 'Enemy_Y_Position',
          'ScreenLeft_X_Pos', 'ScreenLeft_PageLoc')


def proposal(raw):
    bundle = W.Symbols.bundle()
    transport = Ingress.Transport
    origin, scan = transport.LIFECYCLE, transport.EXTRA
    hud_stub = '.segment "TOKEN_INGRESS"\nSteveTokenHud:\n    rts\n'
    ingress, punch = Ingress.link(bundle, token_draw=scan, token_hud=hud_stub)
    fields = {name: ingress['symbols'][name] for name in (
        'SteveTokenStamp', 'SteveTokenOwned', 'SteveTokenPending', 'SteveTokenPattern',
        'SteveTokenFlightX', 'SteveTokenFlightY')}
    fields.update({name: W.address(bundle, name) for name in NATIVE}, NextWorldItem=NEXT)
    fields.update(NativeRender=W.address(bundle, 'MetaspriteRenderLoop'),
                  SteveDrawInvoke=punch['symbols']['SteveDrawInvoke'])
    bindings = ''.join(f'{name}=${address:04x}\n' for name, address in fields.items())
    program = H.assemble(bindings + SOURCE.read_text(encoding='utf-8'),
                         {'ITEM_SELECT': (START, END-START), 'TOKEN_DRAW': (origin, transport.LIFECYCLE_SIZE),
                          'DRAW_SCAN': (scan, transport.EXTRA_SIZE)})
    assert program['symbols']['SteveDrawTokens'] == scan
    select = program['images']['ITEM_SELECT']
    assert len(OLD) == len(select) == END - START
    art = Art.original_art(Art.Donor.DONOR.read_bytes())
    pixels = art[1] + art[2]
    # Only JnDraw's world item select reads these two PRG97 tables. Its
    # special heart pointer is the same slot-1 lookup after rebinding.
    prg = raw[16:C.CHR]
    assert prg.count(bytes.fromhex('b94ec0')) == prg.count(bytes.fromhex('b95cc0')) == 1
    at = C.offset(97, 0xc04e)
    assert raw[at+1] == 0xf5 and raw[at+15] == 0xc1
    edits = ((C.offset(98, START), OLD, select),
             (at+1, b'\xf5', b'\xda'),
             (C.CHR+1024*CHR_PAGE+CHR_OFFSET, bytes(len(pixels)), pixels))
    pair = program['symbols']['SteveDrawTokenPair']
    hud = f'SteveDrawTokenPair=${pair:04x}\n' + HUD.read_text(encoding='utf-8')
    image, info = Ingress.proposal(raw, lifecycle=program['images']['TOKEN_DRAW'], token_draw=scan,
                                   token_hud=hud, extra=program['images']['DRAW_SCAN'], extra_edits=edits)
    assert info['symbols']['SteveTokenOwned'] == fields['SteveTokenOwned']
    return image, info | dict(draw_bytes=len(program['images']['TOKEN_DRAW']), draw_pair=pair,
                              scan_bytes=len(program['images']['DRAW_SCAN']))


def token_pair(memory, x, y, symbol):
    if not (0 <= x < 248 and 0 <= y < 240):
        return False
    tile = 0x31 + (symbol - 1) * 4
    oam = bytes(memory[0x200:0x300])
    cells = {oam[index:index+4] for index in range(0, 253, 4)}
    return {bytes((y, tile, 2, x)), bytes((y, tile+2, 2, x+8))} <= cells


def replay(image, info, *, beta):
    model, route = Ingress.authored_reveal(image, info)
    player_slot = 5
    source = info['symbols']
    offsets = {name: source[name]-0xc000 for name in (
        'SteveTokenPending', 'SteveTokenFlightX', 'SteveTokenFlightY', 'SteveTokenPattern')}
    original_step = route['frame']
    rendered = {'Alpha': 0, 'Beta': 0, 'flight': 0, 'HUD': 0}

    def check():
        if N.get(model, 'Enemy_Flag', player_slot):
            tag = N.get(model, 'InvPickup', player_slot)
            if tag in (0x8c, 0x8d):
                x = 256 * (N.get(model, 'Enemy_PageLoc', player_slot) - N.get(model, 'ScreenLeft_PageLoc'))
                x += N.get(model, 'Enemy_X_Position', player_slot) - N.get(model, 'ScreenLeft_X_Pos')
                y = N.get(model, 'Enemy_Y_Position', player_slot) + 8
                if token_pair(model, x, y, 1 + (tag & 1)):
                    rendered['Beta' if tag & 1 else 'Alpha'] += 1
        work = model.ram[2]
        pending = work[offsets['SteveTokenPending']]
        if pending and token_pair(model, work[offsets['SteveTokenFlightX']],
                                  work[offsets['SteveTokenFlightY']], pending):
            rendered['flight'] += 1
        pattern = work[offsets['SteveTokenPattern']]
        if pattern and token_pair(model, 96, 34, pattern & 3):
            rendered['HUD'] += 1
        assert model.chr_latches[4] == CHR_PAGE

    def observe(pad):
        original_step(pad)
        check()

    check()
    route['frame'] = observe
    earned = Ingress.collect(model, route, info, beta=beta)
    for _ in range(8):
        observe(0)
    assert rendered['Alpha'] and rendered['flight'] and rendered['HUD'], (earned, rendered)
    assert bool(rendered['Beta']) == beta, (earned, rendered)
    return dict(earned=earned, sprite_pairs=rendered)


def multiple_slot_sprites(image, info):
    model, route = Ingress.authored_reveal(image, info)
    # The pickup engine can allocate another native slot before the first
    # token clears. Use a directed visual fixture for the simultaneous pair.
    fields = dict(Enemy_Flag=1, Enemy_ID=46, Enemy_State=128, InvPickup=0x8d,
                  InvPickupOwner=16, Enemy_PageLoc=1, Enemy_X_Position=112,
                  Enemy_Y_Position=120, Enemy_Y_HighPos=1)
    for field, value in fields.items():
        model[W.address(model.bundle, field)+4] = value
    model.ram[2][0x3fc] |= 1 << 4
    route['frame'](0)
    left = N.get(model, 'ScreenLeft_PageLoc')*256 + N.get(model, 'ScreenLeft_X_Pos')
    assert token_pair(model, 336-left, 128, 1)
    assert token_pair(model, 368-left, 128, 2)
    return dict(alpha_slot=5, beta_slot=4, camera=left, matching_sprites=4)


def foreign_item_sprites(raw, image):
    comparisons = 0
    for variant in (0, 1):
        bases = [Ingress.Live.opening(rom, variant)[0] for rom in (raw, image)]
        for payload in (0x81, 0x8c, 0x8d):
            models = [C.Vector.clone(base) for base in bases]
            for model in models:
                fields = dict(Enemy_Flag=1, Enemy_ID=46, Enemy_State=128, InvPickup=payload,
                              InvPickupOwner=16, Enemy_PageLoc=0, Enemy_X_Position=144,
                              Enemy_Y_Position=120, Enemy_Y_HighPos=1)
                for field, value in fields.items():
                    model[W.address(model.bundle, field)+5] = value
                C.Vector.call(model, 'JnDraw')
            parent, candidate = models
            assert bytes(parent[0x200:0x300]) == bytes(candidate[0x200:0x300]), (variant, payload)
            assert parent.chr_latches == candidate.chr_latches
            assert N.get(parent, 'CurrentOAMOffset') == N.get(candidate, 'CurrentOAMOffset')
            comparisons += 1
    return comparisons


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--all-blocks', action='store_true')
    args = parser.parse_args()
    raw = S.Donor.HOST.read_bytes()
    image, info = proposal(raw)
    alpha, beta = (replay(image, info, beta=value) for value in (False, True))
    result = dict(passed=True, candidate=C.digest(image), cookie=info['cookie'].hex(),
                  worker_bytes=info['draw_bytes'], scan_bytes=info['scan_bytes'], alpha=alpha, beta=beta,
                  simultaneous=multiple_slot_sprites(image, info), foreign_item_draws=foreign_item_sprites(raw, image),
                  output_files=0)
    if args.all_blocks:
        model, route = Ingress.third_block(image, info)
        assert all(token_pair(model, x, 34, 1) for x in Art.HUD_X)
        result['three_authored_blocks'] = route['third']
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
