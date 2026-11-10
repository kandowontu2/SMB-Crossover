"""Publish only the physically tested FF optimization, retaining one Current IPS."""
from unittest.mock import patch
import publish_ff_corner_current_1110 as Base
import check_ff_mux_unused_tail_1110 as Mux

PIN = 'a5c54d7624ee961f11b45598ca7cf7fecc24de6ee87d8e8aa70dad55834f2eaa'
PATCH = 'c562f772312dab68907cfe2dcc8b205af811241a6f505f389c93614c4d534d64'
RECEIPTS = (
    '084988b4a3d0c2ecc4f396ed317fc400cb25837a75efe9e383e165eaf2026b22',
    '760cacad47677ce4981a92e299e01de229d683e4f67f5367cc7ed380f8b607fc',
    '8b8156d5dc431d66ad4ffe56cd4844eac1bdfd46d1edc8c97138223b06ce1a85',
    'ec4b84212c32f6ff2634d309085107d46570c88f9680bf99d4762d9c415a86e5')


class Recipe:
    V1 = Mux.Fix.V1
    proposal = staticmethod(Mux.proposal)


def notes(head):
    return ('Current MMC5 WIP nightly. Apply this sole IPS to clean headered Super Mario Bros. (World).\n\n'
        f'ROM SHA-256: {PIN}\nIPS SHA-256: {PATCH}\nSource commit: {head}\n\n'
        'All100 named entries remain startable; some added characters still use borrowed prototype moves.\n\n'
        'Includes FF staircase/pipe repairs and two FF optimizations: remove duplicate same-entry guards '
        'and streamline unused OAM attribute clearing. All four classes earned mushroom and flower, '
        'used their upgraded attack, cleared1-1 and entered underground1-2 without injury in actual Mesen. '
        'The installed Downloads ROM repeated the full run.\n\n'
        'A cold empty-area test runs80 updates in119 video frames versus159 on the earlierc10 baseline; '
        'zero-completion frames fall79 to39. This is an improvement, not60fps. Heavy FF lag remains. '
        'No enemy-loader, firebar, visible-body, projectile or input pass was skipped. '
        'The dense one-unused-sprite case costs8 extra cycles. No helper locations changed.\n\n'
        'Original Sonic/Prince integration and remaining full-roster stage/powerup review continue.\n')


def main():
    with patch.object(Base, 'PIN', PIN), patch.object(Base, 'PATCH_PIN', PATCH), \
         patch.object(Base, 'OLD_PATCH', '0a1960fecf87202e175a26004e6b8f384ff93fdb40fffd1ed582fbc28fd57ab0'), \
         patch.object(Base, 'RECEIPTS', RECEIPTS), patch.object(Base, 'Fix', Recipe), \
         patch.object(Base, 'CANDIDATE', Base.R/'build/ff-mux-performance-native-1110/candidate.nes'), \
         patch.object(Base, 'REPORT', Base.R/'docs/qa/ff-mux-physical-delivery-1110.md'), \
         patch.object(Base, 'release_body', notes):
        Base.main()


if __name__ == '__main__':
    main()
