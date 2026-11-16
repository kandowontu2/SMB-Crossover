"""Actual inline native Toad firstM, output and native paths trapped."""
from pathlib import Path
from unittest.mock import patch
import argparse,json
import replay_smb1_toad_native_mushroom_91dc_1116 as F
import check_smb1_alts_full11_1114 as Runner
import wwf_stock_source_model_1115 as Model

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--metadata',action='store_true');a=p.parse_args()
    raw=F.ROM.read_bytes();assert F.digest(raw)==F.PIN;opening=[]
    def deny(*args,**kw):raise AssertionError('Toad source attempted artifacts/native')
    def cold(image,key):
        m,q=F.Current.cold(image,key,True);opening.append(q);return m
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny),\
        patch.object(Runner,'Factory',F.family()),patch.object(Runner,'cold',cold),patch.object(Runner,'strict_metadata',F.metadata):q=F.metadata(raw)if a.metadata else Model.run(raw,'toad',1600)
    if opening:q['actual_cold_readback']=opening
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    if not a.metadata:assert q['passed'],'Actual native Toad M/60/credit/25 remains unqualified'
