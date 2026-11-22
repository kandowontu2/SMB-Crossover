"""Strict32eaf178 bindings for native D1 Mushroom and D2..D6 suit pickups."""

from copy import deepcopy
from pathlib import Path

import current_smb3_pickup_binding_1122 as Stock

R, ROM, H, N, W, Frames = Stock.R, Stock.ROM, Stock.H, Stock.N, Stock.W, Stock.Frames
PIN = '32eaf1786695d7ac1e69eb4957cc76dee011664e642710d02acc7ae624ca3ad1'
FORMS = Stock.FORMS
ROUTES = ('mushroom', 'mushroom-suit')
STOCK_SHA = '7d9a087c13e940253c8b4b8da58409517d9ca80704ae2b1a9dff749c09bf5605'
SUITS = {1: 'Super', 2: 'Fire', 3: 'Raccoon', 4: 'Frog', 5: 'Tanooki', 6: 'Hammer'}
TARGET_SUITS = {name: form for form, name in SUITS.items() if form >= 3}


def bindings(raw, form='peach3', route='mushroom-suit', *, mode='easy', suit=None):
    assert isinstance(raw, bytes) and H(raw) == PIN and len(raw) == 2097168, 'Exact installed32eaf178 only'
    assert form in FORMS and route in ROUTES
    assert suit is None or (suit in TARGET_SUITS and route == 'mushroom-suit'), 'Suit targeting requires the Mushroom/suit route'
    assert H(Path(Stock.__file__).read_bytes()) == STOCK_SHA
    q = deepcopy(Stock.bindings(raw, form, 'star', mode=mode))
    baseline = Stock.Beans.inverse(raw)
    ref, bundle, _ = Stock.Shared._metadata(baseline)
    q['ram']['PseudoRandomBitReg'] = W.address(bundle, 'PseudoRandomBitReg')
    keep = ('GameLoop', 'M3Movement', 'M3Step', 'M3PreparePickup',
            'M3CollectPickup', 'HandlePowerUpCollision', 'PlayerHeadCollision')
    q['hooks'] = {name: q['hooks'][name] for name in keep}
    for name in ('M3RisePickup', 'M3Graphics', 'M3DrawWorld'):
        pc, at = W.address(bundle, name), W.location(bundle, name)
        bank = (at - 16) // 8192
        code = raw[at:at + 16]
        assert code == ref[at:at + 16] and at - 16 == bank * 8192 + (pc & 8191)
        q['hooks'][name] = dict(pc=pc, tag=bank | 128, offset=at - 16, hex=code.hex(),
                                bytes=list(code), bank_SHA256=H(raw[16 + bank * 8192:16 + (bank + 1) * 8192]))
    pc, at = W.address(bundle, 'M3PreparePickup'), W.location(bundle, 'M3PreparePickup')
    needle = b'\xad' + (q['ram']['PseudoRandomBitReg'] + 2).to_bytes(2, 'little')
    code = raw[at:at + 128]
    hits = [i for i in range(len(code) - 2) if code[i:i + 3] == needle]
    assert len(hits) == 1
    delta = hits[0]
    assert code[delta:delta + 3] == ref[at + delta:at + delta + 3]
    q['hooks']['M3RNGRead'] = dict(pc=pc + delta, tag=((at - 16) // 8192) | 128,
                                 offset=at + delta - 16, hex=needle.hex(), bytes=list(needle))
    q.update(route=route, item=route, stockKind=0 if route == 'mushroom' else 1,
             blockX=336 if route == 'mushroom' else 1248, blockY=144,
             suit_names=SUITS, logical_item_classifier='owner17/D1=Mushroom; owner17/D2..D6=actual suit',
             literal_fire_only_stamp=0xd2, facade_SHA256=H(Path(__file__).read_bytes()),
             source_stock_facade_SHA256=STOCK_SHA, actual_input_CPU_SHA256=PIN)
    if suit is not None:
        for name in ('GamePauseStatus', 'GamePauseTimer', 'FrameCounter',
                     'M3Native::Player_YVelFrac', 'M3Native::Player_YVel'):
            q['ram'][name] = W.address(bundle, name)
        authenticated = {}
        for name, size in (('HpPauseCold', 96), ('M3HeadDispatch', 128),
                           ('M3Native::Player_JumpFlyFlutter', 192),
                           ('M3Native::Player_ApplyVelocity', 96)):
            at = W.location(bundle, name)
            assert raw[at:at+size] == ref[at:at+size], ('Suit prediction authority changed', name)
            authenticated[name] = H(raw[at:at+size])
        pc, at = W.address(bundle, 'HpPauseCold'), W.location(bundle, 'HpPauseCold')
        bank = (at-16)//8192
        assert at-16 == bank*8192+(pc&8191)
        q['hooks']['TargetPauseInput'] = dict(pc=pc, tag=bank|128, offset=at-16,
                                             hex=raw[at:at+16].hex(), bytes=list(raw[at:at+16]))
        at = W.location(bundle, 'M3Native::Player_RootJumpVel')
        assert raw[at:at+5] == ref[at:at+5] == bytes((200, 0, 2, 4, 8))
        q.update(target_suit=TARGET_SUITS[suit], target_suit_name=suit,
                 target_stamp=0xd0+TARGET_SUITS[suit], pause_wait_limit=512,
                 prediction_code_SHA256=authenticated)
    return q
