"""Exact a6 native bindings for Toad/Peach's authored 1-UP and Star."""

from copy import deepcopy
from pathlib import Path

import current_ice_stock_binding_1122 as Shared
import repair_contra_force_beans_ground_1122 as Beans

R, ROM, H, N, W, Frames = Shared.R, Shared.ROM, Shared.H, Shared.N, Shared.W, Shared.Frames
PIN = Shared.PIN
BEANS_PIN = '32eaf1786695d7ac1e69eb4957cc76dee011664e642710d02acc7ae624ca3ad1'
BEANS_SOURCE_SHA = '0af597f98ca65be0113b68782e70f5671b0af7c6d75db19846e6603936a59c4c'
ALLOWED_PINS = (PIN, BEANS_PIN)
FORMS = {'toad3': (2, 'SMB3 TOAD'), 'peach3': (3, 'SMB3 PEACH')}
ITEMS = {'1up': 3, 'star': 2}
SHARED_SHA = '8197bf702dd57f62389b9c061524f1b5aeec2c262e602fdd544375b07479ae49'
EXTRA_FIELDS = (
    'M3Variant', 'M3Ready', 'M3Form', 'M3Previous', 'M3Fresh', 'M3Growth',
    'M3Poof', 'M3Life', 'MbFloatReady', 'MbFloatExpired', 'MbFloatAnchor',
    'InvPickup', 'InvPickupOwner', 'InvRisePhase', 'BoundingBox_UL_Corner',
    'PlayerScoreDisplay',
)
EXTRA_HOOKS = ('M3Movement', 'M3Step', 'M3PreparePickup', 'M3PickupCollision', 'M3CollectPickup')


def bindings(raw, form='toad3', item='1up', *, mode='easy'):
    assert isinstance(raw, bytes) and len(raw) == 2097168
    actual = H(raw)
    assert actual in ALLOWED_PINS, 'Exact a6 or its qualified Beans-only successor required'
    baseline = raw
    if actual == BEANS_PIN:
        assert H(Path(Beans.__file__).read_bytes()) == BEANS_SOURCE_SHA
        assert Beans.PARENT == PIN and Beans.CANDIDATE == BEANS_PIN
        baseline = Beans.inverse(raw)
        assert H(baseline) == PIN
    assert form in FORMS and item in ITEMS and mode in ('easy', 'hard')
    assert H(Path(Shared.__file__).read_bytes()) == SHARED_SHA
    ref, bundle, _ = Shared._metadata(baseline)
    q = deepcopy(Shared.bindings(baseline, 'popo', item, mode=mode))
    q['ram'] = {name: address for name, address in q['ram'].items() if not name.startswith('Ic')}
    for name in EXTRA_FIELDS:
        q['ram'][name] = W.address(bundle, name)
    assert (q['ram']['M3Variant'], q['ram']['M3Form'], q['ram']['M3Ready']) == (0x5fe4, 0x5f40, 0x5c80)
    keep = ('GameLoop', 'HandlePowerUpCollision', 'PlayerHeadCollision', 'SetupPowerUp',
            'MarioSourcePowerupCollision', 'LifeCredit', 'LifeCreditAfter',
            'StockStarGrant', 'StockOneUpGrant')
    q['hooks'] = {name: q['hooks'][name] for name in keep}
    for name, hook in q['hooks'].items():
        at = 16 + hook['offset'];code = bytes.fromhex(hook['hex'])
        assert raw[at:at + len(code)] == code, ('Actual native stock hook changed', name)
        bank = hook['tag'] & 127
        hook['bank_SHA256'] = H(raw[16 + bank * 8192:16 + (bank + 1) * 8192])
    for name in EXTRA_HOOKS:
        pc, at = W.address(bundle, name), W.location(bundle, name)
        bank = (at - 16) // 8192
        assert at - 16 == bank * 8192 + (pc & 8191)
        code = raw[at:at + 16]
        assert code == ref[at:at + 16], ('SMB3 native hook changed', name)
        q['hooks'][name] = dict(pc=pc, tag=bank | 128, offset=at - 16,
                                hex=code.hex(), bytes=list(code),
                                bank_SHA256=H(raw[16 + bank * 8192:16 + (bank + 1) * 8192]))
    preserved = []
    for bank in (66, 81, 90, 91, 92, 124):
        at = 16 + bank * 8192
        assert raw[at:at + 8192] == ref[at:at + 8192], ('SMB3 native bank changed', bank)
        preserved.append(dict(bank=bank, SHA256=H(raw[at:at + 8192])))
    at, end = 1048592 + 969 * 1024, 1048592 + 1019 * 1024
    assert raw[at:end] == ref[at:end]
    smc_return = W.address(bundle, 'FarcallJmpTarget_SMC') + 3
    assert smc_return == 0x016e
    paths = []
    for start in range(32):
        queue, visited = [(start, [])], {start}
        for node, path in queue:
            if node == 16:
                paths.append(path)
                break
            for direction, edges in q['menu_edges'].items():
                nxt = edges[node]
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append((nxt, path + [direction]))
        else:
            raise AssertionError(('SMB3 roster slot unreachable', start))
    assert q['menu_raw_ids'][16] == 17
    variant, name = FORMS[form]
    prefix = [4, 128, 4, 128, 64] if mode == 'hard' else []
    menu = prefix + [16] + [q['bits'][key] for key in paths[0]] + [32] * variant + [16]
    q.pop('preserved_Ice_domains', None)
    q.update(sha=actual, key=form, form=form, name=name, variant=variant, select=variant,
             character=17, slot=16, menu_index=16, variant_symbol='M3Variant',
             menu=menu, menu_route=paths[0], navigation=[path[0] if path else '' for path in paths],
             stockKind=ITEMS[item], item=item, route=item, smc_return_pc=smc_return,
             preserved_SMB3_domains=preserved, preserved_SMB3_CHR_SHA256=H(raw[at:end]),
             facade_SHA256=H(Path(__file__).read_bytes()), shared_facade_SHA256=SHARED_SHA,
             physical_PRG_only=True, actual_a6_CPU=actual==PIN,
             actual_input_CPU_SHA256=actual, metadata_a6_only_SHA256=PIN,
             Beans_inverse_source_SHA256=BEANS_SOURCE_SHA if actual==BEANS_PIN else None)
    return q
