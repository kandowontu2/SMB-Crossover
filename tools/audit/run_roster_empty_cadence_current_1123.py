"""Run the established empty-opening cadence observer on the current nightly."""

from unittest.mock import patch

import compose_dkjr_shinobi_1123 as DK
import compose_shinobi_pickups_1123 as Shinobi
import install_mega_giant_item_semantics_1123 as Mega
import repair_goku_hidden_head_1123 as Goku
import run_arthur_restored_cache_native_1123 as Arthur
import run_dkjr_flower_draw_native_1123 as Flower
import run_roster_empty_cadence_1122 as Previous


def reference(raw):
    import compose_donkey_side_early_1123 as EarlyDonkey
    import compose_donkey_side_shortcut_1123 as Donkey
    import compose_karnov_side_route_1123 as Karnov
    import compose_kirby_spiny_sound_1123 as Needles
    import compose_prince_epoch_current_1123 as Epoch
    import compose_prince_side_current_1123 as Side

    observed = raw
    if Previous.Timing.H(raw) == Karnov.CANDIDATE:
        raw = Karnov.inverse(raw)
    if Previous.Timing.H(raw) == Needles.CANDIDATE:
        raw = Needles.inverse(raw)
    if Previous.Timing.H(raw) == EarlyDonkey.CANDIDATE:
        raw = EarlyDonkey.inverse(raw)
    if Previous.Timing.H(raw) == Donkey.CANDIDATE:
        raw = Donkey.inverse(raw)
    if Previous.Timing.H(raw) == Side.CORRECTED:
        raw = Side.inverse(raw)
    if Previous.Timing.H(raw) == Epoch.PARENT:
        raw = Epoch.Reach.recover_parent(raw)
    assert Previous.Timing.H(raw) == Mega.CANDIDATE
    # The older inverses call their own reference resolver during validation.
    with patch.object(Previous, 'cadence_reference', OLD_REFERENCE):
        image = Mega.recover_parent(raw)
        image = DK.recover_parent(image)
        image = Shinobi.recover_parent(image)
        image = Goku.recover_parent(image)
        image = Arthur.recover_parent(image, Previous.Timing.SHARED)
        image = Flower.without_flower(image)
        baseline = OLD_REFERENCE(image)

    # These are the three fixed-bank PCs used for the physical Main witness.
    # Verify their instruction bytes against the observer's original image.
    for pc in (0x82D9, 0x82BE, 0x82D0):
        offset = 16 + 126 * 8192 + (pc & 8191)
        assert observed[offset:offset + 16] == baseline[offset:offset + 16]
    return baseline


OLD_REFERENCE = Previous.cadence_reference
OLD_CONTROLLER = Previous.controller
LONG_WALK = {
    'PRINCE PERSIA', 'HULK HOGAN', 'TED DIBIASE', 'BAM BAM BIGELOW',
    'HONKY TONK MAN', 'RANDY SAVAGE', 'ANDRE THE GIANT',
}


def controller(raw, row):
    text = OLD_CONTROLLER(raw, row)
    if row['name'] not in LONG_WALK:
        return text

    # The Prince and wrestlers can still be at their starting pixel after
    # 16 Right updates. Keep the standing sample and let acceleration finish.
    for old, new in (('ticks<64', 'ticks<96'), ('ticks==64', 'ticks==96'),
                     ('ticks>=64', 'ticks>=96'), ('Right16', 'Right48'),
                     ('64 actual Main completions', '96 actual Main completions'),
                     ('empty64-Main', 'empty96-Main')):
        assert old in text
        text = text.replace(old, new)
    Previous.LuaRuntime().compile(text)
    return text


if __name__ == '__main__':
    with patch.multiple(Previous, cadence_reference=reference, controller=controller):
        Previous.main()
