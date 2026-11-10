"""Publish the exact Prince/Sonic replayed nightly as the sole Current IPS."""
from hashlib import sha256
from unittest.mock import patch

import deliver_prince_sonic_transport_1110 as Native
import publish_ff_corner_current_1110 as Base

Stage = Native.Stage
PATCH = '92527edf832ecb5349c3c3bfc568914a7fae3e746c5dc9982886b296ea9821cb'
PREVIOUS_PATCH = '0584f89085f4470ecd97fd306d9a761ab4bb350d6fdf7caf58ab191e97524405'
RECEIPTS = (
    '07216d828e974a8dead673eed93021fb10873bd53b5c562b7ed8bb46dcd78b95',
    '410dd288da42744b8c300bf3be2a45bd752e7e1d2dee7e8cf5abab1f46478993',
)
REPORT = Stage.R/'docs/qa/prince-native-pipe-gap-delivery-1110.md'


class Recipe:
    V1 = Stage.Transport.Stage.WWF.Previous.Thomas.Ex.Mux.Fix.V1

    @staticmethod
    def proposal(base):
        assert base == Recipe.V1.BASE.read_bytes()
        return Stage.reconstruct()


def notes(head):
    return ('Current MMC5 WIP nightly. Apply this IPS to clean headered Super Mario Bros. (World).\n\n'
        f'ROM SHA-256: {Stage.PIN}\nIPS SHA-256: {PATCH}\nSource commit: {head}\n\n'
        'Prince of Persia is one Select press from Excitebike. His original jump and climb now take him '
        'across the first four pipes and two gaps in 1-1 with both lives and zero helper platforms. '
        'Mesen verified this route on the candidate and installed Downloads ROM. Later terrain, '
        'enemy encounters, and powerups remain in testing.\n\n'
        'Sonic remains three Select presses from Mr. Gimmick. Both builds repeated his full 1-1 clear '
        'into underground 1-2 with original Master System movement. All 100 names remain available. '
        'See docs/qa/prince-native-pipe-gap-delivery-1110.md for verification.\n')


def main():
    assert sha256(Native.SONIC.read_bytes()).hexdigest() == Native.SONIC_PIN
    assert Native.SONIC_PIN.encode() in REPORT.read_bytes()
    with patch.object(Base, 'PIN', Stage.PIN), patch.object(Base, 'PATCH_PIN', PATCH), \
         patch.object(Base, 'OLD_PATCH', PREVIOUS_PATCH), patch.object(Base, 'RECEIPTS', RECEIPTS), \
         patch.object(Base, 'Fix', Recipe), patch.object(Base, 'CANDIDATE', Native.CANDIDATE), \
         patch.object(Base, 'SCRIPT', Native.PRINCE), patch.object(Base, 'SCRIPT_PIN', Native.PRINCE_PIN), \
         patch.object(Base, 'REPORT', REPORT), patch.object(Base, 'release_body', notes):
        Base.main()


if __name__ == '__main__':
    main()
