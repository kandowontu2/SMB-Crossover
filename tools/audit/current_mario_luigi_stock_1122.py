"""Strict installed 32e Mario/Luigi stock hooks; reference bytes are metadata."""

from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch

import current_ice_stock_binding_1122 as Shared
import repair_contra_force_beans_ground_1122 as Beans

R, ROM, H, N, W, Frames = Shared.R, Shared.ROM, Shared.H, Shared.N, Shared.W, Shared.Frames
PIN = Beans.CANDIDATE
FORMS = {'mario': (0, 0, 'MARIO', 'MarioSourceMovement'),
         'luigi': (8, 1, 'LUIGI', 'LuigiSourceMovement')}
ITEMS = {'1up': 3, 'star': 2}


@lru_cache(maxsize=1)
def metadata_bundle(raw):
    assert isinstance(raw, bytes) and len(raw) == 2097168 and H(raw) == PIN
    baseline = Beans.inverse(raw)
    assert H(baseline) == Shared.PIN
    ref, bundle, _ = Shared._metadata(baseline)
    return baseline, ref, dict(bundle, raw=raw)


def bindings(raw, form='mario', item='1up'):
    assert form in FORMS and item in ITEMS
    baseline, ref, bundle = metadata_bundle(raw)
    q = deepcopy(Shared.bindings(baseline, 'popo', item, mode='easy'))
    q['ram'] = {n: a for n, a in q['ram'].items() if not n.startswith('Ic')}
    for name in ('MarioVariant', 'PlayerScoreDisplay', 'BoundingBox_UL_Corner', 'GuestPowerupActive',
                 'GuestPowerupOld', 'GuestPowerupTarget', 'GuestPowerupAge'):
        q['ram'][name] = W.address(bundle, name)
    keep = ('GameLoop', 'HandlePowerUpCollision', 'PlayerHeadCollision',
            'MarioSourcePowerupCollision', 'LifeCredit')
    q['hooks'] = {n: q['hooks'][n] for n in keep}
    owner, variant, name, movement = FORMS[form]
    for label, symbol in (('GuestMovement', movement),):
        pc, at = W.address(bundle, symbol), W.location(bundle, symbol)
        bank = (at - 16) // 8192
        code = raw[at:at+16]
        assert code == ref[at:at+16], symbol
        assert at - 16 == bank * 8192 + (pc & 8191)
        q['hooks'][label] = dict(pc=pc, tag=bank | 128, offset=at-16,
                                 hex=code.hex(), bytes=list(code))
    for symbol in ('MarioSourceMovement', 'LuigiSourceMovement', 'LuigiSourceMovementBridge'):
        at = W.location(bundle, symbol)
        assert raw[at:at+32] == ref[at:at+32], symbol
    for label, h in q['hooks'].items():
        at = h['offset'] + 16
        code = bytes.fromhex(h['hex'])
        assert raw[at:at+len(code)] == code, label
        bank = h['tag'] & 127
        h['bank_SHA256'] = H(raw[16+bank*8192:16+(bank+1)*8192])
    # The compiled menu graph is retained, with the actual standard slot0.
    navigation = []
    for start in range(32):
        queue, visited = [(start, [])], {start}
        for node, path in queue:
            if node == 0:
                navigation.append(path[0] if path else '')
                break
            for key, edges in q['menu_edges'].items():
                nxt = edges[node]
                if nxt not in visited:
                    visited.add(nxt); queue.append((nxt, path+[key]))
        else:
            raise AssertionError(('Standard roster slot0 unreachable', start))
    q.update(sha=PIN, form=form, key=form, name=name, owner=owner, character=owner,
             variant=variant, select=variant, slot=0, menu_index=0,
             variant_symbol='MarioVariant', mode='easy', mode_value=0,
             item=item, route=item, stockKind=ITEMS[item], navigation=navigation,
             actual_input_CPU_SHA256=PIN, actual_a6_CPU=False,
             source_movement_symbol=movement,
             reference_metadata_only_SHA256=H(ref), Beans_inverse_verified=True,
             facade_SHA256=H(Path(__file__).read_bytes()))
    q.pop('preserved_Ice_domains', None)
    return q


def cold(raw, form):
    config = bindings(raw, form)
    _, _, bundle = metadata_bundle(raw)
    # UI.seed is the retained compiled-menu arena, not a gameplay-state seed.
    with patch.object(N, 'Bus', W.ControllerBus):
        m = W.UI.seed(bundle, 0)
    for _ in range(config['select']):
        W.UI.key(m, 32)
    assert W.UI.menu_name(m)[0] == config['name']
    assert (N.get(m, 'SelectedCharacter'), N.get(m, 'MarioVariant')) == (config['owner'], config['variant'])
    start = W.UI.key(m, 16)
    N.invoke(m, 'NativeRareGameMenuRoutineCore::ChkContinue',
             a=start['A'], x=start['X'], y=start['Y'], p=start['P'])
    # Current Main owns the relocated native pause leaf; the old DBG is metadata.
    import check_contra_force_fast_ingress_1122 as Fast
    old = m.bundle['syms']['PauseRoutine']
    m.bundle = dict(m.bundle, syms=dict(m.bundle['syms'],
        PauseRoutine=dict(old, val=hex(Fast.Layout.NEW_PAUSE))))
    N.invoke(m, 'PauseRoutine', a=0)
    for _ in range(700):
        if tuple(N.get(m, n) for n in ('OperMode', 'OperMode_Task', 'GameEngineSubroutine')) == (1, 3, 8):
            assert N.get(m, 'NumberofLives') == 2 and N.get(m, 'PlayerStatus') == 0
            assert N.get(m, 'CheatInvincible') == N.get(m, 'CheatStartLevel') == 0
            return m
        m.controller_pad = 0
        Frames.frame(m, cold=True)
    raise AssertionError('Actual standard Mario/Luigi cold bound')
