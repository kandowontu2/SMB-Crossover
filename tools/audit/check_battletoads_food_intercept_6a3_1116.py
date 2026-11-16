"""Directed ground-intercept source scope, zero outputs/native/game seeds."""
from pathlib import Path
from unittest.mock import patch
import argparse,json
import replay_battletoads_food_intercept_6a3_1116 as F
import check_smb1_alts_full11_1114 as Runner
import wwf_stock_source_model_1115 as Model

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--identity',choices=F.Current.IDENTITIES,default='rash')
    p.add_argument('--kind',choices=('mushroom','flower'),default='mushroom');p.add_argument('--metadata',action='store_true');a=p.parse_args()
    raw=F.ROM.read_bytes();opening=[];family=F.family(a.kind)
    def deny(*args,**kw):raise AssertionError('BT food source attempted files/native')
    def cold(image,key):
        m,report=F.Current.cold(image,key,True);opening.append(report);return m
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny),\
        patch.object(Runner,'Factory',family),patch.object(Runner,'cold',cold),patch.object(Runner,'strict_metadata',family.metadata):
        q=family.metadata(raw,a.identity)if a.metadata else Model.run(raw,a.identity,2650)
    if not a.metadata:q['actual_cold_readback']=opening
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    if not a.metadata:assert q['passed'],'Actual ground-intercept food scope remains unqualified'
