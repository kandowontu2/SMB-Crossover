"""Publish the tested Thomas nightly as the sole Current/Latest IPS."""
from unittest.mock import patch

import publish_ff_corner_current_1110 as Base
import stage_thomas_powerup_1110 as T
import stage_excitebike_powerup_1110 as Ex
from deliver_thomas_powerup_1110 import CANDIDATE, SCRIPT, SCRIPT_PIN

PATCH = '8ad06ee63a73991830b26bb9bd9792f33fede4b4c6b3ba91b0afda11febccc5c'
RECEIPTS = ('592d77d0fa34dd2e5975f473b8b611a457fac94cd806663949ae90bb2dcf444a',)


class Recipe:
    V1 = Ex.Mux.Fix.V1

    @staticmethod
    def proposal(base):
        assert base == Recipe.V1.BASE.read_bytes()
        return T.reconstruct()


def notes(head):
    return ('Current MMC5 WIP nightly. Apply this sole IPS to clean headered Super Mario Bros. (World).\n\n'
        f'ROM SHA-256: {T.PIN}\nIPS SHA-256: {PATCH}\nSource commit: {head}\n\n'
        'All 100 named entries can start. The Select access list is in docs/character-select-access.md. '
        'Several additions remain partial ports or use borrowed prototype moves.\n\n'
        'Fixes Thomas ignoring mature mushrooms and his rejected powerup-animation update. '
        'Actual Mesen runs on both the candidate and installed Downloads ROM select Thomas, bump '
        'the authored block using his original jump, collect the mushroom, finish all 60 native '
        'updates and resume moving with both lives. Original OAM, consumed CHR pages, palette, HUD '
        'and the actual pickup sound-queue write are checked. Full upgrades, stages and performance '
        'remain unfinished. His existing helper platforms keep their coordinates.\n\n'
        'Retains the Excitebike pickup fix, FF collision/performance repairs and Kirby fixes. '
        'Original-character integration and broader testing continue.\n')


def main():
    with patch.object(Base, 'PIN', T.PIN), patch.object(Base, 'PATCH_PIN', PATCH), \
         patch.object(Base, 'OLD_PATCH', 'aa6424bd4603d1b30152a64aa65026dc729dab72334ea420678f577fdf70f79f'), \
         patch.object(Base, 'RECEIPTS', RECEIPTS), patch.object(Base, 'Fix', Recipe), \
         patch.object(Base, 'CANDIDATE', CANDIDATE), patch.object(Base, 'SCRIPT', SCRIPT), \
         patch.object(Base, 'SCRIPT_PIN', SCRIPT_PIN), \
         patch.object(Base, 'REPORT', T.R/'docs/qa/thomas-physical-delivery-1110.md'), \
         patch.object(Base, 'release_body', notes):
        Base.main()


if __name__ == '__main__':
    main()
