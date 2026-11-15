"""Root current7a80 full Prince route with actual fresh-step admissions."""
from hashlib import sha256
from pathlib import Path
import json
import replay_prince_full_fresh_current_1115 as F
import run_prince_sword_chain_native_1115 as Runner

FACTORY='77729f1c83d5bbf52b23319ecb3a51ce9b4ac48ea6f68c9baa86c6ec05edb1ba'
LUA='53c107fec29692356caa88d727fb64aea096c39f0220be2a5749da81e01b8235'
PIN='7a80f0f37e316436be0825bbd6fd9d372af6b0b7741f84ea87356282033d9b79'

if __name__=='__main__':
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==FACTORY
    Runner.F=F;Runner.FACTORY=FACTORY;Runner.PIN=PIN
    q=Runner.execute();print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['script_SHA256']==LUA and q['passed'],'Current Prince full fresh-step route remains native-unqualified'
    r=q['receipt'];c=r['new_candidate_readback'];s=r['terminal']
    assert c['both_cookies']and c['bytes']==4027 and c['PC']==0xbbc1
    assert s['world']==0 and s['level']==1 and s['lives']==2 and s['hp']>0 and s['engine']==8
    assert r['grounded_1_2_completed_returns']>=25 and r['Main_returns']==r['Main_entries']
