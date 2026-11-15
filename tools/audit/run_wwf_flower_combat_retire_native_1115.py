"""Root queue: per-role natural M/F with walking-action retirement."""
import argparse,json
from hashlib import sha256
from pathlib import Path
import replay_wwf_flower_combat_retire_1115 as F
import run_wwf_flower_defense_native_1115 as Runner

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',nargs='+',choices=F.IDENTITIES,required=True);a=p.parse_args()
    Runner.F=F
    print('FACTORY_SHA256 '+sha256(Path(F.__file__).read_bytes()).hexdigest(),flush=True)
    for key in a.identity:
        q=Runner.execute(key);print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
        Runner.validate(q,key)
        assert q['passed'],('Natural per-role M/F remains native-unqualified',key)
