"""Root queue: keep exact gameplay policy and observe actual cue writers."""
import argparse,json
from hashlib import sha256
from pathlib import Path
import replay_wwf_flower_cue_observed_1115 as F
import run_wwf_flower_defense_native_1115 as Runner

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',nargs='+',choices=F.IDENTITIES,default=['andre']);a=p.parse_args()
    Runner.F=F
    print('FACTORY_SHA256 '+sha256(Path(F.__file__).read_bytes()).hexdigest(),flush=True)
    for key in a.identity:
        q=Runner.execute(key);print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
        assert q['passed'],('Observed-cue natural M/F remains native-unqualified',key)
        r=q['receipt'];assert r['terminal']['power']==2 and r['terminal']['lives']==2
        for k in ('0','1'):
            item=r['items'][k]
            assert item['ticks']==60 and item['resumed']==25 and item['collected']['cue_producer']['value']&32
