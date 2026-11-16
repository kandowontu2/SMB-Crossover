"""Run the same first-pipe component gate on the separate cap-support policy."""
from unittest.mock import patch
import check_dkjr_public_low_depart_67_1115 as Gate
import replay_dkjr_public_cap_depart_67_1115 as F

if __name__ == '__main__':
    with patch.object(Gate, 'F', F):
        Gate.main()
