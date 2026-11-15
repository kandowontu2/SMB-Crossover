"""Actualf11 classic DK ordinary released-A roof route; source only."""
import json
from pathlib import Path
from unittest.mock import patch

import replay_dk_full11_release_current_1114 as Factory
import check_dk_full11_current_1114 as Previous


if __name__=='__main__':
    raw=Factory.ROM.read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('DK release successor attempted files/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Previous.Runner.Native,'run',forbid),patch.object(Previous,'Factory',Factory):
        print('DK_RELEASE_BINDING '+json.dumps(Factory.metadata(raw),separators=(',',':')),flush=True)
        q=Previous.contact(raw)
    print(json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'Classic DK released-A route remains source-unqualified'
