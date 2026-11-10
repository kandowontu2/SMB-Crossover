"""Use the frozen physical route/delivery contract for the source-qualified mux."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch

import check_ff_physical_routes_stdout_1110 as Base
import check_ff_mux_unused_tail_1110 as Mux

PIN = 'a5c54d7624ee961f11b45598ca7cf7fecc24de6ee87d8e8aa70dad55834f2eaa'
PARENT = '96e09ab1b67a7c75b89d49219e8e529582b9a05b7dd82dd3cd570fdb239212bd'


class Recipe:
    V1 = Mux.Fix.V1
    proposal = staticmethod(Mux.proposal)


def main():
    assert sha256(Path(Base.__file__).read_bytes()).hexdigest() == '186da49258ab74ab5395dd516cfcc775bd0cab8954e297f2c111c0f2c606b833'
    with patch.object(Base, 'PIN', PIN), patch.object(Base, 'PARENT', PARENT), \
         patch.object(Base, 'CANDIDATE', Base.R/'build/ff-mux-performance-native-1110/candidate.nes'), \
         patch.object(Base, 'Fix', Recipe):
        Base.main()


if __name__ == '__main__':
    main()
