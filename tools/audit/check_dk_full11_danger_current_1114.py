"""Actualf11 ordinary classic-DK full route, passive contact; zero outputs."""
import argparse
import json
from pathlib import Path
from unittest.mock import patch

import replay_dk_full11_danger_current_1114 as Factory
import check_dk_full11_current_1114 as Previous


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--metadata',action='store_true');a=p.parse_args()
    raw=Factory.ROM.read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('DK danger successor attempted files/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Previous.Runner.Native,'run',forbid),patch.object(Previous,'Factory',Factory):
        print('DK_DANGER_BINDING '+json.dumps(Factory.metadata(raw),separators=(',',':')),flush=True)
        q=Previous.run(raw,metadata=True)if a.metadata else Previous.contact(raw)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not a.metadata:assert q['passed'],'Classic DK danger successor remains source-unqualified'
