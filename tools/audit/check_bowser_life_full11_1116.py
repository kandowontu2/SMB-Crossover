"""Exact6a3 ordinary genuineL/full-stage source regression, no output files."""
from pathlib import Path
from unittest.mock import patch
import argparse,json
import replay_bowser_life_full11_1116 as F
import check_smb1_alts_full11_1114 as Runner
import wwf_stock_source_model_1115 as Model

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--identity',type=int,choices=(0,1),default=1);p.add_argument('--metadata',action='store_true');a=p.parse_args()
    loaded=F.ROM.read_bytes()
    if F.C.digest(loaded)==F.C.PIN:raw,_=F.C.proposal(loaded);source='Composed exact6a3 in memory from exactbc5'
    else:assert F.C.digest(loaded)==F.PIN;F.C.inverse(loaded);raw=loaded;source='Loaded actual exact6a3'
    key='smb1'if a.identity else'smb3';family=F.family(a.identity)
    def deny(*args,**kw):raise AssertionError('Full controller source attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny),\
        patch.object(Runner,'Factory',family),patch.object(Runner,'cold',F.Current.cold),patch.object(Runner,'strict_metadata',family.metadata):
        q=family.metadata(raw,key)if a.metadata else Model.run(raw,key,6950)
    q['explicit_input']=source
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    if not a.metadata:assert q['passed'],'Stated complete stage continuation remains unqualified'
