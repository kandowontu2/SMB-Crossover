"""Run the exact ordinary Lua policy through current compiled CPU, no outputs."""
import argparse,json
from unittest.mock import patch
import replay_wwf_natural_flower_native_1115 as F
import check_smb1_alts_full11_1114 as Runner
import check_shared_world_sprite_images_1114 as Cold

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',choices=F.IDENTITIES,default='hogan');a=p.parse_args()
    raw=F.ROM.read_bytes()
    with patch.object(Runner,'Factory',F),patch.object(Cold,'Factory',F),patch.object(Runner,'cold',Cold.cold):
        q=Runner.run(raw,a.identity,4700)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'The exact ordinary WWF Lua remains source-unqualified'
