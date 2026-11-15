"""Exactcf7 unseeded full-route successor and passive first-contact observer."""
import argparse
import json
from pathlib import Path
from unittest.mock import patch

import replay_dk_full11_contact_current_1114 as Factory
import check_dk_full11_current_1114 as Previous


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--metadata',action='store_true');a=p.parse_args()
    raw=Factory.ROM.read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('DK contact successor attempted files/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Previous.Runner.Native,'run',forbid),patch.object(Previous,'Factory',Factory):
        q=Previous.run(raw,metadata=True)if a.metadata else Previous.contact(raw)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not a.metadata:assert q['passed'],'Classic DK contact successor remains source-unqualified'
