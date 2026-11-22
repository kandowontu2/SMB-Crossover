"""Strict installed a6 Sonic stock-item bindings; reference images stay in RAM.

The returned dictionary uses the SONIC_CONFIG layout of the retained native
ceiling observer.  This module produces neither controllers nor ROM files and
does not launch an emulator.  Older images supply symbols only; callers must
execute the exact supplied a6 image.
"""

from copy import deepcopy
from functools import lru_cache
from pathlib import Path

import check_contra_force_combined_palette_1122 as Combined
import compose_rogue_hud_scene_dirty_cb95_1116 as Hud
import compose_rogue_missile_9826_1116 as Missile
import current_sonic_mini_owner_9826_1116 as Sonic
import replay_sonic_mini_owner_9826_1116 as Frozen


R, ROM, H, N, W, Frames = Sonic.R, Sonic.ROM, Sonic.H, Sonic.N, Sonic.W, Sonic.Frames
PIN = 'a6d91e368657a0ee1458391542e98adafcec45991ebecbe4521a648513cfa4df'
FORMS = Sonic.FORMS
ITEMS = {'flower': 1, 'star': 2}
SOURCE_PINS = {
    Combined: '858729e9d3528ffdb35c80058f23b3e502165458f7a0449a580605160f18f85b',
    Hud: 'd7b924cbba68c99a2c3db6ec23e2b41e47b8ceb9e74476af3bcccc2bda52aa45',
    Missile: 'f38d2e2859631b1156ad5805d29a481a89f6e68e77b17a4f509de8af7d19d3a1',
    Sonic: 'a910664c86de7a1fdd4c0fbdf6bd562a7f7c334ea439f64704d490ec97f40339',
    Frozen: 'd7fd8fa9a5def94ed348122eba57404b8f00cc5689100e290ada029aefeacb0e',
}
EXTRA_FIELDS = (
    'StarInvincibleTimer', 'AreaMusicQueue', 'PlayerSize', 'GuestPowerupActive',
    'GuestPowerupAge', 'GuestPowerupTarget', 'PlayerScoreDisplay',
)
EXTRA_HOOKS = (
    'SetupPowerUp', 'GuestBeginPowerup', 'GuestPowerupUpdate',
    'SetupFloateyNumber', 'FloateyNumbersCore',
)
REQUIRED_HOOKS = (
    'GameLoop', 'SonicHostMain', 'OriginalFrame', 'PlayerHeadCollision',
    'HandlePowerUpCollision',
)


@lru_cache(maxsize=1)
def reference(raw):
    """Recover exact 9826 metadata, without rereading the mutable nightly."""
    assert isinstance(raw, bytes) and len(raw) == 2097168 and H(raw) == PIN, 'Exact installed a6 only'
    for module, expected in SOURCE_PINS.items():
        assert H(Path(module.__file__).read_bytes()) == expected, module.__name__
    assert Combined.COMBINED_SHA == PIN and Combined.BASE_SHA == Hud.CANDIDATE
    parent79fd = Combined.comparison_base(raw)
    parentcb95 = Hud.inverse(parent79fd)
    parent9826 = Missile.inverse(parentcb95)
    assert H(parent9826) == Sonic.PIN == Missile.PARENT
    return parent9826


def bindings(raw, form, item):
    """Return authenticated native/physical-work-RAM hooks for one fresh case."""
    assert form in FORMS and item in ITEMS, 'Sonic/Super and Flower/Star only'
    ref = reference(raw)
    source = Sonic.bindings(ref)
    bundle = source['bundle']
    q = deepcopy(Frozen.bindings(ref, form))

    # The entire Sonic execution, metadata, ring, feedback and both art domains
    # are preserved, as is the full cookie installed into RAM2 and RAM3.
    foundation = Sonic.Previous.Previous
    for row in source['packet_pages']:
        at = foundation.CHR + row['page'] * 1024
        assert raw[at:at + 1024] == ref[at:at + 1024]
        assert H(raw[at:at + 1024]) == row['SHA256']
    cookie = raw[1034472:1034488]
    assert cookie == source['cookie'] == Sonic.COOKIE
    assert q['cookie'] == cookie.hex()

    for name in EXTRA_FIELDS:
        q['ram'][name] = W.address(bundle, name)
    for name in EXTRA_HOOKS:
        at, pc = W.location(bundle, name), W.address(bundle, name)
        expected = ref[at:at + 32]
        assert raw[at:at + len(expected)] == expected, name
        q['hooks'][name] = dict(pc=pc, tag=((at - 16) // 8192) | 128,
                                offset=at - 16, hex=expected.hex())

    for name, hook in q['hooks'].items():
        expected = bytes.fromhex(hook['hex'])
        tag, pc = hook['tag'], hook['pc']
        if tag >= 128:
            bank = tag & 127
            assert hook['offset'] == bank * 8192 + (pc & 8191)
            at = 16 + hook['offset']
            # a6 changes Main's entry veneer.  comparison_base() has already
            # authenticated the complete forward composition against raw.
            if name != 'GameLoop':
                assert raw[at:at + len(expected)] == expected, name
            hook['hex'] = raw[at:at + len(expected)].hex()
            hook['bank_SHA256'] = H(raw[16 + bank * 8192:16 + (bank + 1) * 8192])
        else:
            assert tag in (2, 3)
            assert hook['offset'] == tag * 8192 + (pc & 8191)
            assert source['loaded'](pc)[:len(expected)] == expected, name
        assert len(bytes.fromhex(hook['hex'])) == len(expected)

    assert all(name in q['hooks'] for name in REQUIRED_HOOKS)
    assert q['select'] == FORMS[form][0] and q['name'] == FORMS[form][1]
    assert q['CHR'] == FORMS[form][2]
    q.pop('actual_a2_CPU', None)
    q.pop('actual_f7_CPU', None)
    q.update(sha=PIN, form=form, item=item, stockKind=ITEMS[item],
             actual_a6_CPU=True, actual_CPU_bytes_retained=True,
             reference9826_metadata_only_SHA256=Sonic.PIN,
             facade_SHA256=H(Path(__file__).read_bytes()),
             metadata_facade_SHA256=SOURCE_PINS[Sonic],
             controller_only_required=True, no_files_or_emulator=True)
    return q
