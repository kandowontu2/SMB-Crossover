"""Publish only the all-six tested, Downloads-repeated WWF nightly."""
from unittest.mock import patch

import publish_ff_corner_current_1110 as Base
import stage_wwf_role_palette_1110 as Stage
from check_wwf_physical_powerups_1110 import CANDIDATE,SCRIPT,SCRIPT_PIN

PATCH='a8b2bd9a2fe1677e87e7119f07b10eac5607fc5e4f6d26d9f2b10c49b90ffd1e'
RECEIPTS=(
    'b4cb7d292d80b03fd6dcf749a1592faf408a39abda7aa873c7e05517a86d3065',
    'ccad3c9cfbd6cf2513346c194910934b3b18e1b6e6de801292905aa48d9432bf',
    '2accb9e826bba6b30a3c6ce36a658d7def36b343052636eba411b2d3585c752f',
    '1ca220c3a624077c17dcf7114090375fa11826d5eef659dd39bf4f03c948a674',
    '5b22883301a0ed6326f0c3bac3061c40464249c4444e070a1aaf98bc091c5c08',
    'c2acfc6269a15ab9f38e6604d3f902abcacbdc284bd5157941f7320c79210730')


class Recipe:
    V1=Stage.Previous.Thomas.Ex.Mux.Fix.V1

    @staticmethod
    def proposal(base):
        assert base==Recipe.V1.BASE.read_bytes()
        return Stage.reconstruct()


def notes(head):
    return ('Current MMC5 WIP nightly. Apply the sole IPS to clean headered Super Mario Bros. (World).\n\n'
        f'ROM SHA-256: {Stage.PIN}\nIPS SHA-256: {PATCH}\nSource commit: {head}\n\n'
        'All 100 named entries can start. Several additions remain partial ports or borrowed prototypes. '
        'The Select access list is in docs/character-select-access.md. Sonic is still Mario Select10 in this nightly.\n\n'
        'Fixes native mushroom collection/powerup recovery for all six WWF wrestlers and the shared '
        'sprite palette routine overwriting their secondary colors with Hogan\'s. All six pass actual '
        'Mesen title/menu/authored-block/mushroom/60-update/recovery tests with original art and colors, '
        'and both lives. The installed Downloads ROM independently repeats Hogan. '
        'SMB tier armor is an interim adaptation; original WWF endurance/gear, full stages and '
        'remaining pickups are unfinished. Existing helper platforms and their controls are unchanged.\n\n'
        'Retains Thomas/Excitebike pickup fixes, FF collision/performance repairs and Kirby fixes. '
        'Original Sonic/Prince integration and broader roster testing continue.\n')


def main():
    with patch.object(Base,'PIN',Stage.PIN),patch.object(Base,'PATCH_PIN',PATCH), \
         patch.object(Base,'OLD_PATCH','8ad06ee63a73991830b26bb9bd9792f33fede4b4c6b3ba91b0afda11febccc5c'), \
         patch.object(Base,'RECEIPTS',RECEIPTS),patch.object(Base,'Fix',Recipe), \
         patch.object(Base,'CANDIDATE',CANDIDATE),patch.object(Base,'SCRIPT',SCRIPT), \
         patch.object(Base,'SCRIPT_PIN',SCRIPT_PIN), \
         patch.object(Base,'REPORT',Stage.R/'docs/qa/wwf-pickup-palette-delivery-1110.md'), \
         patch.object(Base,'release_body',notes):
        Base.main()


if __name__=='__main__':main()
