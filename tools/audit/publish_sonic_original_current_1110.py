"""Publish the exact Mesen-tested Sonic nightly as the sole Current IPS."""
from hashlib import sha256
from unittest.mock import patch

import check_sonic_original_physical_1110 as Native
import publish_ff_corner_current_1110 as Base

Stage=Native.Stage
PATCH='0584f89085f4470ecd97fd306d9a761ab4bb350d6fdf7caf58ab191e97524405'
PREVIOUS_PATCH='a8b2bd9a2fe1677e87e7119f07b10eac5607fc5e4f6d26d9f2b10c49b90ffd1e'
RECEIPTS=(
    '650eddee8a9a5fef6bfd05d51c36ea99d0abc0f945de5a8dae3118f0a2c23717',
    'bb782212c48763783d77a94c6df80d6471117aa4ec0111330371a3110373b1da',
    '0185f0fc9a35557ace4d6f843a62d33e41dd4bb7032645c1bdd96693241e5496')
REPORT=Stage.R/'docs/qa/sonic-original-delivery-1110.md'


class Recipe:
    V1=Stage.Portrait.Original.WWF.Previous.Thomas.Ex.Mux.Fix.V1

    @staticmethod
    def proposal(base):
        assert base==Recipe.V1.BASE.read_bytes()
        return Stage.reconstruct()


def notes(head):
    return ('Current MMC5 WIP nightly. Apply this IPS to clean headered Super Mario Bros. (World).\n\n'
        f'ROM SHA-256: {Native.PIN}\nIPS SHA-256: {PATCH}\nSource commit: {head}\n\n'
        'Sonic now uses original Master System movement. Highlight Mr. Gimmick in row 4, column 2 and '
        'press Select three times. The cycle is Mr. Gimmick, Bub, Bob, Sonic. All 100 names remain startable.\n\n'
        'Both the candidate and installed Downloads ROM passed Mesen checks for the select and lives '
        'portraits, opening movement, and full 1-1 through the flag, castle walk and underground 1-2. '
        'The full route used 17 jump requests and zero helper platforms, with both lives at the end. '
        'Sonic still has a temporary gameplay pose and substantial lag. Rings, the full animation set and '
        'original audio remain in development.\n\n'
        'Includes the tested WWF, Thomas and Excitebike pickup fixes. Verification details are in '
        'docs/qa/sonic-original-delivery-1110.md.\n')


def main():
    report=REPORT.read_bytes()
    for script,pin in ((Native.PORTRAITS,Native.PORTRAITS_PIN),(Native.OPENING,Native.OPENING_PIN)):
        assert pin.encode() in report and sha256(script.read_bytes()).hexdigest()==pin
    with patch.object(Base,'PIN',Native.PIN),patch.object(Base,'PATCH_PIN',PATCH), \
         patch.object(Base,'OLD_PATCH',PREVIOUS_PATCH),patch.object(Base,'RECEIPTS',RECEIPTS), \
         patch.object(Base,'Fix',Recipe),patch.object(Base,'CANDIDATE',Stage.CANDIDATE), \
         patch.object(Base,'SCRIPT',Native.FULL_STAGE),patch.object(Base,'SCRIPT_PIN',Native.FULL_STAGE_PIN), \
         patch.object(Base,'REPORT',REPORT),patch.object(Base,'release_body',notes):
        Base.main()


if __name__=='__main__':main()
