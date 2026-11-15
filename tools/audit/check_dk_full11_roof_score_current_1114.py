"""Zero-output ordinary/delayed exact571 DK full route; no emulator."""
import argparse
import json
from pathlib import Path
from unittest.mock import patch

import replay_dk_full11_roof_score_current_1114 as Factory
import check_dk_full11_latched_current_1114 as Common


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--delayed-polls',action='store_true');a=p.parse_args()
    raw=Factory.ROM.read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('DK exact571 source checker attempted files/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Common.Runner.Native,'run',forbid),patch.object(Common,'Factory',Factory):
        q=Common.run(raw,delayed_polls=a.delayed_polls)
    # Keep the full receipt hash and meaningful launch/roof witnesses without
    # repeating32 already frozen first-launch rows in every stdout receipt.
    q['receipt'].pop('jump_launch_trace',None)
    print(json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'Exact571 measured DK roof route remains source-unqualified'
