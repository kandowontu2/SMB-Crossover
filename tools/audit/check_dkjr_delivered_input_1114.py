"""Strict delivered1daca normalization with mutable-ROM reads blocked."""
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import current_dkjr_delivered_input_1114 as I


def main():
    raw=I.NIGHTLY.read_bytes();assert sha256(raw).hexdigest()==I.PIN
    real=Path.read_bytes
    blocked={I.NIGHTLY.resolve(),*(
        (I.Common.R/'build'/name/'candidate.nes').resolve()
        for name in ('smb2-flag-native-1113','metal-flower-native-1112','bub-native-1113'))}
    def read(path):
        assert path.resolve()not in blocked,('Mutable ROM dependency',str(path))
        return real(path)
    I.Classic.proposal.cache_clear();I.Classic.allocation.cache_clear();I.Common.bindings.cache_clear()
    with patch.object(Path,'read_bytes',read):
        base,info=I.normalize(raw,kind=I.KIND)
        reset=I.Common.proposal(base)[0]
    rejected=0;corrupt=bytearray(raw);corrupt[I.Classic.SPANS[0][0]]^=1
    for value,kind in ((base,I.KIND),(reset,I.KIND),(bytes(corrupt),I.KIND),(raw,'world-chr-82')):
        try:I.normalize(value,kind=kind)
        except (AssertionError,ValueError):rejected+=1
        else:raise AssertionError(('Wrong delivered input accepted',kind))
    assert rejected==4
    print('DKJR_DELIVERED_INPUT '+json.dumps(dict(passed=True,**info,rejections=rejected,
        mutable_Downloads_flag_metal_reads_blocked=True,outputs_written=0,ROM_written=False),separators=(',',':')),flush=True)


if __name__=='__main__':main()
