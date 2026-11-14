"""Pin explicit421/82 review normalization and reject mislabeled inputs."""
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import current_dkjr_review_input_1114 as I


def main():
    actual=I.NIGHTLY.read_bytes();digest=sha256(actual).hexdigest()
    if digest==I.Reset.PIN:
        base=actual;reset=I.Reset.proposal(base)[0]
    else:
        assert digest==I.Reset.CANDIDATE
        reset=actual;base=I.Reset.inverse(reset)
    old=Path.read_bytes
    blocked={I.NIGHTLY.resolve(),
        (I.Reset.R/'build/smb2-flag-native-1113/candidate.nes').resolve(),
        (I.Reset.R/'build/metal-flower-native-1112/candidate.nes').resolve()}
    def read(path):
        assert path.resolve()not in blocked,('Mutable ROM dependency',str(path))
        return old(path)
    I.Reset.bindings.cache_clear()
    with patch.object(Path,'read_bytes',read):
        a,aq=I.normalize(base,kind='hidden-421');b,bq=I.normalize(reset,kind='world-chr-82')
        assert a==b==base
    rejected=0
    unknown=bytearray(reset);unknown[16]^=1
    for raw,kind in ((base,'world-chr-82'),(reset,'hidden-421'),
        (reset,'unknown'),(bytes(unknown),'world-chr-82')):
        try:I.normalize(raw,kind=kind)
        except (AssertionError,ValueError):rejected+=1
        else:raise AssertionError(('Unknown/mislabeled input accepted',kind))
    assert rejected==4
    print('DKJR_REVIEW_INPUT '+json.dumps(dict(passed=True,
        actual_inspected_Downloads_SHA256=digest,known_inputs=[aq,bq],rejections=rejected,
        normalization_with_Downloads_flag_and_metal_reads_blocked=True,
        outputs_written=0,ROM_written=False,DK_composition_performed=False,
        scope='Explicit input normalization to frozen421 model only. Known pure82 input uses the already granted29B root proposal; no DK merge or delivery is authorized by this boundary.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
