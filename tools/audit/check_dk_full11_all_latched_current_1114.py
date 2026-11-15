"""Source full route for ordinary DK jump delivery under normal/delayed polls."""
import argparse
import json
from pathlib import Path
from unittest.mock import patch

import replay_dk_full11_all_latched_current_1114 as Factory
import check_dk_full11_latched_current_1114 as Previous


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--delayed-polls',action='store_true');a=p.parse_args()
    raw=Factory.ROM.read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('DK all-jump source gate attempted files/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Previous.Runner.Native,'run',forbid),patch.object(Previous,'Factory',Factory):
        print('DK_ALL_LATCH_BINDING '+json.dumps(Factory.metadata(raw),separators=(',',':')),flush=True)
        q=Previous.run(raw,delayed_polls=a.delayed_polls)
    print(json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'DK all-jump admission route remains source-unqualified'
