"""Publish the tested Excitebike repair as the sole Current/Latest IPS."""
from unittest.mock import patch

import publish_ff_corner_current_1110 as Base
import check_ff_mux_unused_tail_1110 as Mux
from stage_excitebike_powerup_1110 import PIN, PARENT, reconstruct
from deliver_excitebike_powerup_1110 import CANDIDATE, SCRIPT, SCRIPT_PIN

PATCH = 'aa6424bd4603d1b30152a64aa65026dc729dab72334ea420678f577fdf70f79f'
RECEIPTS = ('412ddb541df22140770c8bbf5ddf01188cbb2d0a39ab2a87ba0e155880b461f7',)


class Recipe:
    V1 = Mux.Fix.V1

    @staticmethod
    def proposal(base):
        assert base == Recipe.V1.BASE.read_bytes()
        return reconstruct()


def notes(head):
    return ('Current MMC5 WIP nightly. Apply this sole IPS to clean headered Super Mario Bros. (World).\n\n'
        f'ROM SHA-256: {PIN}\nIPS SHA-256: {PATCH}\nSource commit: {head}\n\n'
        'All100 named entries can start; use the Select access list in docs/character-select-access.md. '
        'Sonic, Jay and Steve still use borrowed prototype moves; Prince and DK Jr. are partial ports.\n\n'
        'Fixes Excitebike freezing after its first earned mushroom. The actual title/menu, authored '
        'mushroom, collection, exactly60 native animation updates and resumed movement passed in Mesen '
        'on both the candidate and installed Downloads ROM. The actual sound-queue write, body CHR, '
        'OAM, palette and HUD were checked. This is not a full-stage or zero-lag claim.\n\n'
        'Retains the prior FF corner/pipe fixes, reduced empty-frame costs and verified Kirby route. '
        'No helper platform locations changed. Original-character integration and broader testing continue.\n')


def main():
    with patch.object(Base, 'PIN', PIN), patch.object(Base, 'PATCH_PIN', PATCH), \
         patch.object(Base, 'OLD_PATCH', 'c562f772312dab68907cfe2dcc8b205af811241a6f505f389c93614c4d534d64'), \
         patch.object(Base, 'RECEIPTS', RECEIPTS), patch.object(Base, 'Fix', Recipe), \
         patch.object(Base, 'CANDIDATE', CANDIDATE), patch.object(Base, 'SCRIPT', SCRIPT), \
         patch.object(Base, 'SCRIPT_PIN', SCRIPT_PIN), \
         patch.object(Base, 'REPORT', Base.R/'docs/qa/excitebike-physical-delivery-1110.md'), \
         patch.object(Base, 'release_body', notes):
        Base.main()


if __name__ == '__main__':
    main()
