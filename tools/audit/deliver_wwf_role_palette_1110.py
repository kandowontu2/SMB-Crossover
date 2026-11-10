"""Install all-six tested WWF pickup/palette fixes and repeat Hogan in Downloads."""
from unittest.mock import patch

import deliver_excitebike_powerup_1110 as Base
import stage_wwf_role_palette_1110 as Stage
from check_wwf_physical_powerups_1110 import CANDIDATE,SCRIPT,SCRIPT_PIN


def main():
    with patch.object(Base,'PIN',Stage.PIN),patch.object(Base,'PARENT',Stage.PARENT), \
         patch.object(Base,'reconstruct',Stage.reconstruct),patch.object(Base,'CANDIDATE',CANDIDATE), \
         patch.object(Base,'SCRIPT',SCRIPT),patch.object(Base,'SCRIPT_PIN',SCRIPT_PIN), \
         patch.object(Base,'EXPECTED_X',419):
        Base.main()


if __name__=='__main__':main()
