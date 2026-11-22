"""Exact a6 Popo/Nana stock-item hooks and compiled-menu metadata, RAM only.

The retained Ice route identifies slot19/raw20/IcVariant0..1. Reference
images supply symbols only; every returned hook describes the supplied a6
image. This facade does not launch an emulator or create build artifacts.
"""

from functools import lru_cache
from pathlib import Path

import current_sonic_stock_binding_1122 as Stock


R, ROM, H, N, W, Frames = Stock.R, Stock.ROM, Stock.H, Stock.N, Stock.W, Stock.Frames
PIN = Stock.PIN
FORMS = {'popo': (0, 'POPO'), 'nana': (1, 'NANA')}
ITEMS = {'mushroom': 0, 'flower': 1, 'star': 2, '1up': 3}
BITS = dict(a=128, b=64, select=32, start=16, up=8, down=4, left=2, right=1)
BLOCKS = {'mushroom': (336, 144), 'flower': (1248, 144),
          'star': (1616, 144), '1up': (1024, 128)}
SOURCE_PINS = {
    'tools/audit/current_sonic_stock_binding_1122.py': '37fd467af96046597fcfa1cc6d72baaee4ab9718439ebbb832e96c62d87fcb38',
    'tools/audit/current_character_route_1030_v4.py': 'cd1bded3e69401981238019ae9426d7f9f5c2eafaa93004126ee4602742b4613',
    'tools/audit/current_ice_route_1030_v1.py': '50812809d9d510ffc6af21a3ee063d99415edf854066af9f8b07f8a335f1b3f8',
    'src/ice_climbers_state.inc': '599ccde67599e166efe39b1bedc5909aad65479f3431c0230a62adc73c6341d3',
    'src/ice_climbers_core.s': 'c2c607a8eee74ffb28c71fb009436ead6a0fa42e40e3c8162ba5b287ee1442f5',
    'src/character_select.s': '405bc5250be8dee5133460d961af489babbb505bff6deb3032d7af1ac42e8a42',
}
RAM_FIELDS = (
    'Player_X_Position', 'Player_PageLoc', 'Player_Y_Position', 'Player_Y_HighPos',
    'Player_State', 'Player_X_Speed', 'Player_Y_Speed', 'PlayerStatus', 'PlayerSize',
    'PlayerFacingDir', 'PreviousA_B_Buttons', 'SavedJoypadBits', 'SavedJoypad1Bits',
    'A_B_Buttons', 'Left_Right_Buttons', 'Up_Down_Buttons', 'WorldNumber',
    'LevelNumber', 'AreaPointer', 'AreaType', 'AreaAddrsLOffset', 'GameEngineSubroutine',
    'ScreenLeft_X_Pos', 'ScreenLeft_PageLoc', 'Block_Buffer_1', 'Enemy_Flag', 'Enemy_ID',
    'Enemy_State', 'Enemy_X_Position', 'Enemy_PageLoc', 'Enemy_Y_Position',
    'Enemy_Y_HighPos', 'PowerUpType', 'ObjectOffset', 'OperMode', 'OperMode_Task',
    'NumberofLives', 'SelectedCharacter', 'CrossoverBehaviorVersion', 'CheatInvincible',
    'CheatStartLevel', 'CrossoverTitleDrawn', 'DisableScreenFlag', 'CrossoverMenuState',
    'CrossoverMenuIndex', 'CrossoverOptionsFocus', 'TimerControl', 'ScrollLock',
    'X5ChrMode', 'StarInvincibleTimer', 'AreaMusicQueue', 'Square1SoundQueue',
    'Square2SoundQueue', 'FloateyNum_Control', 'FloateyNum_Timer', 'Player1ScoreDisplay',
    'IcVariant', 'IcPower', 'IcReady', 'IcLife', 'IcArea', 'IcWorld', 'IcPaletteAck',
    'IcPrevious', 'IcFresh', 'IcAttack', 'IcAttackHits', 'IcRun', 'IcMoveDir', 'IcCoast',
    'IcHurt', 'IcClock', 'IcPose', 'IcJumpAge', 'IcJumpActive', 'IcJumpHits', 'IcWeaponHits',
)
HOOK_NAMES = (
    'GameLoop', 'IcMovement', 'IcPickup', 'IcWeapons', 'IcEnsure', 'IcAreaReset',
    'HandlePowerUpCollision', 'PlayerHeadCollision', 'SetupPowerUp', 'NrPickup',
    'NrPickupCollision', 'MarioSourcePowerupCollision', 'EraseEnemyObject',
    'SetupFloateyNumber', 'FloateyNumbersCore', 'DecNumTimer', 'NrMenuNavigate',
    'NrMenuCharacter',
)


@lru_cache(maxsize=1)
def _metadata(raw):
    for path, expected in SOURCE_PINS.items():
        assert H((R / path).read_bytes()) == expected, path
    ref = Stock.reference(raw)
    bundle = Stock.Sonic.bindings(ref)['bundle']
    assert len(raw) == 2097168 and H(raw) == PIN
    assert raw[:4] == b'NES\x1a' and ((raw[6] >> 4) | (raw[7] & 0xf0)) == 5
    preserved = []
    # Both resident native banks and all four original Ice body pages remain
    # exact. There is no Ice private RAM carrier or invented cookie to admit.
    for bank in (62, 70):
        at = 16 + bank * 8192
        assert raw[at:at+8192] == ref[at:at+8192], ('Ice native bank changed', bank)
        preserved.append(dict(bank=bank, SHA256=H(raw[at:at+8192])))
    chr_start = 16 + 1048576
    for page in range(712, 716):
        at = chr_start + page * 1024
        assert raw[at:at+1024] == ref[at:at+1024], ('Ice body CHR changed', page)
        preserved.append(dict(CHR_page=page, SHA256=H(raw[at:at+1024])))
    return ref, bundle, preserved


def bindings(raw, form='popo', item='mushroom', *, mode=None):
    """Return physical-PRG hooks; historic defaults are Popo Easy/Nana Hard.

    hooks use {pc, tag, offset, hex, bytes}; offset excludes the iNES header.
    navigation[index+1] is a direction name, matching the retained Lua menu.
    menu is its cold-start pulse path for auditing; dynamic state/readback
    checks and complete releases between pulses remain the driver's job.
    """
    assert form in FORMS and item in ITEMS
    mode = mode or ('hard' if form == 'nana' else 'easy')
    assert mode in ('easy', 'hard')
    ref, bundle, preserved = _metadata(raw)
    variant, name = FORMS[form]
    fields = {name: W.address(bundle, name) for name in RAM_FIELDS}
    assert (fields['IcVariant'], fields['IcPower']) == (0x5fec, 0x5f84)

    def hook(name, delta=0, count=12):
        pc, at = W.address(bundle, name)+delta, W.location(bundle, name)+delta
        bank = (at-16)//8192
        assert 0 <= bank < 128 and (at-16) == bank*8192+(pc & 8191)
        code = raw[at:at+count]
        if name != 'GameLoop':
            assert code == ref[at:at+count], ('Native hook changed', name, delta)
        return dict(pc=pc, tag=bank | 128, offset=at-16, hex=code.hex(),
                    bytes=list(code), bank_SHA256=H(raw[16+bank*8192:16+(bank+1)*8192]))

    hooks = {name: hook(name) for name in HOOK_NAMES}
    assert hooks['IcMovement']['tag'] == 128+62 and hooks['IcPickup']['tag'] == 128+62

    def find(owner, pattern, count, limit=256):
        at = W.location(bundle, owner)
        body = raw[at:at+limit]
        hits = [i for i in range(len(body)-len(pattern)+1) if body[i:i+len(pattern)] == pattern]
        assert len(hits) == 1, (owner, pattern.hex(), hits)
        return hook(owner, hits[0], count)

    lives = fields['NumberofLives'].to_bytes(2, 'little')
    hooks['LifeCredit'] = find('DecNumTimer', b'\xee'+lives, 3, 48)
    hooks['LifeCreditAfter'] = hook('DecNumTimer', hooks['LifeCredit']['pc']-W.address(bundle, 'DecNumTimer')+3)
    star = fields['StarInvincibleTimer'].to_bytes(2, 'little')
    music = fields['AreaMusicQueue'].to_bytes(2, 'little')
    star_pattern = b'\xa9\x23\x8d'+star+b'\xa9\x40\x8d'+music
    hooks['StockStarGrant'] = find('MarioSourcePowerupCollision', star_pattern, len(star_pattern), 96)
    float_control = fields['FloateyNum_Control'].to_bytes(2, 'little')
    hooks['StockOneUpGrant'] = find('MarioSourcePowerupCollision', b'\xa9\x0b\x9d'+float_control+b'\x60', 6)
    pickup_at = W.location(bundle, 'IcPickup')
    pickup_size = int(bundle['syms']['IcPickup']['size'], 0)
    assert 0 < pickup_size < 96
    hooks['IcPickupSuccess'] = find('IcPickup', b'\x38\x60', 2, pickup_size)
    hooks['IcPickupReturn'] = hook('IcPickup', pickup_size-1, 1)
    assert hooks['IcPickupReturn']['hex'] == '60'

    # The historical X5Menu* table labels now name executable helpers. Bind
    # their actual callers and implementations before deriving the graph.
    menu_bank = 16+124*8192
    menu_code = {
        0xa000: bytes.fromhex('088a2907d0058a0907d003ca8ae828090060'),
        0xa012: bytes.fromhex('08e88a2907f0058aca4c0ea0ca8a29184c0ea0'),
        0xa080: bytes.fromhex('2086a0491060'),
        0xa086: bytes.fromhex('088a186908291f28090060'),
        0xa0a0: bytes.fromhex('bd40a0'),
    }
    for pc, code in menu_code.items():
        at = menu_bank+(pc & 8191)
        assert raw[at:at+len(code)] == ref[at:at+len(code)] == code, ('Computed menu helper', hex(pc))
    at = W.location(bundle, 'NrMenuNavigate')
    nav = bytes.fromhex('ad0873290ff02da92420a5acae0973ad08732908f0042080a060'
                        'ad08732904f0042086a060ad08732902f0042000a0602012a060')
    assert raw[at:at+len(nav)] == ref[at:at+len(nav)] == nav
    at = W.location(bundle, 'NrMenuCharacter')
    assert raw[at:at+4] == ref[at:at+4] == bytes.fromhex('4c25a0ea')
    ids = list(raw[menu_bank+0x40:menu_bank+0x60])
    assert raw[menu_bank+0x40:menu_bank+0x60] == ref[menu_bank+0x40:menu_bank+0x60] and ids[19] == 20
    edges = {
        'left': [(i & 24) | ((i-1) & 7) for i in range(32)],
        'right': [(i & 24) | ((i+1) & 7) for i in range(32)],
        'up': [(i-8) & 31 for i in range(32)],
        'down': [(i+8) & 31 for i in range(32)],
    }
    paths = []
    for start in range(32):
        queue, seen = [(start, [])], {start}
        for node, path in queue:
            if node == 19:
                paths.append(path)
                break
            for key, table in edges.items():
                nxt = table[node]
                if nxt not in seen:
                    seen.add(nxt); queue.append((nxt, path+[key]))
        else:
            raise AssertionError(('Ice menu unreachable', start))
    prefix = [BITS['down'], BITS['a'], BITS['down'], BITS['a'], BITS['b']] if mode == 'hard' else []
    menu = prefix+[BITS['start']]+[BITS[key] for key in paths[0]]
    menu += [BITS['select']]*variant+[BITS['start']]
    bx, by = BLOCKS[item]
    return dict(sha=PIN, key=form, form=form, name=name, variant=variant, select=variant,
                character=20, slot=19, menu_index=19, variant_symbol='IcVariant',
                mode=mode, mode_value=int(mode == 'hard'), stockKind=ITEMS[item], item=item,
                blockX=bx, blockY=by, bits=BITS.copy(), menu=menu,
                navigation=[path[0] if path else '' for path in paths],
                menu_route=paths[0], menu_edges=edges, menu_raw_ids=ids,
                menu_computed_helpers={hex(pc): code.hex() for pc, code in menu_code.items()},
                ram=fields, hooks=hooks,
                preserved_Ice_domains=preserved, physical_PRG_only=True,
                reference9826_metadata_only_SHA256=Stock.Sonic.PIN,
                reference_facade_SHA256=SOURCE_PINS['tools/audit/current_sonic_stock_binding_1122.py'],
                facade_SHA256=H(Path(__file__).read_bytes()), actual_a6_CPU=True,
                controller_only_required=True, no_files_or_emulator=True)
