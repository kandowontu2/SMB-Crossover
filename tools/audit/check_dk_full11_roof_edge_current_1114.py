"""Actualf11 DK real supported roof-edge route, normal/delayed poll source."""
import argparse
import json
from pathlib import Path
from unittest.mock import patch

import replay_dk_full11_roof_edge_current_1114 as Factory
import check_dk_full11_latched_current_1114 as Previous


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--delayed-polls',action='store_true');a=p.parse_args()
    raw=Factory.ROM.read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('DK roof-edge source checker attempted files/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Previous.Runner.Native,'run',forbid),patch.object(Previous,'Factory',Factory):
        print('DK_ROOF_EDGE_BINDING '+json.dumps(Factory.metadata(raw),separators=(',',':')),flush=True)
        q=Previous.run(raw,delayed_polls=a.delayed_polls)
    print(json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'DK supported roof-edge route remains source-unqualified'
