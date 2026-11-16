"""Actual current Bowser stock source CPU, zero output files/native launch."""
from pathlib import Path
from unittest.mock import patch
import argparse,json
import replay_bowser_natural_stock_bc5_1115 as F
import check_smb1_alts_full11_1114 as Runner
import wwf_stock_source_model_1115 as Model
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--identity',type=int,choices=(0,1),default=0);p.add_argument('--kind',choices=('star','oneup'),default='oneup');p.add_argument('--metadata',action='store_true');a=p.parse_args()
    raw=F.ROM.read_bytes();family=F.family(a.identity,a.kind);key='smb1'if a.identity else'smb3'
    def deny(*args,**kw):raise AssertionError('Bowser source attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny),\
        patch.object(Runner,'Factory',family),patch.object(Runner,'cold',F.Current.cold),patch.object(Runner,'strict_metadata',family.metadata):
        q=family.metadata(raw,key)if a.metadata else Model.run(raw,key,4200)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    if not a.metadata:assert q['passed'],'Bowser stock route remains unqualified'
