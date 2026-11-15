"""Passive actualf11/f02 staircase cells; unchanged controls, bounded window."""
import json
from pathlib import Path
from unittest.mock import patch

import replay_dk_full11_release_current_1114 as Factory
import check_dk_full11_current_1114 as Previous


if __name__=='__main__':
    raw=Factory.ROM.read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('DK stair observer attempted files/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Previous.Runner.Native,'run',forbid),patch.object(Previous,'Factory',Factory):
        q=Previous.contact(raw,staircase=True)
    print('DK_STAIR_WINDOW '+json.dumps(q,separators=(',',':')),flush=True)
    assert q.get('diagnostic_window_complete')and not q['full_route_passed']
