"""Actualf11 ordinary DK early landing/jump and passive head/contact gate."""
import json
from pathlib import Path
from unittest.mock import patch

import replay_dk_full11_landing_current_1114 as Factory
import check_dk_full11_current_1114 as Previous


if __name__=='__main__':
    raw=Factory.ROM.read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('DK landing successor attempted files/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Previous.Runner.Native,'run',forbid),patch.object(Previous,'Factory',Factory):
        print('DK_LANDING_BINDING '+json.dumps(Factory.metadata(raw),separators=(',',':')),flush=True)
        q=Previous.contact(raw)
    print(json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'Classic DK early landing/jump remains source-unqualified'
