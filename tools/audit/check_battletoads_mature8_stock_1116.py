"""Candidate genuine stock scopes, actual cold and source CPU only."""
from pathlib import Path
from unittest.mock import patch
import argparse,json
import replay_battletoads_mature8_stock_1116 as F
import check_smb1_alts_full11_1114 as Runner
import wwf_stock_source_model_1115 as Model

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--identity',choices=F.Current.IDENTITIES,default='rash');p.add_argument('--kind',choices=F.KINDS,default='oneup');p.add_argument('--metadata',action='store_true');a=p.parse_args()
    parent=F.ROM.read_bytes();assert F.C.digest(parent)==F.C.PIN;raw,composition=F.C.proposal(parent);assert F.C.inverse(raw)==parent
    family=F.family(a.kind);opening=[]
    def deny(*args,**kw):raise AssertionError('Candidate stock source attempted files/native')
    def cold(image,key):
        m,q=F.Current.cold(image,key,True);opening.append(q);return m
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny),\
        patch.object(Runner,'Factory',family),patch.object(Runner,'cold',cold),patch.object(Runner,'strict_metadata',family.metadata):
        q=family.metadata(raw,a.identity)if a.metadata else Model.run(raw,a.identity,4250)
    q['composition']=composition
    if not a.metadata:q['actual_cold_readback']=opening
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    if not a.metadata:assert q['passed'],'Actual candidate stock remains unqualified'
