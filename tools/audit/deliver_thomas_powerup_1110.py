"""Deliver the tested Thomas repair through the existing no-backup transaction."""
from unittest.mock import patch

import deliver_excitebike_powerup_1110 as Base
import stage_thomas_powerup_1110 as T

CANDIDATE = T.R/'build/thomas-powerup-native-1110/candidate.nes'
SCRIPT = T.R/'tools/playthroughs/thomas_earned_powerup_stdout_1110_v3.lua'
SCRIPT_PIN = '7b0c6c7e9962a4edb867210853da5d5c78b7052778c041904d9c8d60e4a96320'


def main():
    with patch.object(Base, 'PIN', T.PIN), patch.object(Base, 'PARENT', T.PARENT), \
         patch.object(Base, 'reconstruct', T.reconstruct), \
         patch.object(Base, 'CANDIDATE', CANDIDATE), patch.object(Base, 'SCRIPT', SCRIPT), \
         patch.object(Base, 'SCRIPT_PIN', SCRIPT_PIN), patch.object(Base, 'EXPECTED_X', 418):
        Base.main()


if __name__ == '__main__':
    main()
