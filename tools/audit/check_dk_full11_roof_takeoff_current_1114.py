"""Source-qualify the measured ordinary1506..1510 DK roof takeoff."""
import argparse
import json
from pathlib import Path
from unittest.mock import patch

import replay_dk_full11_roof_takeoff_current_1114 as Factory
import check_dk_full11_roof_geometry_current_1114 as Geometry
import check_dk_full11_latched_current_1114 as Common


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--normal',action='store_true');a=p.parse_args()
    raw=Factory.ROM.read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('DK roof takeoff source checker attempted files/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Common.Runner.Native,'run',forbid):
        if a.normal:
            with patch.object(Common,'Factory',Factory):q=Common.run(raw)
        else:
            with patch.object(Geometry,'Factory',Factory):q=Geometry.run(raw)
    print(json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'Measured DK ordinary roof takeoff remains source-unqualified'
