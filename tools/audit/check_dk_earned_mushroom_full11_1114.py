"""Zero-output exact571 DK full route with genuinely earned first mushroom."""
import json
from pathlib import Path
from unittest.mock import patch

import replay_dk_earned_mushroom_full11_1114 as Factory
import check_dk_full11_latched_current_1114 as Common


if __name__=='__main__':
    raw=Factory.ROM.read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('DK earned full route attempted files/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Common.Runner.Native,'run',forbid),patch.object(Common,'Factory',Factory):
        q=Common.run(raw)
    print(json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'Earned DK mushroom full route remains source-unqualified'
