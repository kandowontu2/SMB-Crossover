"""Actual current Bowser Star from ordinary safe ground return, no outputs."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import argparse,json
import replay_bowser_star_ground_bc5_1115 as F
import check_smb1_alts_full11_1114 as Runner
import wwf_stock_source_model_1115 as Model
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--identity',type=int,choices=(0,1),default=0);a=p.parse_args();raw=F.ROM.read_bytes()
    family=SimpleNamespace(W=F.W,N=F.N,controller=lambda raw,key:F.controller(raw,a.identity),metadata=lambda raw,key:F.metadata(raw,a.identity))
    def deny(*args,**kw):raise AssertionError('Bowser source attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny),\
        patch.object(Runner,'Factory',family),patch.object(Runner,'cold',F.Current.cold),patch.object(Runner,'strict_metadata',family.metadata):q=Model.run(raw,'smb1'if a.identity else'smb3',3600)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'Bowser natural Star route remains unqualified'
