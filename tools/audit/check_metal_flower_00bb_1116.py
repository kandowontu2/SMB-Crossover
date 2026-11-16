"""Actual installed00bb only; natural controls, in-memory aggregate receipt."""
from pathlib import Path
from unittest.mock import patch
import argparse,json
import replay_metal_flower_00bb_1116 as F
import check_smb1_alts_full11_1114 as Runner
import wwf_stock_source_model_1115 as Model

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--metadata',action='store_true');a=p.parse_args();raw=F.ROM.read_bytes();assert F.digest(raw)==F.PIN;opening=[]
    def deny(*args,**kw):raise AssertionError('Metal Flower source attempted artifacts/native')
    def cold(image,key):
        m,q=F.Current.cold(image,key,True);opening.append(q);return m
    family=F.family()
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny),\
        patch.object(Runner,'Factory',family),patch.object(Runner,'cold',cold),patch.object(Runner,'strict_metadata',family.metadata):q=family.metadata(raw,'metal')if a.metadata else Model.run(raw,'metal',4000)
    if not a.metadata:q['actual_cold_readback']=opening
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    if not a.metadata:assert q['passed'],'Actual Flower/use gates remain unqualified'
