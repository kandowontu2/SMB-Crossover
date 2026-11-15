"""Zero-output source execution of the ordinary Gimmick Flower route."""
import json
from pathlib import Path
from unittest.mock import patch
import replay_gimmick_natural_flower_1114 as F


if __name__=='__main__':
    raw=F.ROM.read_bytes()
    def forbid(*a,**k):raise RuntimeError('Gimmick Flower source attempted file or Mesen output')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(F.Runner.Native,'run',forbid):q=F.run(raw)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'Ordinary Gimmick Flower route remains unqualified'
