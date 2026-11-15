"""Source-check actual FF movement-entry endpoint after real1UP credit."""
import argparse
import json
from pathlib import Path
from unittest.mock import patch

import replay_ff_natural_oneup_after_credit_1114 as Factory
import check_ff_natural_oneup_current_1114 as Previous


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',choices=Factory.IDENTITIES,default='fighter-life');a=p.parse_args()
    raw=Factory.ROM.read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('FF post-credit source checker attempted files/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Previous.Runner.Native,'run',forbid),patch.object(Previous,'Factory',Factory):
        q=Previous.run(raw,a.identity)
    print(json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'FF actual post-credit1UP endpoint remains unqualified'
